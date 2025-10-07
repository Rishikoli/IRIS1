"""
Project IRIS - Agent 2: Forensic Analysis Agent
Implements Benford's Law, Altman Z-Score, Beneish M-Score, and financial ratio analysis
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime
from scipy import stats
import math

from config import settings
from database.connection import get_db_client

logger = logging.getLogger(__name__)


class ForensicAnalysisAgent:
    """Agent 2: Forensic analysis with statistical tests and financial ratios"""
    
    def __init__(self):
        self.db_client = get_db_client()
        
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
            # Sort statements by period
            sorted_statements = sorted(financial_statements, 
                                     key=lambda x: x.get("period_end", ""))
            
            horizontal_results = {}
            
            for i in range(1, len(sorted_statements)):
                current = sorted_statements[i]
                previous = sorted_statements[i-1]
                
                period_key = f"{previous.get('period_end')}_to_{current.get('period_end')}"
                horizontal_results[period_key] = self._calculate_growth_rates(
                    previous.get("data", {}), 
                    current.get("data", {})
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
            
            for statement in financial_statements:
                period = statement.get("period_end")
                data = statement.get("data", {})
                statement_type = statement.get("statement_type")
                
                if period not in ratios_results:
                    ratios_results[period] = {}
                
                if statement_type == "balance_sheet":
                    ratios_results[period].update(self._calculate_liquidity_ratios(data))
                    ratios_results[period].update(self._calculate_leverage_ratios(data))
                elif statement_type == "income_statement":
                    ratios_results[period].update(self._calculate_profitability_ratios(data))
                    
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
        
        # Operating Margin (missing from current implementation)
        if total_revenue != 0:
            ratios["operating_margin_pct"] = round((operating_income / total_revenue) * 100, 2)
        
        # Net Margin
        if total_revenue != 0:
            ratios["net_margin_pct"] = round((net_profit / total_revenue) * 100, 2)
        
        # EBITDA Margin (missing from current implementation)
        if total_revenue != 0:
            ratios["ebitda_margin_pct"] = round((ebitda / total_revenue) * 100, 2)
            
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
        
        # Fixed Asset Turnover (missing from current implementation)
        if fixed_assets != 0:
            ratios["fixed_asset_turnover"] = round(total_revenue / fixed_assets, 2)
        
        # Receivables Turnover
        if accounts_receivable != 0:
            ratios["receivables_turnover"] = round(total_revenue / accounts_receivable, 2)
        
        # Inventory Turnover
        if inventory != 0:
            ratios["inventory_turnover"] = round(cost_of_goods_sold / inventory, 2)
            
        # Working Capital Turnover (missing from current implementation)
        working_capital = current_assets - current_liabilities
        if working_capital != 0:
            ratios["working_capital_turnover"] = round(total_revenue / working_capital, 2)
        
        # Days Sales Outstanding (DSO)
        if accounts_receivable != 0 and total_revenue != 0:
            dso = (accounts_receivable / total_revenue) * 365
            ratios["days_sales_outstanding"] = round(dso, 1)
            
        # Days Inventory Outstanding (DIO) - missing from current implementation
        if inventory != 0 and cost_of_goods_sold != 0:
            dio = (inventory / cost_of_goods_sold) * 365
            ratios["days_inventory_outstanding"] = round(dio, 1)
            
        # Cash Conversion Cycle (advanced metric) - missing from current implementation
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
            
            if len(all_numbers) < 30:  # Need sufficient sample size
                return {
                    "success": False,
                    "error": "Insufficient data points for Benford analysis (minimum 30 required)"
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
            # Extract required values
            total_assets = balance_sheet.get("total_assets", 0)
            current_assets = balance_sheet.get("current_assets", 0)
            current_liabilities = balance_sheet.get("current_liabilities", 0)
            retained_earnings = balance_sheet.get("retained_earnings", 0)
            total_equity = balance_sheet.get("total_equity", 0)
            
            total_revenue = income_statement.get("total_revenue", 0)
            ebit = income_statement.get("operating_income", 0)  # Approximation
            
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
            total_liabilities = balance_sheet.get("total_liabilities", 0)
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
        """Calculate Beneish M-Score for earnings manipulation detection"""
        try:
            # Extract current period data
            curr_revenue = current_period.get("total_revenue", 0)
            curr_receivables = current_period.get("accounts_receivable", 0)
            curr_gross_profit = current_period.get("gross_profit", 0)
            curr_total_assets = current_period.get("total_assets", 0)
            curr_ppe = current_period.get("property_plant_equipment", 0)
            curr_sga = current_period.get("sga_expenses", 0)
            curr_depreciation = current_period.get("depreciation", 0)
            curr_total_accruals = current_period.get("total_accruals", 0)
            
            # Extract previous period data
            prev_revenue = previous_period.get("total_revenue", 0)
            prev_receivables = previous_period.get("accounts_receivable", 0)
            prev_gross_profit = previous_period.get("gross_profit", 0)
            prev_total_assets = previous_period.get("total_assets", 0)
            prev_ppe = previous_period.get("property_plant_equipment", 0)
            prev_sga = previous_period.get("sga_expenses", 0)
            prev_depreciation = previous_period.get("depreciation", 0)
            
            # Calculate M-Score variables
            variables = {}
            
            # DSRI (Days Sales in Receivables Index)
            if prev_revenue != 0 and curr_revenue != 0 and prev_receivables != 0:
                dsri_curr = curr_receivables / curr_revenue
                dsri_prev = prev_receivables / prev_revenue
                variables["DSRI"] = dsri_curr / dsri_prev if dsri_prev != 0 else 1
            else:
                variables["DSRI"] = 1
            
            # GMI (Gross Margin Index)
            if prev_revenue != 0 and curr_revenue != 0:
                gm_prev = prev_gross_profit / prev_revenue
                gm_curr = curr_gross_profit / curr_revenue
                variables["GMI"] = gm_prev / gm_curr if gm_curr != 0 else 1
            else:
                variables["GMI"] = 1
            
            # AQI (Asset Quality Index) - simplified
            variables["AQI"] = 1  # Requires detailed asset breakdown
            
            # SGI (Sales Growth Index)
            if prev_revenue != 0:
                variables["SGI"] = curr_revenue / prev_revenue
            else:
                variables["SGI"] = 1
            
            # DEPI (Depreciation Index)
            if prev_ppe != 0 and curr_ppe != 0:
                depr_rate_prev = prev_depreciation / (prev_depreciation + prev_ppe)
                depr_rate_curr = curr_depreciation / (curr_depreciation + curr_ppe)
                variables["DEPI"] = depr_rate_prev / depr_rate_curr if depr_rate_curr != 0 else 1
            else:
                variables["DEPI"] = 1
            
            # SGAI (SG&A Index)
            if prev_revenue != 0 and curr_revenue != 0:
                sga_rate_curr = curr_sga / curr_revenue
                sga_rate_prev = prev_sga / prev_revenue
                variables["SGAI"] = sga_rate_curr / sga_rate_prev if sga_rate_prev != 0 else 1
            else:
                variables["SGAI"] = 1
            
            # LVGI (Leverage Index) - simplified
            variables["LVGI"] = 1  # Requires debt details
            
            # TATA (Total Accruals to Total Assets)
            if curr_total_assets != 0:
                variables["TATA"] = curr_total_accruals / curr_total_assets
            else:
                variables["TATA"] = 0
            
            # Calculate M-Score
            m_score = (-4.84 + 0.92 * variables["DSRI"] + 0.528 * variables["GMI"] + 
                      0.404 * variables["AQI"] + 0.892 * variables["SGI"] + 
                      0.115 * variables["DEPI"] - 0.172 * variables["SGAI"] + 
                      4.679 * variables["TATA"] - 0.327 * variables["LVGI"])
            
            # Classification
            is_manipulator = m_score > -1.78
            
            return {
                "success": True,
                "beneish_m_score": {
                    "m_score": round(m_score, 3),
                    "threshold": -1.78,
                    "is_likely_manipulator": is_manipulator,
                    "risk_level": "HIGH" if is_manipulator else "LOW",
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
                current_period = financial_statements[-1].get("data", {})
                previous_period = financial_statements[-2].get("data", {})
                
                m_score_result = self.calculate_beneish_m_score(current_period, previous_period)
                results["beneish_m_score"] = m_score_result
            
            # Anomaly Detection
            anomalies_result = self.detect_anomalies(financial_statements)
            results["anomaly_detection"] = anomalies_result
            
            return results
            
        except Exception as e:
            logger.error(f"Comprehensive forensic analysis failed: {e}")
            return {"success": False, "error": str(e)}
