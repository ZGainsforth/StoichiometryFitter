"""Shared, portable output types for built-in phase-analysis plugins."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from io import StringIO
import re
from typing import Any, Dict, Iterable, List, Optional



@dataclass
class ImageArtifact:
    """A self-contained image returned by a phase analysis."""

    id: str
    title: str
    mime_type: str
    payload: str
    alt_text: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


def svg_artifact(figure, artifact_id: str, title: str, alt_text: str) -> ImageArtifact:
    """Serialize a locally owned Matplotlib figure as the canonical SVG payload."""
    from matplotlib import rc_context
    output = StringIO()
    # Suppress Matplotlib's generated timestamp so saved/replayed analyses are
    # byte-for-byte reproducible.
    with rc_context({'svg.hashsalt': 'stoichiometry-fitter'}):
        figure.savefig(output, format='svg', bbox_inches='tight', metadata={'Date': None})
    return ImageArtifact(artifact_id, title, 'image/svg+xml', output.getvalue(), alt_text)


def _slug(text: str) -> str:
    return re.sub(r'[^0-9A-Za-z]+', '_', text.strip().lower()).strip('_') or 'table'


def tables_from_report(name: str, report_text: str) -> List[Dict[str, Any]]:
    """Expose the numeric data already emitted in a built-in plugin report as tables.

    Plugins use this while constructing their result, so consumers never need to
    parse a built-in plugin's text output.  The core's similar legacy adapter is
    reserved for un-migrated third-party plugins.
    """
    lines = report_text.splitlines()
    tables: List[Dict[str, Any]] = []
    ratio_rows = []
    ratio_re = re.compile(r'^\s*([^:=]+?)\s*=\s*([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)\b(.*)$')
    for line in lines:
        match = ratio_re.match(line)
        if match and match.group(1).strip():
            ratio_rows.append({'metric': match.group(1).strip(),
                               'value': float(match.group(2)),
                               'note': match.group(3).strip()})
    if ratio_rows:
        tables.append({
            'name': 'phase_analysis_%s_numeric_results' % _slug(name),
            'title': '%s Numeric Results' % name,
            'columns': ['metric', 'value', 'note'],
            'rows': ratio_rows,
            'metadata': {'phase_analysis': name},
            'description': 'Numeric ratio and scalar results from the %s phase analysis.' % name,
        })

    row_re = re.compile(r'^\s*([^:]+):\s*([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)\b')
    index = 0
    while index < len(lines):
        heading = lines[index].strip()
        if not heading.endswith(':'):
            index += 1
            continue
        cursor = index + 1
        while cursor < len(lines) and lines[cursor].strip() and row_re.match(lines[cursor]) is None:
            cursor += 1
        rows = []
        while cursor < len(lines):
            match = row_re.match(lines[cursor])
            if match is None:
                break
            rows.append({'label': match.group(1).strip(), 'value': float(match.group(2))})
            cursor += 1
        if rows:
            tables.append({
                'name': 'phase_analysis_%s_%s' % (_slug(name), _slug(heading[:-1])),
                'title': '%s - %s' % (name, heading[:-1]),
                'columns': ['label', 'value'],
                'rows': rows,
                'metadata': {'phase_analysis': name},
                'description': 'Numeric table from the %s phase analysis.' % name,
            })
            index = cursor
        else:
            index += 1
    return tables


def phase_output(name: str, report_text: str, *, tables: Optional[Iterable[Dict[str, Any]]] = None,
                 figures: Optional[Iterable[ImageArtifact]] = None,
                 warnings: Optional[Iterable[str]] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return the phase-analysis output contract used by every built-in plugin."""
    return {
        'report_text': report_text,
        'tables': list(tables) if tables is not None else tables_from_report(name, report_text),
        'figures': list(figures or []),
        'warnings': list(warnings or []),
        'metadata': dict(metadata or {}),
    }
