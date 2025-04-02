// Settings.js - Simplified version for compatibility
document.addEventListener('DOMContentLoaded', function() {
    // Initialize settings page with static data for testing
    displayStaticSettings();
    setupEventListeners();
});

// Set up event listeners
function setupEventListeners() {
    // Save settings button
    document.getElementById('saveSettings').addEventListener('click', function() {
        alert('In a real implementation, this would save the settings to the database.');
    });
    
    // Currency change event
    document.getElementById('currency').addEventListener('change', function() {
        updateCurrencySymbol();
    });
    
    // Theme change event
    document.getElementById('theme').addEventListener('change', function() {
        updateThemePreview();
    });
}

// Display static settings for testing
function displayStaticSettings() {
    // Set default values
    document.getElementById('currency').value = 'USD';
    document.getElementById('dateFormat').value = 'MM/DD/YYYY';
    document.getElementById('theme').value = 'light';
    document.getElementById('lowBalanceThreshold').value = 1000;
    document.getElementById('defaultForecastWeeks').value = 8;
    
    // Update currency symbol
    updateCurrencySymbol();
}

// Update currency symbol
function updateCurrencySymbol() {
    const currency = document.getElementById('currency').value;
    const currencySymbol = getCurrencySymbol(currency);
    document.getElementById('currencySymbol').textContent = currencySymbol;
}

// Update theme preview
function updateThemePreview() {
    const theme = document.getElementById('theme').value;
    if (theme === 'dark') {
        document.body.classList.add('dark-theme');
    } else {
        document.body.classList.remove('dark-theme');
    }
}

// Helper function to get currency symbol
function getCurrencySymbol(currency) {
    const symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'CAD': 'C$',
        'AUD': 'A$'
    };
    
    return symbols[currency] || '$';
}
