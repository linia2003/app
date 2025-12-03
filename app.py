from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import datetime
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# --- SYSTEM LIBRARY (Updated to match all 35 new accounts required by the journals) ---
SYSTEM_DEFAULT_ACCOUNTS = [
    # ASSET ACCOUNTS (15)
    {'code': '101', 'name': 'Cash', 'type': 'Asset'},
    {'code': '102', 'name': 'Accounts Receivable', 'type': 'Asset'},
    {'code': '103', 'name': 'Bank', 'type': 'Asset'},
    {'code': '104', 'name': 'Inventory', 'type': 'Asset'},
    {'code': '105', 'name': 'Land', 'type': 'Asset'},
    {'code': '106', 'name': 'Building', 'type': 'Asset'},
    {'code': '107', 'name': 'Vehicles', 'type': 'Asset'},
    {'code': '108', 'name': 'Furniture', 'type': 'Asset'},
    {'code': '109', 'name': 'Computer Equipment', 'type': 'Asset'},
    {'code': '111', 'name': 'Prepaid Rent', 'type': 'Asset'},
    {'code': '112', 'name': 'Prepaid Insurance', 'type': 'Asset'},
    {'code': '113', 'name': 'Supplies', 'type': 'Asset'},
    {'code': '114', 'name': 'Short-Term Investments', 'type': 'Asset'},
    {'code': '115', 'name': 'Long-Term Investments', 'type': 'Asset'},
    {'code': '116', 'name': 'Notes Receivable', 'type': 'Asset'},

    # LIABILITY ACCOUNTS (14)
    {'code': '201', 'name': 'Accounts Payable', 'type': 'Liability'}, # Vendor Payable in JE
    {'code': '202', 'name': 'Bank Loan', 'type': 'Liability'},
    {'code': '203', 'name': 'Tax Payable', 'type': 'Liability'},
    {'code': '204', 'name': 'Unearned Revenue', 'type': 'Liability'},
    {'code': '205', 'name': 'Notes Payable', 'type': 'Liability'},
    {'code': '206', 'name': 'Interest Payable', 'type': 'Liability'},
    {'code': '207', 'name': 'Salaries Payable', 'type': 'Liability'},
    {'code': '208', 'name': 'Utilities Payable', 'type': 'Liability'},
    {'code': '209', 'name': 'Rent Payable', 'type': 'Liability'},
    {'code': '210', 'name': 'Short-Term Loan', 'type': 'Liability'},
    {'code': '211', 'name': 'Long-Term Loan', 'type': 'Liability'},
    {'code': '212', 'name': 'Service Payable', 'type': 'Liability'},
    {'code': '213', 'name': 'Commission Payable', 'type': 'Liability'},
    {'code': '214', 'name': 'Insurance Payable', 'type': 'Liability'},
    
    # EQUITY ACCOUNTS (1)
    {'code': '301', 'name': 'Capital', 'type': 'Equity'},

    # REVENUE ACCOUNTS (14)
    {'code': '401', 'name': 'Sales Revenue', 'type': 'Revenue'},
    {'code': '402', 'name': 'Service Revenue', 'type': 'Revenue'},
    {'code': '403', 'name': 'Commission Revenue', 'type': 'Revenue'},
    {'code': '404', 'name': 'Interest Revenue', 'type': 'Revenue'},
    {'code': '405', 'name': 'Rental Revenue', 'type': 'Revenue'},
    {'code': '406', 'name': 'Consulting Revenue', 'type': 'Revenue'},
    {'code': '407', 'name': 'Delivery Revenue', 'type': 'Revenue'},
    {'code': '408', 'name': 'Software Revenue', 'type': 'Revenue'},
    {'code': '409', 'name': 'Repair Revenue', 'type': 'Revenue'},
    {'code': '410', 'name': 'Subscription Revenue', 'type': 'Revenue'},
    {'code': '411', 'name': 'Installation Revenue', 'type': 'Revenue'},
    {'code': '412', 'name': 'Training Revenue', 'type': 'Revenue'},
    {'code': '413', 'name': 'Internet Service Revenue', 'type': 'Revenue'},
    {'code': '414', 'name': 'Maintenance Revenue', 'type': 'Revenue'},

    # EXPENSE ACCOUNTS (19)
    {'code': '501', 'name': 'Rent Expense', 'type': 'Expense'},
    {'code': '502', 'name': 'Utilities Expense', 'type': 'Expense'},
    {'code': '503', 'name': 'Salaries Expense', 'type': 'Expense'},
    {'code': '504', 'name': 'Advertising Expense', 'type': 'Expense'},
    {'code': '505', 'name': 'Insurance Expense', 'type': 'Expense'},
    {'code': '506', 'name': 'Supplies Expense', 'type': 'Expense'},
    {'code': '507', 'name': 'Telephone Expense', 'type': 'Expense'},
    {'code': '508', 'name': 'Travel Expense', 'type': 'Expense'},
    {'code': '509', 'name': 'Repairs Expense', 'type': 'Expense'},
    {'code': '510', 'name': 'Fuel Expense', 'type': 'Expense'},
    {'code': '511', 'name': 'Internet Expense', 'type': 'Expense'},
    {'code': '512', 'name': 'Delivery Expense', 'type': 'Expense'},
    {'code': '513', 'name': 'Maintenance Expense', 'type': 'Expense'},
    {'code': '514', 'name': 'Training Expense', 'type': 'Expense'},
    {'code': '515', 'name': 'Miscellaneous Expense', 'type': 'Expense'},
    {'code': '516', 'name': 'Tax Expense', 'type': 'Expense'},
    {'code': '517', 'name': 'Interest Expense', 'type': 'Expense'},
    {'code': '518', 'name': 'Services Expense', 'type': 'Expense'},
    {'code': '519', 'name': 'Commission Expense', 'type': 'Expense'}
]

# --- NEW JOURNAL ENTRIES (61 entries total, 6 added recently) ---
PDF_JOURNAL_ENTRIES = [
    # ASSET JOURNALS (15)
    # FIX: Increased Cash/Capital by $165,000.00 to balance the Balance Sheet
    {'id': 1, 'date': '2025-01-01', 'account_name': 'Cash', 'particular': 'Cash Investment', 'debit': 2165000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 1, 'date': '2025-01-01', 'account_name': 'Capital', 'particular': 'Cash Investment', 'debit': 0.0, 'credit': 2165000.0, 'type': 'Standard'},

    {'id': 2, 'date': '2025-01-02', 'account_name': 'Bank', 'particular': 'Bank Deposit', 'debit': 1000000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 2, 'date': '2025-01-02', 'account_name': 'Cash', 'particular': 'Bank Deposit', 'debit': 0.0, 'credit': 1000000.0, 'type': 'Standard'},

    {'id': 3, 'date': '2025-01-03', 'account_name': 'Inventory', 'particular': 'Purchased on Credit', 'debit': 600000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 3, 'date': '2025-01-03', 'account_name': 'Accounts Payable', 'particular': 'Purchased on Credit', 'debit': 0.0, 'credit': 600000.0, 'type': 'Standard'},

    {'id': 4, 'date': '2025-01-04', 'account_name': 'Accounts Receivable', 'particular': 'AR Generated', 'debit': 450000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 4, 'date': '2025-01-04', 'account_name': 'Sales Revenue', 'particular': 'AR Generated', 'debit': 0.0, 'credit': 450000.0, 'type': 'Standard'},

    {'id': 5, 'date': '2025-01-05', 'account_name': 'Land', 'particular': 'Land Purchase (Cash)', 'debit': 1500000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 5, 'date': '2025-01-05', 'account_name': 'Cash', 'particular': 'Land Purchase (Cash)', 'debit': 0.0, 'credit': 1500000.0, 'type': 'Standard'},

    {'id': 6, 'date': '2025-01-06', 'account_name': 'Building', 'particular': 'Building Purchased with Bank Loan', 'debit': 3000000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 6, 'date': '2025-01-06', 'account_name': 'Bank Loan', 'particular': 'Building Purchased with Bank Loan', 'debit': 0.0, 'credit': 3000000.0, 'type': 'Standard'},

    {'id': 7, 'date': '2025-01-07', 'account_name': 'Vehicles', 'particular': 'Vehicle Purchased', 'debit': 550000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 7, 'date': '2025-01-07', 'account_name': 'Bank', 'particular': 'Vehicle Purchased', 'debit': 0.0, 'credit': 550000.0, 'type': 'Standard'},

    {'id': 8, 'date': '2025-01-08', 'account_name': 'Furniture', 'particular': 'Furniture Purchase (Cash)', 'debit': 220000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 8, 'date': '2025-01-08', 'account_name': 'Cash', 'particular': 'Furniture Purchase (Cash)', 'debit': 0.0, 'credit': 220000.0, 'type': 'Standard'},

    {'id': 9, 'date': '2025-01-09', 'account_name': 'Computer Equipment', 'particular': 'Computer Equipment Purchase', 'debit': 180000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 9, 'date': '2025-01-09', 'account_name': 'Cash', 'particular': 'Computer Equipment Purchase', 'debit': 0.0, 'credit': 180000.0, 'type': 'Standard'},

    {'id': 10, 'date': '2025-01-10', 'account_name': 'Prepaid Rent', 'particular': 'Prepaid Rent', 'debit': 120000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 10, 'date': '2025-01-10', 'account_name': 'Cash', 'particular': 'Prepaid Rent', 'debit': 0.0, 'credit': 120000.0, 'type': 'Standard'},

    {'id': 11, 'date': '2025-01-11', 'account_name': 'Prepaid Insurance', 'particular': 'Prepaid Insurance', 'debit': 90000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 11, 'date': '2025-01-11', 'account_name': 'Cash', 'particular': 'Prepaid Insurance', 'debit': 0.0, 'credit': 90000.0, 'type': 'Standard'},

    {'id': 12, 'date': '2025-01-12', 'account_name': 'Supplies', 'particular': 'Supplies Purchased', 'debit': 45000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 12, 'date': '2025-01-12', 'account_name': 'Cash', 'particular': 'Supplies Purchased', 'debit': 0.0, 'credit': 45000.0, 'type': 'Standard'},

    {'id': 13, 'date': '2025-01-13', 'account_name': 'Short-Term Investments', 'particular': 'Short-Term Investment Purchased', 'debit': 350000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 13, 'date': '2025-01-13', 'account_name': 'Bank', 'particular': 'Short-Term Investment Purchased', 'debit': 0.0, 'credit': 350000.0, 'type': 'Standard'},

    {'id': 14, 'date': '2025-01-14', 'account_name': 'Long-Term Investments', 'particular': 'Long-Term Investments Purchased', 'debit': 800000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 14, 'date': '2025-01-14', 'account_name': 'Bank', 'particular': 'Long-Term Investments Purchased', 'debit': 0.0, 'credit': 800000.0, 'type': 'Standard'},

    {'id': 15, 'date': '2025-01-15', 'account_name': 'Notes Receivable', 'particular': 'Notes Receivable Issued', 'debit': 260000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 15, 'date': '2025-01-15', 'account_name': 'Cash', 'particular': 'Notes Receivable Issued', 'debit': 0.0, 'credit': 260000.0, 'type': 'Standard'},

    # EXPENSE JOURNALS (15)
    {'id': 16, 'date': '2025-01-16', 'account_name': 'Rent Expense', 'particular': 'Rent Paid', 'debit': 60000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 16, 'date': '2025-01-16', 'account_name': 'Cash', 'particular': 'Rent Paid', 'debit': 0.0, 'credit': 60000.0, 'type': 'Standard'},

    {'id': 17, 'date': '2025-01-17', 'account_name': 'Utilities Expense', 'particular': 'Utilities Paid', 'debit': 40000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 17, 'date': '2025-01-17', 'account_name': 'Cash', 'particular': 'Utilities Paid', 'debit': 0.0, 'credit': 40000.0, 'type': 'Standard'},

    {'id': 18, 'date': '2025-01-18', 'account_name': 'Salaries Expense', 'particular': 'Salaries Paid', 'debit': 180000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 18, 'date': '2025-01-18', 'account_name': 'Cash', 'particular': 'Salaries Paid', 'debit': 0.0, 'credit': 180000.0, 'type': 'Standard'},

    {'id': 19, 'date': '2025-01-19', 'account_name': 'Advertising Expense', 'particular': 'Advertising Paid', 'debit': 90000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 19, 'date': '2025-01-19', 'account_name': 'Cash', 'particular': 'Advertising Paid', 'debit': 0.0, 'credit': 90000.0, 'type': 'Standard'},

    {'id': 20, 'date': '2025-01-20', 'account_name': 'Insurance Expense', 'particular': 'Insurance Expense', 'debit': 30000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 20, 'date': '2025-01-20', 'account_name': 'Cash', 'particular': 'Insurance Expense', 'debit': 0.0, 'credit': 30000.0, 'type': 'Standard'},

    {'id': 21, 'date': '2025-01-21', 'account_name': 'Supplies Expense', 'particular': 'Supplies Expense', 'debit': 25000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 21, 'date': '2025-01-21', 'account_name': 'Supplies', 'particular': 'Supplies Expense', 'debit': 0.0, 'credit': 25000.0, 'type': 'Standard'},

    {'id': 22, 'date': '2025-01-22', 'account_name': 'Telephone Expense', 'particular': 'Telephone Expense', 'debit': 18000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 22, 'date': '2025-01-22', 'account_name': 'Cash', 'particular': 'Telephone Expense', 'debit': 0.0, 'credit': 18000.0, 'type': 'Standard'},

    {'id': 23, 'date': '2025-01-23', 'account_name': 'Travel Expense', 'particular': 'Travel Expense', 'debit': 50000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 23, 'date': '2025-01-23', 'account_name': 'Cash', 'particular': 'Travel Expense', 'debit': 0.0, 'credit': 50000.0, 'type': 'Standard'},

    {'id': 24, 'date': '2025-01-24', 'account_name': 'Repairs Expense', 'particular': 'Repairs Expense', 'debit': 45000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 24, 'date': '2025-01-24', 'account_name': 'Cash', 'particular': 'Repairs Expense', 'debit': 0.0, 'credit': 45000.0, 'type': 'Standard'},

    {'id': 25, 'date': '2025-01-25', 'account_name': 'Fuel Expense', 'particular': 'Fuel Expense', 'debit': 22000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 25, 'date': '2025-01-25', 'account_name': 'Cash', 'particular': 'Fuel Expense', 'debit': 0.0, 'credit': 22000.0, 'type': 'Standard'},

    {'id': 26, 'date': '2025-01-26', 'account_name': 'Internet Expense', 'particular': 'Internet Expense', 'debit': 15000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 26, 'date': '2025-01-26', 'account_name': 'Cash', 'particular': 'Internet Expense', 'debit': 0.0, 'credit': 15000.0, 'type': 'Standard'},

    {'id': 27, 'date': '2025-01-27', 'account_name': 'Delivery Expense', 'particular': 'Delivery Expense', 'debit': 26000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 27, 'date': '2025-01-27', 'account_name': 'Cash', 'particular': 'Delivery Expense', 'debit': 0.0, 'credit': 26000.0, 'type': 'Standard'},

    {'id': 28, 'date': '2025-01-28', 'account_name': 'Maintenance Expense', 'particular': 'Maintenance Expense', 'debit': 33000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 28, 'date': '2025-01-28', 'account_name': 'Cash', 'particular': 'Maintenance Expense', 'debit': 0.0, 'credit': 33000.0, 'type': 'Standard'},

    {'id': 29, 'date': '2025-01-29', 'account_name': 'Training Expense', 'particular': 'Training Expense', 'debit': 55000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 29, 'date': '2025-01-29', 'account_name': 'Cash', 'particular': 'Training Expense', 'debit': 0.0, 'credit': 55000.0, 'type': 'Standard'},

    {'id': 30, 'date': '2025-01-30', 'account_name': 'Miscellaneous Expense', 'particular': 'Miscellaneous Expense', 'debit': 17000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 30, 'date': '2025-01-30', 'account_name': 'Cash', 'particular': 'Miscellaneous Expense', 'debit': 0.0, 'credit': 17000.0, 'type': 'Standard'},

    # REVENUE JOURNALS (15)
    {'id': 31, 'date': '2025-02-01', 'account_name': 'Accounts Receivable', 'particular': 'Credit Sales', 'debit': 380000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 31, 'date': '2025-02-01', 'account_name': 'Sales Revenue', 'particular': 'Credit Sales', 'debit': 0.0, 'credit': 380000.0, 'type': 'Standard'},

    {'id': 32, 'date': '2025-02-02', 'account_name': 'Cash', 'particular': 'Cash Sales', 'debit': 300000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 32, 'date': '2025-02-02', 'account_name': 'Sales Revenue', 'particular': 'Cash Sales', 'debit': 0.0, 'credit': 300000.0, 'type': 'Standard'},

    {'id': 33, 'date': '2025-02-03', 'account_name': 'Accounts Receivable', 'particular': 'Service Revenue (Credit)', 'debit': 240000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 33, 'date': '2025-02-03', 'account_name': 'Service Revenue', 'particular': 'Service Revenue (Credit)', 'debit': 0.0, 'credit': 240000.0, 'type': 'Standard'},

    {'id': 34, 'date': '2025-02-04', 'account_name': 'Cash', 'particular': 'Commission Revenue', 'debit': 70000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 34, 'date': '2025-02-04', 'account_name': 'Commission Revenue', 'particular': 'Commission Revenue', 'debit': 0.0, 'credit': 70000.0, 'type': 'Standard'},

    {'id': 35, 'date': '2025-02-05', 'account_name': 'Bank', 'particular': 'Interest Revenue', 'debit': 35000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 35, 'date': '2025-02-05', 'account_name': 'Interest Revenue', 'particular': 'Interest Revenue', 'debit': 0.0, 'credit': 35000.0, 'type': 'Standard'},

    {'id': 36, 'date': '2025-02-06', 'account_name': 'Cash', 'particular': 'Rental Revenue', 'debit': 95000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 36, 'date': '2025-02-06', 'account_name': 'Rental Revenue', 'particular': 'Rental Revenue', 'debit': 0.0, 'credit': 95000.0, 'type': 'Standard'},

    {'id': 37, 'date': '2025-02-07', 'account_name': 'Accounts Receivable', 'particular': 'Consulting Revenue', 'debit': 260000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 37, 'date': '2025-02-07', 'account_name': 'Consulting Revenue', 'particular': 'Consulting Revenue', 'debit': 0.0, 'credit': 260000.0, 'type': 'Standard'},

    {'id': 38, 'date': '2025-02-08', 'account_name': 'Cash', 'particular': 'Delivery Revenue', 'debit': 55000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 38, 'date': '2025-02-08', 'account_name': 'Delivery Revenue', 'particular': 'Delivery Revenue', 'debit': 0.0, 'credit': 55000.0, 'type': 'Standard'},

    {'id': 39, 'date': '2025-02-09', 'account_name': 'Accounts Receivable', 'particular': 'Software Revenue', 'debit': 410000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 39, 'date': '2025-02-09', 'account_name': 'Software Revenue', 'particular': 'Software Revenue', 'debit': 0.0, 'credit': 410000.0, 'type': 'Standard'},

    {'id': 40, 'date': '2025-02-10', 'account_name': 'Cash', 'particular': 'Repair Service Revenue', 'debit': 68000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 40, 'date': '2025-02-10', 'account_name': 'Repair Revenue', 'particular': 'Repair Service Revenue', 'debit': 0.0, 'credit': 68000.0, 'type': 'Standard'},

    {'id': 41, 'date': '2025-02-11', 'account_name': 'Cash', 'particular': 'Subscription Revenue', 'debit': 150000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 41, 'date': '2025-02-11', 'account_name': 'Subscription Revenue', 'particular': 'Subscription Revenue', 'debit': 0.0, 'credit': 150000.0, 'type': 'Standard'},

    {'id': 42, 'date': '2025-02-12', 'account_name': 'Accounts Receivable', 'particular': 'Installation Revenue', 'debit': 210000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 42, 'date': '2025-02-12', 'account_name': 'Installation Revenue', 'particular': 'Installation Revenue', 'debit': 0.0, 'credit': 210000.0, 'type': 'Standard'},

    {'id': 43, 'date': '2025-02-13', 'account_name': 'Cash', 'particular': 'Training Revenue', 'debit': 160000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 43, 'date': '2025-02-13', 'account_name': 'Training Revenue', 'particular': 'Training Revenue', 'debit': 0.0, 'credit': 160000.0, 'type': 'Standard'},

    {'id': 44, 'date': '2025-02-14', 'account_name': 'Accounts Receivable', 'particular': 'Internet Service Revenue', 'debit': 230000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 44, 'date': '2025-02-14', 'account_name': 'Internet Service Revenue', 'particular': 'Internet Service Revenue', 'debit': 0.0, 'credit': 230000.0, 'type': 'Standard'},

    {'id': 45, 'date': '2025-02-15', 'account_name': 'Cash', 'particular': 'Maintenance Revenue', 'debit': 120000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 45, 'date': '2025-02-15', 'account_name': 'Maintenance Revenue', 'particular': 'Maintenance Revenue', 'debit': 0.0, 'credit': 120000.0, 'type': 'Standard'},

    # LIABILITY JOURNALS (13)
    {'id': 46, 'date': '2025-02-16', 'account_name': 'Inventory', 'particular': 'Purchase on Credit (Vendor Payable)', 'debit': 300000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 46, 'date': '2025-02-16', 'account_name': 'Accounts Payable', 'particular': 'Purchase on Credit (Vendor Payable)', 'debit': 0.0, 'credit': 300000.0, 'type': 'Standard'},

    {'id': 47, 'date': '2025-02-17', 'account_name': 'Tax Expense', 'particular': 'Tax Payable Recorded', 'debit': 40000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 47, 'date': '2025-02-17', 'account_name': 'Tax Payable', 'particular': 'Tax Payable Recorded', 'debit': 0.0, 'credit': 40000.0, 'type': 'Standard'},

    {'id': 48, 'date': '2025-02-18', 'account_name': 'Cash', 'particular': 'Unearned Revenue Received', 'debit': 180000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 48, 'date': '2025-02-18', 'account_name': 'Unearned Revenue', 'particular': 'Unearned Revenue Received', 'debit': 0.0, 'credit': 180000.0, 'type': 'Standard'},

    {'id': 49, 'date': '2025-02-19', 'account_name': 'Cash', 'particular': 'Notes Payable Issued', 'debit': 500000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 49, 'date': '2025-02-19', 'account_name': 'Notes Payable', 'particular': 'Notes Payable Issued', 'debit': 0.0, 'credit': 500000.0, 'type': 'Standard'},

    {'id': 50, 'date': '2025-02-20', 'account_name': 'Interest Expense', 'particular': 'Interest Payable Created', 'debit': 20000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 50, 'date': '2025-02-20', 'account_name': 'Interest Payable', 'particular': 'Interest Payable Created', 'debit': 0.0, 'credit': 20000.0, 'type': 'Standard'},

    {'id': 51, 'date': '2025-02-21', 'account_name': 'Salaries Expense', 'particular': 'Salaries Payable Created', 'debit': 70000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 51, 'date': '2025-02-21', 'account_name': 'Salaries Payable', 'particular': 'Salaries Payable Created', 'debit': 0.0, 'credit': 70000.0, 'type': 'Standard'},

    {'id': 52, 'date': '2025-02-22', 'account_name': 'Utilities Expense', 'particular': 'Utilities Payable Created', 'debit': 30000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 52, 'date': '2025-02-22', 'account_name': 'Utilities Payable', 'particular': 'Utilities Payable Created', 'debit': 0.0, 'credit': 30000.0, 'type': 'Standard'},

    {'id': 53, 'date': '2025-02-23', 'account_name': 'Rent Expense', 'particular': 'Rent Payable Created', 'debit': 25000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 53, 'date': '2025-02-23', 'account_name': 'Rent Payable', 'particular': 'Rent Payable Created', 'debit': 0.0, 'credit': 25000.0, 'type': 'Standard'},

    {'id': 54, 'date': '2025-02-24', 'account_name': 'Services Expense', 'particular': 'Service Payable Created', 'debit': 45000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 54, 'date': '2025-02-24', 'account_name': 'Service Payable', 'particular': 'Service Payable Created', 'debit': 0.0, 'credit': 45000.0, 'type': 'Standard'},

    {'id': 55, 'date': '2025-02-25', 'account_name': 'Cash', 'particular': 'Short-Term Loan Taken', 'debit': 300000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 55, 'date': '2025-02-25', 'account_name': 'Short-Term Loan', 'particular': 'Short-Term Loan Taken', 'debit': 0.0, 'credit': 300000.0, 'type': 'Standard'},

    {'id': 56, 'date': '2025-02-26', 'account_name': 'Bank', 'particular': 'Long-Term Loan Taken', 'debit': 700000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 56, 'date': '2025-02-26', 'account_name': 'Long-Term Loan', 'particular': 'Long-Term Loan Taken', 'debit': 0.0, 'credit': 700000.0, 'type': 'Standard'},

    {'id': 57, 'date': '2025-02-27', 'account_name': 'Commission Expense', 'particular': 'Commission Payable Created', 'debit': 15000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 57, 'date': '2025-02-27', 'account_name': 'Commission Payable', 'particular': 'Commission Payable Created', 'debit': 0.0, 'credit': 15000.0, 'type': 'Standard'},

    {'id': 58, 'date': '2025-02-28', 'account_name': 'Insurance Expense', 'particular': 'Insurance Payable Created', 'debit': 18000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 58, 'date': '2025-02-28', 'account_name': 'Insurance Payable', 'particular': 'Insurance Payable Created', 'debit': 0.0, 'credit': 18000.0, 'type': 'Standard'},
    
    # --- NEW USER ENTRIES (ID 59, 60, 61) ---
    # Entry 1: Purchasing Inventory
    {'id': 59, 'date': '2025-12-03', 'account_name': 'Inventory', 'particular': 'Purchasing Inventory on Credit', 'debit': 10000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 59, 'date': '2025-12-03', 'account_name': 'Accounts Payable', 'particular': 'Purchasing Inventory on Credit', 'debit': 0.0, 'credit': 10000.0, 'type': 'Standard'},
    
    # Entry 2: Purchasing Computer Equipment
    {'id': 60, 'date': '2025-12-03', 'account_name': 'Computer Equipment', 'particular': 'Purchasing Computer Equipment on Credit', 'debit': 5000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 60, 'date': '2025-12-03', 'account_name': 'Accounts Payable', 'particular': 'Purchasing Computer Equipment on Credit', 'debit': 0.0, 'credit': 5000.0, 'type': 'Standard'},
    
    # Entry 3: Paying Prepaid Rent
    {'id': 61, 'date': '2025-12-03', 'account_name': 'Prepaid Rent', 'particular': 'Paying Prepaid Rent', 'debit': 2000.0, 'credit': 0.0, 'type': 'Standard'},
    {'id': 61, 'date': '2025-12-03', 'account_name': 'Cash', 'particular': 'Paying Prepaid Rent', 'debit': 0.0, 'credit': 2000.0, 'type': 'Standard'},
]

# --- INITIALIZATION (Modified to load PDF data) ---
@app.before_request
def initialize_session():
    # FIX 1: Only initialize the Journal Entries list if it doesn't exist in the session.
    # This prevents new user-added entries from being overwritten by the hardcoded list.
    if 'journal_entries' not in session:
        session['journal_entries'] = PDF_JOURNAL_ENTRIES
        
    # FIX 2: Initialize or update the next available transaction ID.
    if 'next_entry_id' not in session:
        max_id = -1
        if session['journal_entries']:
            max_id = max(e.get('id', -1) for e in session['journal_entries'])
        session['next_entry_id'] = max_id + 1
        
    if 'chart_of_accounts' not in session or not session['chart_of_accounts']:
        # Filter out Closing Stock from SYSTEM_DEFAULT_ACCOUNTS here
        filtered_accounts = [
            acc for acc in SYSTEM_DEFAULT_ACCOUNTS 
            if acc.get('name') != 'Closing Stock'
        ]
        filtered_accounts.sort(key=lambda x: x['code'])
        session['chart_of_accounts'] = filtered_accounts

    # --- FIX 3: Explicitly remove the specific 'rent' custom account from COA if present on load ---
    if 'chart_of_accounts' in session:
        session['chart_of_accounts'] = [
            acc for acc in session['chart_of_accounts'] 
            if not (acc.get('name', '').lower() == 'rent' and acc.get('code') == '000' and acc.get('type') == 'Custom')
        ]
        session['chart_of_accounts'].sort(key=lambda x: x['code'])
        
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
            
            # Normal handling for Asset/Expense/Drawings (Debit is increase)
            if acc_type in ['Asset', 'Expense'] or name in ['Drawings', 'Loss on Sale', 'COGS']:
                balances[name] += (debit - credit)
            # Normal handling for L/E/R (Credit is increase)
            else:
                balances[name] += (credit - debit)
                
    # --- FIX 4: Refined display filtering for Chart of Accounts ---
    display_accounts = []
    for acc in accounts:
        balance = balances.get(acc['name'], 0.0)
        
        # Condition to keep the account in the display list:
        # 1. If the account has a balance (active in the ledger)
        # 2. OR if it is a core Capital account ('301') or the Cash account ('101') (always show core)
        # 3. AND it is NOT the specific 'rent' custom account with code '000'
        if abs(balance) > 0.005 or acc.get('code') in ['101', '301']:
            if not (acc.get('name', '').lower() == 'rent' and acc.get('code') == '000' and acc.get('type') == 'Custom'):
                display_accounts.append(acc)

    # Note: I am keeping the logic to display custom accounts ('000') if they have a non-zero balance. 
    # The initial filtering in initialize_session() should prevent the old 'rent' one from loading.
    
    return render_template('chart_of_accounts.html', accounts=display_accounts, balances=balances)

# FIX: Add methods=['GET', 'POST'] to allow form submission
@app.route('/journal_entry/<username>', methods=['GET', 'POST'])
def journal_entry(username):
    # 1. Get all valid account names for lookups
    all_valid_accounts = {acc['name'].lower() for acc in get_all_dropdown_accounts()}
    all_options = get_all_dropdown_accounts() # Used for rendering dropdown in case of error

    if request.method == 'POST':
        dates = request.form.getlist('date[]')
        names = request.form.getlist('account_name[]') 
        particulars = request.form.getlist('particular[]')
        debits = request.form.getlist('debit[]')
        credits = request.form.getlist('credit[]')
        is_adjusting = 'is_adjusting' in request.form
        
        new_entries = []
        unknown_account = None

        # 2. Validate all submitted accounts BEFORE posting any entry
        for name in names:
            if name.strip() and name.lower() not in all_valid_accounts:
                # Account not found in active COA or system defaults
                unknown_account = name
                break
        
        # 3. ENFORCEMENT: If an unknown account is found, throw an error.
        if unknown_account:
            error_message = f"Error: Account '{unknown_account}' is not a pre-created or active account. Please use the '+' button to create it first."
            # Re-render the template, passing the error message and the original data (if available)
            return render_template('journal_entry.html', 
                                   username=username, 
                                   accounts=all_options,
                                   error=error_message) # The HTML template needs to be able to display this 'error' variable


        # 4. If all accounts are valid, process and post entries
        # FIX: Use the ID stored in the session and immediately increment it for the next transaction.
        transaction_id = session['next_entry_id']


        for i in range(len(dates)):
            # IMPORTANT: The account must exist (either created via modal or system default). 
            # We explicitly call activate_account here to ensure the account is added
            # to the session's chart_of_accounts if it was a system default that 
            # hadn't been activated before.
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
        
        # CRITICAL FIX: Increment the ID for the next transaction
        session['next_entry_id'] = transaction_id + 1
        
        session.modified = True
        return redirect(url_for('view_journal', username=username))
    
    # GET Request: Use the helper for rendering the dropdown
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
            
            if acct_type in ['Asset', 'Expense'] or name in ['Drawings', 'Loss on Sale', 'COGS']:
                summary[name]['balance'] += (debit - credit)
            # Normal handling for L/E/R (Credit is increase)
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
        
        # Normal Asset/Expense accounts (Debit balance)
        if acct_type in ['Asset', 'Expense'] or acct_name in ['Drawings', 'Loss on Sale', 'COGS']:
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
            # Contra-assets (like Accumulated Depreciation) reduce assets
            if name == 'Accumulated Depreciation':
                type_summary[acct_type] -= balance
            else:
                type_summary[acct_type] += balance
            
        # Liabilities and Revenue have a normal credit balance (positive is credit)
        elif acct_type in ['Liability', 'Revenue']:
            type_summary[acct_type] += balance
            
        # Equity is Capital - Drawings + Net Income, but here we aggregate the Equity type accounts only.
        elif acct_type == 'Equity':
            # Drawings is contra-equity (debit balance, tracked as positive in balance)
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
    
    # Calculate Total Assets
    for name, data in ledger.items():
        acct_type = data['type']
        balance = data['balance']
        
        if acct_type == 'Asset':
            # Assets normally have a debit balance
            # FIX 1: Exclude Accumulated Depreciation (contra-asset) from being added directly. 
            if name != 'Accumulated Depreciation':
                assets += balance
            
    # FIX for Bank Overdraft: If Bank is negative (liability), subtract the absolute value from assets.
    if bank_balance < 0:
        assets += bank_balance # bank_balance is negative, so this subtracts it.
        
    # Calculate Total Liabilities
    for name, data in ledger.items():
        acct_type = data['type']
        balance = data['balance']
        
        if acct_type == 'Liability':
            # Liabilities normally have a credit balance (positive in ledger)
            liabilities += balance
            
    # Add Bank Overdraft if Bank balance is negative (as a liability)
    if bank_balance < 0:
        liabilities += abs(bank_balance)
        
    # Calculate Total Equity (Capital + Retained Earnings + Net Income - Contra-Equity)
    capital = ledger.get('Capital', {'balance': 0.0})['balance']
    drawings = ledger.get('Drawings', {'balance': 0.0})['balance'] 
    retained_earnings = ledger.get('Retained Earnings', {'balance': 0.0})['balance']
    treasury_stock = ledger.get('Treasury Stock', {'balance': 0.0})['balance'] # Contra Equity
    
    # Final Equity = Capital (Credit) + Retained Earnings (Prior Period) + Net Income (Credit/Increase) - Drawings (Debit/Decrease) - Treasury Stock (Debit/Decrease)
    final_equity = (capital + retained_earnings + net_income) - drawings - treasury_stock

    total_equity_liab = liabilities + final_equity
    
    # Check balance: Assets MUST equal Liabilities + Equity
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
        is_debit_type = (acct_type in ['Asset', 'Expense'] or name in ['Drawings', 'COGS', 'Loss on Sale', 'Treasury Stock'])
        
        # Only include accounts that have a significant activity balance
        if abs(balance) > 0.005: 
            
            # This is the logic for how a final balance is placed on the TB
            if is_debit_type:
                # If Debit-normal type: Debit column if balance is positive (Debit)
                debit_amount = max(0.0, balance)
                credit_amount = max(0.0, -balance)
            else:
                # If Credit-normal type: Credit column if balance is positive (Credit)
                credit_amount = max(0.0, balance)
                debit_amount = max(0.0, -balance)
            
            tb_debits += debit_amount
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
        'balance_sheet': {'assets': assets, 'liabilities': liabilities, 'equity': final_equity, 'total_eq_liab': total_equity_liab, 'is_balanced': is_balanced},
        'trial_balance': {'accounts': trial_balance_accounts, 'total_debits': tb_debits, 'total_credits': tb_credits, 'is_balanced': tb_balanced},
        'type_summary': type_summary # Add summary data for charts
    }


@app.route('/financial_reports')
def financial_reports():
    data = generate_financials()
    return render_template('financial_reports.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)