document.addEventListener('DOMContentLoaded', function () {
    const productionRulesTable = document.getElementById('ProdRulesTable').getElementsByTagName('tbody')[0];
    const initialAxiomInput = document.getElementById('initialAxiomInput');
    const inputString = document.getElementById('inputString');
    const showGrammarButton = document.getElementById('ShowGrammarBtn');
    const evaluateStringButton = document.getElementById('EvaluateStringBtn');
    const clearAllButton = document.getElementById('ClearAllBtn');
    const uploadProductionButton = document.getElementById('UploadProdBtn');
    const saveProductionButton = document.getElementById('SaveProdBtn');
    const productionFileInput = document.getElementById('ProdFileInputAccept');
    const resultsCard = document.getElementById('resultsCard');
    const grammarTypeResult = document.getElementById('grammarTypeResult');
    const stringResult = document.getElementById('stringResult');
    const derivationsResult = document.getElementById('derivationsResult');
    const derivationsText = document.getElementById('derivationsText');
    const loadingSpinner = document.getElementById('loadingSpinner');

    // Variables de estado
    let grammarData = {
        initialAxiom: '',
        nonTerminals: new Set(),
        terminals: new Set(),
        productions: []
    };

    // ==================== FUNCIONES DE VALIDACIÓN ====================
    function validateInitialAxiom(input) {
        input.value = input.value.replace(/[^A-Z]/g, '').toUpperCase();
        if (input.value) grammarData.initialAxiom = input.value;
    }

    function validateNonTerminal(input) {
        input.value = input.value.replace(/[^A-Z]/g, '').toUpperCase();
    }

    function validateProductionRule(input) {
        input.value = input.value.replace(/[^A-Za-z0-9|ε\s→]/g, '');
    }

    function validateInputString(input) {
        input.value = input.value.replace(/[^a-z0-9]/g, '');
    }

    // ==================== FUNCIONES DE MANEJO DE REGLAS ====================
    function addNewProductionRule() {
        const newRow = productionRulesTable.insertRow();

        // Celda para el no terminal
        const nonTermCell = newRow.insertCell(0);
        const arrowCell = newRow.insertCell(1);
        const prodRuleCell = newRow.insertCell(2);
        const actionsCell = newRow.insertCell(3);

        // Input para no terminal
        const nonTermInput = document.createElement('input');
        nonTermInput.type = 'text';
        nonTermInput.className = 'form-control';
        nonTermInput.placeholder = 'Ej: S';
        nonTermInput.addEventListener('input', () => validateNonTerminal(nonTermInput));
        nonTermCell.appendChild(nonTermInput);

        // Celda para la flecha
        arrowCell.innerHTML = '<i class="bi bi-arrow-right"></i>';
        arrowCell.className = 'text-center';

        // Input para regla de producción
        const prodRuleInput = document.createElement('input');
        prodRuleInput.type = 'text';
        prodRuleInput.className = 'form-control';
        prodRuleInput.placeholder = 'Ej: aB | b | ε';
        prodRuleInput.addEventListener('input', () => validateProductionRule(prodRuleInput));
        prodRuleCell.appendChild(prodRuleInput);

        // Botones de acción
        const addBtn = document.createElement('button');
        addBtn.className = 'btn btn-success btn-sm';
        addBtn.innerHTML = '<i class="bi bi-plus"></i>';
        addBtn.title = 'Add rule';
        addBtn.addEventListener('click', function() {
            if (productionRulesTable.rows.length < 10) {
                addNewProductionRule();
            } else {
                alert('Maximum of 10 production rules reached');
            }
        });

        const delBtn = document.createElement('button');
        delBtn.className = 'btn btn-danger btn-sm ms-2';
        delBtn.innerHTML = '<i class="bi bi-trash-fill"></i>';
        delBtn.title = 'Delete rule';
        delBtn.addEventListener('click', function() {
            if (productionRulesTable.rows.length > 1) { // No eliminar la última fila
                productionRulesTable.deleteRow(newRow.rowIndex - 1);
                updateGrammarData();
            }
        });

        actionsCell.appendChild(addBtn);
        actionsCell.appendChild(delBtn);
        actionsCell.className = 'text-center';
    }

    // ==================== FUNCIONES DE ACTUALIZACIÓN DE DATOS ====================
    function updateGrammarData() {
        grammarData = {
            initialAxiom: document.getElementById('initialAxiomInput').value.trim(),
            nonTerminals: new Set(),
            terminals: new Set(),
            productions: []
        };

        const rows = productionRulesTable.getElementsByTagName('tr');
        for (let row of rows) {
            const nonTermInput = row.cells[0]?.querySelector('input');
            const prodRuleInput = row.cells[2]?.querySelector('input');

            if (!nonTermInput || !prodRuleInput) continue;

            const nonTermValue = nonTermInput.value.trim();
            const prodRuleValue = prodRuleInput.value.trim();

            if (nonTermValue) {
                grammarData.nonTerminals.add(nonTermValue);
            }

            const alternatives = prodRuleValue.split('|').map(alt => alt.trim());
            
            if (alternatives.length === 0) alternatives.push('');

            for (const alt of alternatives) {
                if (alt === '') {
                    // Producción vacía (ε)
                    grammarData.productions.push({
                        lhs: nonTermValue,
                        rhs: [] // Epsilon representado como una lista vacía
                    });
                } else {
                    // Procesar la producción normal
                    const symbols = alt.split(/(?=[A-Z])|\B/).filter(c => c !== '' && c !== 'ε');
            
                    // Si no hay símbolos después de filtrar, es una producción vacía (ε)
                    if (symbols.length === 0) {
                        grammarData.productions.push({
                            lhs: nonTermValue,
                            rhs: [] // Epsilon
                        });
                    } else {
                        // Añadir la producción formateada
                        grammarData.productions.push({
                            lhs: nonTermValue,
                            rhs: symbols
                        });
            
                        // Verificar si es terminal o variable
                        symbols.forEach(symbol => {
                            if (/^[a-z0-9]$/.test(symbol)) {
                                grammarData.terminals.add(symbol);
                            } else if (/^[A-Z]$/.test(symbol)) {
                                grammarData.nonTerminals.add(symbol);
                            }
                        });
                    }
                }
            }
        }
    }

    function initializeTable() {
        while (productionRulesTable.rows.length > 0) {
            productionRulesTable.deleteRow(0);
        }
        addNewProductionRule();
    }

    // ==================== FUNCIONES DE VISUALIZACIÓN ====================
    function showGrammar() {
        updateGrammarData();

        if (!grammarData.initialAxiom) {
            showError('Please specify the initial axiom');
            return;
        }

        if (grammarData.productions.length === 0) {
            showError('Please add at least one production rule');
            return;
        }

        const grammarText = `
N = ${Array.from(grammarData.nonTerminals).join(' ')}
T = ${Array.from(grammarData.terminals).join(' ')}
S = ${grammarData.initialAxiom}
P = {
${grammarData.productions.map(p => `    ${p.lhs} → ${p.rhs.length ? p.rhs.join(' ') : 'ε'}`).join('\n')}
}`;

        grammarTypeResult.innerHTML = `<pre>${grammarText}</pre>`;
        stringResult.classList.add('d-none');
        derivationsResult.classList.add('d-none');
        resultsCard.classList.remove('d-none');
    }

    // ==================== FUNCIONES DE EVALUACIÓN ====================
    async function evaluateString() {
        const inputString = document.getElementById('inputString').value.trim();

        if (!inputString) {
            showError('Please enter a string to evaluate');
            return;
        }

        updateGrammarData();

        if (!grammarData.initialAxiom || grammarData.productions.length === 0) {
            showError('Please define a valid grammar first');
            return;
        }

        loadingSpinner.classList.remove('d-none');
        resultsCard.classList.remove('d-none');
        grammarTypeResult.innerHTML = '';
        stringResult.classList.add('d-none');
        derivationsResult.classList.add('d-none');

        try {
            const response = await fetch('/evaluate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    grammar_text: formatGrammarForAPI(),
                    input_string: inputString
                })
            });
            
            console.log(
                'Grammar:', formatGrammarForAPI(),
                'Input String:', inputString,
                'Response:', response.status, response.statusText
            )

            const data = await response.json();

            if (response.ok) {
                showResults(data);
            } else {
                showError(data.error || 'Error evaluating grammar');
            }
        } catch (error) {
            showError('Network error: ' + error.message);
        } finally {
            loadingSpinner.classList.add('d-none');
        }
    }

    function formatGrammarForAPI() {
        return `
N = ${Array.from(grammarData.nonTerminals).join(' ')}
T = ${Array.from(grammarData.terminals).join(' ')}
S = ${grammarData.initialAxiom}
P = {
${grammarData.productions.map(p => `    ${p.lhs} → ${p.rhs.length ? p.rhs.join(' ') : 'ε'}`).join('\n')}
}`;
    }

    function showResults(data) {
        let formattedDerivations = data.derivation;
        if (formattedDerivations) {
            // Convertir *A* a <strong>A</strong> y → a símbolos de flecha
            formattedDerivations = formattedDerivations
                .replace(/\* ([A-Z]) \*/g, '<strong>$1</strong>')
                .replace(/→/g, '→');
        }

        grammarTypeResult.innerHTML = `
        <div class="alert alert-${data.belongs_to_grammar ? 'success' : 'danger'}">
            <strong>Grammar Type:</strong> ${data.grammar_type}<br>
            <strong>Result:</strong> ${data.message}
        </div>
    `;

        if (data.derivation && data.belongs_to_grammar) {
            derivationsText.innerHTML = formattedDerivations;
            derivationsResult.classList.remove('d-none');
        }

        stringResult.classList.remove('d-none');
    }

    function showError(message) {
        grammarTypeResult.innerHTML = `<div class="alert alert-danger">${message}</div>`;
        resultsCard.classList.remove('d-none');
    }

    // ==================== FUNCIONES DE ARCHIVOS ====================
    function saveGrammarToFile() {
        updateGrammarData();

        if (!grammarData.initialAxiom || grammarData.productions.length === 0) {
            showError('No grammar to save');
            return;
        }

        const grammarJson = {
            initialAxiom: grammarData.initialAxiom,
            productions: grammarData.productions
        };

        const blob = new Blob([JSON.stringify(grammarJson, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'grammar.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function loadGrammarFromFile(event) {

    }

    function clearAll() {
        while (productionRulesTable.rows.length > 1) {
            productionRulesTable.deleteRow(1);
        }

        const firstRow = productionRulesTable.rows[0];
        firstRow.cells[0].querySelector('input').value = '';
        firstRow.cells[2].querySelector('input').value = '';

        resultsCard.classList.add('d-none');
        grammarData = {
            initialAxiom: '',
            nonTerminals: new Set(),
            terminals: new Set(),
            productions: []
        };
    }

    // ==================== EVENT LISTENERS ====================
    initialAxiomInput.addEventListener('input', () => validateInitialAxiom(initialAxiomInput));

    inputString.addEventListener('input', () => validateInputString(inputString));
        
    document.getElementById('AddRuleBtn').addEventListener('click', function() {
        if (productionRulesTable.rows.length < 10) {
            addNewProductionRule();
        } else {
            alert('Maximum of 10 production rules reached');
        }
    });

    document.getElementById('DelRuleBtn').addEventListener('click', function() {
        if (productionRulesTable.rows.length > 1) {
            productionRulesTable.deleteRow(productionRulesTable.rows.length - 1);
        }
    });

    // Botones para resultados
    showGrammarButton.addEventListener('click', showGrammar);
    evaluateStringButton.addEventListener('click', evaluateString);
    clearAllButton.addEventListener('click', clearAll);

    // Manejo de archivos
    saveProductionButton.addEventListener('click', saveGrammarToFile);
    uploadProductionButton.addEventListener('click', function () {
        productionFileInput.click();
    });
    productionFileInput.addEventListener('change', loadGrammarFromFile);

    initializeTable();
});