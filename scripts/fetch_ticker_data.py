import json
import yfinance as yf
from datetime import datetime, timedelta
import os
import pytz
import time
import argparse
import pandas as pd

def fill_date_gaps(ticker_records):
    """
    Fill missing dates (weekends/holidays) with the last known price for each ticker
    """
    if not ticker_records:
        return ticker_records
    
    # Group by ticker
    ticker_groups = {}
    for record in ticker_records:
        ticker = record['ticker']
        if ticker not in ticker_groups:
            ticker_groups[ticker] = []
        ticker_groups[ticker].append(record)
    
    filled_records = []
    
    for ticker, records in ticker_groups.items():
        # Sort by date
        records.sort(key=lambda x: x['date'])
        
        if not records:
            continue
            
        # Get date range
        start_date = datetime.strptime(records[0]['date'], '%Y-%m-%d')
        end_date = datetime.strptime(records[-1]['date'], '%Y-%m-%d')
        
        # Create a mapping of existing dates to prices
        existing_dates = {record['date']: record['price'] for record in records}
        
        # Fill in missing dates
        current_date = start_date
        last_price = records[0]['price']
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            
            if date_str in existing_dates:
                # Use actual price and update last_price
                price = existing_dates[date_str]
                last_price = price
            else:
                # Use last known price for missing date
                price = last_price
            
            filled_records.append({
                'ticker': ticker,
                'date': date_str,
                'price': price
            })
            
            current_date += timedelta(days=1)
    
    # Sort final records by ticker then date
    filled_records.sort(key=lambda x: (x['ticker'], x['date']))
    return filled_records

def get_current_tickers_from_balances(input_file='data/account_balances.json'):
    """
    Get the current unique tickers from account_balances.json
    Since the file only contains first-of-month data, we'll use the most recent month's data
    """
    with open(input_file, 'r') as f:
        balances_data = json.load(f)
    
    if not balances_data:
        return []
    
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
                    date_obj = datetime(int(year), int(month), int(day))
                    dated_records.append((date_obj, record))
        except ValueError:
            continue
    
    if not dated_records:
        return []
    
    # Find the most recent date
    most_recent_date = max(dated_records, key=lambda x: x[0])[0]
    
    # Get all records from the most recent month
    recent_records = [record for date_obj, record in dated_records if date_obj == most_recent_date]
    
    # Extract unique tickers, excluding Cash and Fund: entries
    unique_tickers = set()
    for record in recent_records:
        ticker = record['ticker']
        # Skip Cash and Fund entries - these represent dollar values, not share prices
        if ticker != 'Cash' and not ticker.startswith('Fund: '):
            unique_tickers.add(ticker)
    
    return sorted(list(unique_tickers))

def get_current_tickers_from_unvested(input_file='data/unvested_balances.json'):
    """
    Get the current unique tickers from unvested_balances.json
    Since the file only contains first-of-month data, we'll use the most recent month's data
    """
    if not os.path.exists(input_file):
        return []
    
    with open(input_file, 'r') as f:
        unvested_data = json.load(f)
    
    if not unvested_data:
        return []
    
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
                    date_obj = datetime(int(year), int(month), int(day))
                    dated_records.append((date_obj, record))
        except ValueError:
            continue
    
    if not dated_records:
        return []
    
    # Find the most recent date
    most_recent_date = max(dated_records, key=lambda x: x[0])[0]
    
    # Get all records from the most recent month
    recent_records = [record for date_obj, record in dated_records if date_obj == most_recent_date]
    
    # Extract unique tickers
    unique_tickers = set()
    for record in recent_records:
        ticker = record['ticker']
        unique_tickers.add(ticker)
    
    return sorted(list(unique_tickers))

def check_missing_ticker_data(tickers, target_date, existing_data):
    """
    Check which tickers are missing data for the target date
    """
    target_date_str = target_date.strftime('%Y-%m-%d')
    
    # Get existing data for target date
    existing_tickers_for_date = set()
    for record in existing_data:
        if record['date'] == target_date_str:
            existing_tickers_for_date.add(record['ticker'])
    
    # Find missing tickers
    missing_tickers = [ticker for ticker in tickers if ticker not in existing_tickers_for_date]
    return missing_tickers

def fetch_ticker_data_with_retry(tickers, start_date, end_date, max_retries=3):
    """Fetch ticker data with retry logic for failed tickers"""
    
    all_ticker_data = []
    failed_tickers = []
    
    print(f"Fetching data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    for attempt in range(max_retries):
        if attempt > 0:
            print(f"\n=== RETRY ATTEMPT {attempt + 1}/{max_retries} ===")
            print(f"Retrying {len(tickers)} tickers...")
            time.sleep(2)  # Wait 2 seconds between retries
        
        current_failed = []
        current_success = []
        
        # Fetch data for each ticker
        for i, ticker in enumerate(tickers):
            print(f"Fetching data for {ticker} ({i+1}/{len(tickers)})...")
            
            try:
                # Create yfinance ticker object
                ticker_obj = yf.Ticker(ticker)
                
                # Get historical data for the specific date range
                hist_data = ticker_obj.history(start=start_date, end=end_date + timedelta(days=1), auto_adjust=True)
                
                if hist_data.empty:
                    print(f"  No data found for {ticker}")
                    current_failed.append(ticker)
                    continue
                
                # Add daily price data as individual records
                ticker_records = []
                for date, row in hist_data.iterrows():
                    # Only include dates within our target range
                    # Convert pandas Timestamp to naive datetime for comparison
                    date_obj = date.to_pydatetime()
                    # Remove timezone info if present to make it naive
                    if date_obj.tzinfo is not None:
                        date_obj = date_obj.replace(tzinfo=None)
                    
                    if start_date <= date_obj <= end_date:
                        price_record = {
                            'ticker': ticker,
                            'date': date.strftime('%Y-%m-%d'),
                            'price': round(float(row['Close']), 4)
                        }
                        ticker_records.append(price_record)
                
                all_ticker_data.extend(ticker_records)
                current_success.append(ticker)
                print(f"  Successfully fetched {len(ticker_records)} days of data")
                
            except Exception as e:
                print(f"  Error fetching data for {ticker}: {str(e)}")
                current_failed.append(ticker)
        
        # Update the list of tickers to retry
        tickers = current_failed
        failed_tickers = current_failed
        
        # If all tickers succeeded, break out of retry loop
        if not current_failed:
            print(f"All tickers fetched successfully!")
            break
        
        print(f"Attempt {attempt + 1}: {len(current_success)} succeeded, {len(current_failed)} failed")
    
    return all_ticker_data, failed_tickers

def load_existing_ticker_data():
    """Load existing ticker data and get the last fetched date"""
    ticker_file = 'data/tickers.json'
    
    if not os.path.exists(ticker_file):
        return [], None
    
    with open(ticker_file, 'r') as f:
        existing_data = json.load(f)
    
    if not existing_data:
        return [], None
    
    # Find the last fetched date
    last_date = max(record['date'] for record in existing_data)
    last_date = datetime.strptime(last_date, '%Y-%m-%d')
    
    return existing_data, last_date
    """Load existing ticker data and get the last fetched date"""
    ticker_file = 'data/tickers.json'
    
    if not os.path.exists(ticker_file):
        return [], None
    
    with open(ticker_file, 'r') as f:
        existing_data = json.load(f)
    
    if not existing_data:
        return [], None
    
    # Find the last fetched date
    last_date = max(record['date'] for record in existing_data)
    last_date = datetime.strptime(last_date, '%Y-%m-%d')
    
    return existing_data, last_date

def fetch_ticker_data(input_file='data/account_balances.json', output_file='data/tickers.json', period='2y'):
    """
    Fetch historical stock data for unique tickers from account_balances.json and unvested_balances.json 
    with incremental updates and retry logic
    
    Args:
        input_file: Path to account balances JSON file
        output_file: Path to output ticker data JSON file
        period: Period for historical data ('1y', '2y', '5y', 'max', etc.) - used only for initial fetch
    """
    
    # Get current unique tickers from account balances (most recent month)
    account_tickers = get_current_tickers_from_balances(input_file)
    
    # Get current unique tickers from unvested balances (most recent month)
    unvested_tickers = get_current_tickers_from_unvested('data/unvested_balances.json')
    
    # Combine and deduplicate tickers
    unique_tickers = sorted(list(set(account_tickers + unvested_tickers)))
    
    if not unique_tickers:
        print("No tickers found in account balances or unvested balances files!")
        return
    
    print(f"Found {len(account_tickers)} tickers from account balances: {account_tickers}")
    print(f"Found {len(unvested_tickers)} tickers from unvested balances: {unvested_tickers}")
    print(f"Total unique tickers to fetch: {len(unique_tickers)} - {unique_tickers}")
    
    # Load existing ticker data
    print("Loading existing ticker data...")
    existing_data, last_fetched_date = load_existing_ticker_data()
    
    # Determine date range to fetch
    today = datetime.now().date()
    
    # Check if we should fetch today's data (only after 4 PM PST)
    pst_tz = pytz.timezone('US/Pacific')
    current_pst = datetime.now(pst_tz)
    market_close_time = current_pst.replace(hour=16, minute=0, second=0, microsecond=0)  # 4 PM PST
    
    # If it's before 4 PM PST today, don't fetch today's data
    fetch_today = current_pst >= market_close_time
    if not fetch_today:
        today = today - timedelta(days=1)  # Use yesterday as the latest date
        print(f"Current time: {current_pst.strftime('%I:%M %p PST')}")
        print(f"Market closes at 4:00 PM PST - using {today} as latest date")
    else:
        print(f"Current time: {current_pst.strftime('%I:%M %p PST')}")
        print(f"After market close - including today's data: {today}")
    
    # Check if we need to fetch data for today for all current tickers
    missing_tickers_today = check_missing_ticker_data(unique_tickers, datetime.combine(today, datetime.min.time()), existing_data)
    
    if missing_tickers_today:
        print(f"\nMissing ticker data for today ({today}): {missing_tickers_today}")
        
        # Fetch missing data for today with retry logic
        print(f"Fetching missing data for {len(missing_tickers_today)} tickers for today...")
        today_data, failed_today = fetch_ticker_data_with_retry(
            missing_tickers_today,
            datetime.combine(today, datetime.min.time()),
            datetime.combine(today, datetime.min.time()),
            max_retries=3
        )
        
        if failed_today:
            print(f"Warning: Failed to fetch data for {len(failed_today)} tickers after 3 retries: {failed_today}")
        
        existing_data.extend(today_data)
    
    # Determine if we need to do a regular incremental update
    if last_fetched_date is not None:
        # Incremental update: fetch from day after last fetched date
        start_date = (last_fetched_date + timedelta(days=1)).date()
        print(f"Last fetched date: {last_fetched_date.strftime('%Y-%m-%d')}")
        
        if start_date <= today:
            print(f"Performing incremental update from {start_date} to {today}")
            
            # Fetch incremental data with retry logic
            new_data, failed_tickers = fetch_ticker_data_with_retry(
                unique_tickers, 
                datetime.combine(start_date, datetime.min.time()),
                datetime.combine(today, datetime.min.time()),
                max_retries=3
            )
            
            # Combine with existing data
            all_data = existing_data + new_data
        else:
            print("Ticker data is already up to date!")
            all_data = existing_data
            failed_tickers = []
    else:
        # Initial fetch: use the period parameter
        if period == 'max':
            start_date = datetime(2020, 1, 1).date()  # Reasonable start for 'max'
        elif period.endswith('y'):
            years = int(period[:-1])
            start_date = (datetime.now() - timedelta(days=365 * years)).date()
        else:
            # Default to 2 years if period format is unclear
            start_date = (datetime.now() - timedelta(days=365 * 2)).date()
        
        print("Performing initial fetch...")
        print(f"Fetching data from {start_date} to {today}")
        
        # Fetch data with retry logic
        new_data, failed_tickers = fetch_ticker_data_with_retry(
            unique_tickers, 
            datetime.combine(start_date, datetime.min.time()),
            datetime.combine(today, datetime.min.time()),
            max_retries=3
        )
        
        # Combine with existing data
        all_data = existing_data + new_data
    
    # Fill date gaps for the complete dataset
    print(f"\nFilling date gaps for continuous price data...")
    all_data = fill_date_gaps(all_data)
    
    # Write results to JSON file
    with open(output_file, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    # Print summary
    successful_tickers = len(unique_tickers) - len(failed_tickers)
    print(f"\n=== SUMMARY ===")
    print(f"Successfully fetched data for {successful_tickers} tickers")
    print(f"Failed to fetch data for {len(failed_tickers)} tickers")
    
    if failed_tickers:
        print(f"Failed tickers: {failed_tickers}")
    
    print(f"Data saved to: {output_file}")
    print(f"Total price records saved: {len(all_data)}")

def backfill_ticker_data(ticker_symbol, start_date_str, output_file='data/tickers.json'):
    """
    Backfill historical data for a specific ticker from a given date to today
    
    Args:
        ticker_symbol: The ticker symbol to fetch data for
        start_date_str: Start date in format 'M/D/YY' or 'YYYY-MM-DD'
        output_file: Path to output ticker data JSON file
    """
    
    # Parse the start date
    try:
        # Try M/D/YY format first (like 4/13/25)
        if '/' in start_date_str:
            parts = start_date_str.split('/')
            if len(parts) == 3:
                month, day, year = parts
                if len(year) == 2:
                    year = '20' + year
                start_date = datetime(int(year), int(month), int(day))
        else:
            # Try YYYY-MM-DD format
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    except ValueError as e:
        print(f"Error parsing date '{start_date_str}': {e}")
        print("Please use format M/D/YY (e.g., 4/13/25) or YYYY-MM-DD")
        return
    
    # Determine end date (today, but respect market hours)
    today = datetime.now().date()
    
    # Check if we should include today's data (only after 4 PM PST)
    pst_tz = pytz.timezone('US/Pacific')
    current_pst = datetime.now(pst_tz)
    market_close_time = current_pst.replace(hour=16, minute=0, second=0, microsecond=0)  # 4 PM PST
    
    # If it's before 4 PM PST today, don't include today's data
    fetch_today = current_pst >= market_close_time
    if not fetch_today:
        today = today - timedelta(days=1)  # Use yesterday as the latest date
        print(f"Current time: {current_pst.strftime('%I:%M %p PST')}")
        print(f"Market closes at 4:00 PM PST - fetching through {today}")
    else:
        print(f"Current time: {current_pst.strftime('%I:%M %p PST')}")
        print(f"After market close - including today's data: {today}")
    
    end_date = datetime.combine(today, datetime.min.time())
    start_datetime = datetime.combine(start_date.date(), datetime.min.time())
    
    print(f"\nBackfilling data for {ticker_symbol}")
    print(f"Date range: {start_datetime.date()} to {end_date.date()}")
    
    # Load existing ticker data
    existing_data = []
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            existing_data = json.load(f)
    
    # Remove any existing data for this ticker in the date range
    date_range = pd.date_range(start=start_datetime, end=end_date, freq='D')
    target_dates = set(date.strftime('%Y-%m-%d') for date in date_range)
    
    print(f"Removing existing data for {ticker_symbol} in date range...")
    existing_data = [record for record in existing_data 
                     if not (record['ticker'] == ticker_symbol and record['date'] in target_dates)]
    
    # Fetch new data with retry logic
    new_data, failed_tickers = fetch_ticker_data_with_retry(
        [ticker_symbol], 
        start_datetime,
        end_date,
        max_retries=3
    )
    
    if failed_tickers:
        print(f"Failed to fetch data for {ticker_symbol}")
        return
    
    # Fill date gaps for the new data
    print(f"Filling date gaps for {ticker_symbol}...")
    new_data = fill_date_gaps(new_data)
    
    # Combine with existing data and sort
    all_data = existing_data + new_data
    all_data.sort(key=lambda x: (x['ticker'], x['date']))
    
    # Save updated data
    with open(output_file, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print(f"\n=== BACKFILL SUMMARY ===")
    print(f"Successfully backfilled data for {ticker_symbol}")
    print(f"Date range: {start_datetime.date()} to {end_date.date()}")
    print(f"New records added: {len(new_data)}")
    print(f"Total records in file: {len(all_data)}")
    print(f"Data saved to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch ticker data with optional backfill for specific ticker")
    parser.add_argument('--ticker', type=str, help="Specific ticker symbol to backfill")
    parser.add_argument('--date', type=str, help="Start date for backfill (M/D/YY or YYYY-MM-DD format)")
    
    args = parser.parse_args()
    
    if args.ticker and args.date:
        # Backfill mode for specific ticker
        backfill_ticker_data(args.ticker, args.date)
    elif args.ticker or args.date:
        print("Error: Both --ticker and --date must be provided for backfill mode")
        print("Usage: python fetch_ticker_data.py --ticker CART --date 4/13/25")
    else:
        # Regular mode - fetch all tickers
        fetch_ticker_data()