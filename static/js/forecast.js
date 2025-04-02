// Forecast.js - Simplified version for compatibility
document.addEventListener('DOMContentLoaded', function() {
    // Initialize forecast page
    setupEventListeners();
    initializeFormElements();
});

// Set up event listeners
function setupEventListeners() {
    // Calculate forecast button
    document.getElementById('calculateForecast').addEventListener('click', function() {
        displayStaticForecast();
    });
    
    // Export CSV button
    document.getElementById('exportCSV').addEventListener('click', function() {
        alert('In a real implementation, this would export the forecast data to CSV.');
    });
    
    // Print report button
    document.getElementById('printForecast').addEventListener('click', function() {
        alert('In a real implementation, this would print the forecast report.');
    });
}

// Initialize form elements
function initializeFormElements() {
    // Set default date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('startDate').value = today;
    
    // Set default values
    document.getElementById('forecastPeriod').value = 8;
    document.getElementById('initialBalance').value = 5000;
}

// Display static forecast for testing
function displayStaticForecast() {
    // Show results section
    document.getElementById('forecastResults').style.display = 'block';
    
    // Update summary values
    document.getElementById('startingBalanceDisplay').textContent = '$5,000.00';
    document.getElementById('lowestBalanceDisplay').textContent = '$4,200.00';
    document.getElementById('endingBalanceDisplay').textContent = '$7,500.00';
    
    // Hide low balance alert
    document.getElementById('lowBalanceAlert').style.display = 'none';
    
    // Populate forecast table with test data
    const tableBody = document.getElementById('forecastTable').getElementsByTagName('tbody')[0];
    tableBody.innerHTML = '';
    
    const testForecast = [
        { week: 1, date: '2025-04-08', startingBalance: 5000, inflows: 0, outflows: 200, endingBalance: 4800 },
        { week: 2, date: '2025-04-15', startingBalance: 4800, inflows: 0, outflows: 600, endingBalance: 4200 },
        { week: 3, date: '2025-04-22', startingBalance: 4200, inflows: 2000, outflows: 300, endingBalance: 5900 },
        { week: 4, date: '2025-04-29', startingBalance: 5900, inflows: 500, outflows: 400, endingBalance: 6000 },
        { week: 5, date: '2025-05-06', startingBalance: 6000, inflows: 0, outflows: 200, endingBalance: 5800 },
        { week: 6, date: '2025-05-13', startingBalance: 5800, inflows: 0, outflows: 300, endingBalance: 5500 },
        { week: 7, date: '2025-05-20', startingBalance: 5500, inflows: 2000, outflows: 500, endingBalance: 7000 },
        { week: 8, date: '2025-05-27', startingBalance: 7000, inflows: 800, outflows: 300, endingBalance: 7500 }
    ];
    
    testForecast.forEach(entry => {
        const row = tableBody.insertRow();
        
        const weekCell = row.insertCell(0);
        weekCell.textContent = 'Week ' + entry.week + ' (' + formatDate(entry.date) + ')';
        
        const startingBalanceCell = row.insertCell(1);
        startingBalanceCell.textContent = '$' + entry.startingBalance.toFixed(2);
        
        const inflowsCell = row.insertCell(2);
        inflowsCell.textContent = '$' + entry.inflows.toFixed(2);
        inflowsCell.className = 'text-success';
        
        const outflowsCell = row.insertCell(3);
        outflowsCell.textContent = '$' + entry.outflows.toFixed(2);
        outflowsCell.className = 'text-danger';
        
        const endingBalanceCell = row.insertCell(4);
        endingBalanceCell.textContent = '$' + entry.endingBalance.toFixed(2);
        if (entry.endingBalance < 0) {
            endingBalanceCell.className = 'text-danger fw-bold';
        }
    });
    
    // Add placeholder text for chart
    const chartCanvas = document.getElementById('forecastChart');
    if (chartCanvas) {
        const chartContext = chartCanvas.getContext('2d');
        chartContext.clearRect(0, 0, chartCanvas.width, chartCanvas.height);
        chartContext.font = '16px Arial';
        chartContext.fillStyle = '#0d6efd';
        chartContext.textAlign = 'center';
        chartContext.fillText('Cash Flow Forecast Chart (Static Demo)', chartCanvas.width/2, chartCanvas.height/2);
    }
}

// Helper function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}
