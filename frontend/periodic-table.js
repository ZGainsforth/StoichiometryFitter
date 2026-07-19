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

class PeriodicTable {
    constructor(containerId) {
        this.containerId = containerId;
        this.elements = new Map();
        this.values = new Map();
        this.expanded = true;
        this.maxValue = 1;
        this._build();
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

        // Build full grid
        this.grid = document.createElement('div');
        this.grid.className = 'element-grid-full';
        this.grid.style.display = this.expanded ? 'grid' : 'none';

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
            cell.style.gridColumn = col;
            cell.style.gridRow = row;

            const atomicNum = allSymbols.indexOf(symbol) + 1;

            cell.innerHTML = `
                <span class="cell-number">${atomicNum}</span>
                <span class="cell-symbol">${symbol}</span>
            `;
            cell.addEventListener('click', () => this.openOverlay(symbol));
            this.grid.appendChild(cell);
        }
        container.appendChild(this.grid);
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
        for (const [sym, val] of Object.entries(values)) {
            const numVal = parseFloat(val) || 0;
            this.values.set(sym, numVal);
            if (numVal > maxVal) maxVal = numVal;
        }
        this.maxValue = maxVal || 1;
        this.render();
    }

    updateValue(symbol, value) {
        this.values.set(symbol, value);
        const cell = this.grid.querySelector(`[data-symbol="${symbol}"]`);
        if (cell) {
            if (value > 0) {
                const cat = this._getCategory(symbol) || 'transition';
                const intensity = this._logIntensity(value);
                const color = CATEGORY_COLORS[cat] || '#BAE1FF';
                const blended = this._blendColor(color, intensity);
                cell.style.backgroundColor = `rgb(${blended.r}, ${blended.g}, ${blended.b})`;
                cell.classList.add('has-value');
            } else {
                cell.style.backgroundColor = '';
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
                gridCell.classList.add('has-value');
            } else {
                gridCell.style.backgroundColor = '';
                gridCell.classList.remove('has-value');
            }
        }

        // Update collapse toggle text
        const btn = document.getElementById('collapse-toggle');
        if (btn) {
            btn.textContent = this.expanded ? '▶' : '◀';
        }
    }

    toggle() {
        this.expanded = !this.expanded;
        this.grid.style.display = this.expanded ? 'grid' : 'none';
        this.render();
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
