// Dashboard.js - Simplified version without Chart.js for compatibility
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard with static data for testing
    updateDashboardData();
});

// Update dashboard with static test data
function updateDashboardData() {
    // Set static values for testing
    document.getElementById('currentBalance').textContent = '$5,000.00';
    document.getElementById('monthlyExpenses').textContent = '$1,200.00';
    document.getElementById('monthlyRevenue').textContent = '$2,500.00';
    
    // Populate recent expenses table with test data
    const expensesTable = document.getElementById('recentExpensesTable').getElementsByTagName('tbody')[0];
    expensesTable.innerHTML = '';
    
    const testExpenses = [
        { name: 'Rent', amount: 800, date: '2025-04-01' },
        { name: 'Utilities', amount: 120, date: '2025-04-05' },
        { name: 'Groceries', amount: 200, date: '2025-04-10' },
        { name: 'Internet', amount: 80, date: '2025-04-15' }
    ];
    
    testExpenses.forEach(expense => {
        const row = expensesTable.insertRow();
        
        const nameCell = row.insertCell(0);
        nameCell.textContent = expense.name;
        
        const amountCell = row.insertCell(1);
        amountCell.textContent = '$' + expense.amount.toFixed(2);
        amountCell.className = 'text-danger';
        
        const dateCell = row.insertCell(2);
        dateCell.textContent = formatDate(expense.date);
    });
    
    // Populate upcoming revenue table with test data
    const revenueTable = document.getElementById('upcomingRevenueTable').getElementsByTagName('tbody')[0];
    revenueTable.innerHTML = '';
    
    const testRevenue = [
        { source: 'Salary', amount: 2000, date: '2025-04-25' },
        { source: 'Freelance Work', amount: 500, date: '2025-04-15' }
    ];
    
    testRevenue.forEach(revenue => {
        const row = revenueTable.insertRow();
        
        const sourceCell = row.insertCell(0);
        sourceCell.textContent = revenue.source;
        
        const amountCell = row.insertCell(1);
        amountCell.textContent = '$' + revenue.amount.toFixed(2);
        amountCell.className = 'text-success';
        
        const dateCell = row.insertCell(2);
        dateCell.textContent = formatDate(revenue.date);
    });
    
    // Add placeholder text for chart
    const chartCanvas = document.getElementById('cashFlowChart');
    const chartContext = chartCanvas.getContext('2d');
    chartContext.font = '16px Arial';
    chartContext.fillStyle = '#0d6efd';
    chartContext.textAlign = 'center';
    chartContext.fillText('Cash Flow Forecast Chart (Static Demo)', chartCanvas.width/2, chartCanvas.height/2);
}

// Helper function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}
