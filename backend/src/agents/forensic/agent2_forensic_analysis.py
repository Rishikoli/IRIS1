"""
Project IRIS - Agent 2: Forensic Analysis Agent
Implements Benford's Law, Altman Z-Score, Beneish M-Score, and financial ratio analysis
"""

import logging
import asyncio
import json
import numpy as np
import pandas as pd
from typing import AsyncGenerator, Dict, List, Any, Optional, Tuple, Callable
from decimal import Decimal
from datetime import datetime
from scipy import stats
import math

from src.config import settings
from src.database.connection import get_db_client

logger = logging.getLogger(__name__)


class ForensicAnalysisAgent:
    """Agent 2: Forensic analysis with statistical tests and financial ratios"""

    def __init__(self):
        try:
            self.db_client = get_db_client()
        except Exception:
            # For standalone analysis without database
            self.db_client = None
        
    def analyze_yahoo_finance_data(self, symbol: str, quarters: int = 3) -> Dict[str, Any]:
        """Analyze real Yahoo Finance data with enhanced field mapping and pandas NaN detection"""
        try:
            import yfinance as yf
            import pandas as pd

            print(f"📊 Fetching {quarters} quarters of real data for {symbol} from Yahoo Finance...")

            ticker = yf.Ticker(symbol)

            # Get quarterly data for more historical periods
            quarterly_income = ticker.quarterly_financials
            quarterly_balance = ticker.quarterly_balance_sheet
            quarterly_cashflow = ticker.quarterly_cashflow

            if quarterly_income is None or quarterly_balance is None:
                return {"success": False, "error": f"Insufficient quarterly data for {symbol}"}

            print(f"✅ Retrieved {len(quarterly_income.columns) if quarterly_income is not None else 0} quarters of income statements")
            print(f"✅ Retrieved {len(quarterly_balance.columns) if quarterly_balance is not None else 0} quarters of balance sheets")
            print(f"✅ Retrieved {len(quarterly_cashflow.columns) if quarterly_cashflow is not None else 0} quarters of cash flow statements")

            # Enhanced Yahoo Finance to Agent field mapping
            yahoo_to_agent_mapping = {
                'income_statement': {
                    # Revenue fields
                    'Total Revenue': 'total_revenue',
                    'TotalRevenue': 'total_revenue',

                    # Profit fields
                    'Net Income': 'net_profit',
                    'NetIncome': 'net_profit',
                    'Net Income From Continuing And Discontinued Operation': 'net_profit',

                    # Cost fields
                    'Cost Of Revenue': 'cost_of_revenue',
                    'CostOfRevenue': 'cost_of_revenue',

                    # Additional profit metrics
                    'Gross Profit': 'gross_profit',
                    'GrossProfit': 'gross_profit',
                    'Operating Income': 'operating_income',
                    'OperatingIncome': 'operating_income',
                    'EBITDA': 'ebitda',
                    'EBIT': 'ebit',

                    # Expense fields
                    'Interest Expense': 'interest_expense',
                    'InterestExpense': 'interest_expense',
                    'Income Tax Expense': 'tax_expense',
                    'Tax Expense': 'tax_expense',
                },
                'balance_sheet': {
                    # Asset fields
                    'Total Assets': 'total_assets',
                    'TotalAssets': 'total_assets',

                    # Liability fields
                    'Total Liabilities Net Minority Interest': 'total_liabilities',
                    'TotalLiabilitiesNetMinorityInterest': 'total_liabilities',

                    # Equity fields
                    'Stockholders Equity': 'total_equity',
                    'StockholdersEquity': 'total_equity',

                    # Current fields
                    'Current Assets': 'current_assets',
                    'CurrentAssets': 'current_assets',
                    'Current Liabilities': 'current_liabilities',
                    'CurrentLiabilities': 'current_liabilities',

                    # Cash fields
                    'Cash And Cash Equivalents': 'cash_and_equivalents',
                    'CashAndCashEquivalents': 'cash_and_equivalents',
                    'Other Short Term Investments': 'short_term_investments',
                    'OtherShortTermInvestments': 'short_term_investments',
                },
                'cash_flow_statement': {
                    # Operating Activities
                    'Operating Cash Flow': 'operating_cash_flow',
                    'Total Cash From Operating Activities': 'operating_cash_flow',
                    'Cash Flow From Continuing Operating Activities': 'operating_cash_flow'
                }
            }

            # Convert Yahoo Finance data to agent format
            financial_statements = []

            # Process up to specified quarters for each statement type
            periods_to_process = min(quarters, len(quarterly_income.columns) if quarterly_income is not None else 0)

            for i in range(periods_to_process):
                # Income Statement
                if i < len(quarterly_income.columns):
                    income_date = str(quarterly_income.columns[i].date())
                    income_yahoo_data = quarterly_income.iloc[:, i].to_dict()

                    # Map Yahoo fields to agent fields with pandas NaN detection
                    income_mapped_data = {}
                    for yahoo_field, agent_field in yahoo_to_agent_mapping['income_statement'].items():
                        if yahoo_field in income_yahoo_data:
                            value = income_yahoo_data[yahoo_field]
                            if value is not None and not pd.isna(value):
                                try:
                                    numeric_value = float(value)
                                    if numeric_value != 0:  # Include zero values for growth calculations
                                        income_mapped_data[agent_field] = numeric_value
                                except (ValueError, TypeError):
                                    continue

                    if income_mapped_data:  # Only add if we have mapped data
                        financial_statements.append({
                            'statement_type': 'income_statement',
                            'period_end': income_date,
                            'data': income_mapped_data
                        })
                        print(f"  ✅ Income Statement {i+1}: {income_date} ({len(income_mapped_data)} fields)")

                # Balance Sheet
                if i < len(quarterly_balance.columns):
                    balance_date = str(quarterly_balance.columns[i].date())
                    balance_yahoo_data = quarterly_balance.iloc[:, i].to_dict()

                    # Map Yahoo fields to agent fields with pandas NaN detection
                    balance_mapped_data = {}
                    for yahoo_field, agent_field in yahoo_to_agent_mapping['balance_sheet'].items():
                        if yahoo_field in balance_yahoo_data:
                            value = balance_yahoo_data[yahoo_field]
                            if value is not None and not pd.isna(value):
                                try:
                                    numeric_value = float(value)
                                    if numeric_value != 0:  # Include zero values for growth calculations
                                        balance_mapped_data[agent_field] = numeric_value
                                except (ValueError, TypeError):
                                    continue

                    if balance_mapped_data:  # Only add if we have mapped data
                        financial_statements.append({
                            'statement_type': 'balance_sheet',
                            'period_end': balance_date,
                            'data': balance_mapped_data
                        })
                        print(f"  ✅ Balance Sheet {i+1}: {balance_date} ({len(balance_mapped_data)} fields)")

                # Cash Flow Statement
                if quarterly_cashflow is not None and i < len(quarterly_cashflow.columns):
                    cash_date = str(quarterly_cashflow.columns[i].date())
                    cash_yahoo_data = quarterly_cashflow.iloc[:, i].to_dict()

                    # Map Yahoo fields to agent fields
                    cash_mapped_data = {}
                    for yahoo_field, agent_field in yahoo_to_agent_mapping['cash_flow_statement'].items():
                        if yahoo_field in cash_yahoo_data:
                            value = cash_yahoo_data[yahoo_field]
                            if value is not None and not pd.isna(value):
                                try:
                                    numeric_value = float(value)
                                    if numeric_value != 0:
                                        cash_mapped_data[agent_field] = numeric_value
                                except (ValueError, TypeError):
                                    continue
                    
                    if cash_mapped_data:
                         financial_statements.append({
                            'statement_type': 'cash_flow_statement',
                             'period_end': cash_date,
                            'data': cash_mapped_data
                        })
                         print(f"  ✅ Cash Flow {i+1}: {cash_date} ({len(cash_mapped_data)} fields)")

            if not financial_statements:
                return {"success": False, "error": f"No mappable data found for {symbol}"}

            print(f"✅ Successfully mapped {len(financial_statements)} financial statements")

            # Run comprehensive analysis
            results = {
                "company_symbol": symbol,
                "data_source": "Yahoo Finance (Quarterly)",
                "quarters_analyzed": quarters,
                "analysis_date": datetime.now().isoformat(),
                "success": True
            }

            # Vertical Analysis
            vertical_result = self.vertical_analysis(financial_statements)
            results["vertical_analysis"] = vertical_result

            # Horizontal Analysis (only if we have multiple periods)
            if len(financial_statements) >= 2:
                horizontal_result = self.horizontal_analysis(financial_statements)
                results["horizontal_analysis"] = horizontal_result

            # Financial Ratios
            ratios_result = self.calculate_financial_ratios(financial_statements)
            results["financial_ratios"] = ratios_result

            # Sloan Ratio
            sloan_result = self.calculate_sloan_ratio(financial_statements)
            results["sloan_ratio"] = sloan_result

            return results

        except Exception as e:
            logger.error(f"Yahoo Finance analysis failed for {symbol}: {e}")
            return {"success": False, "error": str(e)}
        
    def vertical_analysis(self, financial_statements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform vertical analysis (common-size analysis)"""
        try:
            vertical_results = {}
            
            for statement in financial_statements:
                statement_type = statement.get("statement_type")
                data = statement.get("data", {})
                
                if statement_type == "income_statement":
                    vertical_results[statement_type] = self._vertical_income_statement(data)
                elif statement_type == "balance_sheet":
                    vertical_results[statement_type] = self._vertical_balance_sheet(data)
                    
            return {
                "success": True,
                "vertical_analysis": vertical_results,
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Vertical analysis failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _vertical_income_statement(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Vertical analysis for income statement (% of revenue)"""
        # Handle both raw Yahoo Finance data and normalized data
        total_revenue = (
            data.get("total_revenue") or
            data.get("Total Revenue") or
            data.get("totalRevenue") or
            0
        )

        if not total_revenue:
            return {"error": "No total revenue found"}

        # Calculate percentages using both possible field names
        def get_field_value(field_names, data):
            for name in field_names:
                if name in data and data[name] is not None and not pd.isna(data[name]):
                    try:
                        return float(data[name])
                    except (ValueError, TypeError):
                        continue
            return 0

        cost_of_revenue = get_field_value(["cost_of_revenue", "Cost Of Revenue", "CostOfRevenue"], data)
        gross_profit = get_field_value(["gross_profit", "Gross Profit", "GrossProfit"], data)
        operating_income = get_field_value(["operating_income", "Operating Income", "OperatingIncome"], data)
        net_profit = get_field_value(["net_profit", "Net Income", "NetIncome"], data)
        interest_expense = get_field_value(["interest_expense", "Interest Expense", "InterestExpense"], data)
        tax_expense = get_field_value(["tax_expense", "Income Tax Expense", "Tax Expense", "TaxExpense"], data)

        return {
            "revenue_pct": 100.0,
            "cogs_pct": (cost_of_revenue / total_revenue) * 100,
            "gross_profit_pct": (gross_profit / total_revenue) * 100,
            "operating_expenses_pct": ((gross_profit - operating_income) / total_revenue) * 100,
            "operating_income_pct": (operating_income / total_revenue) * 100,
            "net_income_pct": (net_profit / total_revenue) * 100,
            "interest_expense_pct": (interest_expense / total_revenue) * 100,
            "tax_expense_pct": (tax_expense / total_revenue) * 100
        }
    
    def _vertical_balance_sheet(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Vertical analysis for balance sheet (% of total assets)"""
        # Handle both raw Yahoo Finance data and normalized data
        total_assets = (
            data.get("total_assets") or
            data.get("Total Assets") or
            data.get("totalAssets") or
            0
        )

        if not total_assets:
            return {"error": "No total assets found"}

        # Calculate percentages using both possible field names
        def get_field_value(field_names, data):
            for name in field_names:
                if name in data and data[name] is not None and not pd.isna(data[name]):
                    try:
                        return float(data[name])
                    except (ValueError, TypeError):
                        continue
            return 0

        current_assets = get_field_value(["current_assets", "Current Assets", "CurrentAssets"], data)
        current_liabilities = get_field_value(["current_liabilities", "Current Liabilities", "CurrentLiabilities"], data)
        total_equity = get_field_value(["total_equity", "Stockholders Equity", "StockholdersEquity", "Total Equity Gross Minority Interest"], data)

        return {
            "total_assets_pct": 100.0,
            "current_assets_pct": (current_assets / total_assets) * 100,
            "non_current_assets_pct": ((total_assets - current_assets) / total_assets) * 100,
            "total_liabilities_pct": (data.get("total_liabilities", 0) / total_assets) * 100,
            "current_liabilities_pct": (current_liabilities / total_assets) * 100,
            "non_current_liabilities_pct": ((data.get("total_liabilities", 0) - current_liabilities) / total_assets) * 100,
            "shareholders_equity_pct": (total_equity / total_assets) * 100
        }
    
    def horizontal_analysis(self, financial_statements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform horizontal analysis (YoY and QoQ growth rates)"""
        try:
            # Group statements by type and period
            statements_by_period = {}
            for stmt in financial_statements:
                period = stmt.get("period_end")
                stmt_type = stmt.get("statement_type")
                if period not in statements_by_period:
                    statements_by_period[period] = {}
                statements_by_period[period][stmt_type] = stmt.get("data", {})

            # Sort periods chronologically
            sorted_periods = sorted(statements_by_period.keys())

            if len(sorted_periods) < 2:
                return {"success": False, "error": "Need at least 2 periods for horizontal analysis"}

            horizontal_results = {}

            # Compare same statement types across different periods
            for i in range(1, len(sorted_periods)):
                current_period = sorted_periods[i]
                previous_period = sorted_periods[i-1]

                current_data = statements_by_period[current_period]
                previous_data = statements_by_period[previous_period]

                # Compare each statement type that exists in both periods
                for stmt_type in set(current_data.keys()) & set(previous_data.keys()):
                    period_key = f"{previous_period}_to_{current_period}_{stmt_type}"
                    horizontal_results[period_key] = self._calculate_growth_rates(
                        previous_data[stmt_type],
                        current_data[stmt_type]
                    )

            return {
                "success": True,
                "horizontal_analysis": horizontal_results,
                "analysis_date": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Horizontal analysis failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _calculate_growth_rates(self, previous: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate growth rates between two periods"""
        growth_rates = {}

        # Handle both raw Yahoo Finance data and normalized data
        def get_field_value(field_names, data):
            for name in field_names:
                if name in data and data[name] is not None and not pd.isna(data[name]):
                    try:
                        return float(data[name])
                    except (ValueError, TypeError):
                        continue
            return 0

        key_metrics = [
            (["total_revenue", "Total Revenue", "totalRevenue"], "total_revenue"),
            (["gross_profit", "Gross Profit", "GrossProfit"], "gross_profit"),
            (["operating_income", "Operating Income", "OperatingIncome"], "operating_income"),
            (["net_profit", "Net Income", "NetIncome"], "net_profit"),
            (["total_assets", "Total Assets", "totalAssets"], "total_assets"),
            (["total_liabilities", "Total Liabilities Net Minority Interest", "TotalLiabilitiesNetMinorityInterest"], "total_liabilities"),
            (["total_equity", "Stockholders Equity", "StockholdersEquity"], "total_equity")
        ]

        for field_names, metric_name in key_metrics:
            prev_value = get_field_value(field_names, previous)
            curr_value = get_field_value(field_names, current)

            if prev_value != 0:
                growth_rate = ((curr_value - prev_value) / prev_value) * 100
                growth_rates[f"{metric_name}_growth_pct"] = round(growth_rate, 2)
            else:
                growth_rates[f"{metric_name}_growth_pct"] = None

        return growth_rates
    
    def calculate_financial_ratios(self, financial_statements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive financial ratios"""
        try:
            ratios_results = {}

            # Group statements by period
            statements_by_period = {}
            for statement in financial_statements:
                period = statement.get("period_end")
                stmt_type = statement.get("statement_type")
                if period not in statements_by_period:
                    statements_by_period[period] = {}
                statements_by_period[period][stmt_type] = statement.get("data", {})

            for period, period_statements in statements_by_period.items():
                if period not in ratios_results:
                    ratios_results[period] = {}

                balance_sheet = period_statements.get("balance_sheet", {})
                income_statement = period_statements.get("income_statement", {})

                # Calculate ratios from balance sheet only
                if balance_sheet:
                    ratios_results[period].update(self._calculate_liquidity_ratios(balance_sheet))
                    ratios_results[period].update(self._calculate_leverage_ratios(balance_sheet))

                # Calculate ratios from income statement only
                if income_statement:
                    ratios_results[period].update(self._calculate_profitability_ratios(income_statement))

                # Calculate ratios requiring both statements
                if balance_sheet and income_statement:
                    # ROE and ROA
                    net_profit = income_statement.get("net_profit", 0)
                    total_equity = balance_sheet.get("total_equity", 0)
                    total_assets = balance_sheet.get("total_assets", 0)

                    if total_equity != 0:
                        ratios_results[period]["roe"] = round((net_profit / total_equity) * 100, 2)

                    if total_assets != 0:
                        ratios_results[period]["roa"] = round((net_profit / total_assets) * 100, 2)

                    # Interest Coverage Ratio
                    operating_income = income_statement.get("operating_income", 0)
                    interest_expense = income_statement.get("interest_expense", 0)

                    if interest_expense != 0:
                        ratios_results[period]["interest_coverage"] = round(operating_income / interest_expense, 2)

                    # Efficiency Ratios
                    ratios_results[period].update(self._calculate_efficiency_ratios(balance_sheet, income_statement))

            return {
                "success": True,
                "financial_ratios": ratios_results,
                "analysis_date": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Financial ratio calculation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _calculate_liquidity_ratios(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate liquidity ratios"""
        current_assets = data.get("current_assets", 0)
        current_liabilities = data.get("current_liabilities", 0)
        cash_and_equivalents = data.get("cash_and_equivalents", 0)
        
        ratios = {}
        
        # Current Ratio
        if current_liabilities != 0:
            ratios["current_ratio"] = round(current_assets / current_liabilities, 2)
        
        # Quick Ratio (assuming 70% of current assets are liquid)
        if current_liabilities != 0:
            quick_assets = current_assets * 0.7  # Simplified assumption
            ratios["quick_ratio"] = round(quick_assets / current_liabilities, 2)
        
        # Cash Ratio
        if current_liabilities != 0:
            ratios["cash_ratio"] = round(cash_and_equivalents / current_liabilities, 2)
            
        return ratios
    
    def _calculate_profitability_ratios(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive profitability ratios"""
        # Handle both raw Yahoo Finance data and normalized data
        def get_field_value(field_names, data):
            for name in field_names:
                if name in data and data[name] is not None and not pd.isna(data[name]):
                    try:
                        return float(data[name])
                    except (ValueError, TypeError):
                        continue
            return 0

        total_revenue = get_field_value(["total_revenue", "Total Revenue", "totalRevenue"], data)
        gross_profit = get_field_value(["gross_profit", "Gross Profit", "GrossProfit"], data)
        operating_income = get_field_value(["operating_income", "Operating Income", "OperatingIncome"], data)
        net_profit = get_field_value(["net_profit", "Net Income", "NetIncome"], data)
        ebitda = get_field_value(["ebitda", "EBITDA"], data)

        ratios = {}

        # Gross Margin
        if total_revenue != 0:
            ratios["gross_margin_pct"] = round((gross_profit / total_revenue) * 100, 2)

        # Operating Margin
        if total_revenue != 0:
            ratios["operating_margin_pct"] = round((operating_income / total_revenue) * 100, 2)

        # Net Margin
        if total_revenue != 0:
            ratios["net_margin_pct"] = round((net_profit / total_revenue) * 100, 2)

        # EBITDA Margin
        if total_revenue != 0:
            ratios["ebitda_margin_pct"] = round((ebitda / total_revenue) * 100, 2)

        return ratios
    def _calculate_leverage_ratios(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate leverage ratios"""
        # Handle both raw Yahoo Finance data and normalized data
        def get_field_value(field_names, data):
            for name in field_names:
                if name in data and data[name] is not None and not pd.isna(data[name]):
                    try:
                        return float(data[name])
                    except (ValueError, TypeError):
                        continue
            return 0

        total_debt = get_field_value(["total_liabilities", "Total Liabilities Net Minority Interest", "TotalLiabilitiesNetMinorityInterest"], data)
        total_equity = get_field_value(["total_equity", "Stockholders Equity", "StockholdersEquity"], data)
        total_assets = get_field_value(["total_assets", "Total Assets", "totalAssets"], data)

        ratios = {}

        # Debt-to-Equity Ratio
        if total_equity != 0:
            ratios["debt_to_equity"] = round(total_debt / total_equity, 2)

        # Debt-to-Assets Ratio
        if total_assets != 0:
            ratios["debt_to_assets"] = round(total_debt / total_assets, 2)

        return ratios
    

    def _calculate_efficiency_ratios(self, balance_sheet: Dict[str, Any], 
                                   income_statement: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive efficiency ratios"""
        # Handle both raw Yahoo Finance data and normalized data
        def get_field_value(field_names, data):
            for name in field_names:
                if name in data and data[name] is not None and not pd.isna(data[name]):
                    try:
                        return float(data[name])
                    except (ValueError, TypeError):
                        continue
            return 0

        total_revenue = get_field_value(["total_revenue", "Total Revenue", "totalRevenue"], income_statement)
        total_assets = get_field_value(["total_assets", "Total Assets", "totalAssets"], balance_sheet)
        accounts_receivable = get_field_value(["accounts_receivable", "Accounts Receivable"], balance_sheet)
        inventory = get_field_value(["inventory", "Inventory", "Inventories"], balance_sheet)
        cost_of_goods_sold = get_field_value(["cost_of_goods_sold", "Cost Of Revenue", "CostOfRevenue"], income_statement)
        current_assets = get_field_value(["current_assets", "Current Assets", "CurrentAssets"], balance_sheet)
        current_liabilities = get_field_value(["current_liabilities", "Current Liabilities", "CurrentLiabilities"], balance_sheet)
        fixed_assets = get_field_value(["property_plant_equipment", "Property Plant Equipment", "PropertyPlantEquipment"], balance_sheet)

        ratios = {}

        # Asset Turnover
        if total_assets != 0:
            ratios["asset_turnover"] = round(total_revenue / total_assets, 2)

        # Fixed Asset Turnover
        if fixed_assets != 0:
            ratios["fixed_asset_turnover"] = round(total_revenue / fixed_assets, 2)

        # Receivables Turnover
        if accounts_receivable != 0:
            ratios["receivables_turnover"] = round(total_revenue / accounts_receivable, 2)

        # Inventory Turnover
        if inventory != 0:
            ratios["inventory_turnover"] = round(cost_of_goods_sold / inventory, 2)

        # Working Capital Turnover
        working_capital = current_assets - current_liabilities
        if working_capital != 0:
            ratios["working_capital_turnover"] = round(total_revenue / working_capital, 2)

        # Days Sales Outstanding (DSO)
        if accounts_receivable != 0 and total_revenue != 0:
            dso = (accounts_receivable / total_revenue) * 365
            ratios["days_sales_outstanding"] = round(dso, 1)

        # Days Inventory Outstanding (DIO)
        if inventory != 0 and cost_of_goods_sold != 0:
            dio = (inventory / cost_of_goods_sold) * 365
            ratios["days_inventory_outstanding"] = round(dio, 1)

        # Cash Conversion Cycle (advanced metric)
        if "days_sales_outstanding" in ratios and "days_inventory_outstanding" in ratios:
            # Simplified CCC (would need accounts payable days for complete calculation)
            ratios["cash_conversion_cycle"] = round(ratios["days_sales_outstanding"] + ratios["days_inventory_outstanding"], 1)

        return ratios
    def benford_analysis(self, financial_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform Benford's Law analysis on financial data"""
        try:
            # Extract all numerical values from financial statements
            all_numbers = []
            
            for statement in financial_data:
                data = statement.get("data", {})
                for key, value in data.items():
                    if isinstance(value, (int, float, Decimal)) and value > 0:
                        all_numbers.append(abs(float(value)))
            
            if len(all_numbers) < 10:  # Reduced for testing, but recommend 30+ for production
                return {
                    "success": False,
                    "error": "Insufficient data points for Benford analysis (minimum 10 for testing, 30+ recommended for production)"
                }
            
            # Extract first digits
            first_digits = [int(str(num)[0]) for num in all_numbers if str(num)[0].isdigit()]
            
            # Calculate observed frequencies
            observed_freq = np.zeros(9)
            for digit in first_digits:
                if 1 <= digit <= 9:
                    observed_freq[digit-1] += 1
            
            # Convert to percentages
            total_count = len(first_digits)
            observed_pct = (observed_freq / total_count) * 100
            
            # Expected Benford frequencies
            expected_pct = np.array([
                30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6
            ])
            
            # Chi-square test
            chi_square = np.sum(((observed_pct - expected_pct) ** 2) / expected_pct)
            
            # Critical value at 95% confidence (8 degrees of freedom)
            critical_value = 15.507
            
            # Determine if anomalous
            is_anomalous = chi_square > critical_value
            
            return {
                "success": True,
                "benford_analysis": {
                    "total_numbers_analyzed": total_count,
                    "observed_frequencies": observed_pct.tolist(),
                    "expected_frequencies": expected_pct.tolist(),
                    "chi_square_statistic": round(chi_square, 3),
                    "critical_value": critical_value,
                    "is_anomalous": is_anomalous,
                    "confidence_level": 0.95,
                    "interpretation": "ANOMALOUS" if is_anomalous else "NORMAL"
                },
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Benford analysis failed: {e}")
            return {"success": False, "error": str(e)}

    def analyze_gst_reconciliation(self, financial_statements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Feature 2: GST-Revenue Reconciliation
        Detects revenue inflation by comparing revenue growth vs GST output tax growth.
        """
        try:
            # Group by year to check growth
            yearly_data = []
            for stmt in financial_statements:
                if stmt.get("statement_type") == "income_statement":
                    data = stmt.get("data", {})
                    yearly_data.append({
                        "period": stmt.get("period_end"),
                        "revenue": data.get("total_revenue", 0),
                        # In real use, we'd extract GST from 'Tax Expense' or 'Other Indirect Taxes'
                        # For now, we simulate detection from indirect tax components
                        "indirect_taxes": data.get("tax_expense", 0) * 0.15 # Heuristic for indirect component if not split
                    })
            
            # Sort by period
            yearly_data.sort(key=lambda x: x["period"])
            
            if len(yearly_data) < 2:
                return {"success": False, "error": "Insufficient historical data for GST reconciliation"}
            
            reconciliation_results = []
            for i in range(1, len(yearly_data)):
                prev = yearly_data[i-1]
                curr = yearly_data[i]
                
                rev_growth = ((curr["revenue"] - prev["revenue"]) / prev["revenue"]) * 100 if prev["revenue"] != 0 else 0
                tax_growth = ((curr["indirect_taxes"] - prev["indirect_taxes"]) / prev["indirect_taxes"]) * 100 if prev["indirect_taxes"] != 0 else 0
                
                # Disconnect Detection
                # If Revenue grows > 20% faster than GST tax, flag as potential inflation
                is_disconnect = rev_growth > 20 and (rev_growth - tax_growth) > 15
                
                reconciliation_results.append({
                    "period": curr["period"],
                    "revenue_growth_pct": round(rev_growth, 2),
                    "gst_growth_pct": round(tax_growth, 2),
                    "is_disconnect": is_disconnect,
                    "risk_analysis": "Potential Sales Inflation detected (Revenue growing significantly faster than Tax output)" if is_disconnect else "Reconciliation normal"
                })
            
            return {
                "success": True,
                "reconciliation_results": reconciliation_results,
                "overall_risk_score": 80 if any(r["is_disconnect"] for r in reconciliation_results) else 0
            }

        except Exception as e:
            logger.error(f"GST Reconciliation failed: {e}")
            return {"success": False, "error": str(e)}

    def analyze_contingent_liabilities(self, balance_sheet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Feature 4: Contingent Liability "Debt Hider"
        Checks for hidden liabilities mentioned in notes that aren't on main balance sheet.
        """
        try:
            # In real scenario, this would be extracted from 'Notes to Accounts' by Auditor Agent
            # and passed here. For automated check, we look for common field names.
            contingent_liab = balance_sheet.get("contingent_liabilities", 0)
            total_equity = balance_sheet.get("total_equity", 0)
            
            if total_equity == 0:
                return {"success": False, "error": "Total equity is zero, cannot calculate ratio"}
            
            ratio = (contingent_liab / total_equity)
            
            # Risk Threshold: > 50% of Equity is high risk
            risk_level = "LOW"
            if ratio > 0.5:
                risk_level = "HIGH"
            elif ratio > 0.2:
                risk_level = "MEDIUM"
            
            return {
                "success": True,
                "contingent_liability_amount": contingent_liab,
                "equity_ratio": round(ratio, 4),
                "risk_level": risk_level,
                "interpretation": f"Contingent liabilities represent {round(ratio*100, 2)}% of net worth. " + 
                                ("HIGH RISK: Significant off-balance sheet exposure." if risk_level == "HIGH" else "Exposure within normal limits.")
            }
        except Exception as e:
            logger.error(f"Contingent liability analysis failed: {e}")
            return {"success": False, "error": str(e)}

    def analyze_remuneration_greed(self, financial_statements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Feature 3: Managerial Remuneration "Greed" Index
        Flags cases where executive pay increases are disconnected from company performance.
        """
        try:
            yearly_data = []
            for stmt in financial_statements:
                if stmt.get("statement_type") == "income_statement":
                    data = stmt.get("data", {})
                    yearly_data.append({
                        "period": stmt.get("period_end"),
                        "net_profit": data.get("net_income", 0),
                        # Remuneration is often under 'Selling General & Admin' or 'Employee Benefit Expenses'
                        # In real use, we'd extract specific 'Director Remuneration' from Auditor's text extraction
                        # For the engine, we look for 'executive_compensation' or heuristic
                        "remuneration": data.get("executive_compensation", data.get("total_revenue", 0) * 0.01), # Fallback to 1% of revenue as mock
                        "employee_expenses": data.get("employee_benefit_expense", 0)
                    })
            
            yearly_data.sort(key=lambda x: x["period"])
            
            if len(yearly_data) < 2:
                return {"success": False, "error": "Insufficient data for Greed Index"}
            
            greed_results = []
            for i in range(1, len(yearly_data)):
                prev = yearly_data[i-1]
                curr = yearly_data[i]
                
                pay_growth = ((curr["remuneration"] - prev["remuneration"]) / prev["remuneration"]) * 100 if prev["remuneration"] != 0 else 0
                profit_growth = ((curr["net_profit"] - prev["net_profit"]) / abs(prev["net_profit"])) * 100 if prev["net_profit"] != 0 else 0
                emp_growth = ((curr["employee_expenses"] - prev["employee_expenses"]) / prev["employee_expenses"]) * 100 if prev["employee_expenses"] != 0 else 0
                
                # Greed Metric: Pay Growth minus Profit Growth
                # If Pay up 20% and Profit down 10%, Discrepancy = 30
                discrepancy = pay_growth - profit_growth
                
                # Greed Metric 2: Pay Growth vs Employee Wage Growth
                wage_gap = pay_growth - emp_growth
                
                is_greedy = discrepancy > 25 or wage_gap > 30
                
                greed_results.append({
                    "period": curr["period"],
                    "exec_pay_growth_pct": round(pay_growth, 2),
                    "profit_growth_pct": round(profit_growth, 2),
                    "employee_cost_growth_pct": round(emp_growth, 2),
                    "is_greedy": is_greedy,
                    "greed_score": min(100, max(0, discrepancy + wage_gap)),
                    "risk_analysis": "EXCESSIVE: Pay rising while performance declining." if is_greedy else "Remuneration aligned with performance"
                })
            
            return {
                "success": True,
                "greed_results": greed_results,
                "overall_greed_index": max([r["greed_score"] for r in greed_results]) if greed_results else 0
            }
        except Exception as e:
            logger.error(f"Greed index analysis failed: {e}")
            return {"success": False, "error": str(e)}
    
    def calculate_altman_z_score(self, balance_sheet: Dict[str, Any], 
                                income_statement: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Altman Z-Score for bankruptcy prediction"""
        try:
            # Yahoo Finance uses different field names - need to map them
            # Extract required values with multiple possible field names

            # Total Assets - try multiple possible names
            total_assets = (
                balance_sheet.get("totalAssets") or
                balance_sheet.get("Total Assets") or
                balance_sheet.get("total_assets") or
                0
            )

            # Current Assets
            current_assets = (
                balance_sheet.get("totalCurrentAssets") or
                balance_sheet.get("Total Current Assets") or
                balance_sheet.get("current_assets") or
                0
            )

            # Current Liabilities
            current_liabilities = (
                balance_sheet.get("totalCurrentLiabilities") or
                balance_sheet.get("Total Current Liabilities") or
                balance_sheet.get("current_liabilities") or
                0
            )

            # Retained Earnings
            retained_earnings = (
                balance_sheet.get("retainedEarnings") or
                balance_sheet.get("Retained Earnings") or
                balance_sheet.get("retained_earnings") or
                balance_sheet.get("RetainedEarnings") or
                0
            )

            # Total Equity
            total_equity = (
                balance_sheet.get("totalStockholdersEquity") or
                balance_sheet.get("Total Stockholders Equity") or
                balance_sheet.get("Total Stockholder Equity") or  # Yahoo: Singular
                balance_sheet.get("Stockholders Equity") or       # Yahoo: Short
                balance_sheet.get("Stockholder Equity") or
                balance_sheet.get("total_equity") or
                balance_sheet.get("Total Equity Gross Minority Interest") or
                0
            )

            # Total Liabilities
            total_liabilities = (
                balance_sheet.get("totalLiabilities") or
                balance_sheet.get("Total Liabilities") or
                balance_sheet.get("Total Liabilities Net Minority Interest") or # Yahoo: Full
                balance_sheet.get("total_liabilities") or
                0
            )

            # Impute Total Liabilities if missing (critical for Z-Score)
            if total_liabilities == 0 and total_assets != 0:
                # Accounting Equation: Assets = Liabilities + Equity  =>  Liabilities = Assets - Equity
                # Note: Equity can be negative for distressed companies
                if total_equity != 0:
                    total_liabilities = total_assets - total_equity

            # Total Revenue
            total_revenue = (
                income_statement.get("totalRevenue") or
                income_statement.get("Total Revenue") or
                income_statement.get("total_revenue") or
                0
            )

            # EBIT (Operating Income)
            ebit = (
                income_statement.get("operatingIncome") or
                income_statement.get("Operating Income") or
                income_statement.get("operating_income") or
                0
            )

            if total_assets == 0:
                return {"success": False, "error": "Total assets cannot be zero"}

            # Calculate Z-Score components
            # A = Working Capital / Total Assets
            working_capital = current_assets - current_liabilities
            a_ratio = working_capital / total_assets

            # B = Retained Earnings / Total Assets
            b_ratio = retained_earnings / total_assets

            # C = EBIT / Total Assets
            c_ratio = ebit / total_assets

            # D = Market Value of Equity / Total Liabilities (using book value)
            if total_liabilities == 0:
                d_ratio = 10  # High value if no debt
            else:
                d_ratio = total_equity / total_liabilities

            # E = Sales / Total Assets
            e_ratio = total_revenue / total_assets

            # Calculate Z-Score: Z = 1.2A + 1.4B + 3.3C + 0.6D + 1.0E
            z_score = (1.2 * a_ratio + 1.4 * b_ratio + 3.3 * c_ratio +
                      0.6 * d_ratio + 1.0 * e_ratio)

            # Classification
            if z_score > 2.99:
                classification = "SAFE"
                risk_level = "LOW"
            elif z_score >= 1.81:
                classification = "GREY_ZONE"
                risk_level = "MEDIUM"
            else:
                classification = "DISTRESS"
                risk_level = "HIGH"

            return {
                "success": True,
                "altman_z_score": {
                    "z_score": round(z_score, 3),
                    "classification": classification,
                    "risk_level": risk_level,
                    "components": {
                        "working_capital_ratio": round(a_ratio, 3),
                        "retained_earnings_ratio": round(b_ratio, 3),
                        "ebit_ratio": round(c_ratio, 3),
                        "equity_to_debt_ratio": round(d_ratio, 3),
                        "sales_ratio": round(e_ratio, 3)
                    },
                    "interpretation": {
                        "SAFE": "Low bankruptcy risk",
                        "GREY_ZONE": "Moderate bankruptcy risk",
                        "DISTRESS": "High bankruptcy risk"
                    }[classification]
                },
                "analysis_date": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Altman Z-Score calculation failed: {e}")
            return {"success": False, "error": str(e)}

    def calculate_sloan_ratio(self, financial_statements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate Sloan Ratio (Accruals Ratio) to detect earnings quality issues.
        Formula: (Net Income - CFO) / Total Assets
        Result interpretation:
        - < 5%: Safe
        - 5-10%: Moderate Risk
        - > 10%: High Risk (Earnings are not backed by cash)
        """
        try:
            sloan_results = {}
            
            # Group statements by period
            statements_by_period = {}
            for stmt in financial_statements:
                period = stmt.get("period_end")
                stmt_type = stmt.get("statement_type")
                if period not in statements_by_period:
                    statements_by_period[period] = {}
                statements_by_period[period][stmt_type] = stmt.get("data", {})
            
            sorted_periods = sorted(statements_by_period.keys())
            
            for period in sorted_periods:
                period_data = statements_by_period[period]
                
                income_stmt = period_data.get("income_statement", {})
                balance_sheet = period_data.get("balance_sheet", {})
                cash_flow = period_data.get("cash_flow_statement", {})
                
                if not (income_stmt and balance_sheet and cash_flow):
                    continue
                    
                net_income = income_stmt.get("net_profit", 0)
                cfo = cash_flow.get("operating_cash_flow", 0)
                total_assets = balance_sheet.get("total_assets", 0)
                
                # Check for zero assets to avoid division by zero
                if total_assets == 0:
                    continue
                    
                # Accruals = Net Income - CFO
                accruals = net_income - cfo
                
                # Sloan Ratio = Accruals / Total Assets
                sloan_ratio = (accruals / total_assets)
                sloan_pct = sloan_ratio * 100
                
                risk_level = "LOW"
                if sloan_pct > 10 or sloan_pct < -10:
                     risk_level = "HIGH"
                elif sloan_pct > 5 or sloan_pct < -5:
                     risk_level = "MEDIUM"
                     
                sloan_results[period] = {
                    "net_income": net_income,
                    "operating_cash_flow": cfo,
                    "accruals": accruals,
                    "total_assets": total_assets,
                    "sloan_ratio_pct": round(sloan_pct, 2),
                    "risk_level": risk_level,
                    "interpretation": "High probability of earnings manipulation (High Accruals)" if risk_level == "HIGH" else "Safe"
                }
                
            return {
                "success": True,
                "sloan_analysis": sloan_results,
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Sloan Ratio calculation failed: {e}")
            return {"success": False, "error": str(e)}

    def calculate_dechow_f_score(self, financial_statements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate Dechow F-Score (Misstatement Prediction Model).
        Formula (Model 1):
        Probability = 1 / (1 + e^-Predicted_Value)
        Predicted_Value = -7.893 + 0.790 * RSST + 2.518 * Chg_Rec + 1.191 * Chg_Inv + 1.979 * Soft_Assets + 0.171 * Chg_Cash_Sales + -0.932 * Chg_ROA + 1.029 * Issue_Stock
        
        Where:
        - RSST = (WC_Change + NCO_Change + FIN_Change) / Average Assets
        """
        try:
            f_score_results = {}
            
            # Group statements
            statements_by_period = {}
            for stmt in financial_statements:
                period = stmt.get("period_end")
                stmt_type = stmt.get("statement_type")
                if period not in statements_by_period:
                    statements_by_period[period] = {}
                statements_by_period[period][stmt_type] = stmt.get("data", {})
            
            sorted_periods = sorted(statements_by_period.keys())
            
            # We need at least 2 periods for changes
            if len(sorted_periods) < 2:
                return {"success": False, "error": "Insufficient data for Dechow F-Score"}
            
            for i in range(1, len(sorted_periods)):
                curr_period = sorted_periods[i]
                prev_period = sorted_periods[i-1]
                
                curr_data = statements_by_period[curr_period]
                prev_data = statements_by_period[prev_period]
                
                # Helpers to extract data safely
                def get_val(data, type, field):
                    return float(data.get(type, {}).get(field, 0))
                
                # 1. RSST Accruals
                # Proxy: (Change in WC + Change in NCO + Change in FIN)
                # Simplified Proxy commonly used: (Net Income - CFO - CFI) / Avg Assets 
                # (Note: This is a rough proxy. We will use a component based approach if possible)
                # Let's use the explicit RSST definition if we have balance sheet items.
                
                avg_assets = (get_val(curr_data, "balance_sheet", "total_assets") + get_val(prev_data, "balance_sheet", "total_assets")) / 2
                if avg_assets == 0: continue

                # Change in Receivables (REC)
                curr_rec = get_val(curr_data, "balance_sheet", "accounts_receivable")
                prev_rec = get_val(prev_data, "balance_sheet", "accounts_receivable")
                chg_rec = (curr_rec - prev_rec) / avg_assets
                
                # Change in Inventory (INV)
                curr_inv = get_val(curr_data, "balance_sheet", "inventory")
                prev_inv = get_val(prev_data, "balance_sheet", "inventory")
                chg_inv = (curr_inv - prev_inv) / avg_assets
                
                # Soft Assets
                # (Total Assets - PPE - Cash) / Total Assets
                curr_assets = get_val(curr_data, "balance_sheet", "total_assets")
                curr_ppe = get_val(curr_data, "balance_sheet", "property_plant_equipment")
                curr_cash = get_val(curr_data, "balance_sheet", "cash_and_equivalents")
                soft_assets = (curr_assets - curr_ppe - curr_cash) / curr_assets if curr_assets != 0 else 0
                
                # Change in Cash Sales
                # Cash Sales = Revenue - Change in Receivables
                curr_rev = get_val(curr_data, "income_statement", "total_revenue")
                prev_rev = get_val(prev_data, "income_statement", "total_revenue")
                curr_cash_sales = curr_rev - (curr_rec - prev_rec)
                prev_rec_prev = 0 # Need 3 periods for prev_cash_sales properly? 
                # Simplification: Change in Sales
                chg_cash_sales = (curr_cash_sales - prev_rev) / prev_rev if prev_rev != 0 else 0
                
                # Change in ROA
                curr_roa = get_val(curr_data, "income_statement", "net_profit") / ((get_val(curr_data, "balance_sheet", "total_assets") + get_val(prev_data, "balance_sheet", "total_assets"))/2)
                prev_roa = 0 # Limitation without 3 periods. We assume flat previous or 0? 
                # Better: Use available data. If i > 1, calculate prev_roa.
                if i > 1:
                   prev_prev = sorted_periods[i-2]
                   prev_prev_data = statements_by_period[prev_prev]
                   prev_avg_assets = (get_val(prev_data, "balance_sheet", "total_assets") + get_val(prev_prev_data, "balance_sheet", "total_assets")) / 2
                   prev_roa = get_val(prev_data, "income_statement", "net_profit") / prev_avg_assets
                else:
                   prev_roa = curr_roa # Fallback to 0 change
                
                chg_roa = curr_roa - prev_roa
                
                # Issuance of Stock
                # Check specific field or Change in Equity not explained by Net Income
                 # Actual = 1 if stock issued, 0 otherwise. Proxy: Check if Common Stock increased?
                stock_issued = 1 if (get_val(curr_data, "balance_sheet", "common_stock") > get_val(prev_data, "balance_sheet", "common_stock")) else 0
                
                # RSST Accruals (Richardson, Sloan, Soliman, Tuna 2005)
                # RSST = (WC + NCO + FIN) / Avg Assets
                # WC = Current Assets - Cash - (Current Liabilities - ST Debt)
                wc_curr = (get_val(curr_data, "balance_sheet", "current_assets") - curr_cash) - (get_val(curr_data, "balance_sheet", "current_liabilities") - get_val(curr_data, "balance_sheet", "short_term_debt"))
                nco_curr = (curr_assets - get_val(curr_data, "balance_sheet", "current_assets") - get_val(curr_data, "balance_sheet", "investments")) - (get_val(curr_data, "balance_sheet", "total_liabilities") - get_val(curr_data, "balance_sheet", "current_liabilities") - get_val(curr_data, "balance_sheet", "long_term_debt"))
                fin_curr = (get_val(curr_data, "balance_sheet", "short_term_investments") + get_val(curr_data, "balance_sheet", "investments")) - (get_val(curr_data, "balance_sheet", "short_term_debt") + get_val(curr_data, "balance_sheet", "long_term_debt"))
                
                rsst_accruals = (wc_curr + nco_curr + fin_curr) / avg_assets

                # Calculate Score
                pred_val = -7.893 + (0.790 * rsst_accruals) + (2.518 * chg_rec) + (1.191 * chg_inv) + (1.979 * soft_assets) + (0.171 * chg_cash_sales) + (-0.932 * chg_roa) + (1.029 * stock_issued)
                
                prob = 1 / (1 + math.exp(-pred_val))
                
                # Risk Level
                # F-Score > 1.0 (some papers normalize differently). 
                # Probability > 0.0037 is average misstatement rate. 
                # Prob > 1% (0.01) is High Risk, > 0.4% is elevated.
                
                risk_level = "LOW"
                if prob > 0.02: # > 2% probability of material misstatement
                     risk_level = "HIGH"
                elif prob > 0.01:
                     risk_level = "MEDIUM"
                
                f_score_results[curr_period] = {
                    "f_score": round(prob, 5),
                    "predicted_value": round(pred_val, 3),
                    "risk_level": risk_level,
                    "components": {
                        "rsst_accruals": round(rsst_accruals, 3),
                        "chg_receivables": round(chg_rec, 3),
                        "chg_inventory": round(chg_inv, 3),
                        "soft_assets": round(soft_assets, 3),
                        "chg_cash_sales": round(chg_cash_sales, 3),
                        "chg_roa": round(chg_roa, 3),
                        "stock_issued": stock_issued
                    }
                }

            return {
                "success": True,
                "dechow_f_score": f_score_results,
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Dechow F-Score calculation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def calculate_beneish_m_score(self, current_period: Dict[str, Any], 
                                 previous_period: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Beneish M-Score for earnings manipulation detection using proper field mapping"""
        try:
            # Extract current period data with proper field mapping
            curr_revenue = current_period.get("totalRevenue") or current_period.get("Total Revenue") or 0
            curr_receivables = (current_period.get("netReceivables") or 
                              current_period.get("Net Receivables") or 
                              current_period.get("totalCurrentAssets") or # Fallback
                              current_period.get("Total Current Assets") or 
                              0)
            curr_gross_profit = current_period.get("grossProfit") or current_period.get("Gross Profit") or 0
            curr_total_assets = current_period.get("totalAssets") or current_period.get("Total Assets") or 0
            curr_sga = (current_period.get("sellingGeneralAdministrative") or 
                       current_period.get("Selling General And Administration") or 
                       current_period.get("SG&A Expense") or 
                       0)
            curr_depreciation = (current_period.get("depreciation") or 
                               current_period.get("Depreciation And Amortization In Income Statement") or
                               current_period.get("Depreciation And Amortization") or
                               0)
            curr_current_assets = (current_period.get("totalCurrentAssets") or 
                                 current_period.get("Total Current Assets") or 
                                 current_period.get("current_assets") or 
                                 0)
            curr_ppe = (current_period.get("netPPE") or 
                      current_period.get("Net PPE") or 
                      current_period.get("pp_and_e_net") or 
                      0)
            curr_securities = (current_period.get("investments") or 
                             current_period.get("Investments") or 
                             0) # Simplified
            curr_current_liabilities = (current_period.get("totalCurrentLiabilities") or 
                                      current_period.get("Total Current Liabilities") or 
                                      current_period.get("current_liabilities") or 
                                      0)
            curr_lt_debt = (current_period.get("longTermDebt") or 
                          current_period.get("Long Term Debt") or 
                          current_period.get("long_term_debt") or 
                          0)
            curr_net_income = (current_period.get("netIncome") or 
                             current_period.get("Net Income") or 
                             current_period.get("net_profit") or 
                             0)
            curr_cash_ops = (current_period.get("totalCashFromOperatingActivities") or 
                           current_period.get("Total Cash From Operating Activities") or 
                           current_period.get("operating_cash_flow") or 
                           0)

            # Extract previous period data with proper field mapping
            prev_revenue = previous_period.get("totalRevenue") or previous_period.get("Total Revenue") or 0
            prev_receivables = (previous_period.get("netReceivables") or 
                              previous_period.get("Net Receivables") or 
                              previous_period.get("totalCurrentAssets") or 
                              previous_period.get("Total Current Assets") or 
                              0)
            prev_gross_profit = previous_period.get("grossProfit") or previous_period.get("Gross Profit") or 0
            prev_total_assets = previous_period.get("totalAssets") or previous_period.get("Total Assets") or 0
            prev_sga = (previous_period.get("sellingGeneralAdministrative") or 
                       previous_period.get("Selling General And Administration") or 
                       previous_period.get("SG&A Expense") or 
                       0)
            prev_depreciation = (previous_period.get("depreciation") or 
                               previous_period.get("Depreciation And Amortization In Income Statement") or
                               previous_period.get("Depreciation And Amortization") or
                               0)
            prev_current_assets = (previous_period.get("totalCurrentAssets") or 
                                 previous_period.get("Total Current Assets") or 
                                 previous_period.get("current_assets") or 
                                 0)
            prev_ppe = (previous_period.get("netPPE") or 
                      previous_period.get("Net PPE") or 
                      previous_period.get("pp_and_e_net") or 
                      0)
            prev_securities = (previous_period.get("investments") or 
                             previous_period.get("Investments") or 
                             0) # Simplified
            prev_current_liabilities = (previous_period.get("totalCurrentLiabilities") or 
                                      previous_period.get("Total Current Liabilities") or 
                                      previous_period.get("current_liabilities") or 
                                      0)
            prev_lt_debt = (previous_period.get("longTermDebt") or 
                          previous_period.get("Long Term Debt") or 
                          previous_period.get("long_term_debt") or 
                          0)

            # Calculate all 8 M-Score variables
            variables = {}

            # 1. DSRI (Days Sales in Receivables Index)
            if curr_revenue != 0 and prev_revenue != 0:
                dsri_curr = curr_receivables / curr_revenue
                dsri_prev = prev_receivables / prev_revenue
                variables["DSRI"] = dsri_curr / dsri_prev if dsri_prev != 0 else 1
            else:
                variables["DSRI"] = 1

            # 2. GMI (Gross Margin Index)
            if curr_revenue != 0 and prev_revenue != 0:
                gm_prev = prev_gross_profit / prev_revenue
                gm_curr = curr_gross_profit / curr_revenue
                variables["GMI"] = gm_prev / gm_curr if gm_curr != 0 else 1
            else:
                variables["GMI"] = 1

            # 3. AQI (Asset Quality Index)
            if curr_total_assets != 0 and prev_total_assets != 0:
                # Non-Current Assets approx = Total - Current - PPE - Securities
                # Actually AQI definition: (1 - (Current Assets + PPE + Securities)/Total Assets)
                aq_curr = 1 - ((curr_current_assets + curr_ppe + curr_securities) / curr_total_assets)
                aq_prev = 1 - ((prev_current_assets + prev_ppe + prev_securities) / prev_total_assets)
                variables["AQI"] = aq_curr / aq_prev if aq_prev != 0 else 1
            else:
                variables["AQI"] = 1

            # 4. SGI (Sales Growth Index)
            variables["SGI"] = curr_revenue / prev_revenue if prev_revenue != 0 else 1

            # 5. DEPI (Depreciation Index)
            # Rate = Depreciation / (PPE + Depreciation)
            if (curr_ppe + curr_depreciation) != 0 and (prev_ppe + prev_depreciation) != 0:
                dep_rate_curr = curr_depreciation / (curr_ppe + curr_depreciation)
                dep_rate_prev = prev_depreciation / (prev_ppe + prev_depreciation)
                variables["DEPI"] = dep_rate_prev / dep_rate_curr if dep_rate_curr != 0 else 1
            else:
                variables["DEPI"] = 1

            # 6. SGAI (SG&A Index)
            if curr_revenue != 0 and prev_revenue != 0:
                sga_rate_curr = curr_sga / curr_revenue
                sga_rate_prev = prev_sga / prev_revenue
                variables["SGAI"] = sga_rate_curr / sga_rate_prev if sga_rate_prev != 0 else 1
            else:
                variables["SGAI"] = 1

            # 7. LVGI (Leverage Index)
            if curr_total_assets != 0 and prev_total_assets != 0:
                lev_curr = (curr_current_liabilities + curr_lt_debt) / curr_total_assets
                lev_prev = (prev_current_liabilities + prev_lt_debt) / prev_total_assets
                variables["LVGI"] = lev_curr / lev_prev if lev_prev != 0 else 1
            else:
                variables["LVGI"] = 1

            # 8. TATA (Total Accruals to Total Assets)
            # Accruals = Net Income - Cash from Ops (Simplified)
            if curr_total_assets != 0:
                accruals = curr_net_income - curr_cash_ops
                variables["TATA"] = accruals / curr_total_assets
            else:
                variables["TATA"] = 0

            # Calculate proper M-Score
            m_score = (-4.84 + 0.92 * variables["DSRI"] + 0.528 * variables["GMI"] +
                      0.404 * variables["AQI"] + 0.892 * variables["SGI"] +
                      0.115 * variables["DEPI"] - 0.172 * variables["SGAI"] +
                      4.679 * variables["TATA"] - 0.327 * variables["LVGI"])

            # Classification
            is_manipulator = m_score > -1.78
            risk_level = "HIGH" if is_manipulator else "LOW"

            return {
                "success": True,
                "beneish_m_score": {
                    "m_score": round(m_score, 3),
                    "threshold": -1.78,
                    "is_likely_manipulator": is_manipulator,
                    "risk_level": risk_level,
                    "variables": {k: round(v, 3) for k, v in variables.items()},
                    "interpretation": "High probability of earnings manipulation" if is_manipulator
                                   else "Low probability of earnings manipulation"
                },
                "analysis_date": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Beneish M-Score calculation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _to_float(self, v: Any) -> float:
        """Safely convert numbers (including Decimal) to float. Returns 0.0 on failure."""
        try:
            if v is None:
                return 0.0
            return float(v)
        except Exception:
            try:
                return float(str(v))
            except Exception:
                return 0.0

    def detect_anomalies(self, financial_statements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect financial anomalies using rule-based checks"""
        try:
            anomalies = []
            
            # Sort statements by period
            sorted_statements = sorted(financial_statements, 
                                     key=lambda x: x.get("period_end", ""))
            
            for i, statement in enumerate(sorted_statements):
                data = statement.get("data", {})
                period = statement.get("period_end")
                
                # Check for revenue decline
                if i > 0:
                    prev_data = sorted_statements[i-1].get("data", {})
                    revenue_anomalies = self._check_revenue_anomalies(data, prev_data, period)
                    anomalies.extend(revenue_anomalies)
                
                # Check for profit-cash flow divergence
                cash_anomalies = self._check_cash_flow_anomalies(data, period)
                anomalies.extend(cash_anomalies)
                
                # Check for receivables buildup
                receivables_anomalies = self._check_receivables_anomalies(data, period)
                anomalies.extend(receivables_anomalies)
            
            return {
                "success": True,
                "anomalies_detected": len(anomalies),
                "anomalies": anomalies,
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _check_revenue_anomalies(self, current: Dict[str, Any], 
                                previous: Dict[str, Any], period: str) -> List[Dict[str, Any]]:
        """Check for revenue-related anomalies"""
        anomalies = []
        
        curr_revenue = current.get("total_revenue", 0)
        prev_revenue = previous.get("total_revenue", 0)
        
        if prev_revenue > 0:
            revenue_growth = ((curr_revenue - prev_revenue) / prev_revenue) * 100
            
            # Flag significant revenue decline
            if revenue_growth < -20:
                anomalies.append({
                    "type": "REVENUE_DECLINE",
                    "severity": "HIGH",
                    "period": period,
                    "description": f"Revenue declined by {abs(revenue_growth):.1f}%",
                    "evidence": {
                        "current_revenue": curr_revenue,
                        "previous_revenue": prev_revenue,
                        "growth_rate": revenue_growth
                    }
                })
        
        return anomalies
    
    def _check_cash_flow_anomalies(self, data: Dict[str, Any], period: str) -> List[Dict[str, Any]]:
        """Check for cash flow related anomalies"""
        anomalies = []
        
        net_profit = data.get("net_profit", 0)
        operating_cash_flow = data.get("operating_cash_flow", 0)
        
        # Check profit-cash flow divergence
        if net_profit > 0 and operating_cash_flow < net_profit * 0.5:
            anomalies.append({
                "type": "PROFIT_CASH_DIVERGENCE",
                "severity": "MEDIUM",
                "period": period,
                "description": "Operating cash flow significantly lower than net profit",
                "evidence": {
                    "net_profit": net_profit,
                    "operating_cash_flow": operating_cash_flow,
                    "cash_to_profit_ratio": operating_cash_flow / net_profit if net_profit != 0 else 0
                }
            })
        
        return anomalies
    
    def _check_receivables_anomalies(self, data: Dict[str, Any], period: str) -> List[Dict[str, Any]]:
        """Check for receivables buildup anomalies"""
        anomalies = []
        
        total_revenue = data.get("total_revenue", 0)
        accounts_receivable = data.get("accounts_receivable", 0)
        
        # Check receivables as percentage of revenue
        if total_revenue > 0:
            receivables_ratio = (accounts_receivable / total_revenue) * 100
            
            # Flag if receivables > 25% of revenue
            if receivables_ratio > 25:
                anomalies.append({
                    "type": "RECEIVABLES_BUILDUP",
                    "severity": "MEDIUM",
                    "period": period,
                    "description": f"Accounts receivable is {receivables_ratio:.1f}% of revenue",
                    "evidence": {
                        "accounts_receivable": accounts_receivable,
                        "total_revenue": total_revenue,
                        "receivables_ratio": receivables_ratio
                    }
                })
        
        return anomalies
    
    def comprehensive_forensic_analysis(self, company_id: str, 
                                      financial_statements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comprehensive forensic analysis"""
        try:
            results = {
                "company_id": company_id,
                "analysis_date": datetime.now().isoformat(),
                "success": True
            }
            
            # Vertical Analysis
            vertical_result = self.vertical_analysis(financial_statements)
            results["vertical_analysis"] = vertical_result
            
            # Horizontal Analysis
            horizontal_result = self.horizontal_analysis(financial_statements)
            results["horizontal_analysis"] = horizontal_result
            
            # Financial Ratios
            ratios_result = self.calculate_financial_ratios(financial_statements)
            results["financial_ratios"] = ratios_result

            # Sloan Ratio
            sloan_result = self.calculate_sloan_ratio(financial_statements)
            results["sloan_ratio"] = sloan_result

            # Dechow F-Score
            f_score_result = self.calculate_dechow_f_score(financial_statements)
            results["dechow_f_score"] = f_score_result
            
            # Benford's Law Analysis
            benford_result = self.benford_analysis(financial_statements)
            results["benford_analysis"] = benford_result
            
            # Altman Z-Score (Historical Analysis)
            z_score_history = []
            latest_z_score = None
            
            # Group statements by period for Z-score calculation
            statements_by_period = {}
            for statement in financial_statements:
                period = statement.get("period_end")
                stmt_type = statement.get("statement_type")
                if period not in statements_by_period:
                    statements_by_period[period] = {}
                statements_by_period[period][stmt_type] = statement.get("data", {})
            
            # Sort periods chronologically
            sorted_periods = sorted(statements_by_period.keys())
            
            for period in sorted_periods:
                period_data = statements_by_period[period]
                bs_data = period_data.get("balance_sheet", {})
                is_data = period_data.get("income_statement", {})
                
                if bs_data and is_data:
                    z_result = self.calculate_altman_z_score(bs_data, is_data)
                    
                    if z_result.get("success"):
                        # Add period info to the result
                        z_data = z_result.get("altman_z_score", {})
                        z_data["period"] = period
                        z_score_history.append(z_data)
            
            # Use the most recent period for the main display, but include history
            if z_score_history:
                # The last item in sorted list is the most recent
                latest_z_score_data = z_score_history[-1]
                
                results["altman_z_score"] = {
                    "z_score": latest_z_score_data["z_score"],
                    "classification": latest_z_score_data["classification"],
                    "risk_level": latest_z_score_data["risk_level"],
                    "components": latest_z_score_data["components"],
                    "interpretation": latest_z_score_data["interpretation"],
                    "historical_z_scores": z_score_history
                }
            
            # Beneish M-Score (if we have multiple periods)
            m_score_history = []
            
            if len(sorted_periods) >= 2:
                # We need at least 2 periods for comparison
                # Reverse iterate to calculate history (Newest to Oldest pairs)
                # i goes from N-1 down to 1
                for i in range(len(sorted_periods) - 1, 0, -1):
                    current_period_date = sorted_periods[i]
                    prev_period_date = sorted_periods[i-1]
                    
                    # Find statements for these periods
                    curr_bs = next((s for s in financial_statements 
                                  if s.get("statement_type") == "balance_sheet" and 
                                     s.get("period_end") == current_period_date), None)
                    curr_is = next((s for s in financial_statements 
                                  if s.get("statement_type") == "income_statement" and 
                                     s.get("period_end") == current_period_date), None)
                                     
                    prev_bs = next((s for s in financial_statements 
                                  if s.get("statement_type") == "balance_sheet" and 
                                     s.get("period_end") == prev_period_date), None)
                    prev_is = next((s for s in financial_statements 
                                  if s.get("statement_type") == "income_statement" and 
                                     s.get("period_end") == prev_period_date), None)
                                     
                    if curr_bs and curr_is and prev_bs and prev_is:
                        # Combine BS and IS data for the calculation method
                        curr_data = {**curr_bs.get("data", {}), **curr_is.get("data", {})}
                        prev_data = {**prev_bs.get("data", {}), **prev_is.get("data", {})}
                        
                        m_result = self.calculate_beneish_m_score(curr_data, prev_data)
                        
                        if m_result.get("success"):
                            m_data = m_result.get("beneish_m_score", {})
                            m_data["period"] = current_period_date
                            m_score_history.append(m_data)

            # Sort history by date (ascending)
            m_score_history.sort(key=lambda x: x.get("period", ""))

            if m_score_history:
                latest_m_score_data = m_score_history[-1]
                results["beneish_m_score"] = {
                    "success": True,
                    "beneish_m_score": {
                        "m_score": latest_m_score_data["m_score"],
                        "threshold": latest_m_score_data["threshold"],
                        "is_likely_manipulator": latest_m_score_data["is_likely_manipulator"],
                        "risk_level": latest_m_score_data["risk_level"],
                        "variables": latest_m_score_data["variables"],
                        "interpretation": latest_m_score_data["interpretation"],
                        "historical_m_scores": m_score_history
                    },
                    "analysis_date": datetime.now().isoformat()
                }
            else:
                results["beneish_m_score"] = {
                    "success": False, 
                    "error": "Insufficient data for M-Score analysis (need at least 2 consecutive periods)",
                    "analysis_date": datetime.now().isoformat()
                }
            
            # Anomaly Detection
            anomalies_result = self.detect_anomalies(financial_statements)
            results["anomaly_detection"] = anomalies_result

            # Feature 2: GST-Revenue Reconciliation
            gst_result = self.analyze_gst_reconciliation(financial_statements)
            results["gst_reconciliation"] = gst_result

            # Feature 4: Contingent Liability Analysis
            latest_bs = None
            for stmt in reversed(financial_statements):
                if stmt.get("statement_type") == "balance_sheet":
                    latest_bs = stmt.get("data", {})
                    break
            
            if latest_bs:
                cl_result = self.analyze_contingent_liabilities(latest_bs)
                results["contingent_liability_risk"] = cl_result

            # Feature 3: Greed Index
            greed_result = self.analyze_remuneration_greed(financial_statements)
            results["greed_index"] = greed_result
            
            return results
            
        except Exception as e:
            logger.error(f"Comprehensive forensic analysis failed: {e}")
            return {"success": False, "error": str(e)}

    async def comprehensive_forensic_analysis_realtime(
        self,
        company_id: str,
        financial_statements: List[Dict[str, Any]],
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Perform comprehensive forensic analysis with real-time progress updates"""
        try:
            results = {
                "company_id": company_id,
                "analysis_date": datetime.now().isoformat(),
                "success": True,
                "progress": 0,
                "current_step": "Initializing analysis..."
            }

            if progress_callback:
                await asyncio.sleep(0.1)  # Allow other tasks
                progress_callback(results.copy())

            # Step 1: Vertical Analysis (20%)
            results["progress"] = 10
            results["current_step"] = "Performing vertical analysis..."
            if progress_callback:
                await asyncio.sleep(0.1)
                progress_callback(results.copy())

            vertical_result = self.vertical_analysis(financial_statements)
            results["vertical_analysis"] = vertical_result

            results["progress"] = 20
            results["current_step"] = "Vertical analysis completed"
            if progress_callback:
                await asyncio.sleep(0.1)
                progress_callback(results.copy())

            # Step 2: Horizontal Analysis (40%)
            results["progress"] = 30
            results["current_step"] = "Performing horizontal analysis..."
            if progress_callback:
                await asyncio.sleep(0.1)
                progress_callback(results.copy())

            horizontal_result = self.horizontal_analysis(financial_statements)
            results["horizontal_analysis"] = horizontal_result

            results["progress"] = 40
            results["current_step"] = "Horizontal analysis completed"
            if progress_callback:
                await asyncio.sleep(0.1)
                progress_callback(results.copy())

            # Step 3: Financial Ratios (60%)
            results["progress"] = 50
            results["current_step"] = "Calculating financial ratios..."
            if progress_callback:
                await asyncio.sleep(0.1)
                progress_callback(results.copy())

            ratios_result = self.calculate_financial_ratios(financial_statements)
            results["financial_ratios"] = ratios_result

            results["progress"] = 60
            results["current_step"] = "Financial ratios calculated"
            if progress_callback:
                await asyncio.sleep(0.1)
                progress_callback(results.copy())

            # Step 4: Benford's Law Analysis (80%)
            results["progress"] = 70
            results["current_step"] = "Performing Benford's Law analysis..."
            if progress_callback:
                await asyncio.sleep(0.1)
                progress_callback(results.copy())

            benford_result = self.benford_analysis(financial_statements)
            results["benford_analysis"] = benford_result

            results["progress"] = 80
            results["current_step"] = "Benford's Law analysis completed"
            if progress_callback:
                await asyncio.sleep(0.1)
                progress_callback(results.copy())

            # Step 5: Altman Z-Score (90%)
            results["progress"] = 85
            results["current_step"] = "Calculating Altman Z-Score..."
            if progress_callback:
                await asyncio.sleep(0.1)
                progress_callback(results.copy())

            balance_sheet = next((s for s in financial_statements
                                if s.get("statement_type") == "balance_sheet"), None)
            income_statement = next((s for s in financial_statements
                                   if s.get("statement_type") == "income_statement"), None)

            if balance_sheet and income_statement:
                z_score_result = self.calculate_altman_z_score(
                    balance_sheet.get("data", {}),
                    income_statement.get("data", {})
                )
                results["altman_z_score"] = z_score_result

            results["progress"] = 90
            results["current_step"] = "Altman Z-Score calculated"
            if progress_callback:
                await asyncio.sleep(0.1)
                progress_callback(results.copy())

            # Step 6: Beneish M-Score (95%)
            results["progress"] = 93
            results["current_step"] = "Calculating Beneish M-Score..."
            if progress_callback:
                await asyncio.sleep(0.1)
                progress_callback(results.copy())

            if len(financial_statements) >= 2:
                # Use the detailed M-Score calculation with proper variable extraction
                current_period = financial_statements[-1].get("data", {})
                previous_period = financial_statements[-2].get("data", {})

                # Extract current period data with proper field mapping
                curr_revenue = current_period.get("totalRevenue") or current_period.get("Total Revenue") or 0
                curr_receivables = current_period.get("totalCurrentAssets") or current_period.get("Total Current Assets") or 0
                curr_gross_profit = current_period.get("grossProfit") or current_period.get("Gross Profit") or 0
                curr_total_assets = current_period.get("totalAssets") or current_period.get("Total Assets") or 0
                curr_sga = current_period.get("sellingGeneralAdministrative") or current_period.get("SG&A Expense") or 0
                curr_depreciation = current_period.get("depreciation") or 0

                # Extract previous period data with proper field mapping
                prev_revenue = previous_period.get("totalRevenue") or previous_period.get("Total Revenue") or 0
                prev_receivables = previous_period.get("totalCurrentAssets") or previous_period.get("Total Current Assets") or 0
                prev_gross_profit = previous_period.get("grossProfit") or previous_period.get("Gross Profit") or 0
                prev_total_assets = previous_period.get("totalAssets") or previous_period.get("Total Assets") or 0
                prev_sga = previous_period.get("sellingGeneralAdministrative") or previous_period.get("SG&A Expense") or 0
                prev_depreciation = previous_period.get("depreciation") or 0

                # Calculate all 8 M-Score variables
                variables = {}

                # 1. DSRI (Days Sales in Receivables Index)
                if curr_revenue != 0 and prev_revenue != 0:
                    dsri_curr = curr_receivables / curr_revenue
                    dsri_prev = prev_receivables / prev_revenue
                    variables["DSRI"] = dsri_curr / dsri_prev if dsri_prev != 0 else 1
                else:
                    variables["DSRI"] = 1

                # 2. GMI (Gross Margin Index)
                if curr_revenue != 0 and prev_revenue != 0:
                    gm_prev = prev_gross_profit / prev_revenue
                    gm_curr = curr_gross_profit / curr_revenue
                    variables["GMI"] = gm_prev / gm_curr if gm_curr != 0 else 1
                else:
                    variables["GMI"] = 1

                # 3. AQI (Asset Quality Index) - Simplified for this implementation
                variables["AQI"] = 1

                # 4. SGI (Sales Growth Index)
                variables["SGI"] = curr_revenue / prev_revenue if prev_revenue != 0 else 1

                # 5. DEPI (Depreciation Index) - Simplified for this implementation
                variables["DEPI"] = 1

                # 6. SGAI (SG&A Index)
                if curr_revenue != 0 and prev_revenue != 0:
                    sga_rate_curr = curr_sga / curr_revenue
                    sga_rate_prev = prev_sga / prev_revenue
                    variables["SGAI"] = sga_rate_curr / sga_rate_prev if sga_rate_prev != 0 else 1
                else:
                    variables["SGAI"] = 1

                # 7. LVGI (Leverage Index) - Simplified for this implementation
                variables["LVGI"] = 1

                # 8. TATA (Total Accruals to Total Assets) - Simplified for this implementation
                variables["TATA"] = 0

                # Calculate proper M-Score
                m_score = (-4.84 + 0.92 * variables["DSRI"] + 0.528 * variables["GMI"] +
                          0.404 * variables["AQI"] + 0.892 * variables["SGI"] +
                          0.115 * variables["DEPI"] - 0.172 * variables["SGAI"] +
                          4.679 * variables["TATA"] - 0.327 * variables["LVGI"])

                # Classification
                is_manipulator = m_score > -1.78
                risk_level = "HIGH" if is_manipulator else "LOW"

                results["beneish_m_score"] = {
                    "success": True,
                    "beneish_m_score": {
                        "m_score": round(m_score, 3),
                        "threshold": -1.78,
                        "is_likely_manipulator": is_manipulator,
                        "risk_level": risk_level,
                        "variables": {k: round(v, 3) for k, v in variables.items()},
                        "interpretation": "High probability of earnings manipulation" if is_manipulator
                                       else "Low probability of earnings manipulation"
                    },
                    "analysis_date": datetime.now().isoformat()
                }

            results["progress"] = 95
            results["current_step"] = "Beneish M-Score calculated"
            if progress_callback:
                await asyncio.sleep(0.1)
                progress_callback(results.copy())

            # Step 7: Anomaly Detection (100%)
            results["progress"] = 98
            results["current_step"] = "Detecting anomalies..."
            if progress_callback:
                await asyncio.sleep(0.1)
                progress_callback(results.copy())

            anomalies_result = self.detect_anomalies(financial_statements)
            results["anomaly_detection"] = anomalies_result

            results["progress"] = 100
            results["current_step"] = "Analysis completed successfully!"
            if progress_callback:
                await asyncio.sleep(0.1)
                progress_callback(results.copy())

            yield results

        except Exception as e:
            logger.error(f"Real-time forensic analysis failed: {e}")
            error_result = {
                "success": False,
                "error": str(e),
                "progress": 0,
                "current_step": f"Error: {str(e)}"
            }
            if progress_callback:
                progress_callback(error_result)
            yield error_result

    def run_realtime_analysis(
        self,
        company_id: str,
        financial_statements: List[Dict[str, Any]]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Wrapper method for backwards compatibility"""
        return self.comprehensive_forensic_analysis_realtime(company_id, financial_statements)
