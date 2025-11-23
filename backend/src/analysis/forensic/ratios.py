"""
Financial Ratios Module

This module provides a comprehensive set of financial ratios for analyzing company performance,
liquidity, solvency, and efficiency.
"""
from typing import Dict, Optional, Union, List, Tuple
from dataclasses import dataclass
from enum import Enum

class RatioCategory(str, Enum):
    """Categories of financial ratios."""
    LIQUIDITY = "liquidity"
    PROFITABILITY = "profitability"
    LEVERAGE = "leverage"
    EFFICIENCY = "efficiency"
    VALUATION = "valuation"
    CASH_FLOW = "cash_flow"

@dataclass
class RatioResult:
    """Container for ratio calculation results."""
    value: float
    name: str
    formula: str
    category: RatioCategory
    interpretation: str
    benchmark: Optional[float] = None
    benchmark_source: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            'value': round(self.value, 4) if isinstance(self.value, float) else self.value,
            'name': self.name,
            'formula': self.formula,
            'category': self.category.value,
            'interpretation': self.interpretation,
            'benchmark': round(self.benchmark, 4) if self.benchmark is not None else None,
            'benchmark_source': self.benchmark_source
        }

class FinancialRatios:
    """
    A class to calculate and analyze various financial ratios.
    
    This class provides methods to calculate different categories of financial ratios
    including liquidity, profitability, leverage, efficiency, valuation, and cash flow ratios.
    """
    
    def __init__(self, currency: str = 'INR'):
        """Initialize with currency for proper formatting."""
        self.currency = currency
    
    def calculate_all_ratios(self, financials: Dict) -> Dict[str, Dict]:
        """
        Calculate all available financial ratios.
        
        Args:
            financials: Dictionary containing financial statement data
            
        Returns:
            Dictionary containing all calculated ratios grouped by category
        """
        results = {}
        
        # Calculate ratios by category
        results[RatioCategory.LIQUIDITY] = self.calculate_liquidity_ratios(
            current_assets=financials.get('current_assets'),
            current_liabilities=financials.get('current_liabilities'),
            inventory=financials.get('inventory'),
            cash=financials.get('cash'),
            marketable_securities=financials.get('marketable_securities')
        )
        
        results[RatioCategory.PROFITABILITY] = self.calculate_profitability_ratios(
            net_income=financials.get('net_income'),
            revenue=financials.get('revenue'),
            total_assets=financials.get('total_assets'),
            total_equity=financials.get('total_equity'),
            ebit=financials.get('ebit'),
            interest_expense=financials.get('interest_expense'),
            tax_expense=financials.get('tax_expense')
        )
        
        results[RatioCategory.LEVERAGE] = self.calculate_leverage_ratios(
            total_debt=financials.get('total_debt'),
            total_equity=financials.get('total_equity'),
            total_assets=financials.get('total_assets'),
            ebitda=financials.get('ebitda'),
            interest_expense=financials.get('interest_expense')
        )
        
        results[RatioCategory.EFFICIENCY] = self.calculate_efficiency_ratios(
            revenue=financials.get('revenue'),
            cogs=financials.get('cogs'),
            inventory=financials.get('inventory'),
            accounts_receivable=financials.get('accounts_receivable'),
            accounts_payable=financials.get('accounts_payable'),
            total_assets=financials.get('total_assets'),
            fixed_assets=financials.get('fixed_assets')
        )
        
        results[RatioCategory.VALUATION] = self.calculate_valuation_ratios(
            market_cap=financials.get('market_cap'),
            revenue=financials.get('revenue'),
            net_income=financials.get('net_income'),
            book_value=financials.get('total_equity'),
            eps=financials.get('eps'),
            pe_ratio=financials.get('pe_ratio')
        )
        
        results[RatioCategory.CASH_FLOW] = self.calculate_cash_flow_ratios(
            operating_cash_flow=financials.get('operating_cash_flow'),
            capital_expenditures=financials.get('capital_expenditures'),
            current_liabilities=financials.get('current_liabilities'),
            total_debt=financials.get('total_debt'),
            revenue=financials.get('revenue')
        )
        
        # Convert to serializable format
        return {
            category: [ratio.to_dict() for ratio in ratios]
            for category, ratios in results.items()
        }
    
    def calculate_liquidity_ratios(
        self,
        current_assets: float,
        current_liabilities: float,
        inventory: Optional[float] = None,
        cash: Optional[float] = None,
        marketable_securities: Optional[float] = None
    ) -> List[RatioResult]:
        """Calculate liquidity ratios."""
        results = []
        
        # Current Ratio
        if current_assets is not None and current_liabilities is not None and current_liabilities != 0:
            current_ratio = current_assets / current_liabilities
            results.append(RatioResult(
                value=current_ratio,
                name="Current Ratio",
                formula="Current Assets / Current Liabilities",
                category=RatioCategory.LIQUIDITY,
                interpretation="Measures short-term liquidity. Higher is generally better.",
                benchmark=2.0,
                benchmark_source="General accounting principles"
            ))
        
        # Quick Ratio (Acid-Test)
        if (current_assets is not None and 
            inventory is not None and 
            current_liabilities is not None and 
            current_liabilities != 0):
            
            quick_ratio = (current_assets - inventory) / current_liabilities
            results.append(RatioResult(
                value=quick_ratio,
                name="Quick Ratio (Acid-Test)",
                formula="(Current Assets - Inventory) / Current Liabilities",
                category=RatioCategory.LIQUIDITY,
                interpretation="Measures short-term liquidity excluding inventory.",
                benchmark=1.0,
                benchmark_source="General accounting principles"
            ))
        
        # Cash Ratio
        if (cash is not None and 
            marketable_securities is not None and 
            current_liabilities is not None and 
            current_liabilities != 0):
            
            cash_ratio = (cash + marketable_securities) / current_liabilities
            results.append(RatioResult(
                value=cash_ratio,
                name="Cash Ratio",
                formula="(Cash + Marketable Securities) / Current Liabilities",
                category=RatioCategory.LIQUIDITY,
                interpretation="Measures the ability to pay off current liabilities with cash and cash equivalents.",
                benchmark=0.5,
                benchmark_source="General accounting principles"
            ))
            
        return results
    
    def calculate_profitability_ratios(
        self,
        net_income: Optional[float],
        revenue: Optional[float],
        total_assets: Optional[float],
        total_equity: Optional[float],
        ebit: Optional[float] = None,
        interest_expense: Optional[float] = None,
        tax_expense: Optional[float] = None
    ) -> List[RatioResult]:
        """Calculate profitability ratios."""
        results = []
        
        # Net Profit Margin
        if net_income is not None and revenue is not None and revenue != 0:
            net_margin = (net_income / revenue) * 100
            results.append(RatioResult(
                value=net_margin,
                name="Net Profit Margin",
                formula="(Net Income / Revenue) * 100",
                category=RatioCategory.PROFITABILITY,
                interpretation="Percentage of revenue remaining as profit after all expenses.",
                benchmark=10.0,  # Varies by industry
                benchmark_source="Industry average"
            ))
        
        # Return on Assets (ROA)
        if net_income is not None and total_assets is not None and total_assets != 0:
            roa = (net_income / total_assets) * 100
            results.append(RatioResult(
                value=roa,
                name="Return on Assets (ROA)",
                formula="(Net Income / Total Assets) * 100",
                category=RatioCategory.PROFITABILITY,
                interpretation="Measures how efficiently assets generate profit.",
                benchmark=5.0,  # Varies by industry
                benchmark_source="Industry average"
            ))
        
        # Return on Equity (ROE)
        if net_income is not None and total_equity is not None and total_equity != 0:
            roe = (net_income / total_equity) * 100
            results.append(RatioResult(
                value=roe,
                name="Return on Equity (ROE)",
                formula="(Net Income / Shareholders' Equity) * 100",
                category=RatioCategory.PROFITABILITY,
                interpretation="Measures the return on shareholders' investment.",
                benchmark=15.0,  # Varies by industry
                benchmark_source="Industry average"
            ))
        
        # EBIT Margin
        if ebit is not None and revenue is not None and revenue != 0:
            ebit_margin = (ebit / revenue) * 100
            results.append(RatioResult(
                value=ebit_margin,
                name="EBIT Margin",
                formula="(EBIT / Revenue) * 100",
                category=RatioCategory.PROFITABILITY,
                interpretation="Operating profitability before interest and taxes.",
                benchmark=12.0,  # Varies by industry
                benchmark_source="Industry average"
            ))
        
        # Interest Coverage Ratio
        if ebit is not None and interest_expense is not None and interest_expense != 0:
            interest_coverage = ebit / interest_expense
            results.append(RatioResult(
                value=interest_coverage,
                name="Interest Coverage Ratio",
                formula="EBIT / Interest Expense",
                category=RatioCategory.PROFITABILITY,
                interpretation="Measures ability to pay interest expenses.",
                benchmark=3.0,
                benchmark_source="General accounting principles"
            ))
            
        return results
    
    def calculate_leverage_ratios(
        self,
        total_debt: Optional[float],
        total_equity: Optional[float],
        total_assets: Optional[float],
        ebitda: Optional[float] = None,
        interest_expense: Optional[float] = None
    ) -> List[RatioResult]:
        """Calculate leverage and solvency ratios."""
        results = []
        
        # Debt-to-Equity Ratio
        if total_debt is not None and total_equity is not None and total_equity != 0:
            debt_to_equity = total_debt / total_equity
            results.append(RatioResult(
                value=debt_to_equity,
                name="Debt-to-Equity Ratio",
                formula="Total Debt / Shareholders' Equity",
                category=RatioCategory.LEVERAGE,
                interpretation="Measures financial leverage and risk.",
                benchmark=1.5,
                benchmark_source="General accounting principles"
            ))
        
        # Debt-to-Assets Ratio
        if total_debt is not None and total_assets is not None and total_assets != 0:
            debt_to_assets = total_debt / total_assets
            results.append(RatioResult(
                value=debt_to_assets,
                name="Debt-to-Assets Ratio",
                formula="Total Debt / Total Assets",
                category=RatioCategory.LEVERAGE,
                interpretation="Measures the percentage of assets financed by debt.",
                benchmark=0.4,
                benchmark_source="General accounting principles"
            ))
        
        # Debt-to-EBITDA Ratio
        if total_debt is not None and ebitda is not None and ebitda != 0:
            debt_to_ebitda = total_debt / ebitda
            results.append(RatioResult(
                value=debt_to_ebitda,
                name="Debt-to-EBITDA Ratio",
                formula="Total Debt / EBITDA",
                category=RatioCategory.LEVERAGE,
                interpretation="Measures ability to pay off debt with EBITDA.",
                benchmark=3.0,
                benchmark_source="General accounting principles"
            ))
        
        return results
    
    def calculate_efficiency_ratios(
        self,
        revenue: Optional[float],
        cogs: Optional[float],
        inventory: Optional[float],
        accounts_receivable: Optional[float],
        accounts_payable: Optional[float],
        total_assets: Optional[float],
        fixed_assets: Optional[float]
    ) -> List[RatioResult]:
        """Calculate efficiency ratios."""
        results = []
        
        # Inventory Turnover
        if cogs is not None and inventory is not None and inventory != 0:
            inventory_turnover = cogs / inventory
            results.append(RatioResult(
                value=inventory_turnover,
                name="Inventory Turnover",
                formula="COGS / Average Inventory",
                category=RatioCategory.EFFICIENCY,
                interpretation="Measures how quickly inventory is sold.",
                benchmark=6.0,  # Varies by industry
                benchmark_source="Industry average"
            ))
        
        # Days Sales Outstanding (DSO)
        if accounts_receivable is not None and revenue is not None and revenue != 0:
            dso = (accounts_receivable / revenue) * 365
            results.append(RatioResult(
                value=dso,
                name="Days Sales Outstanding (DSO)",
                formula="(Accounts Receivable / Revenue) * 365",
                category=RatioCategory.EFFICIENCY,
                interpretation="Average collection period for receivables.",
                benchmark=45.0,  # Varies by industry
                benchmark_source="Industry average"
            ))
        
        # Asset Turnover
        if revenue is not None and total_assets is not None and total_assets != 0:
            asset_turnover = revenue / total_assets
            results.append(RatioResult(
                value=asset_turnover,
                name="Asset Turnover",
                formula="Revenue / Total Assets",
                category=RatioCategory.EFFICIENCY,
                interpretation="Measures efficiency of asset utilization.",
                benchmark=0.8,  # Varies by industry
                benchmark_source="Industry average"
            ))
        
        # Fixed Asset Turnover
        if revenue is not None and fixed_assets is not None and fixed_assets != 0:
            fixed_asset_turnover = revenue / fixed_assets
            results.append(RatioResult(
                value=fixed_asset_turnover,
                name="Fixed Asset Turnover",
                formula="Revenue / Net Fixed Assets",
                category=RatioCategory.EFFICIENCY,
                interpretation="Measures efficiency of fixed asset utilization.",
                benchmark=2.0,  # Varies by industry
                benchmark_source="Industry average"
            ))
            
        return results
    
    def calculate_valuation_ratios(
        self,
        market_cap: Optional[float],
        revenue: Optional[float],
        net_income: Optional[float],
        book_value: Optional[float],
        eps: Optional[float],
        pe_ratio: Optional[float] = None
    ) -> List[RatioResult]:
        """Calculate valuation ratios."""
        results = []
        
        # Price-to-Sales (P/S) Ratio
        if market_cap is not None and revenue is not None and revenue != 0:
            ps_ratio = market_cap / revenue
            results.append(RatioResult(
                value=ps_ratio,
                name="Price-to-Sales (P/S) Ratio",
                formula="Market Capitalization / Revenue",
                category=RatioCategory.VALUATION,
                interpretation="Measures the value placed on each dollar of a company's sales.",
                benchmark=2.5,  # Varies by industry
                benchmark_source="Industry average"
            ))
        
        # Price-to-Book (P/B) Ratio
        if market_cap is not None and book_value is not None and book_value != 0:
            pb_ratio = market_cap / book_value
            results.append(RatioResult(
                value=pb_ratio,
                name="Price-to-Book (P/B) Ratio",
                formula="Market Capitalization / Book Value",
                category=RatioCategory.VALUATION,
                interpretation="Measures the market's valuation of a company relative to its book value.",
                benchmark=3.0,  # Varies by industry
                benchmark_source="Industry average"
            ))
        
        # P/E Ratio (if not provided)
        if pe_ratio is None and market_cap is not None and net_income is not None and net_income != 0:
            pe_ratio = market_cap / net_income
            
        if pe_ratio is not None:
            results.append(RatioResult(
                value=pe_ratio,
                name="Price-to-Earnings (P/E) Ratio",
                formula="Market Capitalization / Net Income",
                category=RatioCategory.VALUATION,
                interpretation="Measures the price paid for a share relative to annual net income.",
                benchmark=20.0,  # Varies by industry
                benchmark_source="Industry average"
            ))
        
        # Earnings Yield (inverse of P/E)
        if pe_ratio is not None and pe_ratio != 0:
            earnings_yield = (1 / pe_ratio) * 100
            results.append(RatioResult(
                value=earnings_yield,
                name="Earnings Yield",
                formula="(1 / P/E Ratio) * 100",
                category=RatioCategory.VALUATION,
                interpretation="Measures earnings per dollar invested in the stock.",
                benchmark=5.0,  # Varies by interest rates
                benchmark_source="Market average"
            ))
            
        return results
    
    def calculate_cash_flow_ratios(
        self,
        operating_cash_flow: Optional[float],
        capital_expenditures: Optional[float],
        current_liabilities: Optional[float],
        total_debt: Optional[float],
        revenue: Optional[float]
    ) -> List[RatioResult]:
        """Calculate cash flow ratios."""
        results = []
        
        # Free Cash Flow
        if operating_cash_flow is not None and capital_expenditures is not None:
            fcf = operating_cash_flow - capital_expenditures
            results.append(RatioResult(
                value=fcf,
                name="Free Cash Flow",
                formula="Operating Cash Flow - Capital Expenditures",
                category=RatioCategory.CASH_FLOW,
                interpretation="Cash available to investors after capital expenditures.",
                benchmark=None,
                benchmark_source=None
            ))
        
        # Operating Cash Flow Ratio
        if operating_cash_flow is not None and current_liabilities is not None and current_liabilities != 0:
            ocf_ratio = operating_cash_flow / current_liabilities
            results.append(RatioResult(
                value=ocf_ratio,
                name="Operating Cash Flow Ratio",
                formula="Operating Cash Flow / Current Liabilities",
                category=RatioCategory.CASH_FLOW,
                interpretation="Measures ability to cover current liabilities with operating cash flow.",
                benchmark=1.0,
                benchmark_source="General accounting principles"
            ))
        
        # Cash Flow to Debt Ratio
        if operating_cash_flow is not None and total_debt is not None and total_debt != 0:
            cf_debt_ratio = operating_cash_flow / total_debt
            results.append(RatioResult(
                value=cf_debt_ratio,
                name="Cash Flow to Debt Ratio",
                formula="Operating Cash Flow / Total Debt",
                category=RatioCategory.CASH_FLOW,
                interpretation="Measures ability to pay off debt with operating cash flow.",
                benchmark=0.2,
                benchmark_source="General accounting principles"
            ))
        
        # Operating Cash Flow Margin
        if operating_cash_flow is not None and revenue is not None and revenue != 0:
            ocf_margin = (operating_cash_flow / revenue) * 100
            results.append(RatioResult(
                value=ocf_margin,
                name="Operating Cash Flow Margin",
                formula="(Operating Cash Flow / Revenue) * 100",
                category=RatioCategory.CASH_FLOW,
                interpretation="Measures cash generated per dollar of revenue.",
                benchmark=10.0,  # Varies by industry
                benchmark_source="Industry average"
            ))
            
        return results
