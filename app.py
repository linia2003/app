from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import datetime
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# --- SYSTEM LIBRARY (Updated - Closing Stock Removed) ---
SYSTEM_DEFAULT_ACCOUNTS = [
    {'code': '101', 'name': 'Cash', 'type': 'Asset'},
    {'code': '102', 'name': 'Accounts Receivable', 'type': 'Asset'},
    {'code': '110', 'name': 'Inventory', 'type': 'Asset'}, # Updated name for clarity (was Goods)
    {'code': '150', 'name': 'Computer Equipment', 'type': 'Asset'}, # New
    {'code': '151', 'name': 'Furniture', 'type': 'Asset'},
    {'code': '152', 'name': 'Software Asset', 'type': 'Asset'}, # New
    {'code': '153', 'name': 'Office Equipment', 'type': 'Asset'}, # New
    {'code': '160', 'name': 'Prepaid Rent', 'type': 'Asset'}, # New
    {'code': '161', 'name': 'Prepaid Insurance', 'type': 'Asset'}, # New
    {'code': '180', 'name': 'Office Supplies', 'type': 'Asset'}, # New
    {'code': '190', 'name': 'Bank', 'type': 'Asset'}, # Added Bank

    {'code': '201', 'name': 'Accounts Payable', 'type': 'Liability'}, 
    {'code': '202', 'name': 'Creditors', 'type': 'Liability'}, # Used for various payables in PDF
    {'code': '210', 'name': 'Bank Loan', 'type': 'Liability'}, # New
    {'code': '220', 'name': 'Interest Payable', 'type': 'Liability'}, # New
    {'code': '230', 'name': 'Unearned Revenue', 'type': 'Liability'}, # New
    {'code': '240', 'name': 'Salary Payable', 'type': 'Liability'}, # New

    {'code': '301', 'name': 'Capital', 'type': 'Equity'}, # Renamed from Owner Capital
    {'code': '302', 'name': 'Drawings', 'type': 'Equity'}, # Renamed from Owner Drawing
    {'code': '350', 'name': 'Accumulated Depreciation', 'type': 'Asset'}, # Contra-Asset for Accum Dep
    
    {'code': '401', 'name': 'Service Revenue', 'type': 'Revenue'}, # New
    {'code': '402', 'name': 'Sales', 'type': 'Revenue'},
    {'code': '410', 'name': 'Interest Income', 'type': 'Revenue'}, # New
    # Closing Stock removed
    
    {'code': '501', 'name': 'Rent Expense', 'type': 'Expense'},
    {'code': '502', 'name': 'Salary Expense', 'type': 'Expense'},
    {'code': '503', 'name': 'COGS', 'type': 'Expense'}, # New
    {'code': '504', 'name': 'Loss on Sale', 'type': 'Expense'}, # Treated as expense in IS
    {'code': '510', 'name': 'Internet Expense', 'type': 'Expense'}, # New
    {'code': '511', 'name': 'Electricity Expense', 'type': 'Expense'}, # New
    {'code': '512', 'name': 'Advertising Expense', 'type': 'Expense'}, # New
    {'code': '513', 'name': 'Staff Welfare', 'type': 'Expense'}, # New
    {'code': '514', 'name': 'Bank Charges Expense', 'type': 'Expense'}, # New
    {'code': '515', 'name': 'Telephone Expense', 'type': 'Expense'}, # New
    {'code': '516', 'name': 'Interest Expense', 'type': 'Expense'}, # New
    {'code': '517', 'name': 'Cleaning Expense', 'type': 'Expense'}, # New
    {'code': '518', 'name': 'Repair Expense', 'type': 'Expense'}, # New
    {'code': '519', 'name': 'Depreciation Expense', 'type': 'Expense'}, # New
    {'code': '520', 'name': 'Bad Debt Expense', 'type': 'Expense'}, # New
    {'code': '521', 'name': 'Office Supplies Expense', 'type': 'Expense'}, # New
    {'code': '522', 'name': 'Stationery Expense', 'type': 'Expense'} # New
]

# --- PDF JOURNAL ENTRIES (Consolidated for a clean, balanced ledger) ---
PDF_JOURNAL_ENTRIES = [
    # Initial Capital and Cash
    {'id': 0, 'date': '2025-01-01', 'account_name': 'Cash', 'particular': 'Capital Introduction', 'debit': 600000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 0, 'date': '2025-01-01', 'account_name': 'Capital', 'particular': 'Capital Introduction', 'debit': 0.0, 'credit': 600000.0, 'type': 'Standard'},
    
    # Office Equipment (Initial Debit to balance sale in Entry 12)
    {'id': -1, 'date': '2025-01-01', 'account_name': 'Office Equipment', 'particular': 'Initial Balance', 'debit': 10000.0, 'credit': 0.0, 'type': 'Standard'},
    
    # Operations continued...
    {'id': 1, 'date': '2025-01-02', 'account_name': 'Bank', 'particular': 'Cash Deposit', 'debit': 250000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 1, 'date': '2025-01-02', 'account_name': 'Cash', 'particular': 'Cash Deposit', 'debit': 0.0, 'credit': 250000.0, 'type': 'Standard'},
    {'id': 2, 'date': '2025-01-03', 'account_name': 'Computer Equipment', 'particular': 'Purchase of asset', 'debit': 120000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 2, 'date': '2025-01-03', 'account_name': 'Cash', 'particular': 'Purchase of asset', 'debit': 0.0, 'credit': 120000.0, 'type': 'Standard'},
    {'id': 3, 'date': '2025-01-04', 'account_name': 'Prepaid Rent', 'particular': 'Advance payment for 3 months', 'debit': 90000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 3, 'date': '2025-01-04', 'account_name': 'Cash', 'particular': 'Advance payment for 3 months', 'debit': 0.0, 'credit': 90000.0, 'type': 'Standard'},
    {'id': 4, 'date': '2025-01-05', 'account_name': 'Office Supplies', 'particular': 'Credit purchase of supplies', 'debit': 25000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 4, 'date': '2025-01-05', 'account_name': 'Creditors', 'particular': 'Credit purchase of supplies', 'debit': 0.0, 'credit': 25000.0, 'type': 'Standard'},
    {'id': 5, 'date': '2025-01-06', 'account_name': 'Cash', 'particular': 'Service fees received', 'debit': 85000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 5, 'date': '2025-01-06', 'account_name': 'Service Revenue', 'particular': 'Service fees received', 'debit': 0.0, 'credit': 85000.0, 'type': 'Standard'},
    {'id': 6, 'date': '2025-01-06', 'account_name': 'Accounts Receivable', 'particular': 'Service on credit', 'debit': 65000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 6, 'date': '2025-01-06', 'account_name': 'Service Revenue', 'particular': 'Service on credit', 'debit': 0.0, 'credit': 65000.0, 'type': 'Standard'},
    {'id': 7, 'date': '2025-01-07', 'account_name': 'Salary Expense', 'particular': 'Paid staff wages', 'debit': 55000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 7, 'date': '2025-01-07', 'account_name': 'Cash', 'particular': 'Paid staff wages', 'debit': 0.0, 'credit': 55000.0, 'type': 'Standard'},
    {'id': 8, 'date': '2025-01-08', 'account_name': 'Software Asset', 'particular': 'Credit purchase of license', 'debit': 70000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 8, 'date': '2025-01-08', 'account_name': 'Creditors', 'particular': 'Credit purchase of license', 'debit': 0.0, 'credit': 70000.0, 'type': 'Standard'},
    {'id': 9, 'date': '2025-01-09', 'account_name': 'Internet Expense', 'particular': 'Paid monthly bill', 'debit': 4000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 9, 'date': '2025-01-09', 'account_name': 'Cash', 'particular': 'Paid monthly bill', 'debit': 0.0, 'credit': 4000.0, 'type': 'Standard'},
    {'id': 10, 'date': '2025-01-10', 'account_name': 'Furniture', 'particular': 'Credit purchase of office chairs', 'debit': 30000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 10, 'date': '2025-01-10', 'account_name': 'Creditors', 'particular': 'Credit purchase of office chairs', 'debit': 0.0, 'credit': 30000.0, 'type': 'Standard'},
    {'id': 11, 'date': '2025-01-11', 'account_name': 'Cash', 'particular': 'Sold office equipment at loss', 'debit': 8000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 11, 'date': '2025-01-11', 'account_name': 'Loss on Sale', 'particular': 'Sold office equipment at loss', 'debit': 2000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 11, 'date': '2025-01-11', 'account_name': 'Office Equipment', 'particular': 'Sold office equipment at loss', 'debit': 0.0, 'credit': 10000.0, 'type': 'Standard'},
    {'id': 12, 'date': '2025-01-12', 'account_name': 'Cash', 'particular': 'Collection from customer', 'debit': 30000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 12, 'date': '2025-01-12', 'account_name': 'Accounts Receivable', 'particular': 'Collection from customer', 'debit': 0.0, 'credit': 30000.0, 'type': 'Standard'},
    {'id': 13, 'date': '2025-01-13', 'account_name': 'Electricity Expense', 'particular': 'Paid monthly bill', 'debit': 6500.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 13, 'date': '2025-01-13', 'account_name': 'Cash', 'particular': 'Paid monthly bill', 'debit': 0.0, 'credit': 6500.0, 'type': 'Standard'},
    {'id': 14, 'date': '2025-01-14', 'account_name': 'Advertising Expense', 'particular': 'Credit advertising service', 'debit': 18000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 14, 'date': '2025-01-14', 'account_name': 'Creditors', 'particular': 'Credit advertising service', 'debit': 0.0, 'credit': 18000.0, 'type': 'Standard'},
    {'id': 15, 'date': '2025-01-15', 'account_name': 'Staff Welfare', 'particular': 'Paid for staff amenities', 'debit': 2800.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 15, 'date': '2025-01-15', 'account_name': 'Cash', 'particular': 'Paid for staff amenities', 'debit': 0.0, 'credit': 2800.0, 'type': 'Standard'},
    {'id': 16, 'date': '2025-01-16', 'account_name': 'Bank Charges Expense', 'particular': 'Monthly service fees', 'debit': 900.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 16, 'date': '2025-01-16', 'account_name': 'Bank', 'particular': 'Monthly service fees', 'debit': 0.0, 'credit': 900.0, 'type': 'Standard'},
    {'id': 17, 'date': '2025-01-17', 'account_name': 'Bank', 'particular': 'Service fees deposited', 'debit': 110000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 17, 'date': '2025-01-17', 'account_name': 'Service Revenue', 'particular': 'Service fees deposited', 'debit': 0.0, 'credit': 110000.0, 'type': 'Standard'},
    {'id': 18, 'date': '2025-01-18', 'account_name': 'Creditors', 'particular': 'Payment to supplier', 'debit': 40000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 18, 'date': '2025-01-18', 'account_name': 'Cash', 'particular': 'Payment to supplier', 'debit': 0.0, 'credit': 40000.0, 'type': 'Standard'},
    {'id': 19, 'date': '2025-01-19', 'account_name': 'Cash', 'particular': 'Received advance payment', 'debit': 50000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 19, 'date': '2025-01-19', 'account_name': 'Unearned Revenue', 'particular': 'Received advance payment', 'debit': 0.0, 'credit': 50000.0, 'type': 'Standard'},
    {'id': 20, 'date': '2025-01-20', 'account_name': 'Inventory', 'particular': 'Purchased goods for resale (Cash)', 'debit': 45000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 20, 'date': '2025-01-20', 'account_name': 'Cash', 'particular': 'Purchased goods for resale (Cash)', 'debit': 0.0, 'credit': 45000.0, 'type': 'Standard'},
    {'id': 21, 'date': '2025-01-21', 'account_name': 'Cash', 'particular': 'Sale of goods (Cash)', 'debit': 18000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 21, 'date': '2025-01-21', 'account_name': 'Sales', 'particular': 'Sale of goods (Cash)', 'debit': 0.0, 'credit': 18000.0, 'type': 'Standard'},
    {'id': 22, 'date': '2025-01-21', 'account_name': 'COGS', 'particular': 'Cost of goods sold', 'debit': 10000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 22, 'date': '2025-01-21', 'account_name': 'Inventory', 'particular': 'Cost of goods sold', 'debit': 0.0, 'credit': 10000.0, 'type': 'Standard'},
    {'id': 23, 'date': '2025-01-22', 'account_name': 'Telephone Expense', 'particular': 'Paid monthly bill', 'debit': 1500.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 23, 'date': '2025-01-22', 'account_name': 'Cash', 'particular': 'Paid monthly bill', 'debit': 0.0, 'credit': 1500.0, 'type': 'Standard'},
    {'id': 24, 'date': '2025-01-22', 'account_name': 'Rent Expense', 'particular': 'Paid monthly rent', 'debit': 15000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 24, 'date': '2025-01-22', 'account_name': 'Bank', 'particular': 'Paid monthly rent', 'debit': 0.0, 'credit': 15000.0, 'type': 'Standard'},
    {'id': 25, 'date': '2025-01-23', 'account_name': 'Bank', 'particular': 'Received bank loan', 'debit': 200000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 25, 'date': '2025-01-23', 'account_name': 'Bank Loan', 'particular': 'Received bank loan', 'debit': 0.0, 'credit': 200000.0, 'type': 'Standard'},
    {'id': 26, 'date': '2025-01-24', 'account_name': 'Interest Expense', 'particular': 'Accrued interest', 'debit': 5000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 26, 'date': '2025-01-24', 'account_name': 'Interest Payable', 'particular': 'Accrued interest', 'debit': 0.0, 'credit': 5000.0, 'type': 'Standard'},
    {'id': 27, 'date': '2025-01-25', 'account_name': 'Cleaning Expense', 'particular': 'Paid cleaning services', 'debit': 3200.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 27, 'date': '2025-01-25', 'account_name': 'Cash', 'particular': 'Paid cleaning services', 'debit': 0.0, 'credit': 3200.0, 'type': 'Standard'},
    {'id': 28, 'date': '2025-01-26', 'account_name': 'Repair Expense', 'particular': 'Paid for small repairs', 'debit': 7000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 28, 'date': '2025-01-26', 'account_name': 'Cash', 'particular': 'Paid for small repairs', 'debit': 0.0, 'credit': 7000.0, 'type': 'Standard'},
    {'id': 29, 'date': '2025-01-26', 'account_name': 'Creditors', 'particular': 'Payment to supplier', 'debit': 25000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 29, 'date': '2025-01-26', 'account_name': 'Cash', 'particular': 'Payment to supplier', 'debit': 0.0, 'credit': 25000.0, 'type': 'Standard'},
    {'id': 30, 'date': '2025-01-27', 'account_name': 'Drawings', 'particular': 'Owner withdrawal', 'debit': 20000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 30, 'date': '2025-01-27', 'account_name': 'Cash', 'particular': 'Owner withdrawal', 'debit': 0.0, 'credit': 20000.0, 'type': 'Standard'},
    {'id': 33, 'date': '2025-01-29', 'account_name': 'Bad Debt Expense', 'particular': 'Write off uncollectible debt', 'debit': 5000.0, 'credit': 0.0, 'type': 'Adjusting'},
    {'id': 33, 'date': '2025-01-29', 'account_name': 'Accounts Receivable', 'particular': 'Write off uncollectible debt', 'debit': 0.0, 'credit': 5000.0, 'type': 'Adjusting'},
    {'id': 34, 'date': '2025-01-29', 'account_name': 'Unearned Revenue', 'particular': 'Recognized service revenue', 'debit': 25000.0, 'credit': 0.0, 'type': 'Adjusting'},
    {'id': 34, 'date': '2025-01-29', 'account_name': 'Service Revenue', 'particular': 'Recognized service revenue', 'debit': 0.0, 'credit': 25000.0, 'type': 'Adjusting'},
    {'id': 35, 'date': '2025-01-30', 'account_name': 'Salary Expense', 'particular': 'Accrued salaries for period', 'debit': 20000.0, 'credit': 0.0, 'type': 'Adjusting'},
    {'id': 35, 'date': '2025-01-30', 'account_name': 'Salary Payable', 'particular': 'Accrued salaries for period', 'debit': 0.0, 'credit': 20000.0, 'type': 'Adjusting'},
    {'id': 36, 'date': '2025-01-30', 'account_name': 'Office Supplies Expense', 'particular': 'Supplies consumed', 'debit': 8000.0, 'credit': 0.0, 'type': 'Adjusting'},
    {'id': 36, 'date': '2025-01-30', 'account_name': 'Office Supplies', 'particular': 'Supplies consumed', 'debit': 0.0, 'credit': 8000.0, 'type': 'Adjusting'},
    {'id': 37, 'date': '2025-01-31', 'account_name': 'Prepaid Insurance', 'particular': 'Paid 1 year premium', 'debit': 60000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 37, 'date': '2025-01-31', 'account_name': 'Cash', 'particular': 'Paid 1 year premium', 'debit': 0.0, 'credit': 60000.0, 'type': 'Standard'},
    {'id': 38, 'date': '2025-01-31', 'account_name': 'Accounts Receivable', 'particular': 'Service on credit', 'debit': 95000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 38, 'date': '2025-01-31', 'account_name': 'Service Revenue', 'particular': 'Service on credit', 'debit': 0.0, 'credit': 95000.0, 'type': 'Standard'},
    {'id': 39, 'date': '2025-01-31', 'account_name': 'Electricity Expense', 'particular': 'Paid final bill', 'debit': 7200.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 39, 'date': '2025-01-31', 'account_name': 'Cash', 'particular': 'Paid final bill', 'debit': 0.0, 'credit': 7200.0, 'type': 'Standard'},
    {'id': 40, 'date': '2025-01-31', 'account_name': 'Interest Payable', 'particular': 'Paid accrued interest', 'debit': 5000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 40, 'date': '2025-01-31', 'account_name': 'Cash', 'particular': 'Paid accrued interest', 'debit': 0.0, 'credit': 5000.0, 'type': 'Standard'},
    {'id': 41, 'date': '2025-01-31', 'account_name': 'Salary Payable', 'particular': 'Paid accrued salary', 'debit': 20000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 41, 'date': '2025-01-31', 'account_name': 'Cash', 'particular': 'Paid accrued salary', 'debit': 0.0, 'credit': 20000.0, 'type': 'Standard'},
    {'id': 42, 'date': '2025-01-31', 'account_name': 'Cash', 'particular': 'Collection from customer', 'debit': 60000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 42, 'date': '2025-01-31', 'account_name': 'Accounts Receivable', 'particular': 'Collection from customer', 'debit': 0.0, 'credit': 60000.0, 'type': 'Standard'},
    {'id': 43, 'date': '2025-01-31', 'account_name': 'Bank', 'particular': 'Interest received on deposit', 'debit': 2500.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 43, 'date': '2025-01-31', 'account_name': 'Interest Income', 'particular': 'Interest received on deposit', 'debit': 0.0, 'credit': 2500.0, 'type': 'Standard'},
    {'id': 44, 'date': '2025-01-31', 'account_name': 'Stationery Expense', 'particular': 'Paid for stationery', 'debit': 3600.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 44, 'date': '2025-01-31', 'account_name': 'Cash', 'particular': 'Paid for stationery', 'debit': 0.0, 'credit': 3600.0, 'type': 'Standard'},
    
    # Entry 46: Consolidated Depreciation Adjustment
    {'id': 46, 'date': '2025-01-31', 'account_name': 'Depreciation Expense', 'particular': 'Consolidated Depreciation Adjustment', 'debit': 14000.0, 'credit': 0.0, 'type': 'Adjusting'},
    {'id': 46, 'date': '2025-01-31', 'account_name': 'Accumulated Depreciation', 'particular': 'Consolidated Depreciation Adjustment', 'debit': 0.0, 'credit': 14000.0, 'type': 'Adjusting'},
    
    # Entry 47: Drawings reversal/adjustment
    {'id': 47, 'date': '2025-01-31', 'account_name': 'Cash', 'particular': 'Owner Deposit (Drawings reversal)', 'debit': 20000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 47, 'date': '2025-01-31', 'account_name': 'Drawings', 'particular': 'Owner Deposit (Drawings reversal)', 'debit': 0.0, 'credit': 20000.0, 'type': 'Standard'},
]

# --- INITIALIZATION (Modified to load PDF data) ---
@app.before_request
def initialize_session():
    # Only initialize if it's a fresh session (or cleared)
    if 'journal_entries' not in session or not session['journal_entries']:
        
        # Combine all entries directly. Note: Initial entry (-1) is implicitly handled below.
        # FIX: The entry ID -1 is already included in the PDF_JOURNAL_ENTRIES list above
        # for clean insertion into the master session list.
        
        session['journal_entries'] = PDF_JOURNAL_ENTRIES
        
    if 'chart_of_accounts' not in session or not session['chart_of_accounts']:
        # Filter out Closing Stock from SYSTEM_DEFAULT_ACCOUNTS here
        filtered_accounts = [
            acc for acc in SYSTEM_DEFAULT_ACCOUNTS 
            if acc.get('name') != 'Closing Stock'
        ]
        filtered_accounts.sort(key=lambda x: x['code'])
        session['chart_of_accounts'] = filtered_accounts

    session.modified = True
    # Ensure username is set for dashboard access if testing directly
    if 'username' not in session:
        session['username'] = 'ACCOUNTORIA'

# --- HELPER: ACTIVATES AND CREATES ACCOUNT IF NOT FOUND ---
def activate_account(account_name):
    """
    Checks if account is in user's active list or system defaults. 
    If not found, it creates a new generic "Custom" account and adds it to the user's list.
    """
    current_accounts = session.get('chart_of_accounts', [])
    
    # Check if already active
    if any(acc['name'].lower() == account_name.lower() for acc in current_accounts):
        return

    # Check System Defaults (to avoid re-creating a default with code '000')
    found_default = next((acc for acc in SYSTEM_DEFAULT_ACCOUNTS if acc['name'].lower() == account_name.lower()), None)
    
    if found_default:
        # If it's a system default but not in the user's active list, add it.
        # Ensure 'Closing Stock' isn't added even if it appears in old session data
        if found_default.get('name') != 'Closing Stock':
             current_accounts.append(found_default)
    else:
        # Create new custom account only if the name is non-empty and not just a space
        if account_name.strip():
            # Check for existing custom account with the same name (case-insensitive) before creating a new one
            if not any(acc['name'].lower() == account_name.lower() for acc in current_accounts):
                # Simple code '000' for custom accounts
                new_acc = {'code': '000', 'name': account_name, 'type': 'Custom'}
                current_accounts.append(new_acc)
    
    # Save and Sort (sorting by code ensures consistency)
    current_accounts.sort(key=lambda x: x['code'])
    session['chart_of_accounts'] = current_accounts
    session.modified = True
    
# NEW HELPER: For preparing dropdown data
def get_all_dropdown_accounts():
    active_accounts = session.get('chart_of_accounts', [])
    
    # Filter out Closing Stock before merging for dropdown
    filtered_system_accounts = [
        acc for acc in SYSTEM_DEFAULT_ACCOUNTS 
        if acc.get('name') != 'Closing Stock'
    ]
    
    merged_dict = {acc['name']: acc for acc in filtered_system_accounts} 
    merged_dict.update({acc['name']: acc for acc in active_accounts}) 
    return sorted(merged_dict.values(), key=lambda x: x['code'])

# --- NEW ROUTE FOR ACCOUNT CREATION (Called by JavaScript) ---
@app.route('/create_new_account', methods=['POST'])
def create_new_account_from_journal():
    """Handles creation of a new account initiated from the Journal Entry screen."""
    # Ensure request data is JSON
    data = request.get_json()
    
    code = data.get('new_code')
    name = data.get('new_name')
    acc_type = data.get('new_type')

    if code and name and acc_type:
        new_account = {
            'code': code,
            'name': name,
            'type': acc_type
        }
        
        # Validation checks
        all_accounts = get_all_dropdown_accounts()
        existing_codes = {acc['code'] for acc in all_accounts}
        existing_names = {acc['name'].lower() for acc in all_accounts}

        if code in existing_codes:
            return jsonify({'status': 'error', 'message': f'Account code {code} already exists.'}), 400
        
        if name.lower() in existing_names:
            return jsonify({'status': 'error', 'message': f'Account name "{name}" already exists.'}), 400
        
        # Add to the active chart of accounts
        session['chart_of_accounts'].append(new_account)
        session['chart_of_accounts'].sort(key=lambda x: x['code'])
        session.modified = True
        
        return jsonify({'status': 'success', 'account': new_account})
    
    return jsonify({'status': 'error', 'message': 'Missing required fields.'}), 400

# --- REST OF ROUTES (Updated logic for Balance Calculation, Edit, and Deletion) ---

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
    # Fallback if session expires
    if 'username' not in session:
        return redirect(url_for('login')) 
    # Fetch data for charts
    data = generate_financials()
    return render_template('dashboard.html', username=session.get('username'), data=data)

@app.route('/chart_of_accounts', methods=['GET', 'POST'])
def chart_of_accounts():
    # 1. Manual Add
    if request.method == 'POST':
        new_account = {
            'code': request.form.get('code'),
            'name': request.form.get('name'),
            'type': request.form.get('type')
        }
        # Check against ALL available accounts (system + user-added)
        all_accounts = get_all_dropdown_accounts()
        existing_codes = {acc['code'] for acc in all_accounts}
        
        if new_account['code'] not in existing_codes:
            session['chart_of_accounts'].append(new_account)
            session['chart_of_accounts'].sort(key=lambda x: x['code'])
            session.modified = True

    # 2. Calculate Balances 
    accounts = session.get('chart_of_accounts', [])
    entries = session.get('journal_entries', [])
    
    balances = {acc['name']: 0.0 for acc in accounts}

    for entry in entries:
        name = entry['account_name']
        debit = float(entry.get('debit', 0.0))
        credit = float(entry.get('credit', 0.0))
        
        acc_info = next((a for a in accounts if a['name'] == name), None)
        
        if name in balances and acc_info:
            acc_type = acc_info['type']
            
            # Special handling for Accumulated Depreciation (Contra-Asset: Credit is increase)
            if name == 'Accumulated Depreciation':
                balances[name] += (credit - debit)
            # Normal handling for Asset/Expense/Drawings (Debit is increase)
            elif acc_type in ['Asset', 'Expense'] or name in ['Drawings', 'Loss on Sale', 'COGS']:
                balances[name] += (debit - credit)
            # Normal handling for L/E/R (Credit is increase)
            else:
                balances[name] += (credit - debit)
                
    # Filter to only show accounts that have activity or are manually added
    display_accounts = [acc for acc in accounts if balances.get(acc['name'], 0.0) != 0.0 or acc.get('code') in ['000', '101', '301']]
    
    return render_template('chart_of_accounts.html', accounts=display_accounts, balances=balances)

@app.route('/journal_entry/<username>', methods=['GET', 'POST'])
def journal_entry(username):
    if request.method == 'POST':
        dates = request.form.getlist('date[]')
        names = request.form.getlist('account_name[]') 
        particulars = request.form.getlist('particular[]')
        debits = request.form.getlist('debit[]')
        credits = request.form.getlist('credit[]')
        is_adjusting = 'is_adjusting' in request.form
        
        # Find the highest existing ID and increment for the new batch
        max_id = -1
        if session['journal_entries']:
            max_id = max(e.get('id', -1) for e in session['journal_entries'])
        transaction_id = max_id + 1


        for i in range(len(dates)):
            # Activate the account, which also creates it if it doesn't exist
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
    
    # Use the new helper for rendering the dropdown
    all_options = get_all_dropdown_accounts()

    return render_template('journal_entry.html', username=username, accounts=all_options)

@app.route('/view_journal/<username>')
def view_journal(username):
    entries = session.get('journal_entries', [])
    accounts = session.get('chart_of_accounts', [])
    
    # 1. Prepare Summary Structure
    summary = {}
    for acc in accounts:
        summary[acc['name']] = {'type': acc['type'], 'debit': 0.0, 'credit': 0.0, 'balance': 0.0}

    # 2. Process Entries to calculate Totals and Balances
    for entry in entries:
        name = entry['account_name']
        debit = entry.get('debit', 0.0)
        credit = entry.get('credit', 0.0)
        
        if name in summary:
            # Update totals
            summary[name]['debit'] += debit
            summary[name]['credit'] += credit
            
            # Calculate Balance
            acct_type = summary[name]['type']
            
            if name == 'Accumulated Depreciation':
                summary[name]['balance'] += (credit - debit)
            elif acct_type in ['Asset', 'Expense'] or name in ['Drawings', 'Loss on Sale', 'COGS']:
                summary[name]['balance'] += (debit - credit)
            else:
                summary[name]['balance'] += (credit - debit)
                
    return render_template('view_journal.html', username=username, entries=entries, summary=summary)

# --- FIX: Change route parameter to 'index' to target the specific list position ---
@app.route('/edit_journal/<int:index>', methods=['GET', 'POST'])
def edit_journal(index):
    journal_list = session.get('journal_entries', [])
    target_index = index
    
    if 0 <= target_index < len(journal_list):
        if request.method == 'POST':
            # Note: This logic now updates the specific line located at 'index'
            entry = session['journal_entries'][target_index]
            entry['date'] = request.form.get('date')
            
            acc_name = request.form.get('account_name')
            activate_account(acc_name)
            
            entry['account_name'] = acc_name
            entry['particular'] = request.form.get('particular')
            entry['debit'] = float(request.form.get('debit') or 0.0)
            entry['credit'] = float(request.form.get('credit') or 0.0)
            entry['type'] = 'Adjusting' if 'is_adjusting' in request.form else 'Standard'
            session.modified = True
            return redirect(url_for('view_journal', username=session.get('username')))
        
        # Pass the entry at the calculated index
        return render_template('edit_journal.html', entry=session['journal_entries'][target_index])
    
    return redirect(url_for('view_journal', username=session.get('username')))

# --- DELETE ROUTE: Remains as 'id' (transaction ID) to delete ALL related entries ---
@app.route('/delete_journal/<int:id>', methods=['POST'])
def delete_journal(id):
    journal_list = session.get('journal_entries', [])
    
    # Correctly delete all matching entries by ID (e.g., if one transaction had a Debit and Credit line)
    new_journal_list = [entry for entry in journal_list if entry.get('id') != id]
    
    if len(new_journal_list) < len(journal_list):
        session['journal_entries'] = new_journal_list
        session.modified = True
        
    return redirect(url_for('view_journal', username=session.get('username')))

def generate_financials():
    journals = session.get('journal_entries', [])
    accounts = session.get('chart_of_accounts', [])
    
    # 1. Initialize Ledger with all active accounts
    ledger = {}
    for acc in accounts:
        ledger[acc['name']] = {'type': acc['type'], 'balance': 0.0, 'debit_total': 0.0, 'credit_total': 0.0}
    
    # 2. Post entries to calculate balances
    for entry in journals:
        acct_name = entry['account_name']
        debit = entry['debit']
        credit = entry['credit']
        
        if acct_name not in ledger:
            # Should not happen with current initialization, but necessary for added entries
            activate_account(acct_name)
            acc_info = next((a for a in session['chart_of_accounts'] if a['name'] == acct_name), None)
            if acc_info:
                ledger[acct_name] = {'type': acc_info['type'], 'balance': 0.0, 'debit_total': 0.0, 'credit_total': 0.0}
            else: continue
            
        data = ledger[acct_name]
        data['debit_total'] += debit
        data['credit_total'] += credit
        acct_type = data['type']
        
        # Special handling for Accumulated Depreciation (Contra-Asset)
        if acct_name == 'Accumulated Depreciation':
            data['balance'] += (credit - debit)
        # Normal Asset/Expense accounts (Debit balance)
        elif acct_type in ['Asset', 'Expense'] or acct_name in ['Drawings', 'Loss on Sale', 'COGS']:
            data['balance'] += (debit - credit)
        # Normal Liability/Equity/Revenue accounts (Credit balance)
        else:
            data['balance'] += (credit - debit)

    # 3. Calculate Financial Statements totals
    
    # Income Statement Items
    # Revenue accounts (Credit balance)
    revenue_total = sum(data['balance'] for name, data in ledger.items() if data['type'] == 'Revenue')
    # Expense accounts (Debit balance, thus positive values in ledger['balance'])
    expenses_total = sum(data['balance'] for name, data in ledger.items() if data['type'] == 'Expense' or name in ['COGS', 'Loss on Sale'])

    net_income = revenue_total - expenses_total
    
    # =======================================================
    # NEW BLOCK: DATA FOR CHARTS
    # =======================================================
    type_summary = {
        'Asset': 0.0, 'Liability': 0.0, 'Equity': 0.0, 
        'Revenue': 0.0, 'Expense': 0.0
    }
    for name, data in ledger.items():
        acct_type = data['type']
        
        # Use the calculated final balance for the chart data
        balance = data['balance']
        
        # Assets have a normal debit balance (positive is debit)
        if acct_type == 'Asset':
            # Contra-asset (Accumulated Depreciation) is a credit balance, reducing total assets.
            if name == 'Accumulated Depreciation':
                type_summary[acct_type] -= balance 
            else:
                type_summary[acct_type] += balance
            
        # Liabilities and Revenue have a normal credit balance (positive is credit)
        elif acct_type in ['Liability', 'Revenue']:
            type_summary[acct_type] += balance
            
        # Equity is Capital - Drawings + Net Income, but here we aggregate the Equity type accounts only.
        # Drawings is contra-equity (debit), Capital is equity (credit).
        elif acct_type == 'Equity':
            if name == 'Drawings':
                type_summary[acct_type] -= balance # Drawings reduces equity
            else:
                 type_summary[acct_type] += balance # Capital increases equity
                 
        # Expenses have a normal debit balance (positive is debit)
        elif acct_type == 'Expense' or name in ['COGS', 'Loss on Sale']:
            type_summary['Expense'] += balance

    # =======================================================
    # END NEW BLOCK
    # =======================================================

    
    # Balance Sheet Items
    assets = 0.0
    liabilities = 0.0
    
    bank_balance = ledger.get('Bank', {'balance': 0.0})['balance']
    accumulated_depreciation = ledger.get('Accumulated Depreciation', {'balance': 0.0})['balance']
    
    # Calculate Total Assets based on cleaned logic (Only include positive asset balances)
    for name, data in ledger.items():
        acct_type = data['type']
        balance = data['balance']
        
        if acct_type == 'Asset':
            if name != 'Accumulated Depreciation':
                # Only include assets with a positive balance (Debit balance)
                if balance > 0.01:
                    assets += balance
            
    # Subtract Accumulated Depreciation (Contra-Asset with Credit Balance, so balance is positive)
    assets -= accumulated_depreciation

    # Calculate Liabilities
    for name, data in ledger.items():
        acct_type = data['type']
        balance = data['balance']
        
        if acct_type == 'Liability':
            liabilities += balance
            
    # Add Bank Overdraft if Bank balance is negative
    if bank_balance < 0:
        liabilities += abs(bank_balance)

    # Adjust Equity: Capital + Net Income - Drawings
    capital = ledger.get('Capital', {'balance': 0.0})['balance']
    drawings = ledger.get('Drawings', {'balance': 0.0})['balance']
    
    total_equity_liab = liabilities + capital + net_income - drawings
    
    is_balanced = abs(assets - total_equity_liab) < 0.01

    # =======================================================
    # TRIAL BALANCE DATA PREPARATION
    # =======================================================
    tb_debits = 0.0
    tb_credits = 0.0
    trial_balance_accounts = []

    # Iterate over ledger, only include accounts with non-zero balances
    for name, data in sorted(ledger.items()):
        balance = data['balance']
        acct_type = data['type']
        
        # Determine the account's "normal" balance type (Debit or Credit)
        is_debit_type = (acct_type in ['Asset', 'Expense'] or name in ['Drawings', 'COGS', 'Loss on Sale']) and name != 'Accumulated Depreciation'
        
        if name == 'Accumulated Depreciation':
            is_debit_type = False # Contra-Asset's normal balance is Credit
        
        # Only include accounts that have a significant activity balance
        if abs(balance) > 0.005: 
            
            # If the final balance direction matches the normal direction (or is a Credit type with a negative balance)
            # This is the logic for how a final balance is placed on the TB
            if (is_debit_type and balance >= 0) or (not is_debit_type and balance < 0):
                debit_amount = abs(balance)
                credit_amount = 0.0
                tb_debits += debit_amount
            # Otherwise, assign to Credit column
            else:
                debit_amount = 0.0
                credit_amount = abs(balance)
                tb_credits += credit_amount
            
            trial_balance_accounts.append({
                'name': name,
                'debit': debit_amount,
                'credit': credit_amount
            })

    # Check if the Trial Balance balances
    tb_balanced = abs(tb_debits - tb_credits) < 0.01
    
    # =======================================================
    # END TRIAL BALANCE BLOCK
    # =======================================================


    return {
        'ledger': ledger,
        'income_statement': {'revenue': revenue_total, 'expenses': expenses_total, 'net_income': net_income},
        'balance_sheet': {'assets': assets, 'liabilities': liabilities, 'equity': total_equity_liab - liabilities, 'total_eq_liab': total_equity_liab, 'is_balanced': is_balanced},
        'trial_balance': {'accounts': trial_balance_accounts, 'total_debits': tb_debits, 'total_credits': tb_credits, 'is_balanced': tb_balanced},
        'type_summary': type_summary # Add summary data for charts
    }


@app.route('/financial_reports')
def financial_reports():
    data = generate_financials()
    return render_template('financial_reports.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)