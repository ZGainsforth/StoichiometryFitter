"""Scriptable service layer for Stoichiometry Fitter analyses."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import asdict, dataclass, field
import importlib.util
import json
import os
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

import CountsToQuant
import PhaseFit
import PhysicsBasics as pb
import ReportResults
from PhaseAnalysis.contract import ImageArtifact, svg_artifact


CONFIG_DIR = 'ConfigData'
PHASE_ANALYSIS_DIR = 'PhaseAnalysis'


@dataclass
class ResultTable:
    name: str
    title: str
    columns: List[str]
    rows: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    description: str = ''


@dataclass
class AnalysisInput:
    values: Dict[str, float]
    input_type: str = 'Counts'
    stoichiometry: Optional[List[float]] = None
    stoichiometry_name: Optional[str] = None


@dataclass
class AnalysisOptions:
    kfactors: Optional[str] = None
    arbitrary_absorption: Optional[str] = None
    absorption_correction: float = 0.0
    takeoff: float = 18.0
    selected_phases: Optional[List[str]] = None
    phase_analysis: Optional[str] = None
    phase_analysis_kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    input: AnalysisInput
    options: AnalysisOptions
    tables: List[ResultTable]
    report_text: str
    quant: Dict[str, Dict[str, float]]
    phase_analysis: Optional[Dict[str, Any]] = None
    figures: List[ImageArtifact] = field(default_factory=list, repr=False)
    warnings: List[str] = field(default_factory=list)
    files: Dict[str, str] = field(default_factory=dict)


@dataclass
class SavedFiles:
    input_csv: str
    report_txt: str
    results_json: str
    figures: List[str] = field(default_factory=list)
    legacy_phase_files: List[str] = field(default_factory=list)


def normalize_input_type(input_type: str) -> str:
    aliases = {
        'At%': 'At %',
        'AtPct': 'At %',
        'Wt%': 'Wt %',
        'WtPct': 'Wt %',
        'OxWt%': 'Ox Wt %',
        'OxWtPct': 'Ox Wt %',
    }
    return aliases.get(input_type, input_type)


def empty_element_dict() -> OrderedDict:
    return OrderedDict((symbol, 0.0) for symbol in pb.ElementalSymbols[1:])


def values_to_vector(values: Any) -> np.ndarray:
    if isinstance(values, np.ndarray):
        vector = values.astype(float, copy=True)
    elif isinstance(values, dict):
        vector = np.zeros(pb.MAXELEMENT)
        for symbol, value in values.items():
            if symbol not in pb.ElementalSymbols:
                raise ValueError('Unknown element symbol: %s' % symbol)
            if symbol == 'None':
                continue
            vector[pb.ElementalSymbols.index(symbol) - 1] = float(value)
    else:
        vector = np.array(list(values), dtype=float)

    if len(vector) != pb.MAXELEMENT:
        raise ValueError('Expected %d element values, got %d' % (pb.MAXELEMENT, len(vector)))
    return vector


def vector_to_element_dict(vector: Sequence[float]) -> OrderedDict:
    if len(vector) != pb.MAXELEMENT:
        raise ValueError('Expected %d element values, got %d' % (pb.MAXELEMENT, len(vector)))
    return OrderedDict((pb.ElementalSymbols[i + 1], float(vector[i])) for i in range(pb.MAXELEMENT))


def load_stoichiometry(name: str, config_dir: str = CONFIG_DIR) -> List[float]:
    path = os.path.join(config_dir, 'Stoich ' + name + '.csv')
    stoich = np.genfromtxt(path, dtype=None, comments='#', delimiter=',', skip_header=1,
                           converters={1: lambda s: float(s)})
    return [float(charge) for _, charge in stoich]


def load_phases(config_dir: str = CONFIG_DIR):
    return np.genfromtxt(os.path.join(config_dir, 'Phases.csv'), dtype=None, comments='#',
                         delimiter=',', converters={1: lambda s: str(s).lstrip()})


def phase_analysis_path(name: str, phase_analysis_dir: str = PHASE_ANALYSIS_DIR) -> str:
    return os.path.join(phase_analysis_dir, name + '.py')


def list_config_options(config_dir: str = CONFIG_DIR,
                        phase_analysis_dir: str = PHASE_ANALYSIS_DIR) -> Dict[str, List[str]]:
    files = os.listdir(config_dir)
    phase_files = os.listdir(phase_analysis_dir)
    return {
        'kfactors': sorted(f.split('kfacs ')[1].split('.csv')[0] for f in files
                           if f.startswith('kfacs ') and f.endswith('.csv')),
        'stoichiometry': sorted(f.split('Stoich ')[1].split('.csv')[0] for f in files
                                if f.startswith('Stoich ') and f.endswith('.csv')),
        'arbitrary_absorption': sorted(f.split('Absorption ')[1].split('.csv')[0] for f in files
                                       if f.startswith('Absorption ') and f.endswith('.csv')),
        'phase_analysis': sorted(os.path.splitext(f)[0] for f in phase_files
                                 if f.endswith('.py') and f not in ('__init__.py', 'contract.py',
                                                                     'ternary_diagram.py')),
    }


def load_input_csv(path: str) -> AnalysisInput:
    data = np.genfromtxt(path, dtype=float, delimiter=',', usecols=(1), autostrip=True,
                         comments='#', names=True)
    if len(data) != pb.MAXELEMENT:
        raise ValueError('Expected %d rows in input CSV, got %d' % (pb.MAXELEMENT, len(data)))

    header = data.dtype.names[0]
    if header == 'Counts':
        input_type = 'Counts'
    elif header == 'At':
        input_type = 'At %'
    elif header == 'Wt':
        input_type = 'Wt %'
    elif header == 'OxWt':
        input_type = 'Ox Wt %'
    else:
        raise ValueError('Unsupported input CSV value column: %s' % header)

    return AnalysisInput(values=dict(vector_to_element_dict([float(row[0]) for row in data])),
                         input_type=input_type)


def _coerce_input(input_data: Any, input_type: str = 'Counts') -> AnalysisInput:
    if isinstance(input_data, AnalysisInput):
        input_data.input_type = normalize_input_type(input_data.input_type)
        return input_data
    return AnalysisInput(values=dict(vector_to_element_dict(values_to_vector(input_data))),
                         input_type=normalize_input_type(input_type))


def _coerce_options(options: Optional[Any]) -> AnalysisOptions:
    if options is None:
        return AnalysisOptions()
    if isinstance(options, AnalysisOptions):
        return options
    if isinstance(options, dict):
        return AnalysisOptions(**options)
    raise TypeError('options must be AnalysisOptions, dict, or None')


def _table_from_dict(table: Dict[str, Any]) -> ResultTable:
    return ResultTable(
        name=table['name'],
        title=table.get('title') or table['name'].replace('_', ' ').title(),
        columns=list(table['columns']),
        rows=list(table['rows']),
        metadata=dict(table.get('metadata', {})),
        description=table.get('description', ''),
    )


def _import_function_from_path(function_name: str, path: str):
    spec = importlib.util.spec_from_file_location('stoich_phase_plugin', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function_name)


def _slug(text: str) -> str:
    slug = re.sub(r'[^0-9A-Za-z]+', '_', text.strip().lower()).strip('_')
    return slug or 'table'


def _legacy_phase_tables(name: str, report_text: str) -> List[ResultTable]:
    """Extract useful numeric tables from legacy phase-analysis text output."""
    lines = report_text.splitlines()
    tables = []

    ratio_rows = []
    ratio_re = re.compile(r'^\s*([^:=]+?)\s*=\s*([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)\b(.*)$')
    for line in lines:
        match = ratio_re.match(line)
        if match is None:
            continue
        metric = match.group(1).strip()
        if not metric:
            continue
        ratio_rows.append({
            'metric': metric,
            'value': float(match.group(2)),
            'note': match.group(3).strip(),
        })

    if ratio_rows:
        tables.append(ResultTable(
            name='phase_analysis_%s_numeric_results' % _slug(name),
            title='%s Numeric Results' % name,
            columns=['metric', 'value', 'note'],
            rows=ratio_rows,
            metadata={'phase_analysis': name},
            description='Numeric ratio and scalar results parsed from the %s phase analysis.' % name,
        ))

    row_re = re.compile(r'^\s*([^:]+):\s*([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)\b')
    index = 0
    while index < len(lines):
        heading = lines[index].strip()
        if not heading.endswith(':'):
            index += 1
            continue

        # Legacy reports usually put a text header on the next line, then rows as "label: number".
        cursor = index + 1
        while cursor < len(lines) and lines[cursor].strip() and row_re.match(lines[cursor]) is None:
            cursor += 1

        rows = []
        while cursor < len(lines):
            row_match = row_re.match(lines[cursor])
            if row_match is None:
                break
            rows.append({
                'label': row_match.group(1).strip(),
                'value': float(row_match.group(2)),
            })
            cursor += 1

        if rows:
            tables.append(ResultTable(
                name='phase_analysis_%s_%s' % (_slug(name), _slug(heading[:-1])),
                title='%s - %s' % (name, heading[:-1]),
                columns=['label', 'value'],
                rows=rows,
                metadata={'phase_analysis': name},
                description='Numeric table parsed from the %s phase analysis.' % name,
            ))
            index = cursor
        else:
            index += 1

    return tables


def _run_phase_analysis(name: str, at_pct, wt_pct, ox_wt_pct, stoich, kwargs,
                        phase_analysis_dir: str):
    path = phase_analysis_path(name, phase_analysis_dir)
    analyze_phase = _import_function_from_path('AnalyzePhase', path)
    output = analyze_phase(at_pct, wt_pct, ox_wt_pct, stoich, **kwargs)

    if isinstance(output, dict):
        required = {'report_text', 'tables', 'figures', 'warnings'}
        missing = required.difference(output)
        if missing:
            raise ValueError('phase-analysis output is missing required field(s): %s' %
                             ', '.join(sorted(missing)))
        report_text = output['report_text']
        if not isinstance(report_text, str):
            raise TypeError('phase-analysis report_text must be a string')
        tables = [_table_from_dict(t) if isinstance(t, dict) else t for t in output['tables']]
        if not all(isinstance(table, ResultTable) for table in tables):
            raise TypeError('phase-analysis tables must contain result-table objects or dictionaries')
        figures = []
        for figure in output['figures']:
            if isinstance(figure, dict):
                figure = ImageArtifact(**figure)
            if not isinstance(figure, ImageArtifact):
                raise TypeError('phase-analysis figures must be ImageArtifact objects or dictionaries')
            if figure.mime_type != 'image/svg+xml' or not isinstance(figure.payload, str):
                raise ValueError('phase-analysis figures must contain SVG text artifacts')
            figures.append(figure)
        warnings = output['warnings']
        if not isinstance(warnings, (list, tuple)) or not all(isinstance(warning, str) for warning in warnings):
            raise TypeError('phase-analysis warnings must be a list of strings')
        normalized = {
            'report_text': report_text,
            'tables': [asdict(table) for table in tables],
            'figures': [asdict(figure) for figure in figures],
            'warnings': list(warnings),
            'metadata': dict(output.get('metadata', {})),
        }
        return report_text, tables, figures, list(warnings), normalized

    report_text, figures = output
    if figures is None:
        figures = []
    elif not isinstance(figures, (list, tuple)):
        figures = [figures]
    legacy_artifacts = []
    for index, figure in enumerate(figures, start=1):
        if isinstance(figure, ImageArtifact):
            legacy_artifacts.append(figure)
        elif hasattr(figure, 'savefig'):
            legacy_artifacts.append(svg_artifact(
                figure, '%s_figure_%d' % (_slug(name), index),
                '%s figure %d' % (name, index), '%s phase-analysis figure %d' % (name, index)))
    return (report_text, _legacy_phase_tables(name, report_text), legacy_artifacts, [],
            {'name': name, 'legacy_output': True})


def quant_to_dict(quant) -> Dict[str, Dict[str, float]]:
    return OrderedDict((el, {
        'at_pct': float(values[0]),
        'wt_pct': float(values[1]),
        'oxide_wt_pct': float(values[2]),
        'k_factor': float(values[3]),
    }) for el, values in quant.items() if el not in ('_nonzero_input_', '_zero_kfactor_'))


def run_analysis(input_data: Any, input_type: str = 'Counts', options: Optional[Any] = None,
                 save_dir: Optional[str] = None, basename: str = 'analysis',
                 config_dir: str = CONFIG_DIR,
                 phase_analysis_dir: str = PHASE_ANALYSIS_DIR) -> AnalysisResult:
    analysis_input = _coerce_input(input_data, input_type)
    analysis_options = _coerce_options(options)

    counts = values_to_vector(analysis_input.values)
    stoich = analysis_input.stoichiometry
    if stoich is None and analysis_input.stoichiometry_name:
        stoich = load_stoichiometry(analysis_input.stoichiometry_name, config_dir=config_dir)
    stoich_array = None if stoich is None else np.array(stoich, dtype=float)

    input_dict = vector_to_element_dict(counts)
    input_table = _table_from_dict(ReportResults.BuildInputTable(input_dict, analysis_input.input_type))
    report_parts = [ReportResults.FormatInputResults(input_dict, analysis_input.input_type)]

    quant = CountsToQuant.GetAbundancesFromCounts(
        counts,
        kfacsfile=analysis_options.kfactors,
        InputType=analysis_input.input_type,
        ArbitraryAbsorptionCorrection=analysis_options.arbitrary_absorption,
        AbsorptionCorrection=analysis_options.absorption_correction,
        Takeoff=analysis_options.takeoff,
        OByStoichiometry=stoich_array,
    )
    if quant is None:
        raise ValueError('Quantification failed for input type %s' % analysis_input.input_type)

    quant_table = _table_from_dict(ReportResults.BuildQuantTable(quant, stoich_array))
    report_parts.append(ReportResults.FormatQuantResults(
        quant,
        ArbitraryAbsorptionCorrection=analysis_options.arbitrary_absorption,
        AbsorptionCorrection=analysis_options.absorption_correction,
        Takeoff=analysis_options.takeoff,
        OByStoichiometry=stoich_array,
        kFactors=analysis_options.kfactors,
    ))

    tables = [input_table, quant_table]
    quant_numbers = [a[1] for a in list(quant.items()) if a[0] not in ('_nonzero_input_', '_zero_kfactor_')]
    at_pct, wt_pct, ox_wt_pct, _ = list(zip(*quant_numbers))

    if analysis_options.selected_phases:
        phases = load_phases(config_dir=config_dir)
        phases_to_fit = [phase for phase in phases if phase[0] in analysis_options.selected_phases]
        if phases_to_fit:
            # ``GetAbundancesFromCounts`` annotates its element mapping with
            # bookkeeping entries such as ``_nonzero_input_``.  PhaseFit
            # expects only the 118 element abundance tuples.
            phase_quant = OrderedDict(
                (element, values) for element, values in quant.items()
                if element not in ('_nonzero_input_', '_zero_kfactor_')
            )
            fit_result, residual, fit_composition = PhaseFit.FitPhases(phase_quant, phases_to_fit)
            phase_tables = [_table_from_dict(t) for t in ReportResults.BuildPhaseTables(
                fit_result, residual, fit_composition)]
            tables.extend(phase_tables)
            report_parts.append(ReportResults.FormatPhaseResults(fit_result, residual, fit_composition))

    phase_payload = None
    figures = []
    warnings = []

    # Extract zero k-factor warnings for GUI display.
    zero_kfactor = quant.get('_zero_kfactor_', [])
    for el in zero_kfactor:
        warnings.append(f'Element {el} has zero k-factor in "{analysis_options.kfactors}" — appears with 0% abundance.')
    if analysis_options.phase_analysis:
        try:
            phase_report, phase_tables, figures, phase_warnings, phase_payload = _run_phase_analysis(
                analysis_options.phase_analysis,
                np.array(at_pct, dtype=float),
                np.array(wt_pct, dtype=float),
                np.array(ox_wt_pct, dtype=float),
                stoich_array,
                analysis_options.phase_analysis_kwargs,
                phase_analysis_dir,
            )
            if phase_report:
                report_parts.append(phase_report)
            tables.extend(phase_tables)
            warnings.extend(phase_warnings)
        except Exception as exc:
            warnings.append('Phase analysis "%s" failed: %s' % (analysis_options.phase_analysis, exc))

    result = AnalysisResult(
        input=analysis_input,
        options=analysis_options,
        tables=tables,
        report_text=''.join(report_parts),
        quant=quant_to_dict(quant),
        phase_analysis=phase_payload,
        figures=figures,
        warnings=warnings,
    )

    if save_dir is not None:
        saved = save_analysis(result, save_dir, basename=basename, config_dir=config_dir,
                              phase_analysis_dir=phase_analysis_dir)
        result.files = asdict(saved)

    return result


def _json_default(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if hasattr(value, 'to_json'):
        return value.to_json()
    return str(value)


def analysis_to_dict(result: AnalysisResult) -> Dict[str, Any]:
    return {
        'schema_version': 2,
        'input': asdict(result.input),
        'options': asdict(result.options),
        'text_output': result.report_text,
        'tables': [asdict(table) for table in result.tables],
        'phase_analysis': result.phase_analysis,
        'figures': [asdict(figure) for figure in result.figures],
        'warnings': list(result.warnings),
    }


def load_analysis_json(path: str) -> Tuple[AnalysisInput, AnalysisOptions]:
    """Load replayable inputs and options from a saved Stoichiometry Fitter JSON file."""
    with open(path) as fid:
        payload = json.load(fid)

    if 'input' not in payload or 'options' not in payload:
        raise ValueError('JSON file does not contain replayable input and options.')

    analysis_input = AnalysisInput(**payload['input'])
    analysis_input.input_type = normalize_input_type(analysis_input.input_type)
    analysis_options = AnalysisOptions(**payload['options'])
    return analysis_input, analysis_options


def rerun_analysis_from_json(path: str, save_dir: Optional[str] = None,
                             basename: str = 'analysis',
                             config_dir: str = CONFIG_DIR,
                             phase_analysis_dir: str = PHASE_ANALYSIS_DIR) -> AnalysisResult:
    """Reproduce an analysis from a saved JSON file."""
    analysis_input, analysis_options = load_analysis_json(path)
    return run_analysis(analysis_input, options=analysis_options, save_dir=save_dir,
                        basename=basename, config_dir=config_dir,
                        phase_analysis_dir=phase_analysis_dir)


def save_input_csv(analysis_input: AnalysisInput, path: str) -> None:
    header_by_type = {
        'Counts': 'Counts',
        'At %': 'At%',
        'Wt %': 'Wt%',
        'Ox Wt %': 'OxWt%',
    }
    input_type = normalize_input_type(analysis_input.input_type)
    header = header_by_type[input_type]
    values = vector_to_element_dict(values_to_vector(analysis_input.values))
    with open(path, 'w') as fid:
        fid.write('Element,%s\n' % header)
        for element, value in values.items():
            fid.write('%s,%f\n' % (element, value))


def save_analysis(result: AnalysisResult, output_dir: str, basename: str = 'analysis',
                  config_dir: str = CONFIG_DIR,
                  phase_analysis_dir: str = PHASE_ANALYSIS_DIR) -> SavedFiles:
    os.makedirs(output_dir, exist_ok=True)
    input_csv = os.path.join(output_dir, basename + '.csv')
    report_txt = os.path.join(output_dir, basename + '.txt')
    results_json = os.path.join(output_dir, basename + '.json')

    save_input_csv(result.input, input_csv)
    with open(report_txt, 'w') as fid:
        fid.write(result.report_text)

    figure_paths = []
    used_names = set()
    for index, figure in enumerate(result.figures, start=1):
        artifact_name = _slug(figure.id) or 'figure_%d' % index
        if artifact_name in used_names:
            artifact_name = '%s_%d' % (artifact_name, index)
        used_names.add(artifact_name)
        path = os.path.join(output_dir, '%s_%s.svg' % (basename, artifact_name))
        with open(path, 'w', encoding='utf-8') as fid:
            fid.write(figure.payload)
        figure_paths.append(path)

    # Built-in plugins return self-contained artifacts.  Legacy third-party
    # SaveResults hooks are intentionally not invoked: analysis is now pure.
    legacy_phase_files = []

    saved = SavedFiles(input_csv=input_csv, report_txt=report_txt, results_json=results_json,
                       figures=figure_paths, legacy_phase_files=legacy_phase_files)
    result.files = asdict(saved)
    with open(results_json, 'w') as fid:
        json.dump(analysis_to_dict(result), fid, indent=2, sort_keys=True, default=_json_default)
    return saved
