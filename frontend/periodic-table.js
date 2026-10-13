/**
 * Periodic Table Component
 *
 * Renders the full 118-element periodic table with pastel category colors
 * and log-scale intensity blending based on element values.
 */

// Category pastel colors
const CATEGORY_COLORS = {
    alkali:          '#FFB3BA',
    alkaline:        '#FFDFBA',
    transition:      '#BAE1FF',
    post_transition: '#BFFF86',
    metalloid:       '#E8BAE9',
    nonmetal:        '#BAFFC9',
    halogen:         '#FFFFBA',
    noble_gas:       '#FFC3A0',
    lanthanide:      '#DABF9A',
    actinide:        '#C9C9FF',
};

// Element positions for grid layout: [row, col]
const ELEMENT_POSITIONS = {
    'H':  [1, 1],    'He': [1, 18],
    'Li': [2, 1],    'Be': [2, 2],    'B':  [2, 13], 'C':  [2, 14],
    'N':  [2, 15],   'O':  [2, 16],   'F':  [2, 17], 'Ne': [2, 18],
    'Na': [3, 1],    'Mg': [3, 2],    'Al': [3, 13], 'Si': [3, 14],
    'P':  [3, 15],   'S':  [3, 16],   'Cl': [3, 17], 'Ar': [3, 18],
    'K':  [4, 1],    'Ca': [4, 2],    'Sc': [4, 3],  'Ti': [4, 4],
    'V':  [4, 5],    'Cr': [4, 6],    'Mn': [4, 7],  'Fe': [4, 8],
    'Co': [4, 9],    'Ni': [4, 10],   'Cu': [4, 11], 'Zn': [4, 12],
    'Ga': [4, 13],   'Ge': [4, 14],   'As': [4, 15], 'Se': [4, 16],
    'Br': [4, 17],   'Kr': [4, 18],
    'Rb': [5, 1],    'Sr': [5, 2],    'Y':  [5, 3],  'Zr': [5, 4],
    'Nb': [5, 5],    'Mo': [5, 6],    'Tc': [5, 7],  'Ru': [5, 8],
    'Rh': [5, 9],    'Pd': [5, 10],   'Ag': [5, 11], 'Cd': [5, 12],
    'In': [5, 13],   'Sn': [5, 14],   'Sb': [5, 15], 'Te': [5, 16],
    'I':  [5, 17],   'Xe': [5, 18],
    'Cs': [6, 1],    'Ba': [6, 2],    'La': [9, 4],  'Ce': [9, 5],
    'Pr': [9, 6],    'Nd': [9, 7],    'Pm': [9, 8],  'Sm': [9, 9],
    'Eu': [9, 10],   'Gd': [9, 11],   'Tb': [9, 12], 'Dy': [9, 13],
    'Ho': [9, 14],   'Er': [9, 15],   'Tm': [9, 16], 'Yb': [9, 17],
    'Lu': [9, 18],   'Hf': [6, 4],    'Ta': [6, 5],
    'W':  [6, 6],    'Re': [6, 7],    'Os': [6, 8],  'Ir': [6, 9],
    'Pt': [6, 10],   'Au': [6, 11],   'Hg': [6, 12], 'Tl': [6, 13],
    'Pb': [6, 14],   'Bi': [6, 15],   'Po': [6, 16], 'At': [6, 17],
    'Rn': [6, 18],
    'Fr': [7, 1],    'Ra': [7, 2],    'Ac': [10, 4], 'Th': [10, 5],
    'Pa': [10, 6],   'U':  [10, 7],   'Np': [10, 8], 'Pu': [10, 9],
    'Am': [10, 10],  'Cm': [10, 11],  'Bk': [10, 12],'Cf': [10, 13],
    'Es': [10, 14],  'Fm': [10, 15],  'Md': [10, 16],'No': [10, 17],
    'Lr': [10, 18],  'Rf': [7, 4],    'Db': [7, 5],
    'Sg': [7, 6],    'Bh': [7, 7],    'Hs': [7, 8],  'Mt': [7, 9],
    'Ds': [7, 10],   'Rg': [7, 11],   'Cn': [7, 12], 'Nh': [7, 13],
    'Fl': [7, 14],   'Mc': [7, 15],   'Lv': [7, 16], 'Ts': [7, 17],
    'Og': [7, 18],
};

// Rows in the main table (periods) and in the f-block grid (La/Ac series)
const MAIN_ROWS = [1, 2, 3, 4, 5, 6, 7];
const FBLOCK_ROWS = [9, 10];
const ROW_LABELS = { 9: 'lanthanides', 10: 'actinides' };
const COLLAPSE_STORAGE_KEY = 'stoich.ptCollapse';

class PeriodicTable {
    constructor(containerId) {
        this.containerId = containerId;
        this.elements = new Map();
        this.values = new Map();
        this.maxValue = 1;
        this.onValueChange = null;
        this.collapsedRows = new Set();
        this.collapsedCols = new Set();
        this._loadCollapse();
        this._build();
    }

    // --- Row/column collapsing ---

    _loadCollapse() {
        try {
            const saved = JSON.parse(localStorage.getItem(COLLAPSE_STORAGE_KEY) || '{}');
            this.collapsedRows = new Set(saved.rows || []);
            this.collapsedCols = new Set(saved.cols || []);
        } catch (e) {
            // Storage unavailable or corrupt: start fully expanded
        }
    }

    _saveCollapse() {
        try {
            localStorage.setItem(COLLAPSE_STORAGE_KEY, JSON.stringify({
                rows: [...this.collapsedRows],
                cols: [...this.collapsedCols],
            }));
        } catch (e) {
            // Ignore: persistence is a convenience only
        }
    }

    toggleRow(row) {
        if (this.collapsedRows.has(row)) this.collapsedRows.delete(row);
        else this.collapsedRows.add(row);
        this._applyCollapse();
        this._saveCollapse();
    }

    toggleCol(col) {
        if (this.collapsedCols.has(col)) this.collapsedCols.delete(col);
        else this.collapsedCols.add(col);
        this._applyCollapse();
        this._saveCollapse();
    }

    expandAll() {
        this.collapsedRows.clear();
        this.collapsedCols.clear();
        this._applyCollapse();
        this._saveCollapse();
    }

    /** Collapse every row and column that holds no nonzero value. */
    collapseUnused() {
        const usedRows = new Set();
        const usedCols = new Set();
        for (const [sym, val] of this.values) {
            if (!(val > 0) || !ELEMENT_POSITIONS[sym]) continue;
            const [row, col] = ELEMENT_POSITIONS[sym];
            usedRows.add(row);
            if (row <= 7) usedCols.add(col);
        }
        // Nothing entered yet: collapsing everything would leave nothing to click
        if (usedRows.size === 0) return;

        this.collapsedRows = new Set([...MAIN_ROWS, ...FBLOCK_ROWS].filter(r => !usedRows.has(r)));
        this.collapsedCols = new Set();
        for (let c = 1; c <= 18; c++) {
            if (!usedCols.has(c)) this.collapsedCols.add(c);
        }
        this._applyCollapse();
        this._saveCollapse();
    }

    /** Expand the row (and main-table column) containing symbol. Returns true if anything changed. */
    _ensureVisible(symbol) {
        const pos = ELEMENT_POSITIONS[symbol];
        if (!pos) return false;
        const [row, col] = pos;
        let changed = this.collapsedRows.delete(row);
        if (row <= 7) changed = this.collapsedCols.delete(col) || changed;
        return changed;
    }

    _applyCollapse() {
        if (!this.mainGrid) return;
        const STRIP = 10;
        // Expanded columns share whatever width the gutter and collapsed strips leave,
        // so the table always spans the container and remaining cells grow
        const nCollapsed = this.collapsedCols.size;
        const nExpanded = 18 - nCollapsed;
        const cell = `calc((100% - var(--pt-gutter) - 18 * 2px - ${nCollapsed * STRIP}px) / ${Math.max(nExpanded, 1)})`;
        const colTrack = c => this.collapsedCols.has(c) ? `${STRIP}px` : cell;
        const rowTrack = r => this.collapsedRows.has(r) ? `${STRIP}px` : 'auto';

        // Column 1 is the row-toggle gutter; element column c lives in grid column c + 1
        const mainCols = [];
        for (let c = 1; c <= 18; c++) mainCols.push(colTrack(c));
        this.mainGrid.style.gridTemplateColumns = `var(--pt-gutter) ${mainCols.join(' ')}`;
        this.mainGrid.style.gridTemplateRows = `var(--pt-gutter) ${MAIN_ROWS.map(rowTrack).join(' ')}`;

        // f-block reuses main tracks for groups 1-3 so La/Ac start under group 4, then
        // splits the remaining width among its 15 cells
        this.fGrid.style.gridTemplateColumns =
            `var(--pt-gutter) ${mainCols.slice(0, 3).join(' ')} repeat(15, minmax(0, 1fr))`;
        this.fGrid.style.gridTemplateRows = FBLOCK_ROWS.map(rowTrack).join(' ');

        for (const cell of this.grid.querySelectorAll('.element-cell')) {
            const row = +cell.dataset.row;
            const col = +cell.dataset.col;
            const hidden = this.collapsedRows.has(row) || (row <= 7 && this.collapsedCols.has(col));
            cell.classList.toggle('pt-hidden', hidden);
        }

        for (const btn of this.grid.querySelectorAll('.pt-col-toggle')) {
            const col = +btn.dataset.col;
            const collapsed = this.collapsedCols.has(col);
            btn.classList.toggle('collapsed', collapsed);
            btn.title = `${collapsed ? 'Expand' : 'Collapse'} group ${col}`;
        }
        for (const btn of this.grid.querySelectorAll('.pt-row-toggle')) {
            const row = +btn.dataset.row;
            const collapsed = this.collapsedRows.has(row);
            btn.classList.toggle('collapsed', collapsed);
            btn.title = `${collapsed ? 'Expand' : 'Collapse'} ${ROW_LABELS[row] || 'period ' + row}`;
        }
    }

    _makeToggle(kind, value, gridRow, gridCol) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = `pt-toggle pt-${kind}-toggle`;
        btn.dataset[kind] = value;
        btn.style.gridRow = gridRow;
        btn.style.gridColumn = gridCol;
        btn.addEventListener('click', () => kind === 'row' ? this.toggleRow(value) : this.toggleCol(value));
        return btn;
    }

    _hexToRgb(hex) {
        hex = hex.replace('#', '');
        return {
            r: parseInt(hex.substring(0, 2), 16),
            g: parseInt(hex.substring(2, 4), 16),
            b: parseInt(hex.substring(4, 6), 16),
        };
    }

    _blendColor(hex, intensity) {
        const rgb = this._hexToRgb(hex);
        return {
            r: Math.round(rgb.r * intensity + 255 * (1 - intensity)),
            g: Math.round(rgb.g * intensity + 255 * (1 - intensity)),
            b: Math.round(rgb.b * intensity + 255 * (1 - intensity)),
        };
    }

    _logIntensity(value) {
        if (this.maxValue <= 0 || value <= 0) return 0;
        return Math.min(1, Math.log10(value + 1) / Math.log10(this.maxValue + 1));
    }

    _getCategory(symbol) {
        const data = window.ELEMENT_CATEGORIES;
        return data ? data[symbol] : 'transition';
    }

    _build() {
        const container = document.getElementById(this.containerId);
        container.innerHTML = '';
        container.className = 'pt-wrapper';

        // The container holds the main table and the f-block; cell lookups search it
        this.grid = container;
        this.mainGrid = document.createElement('div');
        this.mainGrid.className = 'element-grid-full';
        this.fGrid = document.createElement('div');
        this.fGrid.className = 'element-grid-full pt-fblock';
        container.append(this.mainGrid, this.fGrid);

        for (let c = 1; c <= 18; c++) {
            this.mainGrid.appendChild(this._makeToggle('col', c, 1, c + 1));
        }
        for (const [i, r] of MAIN_ROWS.entries()) {
            this.mainGrid.appendChild(this._makeToggle('row', r, i + 2, 1));
        }
        for (const [i, r] of FBLOCK_ROWS.entries()) {
            this.fGrid.appendChild(this._makeToggle('row', r, i + 1, 1));
        }

        // Calculate atomic numbers once
        const allSymbols = Object.keys(ELEMENT_POSITIONS).sort((a, b) => {
            return (ELEMENT_POSITIONS[a][0] * 18 + ELEMENT_POSITIONS[a][1]) -
                   (ELEMENT_POSITIONS[b][0] * 18 + ELEMENT_POSITIONS[b][1]);
        });

        // Create all 118 element cells
        for (const [symbol, [row, col]] of Object.entries(ELEMENT_POSITIONS)) {
            const cell = document.createElement('div');
            cell.className = 'element-cell';
            cell.dataset.symbol = symbol;
            cell.dataset.row = row;
            cell.dataset.col = col;
            // Shift by one for the toggle gutter (column) and header (main-table row)
            cell.style.gridColumn = col + 1;
            cell.style.gridRow = row <= 7 ? row + 1 : FBLOCK_ROWS.indexOf(row) + 1;

            const atomicNum = allSymbols.indexOf(symbol) + 1;

            cell.innerHTML = `
                <span class="cell-number">${atomicNum}</span>
                <span class="cell-symbol">${symbol}</span>
            `;
            cell.addEventListener('click', () => this.openOverlay(symbol));
            cell.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                this.updateValue(symbol, 0);
                if (this.onValueChange) this.onValueChange(symbol, 0);
            });
            (row <= 7 ? this.mainGrid : this.fGrid).appendChild(cell);
        }
        this._applyCollapse();
    }

    setElements(elements) {
        this.elements = new Map();
        for (const el of elements) {
            this.elements.set(el.symbol, el);
        }
        this.render();
    }

    setValues(values) {
        this.values = new Map();
        let maxVal = 0;
        let expanded = false;
        for (const [sym, val] of Object.entries(values)) {
            const numVal = parseFloat(val) || 0;
            this.values.set(sym, numVal);
            if (numVal > maxVal) maxVal = numVal;
            if (numVal > 0) expanded = this._ensureVisible(sym) || expanded;
        }
        this.maxValue = maxVal || 1;
        if (expanded) {
            this._applyCollapse();
            this._saveCollapse();
        }
        this.render();
    }

    _luminance({ r, g, b }) {
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    }

    updateValue(symbol, value) {
        this.values.set(symbol, value);
        if (value > 0 && this._ensureVisible(symbol)) {
            this._applyCollapse();
            this._saveCollapse();
        }
        const cell = this.grid.querySelector(`[data-symbol="${symbol}"]`);
        if (cell) {
            if (value > 0) {
                const cat = this._getCategory(symbol) || 'transition';
                const intensity = this._logIntensity(value);
                const color = CATEGORY_COLORS[cat] || '#BAE1FF';
                const blended = this._blendColor(color, intensity);
                cell.style.backgroundColor = `rgb(${blended.r}, ${blended.g}, ${blended.b})`;
                cell.style.color = this._luminance(blended) > 0.6 ? '#0f172a' : '#f8fafc';
                cell.classList.add('has-value');
            } else {
                cell.style.backgroundColor = '';
                cell.style.color = '';
                cell.classList.remove('has-value');
            }
        }
    }

    clearValues() {
        for (const [sym] of this.values) {
            this.values.set(sym, 0);
            const cell = this.grid.querySelector(`[data-symbol="${sym}"]`);
            if (cell) {
                cell.style.backgroundColor = '';
                cell.style.color = '';
                cell.classList.remove('has-value');
            }
        }
        this.render();
    }

    render() {
        if (!this.grid) return;

        for (const [symbol, cell] of Object.entries(ELEMENT_POSITIONS)) {
            const gridCell = this.grid.querySelector(`[data-symbol="${symbol}"]`);
            if (!gridCell) continue;

            const val = this.values.get(symbol) || 0;
            const cat = this._getCategory(symbol) || 'transition';
            const color = CATEGORY_COLORS[cat] || '#BAE1FF';
            const intensity = this._logIntensity(val);
            const blended = this._blendColor(color, intensity);

            if (val > 0) {
                gridCell.style.backgroundColor = `rgb(${blended.r}, ${blended.g}, ${blended.b})`;
                gridCell.style.color = this._luminance(blended) > 0.6 ? '#0f172a' : '#f8fafc';
                gridCell.classList.add('has-value');
            } else {
                gridCell.style.backgroundColor = '';
                gridCell.style.color = '';
                gridCell.classList.remove('has-value');
            }
        }
    }

    openOverlay(symbol) {
        const overlay = document.getElementById('element-overlay');
        const symEl = document.getElementById('overlay-symbol');
        const valueInput = document.getElementById('overlay-value');
        const errorEl = document.getElementById('overlay-error');

        symEl.textContent = symbol;
        valueInput.value = this.values.get(symbol) || '';
        errorEl.classList.add('hidden');
        overlay.classList.remove('hidden');
        valueInput.focus();
        valueInput.select();
    }

    closeOverlay() {
        document.getElementById('element-overlay').classList.add('hidden');
    }

    applyValue(symbol, value) {
        const numVal = parseFloat(value);
        if (isNaN(numVal) || numVal < 0) {
            const errorEl = document.getElementById('overlay-error');
            errorEl.textContent = 'Value must be a nonnegative number.';
            errorEl.classList.remove('hidden');
            return false;
        }
        this.updateValue(symbol, numVal);
        this.closeOverlay();
        return true;
    }
}
