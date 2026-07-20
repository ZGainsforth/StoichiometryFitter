"""FastAPI application for Stoichiometry Fitter.

Wraps existing Python modules without modifying them.
Serves static frontend files and exposes JSON API routes.
"""

from __future__ import annotations

import csv
import io
import json
import os
import sys
import threading
from collections import deque
from dataclasses import asdict
from typing import Any, Dict, List, Optional
from collections import defaultdict

# Project root (backend/ is NOT on sys.path when running this script)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ProjectPackage as package
import StoichiometryCore as core
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# --- Project root ---
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(APP_DIR, 'ConfigData')
FRONTEND_DIR = os.path.join(APP_DIR, 'frontend')

# --- Threading lock for analysis ---
_analysis_lock = threading.Lock()

# --- Rate limiter ---
class RunRateLimiter:
    def __init__(self, maximum: int = 10, window_seconds: int = 60):
        self.maximum = maximum
        self.window_seconds = window_seconds
        self._requests: Dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = __import__('time').monotonic()
        with self._lock:
            requests = self._requests[key]
            while requests and now - requests[0] >= self.window_seconds:
                requests.popleft()
            if len(requests) >= self.maximum:
                return False
            requests.append(now)
            return True

_run_limiter = RunRateLimiter()

# --- Pydantic models for API ---
class AnalysisRequest(BaseModel):
    values: Dict[str, float]
    input_type: str = 'Counts'
    stoichiometry_name: Optional[str] = None
    kfactors: Optional[str] = None
    arbitrary_absorption: Optional[str] = None
    absorption_correction: Optional[float] = None
    takeoff: float = 18.0
    selected_phases: Optional[List[str]] = None
    phase_analysis: Optional[str] = None

class ElementValueRequest(BaseModel):
    symbol: str
    value: float

# --- Helper functions ---
def _safe_error(error: Exception) -> str:
    if isinstance(error, (package.ProjectError, ValueError, TypeError)):
        return str(error)
    return 'Unable to process this request.'

def _get_element_categories() -> Dict[str, str]:
    """Get element-to-category mapping from Python periodic table module."""
    try:
        import prototypes.periodic_table as pt
        return {symbol: entry[4] for symbol, entry in pt.ELEMENT_BY_SYMBOL.items()}
    except Exception:
        return {}

def _get_config_options() -> Dict[str, Any]:
    """Get available configuration options from ConfigData."""
    catalog = core.list_resource_options()
    return {
        'kfactors': catalog.get('kfactors', []),
        'stoichiometry': catalog.get('stoichiometry', []),
        'arbitrary_absorption': catalog.get('arbitrary_absorption', []),
        'selected_phases': catalog.get('selected_phases', []),
        'phase_analysis': catalog.get('phase_analysis', []),
    }

def _get_elements_data() -> List[Dict[str, Any]]:
    """Get full 118-element periodic table data."""
    elements = []
    for sym in core.pb.ElementalSymbols[1:]:
        elements.append({
            'symbol': sym,
            'atomic_number': core.pb.ElementalSymbols.index(sym),
            'value': 0.0,
        })
    return elements

def _load_example() -> Dict[str, Any]:
    """Load ExampleInput.csv and return parsed element values."""
    example_path = os.path.join(CONFIG_DIR, 'ExampleInput.csv')
    values = {}
    with open(example_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbol = row.get('Element', '')
            if symbol and symbol not in ('Uut', 'Uup', 'Uus', 'Uuo'):
                try:
                    values[symbol] = float(row.get('Counts', 0))
                except (ValueError, TypeError):
                    pass
    return {'values': values}

def _parse_upload(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """Parse an uploaded file (.csv, .stf) and return all input data and settings."""
    safe_name = package.safe_filename(filename)
    if safe_name.lower().endswith(('.html', '.htm')):
        raise package.ProjectError('HTML reports cannot be uploaded; upload the matching .stf package.')
    if safe_name.lower().endswith('.stf') or file_bytes.startswith(b'PK\x03\x04'):
        loaded = package.load_stf_bytes(file_bytes)
        if isinstance(loaded, package.Project):
            inp = loaded.input
            opts = loaded.options
            return {
                'values': inp.values,
                'input_type': inp.input_type,
                'stoichiometry_name': inp.stoichiometry_name,
                'stoichiometry': inp.stoichiometry,
                'kfactors': opts.kfactors,
                'arbitrary_absorption': opts.arbitrary_absorption,
                'absorption_correction': opts.absorption_correction,
                'takeoff': opts.takeoff,
                'selected_phases': opts.selected_phases,
                'phase_analysis': opts.phase_analysis,
                'phase_analysis_kwargs': {},
            }
        else:
            inp = loaded.analysis_input
            return {
                'values': inp.values,
                'input_type': inp.input_type,
                'stoichiometry_name': getattr(inp, 'stoichiometry_name', None),
                'stoichiometry': getattr(inp, 'stoichiometry', None),
                'kfactors': None,
                'arbitrary_absorption': None,
                'absorption_correction': None,
                'takeoff': None,
                'selected_phases': None,
                'phase_analysis': None,
                'phase_analysis_kwargs': {},
            }
    result = package.detect_and_load_input_bytes(file_bytes, safe_name)
    return {
        'values': result.analysis_input.values,
        'input_type': result.analysis_input.input_type,
        'stoichiometry_name': getattr(result.analysis_input, 'stoichiometry_name', None),
        'stoichiometry': getattr(result.analysis_input, 'stoichiometry', None),
        'kfactors': None,
        'arbitrary_absorption': None,
        'absorption_correction': None,
        'takeoff': None,
        'selected_phases': None,
        'phase_analysis': None,
        'phase_analysis_kwargs': {},
    }

def _build_corrections_list(req: AnalysisRequest, quant_data: Optional[Any] = None) -> List[Dict[str, str]]:
    """Build a list of correction factor key-value pairs for display."""
    corrections = []

    # k-factor file (only for Counts input with k-factors selected)
    if req.input_type == 'Counts' and req.kfactors:
        corrections.append({'key': 'k-factor file', 'value': req.kfactors})

    # Takeoff angle (only for Counts input with k-factors selected)
    if req.input_type == 'Counts' and req.kfactors:
        corrections.append({'key': 'takeoff angle', 'value': f'{req.takeoff:.1f}°'})

    # Absorption correction
    if req.absorption_correction is not None and req.absorption_correction != 0:
        corrections.append({'key': 'absorption correction', 'value': f'{req.absorption_correction:.3f} g/cm³·nm'})
    else:
        corrections.append({'key': 'absorption correction', 'value': 'none'})

    # Arbitrary absorption
    if req.arbitrary_absorption:
        corrections.append({'key': 'arbitrary absorption', 'value': req.arbitrary_absorption})
    else:
        corrections.append({'key': 'arbitrary absorption', 'value': '(disabled)'})

    # O by stoichiometry
    if req.stoichiometry_name:
        corrections.append({'key': 'oxygen by stoichiometry', 'value': f'yes ({req.stoichiometry_name})'})
    else:
        corrections.append({'key': 'oxygen by stoichiometry', 'value': 'no'})

    return corrections

# --- FastAPI App ---
app = FastAPI(title='Stoichiometry Fitter', version='1.0.0')

# CORS for web deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Serve static frontend files
if os.path.isdir(FRONTEND_DIR):
    app.mount('/static', StaticFiles(directory=FRONTEND_DIR), name='static')

# --- Favicon ---
@app.get('/favicon.ico')
async def favicon():
    """Serve the favicon.ico file."""
    favicon_path = os.path.join(FRONTEND_DIR, 'favicon.ico')
    if os.path.isfile(favicon_path):
        return FileResponse(favicon_path)
    # Return 204 No Content if no favicon exists
    return Response(status_code=204)

# --- Health check ---
@app.get('/healthz')
def healthz():
    return {'status': 'ok'}

# --- API Routes ---

@app.get('/api/elements')
def get_elements():
    """Get full periodic table data."""
    return _get_elements_data()

@app.get('/api/categories')
def get_categories():
    """Get element-to-category mapping."""
    return _get_element_categories()

@app.get('/api/config-options')
def get_config_options():
    """Get available configuration options."""
    return _get_config_options()

@app.get('/api/example')
def get_example():
    """Load ExampleInput.csv."""
    return _load_example()

@app.post('/api/upload')
async def upload_file(file: UploadFile = File(...)):
    """Handle file upload (.csv, .stf)."""
    file_bytes = await file.read()
    try:
        result = _parse_upload(file_bytes, file.filename or 'upload')
        # Return all parsed settings so frontend can restore the full project state
        return {
            'values': result['values'],
            'filename': file.filename,
            'input_type': result.get('input_type', 'Counts'),
            'stoichiometry_name': result.get('stoichiometry_name'),
            'stoichiometry': result.get('stoichiometry'),
            'kfactors': result.get('kfactors'),
            'arbitrary_absorption': result.get('arbitrary_absorption'),
            'absorption_correction': result.get('absorption_correction'),
            'takeoff': result.get('takeoff'),
            'selected_phases': result.get('selected_phases'),
            'phase_analysis': result.get('phase_analysis'),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=_safe_error(e))

def _build_analysis_input(req: AnalysisRequest) -> core.AnalysisInput:
    """Build AnalysisInput from request."""
    return core.AnalysisInput(
        values=req.values,
        input_type=req.input_type,
        stoichiometry_name=req.stoichiometry_name,
    )

def _build_analysis_options(req: AnalysisRequest) -> core.AnalysisOptions:
    """Build AnalysisOptions from request."""
    return core.AnalysisOptions(
        kfactors=req.kfactors if req.kfactors else None,
        arbitrary_absorption=req.arbitrary_absorption if req.arbitrary_absorption else None,
        absorption_correction=req.absorption_correction if req.absorption_correction is not None else 0.0,
        takeoff=req.takeoff,
        selected_phases=req.selected_phases if req.selected_phases else None,
        phase_analysis=req.phase_analysis if req.phase_analysis else None,
    )

@app.post('/api/quick-quant')
def quick_quant(req: AnalysisRequest):
    """Lightweight quantification: run analysis without phase analysis, no save.
    
    Returns quant results and correction factors only — no phase fitting.
    Called in real-time when user edits element values.
    """
    try:
        analysis_input = _build_analysis_input(req)
        options = _build_analysis_options(req)
        # Disable phase analysis for quick quant
        options.phase_analysis = None
        options.selected_phases = None
        package.validate_analysis_input(analysis_input)
        package.validate_options(options)
        core.validate_resource_selections(analysis_input, options)
        
        with _analysis_lock:
            result = core.run_analysis(analysis_input, options=options)
        
        # Build corrections list from result quant data
        corrections = _build_corrections_list(req, result.quant)
        
        # Return only quant and corrections (no tables, no phase analysis)
        output = {
            'quant': result.quant,
            'corrections': corrections,
        }
        return output
    except Exception as e:
        raise HTTPException(status_code=400, detail=_safe_error(e))

@app.post('/api/analysis')
def run_analysis(req: AnalysisRequest):
    """Run full analysis on element values + options."""
    client_id = 'api'
    if not _run_limiter.allow(client_id):
        raise HTTPException(status_code=429, detail='Too many requests. Please wait a minute.')

    try:
        analysis_input = _build_analysis_input(req)
        options = _build_analysis_options(req)

        with _analysis_lock:
            result = core.run_analysis(analysis_input, options=options)

        # Build corrections list
        corrections = _build_corrections_list(req, result.quant)

        # Convert result to JSON-serializable dict
        output = {
            'input_type': result.input.input_type,
            'tables': [],
            'report_text': result.report_text,
            'warnings': result.warnings,
            'quant': result.quant,
            'corrections': corrections,
            'figures': [asdict(f) for f in result.figures],
        }
        for table in result.tables:
            output['tables'].append({
                'title': table.title,
                'columns': table.columns,
                'rows': table.rows,
                'description': table.description,
            })
        return output
    except Exception as e:
        raise HTTPException(status_code=400, detail=_safe_error(e))

@app.put('/api/element/{symbol}')
def update_element(symbol: str, req: ElementValueRequest):
    """Update a single element value (for future use)."""
    return {'symbol': symbol, 'value': req.value}

# --- Download endpoints ---
def _build_download_analysis(req: AnalysisRequest) -> core.AnalysisResult:
    """Run analysis for download, saving to temp directory."""
    analysis_input = _build_analysis_input(req)
    options = _build_analysis_options(req)
    package.validate_analysis_input(analysis_input)
    package.validate_options(options)
    core.validate_resource_selections(analysis_input, options)
    with _analysis_lock:
        result = core.run_analysis(analysis_input, options=options)
    return result

@app.post('/api/download-csv')
def download_csv(req: AnalysisRequest):
    """Run analysis and return CSV download."""
    client_id = 'api'
    if not _run_limiter.allow(client_id):
        raise HTTPException(status_code=429, detail='Too many requests.')

    try:
        result = _build_download_analysis(req)
        csv_content = _generate_csv(result)
        return Response(
            content=csv_content,
            media_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="stoichiometry_results.csv"'}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=_safe_error(e))

@app.post('/api/download-report')
def download_report(req: AnalysisRequest):
    """Run analysis and return report text download."""
    client_id = 'api'
    if not _run_limiter.allow(client_id):
        raise HTTPException(status_code=429, detail='Too many requests.')

    try:
        result = _build_download_analysis(req)
        return Response(
            content=result.report_text,
            media_type='text/plain',
            headers={'Content-Disposition': 'attachment; filename="stoichiometry_report.txt"'}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=_safe_error(e))


@app.post('/api/download-html-report')
def download_html_report(req: AnalysisRequest):
    """Run analysis and return the HTML report that accompanies the .stf package."""
    client_id = 'api'
    if not _run_limiter.allow(client_id):
        raise HTTPException(status_code=429, detail='Too many requests.')

    try:
        result = _build_download_analysis(req)
        project = package.project_from_result(result)
        html_content = package.render_html_report(project)
        return Response(
            content=html_content,
            media_type='text/html',
            headers={'Content-Disposition': 'attachment; filename="stoichiometry_report.html"'}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=_safe_error(e))


@app.post('/api/download-stf')
def download_stf(req: AnalysisRequest):
    """Run analysis and return STF package download."""
    client_id = 'api'
    if not _run_limiter.allow(client_id):
        raise HTTPException(status_code=429, detail='Too many requests.')

    try:
        result = _build_download_analysis(req)
        
        # Build a proper STF package from the analysis result
        project = package.project_from_result(result)
        stf_bytes = package.serialize_stf(project)
        return Response(
            content=stf_bytes,
            media_type='application/zip',
            headers={'Content-Disposition': 'attachment; filename="stoichiometry_results.stf"'}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=_safe_error(e))

def _generate_csv(result: Any) -> str:
    """Generate CSV from analysis result."""
    output = io.StringIO()
    writer = csv.writer(output)
    for table in result.tables:
        writer.writerow([table.title])
        writer.writerow(table.columns)
        for row in table.rows:
            writer.writerow(row)
        writer.writerow([])  # blank line between tables
    return output.getvalue()

# --- Serve frontend ---
@app.get('/', response_class=HTMLResponse)
def serve_frontend():
    """Serve the main frontend page."""
    index_path = os.path.join(FRONTEND_DIR, 'index.html')
    if os.path.isfile(index_path):
        with open(index_path, 'r') as f:
            return f.read()
    raise HTTPException(status_code=404, detail='Frontend not found')

# --- Main entry point ---
if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('STOICHIOMETRY_API_PORT', '8000'))
    uvicorn.run(app, host='0.0.0.0', port=port)
