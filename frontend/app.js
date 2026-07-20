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

// --- Upload/Download directory handle storage ---
let uploadDirHandle = null;
let downloadDirHandle = null;

// --- IndexedDB for persistent directory handle storage ---
const DB_NAME = 'stoichiometry-fitter-db';
const DB_VERSION = 1;
const STORE_NAME = 'directory-handles';

async function initIndexedDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains(STORE_NAME)) {
                db.createObjectStore(STORE_NAME);
            }
        };
    });
}

async function saveDirHandle(key, handle) {
    try {
        const db = await initIndexedDB();
        return new Promise((resolve, reject) => {
            const transaction = db.transaction(STORE_NAME, 'readwrite');
            const store = transaction.objectStore(STORE_NAME);
            const request = store.put(handle, key);
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    } catch (err) {
        console.warn('Failed to save directory handle:', err);
    }
}

async function loadDirHandle(key) {
    try {
        const db = await initIndexedDB();
        return new Promise((resolve, reject) => {
            const transaction = db.transaction(STORE_NAME, 'readonly');
            const store = transaction.objectStore(STORE_NAME);
            const request = store.get(key);
            request.onsuccess = () => resolve(request.result || null);
            request.onerror = () => reject(request.error);
        });
    } catch (err) {
        console.warn('Failed to load directory handle:', err);
        return null;
    }
}

async function loadStoredDirHandles() {
    uploadDirHandle = await loadDirHandle('uploadDirHandle');
    downloadDirHandle = await loadDirHandle('downloadDirHandle');
    console.log('Loaded directory handles:', { uploadDirHandle, downloadDirHandle });
}

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
    const inputType = getInputTypeValue();
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

// --- Helper: read input type from values-table dropdown ---
function getInputTypeValue() {
    const el = document.getElementById('values-table-input-type');
    return el ? el.value : 'Counts';
}

// --- Helper: set input type on values-table dropdown ---
function setInputTypeValue(val) {
    const el = document.getElementById('values-table-input-type');
    if (el) el.value = val;
}

// --- Load example input ---
async function loadExample() {
    try {
        setStatus('Loading example input...', 'text-blue-400');
        const data = await apiJSON('/api/example');
        
        // Set input type to Counts (example data is in Counts)
        setInputTypeValue('Counts');
        
        // Auto-select first available k-factor (Counts requires k-factors)
        const kfSel = document.getElementById('k-factors');
        const firstOpt = kfSel.querySelector('option:not([value=""])');
        if (firstOpt) kfSel.value = firstOpt.value;
        
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
        
        // Restore ALL settings from the uploaded file (STF stores full project state)
        restoreSettings(data);
        
        // Load values and trigger quick quant (updates sidebar table & results)
        loadValues(data.values);
        
        // If phase_analysis was set in the STF, run full analysis so results
        // include the saved phase analysis (e.g. Olivine cation calculations).
        if (data.phase_analysis) {
            await runAnalysis();
            // runAnalysis() sets "Analysis complete." status — do NOT overwrite it
        } else {
            setStatus(`Loaded ${file.name} with ${Object.keys(data.values).length} elements.`, 'text-green-400');
        }
    } catch (err) {
        setStatus(`Upload failed: ${err.message}`, 'text-red-400');
    }
}

// --- Restore settings from uploaded file data ---
function restoreSettings(data) {
    // Input type
    if (data.input_type) {
        setInputTypeValue(data.input_type);
    }
    
    // k-factors
    if (data.kfactors) {
        const kfSel = document.getElementById('k-factors');
        kfSel.value = data.kfactors;
        // Hide/show None option based on input type
        const inputType = getInputTypeValue();
        const noneOption = kfSel.querySelector('option[value=""]');
        if (inputType === 'Counts') {
            noneOption.style.display = 'none';
        } else {
            noneOption.style.display = '';
        }
    }
    
    // Stoichiometry
    if (data.stoichiometry_name) {
        document.getElementById('stoichiometry').value = data.stoichiometry_name;
    }
    
    // Arbitrary absorption
    if (data.arbitrary_absorption) {
        document.getElementById('arbitrary-absorption').value = data.arbitrary_absorption;
    }
    
    // Absorption correction
    if (data.absorption_correction !== undefined && data.absorption_correction !== null) {
        document.getElementById('absorption-correction').value = data.absorption_correction;
    }
    
    // Takeoff angle
    if (data.takeoff !== undefined && data.takeoff !== null) {
        document.getElementById('takeoff').value = data.takeoff;
    }
    
    // Selected phases (multi-select)
    if (data.selected_phases && Array.isArray(data.selected_phases)) {
        const phaseSel = document.getElementById('selected-phases');
        for (const option of phaseSel.options) {
            option.selected = data.selected_phases.includes(option.value);
        }
    }
    
    // Phase analysis
    if (data.phase_analysis) {
        document.getElementById('phase-analysis').value = data.phase_analysis;
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
    const inputType = getInputTypeValue();
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
    html += `<thead><tr><th>Element</th><th><select id="values-table-input-type" class="px-1 py-0.5 bg-bg border border-border rounded text-xs text-text focus:outline-none focus:ring-1 focus:ring-blue-500">`;
    html += `<option${abundanceLabel === 'Counts' ? ' selected' : ''}>Counts</option>`;
    html += `<option${abundanceLabel === 'At %' ? ' selected' : ''}>At %</option>`;
    html += `<option${abundanceLabel === 'Wt %' ? ' selected' : ''}>Wt %</option>`;
    html += `<option${abundanceLabel === 'Ox Wt %' ? ' selected' : ''}>Ox Wt %</option>`;
    html += `</select></th></tr></thead>`;
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

    // Bind change handler on the dynamically-created dropdown
    const vtInputType = document.getElementById('values-table-input-type');
    if (vtInputType) {
        // Remove any previous listener to avoid duplicates
        const newEl = vtInputType.cloneNode(true);
        if (vtInputType.parentNode) {
            vtInputType.parentNode.replaceChild(newEl, vtInputType);
        }
        newEl.addEventListener('change', onInputTypeChange);
    }
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
        input_type: getInputTypeValue(),
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
    document.getElementById('download-csv')?.addEventListener('click', async () => {
        if (!lastResult) {
            setStatus('No results to download.', 'text-yellow-400');
            return;
        }
        const config = getConfigForAnalysis(true);
        try {
            const resp = await fetch('/api/download-csv', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config),
            });
            if (!resp.ok) throw new Error('Download failed');
            const blob = await resp.blob();
            await downloadBlob(blob, 'stoichiometry_results.csv', 'download');
            setStatus('CSV downloaded.', 'text-green-400');
        } catch (err) {
            setStatus(`Download failed: ${err.message}`, 'text-red-400');
        }
    });

    document.getElementById('download-report')?.addEventListener('click', async () => {
        if (!lastResult) {
            setStatus('No results to download.', 'text-yellow-400');
            return;
        }
        const config = getConfigForAnalysis(true);
        try {
            const resp = await fetch('/api/download-report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config),
            });
            if (!resp.ok) throw new Error('Download failed');
            const blob = await resp.blob();
            await downloadBlob(blob, 'stoichiometry_report.txt', 'download');
            setStatus('Report downloaded.', 'text-green-400');
        } catch (err) {
            setStatus(`Download failed: ${err.message}`, 'text-red-400');
        }
    });

    document.getElementById('download-stf')?.addEventListener('click', async () => {
        if (!lastResult) {
            setStatus('No results to download.', 'text-yellow-400');
            return;
        }
        const config = getConfigForAnalysis(true);
        try {
            const resp = await fetch('/api/download-stf', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config),
            });
            if (!resp.ok) throw new Error('Download failed');
            const blob = await resp.blob();
            await downloadBlob(blob, 'stoichiometry_results.stf', 'download');
            setStatus('.stf file downloaded.', 'text-green-400');
        } catch (err) {
            setStatus(`Download failed: ${err.message}`, 'text-red-400');
        }
    });
}

async function downloadBlob(blob, filename, operationType) {
    // Try the modern File System Access API for a proper save-as dialog
    if ('showSaveFilePicker' in window) {
        try {
            const options = {
                suggestedName: filename,
                types: [{
                    description: 'File',
                    accept: { 'application/octet-stream': ['.' + filename.split('.').pop()] },
                }],
            };
            // Pass startIn directory handle if available for downloads
            if (operationType === 'download' && downloadDirHandle) {
                options.startIn = downloadDirHandle;
            }
            const handle = await window.showSaveFilePicker(options);
            const writable = await handle.createWritable();
            await writable.write(blob);
            await writable.close();
            // Save the directory handle for next time
            if (operationType === 'download') {
                try {
                    const parent = await handle.getParent();
                    downloadDirHandle = parent;
                    await saveDirHandle('downloadDirHandle', downloadDirHandle);
                } catch (parentErr) {
                    console.warn('Could not get parent directory for download:', parentErr);
                    // For now, we'll just not persist the directory for this operation
                }
            }
            return;
        } catch (err) {
            // User cancelled or API failed — fall through to legacy method
            if (err.name !== 'AbortError') {
                console.warn('File System Access API failed, falling back to legacy download:', err);
            } else {
                return; // User cancelled
            }
        }
    }
    // Legacy fallback: create a temporary link and click it
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    // Wait a short delay before cleaning up to ensure the download starts in all browsers
    setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, 100);
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

// --- File upload handler (using File System Access API) ---
function setupFileUpload() {
    const uploadBtn = document.getElementById('upload-btn');
    const fileName = document.getElementById('file-name');

    uploadBtn.addEventListener('click', async () => {
        if ('showOpenFilePicker' in window) {
            try {
                const options = {
                    types: [{
                        description: 'Data Files',
                        accept: {
                            'text/csv': ['.csv'],
                            'text/plain': ['.txt'],
                            'application/zip': ['.stf'],
                        },
                    }],
                    multiple: false,
                };
                // Pass startIn directory handle if available for uploads
                if (uploadDirHandle) {
                    options.startIn = uploadDirHandle;
                }
                const [handle] = await window.showOpenFilePicker(options);
                const file = await handle.getFile();
                await loadFile(file);
                fileName.textContent = file.name;
                fileName.classList.remove('hidden');
                // Save the directory handle for next time
                try {
                    const parent = await handle.getParent();
                    uploadDirHandle = parent;
                    await saveDirHandle('uploadDirHandle', uploadDirHandle);
                } catch (parentErr) {
                    console.warn('Could not get parent directory for upload:', parentErr);
                    // Fallback: try to use the handle itself or skip persistence
                    // For now, we'll just not persist the directory for this operation
                }
            } catch (err) {
                if (err.name !== 'AbortError') {
                    console.error('File upload failed:', err);
                    setStatus(`Upload failed: ${err.message}`, 'text-red-400');
                }
                // User cancelled - do nothing
            }
        } else {
            // Fallback: create a temporary file input
            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.accept = '.csv,.txt,.stf';
            fileInput.style.display = 'none';
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    loadFile(e.target.files[0]);
                    fileName.textContent = e.target.files[0].name;
                    fileName.classList.remove('hidden');
                }
            });
            document.body.appendChild(fileInput);
            fileInput.click();
            setTimeout(() => document.body.removeChild(fileInput), 100);
        }
    });
}

// --- Helper: read input type from values-table dropdown ---
function getInputTypeValue() {
    const el = document.getElementById('values-table-input-type');
    return el ? el.value : 'Counts';
}

// --- Helper: set input type on values-table dropdown ---
function setInputTypeValue(val) {
    const el = document.getElementById('values-table-input-type');
    if (el) el.value = val;
}

// --- Reset to default settings ---
function resetToDefaultSettings() {
    // 1. Clear element values (sets input type to "Counts" implicitly when table empty)
    periodicTable.clearValues();
    updateElementValuesTable();
    
    // 2. Reset settings to defaults
    document.getElementById('k-factors').value = "";
    document.getElementById('stoichiometry').value = "";
    document.getElementById('arbitrary-absorption').value = "";
    document.getElementById('absorption-correction').value = "0";
    document.getElementById('takeoff').value = "18";
    
    // Clear multi-select selections
    const phaseSel = document.getElementById('selected-phases');
    for (let i = 0; i < phaseSel.options.length; i++) {
        phaseSel.options[i].selected = false;
    }
    
    document.getElementById('phase-analysis').value = "";
    
    // 3. Update quantification results
    runQuickQuant();
}

// --- Reset button ---
function setupResetButton() {
    const resetBtn = document.getElementById('reset-btn');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetToDefaultSettings);
    }
}

// --- Example button ---
function setupExampleButton() {
    document.getElementById('example-btn').addEventListener('click', loadExample);
}

// --- Settings change listeners ---
function setupSettingsListeners() {
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
    // Load persisted directory handles first
    await loadStoredDirHandles();
    
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
    setupResetButton();
    setupSettingsListeners();
    setupRunButton();
    setupDownloadButtons();

    setStatus('Ready. Load a measurement input or .stf project to begin.', '');
}

document.addEventListener('DOMContentLoaded', init);
