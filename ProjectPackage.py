"""Safe, portable Stoichiometry Fitter project packages.

``.stf`` files are ordinary ZIP files with a small, versioned JSON schema.
The adjacent HTML report is presentation only; ``.stf`` is authoritative.
No Python code from a package is imported or executed.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import asdict, dataclass, field
import csv
import hashlib
from html import escape
from io import BytesIO, StringIO
import json
import math
import os
from pathlib import PurePosixPath
import re
import stat
import shutil
import tempfile
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple
import uuid
import zipfile
import xml.etree.ElementTree as ElementTree

import numpy as np

import PhysicsBasics as pb
import StoichiometryCore as core
from PhaseAnalysis.contract import ImageArtifact


SCHEMA_VERSION = 6
MEDIA_TYPE = 'application/vnd.stoichiometry-fitter.project+zip'
MAX_ARCHIVE_SIZE = 100 * 1024 * 1024
MAX_ENTRY_SIZE = 25 * 1024 * 1024
MAX_ENTRIES = 1000
MAX_COMPRESSION_RATIO = 100
HTML_PROJECT_ID_RE = re.compile(
    rb'<meta\s+name=["\']stoichiometry-fitter-project-id["\']\s+content=["\']([^"\']+)["\']',
    re.IGNORECASE)


class ProjectError(ValueError):
    """Raised when project or imported input data fails validation."""


@dataclass
class OriginalSource:
    filename: str
    detected_format: str
    content: bytes = field(repr=False)
    sha256: str = ''

    def __post_init__(self):
        if not isinstance(self.content, bytes):
            raise ProjectError('Original source content must be bytes.')
        if not isinstance(self.detected_format, str) or not self.detected_format:
            raise ProjectError('Original source format is invalid.')
        if len(self.content) > MAX_ENTRY_SIZE:
            raise ProjectError('Original source exceeds the maximum entry size.')
        self.filename = safe_filename(self.filename)
        if not self.sha256:
            self.sha256 = sha256(self.content)
        if self.sha256 != sha256(self.content):
            raise ProjectError('Original source checksum does not match its content.')


@dataclass
class ImportedInput:
    analysis_input: core.AnalysisInput
    source: OriginalSource


@dataclass
class Project:
    project_id: str
    lifecycle: str
    input: core.AnalysisInput
    options: core.AnalysisOptions
    resources: core.ResolvedResources = field(default_factory=core.ResolvedResources)
    result: Optional[core.AnalysisResult] = None
    original_source: Optional[OriginalSource] = None
    calculation_fingerprint: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self):
        validate_uuid(self.project_id)
        if self.lifecycle not in ('draft', 'calculated'):
            raise ProjectError('Project lifecycle must be draft or calculated.')
        if self.lifecycle == 'calculated' and self.result is None:
            raise ProjectError('A calculated project must contain archived results.')
        if self.lifecycle == 'draft' and self.result is not None:
            raise ProjectError('A draft project cannot contain calculated results.')
        validate_analysis_input(self.input)
        validate_options(self.options)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_default(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError('Value is not JSON serializable: %s' % type(value).__name__)


def _element_mapping(values: Any) -> OrderedDict:
    """Represent an elemental vector as a Z-ordered, human-readable mapping."""
    if isinstance(values, dict):
        vector = [values[symbol] for symbol in pb.ElementalSymbols[1:] if symbol in values]
    else:
        vector = list(values)
    if not vector or len(vector) > pb.MAXELEMENT:
        raise ProjectError('Elemental data must contain between 1 and %d values.' % pb.MAXELEMENT)
    return OrderedDict((pb.ElementalSymbols[index + 1], float(value))
                       for index, value in enumerate(vector))


def _element_vector(value: Any, label: str, expected_length: Optional[int] = pb.MAXELEMENT) -> List[float]:
    """Read an elemental mapping from project JSON into its in-memory vector."""
    if expected_length is None:
        expected_length = len(value) if isinstance(value, dict) else 0
    symbols = list(pb.ElementalSymbols[1:expected_length + 1])
    if not isinstance(value, dict) or set(value) != set(symbols):
        raise ProjectError('%s must be an object containing every element symbol.' % label)
    return [_finite(value[symbol], '%s %s' % (label, symbol)) for symbol in symbols]


def _z_ordered_mapping(value: Any) -> OrderedDict:
    """Order element-keyed result mappings by atomic number without losing extras."""
    if not isinstance(value, dict):
        return value
    ordered = OrderedDict((symbol, value[symbol]) for symbol in pb.ElementalSymbols[1:]
                          if symbol in value)
    ordered.update((key, item) for key, item in value.items() if key not in ordered)
    return ordered


def validate_uuid(value: str) -> None:
    try:
        parsed = uuid.UUID(value)
    except (ValueError, TypeError, AttributeError) as exc:
        raise ProjectError('Invalid project ID.') from exc
    if str(parsed) != value.lower():
        raise ProjectError('Project ID must be a canonical UUID.')


def safe_filename(filename: str) -> str:
    name = os.path.basename(str(filename).replace('\\', '/')).strip()
    if not name or name in ('.', '..') or '\x00' in name:
        return 'original-input'
    return re.sub(r'[\x00-\x1f/:*?"<>|]+', '_', name)


def slug(text: str, fallback: str = 'artifact') -> str:
    value = re.sub(r'[^0-9A-Za-z._-]+', '_', str(text).strip()).strip('._-').lower()
    return value or fallback


def unique_name(label: str, suffix: str, used: set, fallback: str) -> str:
    base = slug(label, fallback)
    candidate = base + suffix
    index = 2
    while candidate.casefold() in used:
        candidate = '%s_%d%s' % (base, index, suffix)
        index += 1
    used.add(candidate.casefold())
    return candidate


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ProjectError('%s must be numeric.' % label) from exc
    if not math.isfinite(number):
        raise ProjectError('%s must be finite.' % label)
    return number


def _validate_json_value(value: Any, label: str = 'value') -> None:
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, (int, float, np.number)):
        _finite(value, label)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _validate_json_value(item, label)
        return
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise ProjectError('%s object keys must be strings.' % label)
        for item in value.values():
            _validate_json_value(item, label)
        return
    raise ProjectError('%s contains an unsupported value type.' % label)


def _require_keys(value: Dict[str, Any], required: set, allowed: set, label: str) -> None:
    if not isinstance(value, dict):
        raise ProjectError('%s must be an object.' % label)
    missing = required.difference(value)
    unknown = set(value).difference(allowed)
    if missing:
        raise ProjectError('%s is missing field(s): %s.' % (label, ', '.join(sorted(missing))))
    if unknown:
        raise ProjectError('%s contains unknown field(s): %s.' % (label, ', '.join(sorted(unknown))))


def validate_analysis_input(value: core.AnalysisInput) -> None:
    value.input_type = core.normalize_input_type(value.input_type)
    if value.input_type not in ('Counts', 'At %', 'Wt %', 'Ox Wt %'):
        raise ProjectError('Unsupported input type: %s' % value.input_type)
    vector = core.values_to_vector(value.values)
    for index, item in enumerate(vector):
        number = _finite(item, 'Input value %d' % index)
        if number < 0:
            raise ProjectError('Input values cannot be negative.')
    value.values = dict(core.vector_to_element_dict(vector))
    if value.stoichiometry is not None:
        if len(value.stoichiometry) != pb.MAXELEMENT:
            raise ProjectError('Stoichiometry must contain %d values.' % pb.MAXELEMENT)
        value.stoichiometry = [_finite(item, 'Stoichiometry value') for item in value.stoichiometry]


def validate_options(value: core.AnalysisOptions) -> None:
    value.absorption_correction = _finite(value.absorption_correction, 'Absorption correction')
    value.takeoff = _finite(value.takeoff, 'Takeoff angle')
    if value.absorption_correction < 0:
        raise ProjectError('Absorption correction cannot be negative.')
    if not 0.1 <= value.takeoff <= 90:
        raise ProjectError('Takeoff angle must be between 0.1 and 90 degrees.')
    if value.selected_phases is not None and not all(isinstance(x, str) for x in value.selected_phases):
        raise ProjectError('Selected phase names must be strings.')
    if not isinstance(value.phase_analysis_kwargs, dict):
        raise ProjectError('Phase analysis settings must be an object.')
    for label, item in (('k-factor name', value.kfactors),
                        ('arbitrary absorption name', value.arbitrary_absorption),
                        ('phase-analysis name', value.phase_analysis)):
        if item is not None and not isinstance(item, str):
            raise ProjectError('%s must be a string or null.' % label)
    _validate_json_value(value.phase_analysis_kwargs, 'Phase analysis settings')


def validate_resources(value: core.ResolvedResources) -> None:
    for label, vector in (('k-factor', value.k_factors),
                          ('resource stoichiometry', value.stoichiometry)):
        if vector is not None:
            if len(vector) != pb.MAXELEMENT:
                raise ProjectError('%s data must contain %d values.' % (label, pb.MAXELEMENT))
            for item in vector:
                _finite(item, label)
    if value.arbitrary_absorption is not None:
        absorption = value.arbitrary_absorption
        if not isinstance(absorption, dict) or set(absorption) != {'tau', 'rho', 'wt_pct'}:
            raise ProjectError('Resolved arbitrary absorption data is invalid.')
        _finite(absorption['tau'], 'Absorption tau')
        _finite(absorption['rho'], 'Absorption density')
        if not isinstance(absorption['wt_pct'], list) or len(absorption['wt_pct']) != pb.MAXELEMENT:
            raise ProjectError('Absorption composition must contain %d values.' % pb.MAXELEMENT)
        for item in absorption['wt_pct']:
            _finite(item, 'Absorption composition')
    if not isinstance(value.selected_phase_formulas, dict) or not all(
            isinstance(key, str) and isinstance(item, str)
            for key, item in value.selected_phase_formulas.items()):
        raise ProjectError('Resolved phase formulas are invalid.')
    if not isinstance(value.phase_analysis_resources, dict):
        raise ProjectError('Resolved phase-analysis resources are invalid.')
    _validate_json_value(value.phase_analysis_resources, 'Phase-analysis resources')
    if not isinstance(value.hashes, dict) or not all(
            isinstance(key, str) and isinstance(item, str) and re.fullmatch(r'[0-9a-f]{64}', item)
            for key, item in value.hashes.items()):
        raise ProjectError('Resolved resource hashes are invalid.')


def new_project(analysis_input: core.AnalysisInput, options: Optional[core.AnalysisOptions] = None,
                result: Optional[core.AnalysisResult] = None,
                original_source: Optional[OriginalSource] = None,
                project_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None,
                config_dir: str = core.CONFIG_DIR,
                phase_analysis_dir: str = core.PHASE_ANALYSIS_DIR) -> Project:
    options = options or core.AnalysisOptions()
    resources = result.resources if result is not None else core.ResolvedResources()
    fingerprint = result.calculation_fingerprint if result is not None else {}
    return Project(project_id or str(uuid.uuid4()), 'calculated' if result else 'draft',
                   analysis_input, options, resources, result, original_source,
                   fingerprint, dict(metadata or {}))


def project_from_result(result: core.AnalysisResult,
                        original_source: Optional[OriginalSource] = None,
                        project_id: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> Project:
    return new_project(result.input, result.options, result, original_source,
                       project_id, metadata)


def _csv_text(rows: Iterable[Iterable[Any]]) -> str:
    output = StringIO(newline='')
    writer = csv.writer(output, lineterminator='\n')
    writer.writerows(rows)
    return output.getvalue()


def export_input_csv_bytes(analysis_input: core.AnalysisInput) -> bytes:
    headers = {'Counts': 'Counts', 'At %': 'At%', 'Wt %': 'Wt%', 'Ox Wt %': 'OxWt%'}
    input_type = core.normalize_input_type(analysis_input.input_type)
    values = core.vector_to_element_dict(core.values_to_vector(analysis_input.values))
    return _csv_text([['Element', headers[input_type]]] +
                     [[element, format(value, '.17g')] for element, value in values.items()]).encode('utf-8')


def export_report_text_bytes(project_or_result: Any) -> bytes:
    result = project_or_result.result if isinstance(project_or_result, Project) else project_or_result
    return (result.report_text if result is not None else 'Not yet calculated.\n').encode('utf-8')


def export_table_csv_bytes(table: core.ResultTable) -> bytes:
    rows = [list(table.columns)]
    for row in table.rows:
        rows.append([row.get(column, '') for column in table.columns])
    return _csv_text(rows).encode('utf-8')


def export_svg_bytes(figure: ImageArtifact) -> bytes:
    if figure.mime_type != 'image/svg+xml' or not isinstance(figure.payload, str):
        raise ProjectError('Only SVG image artifacts can be exported.')
    return validate_svg_payload(figure.payload).encode('utf-8')


def _svg_name(value: str) -> str:
    return value.rsplit('}', 1)[-1].lower()


def _safe_svg_reference(value: str) -> bool:
    """Allow only local SVG fragment references such as ``url(#clip)``."""
    text = str(value).strip()
    lowered = text.lower()
    if any(token in lowered for token in ('javascript:', 'data:', 'file:', 'http:', 'https:', '@import', 'expression(')):
        return False
    for match in re.finditer(r'url\(\s*([^)]*?)\s*\)', text, flags=re.I):
        target = match.group(1).strip().strip('\"\'')
        if not target.startswith('#'):
            return False
    return True


def validate_svg_payload(payload: str) -> str:
    """Validate SVG for inert browser display and download.

    Project packages may be received from another machine, so figure SVG is
    treated as untrusted even though installed phase analyses normally produce
    it.  The accepted subset permits ordinary Matplotlib SVG (including local
    clip-path references) but excludes executable and externally loaded nodes.
    """
    if not isinstance(payload, str):
        raise ProjectError('Invalid SVG artifact.')
    if re.search(r'<!\s*entity\b', payload, flags=re.I):
        raise ProjectError('SVG entities are not permitted.')
    doctype = re.search(r'<!\s*doctype\b([^>]|\[[\s\S]*?\])*?>', payload, flags=re.I)
    if doctype:
        if '[' in doctype.group(0):
            raise ProjectError('SVG internal declarations are not permitted.')
        # Matplotlib emits a harmless SVG 1.1 public doctype.  Drop it so no
        # renderer has a reason to resolve the declared external DTD.
        payload = payload[:doctype.start()] + payload[doctype.end():]
    try:
        root = ElementTree.fromstring(payload)
    except ElementTree.ParseError as exc:
        raise ProjectError('Invalid SVG artifact.') from exc
    if _svg_name(root.tag) != 'svg':
        raise ProjectError('Image artifact root must be SVG.')
    # Matplotlib records Dublin Core metadata with external namespace URLs.
    # It is not needed to display the figure, so omit metadata instead of
    # permitting external-looking references from an uploaded artifact.
    for parent in root.iter():
        for child in list(parent):
            if _svg_name(child.tag) == 'metadata':
                parent.remove(child)
    blocked_tags = {'script', 'foreignobject', 'iframe', 'object', 'embed', 'image',
                    'audio', 'video', 'animate', 'animatecolor', 'animatemotion',
                    'animatetransform', 'set', 'mpath'}
    for element in root.iter():
        tag = _svg_name(element.tag)
        if tag in blocked_tags:
            raise ProjectError('SVG contains unsafe element: %s.' % tag)
        if tag == 'style' and not _safe_svg_reference(element.text or ''):
            raise ProjectError('SVG contains an unsafe style reference.')
        for attribute, value in element.attrib.items():
            name = _svg_name(attribute)
            if name.startswith('on') or name in ('base', 'src'):
                raise ProjectError('SVG contains an unsafe attribute: %s.' % name)
            if name == 'href' and not str(value).strip().startswith('#'):
                raise ProjectError('SVG contains an external reference.')
            if not _safe_svg_reference(value):
                raise ProjectError('SVG contains an unsafe reference.')
    return ElementTree.tostring(root, encoding='unicode')


def export_input_csv(analysis_input: core.AnalysisInput, path: str) -> None:
    with open(path, 'wb') as fid:
        fid.write(export_input_csv_bytes(analysis_input))


def export_report_text(project_or_result: Any, path: str) -> None:
    with open(path, 'wb') as fid:
        fid.write(export_report_text_bytes(project_or_result))


def export_table_csv(table: core.ResultTable, path: str) -> None:
    with open(path, 'wb') as fid:
        fid.write(export_table_csv_bytes(table))


def export_svg(figure: ImageArtifact, path: str) -> None:
    with open(path, 'wb') as fid:
        fid.write(export_svg_bytes(figure))


def _resource_hash_value(key: str, analysis_input: core.AnalysisInput,
                         options: core.AnalysisOptions, resources: core.ResolvedResources) -> Any:
    """Return the readable configuration value represented by a resource hash."""
    values = {
        'stoichiometry': analysis_input.stoichiometry_name or 'Custom stoichiometry values',
        'k_factors': options.kfactors,
        'arbitrary_absorption': options.arbitrary_absorption,
        'selected_phase_formulas': resources.selected_phase_formulas,
        'phase_analysis_algorithm': options.phase_analysis,
        'phase_analysis_protosolar_abundances': 'Protosolar abundance dataset',
    }
    return values.get(key, key.replace('_', ' '))


def _fingerprint_payload(fingerprint: Dict[str, Any], analysis_input: core.AnalysisInput,
                         options: core.AnalysisOptions,
                         resources: core.ResolvedResources) -> Dict[str, Any]:
    """Add a readable value beside every persisted calculation hash."""
    payload = dict(fingerprint)
    for field in ('algorithm_hashes', 'resource_hashes'):
        hashes = payload.get(field, {})
        if not isinstance(hashes, dict):
            continue
        payload[field] = OrderedDict(
            (key, {'sha256': digest,
                   'value': (_resource_hash_value(key, analysis_input, options, resources)
                             if field == 'resource_hashes' else key)})
            for key, digest in hashes.items())
    return payload


def _fingerprint_from_payload(value: Any) -> Dict[str, Any]:
    """Restore compact in-memory calculation hashes from readable JSON records."""
    if not isinstance(value, dict):
        raise ProjectError('Calculation fingerprint must be an object.')
    payload = dict(value)
    for field in ('algorithm_hashes', 'resource_hashes'):
        hashes = payload.get(field, {})
        if not isinstance(hashes, dict):
            raise ProjectError('Calculation fingerprint hashes are invalid.')
        compact = {}
        for key, hash_record in hashes.items():
            _require_keys(hash_record, {'sha256', 'value'}, {'sha256', 'value'},
                          'Calculation hash record')
            if not isinstance(hash_record['sha256'], str):
                raise ProjectError('Calculation hash digest is invalid.')
            compact[key] = hash_record['sha256']
        payload[field] = compact
    return payload


def _resources_payload(resources: core.ResolvedResources, analysis_input: core.AnalysisInput,
                       options: core.AnalysisOptions) -> Dict[str, Any]:
    """Create the readable on-disk representation of resolved resources."""
    payload = asdict(resources)
    for key in ('k_factors', 'stoichiometry'):
        if payload[key] is not None:
            payload[key] = _element_mapping(payload[key])
    if payload['arbitrary_absorption'] is not None:
        payload['arbitrary_absorption']['wt_pct'] = _element_mapping(
            payload['arbitrary_absorption']['wt_pct'])
    phase_resources = payload['phase_analysis_resources']
    if 'protosolar_abundances' in phase_resources:
        phase_resources['protosolar_abundances'] = _element_mapping(
            phase_resources['protosolar_abundances'])
    payload['hashes'] = OrderedDict(
        (key, {'sha256': digest,
               'value': _resource_hash_value(key, analysis_input, options, resources)})
        for key, digest in resources.hashes.items())
    return payload


def _result_payload(result: Optional[core.AnalysisResult], figure_paths: List[str]) -> Optional[Dict[str, Any]]:
    if result is None:
        return None
    return {
        'report_text': result.report_text,
        'tables': [asdict(table) for table in result.tables],
        'quant': _z_ordered_mapping(result.quant),
        'phase_analysis': result.phase_analysis,
        'figures': [dict(id=figure.id, title=figure.title, mime_type=figure.mime_type,
                         alt_text=figure.alt_text, path=path)
                    for figure, path in zip(result.figures, figure_paths)],
        'warnings': list(result.warnings),
    }


def _project_payload(project: Project, figure_paths: List[str], source_path: Optional[str]) -> Dict[str, Any]:
    source = None
    if project.original_source:
        source = {'filename': project.original_source.filename,
                  'detected_format': project.original_source.detected_format,
                  'sha256': project.original_source.sha256, 'path': source_path}
    input_payload = {
        'values': _element_mapping(project.input.values),
        'input_type': project.input.input_type,
        'stoichiometry': (_element_mapping(project.input.stoichiometry)
                           if project.input.stoichiometry is not None else None),
        'stoichiometry_name': project.input.stoichiometry_name,
    }
    resources_payload = _resources_payload(project.resources, project.input, project.options)
    return {
        'schema_version': project.schema_version,
        'project_id': project.project_id,
        'lifecycle': project.lifecycle,
        'input': input_payload,
        'settings': asdict(project.options),
        'resources': resources_payload,
        'results': _result_payload(project.result, figure_paths),
        'original_source': source,
        'calculation_fingerprint': _fingerprint_payload(
            project.calculation_fingerprint, project.input, project.options, project.resources),
        'metadata': project.metadata,
    }


def _resource_entries(project: Project) -> Dict[str, bytes]:
    resources = project.resources
    readable_resources = _resources_payload(resources, project.input, project.options)
    entries = {'data/inputs/calculation_parameters.json': _calculation_parameters_json(project)}
    if resources.k_factors is not None:
        entries['data/inputs/k_factors.csv'] = _csv_text(
            [['Element', 'K']] + [[pb.ElementalSymbols[i + 1], format(v, '.17g')]
                                  for i, v in enumerate(resources.k_factors)]).encode('utf-8')
    if resources.stoichiometry is not None:
        entries['data/inputs/stoichiometry.csv'] = _csv_text(
            [['Element', 'Charge']] + [[pb.ElementalSymbols[i + 1], format(v, '.17g')]
                                       for i, v in enumerate(resources.stoichiometry)]).encode('utf-8')
    if resources.arbitrary_absorption is not None:
        entries['data/inputs/arbitrary_absorption.json'] = json.dumps(
            readable_resources['arbitrary_absorption'], indent=2, sort_keys=False,
            allow_nan=False, default=_json_default).encode('utf-8')
    if resources.selected_phase_formulas:
        entries['data/inputs/selected_phases.csv'] = _csv_text(
            [['Phase', 'Formula']] + sorted(resources.selected_phase_formulas.items())).encode('utf-8')
    if resources.phase_analysis_resources:
        entries['data/inputs/phase_analysis_resources.json'] = json.dumps(
            readable_resources['phase_analysis_resources'], indent=2, sort_keys=False,
            allow_nan=False, default=_json_default).encode('utf-8')
    return entries


def _calculation_parameters_json(project: Project) -> bytes:
    """Summarize calculation choices without repeating detailed elemental data."""
    resources = project.resources
    def parameter(value, hash_key='', archived_data=None):
        result = {'value': value}
        if hash_key in resources.hashes:
            result['sha256'] = resources.hashes[hash_key]
        if archived_data:
            result['archived_data'] = archived_data
        return result

    values = {
        'input_type': parameter(project.input.input_type, archived_data='data/inputs/input.csv'),
        'stoichiometry': parameter(
            project.input.stoichiometry_name or
            ('Custom values' if project.input.stoichiometry is not None else None),
            'stoichiometry', 'data/inputs/stoichiometry.csv'
            if resources.stoichiometry is not None else None),
        'k_factors': parameter(project.options.kfactors, 'k_factors',
                               'data/inputs/k_factors.csv' if resources.k_factors is not None else None),
        'arbitrary_absorption': parameter(
            project.options.arbitrary_absorption, 'arbitrary_absorption',
            'data/inputs/arbitrary_absorption.json' if resources.arbitrary_absorption is not None else None),
        'absorption_correction': parameter(project.options.absorption_correction),
        'takeoff_angle_degrees': parameter(project.options.takeoff),
        'selected_phase_formulas': parameter(
            project.options.selected_phases or [], 'selected_phase_formulas',
            'data/inputs/selected_phases.csv' if resources.selected_phase_formulas else None),
        'phase_analysis': parameter(project.options.phase_analysis, 'phase_analysis_algorithm'),
    }
    if resources.phase_analysis_resources:
        values['phase_analysis_auxiliary_data'] = parameter(
            list(resources.phase_analysis_resources), 'phase_analysis_protosolar_abundances',
            'data/inputs/phase_analysis_resources.json')
    payload = {'description': 'Calculation settings and references to detailed archived input data.',
               'parameters': values}
    return json.dumps(payload, indent=2, sort_keys=False, ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def render_html_report(project: Project) -> str:
    """Render a self-contained, browser-readable report with no external URLs."""
    title = str(project.metadata.get('title') or 'Stoichiometry Fitter Project')
    status = 'Calculated' if project.lifecycle == 'calculated' else 'Not yet calculated'
    result = project.result
    sections = []
    if result is not None:
        sections.append('<section><h2>Report</h2><pre>%s</pre></section>' % escape(result.report_text))
        if result.warnings:
            sections.append('<section class="warnings"><h2>Warnings</h2><ul>%s</ul></section>' % ''.join(
                '<li>%s</li>' % escape(warning) for warning in result.warnings))
        for table in result.tables:
            head = ''.join('<th scope="col">%s</th>' % escape(str(column)) for column in table.columns)
            body = ''.join('<tr>%s</tr>' % ''.join(
                '<td>%s</td>' % escape(str(row.get(column, ''))) for column in table.columns)
                           for row in table.rows)
            sections.append('<section><h2>%s</h2>%s<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></section>' %
                            (escape(table.title), '<p>%s</p>' % escape(table.description) if table.description else '',
                             head, body))
        for figure in result.figures:
            # SVG is generated by installed analyses, not accepted as executable HTML.
            # Strip active/script-capable constructs before inline presentation.
            svg = _sanitize_svg(figure.payload)
            sections.append('<section><h2>%s</h2><figure>%s<figcaption>%s</figcaption></figure></section>' %
                            (escape(figure.title), svg, escape(figure.alt_text)))
    else:
        sections.append('<section class="draft"><h2>Not yet calculated</h2><p>This project contains editable input and settings, but no archived calculation results.</p></section>')
    css = """
html{font-family:system-ui,-apple-system,sans-serif;color:#202124;background:#fff}body{max-width:1100px;margin:2rem auto;padding:0 1rem;line-height:1.45}h1,h2{color:#17365d}header{border-bottom:3px solid #4f81bd;margin-bottom:2rem}.status{font-weight:700}.draft{padding:1rem;background:#fff5cc;border-left:5px solid #d6a600}pre{white-space:pre-wrap;background:#f6f8fa;padding:1rem;overflow:auto}table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}th,td{border:1px solid #c8ccd0;padding:.35rem .55rem;text-align:left}th{background:#eaf1f8;position:sticky;top:0}.warnings{background:#fff4f4;border-left:5px solid #b42318;padding:.5rem 1rem}figure{margin:1rem 0}svg{max-width:100%;height:auto}@media print{body{max-width:none;margin:0}section{break-inside:avoid}th{position:static}}
""".strip()
    return '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="stoichiometry-fitter-project-id" content="%s"><title>%s</title><style>%s</style></head><body><header><h1>%s</h1><p class="status">Status: %s</p><p>Project ID: <code>%s</code></p></header>%s</body></html>\n' % (
        escape(project.project_id, quote=True), escape(title), css, escape(title), status,
        escape(project.project_id), ''.join(sections))


def _sanitize_svg(payload: str) -> str:
    return validate_svg_payload(payload)


def _build_entries(project: Project) -> Dict[str, bytes]:
    validate_project(project)
    entries: Dict[str, bytes] = {}
    used_tables, used_images = set(), set()
    table_paths = []
    figure_paths = []
    if project.result:
        for table in project.result.tables:
            name = unique_name(table.name, '.csv', used_tables, 'table')
            path = ('data/outputs/' if table.name == 'quantification'
                    else 'data/outputs/phase_analysis/') + name
            table_paths.append(path)
            entries[path] = export_table_csv_bytes(table)
        for figure in project.result.figures:
            name = unique_name(figure.id, '.svg', used_images, 'figure')
            path = 'data/outputs/phase_analysis/images/' + name
            figure_paths.append(path)
            entries[path] = export_svg_bytes(figure)
    source_path = None
    if project.original_source:
        source_path = 'data/inputs/source/original/' + safe_filename(project.original_source.filename)
        entries[source_path] = project.original_source.content
    entries['data/inputs/input.csv'] = export_input_csv_bytes(project.input)
    entries['data/outputs/report.txt'] = export_report_text_bytes(project)
    entries.update(_resource_entries(project))
    payload = _project_payload(project, figure_paths, source_path)
    if project.result:
        for table_payload, path in zip(payload['results']['tables'], table_paths):
            table_payload['path'] = path
    entries['project.json'] = json.dumps(payload, indent=2, sort_keys=False,
                                         ensure_ascii=False, allow_nan=False,
                                         default=_json_default).encode('utf-8')
    entries['report.html'] = render_html_report(project).encode('utf-8')
    return entries


def validate_project(project: Project) -> None:
    if project.schema_version != SCHEMA_VERSION:
        raise ProjectError('Unsupported project schema version: %s' % project.schema_version)
    validate_uuid(project.project_id)
    validate_analysis_input(project.input)
    validate_options(project.options)
    validate_resources(project.resources)
    if project.original_source is not None:
        validate_original_source(project.original_source)
    _validate_json_value(project.metadata, 'Project metadata')
    _validate_json_value(project.calculation_fingerprint, 'Calculation fingerprint')
    if project.result:
        if project.result.input != project.input or project.result.options != project.options:
            raise ProjectError('Archived results do not match project input and settings.')
        for table in project.result.tables:
            if not table.name or not table.columns or not isinstance(table.rows, list):
                raise ProjectError('Invalid result table.')
            for row in table.rows:
                if not isinstance(row, dict):
                    raise ProjectError('Result table rows must be objects.')
                _validate_json_value(row, 'Result table')
        for warning in project.result.warnings:
            if not isinstance(warning, str):
                raise ProjectError('Warnings must be strings.')
        if not isinstance(project.result.report_text, str):
            raise ProjectError('Archived report text must be a string.')
        _validate_json_value(project.result.quant, 'Archived quantification')
        _validate_json_value(project.result.phase_analysis, 'Archived phase analysis')


def _entry_description(path: str, project: Project) -> str:
    """Describe an archive member for people inspecting a project ZIP."""
    if path == 'project.json':
        return 'Authoritative project data: inputs, settings, resolved resources, and archived results.'
    if path == 'report.html':
        return 'Browser-readable presentation of the archived report and result tables.'
    if path == 'data/outputs/report.txt':
        return 'Plain-text calculation report for reading or copying outside the application.'
    if path == 'data/inputs/input.csv':
        return 'Normalized elemental input values used for the calculation; this is not a result table.'
    if path == 'data/outputs/quantification.csv':
        return 'Elemental quantification results exported as CSV.'
    if path.startswith('data/outputs/phase_analysis/'):
        if project.result is not None:
            table_paths = [slug(table.name, 'table') for table in project.result.tables]
            filename = PurePosixPath(path).stem
            for table, table_path in zip(project.result.tables, table_paths):
                if filename == table_path:
                    return 'Result table "%s". %s' % (table.title, table.description or
                                                        'Archived calculation output.')
        return 'Structured calculation result table exported as CSV.'
    if path == 'data/inputs/calculation_parameters.json':
        return 'Summary of calculation settings, selected values, hashes, and links to detailed input data.'
    if path == 'data/inputs/k_factors.csv':
        return 'Elemental k-factors used for quantification.'
    if path == 'data/inputs/stoichiometry.csv':
        return 'Elemental stoichiometry or charge values used for the calculation.'
    if path == 'data/inputs/arbitrary_absorption.json':
        return 'Arbitrary absorption correction parameters and elemental composition.'
    if path == 'data/inputs/selected_phases.csv':
        return 'Phase formulas selected for the phase-fit calculation.'
    if path == 'data/inputs/phase_analysis_resources.json':
        return 'Auxiliary datasets supplied to the selected phase analysis.'
    if path.startswith('data/outputs/phase_analysis/images/'):
        return 'SVG figure generated by the archived phase analysis.'
    if path.startswith('data/inputs/source/original/'):
        return 'Original imported input file, retained verbatim for provenance.'
    return 'Project package member.'


def serialize_stf(project: Project) -> bytes:
    entries = _build_entries(project)
    if len(entries) + 1 > MAX_ENTRIES:
        raise ProjectError('Project contains too many package entries.')
    for path, content in entries.items():
        if len(content) > MAX_ENTRY_SIZE:
            raise ProjectError('Project entry is too large: %s' % path)
    if sum(len(content) for content in entries.values()) > MAX_ARCHIVE_SIZE:
        raise ProjectError('Expanded project package is too large.')
    inventory = [{'path': path, 'description': _entry_description(path, project),
                  'size': len(data), 'sha256': sha256(data)}
                 for path, data in sorted(entries.items())]
    source_provenance = None
    if project.original_source:
        source_provenance = {'filename': project.original_source.filename,
                             'detected_format': project.original_source.detected_format,
                             'sha256': project.original_source.sha256}
    manifest = {
        'schema_version': SCHEMA_VERSION,
        'media_type': MEDIA_TYPE,
        'project_id': project.project_id,
        'description': 'Inventory and integrity record for this Stoichiometry Fitter project package.',
        'provenance': {'lifecycle': project.lifecycle,
                       'calculation_fingerprint': _fingerprint_payload(
                           project.calculation_fingerprint, project.input, project.options,
                           project.resources),
                       'original_source': source_provenance},
        'entries': inventory,
    }
    entries['manifest.json'] = json.dumps(manifest, indent=2, sort_keys=False,
                                          allow_nan=False).encode('utf-8')
    output = BytesIO()
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(entries):
            info = zipfile.ZipInfo(path, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, entries[path])
    return output.getvalue()


def serialize_stf_to_stream(project: Project, stream) -> None:
    stream.write(serialize_stf(project))


def _safe_zip_path(name: str) -> bool:
    if not name or '\x00' in name or '\\' in name or name.startswith('/'):
        return False
    path = PurePosixPath(name)
    return not any(part in ('', '.', '..') for part in path.parts)


def _safe_zip_member(info: zipfile.ZipInfo) -> bool:
    """Return whether a ZIP member is a regular, bounded, readable file."""
    if not _safe_zip_path(info.filename) or info.is_dir() or info.flag_bits & 0x1:
        return False
    mode = (info.external_attr >> 16) & 0xffff
    file_type = stat.S_IFMT(mode)
    if file_type and file_type != stat.S_IFREG:
        return False
    if info.file_size > MAX_ENTRY_SIZE:
        return False
    if info.file_size and not info.compress_size:
        return False
    if (info.compress_size and info.file_size / info.compress_size > MAX_COMPRESSION_RATIO):
        return False
    return True


def _read_archive(data: bytes) -> Tuple[Dict[str, bytes], Dict[str, Any]]:
    if len(data) > MAX_ARCHIVE_SIZE:
        raise ProjectError('Project package exceeds the maximum archive size.')
    try:
        archive = zipfile.ZipFile(BytesIO(data), 'r')
    except (zipfile.BadZipFile, OSError) as exc:
        raise ProjectError('File is not a valid Stoichiometry Fitter package.') from exc
    with archive:
        infos = archive.infolist()
        if len(infos) > MAX_ENTRIES:
            raise ProjectError('Project package contains too many entries.')
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise ProjectError('Project package contains duplicate ZIP members.')
        total = 0
        for info in infos:
            if not _safe_zip_path(info.filename):
                raise ProjectError('Project package contains an unsafe ZIP path.')
            if not _safe_zip_member(info):
                raise ProjectError('Project package contains an unsafe ZIP member: %s' %
                                   info.filename)
            total += info.file_size
        if total > MAX_ARCHIVE_SIZE:
            raise ProjectError('Expanded project package is too large.')
        try:
            entries = {info.filename: archive.read(info) for info in infos}
        except (zipfile.BadZipFile, RuntimeError, OSError) as exc:
            raise ProjectError('Project package data is corrupt or unreadable.') from exc
    if 'manifest.json' not in entries or 'project.json' not in entries:
        raise ProjectError('Project package is missing manifest.json or project.json.')
    manifest = _json_object(entries['manifest.json'], 'manifest.json')
    manifest_fields = {'schema_version', 'media_type', 'project_id', 'description', 'provenance', 'entries'}
    _require_keys(manifest, manifest_fields, manifest_fields, 'manifest.json')
    if not isinstance(manifest.get('description'), str) or not manifest['description']:
        raise ProjectError('Manifest description is invalid.')
    provenance_fields = {'lifecycle', 'calculation_fingerprint', 'original_source'}
    _require_keys(manifest.get('provenance'), provenance_fields, provenance_fields,
                  'Manifest provenance')
    _validate_json_value(manifest['provenance'], 'Manifest provenance')
    if manifest.get('schema_version') != SCHEMA_VERSION:
        version = manifest.get('schema_version')
        if isinstance(version, int) and version > SCHEMA_VERSION:
            raise ProjectError('Project uses unsupported future schema version %s.' % version)
        raise ProjectError('Unsupported project schema version: %s' % version)
    if manifest.get('media_type') != MEDIA_TYPE:
        raise ProjectError('Invalid project package media type.')
    inventory = manifest.get('entries')
    if not isinstance(inventory, list):
        raise ProjectError('Manifest entry inventory is invalid.')
    expected = set(entries).difference({'manifest.json'})
    listed = set()
    for item in inventory:
        if not isinstance(item, dict):
            raise ProjectError('Manifest entry inventory is invalid.')
        _require_keys(item, {'path', 'description', 'size', 'sha256'},
                      {'path', 'description', 'size', 'sha256'},
                      'Manifest inventory entry')
        if not isinstance(item.get('path'), str) or not isinstance(item.get('description'), str):
            raise ProjectError('Manifest entry path or description is invalid.')
        path = item['path']
        if not _safe_zip_path(path):
            raise ProjectError('Project package contains an unsafe ZIP path.')
        if path in listed:
            raise ProjectError('Manifest contains a duplicate inventory entry.')
        listed.add(path)
        content = entries.get(path)
        if content is None or item.get('size') != len(content) or item.get('sha256') != sha256(content):
            raise ProjectError('Checksum or size validation failed for %s.' % path)
    if listed != expected:
        raise ProjectError('Manifest inventory does not match package contents.')
    return entries, manifest


def _json_object(data: bytes, label: str) -> Dict[str, Any]:
    try:
        value = json.loads(data.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProjectError('%s is not valid UTF-8 JSON.' % label) from exc
    if not isinstance(value, dict):
        raise ProjectError('%s must contain a JSON object.' % label)
    return value


def _table_from_payload(value: Dict[str, Any]) -> core.ResultTable:
    required = {'name', 'title', 'columns', 'rows'}
    allowed = required.union({'metadata', 'description', 'path'})
    _require_keys(value, required, allowed, 'Archived table')
    return core.ResultTable(value['name'], value['title'], list(value['columns']),
                            list(value['rows']), dict(value.get('metadata', {})),
                            value.get('description', ''))


def load_stf_bytes(data: bytes) -> Project:
    entries, manifest = _read_archive(data)
    payload = _json_object(entries['project.json'], 'project.json')
    project_fields = {'schema_version', 'project_id', 'lifecycle', 'input', 'settings',
                      'resources', 'results', 'original_source',
                      'calculation_fingerprint', 'metadata'}
    _require_keys(payload, project_fields, project_fields, 'project.json')
    if payload.get('schema_version') != SCHEMA_VERSION:
        raise ProjectError('project.json schema does not match this application.')
    project_id = payload.get('project_id')
    if project_id != manifest.get('project_id'):
        raise ProjectError('Manifest and project IDs do not match.')
    input_fields = {'values', 'input_type', 'stoichiometry', 'stoichiometry_name'}
    option_fields = {'kfactors', 'arbitrary_absorption', 'absorption_correction', 'takeoff',
                     'selected_phases', 'phase_analysis', 'phase_analysis_kwargs'}
    resource_fields = {'k_factors', 'stoichiometry', 'arbitrary_absorption',
                       'selected_phase_formulas', 'phase_analysis_resources', 'hashes'}
    _require_keys(payload.get('input'), input_fields, input_fields, 'Project input')
    _require_keys(payload.get('settings'), option_fields, option_fields, 'Project settings')
    _require_keys(payload.get('resources'), resource_fields, resource_fields, 'Project resources')
    input_payload = dict(payload['input'])
    input_payload['values'] = _z_ordered_mapping(input_payload['values'])
    if input_payload['stoichiometry'] is not None:
        input_payload['stoichiometry'] = _element_vector(
            input_payload['stoichiometry'], 'Input stoichiometry')
    resources_payload = dict(payload['resources'])
    for key in ('k_factors', 'stoichiometry'):
        if resources_payload[key] is not None:
            resources_payload[key] = _element_vector(resources_payload[key],
                                                      'Resource %s' % key)
    if resources_payload['arbitrary_absorption'] is not None:
        absorption = dict(resources_payload['arbitrary_absorption'])
        absorption['wt_pct'] = _element_vector(absorption['wt_pct'],
                                                'Absorption composition')
        resources_payload['arbitrary_absorption'] = absorption
    phase_resources = dict(resources_payload['phase_analysis_resources'])
    if 'protosolar_abundances' in phase_resources:
        phase_resources['protosolar_abundances'] = _element_vector(
            phase_resources['protosolar_abundances'], 'Protosolar abundances',
            expected_length=None)
    resources_payload['phase_analysis_resources'] = phase_resources
    hash_payload = resources_payload['hashes']
    if not isinstance(hash_payload, dict):
        raise ProjectError('Resource hashes must be an object.')
    resources_payload['hashes'] = {}
    for key, hash_record in hash_payload.items():
        _require_keys(hash_record, {'sha256', 'value'}, {'sha256', 'value'},
                      'Resource hash record')
        if not isinstance(hash_record['sha256'], str):
            raise ProjectError('Resource hash digest is invalid.')
        resources_payload['hashes'][key] = hash_record['sha256']
    fingerprint = _fingerprint_from_payload(payload.get('calculation_fingerprint', {}))
    try:
        analysis_input = core.AnalysisInput(**input_payload)
        options = core.AnalysisOptions(**payload['settings'])
        resources = core.ResolvedResources(**resources_payload)
    except (KeyError, TypeError) as exc:
        raise ProjectError('Project input, settings, or resources are invalid.') from exc
    source = None
    source_payload = payload.get('original_source')
    if source_payload is not None:
        source_fields = {'filename', 'detected_format', 'sha256', 'path'}
        _require_keys(source_payload, source_fields, source_fields, 'Original source')
        try:
            source_path = source_payload['path']
            source_content = entries[source_path]
            source = OriginalSource(source_payload['filename'], source_payload['detected_format'],
                                    source_content, source_payload['sha256'])
        except (KeyError, TypeError) as exc:
            raise ProjectError('Original source archive is missing or invalid.') from exc
    result = None
    result_payload = payload.get('results')
    if result_payload is not None:
        result_fields = {'report_text', 'tables', 'quant', 'phase_analysis', 'figures', 'warnings'}
        _require_keys(result_payload, result_fields, result_fields, 'Archived results')
        try:
            tables = [_table_from_payload(table) for table in result_payload['tables']]
            figures = []
            for figure in result_payload.get('figures', []):
                figure_fields = {'id', 'title', 'mime_type', 'alt_text', 'path'}
                _require_keys(figure, figure_fields, figure_fields, 'Archived figure')
                figure_data = entries[figure['path']].decode('utf-8')
                figures.append(ImageArtifact(figure['id'], figure['title'], figure['mime_type'],
                                             figure_data, figure['alt_text']))
            result = core.AnalysisResult(
                analysis_input, options, tables, result_payload['report_text'],
                _z_ordered_mapping(result_payload.get('quant', {})), result_payload.get('phase_analysis'), figures,
                list(result_payload.get('warnings', [])), resources,
                fingerprint)
        except (KeyError, TypeError, UnicodeDecodeError) as exc:
            raise ProjectError('Archived calculation results are invalid.') from exc
    project = Project(project_id, payload.get('lifecycle'), analysis_input, options, resources,
                      result, source, fingerprint,
                      dict(payload.get('metadata', {})), payload.get('schema_version'))
    validate_project(project)
    core.validate_resource_selections(project.input, project.options)
    expected_source_provenance = None
    if project.original_source:
        expected_source_provenance = {
            'filename': project.original_source.filename,
            'detected_format': project.original_source.detected_format,
            'sha256': project.original_source.sha256,
        }
    expected_provenance = {'lifecycle': project.lifecycle,
                           'calculation_fingerprint': _fingerprint_payload(
                               project.calculation_fingerprint, project.input, project.options,
                               project.resources),
                           'original_source': expected_source_provenance}
    if manifest.get('provenance') != expected_provenance:
        raise ProjectError('Manifest provenance does not match project.json.')
    expected_entries = _build_entries(project)
    actual_entries = {path: content for path, content in entries.items()
                      if path != 'manifest.json'}
    if set(actual_entries) != set(expected_entries):
        raise ProjectError('Project package contains undeclared or missing members.')
    for path, expected_content in expected_entries.items():
        if actual_entries[path] != expected_content:
            raise ProjectError('Project package member is stale or invalid: %s.' % path)
    return project


def load_stf_stream(stream) -> Project:
    return load_stf_bytes(stream.read(MAX_ARCHIVE_SIZE + 1))


def html_project_id(data: bytes) -> Optional[str]:
    match = HTML_PROJECT_ID_RE.search(data[:1024 * 1024])
    if match is None:
        return None
    try:
        value = match.group(1).decode('ascii', 'strict')
        validate_uuid(value)
    except (UnicodeDecodeError, ProjectError):
        return None
    return value


def load_html_sidecar_bytes(html_data: bytes, stf_data: Optional[bytes]) -> Project:
    expected_id = html_project_id(html_data)
    if expected_id is None:
        raise ProjectError('HTML data is not a Stoichiometry Fitter project report.')
    if stf_data is None:
        raise ProjectError('The matching .stf project package is required to open this HTML report.')
    project = load_stf_bytes(stf_data)
    if project.project_id != expected_id:
        raise ProjectError('The .stf package is stale or belongs to a different project.')
    return project


def detect_and_load_bytes(data: bytes, filename: str = 'input',
                          matching_stf_data: Optional[bytes] = None) -> Any:
    """Detect a project package, matching HTML, or supported legacy input."""
    extension = os.path.splitext(filename)[1].lower()
    if extension == '.stf' or data.startswith(b'PK\x03\x04'):
        return load_stf_bytes(data)
    if extension == '.html' or html_project_id(data) is not None:
        return load_html_sidecar_bytes(data, matching_stf_data)
    return detect_and_load_input_bytes(data, filename)


def save_project_files(project: Project, path: str) -> Tuple[str, str]:
    """Atomically replace the authoritative package and its HTML sidecar."""
    root, extension = os.path.splitext(os.path.abspath(path))
    stf_path = path if extension.lower() == '.stf' else path + '.stf'
    stf_path = os.path.abspath(stf_path)
    html_path = os.path.splitext(stf_path)[0] + '.html'
    package = serialize_stf(project)
    html = render_html_report(project).encode('utf-8')
    directory = os.path.dirname(stf_path) or '.'
    os.makedirs(directory, exist_ok=True)
    temporary = []
    backups: Dict[str, Optional[str]] = {}
    try:
        for target, content in ((stf_path, package), (html_path, html)):
            fd, temp_path = tempfile.mkstemp(prefix='.%s.' % os.path.basename(target),
                                             suffix='.tmp', dir=directory)
            temporary.append(temp_path)
            with os.fdopen(fd, 'wb') as fid:
                fid.write(content)
                fid.flush()
                os.fsync(fid.fileno())
        for target in (stf_path, html_path):
            if os.path.exists(target):
                fd, backup_path = tempfile.mkstemp(prefix='.%s.' % os.path.basename(target),
                                                    suffix='.backup', dir=directory)
                os.close(fd)
                shutil.copy2(target, backup_path)
                backups[target] = backup_path
            else:
                backups[target] = None
        # Publish presentation first and the authoritative package last.  A
        # process interruption can therefore produce a detectable stale HTML,
        # never an apparently valid new package paired with an old report.
        html_temp = temporary[1]
        os.replace(html_temp, html_path)
        temporary.remove(html_temp)
        stf_temp = temporary[0]
        os.replace(stf_temp, stf_path)
        temporary.remove(stf_temp)
    except Exception:
        for target in (stf_path, html_path):
            backup = backups.get(target)
            try:
                if backup is not None:
                    os.replace(backup, target)
                    backups[target] = None
                elif target in backups and os.path.exists(target):
                    os.unlink(target)
            except OSError:
                pass
        raise
    finally:
        for temp_path in temporary:
            try:
                os.unlink(temp_path)
            except FileNotFoundError:
                pass
        for backup_path in backups.values():
            if backup_path is not None:
                try:
                    os.unlink(backup_path)
                except FileNotFoundError:
                    pass
    return stf_path, html_path


def load_project_path(path: str) -> Project:
    extension = os.path.splitext(path)[1].lower()
    if extension == '.html':
        with open(path, 'rb') as fid:
            expected_id = html_project_id(fid.read(1024 * 1024))
        if expected_id is None:
            raise ProjectError('HTML file is not a Stoichiometry Fitter project report.')
        stf_path = os.path.splitext(path)[0] + '.stf'
        if not os.path.isfile(stf_path):
            raise ProjectError('The matching adjacent .stf project package is missing.')
        project = load_project_path(stf_path)
        if project.project_id != expected_id:
            raise ProjectError('The adjacent .stf is stale or belongs to a different project.')
        return project
    if extension != '.stf':
        raise ProjectError('Expected a .stf package or matching .html report.')
    with open(path, 'rb') as fid:
        return load_stf_stream(fid)


def rerun_project(project: Project, config_dir: str = core.CONFIG_DIR,
                  phase_analysis_dir: str = core.PHASE_ANALYSIS_DIR) -> Project:
    """Rerun with archived resources and currently installed algorithms."""
    archived_resources = project.resources if project.lifecycle == 'calculated' else None
    current = core.calculation_fingerprint(archived_resources, project.options.phase_analysis,
                                           phase_analysis_dir)
    stored_algorithms = project.calculation_fingerprint.get('algorithm_hashes', {})
    mismatch = bool(stored_algorithms and stored_algorithms != current.get('algorithm_hashes', {}))
    result = core.run_analysis(project.input, options=project.options,
                               resolved_resources=archived_resources,
                               config_dir=config_dir, phase_analysis_dir=phase_analysis_dir)
    if mismatch:
        result.warnings.insert(0, 'This project was calculated with a different algorithm fingerprint; rerun results may differ from the archived snapshot.')
    project.lifecycle = 'calculated'
    project.result = result
    project.calculation_fingerprint = result.calculation_fingerprint
    return project


# Input loader registry -----------------------------------------------------

Loader = Tuple[str, Callable[[bytes, str], bool], Callable[[bytes, str], core.AnalysisInput]]
_LOADERS: List[Loader] = []
LEGACY_ELEMENT_SYMBOLS = {
    # IUPAC's temporary names appear in historic 118-row Stoichiometry Fitter
    # CSV files.  Accept them on import while always exporting current names.
    'Uut': 'Nh', 'Uup': 'Mc', 'Uus': 'Ts', 'Uuo': 'Og',
}


def register_input_loader(name: str, detector: Callable[[bytes, str], bool],
                          loader: Callable[[bytes, str], core.AnalysisInput],
                          prepend: bool = False) -> None:
    entry = (name, detector, loader)
    if prepend:
        _LOADERS.insert(0, entry)
    else:
        _LOADERS.append(entry)


def _decode_text(data: bytes) -> str:
    for encoding in ('utf-8-sig', 'cp1252'):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ProjectError('Input is not valid UTF-8 or Windows text.')


def _first_data_line(data: bytes) -> str:
    for line in _decode_text(data).splitlines():
        if line.strip() and not line.lstrip().startswith('#'):
            return line
    return ''


def _legacy_csv_detect(data: bytes, filename: str) -> bool:
    first = _first_data_line(data[:4096]) if data else ''
    normalized = re.sub(r'\s+', '', first).lower()
    return normalized.startswith('element,') and any(
        token in normalized for token in ('counts', 'at%', 'atpct', 'wt%', 'wtpct', 'oxwt'))


def _legacy_csv_load(data: bytes, filename: str) -> core.AnalysisInput:
    rows = list(csv.reader(StringIO(_decode_text(data))))
    rows = [row for row in rows if row and not row[0].lstrip().startswith('#')]
    if not rows or len(rows[0]) < 2:
        raise ProjectError('Input CSV header is missing.')
    header = re.sub(r'[\s_]+', '', rows[0][1]).lower()
    types = {'counts': 'Counts', 'at%': 'At %', 'atpct': 'At %', 'at': 'At %',
             'wt%': 'Wt %', 'wtpct': 'Wt %', 'wt': 'Wt %',
             'oxwt%': 'Ox Wt %', 'oxwtpct': 'Ox Wt %', 'oxwt': 'Ox Wt %'}
    if header not in types:
        raise ProjectError('Unsupported Stoichiometry Fitter CSV value column.')
    values = core.empty_element_dict()
    seen = set()
    for row_number, row in enumerate(rows[1:], start=2):
        if len(row) < 2:
            raise ProjectError('CSV row %d has fewer than two columns.' % row_number)
        element = LEGACY_ELEMENT_SYMBOLS.get(row[0].strip(), row[0].strip())
        if element not in values or element in seen:
            raise ProjectError('CSV contains an unknown or duplicate element: %s' % element)
        values[element] = _finite(row[1].strip(), 'CSV row %d' % row_number)
        seen.add(element)
    if len(seen) != pb.MAXELEMENT:
        raise ProjectError('Expected %d element rows, got %d.' % (pb.MAXELEMENT, len(seen)))
    return core.AnalysisInput(dict(values), types[header])


def _bruker_detect(data: bytes, filename: str) -> bool:
    return data.startswith(b'Spectrum: ')


def _bruker_load(data: bytes, filename: str) -> core.AnalysisInput:
    values = core.empty_element_dict()
    parsed = 0
    for line in _decode_text(data).splitlines()[5:]:
        fields = line.split()
        if len(fields) < 4:
            continue
        candidates = [field for field in fields[:2] if field in values]
        if not candidates:
            continue
        try:
            count = float(fields[3])
        except ValueError:
            continue
        values[candidates[0]] += _finite(count, 'Bruker count')
        parsed += 1
    if not parsed:
        raise ProjectError('Bruker input contains no recognized element counts.')
    return core.AnalysisInput(dict(values), 'Counts')


def _hyperspy_detect(data: bytes, filename: str) -> bool:
    first = _first_data_line(data[:4096]).lower() if data else ''
    return first.startswith('hyperspy') or ('name' in first and 'area' in first)


def _hyperspy_load(data: bytes, filename: str) -> core.AnalysisInput:
    text = _decode_text(data)
    lines = text.splitlines()
    if lines and lines[0].lower().startswith('hyperspy') and 'name' not in lines[0].lower():
        lines = lines[1:]
    reader = csv.DictReader(lines)
    if not reader.fieldnames or 'Name' not in reader.fieldnames or 'Area' not in reader.fieldnames:
        raise ProjectError('HyperSpy CSV must contain Name and Area columns.')
    values = core.empty_element_dict()
    parsed = 0
    for row in reader:
        name = (row.get('Name') or '').strip()
        match = re.match(r'^([A-Z][a-z]?)_(.+)$', name)
        if not match or match.group(1) not in values or 'K' not in match.group(2):
            continue
        values[match.group(1)] += _finite(row.get('Area'), 'HyperSpy peak area')
        parsed += 1
    if not parsed:
        raise ProjectError('HyperSpy input contains no recognized K-shell peak areas.')
    return core.AnalysisInput(dict(values), 'Counts')


register_input_loader('bruker', _bruker_detect, _bruker_load)
register_input_loader('hyperspy', _hyperspy_detect, _hyperspy_load)
register_input_loader('stoichiometry-fitter-csv', _legacy_csv_detect, _legacy_csv_load)


def detect_and_load_input_bytes(data: bytes, filename: str = 'input') -> ImportedInput:
    if not isinstance(data, bytes):
        raise TypeError('Input data must be bytes.')
    for name, detector, loader in _LOADERS:
        try:
            matches = detector(data, filename)
        except (UnicodeDecodeError, ProjectError):
            matches = False
        if matches:
            analysis_input = loader(data, filename)
            return ImportedInput(analysis_input,
                                 OriginalSource(filename, name, data))
    raise ProjectError('Unsupported input format. Expected Stoichiometry Fitter CSV, Bruker text, or HyperSpy CSV.')


def validate_original_source(source: OriginalSource) -> None:
    """Ensure archived source bytes are an actually supported measurement input.

    A source file is retained for provenance only.  Re-detecting it here means
    an STF cannot use that otherwise opaque member to carry arbitrary binary
    payloads under a benign archive path.
    """
    try:
        imported = detect_and_load_input_bytes(source.content, source.filename)
    except (ProjectError, UnicodeDecodeError) as exc:
        raise ProjectError('Archived original source is not a supported input file.') from exc
    if imported.source.detected_format != source.detected_format:
        raise ProjectError('Archived original source format does not match its metadata.')


def detect_and_load_input_stream(stream, filename: str = 'input') -> ImportedInput:
    data = stream.read(MAX_ARCHIVE_SIZE + 1)
    if len(data) > MAX_ARCHIVE_SIZE:
        raise ProjectError('Input file is too large.')
    return detect_and_load_input_bytes(data, filename)


def detect_and_load_path(path: str) -> Any:
    extension = os.path.splitext(path)[1].lower()
    if extension in ('.stf', '.html'):
        return load_project_path(path)
    with open(path, 'rb') as fid:
        return detect_and_load_input_stream(fid, os.path.basename(path))
