import json
import pandas as pd
from datetime import timedelta
from datetime import datetime
import os
import subprocess
import pytz
import time
import argparse
import numpy as np

def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

def load_account_data():
    """Load account balances data"""
    with open('data/account_balances.json', 'r') as f:
        account_balances = json.load(f)
    
    df_accounts = pd.DataFrame(account_balances)
    # Fix date parsing - the JSON has dates in M/D/YY format
    df_accounts['date'] = pd.to_datetime(df_accounts['date'], format='%m/%d/%y')
    
    return df_accounts

def load_unvested_data():
    """Load unvested balances data"""
    unvested_file = 'data/unvested_balances.json'
    
    if not os.path.exists(unvested_file):
        print(f"Warning: {unvested_file} not found. Returning empty unvested data.")
        return pd.DataFrame()
    
    with open(unvested_file, 'r') as f:
        unvested_balances = json.load(f)
    
    if not unvested_balances:
        print("Warning: unvested_balances.json is empty. Returning empty unvested data.")
        return pd.DataFrame()
    
    df_unvested = pd.DataFrame(unvested_balances)
    # Fix date parsing - the JSON has dates in M/D/YY format
    df_unvested['date'] = pd.to_datetime(df_unvested['date'], format='%m/%d/%y')
    
    return df_unvested

def load_ticker_data():
    """Load ticker prices data"""
    ticker_file = 'data/tickers.json'
    
    if not os.path.exists(ticker_file):
        print(f"Warning: {ticker_file} not found. Returning empty ticker data.")
        return pd.DataFrame()
    
    with open(ticker_file, 'r') as f:
        ticker_prices = json.load(f)
    
    if not ticker_prices:
        print("Warning: tickers.json is empty. Returning empty ticker data.")
        return pd.DataFrame()
    
    df_tickers = pd.DataFrame(ticker_prices)
    df_tickers['date'] = pd.to_datetime(df_tickers['date'])
    
    # Create a pivot table for easier lookup
    ticker_pivot = df_tickers.pivot(index='date', columns='ticker', values='price')
    
    return ticker_pivot

def load_existing_balances():
    """Load existing precomputed balances and get the last calculated date"""
    balances_file = 'data/daily_balances.json'
    
    if not os.path.exists(balances_file):
        return [], None
    
    with open(balances_file, 'r') as f:
        existing_balances = json.load(f)
    
    if not existing_balances:
        return [], None
    
    # Find the last calculated date
    last_date = max(record['date'] for record in existing_balances)
    last_date = pd.to_datetime(last_date)
    
    return existing_balances, last_date

def get_shares_for_date(df_accounts, account, ticker, target_date):
    """Get the number of shares for a specific account/ticker on a given date"""
    
    # Filter for the specific account and ticker
    account_ticker_data = df_accounts[
        (df_accounts['account'] == account) & 
        (df_accounts['ticker'] == ticker)
    ].copy()
    
    if account_ticker_data.empty:
        return 0
    
    # Get the target month/year
    target_month_year = target_date.to_period('M')
    
    # Find records in the same month as the target date
    same_month_records = account_ticker_data[
        account_ticker_data['date'].dt.to_period('M') == target_month_year
    ]
    
    if not same_month_records.empty:
        # Use the record from the same month (should be the 1st of the month)
        most_recent = same_month_records.loc[same_month_records['date'].idxmax()]
        if ticker.startswith('Fund: ') and account == 'Fidelity - Amazon':
            print(f"  Found matching record: {most_recent['shares']} shares on {most_recent['date'].date()}")
        return most_recent['shares']
    
    # If no record in the same month, return 0 (no position)
    if ticker.startswith('Fund: ') and account == 'Fidelity - Amazon':
        print(f"  No matching record found for {target_month_year}")
    return 0

def get_unvested_shares_for_date(df_unvested, ticker, target_date):
    """Get the number of unvested shares for a specific ticker on a given date"""
    
    if df_unvested.empty:
        return 0
    
    # Filter for the specific ticker
    ticker_data = df_unvested[df_unvested['ticker'] == ticker].copy()
    
    if ticker_data.empty:
        return 0
    
    # Get the target month/year
    target_month_year = target_date.to_period('M')
    
    # Find records in the same month as the target date
    same_month_records = ticker_data[
        ticker_data['date'].dt.to_period('M') == target_month_year
    ]
    
    if not same_month_records.empty:
        # Use the record from the same month (should be the 1st of the month)
        most_recent = same_month_records.loc[same_month_records['date'].idxmax()]
        return most_recent['shares']
    
    # If no record in the same month, return 0 (no unvested position)
    return 0

def calculate_balances_for_date_range(df_accounts, ticker_pivot, start_date, end_date):
    """Calculate daily balances for a specific date range"""
    
    # Load unvested data
    df_unvested = load_unvested_data()
    
    # Get unique accounts and tickers from regular holdings
    unique_accounts = df_accounts['account'].unique()
    unique_tickers = df_accounts['ticker'].unique()
    
    # Get unique unvested tickers
    unvested_tickers = []
    if not df_unvested.empty:
        unvested_tickers = df_unvested['ticker'].unique()
    
    print(f"Unique accounts: {unique_accounts}")
    print(f"Unique tickers: {unique_tickers}")
    print(f"Unique unvested tickers: {unvested_tickers}")
    
    # Create date range
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    results = []
    total_days = len(date_range)
    
    print(f"Calculating balances for {total_days} days from {start_date.date()} to {end_date.date()}")
    
    for day_idx, date in enumerate(date_range):
        if day_idx % 10 == 0 or day_idx == total_days - 1:
            print(f"Processing day {day_idx + 1}/{total_days}: {date.date()}")
        
        # Process regular account holdings
        for account in unique_accounts:
            for ticker in unique_tickers:
                # Get shares for this date
                shares = get_shares_for_date(df_accounts, account, ticker, date)
                
                if shares == 0:
                    continue
             
                # Calculate value
                if ticker == 'Cash' or ticker.startswith('Fund: '):
                    # For Cash and Fund entries, shares represent total value
                    value = shares
                    price = 1.0
                else:
                    # Look up price from ticker data
                    if ticker_pivot.empty:
                        # Skip non-cash/fund tickers if no ticker data is available
                        continue
                    elif ticker in ticker_pivot.columns and date in ticker_pivot.index:
                        price = ticker_pivot.loc[date, ticker]
                        if pd.isna(price):
                            continue
                        value = shares * price
                    else:
                        continue
                
                results.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'account': account,
                    'ticker': ticker,
                    'shares': shares,
                    'price': price,
                    'value': value
                })
        
        # Process unvested holdings
        for ticker in unvested_tickers:
            # Get unvested shares for this date
            shares = get_unvested_shares_for_date(df_unvested, ticker, date)
            
            if shares == 0:
                continue
            
            # Look up price from ticker data
            if ticker_pivot.empty:
                # Skip if no ticker data is available
                continue
            elif ticker in ticker_pivot.columns and date in ticker_pivot.index:
                price = ticker_pivot.loc[date, ticker]
                if pd.isna(price):
                    continue
                # Calculate gross value first
                gross_value = shares * price
                # Reduce by 30% for taxes on unvested RSU
                value = gross_value * 0.7
            else:
                continue
            
            results.append({
                'date': date.strftime('%Y-%m-%d'),
                'account': 'Unvested RSU',  # Special account name for unvested shares
                'ticker': ticker,
                'shares': shares,
                'price': price,
                'value': value
            })
    
    return results

def calculate_balances_for_account_and_date_range(df_accounts, ticker_pivot, account_name, start_date, end_date):
    """Calculate daily balances for a specific account and date range"""
    
    # Load unvested data
    df_unvested = load_unvested_data()
    
    # Create date range
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    results = []
    total_days = len(date_range)
    
    print(f"Calculating balances for account '{account_name}' for {total_days} days from {start_date.date()} to {end_date.date()}")
    
    for day_idx, date in enumerate(date_range):
        if day_idx % 10 == 0 or day_idx == total_days - 1:
            print(f"Processing day {day_idx + 1}/{total_days}: {date.date()}")
        
        if account_name == "Unvested RSU":
            # Process unvested holdings
            if not df_unvested.empty:
                unvested_tickers = df_unvested['ticker'].unique()
                for ticker in unvested_tickers:
                    # Get unvested shares for this date
                    shares = get_unvested_shares_for_date(df_unvested, ticker, date)
                    
                    if shares == 0:
                        continue
                    
                    # Look up price from ticker data
                    if ticker_pivot.empty:
                        # Skip if no ticker data is available
                        continue
                    elif ticker in ticker_pivot.columns and date in ticker_pivot.index:
                        price = ticker_pivot.loc[date, ticker]
                        if pd.isna(price):
                            continue
                        # Calculate gross value first
                        gross_value = shares * price
                        # Reduce by 30% for taxes on unvested RSU
                        value = gross_value * 0.7
                    else:
                        continue
                    
                    results.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'account': account_name,
                        'ticker': ticker,
                        'shares': float(shares),  # Convert to native Python float
                        'price': float(price),    # Convert to native Python float
                        'value': float(value)     # Convert to native Python float
                    })
        else:
            # Process regular account holdings
            if not df_accounts.empty:
                # Filter for the specific account
                account_data = df_accounts[df_accounts['account'] == account_name]
                if not account_data.empty:
                    unique_tickers = account_data['ticker'].unique()
                    for ticker in unique_tickers:
                        # Get shares for this date
                        shares = get_shares_for_date(df_accounts, account_name, ticker, date)
                        
                        if shares == 0:
                            continue
                     
                        # Calculate value
                        if ticker == 'Cash' or ticker.startswith('Fund: '):
                            # For Cash and Fund entries, shares represent total value
                            value = shares
                            price = 1.0
                        else:
                            # Look up price from ticker data
                            if ticker_pivot.empty:
                                # Skip non-cash/fund tickers if no ticker data is available
                                continue
                            elif ticker in ticker_pivot.columns and date in ticker_pivot.index:
                                price = ticker_pivot.loc[date, ticker]
                                if pd.isna(price):
                                    continue
                                value = shares * price
                            else:
                                continue
                        
                        results.append({
                            'date': date.strftime('%Y-%m-%d'),
                            'account': account_name,
                            'ticker': ticker,
                            'shares': float(shares),  # Convert to native Python float
                            'price': float(price),    # Convert to native Python float
                            'value': float(value)     # Convert to native Python float
                        })
    
    return results

def get_current_tickers_from_balances():
    """
    Get the current unique tickers from account_balances.json and unvested_balances.json
    Since the files only contain first-of-month data, we'll use the most recent month's data
    """
    # Get tickers from account balances
    account_tickers = set()
    try:
        with open('data/account_balances.json', 'r') as f:
            balances_data = json.load(f)
        
        if balances_data:
            # Parse all dates and find the most recent month
            dated_records = []
            for record in balances_data:
                # Parse the date format (assuming it's M/D/YY format like "7/1/25")
                date_str = record['date']
                try:
                    # Try different date formats
                    if '/' in date_str:
                        parts = date_str.split('/')
                        if len(parts) == 3:
                            month, day, year = parts
                            # Handle 2-digit year
                            if len(year) == 2:
                                year = '20' + year
                            date_obj = pd.to_datetime(f"{year}-{month}-{day}")
                            dated_records.append((date_obj, record))
                except ValueError:
                    continue
            
            if dated_records:
                # Find the most recent date
                most_recent_date = max(dated_records, key=lambda x: x[0])[0]
                
                # Get all records from the most recent month
                recent_records = [record for date_obj, record in dated_records if date_obj == most_recent_date]
                
                # Extract unique tickers, excluding Cash and Fund: entries for price checking
                for record in recent_records:
                    ticker = record['ticker']
                    # Skip Cash and Fund entries - these represent dollar values, not share prices
                    if ticker != 'Cash' and not ticker.startswith('Fund: '):
                        account_tickers.add(ticker)
    except FileNotFoundError:
        print("Warning: account_balances.json not found")
    
    # Get tickers from unvested balances
    unvested_tickers = set()
    try:
        with open('data/unvested_balances.json', 'r') as f:
            unvested_data = json.load(f)
        
        if unvested_data:
            # Parse all dates and find the most recent month
            dated_records = []
            for record in unvested_data:
                # Parse the date format (assuming it's M/D/YY format like "7/1/25")
                date_str = record['date']
                try:
                    # Try different date formats
                    if '/' in date_str:
                        parts = date_str.split('/')
                        if len(parts) == 3:
                            month, day, year = parts
                            # Handle 2-digit year
                            if len(year) == 2:
                                year = '20' + year
                            date_obj = pd.to_datetime(f"{year}-{month}-{day}")
                            dated_records.append((date_obj, record))
                except ValueError:
                    continue
            
            if dated_records:
                # Find the most recent date
                most_recent_date = max(dated_records, key=lambda x: x[0])[0]
                
                # Get all records from the most recent month
                recent_records = [record for date_obj, record in dated_records if date_obj == most_recent_date]
                
                # Extract unique tickers
                for record in recent_records:
                    ticker = record['ticker']
                    unvested_tickers.add(ticker)
    except FileNotFoundError:
        print("Warning: unvested_balances.json not found")
    
    # Combine and return all unique tickers
    all_tickers = account_tickers.union(unvested_tickers)
    return sorted(list(all_tickers))

def check_missing_ticker_data_for_today(tickers, ticker_pivot, target_date):
    """
    Check which tickers are missing price data for the target date
    """
    if ticker_pivot.empty:
        return tickers
    
    missing_tickers = []
    for ticker in tickers:
        if ticker not in ticker_pivot.columns or target_date not in ticker_pivot.index:
            missing_tickers.append(ticker)
        elif pd.isna(ticker_pivot.loc[target_date, ticker]):
            missing_tickers.append(ticker)
    
    return missing_tickers

def check_missing_balance_data_for_today(existing_balances, target_date):
    """
    Check if we have complete balance data for the target date
    """
    target_date_str = target_date.strftime('%Y-%m-%d')
    
    # Check if we have any balance records for the target date
    existing_dates = set(record['date'] for record in existing_balances)
    
    return target_date_str not in existing_dates

def update_ticker_data_with_retry(max_retries=3):
    """Update ticker data by running the fetch script with retry logic"""
    
    for attempt in range(max_retries):
        if attempt > 0:
            print(f"\n=== RETRY ATTEMPT {attempt + 1}/{max_retries} for ticker data update ===")
            time.sleep(2)  # Wait 2 seconds between retries
        
        print("Updating ticker data...")
        try:
            result = subprocess.run(['python', 'scripts/fetch_ticker_data.py'], 
                                  capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode != 0:
                print(f"Error updating ticker data (attempt {attempt + 1}): {result.stderr}")
                if attempt == max_retries - 1:
                    return False
            else:
                print("Ticker data updated successfully")
                return True
        except Exception as e:
            print(f"Error running ticker fetch script (attempt {attempt + 1}): {str(e)}")
            if attempt == max_retries - 1:
                return False
    
    return False

def update_daily_balances(target_end_date=None, target_account=None):
    """
    Update daily balances with incremental calculation and retry logic.
    If target_end_date is provided, recalculate balances up to that date (inclusive).
    If target_account is provided, calculate balances only for that specific account.
    Override any existing entries in daily_balances.json for the recalculated range.
    """
    # Get current tickers from account balances
    current_tickers = get_current_tickers_from_balances()
    # Load existing data
    existing_balances, last_calculated_date = load_existing_balances()
    
    # Set up time variables
    pst_tz = pytz.timezone('US/Pacific')
    current_pst = pd.Timestamp.now(tz=pst_tz)
    market_close_time = current_pst.replace(hour=16, minute=0, second=0, microsecond=0)  # 4 PM PST
    today = pd.to_datetime('today').normalize()
    
    # Determine the date range to calculate
    if target_account:
        # For account-specific calculations, use provided date as start date
        if target_end_date:
            try:
                start_date = pd.to_datetime(target_end_date)
                print(f"Using provided start date for account calculation: {start_date.date()}")
            except Exception:
                print(f"Invalid date format for --date: {target_end_date}. Using default start date.")
                start_date = pd.to_datetime('2024-01-01')
        else:
            start_date = pd.to_datetime('2024-01-01')
        
        # For account-specific calculations, always calculate to today
        include_today = current_pst >= market_close_time
        if not include_today:
            end_date = today - timedelta(days=1)
            print(f"Current time: {current_pst.strftime('%I:%M %p PST')}")
            print(f"Market closes at 4:00 PM PST - calculating through {end_date.date()}")
        else:
            end_date = today
            print(f"Current time: {current_pst.strftime('%I:%M %p PST')}")
            print(f"After market close - including today's data: {end_date.date()}")
    else:
        # For full recalculation, use default behavior
        start_date = pd.to_datetime('2024-01-01')
        
        # If a target_end_date is provided, use it; otherwise, use today (possibly yesterday if before market close)
        if target_end_date:
            try:
                end_date = pd.to_datetime(target_end_date)
            except Exception:
                print(f"Invalid date format for --date: {target_end_date}. Using today's date.")
                end_date = today
        else:
            include_today = current_pst >= market_close_time
            if not include_today:
                end_date = today - timedelta(days=1)
                print(f"Current time: {current_pst.strftime('%I:%M %p PST')}")
                print(f"Market closes at 4:00 PM PST - calculating through {end_date.date()}")
            else:
                end_date = today
                print(f"Current time: {current_pst.strftime('%I:%M %p PST')}")
                print(f"After market close - including today's data: {end_date.date()}")
    
    # Check if we need today's data
    need_today_data = check_missing_balance_data_for_today(existing_balances, end_date)
    if need_today_data and current_tickers:
        print(f"\nChecking ticker data completeness for {end_date.date()}...")
        ticker_update_success = update_ticker_data_with_retry(max_retries=3)
        if not ticker_update_success:
            print("Warning: Failed to update ticker data after retries, proceeding with existing data...")
        ticker_pivot = load_ticker_data()
        missing_tickers_today = check_missing_ticker_data_for_today(current_tickers, ticker_pivot, end_date)
        if missing_tickers_today:
            print(f"Warning: Missing ticker data for {end_date.date()} for: {missing_tickers_today}")
            for retry in range(3):
                print(f"Retry {retry + 1}/3: Attempting to fetch missing ticker data...")
                if update_ticker_data_with_retry(max_retries=1):
                    ticker_pivot = load_ticker_data()
                    still_missing = check_missing_ticker_data_for_today(current_tickers, ticker_pivot, end_date)
                    if not still_missing:
                        print("All ticker data now complete!")
                        break
                    else:
                        print(f"Still missing: {still_missing}")
                        if retry < 2:
                            time.sleep(5)
                else:
                    print(f"Ticker update retry {retry + 1} failed")
                    if retry < 2:
                        time.sleep(5)
        else:
            print(f"All required ticker data is available for {end_date.date()}")
    else:
        if not update_ticker_data_with_retry(max_retries=3):
            print("Warning: Failed to update ticker data, proceeding with existing data...")
    
    # Load the final data for calculations
    df_accounts = load_account_data()
    ticker_pivot = load_ticker_data()
    
    # Calculate balances based on whether a specific account is requested
    if target_account:
        print(f"Calculating balances for account '{target_account}' from {start_date.date()} to {end_date.date()} (inclusive)")
        new_balances = calculate_balances_for_account_and_date_range(
            df_accounts, ticker_pivot, target_account, start_date, end_date
        )
        
        # Remove any existing balances for this account in the recalculated date range
        recalculated_dates = set(
            pd.date_range(start=start_date, end=end_date, freq='D').strftime('%Y-%m-%d')
        )
        filtered_existing = [rec for rec in existing_balances 
                           if not (rec['account'] == target_account and rec['date'] in recalculated_dates)]
        
        print(f"Removed {len(existing_balances) - len(filtered_existing)} existing records for account '{target_account}'")
    else:
        print(f"Recalculating balances for all accounts from {start_date.date()} to {end_date.date()} (inclusive)")
        new_balances = calculate_balances_for_date_range(
            df_accounts, ticker_pivot, start_date, end_date
        )
        
        # Remove any existing balances in the recalculated date range
        recalculated_dates = set(
            pd.date_range(start=start_date, end=end_date, freq='D').strftime('%Y-%m-%d')
        )
        filtered_existing = [rec for rec in existing_balances if rec['date'] not in recalculated_dates]
    
    all_balances = filtered_existing + new_balances
    
    # Save updated balances
    with open('data/daily_balances.json', 'w') as f:
        # Convert all numpy types to native Python types before JSON serialization
        serializable_balances = []
        for record in all_balances:
            serializable_record = {}
            for key, value in record.items():
                serializable_record[key] = convert_numpy_types(value)
            serializable_balances.append(serializable_record)
        json.dump(serializable_balances, f, indent=2)
    
    print(f"\n=== SUMMARY ===")
    if target_account:
        print(f"Recalculated {len(new_balances)} balance records for account '{target_account}'")
    else:
        print(f"Recalculated {len(new_balances)} balance records for all accounts")
    print(f"Total balance records: {len(all_balances)}")
    print(f"Data saved to: data/daily_balances.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recalculate daily balances up to a given date, optionally for a specific account.")
    parser.add_argument('--date', type=str, help="Date parameter: End date for full recalculation (YYYY-MM-DD), or start date when used with --account.")
    parser.add_argument('--account', type=str, help="Optional account name to calculate balances for (e.g., 'Vanguard', 'Unvested RSU'). When used with --date, date becomes the start date.")
    args = parser.parse_args()
    update_daily_balances(target_end_date=args.date, target_account=args.account)
