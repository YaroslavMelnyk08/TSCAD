document.addEventListener("DOMContentLoaded", function() {
    const matrixTable = document.getElementById('matrix');
    const randomMatrixTable = document.getElementById('random-matrix');
    const resultContainer = document.getElementById('result');

    for (let i = 0; i < 4; i++) {
        const row = document.createElement('tr');
        for (let j = 0; j < 5; j++) {
            const cell = document.createElement('td');
            const input = document.createElement('input');
            input.type = 'number';
            input.className = 'matrix-input';
            input.id = `cell-${i}-${j}`;
            cell.appendChild(input);
            row.appendChild(cell);
        }
        matrixTable.appendChild(row);
    }

    let relations = [];
    let placedElements = [];
    const totalElements = 12;

    document.getElementById('add-relation').addEventListener('click', () => {
        const element1 = parseInt(document.getElementById('relation1').value);
        const count = parseInt(document.getElementById('relation').value);
        const element2 = parseInt(document.getElementById('relation2').value);

        if (!isNaN(element1) && !isNaN(count) && !isNaN(element2)) {
            relations.push({ element1, element2, count });
            relations.push({ element1: element2, element2: element1, count });
            const relationList = document.getElementById('relation-list');
            const listItem = document.createElement('li');
            listItem.textContent = `Елемент ${element1} з'єднується з елементом ${element2}, кількість з'єднань: ${count}`;
            relationList.appendChild(listItem);
        }
    });

    document.querySelector('.calculate-btn').addEventListener('click', () => {
        const randomMatrix = generateRandomMatrix();
        const randomKkin = calculateKkin(relations, randomMatrix);
        displayRandomMatrix(randomMatrix);
        resultContainer.innerHTML = `<h2>Kпоч: ${randomKkin}</h2>`;

        const matrix = [];
        placedElements = [];

        for (let i = 0; i < 4; i++) {
            const row = [];
            for (let j = 0; j < 5; j++) {
                const value = parseInt(document.getElementById(`cell-${i}-${j}`).value);
                if (!isNaN(value) && value > 0) {
                    placedElements.push(value);
                }
                row.push(value || 0);
            }
            matrix.push(row);
        }

        showInitialConnections();

        let iterationCount = 1;

        // Ітерації розміщення
        while (placedElements.length < totalElements) {
            let bestCandidate = null;
            let bestPlacedConnections = -1;
            let bestUnplacedConnections = Infinity;

            relations.forEach(({ element1 }) => {
                if (!placedElements.includes(element1)) {
                    const placedConnections = relations
                        .filter(r => placedElements.includes(r.element2) && r.element1 === element1)
                        .reduce((acc, r) => acc + r.count, 0);

                    const unplacedConnections = relations
                        .filter(r => !placedElements.includes(r.element2) && r.element1 === element1)
                        .reduce((acc, r) => acc + r.count, 0);

                    if (
                        placedConnections > bestPlacedConnections ||
                        (placedConnections === bestPlacedConnections && unplacedConnections < bestUnplacedConnections) ||
                        (placedConnections === bestPlacedConnections && unplacedConnections === bestUnplacedConnections && element1 < bestCandidate)
                    ) {
                        bestPlacedConnections = placedConnections;
                        bestUnplacedConnections = unplacedConnections;
                        bestCandidate = element1;
                    }
                }
            });

            if (bestCandidate !== null) {
                const bestPosition = findBestPosition(bestCandidate, matrix);
                const [x, y] = placeElement(bestCandidate, matrix, bestPosition);

                const iterationResult = `Ітерація ${iterationCount}: Ел. ${bestCandidate} (${getConnectionCounts(bestCandidate)}) розміщено на позиції [${x}, ${y}]`;
                resultContainer.innerHTML += iterationResult + "<br>";

                placedElements.push(bestCandidate);
                iterationCount++;

                updateConnectionCounts(bestCandidate);
                showUpdatedConnections();
            } else {
                break;
            }
        }

        const originalKkin = calculateKkin(relations, matrix);
        resultContainer.innerHTML += `<h3>Kкін: ${originalKkin}</h3>`;

        e = Math.round(((randomKkin - originalKkin) / randomKkin ) * 100, 2);
        resultContainer.innerHTML += `<h3>E: ${e}%</h3>`;
    });

    function generateRandomMatrix() {
        const newMatrix = Array.from({ length: 4 }, () => Array(5).fill(null));
        let availableNumbers = Array.from({ length: 12 }, (_, i) => i + 1);
        let emptyPositions = [];
        let fixedElements = [];
        
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 5; j++) {
                const cellValue = parseInt(document.getElementById(`cell-${i}-${j}`).value);
                if (!isNaN(cellValue) && cellValue > 0) {
                    fixedElements.push({ value: cellValue, position: [i, j] });
                    availableNumbers = availableNumbers.filter(num => num !== cellValue);
                    newMatrix[i][j] = cellValue;
                } else {
                    emptyPositions.push([i, j]);
                }
            }
        }

        emptyPositions = shuffleArray(emptyPositions);
        
        availableNumbers = shuffleArray(availableNumbers); 

        for (let i = 0; i < availableNumbers.length; i++) {
            const [row, col] = emptyPositions[i];
            newMatrix[row][col] = availableNumbers[i];
        }

        return newMatrix;
    }

    function shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    function displayRandomMatrix(matrix) {
        randomMatrixTable.innerHTML = "";
        for (let i = 0; i < 4; i++) {
            const row = document.createElement('tr');
            for (let j = 0; j < 5; j++) {
                const cell = document.createElement('td');
                cell.textContent = matrix[i][j];
                row.appendChild(cell);
            }
            randomMatrixTable.appendChild(row);
        }
    }

    function placeElement(element, matrix, position) {
        const [i, j] = position;
        const cell = document.getElementById(`cell-${i}-${j}`);
        cell.value = element;
        matrix[i][j] = element;
        return [i, j];
    }

    function findBestPosition(element, matrix) {
        const distances = [];
        relations.forEach(({ element1, element2 }) => {
            if (element1 === element && placedElements.includes(element2)) {
                const [x2, y2] = findElementPosition(element2, matrix);
                if (x2 !== -1) {
                    for (let i = 0; i < 4; i++) {
                        for (let j = 0; j < 5; j++) {
                            const cell = document.getElementById(`cell-${i}-${j}`);
                            if (!cell.value) {
                                const distance = Math.abs(x2 - i) + Math.abs(y2 - j);
                                distances.push({ distance, position: [i, j] });
                            }
                        }
                    }
                }
            }
        });
        distances.sort((a, b) => a.distance - b.distance);
        return distances.length > 0 ? distances[0].position : [0, 0];
    }

    function getConnectionCounts(element) {
        const placedConnections = relations
            .filter(r => placedElements.includes(r.element2) && r.element1 === element)
            .reduce((acc, r) => acc + r.count, 0);
    
        const unplacedConnections = relations
            .filter(r => !placedElements.includes(r.element2) && r.element1 === element)
            .reduce((acc, r) => acc + r.count, 0);
    
        return `${placedConnections}, ${unplacedConnections}`;
    }    

    function updateConnectionCounts(placedElement) {
        relations = relations.map(r => {
            if (r.element1 === placedElement || r.element2 === placedElement) {
                if (!placedElements.includes(r.element2)) {
                    return { ...r, count: Math.max(0, r.count - 1) };
                }
            }
            return r;
        });
    }    

    function showInitialConnections() {
        const elementConnections = {};

        relations.forEach(({ element1, element2, count }) => {
            if (!elementConnections[element1]) {
                elementConnections[element1] = { placed: 0, unplaced: 0 };
            }
            if (placedElements.includes(element2)) {
                elementConnections[element1].placed += count;
            } else {
                elementConnections[element1].unplaced += count;
            }
        });

        resultContainer.innerHTML += "<h3>Початкові зв'язки:</h3>";
        for (const element in elementConnections) {
            const { placed, unplaced } = elementConnections[element];
            resultContainer.innerHTML += `Ел. ${element} (${placed}, ${unplaced})<br>`;
        }
    }

    function showUpdatedConnections() {
        const elementConnections = {};
    
        relations.forEach(({ element1, element2, count }) => {
            if (!elementConnections[element1]) {
                elementConnections[element1] = { placed: 0, unplaced: 0 };
            }
            if (placedElements.includes(element2)) {
                elementConnections[element1].placed += count;
            } else {
                elementConnections[element1].unplaced += count;
            }
        });
    
        resultContainer.innerHTML += "<h3>Оновлені зв'язки:</h3>";
        for (const element in elementConnections) {
            const { placed, unplaced } = elementConnections[element];
            if (!placedElements.includes(parseInt(element))) {
                resultContainer.innerHTML += `Ел. ${element} (${placed}, ${unplaced})<br>`;
            }
        }
    }  

    function calculateKkin(relations, matrix) {
        let Kkin = 0;
        let processedPairs = new Set();
    
        relations.forEach(({ element1, element2, count }) => {
            const pairKey = `${element1}-${element2}`;
            const reversePairKey = `${element2}-${element1}`;

            if (processedPairs.has(reversePairKey)) {
                return;
            }
    
            const [x1, y1] = findElementPosition(element1, matrix);
            const [x2, y2] = findElementPosition(element2, matrix);
    
            if (x1 !== -1 && x2 !== -1) {
                const dx = Math.abs(x1 - x2);
                const dy = Math.abs(y1 - y2);
    
                const distance = (dx === 1 && dy === 1) ? 2 : (dx + dy);
                const addition = distance * count;
    
                Kkin += addition;
    
                console.log(`Елементи: ${element1} і ${element2}, відстань: ${distance}, кількість зв'язків: ${count}, додаток до Kкін: ${addition}`);

                processedPairs.add(pairKey);
            }
        });
        
        return Kkin;
    }       
       
    function findElementPosition(element, matrix) {
        for (let i = 0; i < matrix.length; i++) {
            for (let j = 0; j < matrix[i].length; j++) {
                if (matrix[i][j] === element) {
                    return [i, j];
                }
            }
        }
        return [-1, -1];
    }
});