// Revenue.js - Simplified version for compatibility
document.addEventListener('DOMContentLoaded', function() {
    // Initialize revenue page with static data for testing
    displayStaticRevenue();
    setupEventListeners();
});

// Set up event listeners
function setupEventListeners() {
    // Filter buttons
    document.getElementById('filterAll').addEventListener('click', function() {
        setActiveFilter(this);
        // Would fetch revenue in real implementation
    });
    
    document.getElementById('filterRecurring').addEventListener('click', function() {
        setActiveFilter(this);
        // Would fetch recurring revenue in real implementation
    });
    
    document.getElementById('filterOneTime').addEventListener('click', function() {
        setActiveFilter(this);
        // Would fetch one-time revenue in real implementation
    });
    
    // Form events
    document.getElementById('isRecurring').addEventListener('change', function() {
        toggleRecurringOptions();
    });
    
    document.getElementById('saveRevenue').addEventListener('click', function() {
        alert('In a real implementation, this would save the revenue to the database.');
    });
    
    // Delete confirmation
    document.getElementById('confirmDelete').addEventListener('click', function() {
        alert('In a real implementation, this would delete the revenue from the database.');
    });
}

// Display static revenue for testing
function displayStaticRevenue() {
    const tableBody = document.getElementById('revenueTable').getElementsByTagName('tbody')[0];
    tableBody.innerHTML = '';
    
    const testRevenue = [
        { id: 'rev-1', source: 'Salary', amount: 2000, probability: 100, isRecurring: true, frequency: 'monthly', startDate: '2025-04-25' },
        { id: 'rev-2', source: 'Freelance Work', amount: 500, probability: 80, isRecurring: false, frequency: 'one-time', startDate: '2025-04-15' },
        { id: 'rev-3', source: 'Consulting', amount: 800, probability: 70, isRecurring: true, frequency: 'monthly', startDate: '2025-04-10' },
        { id: 'rev-4', source: 'Investment Dividend', amount: 300, probability: 95, isRecurring: true, frequency: 'quarterly', startDate: '2025-05-01' }
    ];
    
    testRevenue.forEach(item => {
        const row = tableBody.insertRow();
        
        const sourceCell = row.insertCell(0);
        sourceCell.textContent = item.source;
        
        const amountCell = row.insertCell(1);
        amountCell.textContent = '$' + item.amount.toFixed(2);
        
        const probabilityCell = row.insertCell(2);
        probabilityCell.textContent = item.probability + '%';
        
        const expectedCell = row.insertCell(3);
        const expectedAmount = item.amount * (item.probability / 100);
        expectedCell.textContent = '$' + expectedAmount.toFixed(2);
        expectedCell.className = 'text-success';
        
        const frequencyCell = row.insertCell(4);
        if (item.isRecurring) {
            frequencyCell.textContent = capitalizeFirstLetter(item.frequency);
        } else {
            frequencyCell.textContent = 'One-time';
        }
        
        const dateCell = row.insertCell(5);
        dateCell.textContent = formatDate(item.startDate);
        
        const actionsCell = row.insertCell(6);
        actionsCell.innerHTML = `
            <button class="btn btn-sm btn-outline-primary me-1 edit-revenue" data-id="${item.id}">
                <i class="bi bi-pencil"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger delete-revenue" data-id="${item.id}">
                <i class="bi bi-trash"></i>
            </button>
        `;
    });
    
    // Add event listeners to edit and delete buttons
    document.querySelectorAll('.edit-revenue').forEach(button => {
        button.addEventListener('click', function() {
            alert('In a real implementation, this would open the edit form for this revenue item.');
        });
    });
    
    document.querySelectorAll('.delete-revenue').forEach(button => {
        button.addEventListener('click', function() {
            alert('In a real implementation, this would open the delete confirmation modal.');
        });
    });
}

// Toggle recurring options based on checkbox
function toggleRecurringOptions() {
    const isRecurring = document.getElementById('isRecurring').checked;
    const recurringOptions = document.getElementById('recurringOptions');
    const endDateContainer = document.getElementById('endDateContainer');
    
    if (isRecurring) {
        recurringOptions.style.display = 'block';
        endDateContainer.style.display = 'block';
    } else {
        recurringOptions.style.display = 'none';
        endDateContainer.style.display = 'none';
    }
}

// Set active filter button
function setActiveFilter(button) {
    // Remove active class from all filter buttons
    document.querySelectorAll('.btn-group .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Add active class to clicked button
    button.classList.add('active');
}

// Helper function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

// Helper function to capitalize first letter
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
