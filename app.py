from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import os
import json
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
app.config['DATABASE'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance/cash_flow.db')

# Ensure the instance folder exists
os.makedirs(os.path.dirname(app.config['DATABASE']), exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Create expenses table
    conn.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        is_recurring BOOLEAN NOT NULL,
        frequency TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT,
        payment_day INTEGER NOT NULL,
        notes TEXT
    )
    ''')
    
    # Create revenue table
    conn.execute('''
    CREATE TABLE IF NOT EXISTS revenue (
        id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        amount REAL NOT NULL,
        probability REAL NOT NULL,
        is_recurring BOOLEAN NOT NULL,
        frequency TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT,
        payment_day INTEGER NOT NULL,
        notes TEXT
    )
    ''')
    
    # Create settings table
    conn.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY,
        currency TEXT DEFAULT 'USD',
        date_format TEXT DEFAULT 'MM/DD/YYYY',
        theme TEXT DEFAULT 'light',
        low_balance_threshold REAL DEFAULT 0.0,
        default_forecast_weeks INTEGER DEFAULT 8
    )
    ''')
    
    # Initialize settings if not exists
    settings = conn.execute('SELECT * FROM settings').fetchone()
    if not settings:
        conn.execute('''
        INSERT INTO settings (currency, date_format, theme, low_balance_threshold, default_forecast_weeks)
        VALUES (?, ?, ?, ?, ?)
        ''', ('USD', 'MM/DD/YYYY', 'light', 0.0, 8))
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Helper functions for cash flow forecasting
def generate_forecast(start_date, num_weeks, initial_balance):
    conn = get_db_connection()
    expenses = conn.execute('SELECT * FROM expenses').fetchall()
    revenue_items = conn.execute('SELECT * FROM revenue').fetchall()
    conn.close()
    
    # Convert start_date string to datetime object
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00')).replace(tzinfo=None)
    
    # Initialize forecast data
    forecast = {
        'startDate': start_date.isoformat(),
        'numWeeks': num_weeks,
        'entries': [],
        'lowestBalance': initial_balance,
        'highestBalance': initial_balance,
        'endingBalance': initial_balance
    }
    
    current_balance = initial_balance
    current_date = start_date
    
    # Generate weekly entries
    for week in range(num_weeks):
        end_date = current_date + timedelta(days=6)
        
        # Create entry for this week
        entry = {
            'date': current_date.isoformat(),
            'startingBalance': current_balance,
            'inflows': 0.0,
            'outflows': 0.0,
            'endingBalance': current_balance,
            'inflowDetails': [],
            'outflowDetails': []
        }
        
        # Process expenses for this week
        for expense in expenses:
            expense_start = datetime.fromisoformat(expense['start_date'].replace('Z', '+00:00')).replace(tzinfo=None)
            expense_end = None
            if expense['end_date']:
                expense_end = datetime.fromisoformat(expense['end_date'].replace('Z', '+00:00')).replace(tzinfo=None)
            
            # Skip expenses that start after the end date
            if expense_start > end_date:
                continue
                
            # Skip expenses that have ended before the start date
            if expense_end and expense_end < current_date:
                continue
                
            # Handle one-time expenses
            if not expense['is_recurring']:
                if current_date <= expense_start <= end_date:
                    entry['outflows'] += expense['amount']
                    entry['endingBalance'] -= expense['amount']
                    entry['outflowDetails'].append({
                        'amount': expense['amount'],
                        'name': expense['name'],
                        'expense_id': expense['id']
                    })
                continue
                
            # Handle recurring expenses based on frequency
            if is_payment_due(expense, current_date, end_date):
                entry['outflows'] += expense['amount']
                entry['endingBalance'] -= expense['amount']
                entry['outflowDetails'].append({
                    'amount': expense['amount'],
                    'name': expense['name'],
                    'expense_id': expense['id']
                })
        
        # Process revenue for this week
        for revenue in revenue_items:
            revenue_start = datetime.fromisoformat(revenue['start_date'].replace('Z', '+00:00')).replace(tzinfo=None)
            revenue_end = None
            if revenue['end_date']:
                revenue_end = datetime.fromisoformat(revenue['end_date'].replace('Z', '+00:00')).replace(tzinfo=None)
            
            # Skip revenue that starts after the end date
            if revenue_start > end_date:
                continue
                
            # Skip revenue that has ended before the start date
            if revenue_end and revenue_end < current_date:
                continue
                
            # Handle one-time revenue
            if not revenue['is_recurring']:
                if current_date <= revenue_start <= end_date:
                    expected_amount = revenue['amount'] * revenue['probability']
                    entry['inflows'] += expected_amount
                    entry['endingBalance'] += expected_amount
                    entry['inflowDetails'].append({
                        'amount': expected_amount,
                        'source': revenue['source'],
                        'source_id': revenue['id']
                    })
                continue
                
            # Handle recurring revenue based on frequency
            if is_payment_due(revenue, current_date, end_date):
                expected_amount = revenue['amount'] * revenue['probability']
                entry['inflows'] += expected_amount
                entry['endingBalance'] += expected_amount
                entry['inflowDetails'].append({
                    'amount': expected_amount,
                    'source': revenue['source'],
                    'source_id': revenue['id']
                })
        
        # Add entry to forecast
        forecast['entries'].append(entry)
        
        # Update forecast stats
        forecast['lowestBalance'] = min(forecast['lowestBalance'], entry['endingBalance'])
        forecast['highestBalance'] = max(forecast['highestBalance'], entry['endingBalance'])
        forecast['endingBalance'] = entry['endingBalance']
        
        # Update for next week
        current_balance = entry['endingBalance']
        current_date = end_date + timedelta(days=1)
    
    return forecast

def is_payment_due(item, start_date, end_date):
    """Check if a recurring payment is due within the given period"""
    item_start = datetime.fromisoformat(item['start_date'].replace('Z', '+00:00')).replace(tzinfo=None)
    item_end = None
    if item['end_date']:
        item_end = datetime.fromisoformat(item['end_date'].replace('Z', '+00:00')).replace(tzinfo=None)
    
    # If the item starts after the end date, it's not due
    if item_start > end_date:
        return False
        
    # If the item has ended before the start date, it's not due
    if item_end and item_end < start_date:
        return False
        
    # Check based on frequency
    if item['frequency'] == 'weekly':
        # Check if any day in the period matches the weekday of the item start date
        item_weekday = item_start.weekday()
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() == item_weekday:
                return True
            current_date += timedelta(days=1)
        return False
        
    elif item['frequency'] == 'monthly':
        # Check if the payment day falls within the period
        payment_day = item['payment_day']
        
        # Check if this day falls within our period
        for month_offset in range(-1, 2):  # Check previous, current, and next month
            year = start_date.year
            month = start_date.month + month_offset
            
            # Adjust year if month overflows
            if month > 12:
                month -= 12
                year += 1
            elif month < 1:
                month += 12
                year -= 1
                
            # Check if payment day exists in this month
            try:
                check_date = datetime(year, month, payment_day)
                if start_date <= check_date <= end_date:
                    return True
            except ValueError:
                # Day is out of range for this month
                pass
        return False
        
    elif item['frequency'] == 'quarterly':
        # Check if the payment day in the quarter falls within the period
        payment_day = item['payment_day']
        
        # Get the quarter start month (1, 4, 7, 10)
        quarter_month = ((item_start.month - 1) // 3) * 3 + 1
        
        # Check each possible quarter payment date
        for quarter_offset in range(-1, 2):  # Check previous, current, and next quarter
            for month_offset in range(3):  # Check each month in the quarter
                year = start_date.year
                month = quarter_month + month_offset + quarter_offset * 3
                
                # Adjust year if month overflows
                while month > 12:
                    month -= 12
                    year += 1
                while month < 1:
                    month += 12
                    year -= 1
                    
                # Check if payment day exists in this month
                try:
                    check_date = datetime(year, month, payment_day)
                    if start_date <= check_date <= end_date:
                        return True
                except ValueError:
                    # Day is out of range for this month
                    pass
        return False
        
    # Default case (should not reach here if data is valid)
    return False

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/expenses')
def expenses_page():
    return render_template('expenses.html')

@app.route('/revenue')
def revenue_page():
    return render_template('revenue.html')

@app.route('/forecast')
def forecast_page():
    return render_template('forecast.html')

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

# API Routes
@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    conn = get_db_connection()
    expenses = conn.execute('SELECT * FROM expenses').fetchall()
    conn.close()
    
    result = []
    for expense in expenses:
        result.append({
            'id': expense['id'],
            'name': expense['name'],
            'amount': expense['amount'],
            'category': expense['category'],
            'isRecurring': bool(expense['is_recurring']),
            'frequency': expense['frequency'],
            'startDate': expense['start_date'],
            'endDate': expense['end_date'],
            'paymentDay': expense['payment_day'],
            'notes': expense['notes']
        })
    
    return jsonify(result)

@app.route('/api/expenses/<string:expense_id>', methods=['GET'])
def get_expense(expense_id):
    conn = get_db_connection()
    expense = conn.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,)).fetchone()
    conn.close()
    
    if expense is None:
        return jsonify({'error': 'Expense not found'}), 404
    
    result = {
        'id': expense['id'],
        'name': expense['name'],
        'amount': expense['amount'],
        'category': expense['category'],
        'isRecurring': bool(expense['is_recurring']),
        'frequency': expense['frequency'],
        'startDate': expense['start_date'],
        'endDate': expense['end_date'],
        'paymentDay': expense['payment_day'],
        'notes': expense['notes']
    }
    
    return jsonify(result)

@app.route('/api/expenses', methods=['POST'])
def create_expense():
    data = request.json
    
    # Generate ID if not provided
    expense_id = data.get('id')
    if not expense_id:
        expense_id = f"exp-{str(uuid.uuid4())[:8]}"
    
    conn = get_db_connection()
    conn.execute('''
    INSERT INTO expenses (id, name, amount, category, is_recurring, frequency, start_date, end_date, payment_day, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        expense_id,
        data['name'],
        data['amount'],
        data['category'],
        data['isRecurring'],
        data['frequency'],
        data['startDate'],
        data.get('endDate'),
        data['paymentDay'],
        data.get('notes', '')
    ))
    conn.commit()
    
    # Get the created expense
    expense = conn.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,)).fetchone()
    conn.close()
    
    result = {
        'id': expense['id'],
        'name': expense['name'],
        'amount': expense['amount'],
        'category': expense['category'],
        'isRecurring': bool(expense['is_recurring']),
        'frequency': expense['frequency'],
        'startDate': expense['start_date'],
        'endDate': expense['end_date'],
        'paymentDay': expense['payment_day'],
        'notes': expense['notes']
    }
    
    return jsonify(result), 201

@app.route('/api/expenses/<string:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    data = request.json
    
    conn = get_db_connection()
    conn.execute('''
    UPDATE expenses
    SET name = ?, amount = ?, category = ?, is_recurring = ?, frequency = ?, 
        start_date = ?, end_date = ?, payment_day = ?, notes = ?
    WHERE id = ?
    ''', (
        data['name'],
        data['amount'],
        data['category'],
        data['isRecurring'],
        data['frequency'],
        data['startDate'],
        data.get('endDate'),
        data['paymentDay'],
        data.get('notes', ''),
        expense_id
    ))
    conn.commit()
    
    # Get the updated expense
    expense = conn.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,)).fetchone()
    conn.close()
    
    if expense is None:
        return jsonify({'error': 'Expense not found'}), 404
    
    result = {
        'id': expense['id'],
        'name': expense['name'],
        'amount': expense['amount'],
        'category': expense['category'],
        'isRecurring': bool(expense['is_recurring']),
        'frequency': expense['frequency'],
        'startDate': expense['start_date'],
        'endDate': expense['end_date'],
        'paymentDay': expense['payment_day'],
        'notes': expense['notes']
    }
    
    return jsonify(result)

@app.route('/api/expenses/<string:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Expense deleted successfully'})

@app.route('/api/revenue', methods=['GET'])
def get_revenue():
    conn = get_db_connection()
    revenue_items = conn.execute('SELECT * FROM revenue').fetchall()
    conn.close()
    
    result = []
    for revenue in revenue_items:
        result.append({
            'id': revenue['id'],
            'source': revenue['source'],
            'amount': revenue['amount'],
            'probability': revenue['probability'],
            'isRecurring': bool(revenue['is_recurring']),
            'frequency': revenue['frequency'],
            'startDate': revenue['start_date'],
            'endDate': revenue['end_date'],
            'paymentDay': revenue['payment_day'],
            'notes': revenue['notes']
        })
    
    return jsonify(result)

@app.route('/api/revenue/<string:revenue_id>', methods=['GET'])
def get_revenue_item(revenue_id):
    conn = get_db_connection()
    revenue = conn.execute('SELECT * FROM revenue WHERE id = ?', (revenue_id,)).fetchone()
    conn.close()
    
    if revenue is None:
        return jsonify({'error': 'Revenue not found'}), 404
    
    result = {
        'id': revenue['id'],
        'source': revenue['source'],
        'amount': revenue['amount'],
        'probability': revenue['probability'],
        'isRecurring': bool(revenue['is_recurring']),
        'frequency': revenue['frequency'],
        'startDate': revenue['start_date'],
        'endDate': revenue['end_date'],
        'paymentDay': revenue['payment_day'],
        'notes': revenue['notes']
    }
    
    return jsonify(result)

@app.route('/api/revenue', methods=['POST'])
def create_revenue():
    data = request.json
    
    # Generate ID if not provided
    revenue_id = data.get('id')
    if not revenue_id:
        revenue_id = f"rev-{str(uuid.uuid4())[:8]}"
    
    conn = get_db_connection()
    conn.execute('''
    INSERT INTO revenue (id, source, amount, probability, is_recurring, frequency, start_date, end_date, payment_day, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        revenue_id,
        data['source'],
        data['amount'],
        data['probability'],
        data['isRecurring'],
        data['frequency'],
        data['startDate'],
        data.get('endDate'),
        data['paymentDay'],
        data.get('notes', '')
    ))
    conn.commit()
    
    # Get the created revenue
    revenue = conn.execute('SELECT * FROM revenue WHERE id = ?', (revenue_id,)).fetchone()
    conn.close()
    
    result = {
        'id': revenue['id'],
        'source': revenue['source'],
        'amount': revenue['amount'],
        'probability': revenue['probability'],
        'isRecurring': bool(revenue['is_recurring']),
        'frequency': revenue['frequency'],
        'startDate': revenue['start_date'],
        'endDate': revenue['end_date'],
        'paymentDay': revenue['payment_day'],
        'notes': revenue['notes']
    }
    
    return jsonify(result), 201

@app.route('/api/revenue/<string:revenue_id>', methods=['PUT'])
def update_revenue(revenue_id):
    data = request.json
    
    conn = get_db_connection()
    conn.execute('''
    UPDATE revenue
    SET source = ?, amount = ?, probability = ?, is_recurring = ?, frequency = ?, 
        start_date = ?, end_date = ?, payment_day = ?, notes = ?
    WHERE id = ?
    ''', (
        data['source'],
        data['amount'],
        data['probability'],
        data['isRecurring'],
        data['frequency'],
        data['startDate'],
        data.get('endDate'),
        data['paymentDay'],
        data.get('notes', ''),
        revenue_id
    ))
    conn.commit()
    
    # Get the updated revenue
    revenue = conn.execute('SELECT * FROM revenue WHERE id = ?', (revenue_id,)).fetchone()
    conn.close()
    
    if revenue is None:
        return jsonify({'error': 'Revenue not found'}), 404
    
    result = {
        'id': revenue['id'],
        'source': revenue['source'],
        'amount': revenue['amount'],
        'probability': revenue['probability'],
        'isRecurring': bool(revenue['is_recurring']),
        'frequency': revenue['frequency'],
        'startDate': revenue['start_date'],
        'endDate': revenue['end_date'],
        'paymentDay': revenue['payment_day'],
        'notes': revenue['notes']
    }
    
    return jsonify(result)

@app.route('/api/revenue/<string:revenue_id>', methods=['DELETE'])
def delete_revenue(revenue_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM revenue WHERE id = ?', (revenue_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Revenue deleted successfully'})

@app.route('/api/settings', methods=['GET'])
def get_settings():
    conn = get_db_connection()
    settings = conn.execute('SELECT * FROM settings').fetchone()
    conn.close()
    
    result = {
        'currency': settings['currency'],
        'dateFormat': settings['date_format'],
        'theme': settings['theme'],
        'lowBalanceThreshold': settings['low_balance_threshold'],
        'defaultForecastWeeks': settings['default_forecast_weeks']
    }
    
    return jsonify(result)

@app.route('/api/settings', methods=['PUT'])
def update_settings():
    data = request.json
    
    conn = get_db_connection()
    conn.execute('''
    UPDATE settings
    SET currency = ?, date_format = ?, theme = ?, low_balance_threshold = ?, default_forecast_weeks = ?
    WHERE id = 1
    ''', (
        data['currency'],
        data['dateFormat'],
        data['theme'],
        data['lowBalanceThreshold'],
        data['defaultForecastWeeks']
    ))
    conn.commit()
    
    # Get the updated settings
    settings = conn.execute('SELECT * FROM settings').fetchone()
    conn.close()
    
    result = {
        'currency': settings['currency'],
        'dateFormat': settings['date_format'],
        'theme': settings['theme'],
        'lowBalanceThreshold': settings['low_balance_threshold'],
        'defaultForecastWeeks': settings['default_forecast_weeks']
    }
    
    return jsonify(result)

@app.route('/api/forecast/calculate', methods=['POST'])
def calculate_forecast():
    data = request.json
    
    # Parse parameters
    start_date = datetime.fromisoformat(data['startDate'].replace('Z', '+00:00')).replace(tzinfo=None)
    num_weeks = data.get('numWeeks', 8)
    initial_balance = data.get('initialBalance', 0.0)
    
    # Generate forecast
    forecast = generate_forecast(start_date, num_weeks, initial_balance)
    
    return jsonify(forecast)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
