from flask import Flask, render_template, request, redirect, url_for, session
import datetime
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# --- INITIALIZATION ---
@app.before_request
def initialize_session():
    if 'journal_entries' not in session:
        session['journal_entries'] = []
    
    default_accounts = [
        {'code': '101', 'name': 'Cash', 'type': 'Asset'},
        {'code': '102', 'name': 'Accounts Receivable', 'type': 'Asset'},
        {'code': '110', 'name': 'Goods (Inventory)', 'type': 'Asset'},
        {'code': '150', 'name': 'Machinery', 'type': 'Asset'},
        {'code': '151', 'name': 'Furniture', 'type': 'Asset'},
        {'code': '201', 'name': 'Accounts Payable', 'type': 'Liability'},
        {'code': '202', 'name': 'Advertisement Payable', 'type': 'Liability'},
        {'code': '301', 'name': 'Owner Capital', 'type': 'Equity'},
        {'code': '302', 'name': 'Owner Drawing', 'type': 'Equity'},
        {'code': '401', 'name': 'Sales Revenue', 'type': 'Revenue'},
        {'code': '402', 'name': 'Sales Return', 'type': 'Revenue'},
        {'code': '501', 'name': 'Rent Expense', 'type': 'Expense'},
        {'code': '502', 'name': 'Salary Expense', 'type': 'Expense'},
        {'code': '510', 'name': 'Purchases', 'type': 'Expense'},
        {'code': '511', 'name': 'Purchase Return', 'type': 'Expense'},
        {'code': '520', 'name': 'Bank Charges', 'type': 'Expense'}
    ]

    if 'chart_of_accounts' not in session:
        session['chart_of_accounts'] = default_accounts
    else:
        # Merge logic to ensure new defaults appear
        existing_codes = [acc['code'] for acc in session['chart_of_accounts']]
        updates_made = False
        for account in default_accounts:
            if account['code'] not in existing_codes:
                session['chart_of_accounts'].append(account)
                updates_made = True
        
        if updates_made:
            session['chart_of_accounts'].sort(key=lambda x: x['code'])
            session.modified = True

@app.context_processor
def inject_accounts():
    return dict(accounts=session.get('chart_of_accounts', []))

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = request.args.get('message') # Get success message if it exists
    new_user_id = request.args.get('user_id') # Get generated ID if it exists

    if request.method == 'POST':
        # In a real app, you would verify credentials here.
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple check (You can expand this logic)
        if username and password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid Credentials")

    return render_template('login.html', message=message, new_user_id=new_user_id)

# --- REGISTER ROUTE WITH ID GENERATION ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Generate a simple User ID (First Name + 4 Random Digits)
        # Example: John Doe -> JOHN4821
        first_name = name.split()[0].upper() if name else "USER"
        random_digits = str(random.randint(1000, 9999))
        generated_user_id = f"{first_name}{random_digits}"
        
        # Here, we pass it to the login page to show the user.
        success_msg = f"Account Created! Your User ID is: {generated_user_id}"
        
        return redirect(url_for('login', message=success_msg, user_id=generated_user_id))
        
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/chart_of_accounts', methods=['GET', 'POST'])
def chart_of_accounts():
    if request.method == 'POST':
        # Manual Add Account Logic
        new_account = {
            'code': request.form.get('code'),
            'name': request.form.get('name'),
            'type': request.form.get('type')
        }
        existing_codes = [acc['code'] for acc in session['chart_of_accounts']]
        if new_account['code'] not in existing_codes:
            session['chart_of_accounts'].append(new_account)
            session['chart_of_accounts'].sort(key=lambda x: x['code'])
            session.modified = True
    
    # --- CALCULATE BALANCES FOR COA DISPLAY ---
    accounts = session.get('chart_of_accounts', [])
    journals = session.get('journal_entries', [])
    
    # Initialize dictionary with 0.0 for all accounts
    balances = {acc['name']: 0.0 for acc in accounts}
    
    for entry in journals:
        name = entry['account_name']
        debit = entry.get('debit', 0.0)
        credit = entry.get('credit', 0.0)
        
        # Find account type to apply Normal Balance rule
        acct_type = next((a['type'] for a in accounts if a['name'] == name), 'Expense') 
        
        if name in balances:
            if acct_type in ['Asset', 'Expense']:
                balances[name] += (debit - credit)
            else:
                balances[name] += (credit - debit)
        else:
            # Fallback for old/missing accounts - treat as Expense for calculation purposes
            balances[name] = (debit - credit) if acct_type in ['Asset', 'Expense'] else (credit - debit)

    return render_template('chart_of_accounts.html', accounts=accounts, balances=balances)

@app.route('/journal_entry/<username>', methods=['GET', 'POST'])
def journal_entry(username):
    if request.method == 'POST':
        dates = request.form.getlist('date[]')
        names = request.form.getlist('account_name[]') 
        particulars = request.form.getlist('particular[]')
        debits = request.form.getlist('debit[]')
        credits = request.form.getlist('credit[]')
        is_adjusting = 'is_adjusting' in request.form
        transaction_id = len(session['journal_entries']) 

        # --- AUTO-CREATE NEW ACCOUNTS LOGIC ---
        # Create a set of existing names (lowercase) for easy checking
        existing_account_names = {acc['name'].lower() for acc in session['chart_of_accounts']}
        accounts_updated = False

        for i in range(len(names)):
            original_name = names[i].strip()
            lower_name = original_name.lower()
            
            # If account does not exist in our list, create it
            if original_name and lower_name not in existing_account_names:
                
                debit_val = float(debits[i]) if debits[i] else 0.0
                
                # --- TYPE INFERENCE LOGIC ---
                # If user entered a Debit amount > 0 -> Assume 'Expense'
                # Otherwise, assume 'Revenue'
                inferred_type = 'Expense' if debit_val > 0 else 'Revenue'
                
                # Generate a random code (e.g., AUTO-9281)
                new_code = f"AUTO-{random.randint(1000, 9999)}"
                
                new_account = {
                    'code': new_code, 
                    'name': original_name, 
                    'type': inferred_type
                }
                
                # Add to Chart of Accounts
                session['chart_of_accounts'].append(new_account)
                
                # Update our local check set so we don't add it twice in the same transaction
                existing_account_names.add(lower_name) 
                accounts_updated = True
        
        if accounts_updated:
            # Sort again by code so they appear neatly
            session['chart_of_accounts'].sort(key=lambda x: x['code'])
            session.modified = True

        # --- SAVE JOURNAL ENTRIES ---
        for i in range(len(dates)):
            new_entry = {
                'id': transaction_id, 
                'date': dates[i],
                'account_name': names[i],
                'particular': particulars[i],
                'debit': float(debits[i]) if debits[i] else 0.0,
                'credit': float(credits[i]) if credits[i] else 0.0,
                'type': 'Adjusting' if is_adjusting else 'Standard'
            }
            session['journal_entries'].append(new_entry)
        
        session.modified = True
        return redirect(url_for('view_journal', username=username))
    return render_template('journal_entry.html', username=username)

@app.route('/view_journal/<username>')
def view_journal(username):
    return render_template('view_journal.html', username=username, entries=session['journal_entries'])

@app.route('/edit_journal/<int:id>', methods=['GET', 'POST'])
def edit_journal(id):
    if 'journal_entries' in session and 0 <= id < len(session['journal_entries']):
        if request.method == 'POST':
            entry = session['journal_entries'][id]
            entry['date'] = request.form.get('date')
            entry['account_name'] = request.form.get('account_name')
            entry['particular'] = request.form.get('particular')
            entry['debit'] = float(request.form.get('debit') or 0.0)
            entry['credit'] = float(request.form.get('credit') or 0.0)
            entry['type'] = 'Adjusting' if 'is_adjusting' in request.form else 'Standard'
            session.modified = True
            return redirect(url_for('view_journal', username=session.get('username')))
        return render_template('edit_journal.html', entry=session['journal_entries'][id], id=id)
    return redirect(url_for('view_journal', username=session.get('username', 'admin')))

@app.route('/delete_journal/<int:index>', methods=['POST'])
def delete_journal(index):
    if 0 <= index < len(session['journal_entries']):
        session['journal_entries'].pop(index)
        session.modified = True
    return redirect(url_for('view_journal', username=session.get('username')))

def generate_financials():
    journals = session.get('journal_entries', [])
    accounts = session.get('chart_of_accounts', [])
    ledger = {acc['name']: {'type': acc['type'], 'balance': 0.0, 'debit_total': 0.0, 'credit_total': 0.0} for acc in accounts}
    
    for entry in journals:
        acct_name = entry['account_name']
        debit = entry['debit']
        credit = entry['credit']
        
        if acct_name not in ledger:
             # Handle dynamically added accounts that might not have been re-fetched into the function's scope
             ledger[acct_name] = {'type': 'Expense', 'balance': 0.0, 'debit_total': 0.0, 'credit_total': 0.0}

        if acct_name in ledger:
            ledger[acct_name]['debit_total'] += debit
            ledger[acct_name]['credit_total'] += credit
            acct_type = ledger[acct_name]['type']
            if acct_type in ['Asset', 'Expense']:
                ledger[acct_name]['balance'] += (debit - credit)
            else:
                ledger[acct_name]['balance'] += (credit - debit)

    revenue = sum(data['balance'] for data in ledger.values() if data['type'] == 'Revenue')
    expenses = sum(data['balance'] for data in ledger.values() if data['type'] == 'Expense')
    net_income = revenue - expenses
    assets = sum(data['balance'] for data in ledger.values() if data['type'] == 'Asset')
    liabilities = sum(data['balance'] for data in ledger.values() if data['type'] == 'Liability')
    equity = sum(data['balance'] for data in ledger.values() if data['type'] == 'Equity')
    total_equity_liab = liabilities + equity + net_income
    is_balanced = abs(assets - total_equity_liab) < 0.01

    return {
        'ledger': ledger,
        'income_statement': {'revenue': revenue, 'expenses': expenses, 'net_income': net_income},
        'balance_sheet': {'assets': assets, 'liabilities': liabilities, 'equity': equity, 'total_eq_liab': total_equity_liab, 'is_balanced': is_balanced}
    }

@app.route('/financial_reports')
def financial_reports():
    data = generate_financials()
    return render_template('financial_reports.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)