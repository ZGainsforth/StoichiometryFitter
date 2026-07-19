/**
 * Stoichiometry Fitter — Main Application Logic
 *
 * Wires together the periodic table component, API calls,
 * state management, and result display.
 */

// --- State ---
let periodicTable = null;
let configOptions = {};
let lastResult = null;
let isRunning = false;

// --- Utility ---
const api = (path, options = {}) => {
    const base = window.STOICHIOMETRY_API_BASE || '';
    return fetch(`${base}${path}`, { ...options });
};

const apiJSON = async (path, method = 'GET', body = null) => {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const resp = await api(path, opts);
    if (!resp.ok) {
        const err = await resp.json().catch(() => ({ detail: resp.statusText }));
        throw new Error(err.detail || resp.statusText);
    }
    return resp.json();
};

// --- Status bar ---
function setStatus(message, type = '') {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = type ? `mb-4 text-sm ${type}` : 'mb-4 text-sm text-text-secondary';
}

// --- Load config options ---
async function loadConfigOptions() {
    try {
        configOptions = await apiJSON('/api/config-options');

        // Populate dropdowns
        const populate = (id, items, defaultLabel = '(None)') => {
            const sel = document.getElementById(id);
            sel.innerHTML = `<option value="">${defaultLabel}</option>`;
            if (items) {
                for (const item of items) {
                    const opt = document.createElement('option');
                    opt.value = item;
                    opt.textContent = item;
                    sel.appendChild(opt);
                }
            }
        };

        populate('k-factors', configOptions.kfactors);
        populate('stoichiometry', configOptions.stoichiometry);
        populate('arbitrary-absorption', configOptions.arbitrary_absorption);
        populate('phase-analysis', configOptions.phase_analysis);

        // Multi-select for phases
        const phaseSel = document.getElementById('selected-phases');
        phaseSel.innerHTML = '';
        if (configOptions.selected_phases) {
            for (const phase of configOptions.selected_phases) {
                const opt = document.createElement('option');
                opt.value = phase;
                opt.textContent = phase;
                phaseSel.appendChild(opt);
            }
        }
    } catch (err) {
        console.error('Failed to load config options:', err);
        setStatus('Warning: Could not load config options.', 'text-yellow-400');
    }
}

// --- Load categories ---
async function loadCategories() {
    try {
        const categories = await apiJSON('/api/categories');
        window.ELEMENT_CATEGORIES = categories;
    } catch (err) {
        console.error('Failed to load categories:', err);
    }
}

// --- Load periodic table ---
async function loadElements() {
    try {
        const elements = await apiJSON('/api/elements');
        periodicTable.setElements(elements);
    } catch (err) {
        console.error('Failed to load elements:', err);
    }
}

// --- Handle input type changes ---
function onInputTypeChange() {
    // Re-render the values table with new column label
    updateElementValuesTable();

    // Show/hide (None) option in k-factors based on input type
    // When Counts is selected, k-factors are required (hide None)
    // When At%, Wt%, Ox Wt% is selected, k-factors are optional
    const inputType = document.getElementById('input-type').value;
    const kfSel = document.getElementById('k-factors');
    const noneOption = kfSel.querySelector('option[value=""]');
    if (inputType === 'Counts') {
        noneOption.style.display = 'none';
        // If currently "None" is selected, auto-select first available
        if (kfSel.value === '') {
            const firstOpt = kfSel.querySelector('option:not([value=""])');
            if (firstOpt) kfSel.value = firstOpt.value;
        }
    } else {
        noneOption.style.display = '';
        // Reset to None when switching away from Counts
        kfSel.value = '';
    }

    // Trigger quick quant with new settings
    runQuickQuant();
}

// --- Load example input ---
async function loadExample() {
    try {
        setStatus('Loading example input...', 'text-blue-400');
        const data = await apiJSON('/api/example');
        loadValues(data.values);
        setStatus(`Loaded example input with ${Object.keys(data.values).length} elements.`, 'text-green-400');
    } catch (err) {
        setStatus(`Failed to load example: ${err.message}`, 'text-red-400');
    }
}

// --- Load file upload ---
async function loadFile(file) {
    try {
        setStatus(`Uploading ${file.name}...`, 'text-blue-400');
        const formData = new FormData();
        formData.append('file', file);

        const resp = await fetch('/api/upload', { method: 'POST', body: formData });
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({ detail: resp.statusText }));
            throw new Error(err.detail || resp.statusText);
        }
        const data = await resp.json();
        loadValues(data.values);
        setStatus(`Loaded ${file.name} with ${Object.keys(data.values).length} elements.`, 'text-green-400');
    } catch (err) {
        setStatus(`Upload failed: ${err.message}`, 'text-red-400');
    }
}

// --- Load values into state ---
function loadValues(values) {
    periodicTable.setValues(values);
    updateElementValuesTable();
    // Also run a lightweight quant update (no phase analysis)
    runQuickQuant();
}

// --- Get abundance label from input type ---
function getAbundanceLabel() {
    const inputType = document.getElementById('input-type').value;
    return inputType;
}

// --- Update element values table (2 columns: Element + dynamic abundance) ---
function updateElementValuesTable() {
    const container = document.getElementById('element-values-table');
    const entries = [];
    for (const [sym, val] of periodicTable.values) {
        if (val > 0) {
            entries.push({ symbol: sym, value: val });
        }
    }

    if (entries.length === 0) {
        container.innerHTML = '<p class="text-xs text-text-muted italic p-2">No elements with non-zero values.</p>';
        return;
    }

    const abundanceLabel = getAbundanceLabel();

    let html = `<table class="element-values-table">`;
    html += `<thead><tr><th>Element</th><th>${abundanceLabel}</th></tr></thead>`;
    html += `<tbody>`;

    for (const entry of entries) {
        html += `<tr>
            <td>${entry.symbol}</td>
            <td><input type="number" min="0" step="any" value="${entry.value}"
                       data-symbol="${entry.symbol}"
                       onchange="onValueChange(this)"
                       onkeydown="onValueKeyup(event, this)"
                       class="value-input"></td>
        </tr>`;
    }

    html += `</tbody></table>`;
    container.innerHTML = html;
}

// --- Handle direct value input changes ---
function onValueChange(input) {
    const sym = input.dataset.symbol;
    const val = parseFloat(input.value);
    if (!isNaN(val) && val >= 0) {
        periodicTable.updateValue(sym, val);
        updateElementValuesTable();
        // Recalculate quantification (lightweight, no phase analysis)
        runQuickQuant();
    }
}

function onValueKeyup(event, input) {
    if (event.key === 'Enter') {
        onValueChange(input);
        input.blur();
    }
}

// --- Get current config for analysis ---
function getConfigForAnalysis(fullAnalysis = false) {
    const phaseSel = document.getElementById('selected-phases');
    const values = {};
    for (const [sym, val] of periodicTable.values) {
        values[sym] = val;
    }

    // Select values — empty string means disabled/None
    const kfSel = document.getElementById('k-factors');
    const stoichSel = document.getElementById('stoichiometry');
    const absSel = document.getElementById('arbitrary-absorption');

    return {
        values,
        input_type: document.getElementById('input-type').value,
        stoichiometry_name: stoichSel.value || null,
        kfactors: kfSel.value || null,
        arbitrary_absorption: absSel.value || null,
        absorption_correction: parseFloat(document.getElementById('absorption-correction').value) || null,
        takeoff: parseFloat(document.getElementById('takeoff').value) || 18,
        selected_phases: Array.from(phaseSel.selectedOptions).filter(o => o.value).map(o => o.value),
        phase_analysis: (fullAnalysis && document.getElementById('phase-analysis').value) ? document.getElementById('phase-analysis').value : null,
    };
}

// --- Run lightweight quantification (real-time, no phase analysis) ---
async function runQuickQuant() {
    try {
        const config = getConfigForAnalysis(false);
        const result = await apiJSON('/api/quick-quant', 'POST', config);
        displayQuickQuant(result);
    } catch (err) {
        console.error('Quick quant failed:', err);
        setStatus(`Quick quant failed: ${err.message}`, 'text-red-400');
    }
}

// --- Display quick quantification (real-time update) ---
function displayQuickQuant(result) {
    // Update the quant results table
    const quantBody = document.getElementById('quant-results-body');
    if (quantBody && result.quant) {
        let html = '';
        const entries = Object.entries(result.quant)
            .filter(([sym]) => sym !== '_nonzero_input_' && sym !== '_zero_kfactor_')
            .sort((a, b) => {
                // Sort by Wt% descending
                return (b[1].wt_pct || 0) - (a[1].wt_pct || 0);
            });

        for (const [sym, data] of entries) {
            if (data.at_pct > 0 || data.wt_pct > 0) {
                html += `<tr>
                    <td class="text-left font-medium" style="font-family:'Inter',system-ui,sans-serif">${sym}</td>
                    <td>${data.at_pct ? data.at_pct.toFixed(4) : '-'}</td>
                    <td>${data.wt_pct ? data.wt_pct.toFixed(4) : '-'}</td>
                    <td>${data.oxide_wt_pct ? data.oxide_wt_pct.toFixed(4) : '-'}</td>
                    <td>${data.k_factor ? data.k_factor.toFixed(6) : '-'}</td>
                </tr>`;
            }
        }
        if (html) {
            quantBody.innerHTML = html;
        } else {
            quantBody.innerHTML = '<tr><td colspan="5" class="text-center text-text-muted">No quantified elements.</td></tr>';
        }
    }

    // Update the correction key-value table
    const corrTable = document.getElementById('corrections-table-body');
    if (corrTable && result.corrections) {
        let html = '';
        for (const corr of result.corrections) {
            html += `<tr><td class="text-left font-medium" style="font-family:'Inter',system-ui,sans-serif">${corr.key}</td><td>${corr.value}</td></tr>`;
        }
        corrTable.innerHTML = html;
    }

    // Show the results section if hidden
    document.getElementById('results-section').classList.remove('hidden');
}

// --- Run full analysis ---
async function runAnalysis() {
    if (isRunning) return;

    // Check from periodicTable.values (where all values live)
    let hasValues = false;
    for (const [sym, val] of periodicTable.values) {
        if (val > 0) { hasValues = true; break; }
    }

    if (!hasValues) {
        setStatus('No element values to analyze. Upload a file or use example input first.', 'text-red-400');
        return;
    }

    isRunning = true;
    const runBtn = document.getElementById('run-btn');
    runBtn.disabled = true;
    runBtn.textContent = 'Running...';
    setStatus('Running analysis...', 'text-blue-400');
    document.getElementById('results-section').classList.remove('hidden');

    try {
        const config = getConfigForAnalysis(true);
        const result = await apiJSON('/api/analysis', 'POST', config);
        lastResult = result;
        displayResults(result);
        setStatus('Analysis complete.', 'text-green-400');
    } catch (err) {
        setStatus(`Analysis failed: ${err.message}`, 'text-red-400');
        console.error('Analysis error:', err);
    } finally {
        isRunning = false;
        runBtn.disabled = false;
        runBtn.textContent = 'Run Full Analysis';
    }
}

// --- Display results ---
function displayResults(result) {
    document.getElementById('results-section').classList.remove('hidden');

    // Warnings
    const warningsEl = document.getElementById('warnings');
    warningsEl.innerHTML = '';
    if (result.warnings && result.warnings.length > 0) {
        for (const warning of result.warnings) {
            const div = document.createElement('div');
            div.className = 'warning';
            div.textContent = `⚠ ${warning}`;
            warningsEl.appendChild(div);
        }
    }

    // Tables
    const tablesEl = document.getElementById('results-tables');
    tablesEl.innerHTML = '';

    if (result.tables && result.tables.length > 0) {
        for (const table of result.tables) {
            // Skip the Input Data and Quantification Results tables (inline already)
            if (table.title === 'Input Data' || table.title === 'Quantification Results') continue;

            const section = document.createElement('div');

            if (table.title) {
                const title = document.createElement('div');
                title.className = 'results-table-title';
                title.textContent = table.title;
                section.appendChild(title);
            }

            const tableEl = document.createElement('table');
            tableEl.className = 'results-table';

            // Header
            if (table.columns && table.columns.length > 0) {
                const thead = document.createElement('thead');
                const headerRow = document.createElement('tr');
                for (const col of table.columns) {
                    const th = document.createElement('th');
                    th.textContent = col;
                    headerRow.appendChild(th);
                }
                thead.appendChild(headerRow);
                tableEl.appendChild(thead);
            }

            // Body
            if (table.rows && table.rows.length > 0) {
                const tbody = document.createElement('tbody');
                for (const row of table.rows) {
                    const tr = document.createElement('tr');
                    for (const col of table.columns) {
                        const td = document.createElement('td');
                        td.textContent = row[col] != null ? String(row[col]) : '';
                        tr.appendChild(td);
                    }
                    tbody.appendChild(tr);
                }
                tableEl.appendChild(tbody);
            }

            section.appendChild(tableEl);
            tablesEl.appendChild(section);
        }
    }

    // Raw report
    if (result.report_text) {
        document.getElementById('raw-report').textContent = result.report_text;
    } else {
        document.getElementById('raw-report').textContent = '(No report text available)';
    }
}

// --- Download handlers ---
function setupDownloadButtons() {
    document.getElementById('download-csv')?.addEventListener('click', () => {
        if (!lastResult) {
            setStatus('No results to download.', 'text-yellow-400');
            return;
        }
        // Fetch CSV from backend (handles full result)
        const config = getConfigForAnalysis(true);
        fetch('/api/download-csv', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config),
        })
        .then(resp => {
            if (!resp.ok) throw new Error('Download failed');
            return resp.blob();
        })
        .then(blob => {
            downloadBlob(blob, 'stoichiometry_results.csv');
            setStatus('CSV downloaded.', 'text-green-400');
        })
        .catch(err => setStatus(`Download failed: ${err.message}`, 'text-red-400'));
    });

    document.getElementById('download-report')?.addEventListener('click', () => {
        if (!lastResult) {
            setStatus('No results to download.', 'text-yellow-400');
            return;
        }
        const config = getConfigForAnalysis(true);
        fetch('/api/download-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config),
        })
        .then(resp => {
            if (!resp.ok) throw new Error('Download failed');
            return resp.blob();
        })
        .then(blob => {
            downloadBlob(blob, 'stoichiometry_report.txt');
            setStatus('Report downloaded.', 'text-green-400');
        })
        .catch(err => setStatus(`Download failed: ${err.message}`, 'text-red-400'));
    });

    document.getElementById('download-stf')?.addEventListener('click', () => {
        if (!lastResult) {
            setStatus('No results to download.', 'text-yellow-400');
            return;
        }
        const config = getConfigForAnalysis(true);
        fetch('/api/download-stf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config),
        })
        .then(resp => {
            if (!resp.ok) throw new Error('Download failed');
            return resp.blob();
        })
        .then(blob => {
            downloadBlob(blob, 'stoichiometry_results.stf');
            setStatus('.stf file downloaded.', 'text-green-400');
        })
        .catch(err => setStatus(`Download failed: ${err.message}`, 'text-red-400'));
    });
}

function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// --- Overlay handlers ---
function setupOverlayHandlers() {
    const overlay = document.getElementById('element-overlay');
    const backdrop = document.getElementById('overlay-backdrop');
    const applyBtn = document.getElementById('overlay-apply');
    const valueInput = document.getElementById('overlay-value');

    backdrop.addEventListener('click', () => periodicTable.closeOverlay());

    applyBtn.addEventListener('click', () => {
        const symbol = document.getElementById('overlay-symbol').textContent;
        const value = valueInput.value;
        periodicTable.applyValue(symbol, value);
        updateElementValuesTable();
        runQuickQuant();
    });

    valueInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') applyBtn.click();
        if (e.key === 'Escape') periodicTable.closeOverlay();
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') periodicTable.closeOverlay();
    });
}

// --- Collapse toggle ---
function setupCollapseToggle() {
    const btn = document.getElementById('collapse-toggle');
    btn.addEventListener('click', () => {
        periodicTable.toggle();
    });
}

// --- Clear all values ---
function setupClearValues() {
    document.getElementById('clear-values-btn')?.addEventListener('click', () => {
        periodicTable.clearValues();
        updateElementValuesTable();
    });
}

// --- File upload handler ---
function setupFileUpload() {
    const uploadBtn = document.getElementById('upload-btn');
    const fileInput = document.getElementById('file-upload');
    const fileName = document.getElementById('file-name');

    uploadBtn.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            loadFile(e.target.files[0]);
            fileName.textContent = e.target.files[0].name;
            fileName.classList.remove('hidden');
        }
    });
}

// --- Example button ---
function setupExampleButton() {
    document.getElementById('example-btn').addEventListener('click', loadExample);
}

// --- Settings change listeners ---
function setupSettingsListeners() {
    document.getElementById('input-type').addEventListener('change', onInputTypeChange);
    document.getElementById('k-factors').addEventListener('change', runQuickQuant);
    document.getElementById('stoichiometry').addEventListener('change', runQuickQuant);
    document.getElementById('arbitrary-absorption').addEventListener('change', runQuickQuant);
    document.getElementById('absorption-correction').addEventListener('input', runQuickQuant);
    document.getElementById('takeoff').addEventListener('input', runQuickQuant);
}

// --- Run button ---
function setupRunButton() {
    document.getElementById('run-btn').addEventListener('click', runAnalysis);
}

// --- Init ---
async function init() {
    periodicTable = new PeriodicTable('element-grid');

    await Promise.all([
        loadConfigOptions(),
        loadElements(),
        loadCategories(),
    ]);

    setupOverlayHandlers();
    setupCollapseToggle();
    setupClearValues();
    setupFileUpload();
    setupExampleButton();
    setupSettingsListeners();
    setupRunButton();
    setupDownloadButtons();

    setStatus('Ready. Load a measurement input or .stf project to begin.', '');
}

document.addEventListener('DOMContentLoaded', init);
