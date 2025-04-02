// Expenses.js - Simplified version for compatibility
document.addEventListener('DOMContentLoaded', function() {
    // Initialize expenses page with static data for testing
    displayStaticExpenses();
    setupEventListeners();
});

// Set up event listeners
function setupEventListeners() {
    // Filter buttons
    document.getElementById('filterAll').addEventListener('click', function() {
        setActiveFilter(this);
        // Would fetch expenses in real implementation
    });
    
    document.getElementById('filterRecurring').addEventListener('click', function() {
        setActiveFilter(this);
        // Would fetch recurring expenses in real implementation
    });
    
    document.getElementById('filterOneTime').addEventListener('click', function() {
        setActiveFilter(this);
        // Would fetch one-time expenses in real implementation
    });
    
    // Form events
    document.getElementById('isRecurring').addEventListener('change', function() {
        toggleRecurringOptions();
    });
    
    document.getElementById('saveExpense').addEventListener('click', function() {
        alert('In a real implementation, this would save the expense to the database.');
    });
    
    // Delete confirmation
    document.getElementById('confirmDelete').addEventListener('click', function() {
        alert('In a real implementation, this would delete the expense from the database.');
    });
}

// Display static expenses for testing
function displayStaticExpenses() {
    const tableBody = document.getElementById('expensesTable').getElementsByTagName('tbody')[0];
    tableBody.innerHTML = '';
    
    const testExpenses = [
        { id: 'exp-1', name: 'Rent', amount: 800, category: 'Housing', isRecurring: true, frequency: 'monthly', startDate: '2025-04-01' },
        { id: 'exp-2', name: 'Utilities', amount: 120, category: 'Housing', isRecurring: true, frequency: 'monthly', startDate: '2025-04-05' },
        { id: 'exp-3', name: 'Groceries', amount: 200, category: 'Food', isRecurring: true, frequency: 'weekly', startDate: '2025-04-10' },
        { id: 'exp-4', name: 'Internet', amount: 80, category: 'Utilities', isRecurring: true, frequency: 'monthly', startDate: '2025-04-15' },
        { id: 'exp-5', name: 'Car Repair', amount: 350, category: 'Transportation', isRecurring: false, frequency: 'one-time', startDate: '2025-04-20' }
    ];
    
    testExpenses.forEach(expense => {
        const row = tableBody.insertRow();
        
        const nameCell = row.insertCell(0);
        nameCell.textContent = expense.name;
        
        const amountCell = row.insertCell(1);
        amountCell.textContent = '$' + expense.amount.toFixed(2);
        amountCell.className = 'text-danger';
        
        const categoryCell = row.insertCell(2);
        categoryCell.textContent = expense.category;
        
        const frequencyCell = row.insertCell(3);
        if (expense.isRecurring) {
            frequencyCell.textContent = capitalizeFirstLetter(expense.frequency);
        } else {
            frequencyCell.textContent = 'One-time';
        }
        
        const dateCell = row.insertCell(4);
        dateCell.textContent = formatDate(expense.startDate);
        
        const actionsCell = row.insertCell(5);
        actionsCell.innerHTML = `
            <button class="btn btn-sm btn-outline-primary me-1 edit-expense" data-id="${expense.id}">
                <i class="bi bi-pencil"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger delete-expense" data-id="${expense.id}">
                <i class="bi bi-trash"></i>
            </button>
        `;
    });
    
    // Add event listeners to edit and delete buttons
    document.querySelectorAll('.edit-expense').forEach(button => {
        button.addEventListener('click', function() {
            alert('In a real implementation, this would open the edit form for this expense.');
        });
    });
    
    document.querySelectorAll('.delete-expense').forEach(button => {
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
