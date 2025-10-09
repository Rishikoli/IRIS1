#!/usr/bin/env python3
"""
Yahoo Finance Data Mapping for Forensic Analysis
"""

def create_yahoo_to_agent_mapping():
    """Create comprehensive mapping from Yahoo Finance fields to agent fields"""

    # Income Statement Mapping
    income_mapping = {
        # Revenue metrics
        'TotalRevenue': 'total_revenue',
        'Total Revenue': 'total_revenue',

        # Cost metrics
        'CostOfRevenue': 'cost_of_revenue',
        'Cost Of Revenue': 'cost_of_revenue',
        'Reconciled Cost Of Revenue': 'cost_of_revenue',

        # Profit metrics
        'GrossProfit': 'gross_profit',
        'Gross Profit': 'gross_profit',

        'OperatingIncome': 'operating_income',
        'Operating Income': 'operating_income',

        'NetIncome': 'net_profit',
        'Net Income': 'net_profit',
        'Net Income From Continuing Operation Net Minority Interest': 'net_profit',
        'Net Income From Continuing And Discontinued Operation': 'net_profit',

        # Expense metrics
        'InterestExpense': 'interest_expense',
        'Interest Expense': 'interest_expense',

        'IncomeTaxExpense': 'tax_expense',
        'Tax Expense': 'tax_expense',
        'Income Tax Expense': 'tax_expense',

        # Additional metrics that might be available
        'EBITDA': 'ebitda',
        'EBIT': 'ebit',
        'Selling General And Administration': 'sga_expense',
        'Selling General Administrative': 'sga_expense',
    }

    # Balance Sheet Mapping
    balance_mapping = {
        # Asset metrics
        'TotalAssets': 'total_assets',
        'Total Assets': 'total_assets',

        'CurrentAssets': 'current_assets',
        'Current Assets': 'current_assets',

        'CashAndCashEquivalents': 'cash_and_equivalents',
        'Cash And Cash Equivalents': 'cash_and_equivalents',
        'Cash Financial': 'cash_and_equivalents',

        # Liability metrics
        'TotalLiabilitiesNetMinorityInterest': 'total_liabilities',
        'Total Liabilities Net Minority Interest': 'total_liabilities',
        'Total Liabilities': 'total_liabilities',

        'CurrentLiabilities': 'current_liabilities',
        'Current Liabilities': 'current_liabilities',

        # Equity metrics
        'StockholdersEquity': 'total_equity',
        'Stockholders Equity': 'total_equity',
        'Total Equity Gross Minority Interest': 'total_equity',

        'RetainedEarnings': 'retained_earnings',
        'Retained Earnings': 'retained_earnings',

        # Additional asset metrics
        'AccountsReceivable': 'accounts_receivable',
        'Accounts Receivable': 'accounts_receivable',
        'Net Receivables': 'accounts_receivable',

        'Inventory': 'inventory',
        'Inventories': 'inventory',

        'PropertyPlantEquipment': 'property_plant_equipment',
        'Property Plant Equipment': 'property_plant_equipment',
        'Net PPE': 'property_plant_equipment',

        'Goodwill': 'goodwill',
        'IntangibleAssets': 'intangible_assets',
        'Intangible Assets': 'intangible_assets',

        # Additional liability metrics
        'AccountsPayable': 'accounts_payable',
        'Accounts Payable': 'accounts_payable',
        'Current Accrued Expenses': 'accounts_payable',

        'ShortTermDebt': 'short_term_debt',
        'Short Term Debt': 'short_term_debt',
        'LongTermDebt': 'long_term_debt',
        'Long Term Debt': 'long_term_debt',
    }

    return {
        'income_statement': income_mapping,
        'balance_sheet': balance_mapping
    }

def map_yahoo_data_to_agent_format(yahoo_data, statement_type):
    """Map Yahoo Finance data to agent-expected format"""

    mapping = create_yahoo_to_agent_mapping()
    field_mapping = mapping.get(statement_type, {})

    mapped_data = {}

    for yahoo_field, agent_field in field_mapping.items():
        if yahoo_field in yahoo_data:
            value = yahoo_data[yahoo_field]
            if value is not None and not (isinstance(value, float) and str(value) == 'nan'):
                try:
                    # Convert to float if it's a number
                    numeric_value = float(value)
                    if numeric_value > 0:  # Only include positive values
                        mapped_data[agent_field] = numeric_value
                except (ValueError, TypeError):
                    # Skip non-numeric values
                    continue

    return mapped_data

def prepare_financial_statements_for_analysis(companies_data):
    """Prepare financial statements in the format expected by ForensicAnalysisAgent"""

    financial_statements = []

    for company_data in companies_data:
        symbol = company_data.get('symbol', 'UNKNOWN')
        print(f"🔄 Processing {symbol}...")

        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)

            # Get financial statements
            income_stmt = ticker.financials
            balance_sheet = ticker.balance_sheet

            if income_stmt is None or balance_sheet is None:
                print(f"❌ Insufficient data for {symbol}")
                continue

            # Process latest 2 periods for each statement type
            periods_to_process = min(2, len(income_stmt.columns), len(balance_sheet.columns))

            for i in range(periods_to_process):
                # Income Statement
                if i < len(income_stmt.columns):
                    income_date = str(income_stmt.columns[i].date())
                    income_yahoo_data = income_stmt.iloc[:, i].to_dict()
                    income_mapped_data = map_yahoo_data_to_agent_format(income_yahoo_data, 'income_statement')

                    if income_mapped_data:  # Only add if we have mapped data
                        financial_statements.append({
                            'statement_type': 'income_statement',
                            'period_end': income_date,
                            'data': income_mapped_data,
                            'company': symbol
                        })

                # Balance Sheet
                if i < len(balance_sheet.columns):
                    balance_date = str(balance_sheet.columns[i].date())
                    balance_yahoo_data = balance_sheet.iloc[:, i].to_dict()
                    balance_mapped_data = map_yahoo_data_to_agent_format(balance_yahoo_data, 'balance_sheet')

                    if balance_mapped_data:  # Only add if we have mapped data
                        financial_statements.append({
                            'statement_type': 'balance_sheet',
                            'period_end': balance_date,
                            'data': balance_mapped_data,
                            'company': symbol
                        })

        except Exception as e:
            print(f"❌ Error processing {symbol}: {e}")
            continue

    return financial_statements

def inspect_mapped_data(financial_statements):
    """Show what data was successfully mapped"""
    print("\n📋 MAPPED DATA INSPECTION")
    print("=" * 35)

    for i, stmt in enumerate(financial_statements, 1):
        stmt_type = stmt.get('statement_type', 'Unknown')
        period = stmt.get('period_end', 'Unknown')
        company = stmt.get('company', 'Unknown')
        data = stmt.get('data', {})

        print(f"\n{i}. {company} - {period} - {stmt_type}")
        print(f"   Mapped fields ({len(data)}):")

        if stmt_type == 'income_statement':
            expected_fields = ['total_revenue', 'gross_profit', 'operating_income', 'net_profit']
        else:  # balance_sheet
            expected_fields = ['total_assets', 'total_liabilities', 'total_equity', 'current_assets']

        for field in expected_fields:
            if field in data:
                print(f"   ✅ {field}: {data[field]:,}")
            else:
                print(f"   ❌ {field}: NOT MAPPED")

if __name__ == "__main__":
    """Test the mapping functionality"""
    print("🔄 TESTING YAHOO FINANCE DATA MAPPING")
    print("=" * 45)

    # Test with HCL Technologies
    test_companies = [
        {'symbol': 'HCLTECH.NS', 'name': 'HCL Technologies'}
    ]

    # Prepare financial statements
    financial_statements = prepare_financial_statements_for_analysis(test_companies)

    if financial_statements:
        print(f"\n✅ Successfully prepared {len(financial_statements)} financial statements")

        # Show mapped data
        inspect_mapped_data(financial_statements)

        print("\n🎉 YAHOO FINANCE MAPPING TEST COMPLETED!")
        print(f"✅ Mapped {len(financial_statements)} statements successfully")
        print("✅ Ready for forensic analysis with real data")
    else:
        print("\n❌ No financial statements could be mapped")
