Array.prototype.max = function() {
    return Math.max.apply(null, this);
}; 

Array.prototype.min = function() {
    return Math.min.apply(null, this);
};

let relations = [];

function clearInputs() {
    document.querySelectorAll('.weight-input').forEach(input => input.value = '');
    document.querySelectorAll('.number-input').forEach(input => input.value = '');

    relations = [];
    document.getElementById('relation-list').innerHTML = '';

    document.getElementById('result').innerHTML = '';
    document.getElementById('iterations').innerHTML = '';
}

function buildMatrixD(weightElements, weights) {
    const matrix_D = Array.from({ length: weightElements.length }, () => Array(weightElements.length).fill(0));
    for (let i = 0; i < weightElements.length; i++) {
        let currentWeightSum = 0;
        for (let j = i + 1; j < weightElements.length; j++) {
            currentWeightSum += weights[j - 1];
            matrix_D[weightElements[i] - 1][weightElements[j] - 1] = currentWeightSum;
            matrix_D[weightElements[j] - 1][weightElements[i] - 1] = currentWeightSum; 
        }
    }
    return matrix_D;
}

function buildMatrixC(relations) {
    const matrix_C = Array.from({ length: 5 }, () => Array(5).fill(0));
    relations.forEach(relation => {
        matrix_C[relation.element1 - 1][relation.element2 - 1] = relation.count;
        matrix_C[relation.element2 - 1][relation.element1 - 1] = relation.count;
    });
    return matrix_C;
}

function buildVectorView(matrix) {
    return matrix.map(row => row.reduce((sum, value) => sum + value, 0));
}

function processReorganization(vector_D, vector_C, initialState) {
    const newState = [...initialState];
    const iterationLogs = [];

    for (let i = 0; i < vector_C.length; i++) {
        const elemIndex = vector_C.indexOf(vector_C.max());
        const elem = elemIndex + 1;

        const positionIndex = vector_D.indexOf(vector_D.min());
        const position = initialState.indexOf(positionIndex + 1);

        newState[position] = elem;
        iterationLogs.push(`Ітерація ${i + 1}: Елемент ${elem} переміщується на позицію ${position + 1}`);
        
        vector_C[elemIndex] = -Infinity;
        vector_D[positionIndex] = Infinity;
    }

    return { newState, iterationLogs };
}

function calculateQualityCriterion(matrixC, matrixD) {
    let sum = 0;
    for (let i = 0; i < matrixC.length; i++) {
        for (let j = 0; j < matrixC[i].length; j++) {
            sum += matrixC[i][j] * matrixD[i][j];
        }
    }
    return sum / 2;
}

function formatMatrixToTable(matrix) {
    const table = document.createElement('table');
    table.style.borderCollapse = 'collapse';
    matrix.forEach(row => {
        const tr = document.createElement('tr');
        row.forEach(cell => {
            const td = document.createElement('td');
            td.textContent = cell;
            td.style.border = '1px solid black';
            td.style.padding = '5px';
            tr.appendChild(td);
        });
        table.appendChild(tr);
    });
    return table;
}

function formatVectorToList(vector) {
    const ul = document.createElement('ul');
    vector.forEach(value => {
        const li = document.createElement('li');
        li.textContent = value;
        ul.appendChild(li);
    });
    return ul;
}

document.getElementById('add-relation').addEventListener('click', () => {
    const element1 = parseInt(document.getElementById('relation1').value);
    const count = parseInt(document.getElementById('relation').value);
    const element2 = parseInt(document.getElementById('relation2').value);

    if (!isNaN(element1) && !isNaN(count) && !isNaN(element2)) {
        relations.push({ element1, element2, count });

        const relationList = document.getElementById('relation-list');
        const listItem = document.createElement('li');
        listItem.textContent = `Елемент ${element1} з'єднується з елементом ${element2}, з кількістю з'єднань ${count}`;
        relationList.appendChild(listItem);
    }
});

document.querySelector('.calculate').addEventListener('click', () => {
    const weights = [
        parseInt(document.getElementById('weight1').value),
        parseInt(document.getElementById('weight2').value),
        parseInt(document.getElementById('weight3').value),
        parseInt(document.getElementById('weight4').value)
    ];

    const weightElements = [
        parseInt(document.getElementById('places1').value), 
        parseInt(document.getElementById('places2').value),
        parseInt(document.getElementById('places3').value),
        parseInt(document.getElementById('places4').value),
        parseInt(document.getElementById('places5').value),
    ];

    const matrix_D = buildMatrixD(weightElements, weights);
    const matrix_C = buildMatrixC(relations);
   
    const vector_D = buildVectorView(matrix_D);
    const vector_C = buildVectorView(matrix_C);

    const { newState, iterationLogs } = processReorganization([...vector_D], [...vector_C], weightElements);
    const processedMatrixD = buildMatrixD(newState, weights);

    const k1 = calculateQualityCriterion(matrix_C, matrix_D);
    const k2 = calculateQualityCriterion(matrix_C, processedMatrixD);
    const percent = (k1 - k2) / k1 * 100;

    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = '<h3>Результат:</h3>';

    resultDiv.innerHTML += '<p><strong>Матриця D:</strong></p>';
    resultDiv.appendChild(formatMatrixToTable(matrix_D));

    resultDiv.innerHTML += '<p><strong>Матриця C:</strong></p>';
    resultDiv.appendChild(formatMatrixToTable(matrix_C));

    resultDiv.innerHTML += '<p><strong>D*:</strong></p>';
    resultDiv.appendChild(formatVectorToList(vector_D));

    resultDiv.innerHTML += '<p><strong>C*:</strong></p>';
    resultDiv.appendChild(formatVectorToList(vector_C));

    resultDiv.innerHTML += `<p><strong>Нова схема місць:</strong> ${newState.join(', ')}</p>`;
    resultDiv.innerHTML += `<p><strong>Кпоч:</strong> ${k1}</p>`;
    resultDiv.innerHTML += `<p><strong>Ккін:</strong> ${k2}</p>`;
    resultDiv.innerHTML += `<p><strong>E:</strong> ${Math.abs(Math.round(percent * 100) / 100)}%</p>`;

    const iterationsDiv = document.getElementById('iterations');
    iterationsDiv.innerHTML = '<h3>Ітерації:</h3>';
    iterationLogs.forEach(log => {
        const p = document.createElement('p');
        p.textContent = log;
        iterationsDiv.appendChild(p);
    });
});

document.getElementById('clear-data').addEventListener('click', clearInputs);