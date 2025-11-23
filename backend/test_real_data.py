"""
Real Data Testing for Forensic Analysis

This script tests the forensic analysis modules with real financial data
from public companies using the yfinance library.
"""
import os
import sys
import time
import random
import json
import requests
import yfinance as yf
import pandas as pd
import numpy as np
from functools import wraps, lru_cache
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure requests session with retries
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "POST"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

# Configure yfinance to use our session
# Note: pdr_override is not available in all yfinance versions
# yf.pdr_override()  # Removed as it's not available in current yfinance

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import forensic analysis modules
from src.analysis.forensic.benfords_law import benfords_law_analysis as analyze_benfords_law
from src.analysis.forensic.zscore import calculate_altman_zscore
from src.analysis.forensic.mscore import calculate_beneish_mscore
from src.analysis.forensic.ratios import FinancialRatios

def rate_limited(max_per_second, max_retries=3, initial_delay=1.0, max_delay=30.0):
    """Decorator to limit the number of API calls per second with exponential backoff."""
    min_interval = 1.0 / float(max_per_second)
    
    def decorate(func):
        last_time_called = 0.0
        
        @wraps(func)
        def rate_limited_function(*args, **kwargs):
            nonlocal last_time_called
            
            delay = initial_delay
            for attempt in range(max_retries + 1):
                try:
                    # Enforce rate limiting
                    elapsed = time.time() - last_time_called
                    left_to_wait = min_interval - elapsed
                    if left_to_wait > 0:
                        time.sleep(left_to_wait)
                    
                    last_time_called = time.time()
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    if attempt == max_retries:
                        print(f"Max retries ({max_retries}) reached. Giving up.")
                        raise
                        
                    if '429' in str(e) or 'Too Many Requests' in str(e):
                        wait_time = min(delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                        print(f"Rate limited. Waiting {wait_time:.1f} seconds before retry {attempt + 1}/{max_retries}...")
                        time.sleep(wait_time)
                        delay = min(delay * 2, max_delay)
                    else:
                        raise
            
        return rate_limited_function
    return decorate

@rate_limited(max_per_second=0.2, max_retries=5, initial_delay=2.0)  # More conservative rate limiting
def get_company_data(ticker: str, use_cache=True):
    """Fetch financial data for a given ticker.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT.NS', 'RELIANCE.NS', 'RELIANCE.BO')
        
    Returns:
        dict: Dictionary containing financial data or None if data cannot be fetched
    """
    original_ticker = ticker
    
    # Try different ticker formats
    ticker_formats = [
        ticker,  # Try as-is first
        f"{ticker}.NS",  # NSE (India)
        f"{ticker}.BO",  # BSE (India)
        f"{ticker}.NS" if not ticker.endswith(('.NS', '.BO')) else None,  # Add NS if no exchange
        f"{ticker}.BO" if not ticker.endswith(('.NS', '.BO')) else None,  # Add BO if no exchange
    ]
    
    # Try cached data first if available
    if use_cache:
        try:
            cached_data = _get_cached_data(original_ticker)
            if cached_data:
                print(f"Using cached data for {original_ticker}")
                return cached_data
        except Exception as e:
            print(f"Cache error: {e}")
    
    for t in ticker_formats:
        if t is None:
            continue
            
        try:
            print(f"Trying ticker: {t}")
            try:
                # Add a small random delay to avoid hitting rate limits
                time.sleep(random.uniform(2.0, 4.0))
                
                # Use session with retries
                company = yf.Ticker(t, session=session)
                
                # Try to get minimal info first
                info = company.info or {}
                
                # Check if we have minimal required info
                if info.get('regularMarketPrice') is not None:
                    ticker = t  # Update to the working ticker
                    print(f"Found data for ticker: {t}")
                    
                    # Get all data with error handling
                    data = {
                        'ticker': t,
                        'company': company,
                        'info': info,
                        'balance_sheet': _safe_get(company, 'balance_sheet'),
                        'income_stmt': _safe_get(company, 'income_stmt'),
                        'cash_flow': _safe_get(company, 'cash_flow'),
                        'quarterly_balance_sheet': _safe_get(company, 'quarterly_balance_sheet'),
                        'quarterly_income_stmt': _safe_get(company, 'quarterly_income_stmt'),
                        'quarterly_cash_flow': _safe_get(company, 'quarterly_cash_flow'),
                        'last_updated': datetime.now().isoformat()
                    }
                    
                    # Cache the successful response
                    _cache_data(original_ticker, data)
                    return data
            except Exception as e:
                print(f"Error with ticker {t}: {str(e)}")
                # Let the rate_limited decorator handle retries
                raise
                
        except Exception as e:
            print(f"Error with ticker {t}: {str(e)}")
            # If we get rate limited, wait longer before next attempt
            if '429' in str(e):
                wait_time = random.uniform(5.0, 10.0)
                print(f"Rate limited. Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
            continue
    else:
        error_msg = f"No data found for ticker: {original_ticker} (tried formats: {', '.join([t for t in ticker_formats if t])})"
        print(error_msg)
        
        # Try to return cached data if available, even if it's old
        try:
            cached_data = _get_cached_data(original_ticker, max_age_days=30)  # Accept up to 30-day old data
            if cached_data:
                print("Using cached data as fallback")
                return cached_data
        except Exception as e:
            print(f"Cache fallback failed: {e}")
        
        return None
    
    # Get financial statements with error handling
    try:
        # Try to get quarterly data first, if not available try annual
        for period in ['quarterly', 'annual']:
            try:
                income_stmt = company.income_stmt if period == 'annual' else company.quarterly_income_stmt
                balance_sheet = company.balance_sheet if period == 'annual' else company.quarterly_balance_sheet
                cash_flow = company.cash_flow if period == 'annual' else company.quarterly_cash_flow
                
                if not income_stmt.empty and not balance_sheet.empty and not cash_flow.empty:
                    print(f"Using {period} financial statements for {ticker}")
                    break
                    
            except Exception as e:
                print(f"Error fetching {period} statements for {ticker}: {str(e)}")
        else:
            print(f"Could not fetch any financial statements for {ticker}")
            return None
            
        # If we got here, we have some data
        if income_stmt.empty or balance_sheet.empty or cash_flow.empty:
            print(f"Incomplete financial data for {ticker}")
            return None
            
    except Exception as e:
        print(f"Error processing financial statements for {ticker}: {str(e)}")
        return None
        
    # Get the most recent period's data
    try:
        if not income_stmt.empty:
            year = income_stmt.columns[0]
            print(f"Using financial data for period: {year}")
        else:
            print(f"No financial data available for {ticker}")
            return None
    except Exception as e:
        print(f"Error processing financial data for {ticker}: {str(e)}")
        return None
        
        # Helper function to safely get data with multiple possible field names
        def get_data(field_names, df, default=0, required=False):
            return get_financial_data(field_names, df, year, default, required)
        
        # Add company info to the data
        data = {
            'company_name': info.get('shortName', ticker),
            'ticker': ticker,
            'industry': info.get('industry', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'market_cap': info.get('marketCap', 0),
            'currency': info.get('currency', 'USD'),
            'data_source': 'Yahoo Finance',
            
            # Financial data
            # Income statement
            'revenue': get_data(['Total Revenue', 'Revenue', 'Sales'], income_stmt, 0, True),
            'cogs': get_data(['Cost of Revenue', 'Cost of Goods Sold'], income_stmt, 0),
            'gross_profit': get_data(['Gross Profit'], income_stmt, 0),
            'operating_income': get_data(['Operating Income', 'Operating Income/Loss'], income_stmt, 0),
            'net_income': get_data(['Net Income', 'Net Income/Loss'], income_stmt, 0, True),
            'ebit': get_data(['EBIT', 'Operating Income'], income_stmt, 0),
            'depreciation': get_data(['Depreciation And Amortization', 'Depreciation'], cash_flow, 0),
            'rnd': get_data(['Research And Development', 'Research & Development'], income_stmt, 0),
            'sga': get_data(['Selling General And Administration', 'Selling General Administrative'], income_stmt, 0),
            'taxes': get_data(['Income Tax', 'Provision for Income Tax'], income_stmt, 0),
            'interest_expense': get_data(['Interest Expense', 'Interest Expense, Net'], income_stmt, 0),
            'interest_income': get_data(['Interest Income'], income_stmt, 0),
            'total_operating_expenses': get_data(['Total Operating Expenses'], income_stmt, 0),
            'total_other_income_expenses': get_data(['Total Other Income/Expenses Net'], income_stmt, 0),
            
            # Balance sheet
            'total_assets': get_data(['Total Assets'], balance_sheet, 0, True),
            'total_current_assets': get_data(['Current Assets', 'Total Current Assets'], balance_sheet, 0, True),
            'cash': get_data(['Cash And Cash Equivalents', 'Cash And Short Term Investments'], balance_sheet, 0),
            'accounts_receivable': get_data(['Net Receivables', 'Accounts Receivable'], balance_sheet, 0),
            'inventory': get_data(['Inventory', 'Total Inventory'], balance_sheet, 0),
            'total_liabilities': get_data(['Total Liabilities Net Minority Interest', 'Total Liabilities'], balance_sheet, 0, True),
            'total_current_liabilities': get_data(['Current Liabilities', 'Total Current Liabilities'], balance_sheet, 0, True),
            'long_term_debt': get_data(['Long Term Debt', 'Long Term Debt And Capital Lease Obligation'], balance_sheet, 0),
            'retained_earnings': get_data(['Retained Earnings'], balance_sheet, 0, True),
            'total_equity': get_data(['Stockholders Equity', 'Total Stockholder Equity', 'Total Equity'], balance_sheet, 0, True),
            'common_stock': get_data(['Common Stock'], balance_sheet, 0),
            'preferred_stock': get_data(['Preferred Stock'], balance_sheet, 0),
            'goodwill': get_data(['Goodwill'], balance_sheet, 0),
            'intangible_assets': get_data(['Intangible Assets', 'Other Intangible Assets'], balance_sheet, 0),
            'property_plant_equipment': get_data(['Property Plant And Equipment Net', 'Net Property Plant And Equipment'], balance_sheet, 0),
            
            # Cash flow
            'operating_cash_flow': get_data(['Operating Cash Flow', 'Cash Flow From Operating Activities'], cash_flow, 0, True),
            'capital_expenditures': abs(get_data(['Capital Expenditure', 'Purchase of Property, Plant, and Equipment'], cash_flow, 0)),
            'free_cash_flow': get_data(['Free Cash Flow'], cash_flow, 0),
            'dividends_paid': abs(get_data(['Dividends Paid', 'Payment of Dividends & Other Cash Distributions'], cash_flow, 0)),
            'stock_repurchases': abs(get_data(['Repurchase Of Stock', 'Repurchase of Common Stock'], cash_flow, 0)),
            'debt_issuance': get_data(['Issuance of Debt'], cash_flow, 0),
            'debt_repayment': abs(get_data(['Repayment of Debt', 'Repayment of Long Term Debt'], cash_flow, 0)),
            
            # Market data
            'market_cap': info.get('marketCap', 0),
            'shares_outstanding': info.get('sharesOutstanding', 0),
            'price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
            'beta': info.get('beta', 0),
            'company_name': info.get('longName', info.get('shortName', ticker)),
            'industry': info.get('industry', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'year': year.year if hasattr(year, 'year') else str(year),
            'currency': info.get('currency', 'USD'),
            
            # Store the raw data for reference
            'income_stmt': income_stmt,
            'balance_sheet': balance_sheet,
            'cash_flow': cash_flow,
            'company': company,
            'info': info
        }
        
        # Calculate derived metrics
        data['working_capital'] = data['total_current_assets'] - data['total_current_liabilities']
        data['total_debt'] = data['long_term_debt'] + data['total_current_liabilities']
        data['ebitda'] = data['ebit'] + data['depreciation']
        
        # Print key metrics
        print(f"\nCompany: {data['company_name']}")
        print(f"Industry: {data['industry']}")
        print(f"Market Cap: ${data['market_cap']/1e9:.2f}B" if data['market_cap'] > 0 else "Market Cap: N/A")
        print(f"Fiscal Year: {data['year']}")
        
        print("\nKey Financials:")
        print(f"Revenue: ${data['revenue']/1e9:.2f}B" if data['revenue'] > 0 else "Revenue: N/A")
        print(f"Net Income: ${data['net_income']/1e9:.2f}B" if data['net_income'] != 0 else "Net Income: N/A")
        print(f"Total Assets: ${data['total_assets']/1e9:.2f}B" if data['total_assets'] > 0 else "Total Assets: N/A")
        print(f"Total Liabilities: ${data['total_liabilities']/1e9:.2f}B" if data['total_liabilities'] > 0 else "Total Liabilities: N/A")
        print(f"Total Equity: ${data['total_equity']/1e9:.2f}B" if data['total_equity'] > 0 else "Total Equity: N/A")
        
        print("\nRunning analyses...")
        return data
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error fetching data for {ticker}: {str(e)}\n{error_details}")
        return None
        print(f"Total Assets: ${data['total_assets']/1e9:.2f}B" if data['total_assets'] > 0 else "Total Assets: N/A")
        print(f"Total Liabilities: ${data['total_liabilities']/1e9:.2f}B" if data['total_liabilities'] > 0 else "Total Liabilities: N/A")
        print(f"Total Equity: ${data['total_equity']/1e9:.2f}B" if data['total_equity'] > 0 else "Total Equity: N/A")
        
        print("\nRunning analyses...")
        return data

def analyze_benford(data):
    """Perform Benford's Law analysis on financial statement line items."""
    try:
        # Prepare data for Benford's Law analysis
        benford_data = []
        
        def add_to_benford_data(value):
            """Helper function to safely add a value to benford_data."""
            try:
                # Skip None values
                if value is None:
                    return
                    
                # Convert to float directly if it's already a number
                if isinstance(value, (int, float)):
                    num = abs(float(value))
                    if num > 0:
                        benford_data.append(num)
                    return
                    
                # Handle string values
                if isinstance(value, str):
                    # Remove any non-numeric characters except decimal point and negative sign
                    clean_val = ''.join(c for c in value.strip() if c.isdigit() or c in '.-')
                    if not clean_val:
                        return
                    num = abs(float(clean_val))
                    if num > 0:
                        benford_data.append(num)
                        
            except (ValueError, TypeError) as e:
                # Skip values that can't be converted to numbers
                pass
        
        # Add income statement items
        if 'income_stmt' in data and data['income_stmt'] is not None:
            for item in data['income_stmt'].index:
                try:
                    value = data['income_stmt'].loc[item].iloc[0]
                    add_to_benford_data(value)
                except (IndexError, KeyError):
                    continue
        
        # Add balance sheet items
        if 'balance_sheet' in data and data['balance_sheet'] is not None:
            for item in data['balance_sheet'].index:
                try:
                    value = data['balance_sheet'].loc[item].iloc[0]
                    add_to_benford_data(value)
                except (IndexError, KeyError):
                    continue
        
        # Add cash flow items
        if 'cash_flow' in data and data['cash_flow'] is not None:
            for item in data['cash_flow'].index:
                try:
                    value = data['cash_flow'].loc[item].iloc[0]
                    add_to_benford_data(value)
                except (IndexError, KeyError):
                    continue
        
        if not benford_data:
            return {'error': 'No valid data available for Benford\'s Law analysis'}
        
        # Debug: Print first few values for inspection
        print(f"\nFirst 5 values for Benford's analysis:")
        for val in benford_data[:5]:
            print(f"  - {val}")
        
        # Perform Benford's Law analysis
        result = analyze_benfords_law(benford_data)
        
        # Ensure all numeric values are properly converted
        m_score = 0
        if 'm_score' in result and result['m_score'] is not None:
            try:
                m_score = float(result['m_score'])
            except (ValueError, TypeError):
                pass
                
        mad = 0
        if 'mad' in result and result['mad'] is not None:
            try:
                mad = float(result['mad'])
            except (ValueError, TypeError):
                pass
        
        return {
            'm_score': m_score,
            'significant': bool(result.get('significant', False)),
            'mad': mad,
            'conclusion': str(result.get('mad_conclusion', 'Insufficient data')),
            'digit_distribution': dict((str(k), float(v)) for k, v in result.get('digit_distribution', {}).items())
        }
    except Exception as e:
        return {'error': f'Error in Benford\'s Law analysis: {str(e)}'}

def analyze_zscore(data):
    """Calculate Altman Z-Score."""
    try:
        # Ensure we have all required data
        if data['total_assets'] <= 0:
            raise ValueError("Total assets must be greater than zero")
            
        result = calculate_altman_zscore(
            working_capital=data['working_capital'],
            total_assets=data['total_assets'],
            retained_earnings=data['retained_earnings'],
            ebit=data['ebit'],
            market_value_equity=data['market_cap'],
            total_liabilities=data['total_liabilities'],
            sales=data['revenue']
        )
        return {
            'z_score': result.get('z_score', 0),
            'risk_category': result.get('risk_category', 'Unknown'),
            'model_used': result.get('model_used', 'N/A')
        }
    except Exception as e:
        return {'error': str(e)}

def analyze_mscore(data):
    """Calculate Beneish M-Score."""
    try:
        # Calculate M-Score with error handling
        try:
            result = calculate_beneish_mscore(
                sales=data['revenue'],
                cogs=data['cogs'],
                sga=data['sga'],
                dep=data['depreciation'],
                current_assets=data['total_current_assets'],
                current_liabilities=data['total_current_liabilities'],
                total_assets=data['total_assets'],
                total_assets_prev=data['total_assets'],  # Using current as previous for now
                ppe=data['property_plant_equipment'],
                ppe_prev=data['property_plant_equipment'],  # Using current as previous for now
                net_income=data['net_income'],
                cash_flow_ops=data['operating_cash_flow'],
                long_term_debt=data['long_term_debt'],
                long_term_debt_prev=data['long_term_debt'],  # Using current as previous for now
                sales_prev=data['revenue'],  # Using current as previous for now
                sga_prev=data['sga'],  # Using current as previous for now
                dep_prev=data['depreciation'],  # Using current as previous for now
                current_assets_prev=data['total_current_assets'],  # Using current as previous for now
                current_liabilities_prev=data['total_current_liabilities']  # Using current as previous for now
            )
            return {
                'm_score': result.get('m_score', 0),
                'is_likely_manipulator': result.get('is_likely_manipulator', False),
                'interpretation': result.get('interpretation', 'Insufficient data for analysis')
            }
        except Exception as e:
            return {'error': f'Error calculating M-Score: {str(e)}'}
    except Exception as e:
        return {'error': f'Error in M-Score analysis: {str(e)}'}

def analyze_ratios(data):
    """Calculate financial ratios."""
    try:
        if data is None:
            return {'error': 'No data provided for ratio analysis'}
        
        # Create a financial ratios calculator instance
        ratios_calculator = FinancialRatios()
        
        # Prepare financials dictionary with all required fields
        financials = {
            'current_assets': data['total_current_assets'],
            'total_assets': data['total_assets'],
            'current_liabilities': data['total_current_liabilities'],
            'total_liabilities': data['total_liabilities'],
            'total_equity': data['total_equity'],
            'revenue': data['revenue'],
            'net_income': data['net_income'],
            'operating_income': data['operating_income'],
            'ebit': data['ebit'],
            'ebitda': data['ebitda'],
            'cash': data['cash'],
            'accounts_receivable': data['accounts_receivable'],
            'inventory': data['inventory'],
            'long_term_debt': data['long_term_debt'],
            'interest_expense': data['interest_expense'],
            'total_debt': data['total_debt'],
            'working_capital': data['working_capital'],
            'market_cap': data['market_cap'],
            'shares_outstanding': data['shares_outstanding'],
            'price': data['price'],
            'operating_cash_flow': data['operating_cash_flow'],
            'capital_expenditures': data['capital_expenditures'],
            'free_cash_flow': data['free_cash_flow'],
            'dividends_paid': data['dividends_paid'],
            'stock_repurchases': data['stock_repurchases'],
            'eps': data['net_income'] / data['shares_outstanding'] if data['shares_outstanding'] > 0 else 0,
            'book_value': data['total_equity'],
            'research_development': data['rnd'],
            'sga_expense': data['sga'],
            'cogs': data.get('cogs', 0),  # Default to 0 if not available
            'fixed_assets': data.get('property_plant_equipment', 0),  # Default to 0 if not available
            'accounts_payable': data.get('accounts_payable', 0),  # Default to 0 if not available
            'tax_expense': data.get('income_tax_expense', 0),  # Default to 0 if not available
            'marketable_securities': data.get('short_term_investments', 0)  # Default to 0 if not available
        }
        
        # Calculate all ratios
        ratio_results = ratios_calculator.calculate_all_ratios(financials)
        
        return ratio_results
        
    except Exception as e:
        print(f"RATIOS Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'error': str(e)}

def print_analysis(ticker, analysis):
    """Print the analysis results in a readable format."""
    print(f"\n{'='*80}")
    print(f"FORENSIC ANALYSIS REPORT: {ticker}")
    print(f"Company: {analysis.get('company_name', 'N/A')}")
    print(f"Industry: {analysis.get('industry', 'N/A')}")
    print(f"Market Cap: ${analysis.get('market_cap', 0)/1e9:.2f}B" if analysis.get('market_cap') else "Market Cap: N/A")
    if 'analysis_date' in analysis:
        print(f"Analysis Date: {analysis['analysis_date']}")
    print(f"{'='*80}")
    
    # Benford's Law Analysis
    print("\nBENFORD'S LAW ANALYSIS")
    print("-" * 50)
    if 'error' in analysis['benford']:
        print(f"Error: {analysis['benford']['error']}")
    else:
        # Print Benford's Law summary
        print(f"M-Score: {analysis['benford'].get('m_score', 0):.4f}")
        print(f"Significant Deviation: {analysis['benford'].get('significant', False)}")
        print(f"MAD: {analysis['benford'].get('mad', 0):.4f} - {analysis['benford'].get('conclusion', 'N/A')}")
        
        # Print digit distribution if available
        if 'digit_distribution' in analysis['benford'] and analysis['benford']['digit_distribution']:
            print("\nDigit Distribution:")
            print("Digit  Observed  Expected  Deviation")
            print("-----  --------  --------  ---------")
            
            # Get expected distribution from Benford's Law
            expected_dist = {
                1: 0.3010, 2: 0.1761, 3: 0.1249,
                4: 0.0969, 5: 0.0792, 6: 0.0669,
                7: 0.0580, 8: 0.0512, 9: 0.0458
            }
            
            # Print distribution for each digit
            for digit in range(1, 10):
                observed = analysis['benford']['digit_distribution'].get(str(digit), 0)
                expected = expected_dist.get(digit, 0)
                deviation = (observed - expected) * 100  # as percentage
                print(f"{digit:>4}  {observed:>8.2%}  {expected:>8.2%}  {deviation:>+8.2f}%")
    
    # Z-Score Analysis
    print("\nALTMAN Z-SCORE ANALYSIS")
    print("-" * 50)
    if 'error' in analysis['zscore']:
        print(f"Error: {analysis['zscore']['error']}")
    else:
        print(f"Z-Score: {analysis['zscore']['z_score']:.2f}")
        print(f"Risk Category: {analysis['zscore']['risk_category']}")
        print(f"Model Used: {analysis['zscore']['model_used']}")
    
    # M-Score Analysis
    print("\nBENEISH M-SCORE ANALYSIS")
    print("-" * 50)
    if 'error' in analysis['mscore']:
        print(f"Error: {analysis['mscore']['error']}")
    else:
        print(f"M-Score: {analysis['mscore']['m_score']:.2f}")
        print(f"Likely Manipulator: {analysis['mscore']['is_likely_manipulator']}")
        print(f"Interpretation: {analysis['mscore']['interpretation']}")
    
    # Financial Ratios
    print("\nFINANCIAL RATIOS")
    print("-" * 50)
    if 'error' in analysis['ratios']:
        print(f"Error: {analysis['ratios']['error']}")
    else:
        ratios = analysis['ratios']
        
        def format_value(value):
            """Format numeric values with appropriate units and decimal places."""
            if value is None:
                return "N/A"
                
            if isinstance(value, (int, float)):
                # Handle numpy numeric types
                if hasattr(value, 'item'):
                    value = value.item()
                
                # Format large numbers with appropriate units
                abs_val = abs(value)
                if abs_val >= 1_000_000_000:
                    return f"${value/1_000_000_000:,.2f}B"
                elif abs_val >= 1_000_000:
                    return f"${value/1_000_000:,.2f}M"
                elif abs_val >= 1_000:
                    return f"${value/1_000:,.1f}K"
                # Format percentages (values between 0 and 1 or when value < 1)
                elif (0 <= abs_val <= 1) or (isinstance(value, float) and abs_val < 1):
                    return f"{value:.2%}"
                # Format other numbers with 2 decimal places
                else:
                    return f"{value:,.2f}"
            return str(value)
        
        def print_ratio_section(section_name, ratio_list):
            """Print a section of financial ratios in a clean, readable format."""
            if not ratio_list or not isinstance(ratio_list, list):
                return
                
            print(f"\n{section_name.upper()}")
            print("-" * len(section_name.upper()))
            
            max_name_length = 0
            formatted_ratios = []
            
            # First pass: collect and format all ratios, find max name length
            for ratio in ratio_list:
                if not isinstance(ratio, dict):
                    continue
                    
                name = ratio.get('name', 'Unnamed Ratio')
                value = ratio.get('value')
                formula = ratio.get('formula', '')
                interpretation = ratio.get('interpretation', '')
                benchmark = ratio.get('benchmark')
                
                # Format the value with appropriate units
                formatted_value = format_value(value)
                
                # Track the longest name for alignment
                if len(name) > max_name_length:
                    max_name_length = len(name)
                
                formatted_ratios.append({
                    'name': name,
                    'formatted_value': formatted_value,
                    'formula': formula,
                    'interpretation': interpretation,
                    'benchmark': benchmark,
                    'benchmark_source': ratio.get('benchmark_source', 'Industry average')
                })
            
            # Second pass: print all ratios with aligned values
            for ratio in formatted_ratios:
                # Print ratio name and value on the same line with fixed width
                print(f"{ratio['name'].ljust(max_name_length + 2)} {ratio['formatted_value']}")
                
                # Print additional details indented
                if ratio['formula']:
                    print(f"  {' ' * max_name_length}  Formula: {ratio['formula']}")
                if ratio['interpretation']:
                    print(f"  {' ' * max_name_length}  {ratio['interpretation']}")
                if ratio['benchmark'] is not None:
                    benchmark_str = format_value(ratio['benchmark'])
                    print(f"  {' ' * max_name_length}  Benchmark ({ratio['benchmark_source']}): {benchmark_str}")
                
                print()  # Add a blank line between ratios
        
        # Extract and process the ratio data
        ratio_sections = {}
        
        # Helper function to extract ratio items from the data structure
        def extract_ratio_items(ratio_dict):
            if not ratio_dict:
                return []
                
            if isinstance(ratio_dict, list):
                return ratio_dict
                
            if 'value' in ratio_dict and 'name' in ratio_dict:
                return [ratio_dict]
                
            if isinstance(ratio_dict, dict):
                return [
                    {'name': k, 'value': v} if not isinstance(v, dict) else v 
                    for k, v in ratio_dict.items()
                ]
                
            return []
        
        # Process each ratio category
        for category in ['liquidity_ratios', 'profitability_ratios', 'leverage_ratios', 
                        'efficiency_ratios', 'valuation_ratios', 'cash_flow_ratios']:
            if category in ratios:
                ratio_sections[category.replace('_', ' ').title()] = extract_ratio_items(ratios[category])
        
        # Print each section
        for section_name, section_data in ratio_sections.items():
            if section_data:  # Only print non-empty sections
                print_ratio_section(section_name, section_data)
        
        # If no sections were found, print the raw ratios for debugging
        if not ratio_sections and ratios:
            print("\nUNABLE TO PARSE FINANCIAL RATIOS. RAW DATA:")
            print("-" * 40)
            for key, value in list(ratios.items())[:10]:  # Limit to first 10 items
                print(f"\n{key}:")
                if isinstance(value, dict):
                    for k, v in list(value.items())[:5]:  # First 5 items of each dict
                        print(f"  {k}: {v}")
                    if len(value) > 5:
                        print(f"  ... and {len(value) - 5} more items")
                else:
                    print(f"  {value}")
    
    print("\n" + "="*80 + "\n")

def get_financial_data(names, df, year, default=0, required=False):
    """Safely get financial data with multiple possible field names.
    
    Args:
        names: Single field name or list of possible field names to try
        df: DataFrame containing the financial data
        year: The year/period to get data for
        default: Default value to return if field not found
        required: If True, raises an error if the field is not found
        
    Returns:
        The requested financial data or default value
        
    Raises:
        ValueError: If required is True and field is not found
    """
    if not isinstance(names, list):
        names = [names]
    
    # Print available fields for debugging
    if required:
        print(f"\nLooking for required field in: {', '.join(names)}")
        print("Available fields in DataFrame:")
        for idx in df.index:
            print(f"- {idx}")
    
    for name in names:
        if name in df.index:
            try:
                value = df.loc[name, year]
                # Convert any string numbers to float
                if isinstance(value, str):
                    try:
                        value = float(value.replace(',', ''))
                    except (ValueError, AttributeError):
                        pass
                return value
            except KeyError:
                # If the year is not found, try to get the first available year
                try:
                    value = df.loc[name].iloc[0]
                    if isinstance(value, str):
                        try:
                            value = float(value.replace(',', ''))
                        except (ValueError, AttributeError):
                            pass
                    return value
                except (IndexError, KeyError):
                    continue
    
    if required:
        raise ValueError(f"Required field not found in: {', '.join(names)}. Available fields: {', '.join(df.index.tolist()[:10])}...")
    return default

def _safe_get(obj, attr, default=None):
    """Safely get an attribute from an object."""
    try:
        return getattr(obj, attr, default)
    except Exception as e:
        print(f"Warning: Could not get {attr}: {e}")
        return default

def _get_cache_path(ticker):
    """Get the cache file path for a ticker."""
    cache_dir = os.path.join(os.path.dirname(__file__), ".ticker_cache")
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, f"{ticker.upper()}.json")

def _cache_data(ticker, data):
    """Cache the ticker data to a file."""
    try:
        cache_file = _get_cache_path(ticker)
        with open(cache_file, 'w') as f:
            # Convert numpy types to native Python types for JSON serialization
            def convert(o):
                if isinstance(o, (np.integer, np.floating)):
                    return int(o) if isinstance(o, np.integer) else float(o)
                elif isinstance(o, (pd.Timestamp, np.datetime64)):
                    return str(o)
                elif isinstance(o, pd.DataFrame):
                    return o.to_dict()
                raise TypeError(f"Object of type {type(o)} is not JSON serializable")
            
            json.dump(data, f, default=convert, indent=2)
    except Exception as e:
        print(f"Warning: Failed to cache data: {e}")

def _get_cached_data(ticker, max_age_days=1):
    """Get cached data for a ticker if it exists and is fresh enough."""
    try:
        cache_file = _get_cache_path(ticker)
        
        # Check if cache file exists and is fresh
        if os.path.exists(cache_file):
            file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
            if (datetime.now() - file_time) < timedelta(days=max_age_days):
                with open(cache_file, 'r') as f:
                    return json.load(f)
    except Exception as e:
        print(f"Cache read error: {e}")
    return None

def main():
    import sys
    import traceback
    
    # List of companies to analyze
    companies = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'JPM', 'WMT']
    
    # If tickers are provided as command line arguments, use those instead
    if len(sys.argv) > 1:
        companies = sys.argv[1:]
    
    print(f"Analyzing {len(companies)} companies: {', '.join(companies)}\n")
    
    for i, ticker in enumerate(companies):
        try:
            print("\n" + "="*50)
            print(f"ANALYZING {ticker} ({i+1}/{len(companies)})")
            print("="*50)
            
            # Add a delay between tickers
            if i > 0:
                delay = random.uniform(2.0, 5.0)
                print(f"Waiting {delay:.1f} seconds before next request...")
                time.sleep(delay)
            
            # Get company data
            data = get_company_data(ticker)
            if data is None:
                print(f"Skipping {ticker} due to missing data")
                # Add a delay even when skipping
                time.sleep(1)
                continue
            
            # Run analyses
            print("\nRunning Benford's Law analysis...")
            benford = analyze_benford(data)
            
            print("Running Altman Z-Score analysis...")
            zscore = analyze_zscore(data)
            
            print("Running Beneish M-Score analysis...")
            mscore = analyze_mscore(data)
            
            print("Calculating financial ratios...")
            ratios = analyze_ratios(data)
            
            # Print results
            print_analysis(ticker, {
                'company_name': data['company_name'],
                'industry': data['industry'],
                'market_cap': data['market_cap'],
                'year': data['year'],
                'benford': benford,
                'zscore': zscore,
                'mscore': mscore,
                'ratios': ratios if ratios is not None else {'error': 'No ratio data available'}
            })
            
        except Exception as e:
            print(f"\nError analyzing {ticker}: {str(e)}")
            traceback.print_exc()
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()
