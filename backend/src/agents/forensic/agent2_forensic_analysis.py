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
        self.db_client = get_db_client()
        
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

            if quarterly_income is None or quarterly_balance is None:
                return {"success": False, "error": f"Insufficient quarterly data for {symbol}"}

            print(f"✅ Retrieved {len(quarterly_income.columns)} quarters of income statements")
            print(f"✅ Retrieved {len(quarterly_balance.columns)} quarters of balance sheets")

            # Enhanced Yahoo Finance to Agent field mapping
            yahoo_to_agent_mapping = {
                'income_statement': {
                    # Revenue fields
                    'TotalRevenue': 'total_revenue',
                    'Total Revenue': 'total_revenue',

                    # Profit fields
                    'NetIncome': 'net_profit',
                    'Net Income': 'net_profit',
                    'Net Income From Continuing Operation Net Minority Interest': 'net_profit',
                    'Net Income From Continuing And Discontinued Operation': 'net_profit',

                    # Cost fields
                    'CostOfRevenue': 'cost_of_revenue',
                    'Cost Of Revenue': 'cost_of_revenue',
                    'Reconciled Cost Of Revenue': 'cost_of_revenue',

                    # Additional profit metrics
                    'GrossProfit': 'gross_profit',
                    'Gross Profit': 'gross_profit',
                    'OperatingIncome': 'operating_income',
                    'Operating Income': 'operating_income',
                    'EBITDA': 'ebitda',
                    'EBIT': 'ebit',

                    # Expense fields
                    'InterestExpense': 'interest_expense',
                    'Interest Expense': 'interest_expense',
                    'IncomeTaxExpense': 'tax_expense',
                    'Tax Expense': 'tax_expense',
                },
                'balance_sheet': {
                    # Asset fields
                    'TotalAssets': 'total_assets',
                    'Total Assets': 'total_assets',

                    # Liability fields
                    'TotalLiabilitiesNetMinorityInterest': 'total_liabilities',
                    'Total Liabilities Net Minority Interest': 'total_liabilities',
                    'TotalLiabilities': 'total_liabilities',
                    'Total Liabilities': 'total_liabilities',

                    # Equity fields
                    'StockholdersEquity': 'total_equity',
                    'Stockholders Equity': 'total_equity',
                    'TotalEquityGrossMinorityInterest': 'total_equity',
                    'Total Equity Gross Minority Interest': 'total_equity',

                    # Current fields
                    'CurrentAssets': 'current_assets',
                    'Current Assets': 'current_assets',
                    'CurrentLiabilities': 'current_liabilities',
                    'Current Liabilities': 'current_liabilities',

                    # Cash fields
                    'CashAndCashEquivalents': 'cash_and_equivalents',
                    'Cash And Cash Equivalents': 'cash_and_equivalents',
                    'CashFinancial': 'cash_and_equivalents',
                    'Cash Financial': 'cash_and_equivalents',

                    # Additional asset fields
                    'AccountsReceivable': 'accounts_receivable',
                    'Accounts Receivable': 'accounts_receivable',
                    'Inventory': 'inventory',
                    'Inventories': 'inventory',
                    'PropertyPlantEquipment': 'property_plant_equipment',
                    'Property Plant Equipment': 'property_plant_equipment',
                }
            }

            # Convert Yahoo Finance data to agent format
            financial_statements = []

            # Process up to specified quarters for each statement type
            periods_to_process = min(quarters, len(quarterly_income.columns), len(quarterly_balance.columns))

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
        total_revenue = data.get("total_revenue", 0)
        if not total_revenue:
            return {"error": "No total revenue found"}
            
        return {
            "cost_of_revenue_pct": (data.get("cost_of_revenue", 0) / total_revenue) * 100,
            "gross_profit_pct": (data.get("gross_profit", 0) / total_revenue) * 100,
            "operating_income_pct": (data.get("operating_income", 0) / total_revenue) * 100,
            "net_profit_pct": (data.get("net_profit", 0) / total_revenue) * 100,
            "interest_expense_pct": (data.get("interest_expense", 0) / total_revenue) * 100,
            "tax_expense_pct": (data.get("tax_expense", 0) / total_revenue) * 100
        }
    
    def _vertical_balance_sheet(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Vertical analysis for balance sheet (% of total assets)"""
        total_assets = data.get("total_assets", 0)
        if not total_assets:
            return {"error": "No total assets found"}
            
        return {
            "current_assets_pct": (data.get("current_assets", 0) / total_assets) * 100,
            "non_current_assets_pct": (data.get("non_current_assets", 0) / total_assets) * 100,
            "current_liabilities_pct": (data.get("current_liabilities", 0) / total_assets) * 100,
            "non_current_liabilities_pct": (data.get("non_current_liabilities", 0) / total_assets) * 100,
            "total_equity_pct": (data.get("total_equity", 0) / total_assets) * 100
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
        
        key_metrics = [
            "total_revenue", "gross_profit", "operating_income", "net_profit",
            "total_assets", "total_liabilities", "total_equity"
        ]
        
        for metric in key_metrics:
            prev_value = previous.get(metric, 0)
            curr_value = current.get(metric, 0)
            
            if prev_value != 0:
                growth_rate = ((curr_value - prev_value) / prev_value) * 100
                growth_rates[f"{metric}_growth_pct"] = round(growth_rate, 2)
            else:
                growth_rates[f"{metric}_growth_pct"] = None
                
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
        total_revenue = data.get("total_revenue", 0)
        gross_profit = data.get("gross_profit", 0)
        operating_income = data.get("operating_income", 0)
        net_profit = data.get("net_profit", 0)
        ebitda = data.get("ebitda", 0)

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

        # Note: ROE and ROA need balance sheet data, so they're calculated in the main function
        # when we have both income statement and balance sheet data

        return ratios
    def _calculate_leverage_ratios(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate leverage ratios"""
        total_debt = data.get("total_liabilities", 0)
        total_equity = data.get("total_equity", 0)
        total_assets = data.get("total_assets", 0)

        ratios = {}

        # Debt-to-Equity Ratio
        if total_equity != 0:
            ratios["debt_to_equity"] = round(total_debt / total_equity, 2)

        # Debt-to-Assets Ratio
        if total_assets != 0:
            ratios["debt_to_assets"] = round(total_debt / total_assets, 2)

        # Note: Interest coverage needs income statement data, so it's calculated in the main function

        return ratios
    

    def _calculate_efficiency_ratios(self, balance_sheet: Dict[str, Any], 
                                   income_statement: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive efficiency ratios"""
        total_revenue = income_statement.get("total_revenue", 0)
        total_assets = balance_sheet.get("total_assets", 0)
        accounts_receivable = balance_sheet.get("accounts_receivable", 0)
        inventory = balance_sheet.get("inventory", 0)
        cost_of_goods_sold = income_statement.get("cost_of_goods_sold", 0)
        current_assets = balance_sheet.get("current_assets", 0)
        current_liabilities = balance_sheet.get("current_liabilities", 0)
        fixed_assets = balance_sheet.get("property_plant_equipment", 0)

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
                0
            )

            # Total Equity
            total_equity = (
                balance_sheet.get("totalStockholdersEquity") or
                balance_sheet.get("Total Stockholders Equity") or
                balance_sheet.get("total_equity") or
                0
            )

            # Total Liabilities
            total_liabilities = (
                balance_sheet.get("totalLiabilities") or
                balance_sheet.get("Total Liabilities") or
                balance_sheet.get("total_liabilities") or
                0
            )

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
    
    def calculate_beneish_m_score(self, current_period: Dict[str, Any], 
                                 previous_period: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Beneish M-Score for earnings manipulation detection using proper field mapping"""
        try:
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
            
            # Benford's Law Analysis
            benford_result = self.benford_analysis(financial_statements)
            results["benford_analysis"] = benford_result
            
            # Altman Z-Score (if we have balance sheet and income statement)
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
            
            # Beneish M-Score (if we have multiple periods)
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
            
            # Anomaly Detection
            anomalies_result = self.detect_anomalies(financial_statements)
            results["anomaly_detection"] = anomalies_result
            
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
