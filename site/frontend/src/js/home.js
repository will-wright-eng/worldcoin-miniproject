document.addEventListener('DOMContentLoaded', async () => {
    await initializePage();
});

async function initializePage() {
    await loadMetrics();
    await loadDataDetails();
    await loadMongoDBInfo();
    setupEventListeners();
}

function setupEventListeners() {
    document.getElementById('refreshMetrics').addEventListener('click', loadMetrics);
    document.getElementById('sampleSubmit').addEventListener('click', sampleData);
}

async function loadMetrics() {
    const metricsEndpoints = [
        '/api/v1/status/fraction_processed',
        '/api/v1/status/fraction_correct_audits',
        '/api/v1/status/count_unannotated_predictions'
    ];
    for (const url of metricsEndpoints) {
        await updateMetric(url);
    }
}

async function updateMetric(url) {
    const response = await fetchData(url);
    if (response && response.field_name && response.value !== undefined) {
        document.getElementById(response.field_name).textContent = response.value.toFixed(2);
    }
}

async function sampleData() {
    const data = await fetchData('/api/v1/model_failure_inspection/sample');
    document.getElementById('sampleDataResult').textContent = JSON.stringify(data, null, 2);
}

async function fetchData(url, options = {}) {
    try {
        const response = await fetch(url, options);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Fetch error:", error);
        return null;
    }
}

async function loadDataDetails() {
    const data = await fetchData('/api/v1/info/data_details');
    if (data) {
        document.getElementById('cwd').textContent = data["current working directory"];
        document.getElementById('dataFiles').textContent = data["data files"].join(', ');
        document.getElementById('dataDirFiles').textContent = data["data directory files"].join(', ');
    }
}

async function loadMongoDBInfo() {
    const info = await fetchData('/api/v1/info/mongodb_info');
    if (info) {
        document.getElementById('mongodbUri').textContent = info.mongodb_uri;
        document.getElementById('databaseName').textContent = info.database;
        document.getElementById('collections').textContent = info.collections.join(', ');

        const table = document.createElement('table');
        table.setAttribute('id', 'collectionsTable');

        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        const collectionHeader = document.createElement('th');
        collectionHeader.textContent = 'Collection Name';
        const countHeader = document.createElement('th');
        countHeader.textContent = 'Document Count';
        headerRow.appendChild(collectionHeader);
        headerRow.appendChild(countHeader);
        thead.appendChild(headerRow);
        table.appendChild(thead);

        const tbody = document.createElement('tbody');

        for (const collectionName of info.collections) {
            const count = await fetchCollectionCount(collectionName);
            const row = document.createElement('tr');
            const collectionCell = document.createElement('td');
            collectionCell.textContent = collectionName;
            const countCell = document.createElement('td');
            countCell.textContent = count;
            row.appendChild(collectionCell);
            row.appendChild(countCell);
            tbody.appendChild(row);
        }

        table.appendChild(tbody);

        document.getElementById('collectionsContainer').innerHTML = '';
        document.getElementById('collectionsContainer').appendChild(table);
    }
}

async function fetchCollectionCount(collectionName) {
    if (collectionName == "model_failure_inspection") {
        const url = '/api/v1/model_failure_inspection/count';
        const data = await fetchData(url);
        return data ? data.count : 'Error fetching count';
    } else {
        const url = `/api/v1/info/count/${collectionName}`;
        const data = await fetchData(url);
        return data ? data.count : 'Error fetching count';
    }
}
