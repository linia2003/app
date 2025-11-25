from flask import Flask, render_template, request, redirect, url_for, session
import datetime
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# --- SYSTEM LIBRARY (Kept in code, but not loaded by default) ---
SYSTEM_DEFAULT_ACCOUNTS = [
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

# --- INITIALIZATION ---
@app.before_request
def initialize_session():
    if 'journal_entries' not in session:
        session['journal_entries'] = []
    
    # START EMPTY: Only show accounts the user actually adds or uses
    if 'chart_of_accounts' not in session:
        session['chart_of_accounts'] = []

# --- HELPER: ACTIVATES AN ACCOUNT IF USED ---
def activate_account(account_name):
    """
    Checks if account is in user's list. If not:
    1. Checks System Defaults (to get correct code/type).
    2. Or creates a new generic one.
    3. Adds to user's list.
    """
    current_accounts = session.get('chart_of_accounts', [])
    
    # 1. Check if already active
    if any(acc['name'].lower() == account_name.lower() for acc in current_accounts):
        return

    # 2. Check System Defaults
    found_default = next((acc for acc in SYSTEM_DEFAULT_ACCOUNTS if acc['name'].lower() == account_name.lower()), None)
    
    if found_default:
        # Copy from system defaults
        current_accounts.append(found_default)
    else:
        # Create new custom account
        if account_name.strip():
            new_acc = {'code': '000', 'name': account_name, 'type': 'General'}
            current_accounts.append(new_acc)
    
    # Save and Sort
    current_accounts.sort(key=lambda x: x['code'])
    session['chart_of_accounts'] = current_accounts
    session.modified = True

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = request.args.get('message')
    new_user_id = request.args.get('user_id')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username and password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid Credentials")

    return render_template('login.html', message=message, new_user_id=new_user_id)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        first_name = name.split()[0].upper() if name else "USER"
        random_digits = str(random.randint(1000, 9999))
        generated_user_id = f"{first_name}{random_digits}"
        success_msg = f"Account Created! Your User ID is: {generated_user_id}"
        return redirect(url_for('login', message=success_msg, user_id=generated_user_id))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/chart_of_accounts', methods=['GET', 'POST'])
def chart_of_accounts():
    # 1. Manual Add
    if request.method == 'POST':
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

    # 2. Calculate Balances (ONLY for active accounts)
    accounts = session.get('chart_of_accounts', [])
    entries = session.get('journal_entries', [])
    
    balances = {acc['name']: 0.0 for acc in accounts}

    for entry in entries:
        name = entry['account_name']
        debit = float(entry.get('debit', 0.0))
        credit = float(entry.get('credit', 0.0))
        
        if name in balances:
            acc_type = next((a['type'] for a in accounts if a['name'] == name), 'Asset')
            if acc_type in ['Asset', 'Expense']:
                balances[name] += (debit - credit)
            else:
                balances[name] += (credit - debit)

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

        for i in range(len(dates)):
            # Activate the account so it shows up in Chart of Accounts
            activate_account(names[i])

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
    
    # Prepare Dropdown Options: Merge Active + System Defaults (removing duplicates)
    active_accounts = session.get('chart_of_accounts', [])
    # Create a dictionary to deduplicate by name
    merged_dict = {acc['name']: acc for acc in SYSTEM_DEFAULT_ACCOUNTS} 
    merged_dict.update({acc['name']: acc for acc in active_accounts}) # Active overrides default
    
    # Sort for the dropdown
    all_options = sorted(merged_dict.values(), key=lambda x: x['code'])

    return render_template('journal_entry.html', username=username, accounts=all_options)

@app.route('/view_journal/<username>')
def view_journal(username):
    entries = session.get('journal_entries', [])
    accounts = session.get('chart_of_accounts', [])
    
    summary = {acc['name']: {'type': acc['type'], 'debit': 0.0, 'credit': 0.0, 'balance': 0.0} for acc in accounts}
    
    for entry in entries:
        name = entry['account_name']
        debit = entry.get('debit', 0.0)
        credit = entry.get('credit', 0.0)
        
        if name in summary:
            summary[name]['debit'] += debit
            summary[name]['credit'] += credit
            
            acct_type = summary[name]['type']
            if acct_type in ['Asset', 'Expense']:
                summary[name]['balance'] += (debit - credit)
            else:
                summary[name]['balance'] += (credit - debit)
                
    return render_template('view_journal.html', username=username, entries=entries, summary=summary)

@app.route('/edit_journal/<int:id>', methods=['GET', 'POST'])
def edit_journal(id):
    journal_list = session.get('journal_entries', [])
    target_index = -1
    for i, entry in enumerate(journal_list):
        if entry.get('id') == id:
            target_index = i
            break
            
    if target_index != -1:
        if request.method == 'POST':
            entry = session['journal_entries'][target_index]
            entry['date'] = request.form.get('date')
            
            # Ensure account stays active/valid
            acc_name = request.form.get('account_name')
            activate_account(acc_name)
            
            entry['account_name'] = acc_name
            entry['particular'] = request.form.get('particular')
            entry['debit'] = float(request.form.get('debit') or 0.0)
            entry['credit'] = float(request.form.get('credit') or 0.0)
            entry['type'] = 'Adjusting' if 'is_adjusting' in request.form else 'Standard'
            session.modified = True
            return redirect(url_for('view_journal', username=session.get('username')))
        return render_template('edit_journal.html', entry=session['journal_entries'][target_index])
    
    return redirect(url_for('view_journal', username=session.get('username')))

@app.route('/delete_journal/<int:index>', methods=['POST'])
def delete_journal(index):
    journal_list = session.get('journal_entries', [])
    target_index = -1
    for i, entry in enumerate(journal_list):
        if entry.get('id') == index:
            target_index = i
            break
            
    if target_index != -1:
        session['journal_entries'].pop(target_index)
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