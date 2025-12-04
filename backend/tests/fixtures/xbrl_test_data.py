"""
Project IRIS - XBRL Test Fixtures
Sample XBRL data for testing financial statement parsing and validation
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Any
from decimal import Decimal


def create_sample_xbrl_company_data() -> Dict[str, Any]:
    """Create sample XBRL company data for testing"""
    return {
        "entity_info": {
            "identifier": "INE002A01018",  # Reliance Industries
            "name": "Reliance Industries Limited",
            "fiscal_year_end": "--03-31",
            "reporting_currency": "INR"
        },
        "context_info": {
            "current_year": {
                "id": "c1",
                "period": "2023-04-01/2024-03-31",
                "entity": "entity1"
            },
            "previous_year": {
                "id": "c2",
                "period": "2022-04-01/2023-03-31",
                "entity": "entity1"
            }
        }
    }


def create_sample_xbrl_balance_sheet() -> str:
    """Create sample XBRL balance sheet data"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<xbrl xmlns="http://www.xbrl.org/2003/instance"
      xmlns:xbrli="http://www.xbrl.org/2003/instance"
      xmlns:xbrldi="http://xbrl.org/2006/xbrldi"
      xmlns:rei="http://www.reliance.com/xbrl/reliance">

  <!-- Entity Information -->
  <xbrli:entity>
    <xbrli:identifier scheme="http://www.sebi.gov.in">INE002A01018</xbrli:identifier>
    <xbrli:segment>
      <xbrldi:explicitMember dimension="rei:ReportingEntityAxis">rei:RelianceIndustriesLimited</xbrldi:explicitMember>
    </xbrli:segment>
  </xbrli:entity>

  <!-- Contexts -->
  <xbrli:context id="c1">
    <xbrli:entity>
      <xbrli:identifier scheme="http://www.sebi.gov.in">INE002A01018</xbrli:identifier>
    </xbrli:entity>
    <xbrli:period>
      <xbrli:instant>2024-03-31</xbrli:instant>
    </xbrli:period>
  </xbrli:context>

  <xbrli:context id="c2">
    <xbrli:entity>
      <xbrli:identifier scheme="http://www.sebi.gov.in">INE002A01018</xbrli:identifier>
    </xbrli:entity>
    <xbrli:period>
      <xbrli:instant>2023-03-31</xbrli:instant>
    </xbrli:period>
  </xbrli:context>

  <!-- Balance Sheet Data -->
  <xbrli:unit id="u1">
    <xbrli:measure>iso4217:INR</xbrli:measure>
  </xbrli:unit>

  <!-- ASSETS (₹ in crores) -->
  <rei:TotalAssets contextRef="c1" unitRef="u1" decimals="2">1500000</rei:TotalAssets>
  <rei:NonCurrentAssets contextRef="c1" unitRef="u1" decimals="2">1200000</rei:NonCurrentAssets>
  <rei:CurrentAssets contextRef="c1" unitRef="u1" decimals="2">300000</rei:CurrentAssets>

  <!-- Property, Plant and Equipment -->
  <rei:PropertyPlantEquipment contextRef="c1" unitRef="u1" decimals="2">800000</rei:PropertyPlantEquipment>
  <rei:AccumulatedDepreciation contextRef="c1" unitRef="u1" decimals="2">-150000</rei:AccumulatedDepreciation>

  <!-- Investments -->
  <rei:NonCurrentInvestments contextRef="c1" unitRef="u1" decimals="2">200000</rei:NonCurrentInvestments>
  <rei:CurrentInvestments contextRef="c1" unitRef="u1" decimals="2">50000</rei:CurrentInvestments>

  <!-- LIABILITIES (₹ in crores) -->
  <rei:TotalLiabilities contextRef="c1" unitRef="u1" decimals="2">900000</rei:TotalLiabilities>
  <rei:NonCurrentLiabilities contextRef="c1" unitRef="u1" decimals="2">600000</rei:NonCurrentLiabilities>
  <rei:CurrentLiabilities contextRef="c1" unitRef="u1" decimals="2">300000</rei:CurrentLiabilities>

  <!-- EQUITY (₹ in crores) -->
  <rei:TotalEquity contextRef="c1" unitRef="u1" decimals="2">600000</rei:TotalEquity>
  <rei:ShareCapital contextRef="c1" unitRef="u1" decimals="2">50000</rei:ShareCapital>
  <rei:ReservesAndSurplus contextRef="c1" unitRef="u1" decimals="2">550000</rei:ReservesAndSurplus>

</xbrl>'''


def create_sample_xbrl_income_statement() -> str:
    """Create sample XBRL income statement data"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<xbrl xmlns="http://www.xbrl.org/2003/instance"
      xmlns:xbrli="http://www.xbrl.org/2003/instance"
      xmlns:xbrldi="http://xbrl.org/2006/xbrldi"
      xmlns:rei="http://www.reliance.com/xbrl/reliance">

  <!-- Entity Information -->
  <xbrli:entity>
    <xbrli:identifier scheme="http://www.sebi.gov.in">INE002A01018</xbrli:identifier>
  </xbrli:entity>

  <!-- Contexts -->
  <xbrli:context id="c1">
    <xbrli:entity>
      <xbrli:identifier scheme="http://www.sebi.gov.in">INE002A01018</xbrli:identifier>
    </xbrli:entity>
    <xbrli:period>
      <xbrli:startDate>2023-04-01</xbrli:startDate>
      <xbrli:endDate>2024-03-31</xbrli:endDate>
    </xbrli:period>
  </xbrli:context>

  <xbrli:context id="c2">
    <xbrli:entity>
      <xbrli:identifier scheme="http://www.sebi.gov.in">INE002A01018</xbrli:identifier>
    </xbrli:entity>
    <xbrli:period>
      <xbrli:startDate>2022-04-01</xbrli:startDate>
      <xbrli:endDate>2023-03-31</xbrli:endDate>
    </xbrli:period>
  </xbrli:context>

  <!-- Unit -->
  <xbrli:unit id="u1">
    <xbrli:measure>iso4217:INR</xbrli:measure>
  </xbrli:unit>

  <!-- INCOME STATEMENT (₹ in crores) -->
  <!-- Revenue -->
  <rei:TotalRevenue contextRef="c1" unitRef="u1" decimals="2">850000</rei:TotalRevenue>
  <rei:RevenueFromOperations contextRef="c1" unitRef="u1" decimals="2">800000</rei:RevenueFromOperations>
  <rei:OtherIncome contextRef="c1" unitRef="u1" decimals="2">50000</rei:OtherIncome>

  <!-- Expenses -->
  <rei:CostOfMaterials contextRef="c1" unitRef="u1" decimals="2">400000</rei:CostOfMaterials>
  <rei:EmployeeBenefitsExpense contextRef="c1" unitRef="u1" decimals="2">25000</rei:EmployeeBenefitsExpense>
  <rei:FinanceCosts contextRef="c1" unitRef="u1" decimals="2">15000</rei:FinanceCosts>
  <rei:DepreciationAndAmortisation contextRef="c1" unitRef="u1" decimals="2">30000</rei:DepreciationAndAmortisation>
  <rei:OtherExpenses contextRef="c1" unitRef="u1" decimals="2">50000</rei:OtherExpenses>

  <!-- Profit -->
  <rei:ProfitBeforeTax contextRef="c1" unitRef="u1" decimals="2">320000</rei:ProfitBeforeTax>
  <rei:TaxExpense contextRef="c1" unitRef="u1" decimals="2">70000</rei:TaxExpense>
  <rei:ProfitAfterTax contextRef="c1" unitRef="u1" decimals="2">250000</rei:ProfitAfterTax>

  <!-- Earnings Per Share -->
  <rei:BasicEPS contextRef="c1" unitRef="u1" decimals="2">125.50</rei:BasicEPS>
  <rei:DilutedEPS contextRef="c1" unitRef="u1" decimals="2">125.25</rei:DilutedEPS>

</xbrl>'''


def create_sample_xbrl_cash_flow() -> str:
    """Create sample XBRL cash flow statement data"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<xbrl xmlns="http://www.xbrl.org/2003/instance"
      xmlns:xbrli="http://www.xbrl.org/2003/instance"
      xmlns:xbrldi="http://xbrl.org/2006/xbrldi"
      xmlns:rei="http://www.reliance.com/xbrl/reliance">

  <!-- Entity Information -->
  <xbrli:entity>
    <xbrli:identifier scheme="http://www.sebi.gov.in">INE002A01018</xbrli:identifier>
  </xbrli:entity>

  <!-- Contexts -->
  <xbrli:context id="c1">
    <xbrli:entity>
      <xbrli:identifier scheme="http://www.sebi.gov.in">INE002A01018</xbrli:identifier>
    </xbrli:entity>
    <xbrli:period>
      <xbrli:startDate>2023-04-01</xbrli:startDate>
      <xbrli:endDate>2024-03-31</xbrli:endDate>
    </xbrli:period>
  </xbrli:context>

  <!-- Unit -->
  <xbrli:unit id="u1">
    <xbrli:measure>iso4217:INR</xbrli:measure>
  </xbrli:unit>

  <!-- CASH FLOW STATEMENT (₹ in crores) -->
  <!-- Operating Activities -->
  <rei:NetCashFromOperatingActivities contextRef="c1" unitRef="u1" decimals="2">200000</rei:NetCashFromOperatingActivities>
  <rei:CashFromOperations contextRef="c1" unitRef="u1" decimals="2">180000</rei:CashFromOperations>
  <rei:InterestPaid contextRef="c1" unitRef="u1" decimals="2">-15000</rei:InterestPaid>
  <rei:IncomeTaxPaid contextRef="c1" unitRef="u1" decimals="2">-70000</rei:IncomeTaxPaid>

  <!-- Investing Activities -->
  <rei:NetCashFromInvestingActivities contextRef="c1" unitRef="u1" decimals="2">-150000</rei:NetCashFromInvestingActivities>
  <rei:PurchaseOfFixedAssets contextRef="c1" unitRef="u1" decimals="2">-120000</rei:PurchaseOfFixedAssets>
  <rei:SaleOfInvestments contextRef="c1" unitRef="u1" decimals="2">80000</rei:SaleOfInvestments>
  <rei:InterestReceived contextRef="c1" unitRef="u1" decimals="2">15000</rei:InterestReceived>

  <!-- Financing Activities -->
  <rei:NetCashFromFinancingActivities contextRef="c1" unitRef="u1" decimals="2">-50000</rei:NetCashFromFinancingActivities>
  <rei:ProceedsFromBorrowings contextRef="c1" unitRef="u1" decimals="2">100000</rei:ProceedsFromBorrowings>
  <rei:RepaymentOfBorrowings contextRef="c1" unitRef="u1" decimals="2">-80000</rei:RepaymentOfBorrowings>
  <rei:DividendPaid contextRef="c1" unitRef="u1" decimals="2">-70000</rei:DividendPaid>

  <!-- Net Cash Flow -->
  <rei:NetIncreaseInCash contextRef="c1" unitRef="u1" decimals="2">0</rei:NetIncreaseInCash>
  <rei:CashAtBeginning contextRef="c1" unitRef="u1" decimals="2">50000</rei:CashAtBeginning>
  <rei:CashAtEnd contextRef="c1" unitRef="u1" decimals="2">50000</rei:CashAtEnd>

</xbrl>'''


def create_malformed_xbrl_data() -> str:
    """Create malformed XBRL data for edge case testing"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<xbrl xmlns="http://www.xbrl.org/2003/instance"
      xmlns:xbrli="http://www.xbrl.org/2003/instance">

  <!-- Missing entity information -->
  <xbrli:context id="c1">
    <xbrli:period>
      <xbrli:instant>2024-03-31</xbrli:instant>
    </xbrli:period>
  </xbrli:context>

  <!-- Invalid XML structure -->
  <xbrli:unit id="u1">
    <xbrli:measure>invalid_currency</xbrli:measure>
  </xbrli:unit>

  <!-- Missing required fields -->
  <invalid_tag>TotalAssets</invalid_tag>

</xbrl>'''


def create_xbrl_with_negative_values() -> str:
    """Create XBRL data with negative values for edge case testing"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<xbrl xmlns="http://www.xbrl.org/2003/instance"
      xmlns:xbrli="http://www.xbrl.org/2003/instance"
      xmlns:xbrldi="http://xbrl.org/2006/xbrldi"
      xmlns:rei="http://www.reliance.com/xbrl/reliance">

  <xbrli:entity>
    <xbrli:identifier scheme="http://www.sebi.gov.in">INE002A01018</xbrli:identifier>
  </xbrli:entity>

  <xbrli:context id="c1">
    <xbrli:entity>
      <xbrli:identifier scheme="http://www.sebi.gov.in">INE002A01018</xbrli:identifier>
    </xbrli:entity>
    <xbrli:period>
      <xbrli:instant>2024-03-31</xbrli:instant>
    </xbrli:period>
  </xbrli:context>

  <xbrli:unit id="u1">
    <xbrli:measure>iso4217:INR</xbrli:measure>
  </xbrli:unit>

  <!-- Negative Assets (invalid scenario) -->
  <rei:TotalAssets contextRef="c1" unitRef="u1" decimals="2">-100000</rei:TotalAssets>
  <rei:TotalLiabilities contextRef="c1" unitRef="u1" decimals="2">60000</rei:TotalLiabilities>
  <rei:TotalEquity contextRef="c1" unitRef="u1" decimals="2">40000</rei:TotalEquity>

</xbrl>'''


def create_xbrl_validation_edge_cases() -> List[Dict[str, Any]]:
    """Create XBRL validation edge cases for testing"""
    return [
        # Valid balance sheet
        {
            "name": "valid_balance_sheet",
            "data": {
                "total_assets": Decimal("100000"),
                "total_liabilities": Decimal("60000"),
                "total_equity": Decimal("40000")
            },
            "expected_valid": True,
            "expected_errors": []
        },

        # Invalid balance sheet - Assets != Liabilities + Equity
        {
            "name": "invalid_balance_sheet",
            "data": {
                "total_assets": Decimal("100000"),
                "total_liabilities": Decimal("60000"),
                "total_equity": Decimal("50000")  # Should be 40000
            },
            "expected_valid": False,
            "expected_errors": ["Balance sheet equation violation"]
        },

        # Negative assets
        {
            "name": "negative_assets",
            "data": {
                "total_assets": Decimal("-100000"),
                "total_liabilities": Decimal("60000"),
                "total_equity": Decimal("40000")
            },
            "expected_valid": False,
            "expected_errors": ["Negative total assets"]
        },

        # Zero values
        {
            "name": "zero_values",
            "data": {
                "total_assets": Decimal("0"),
                "total_liabilities": Decimal("0"),
                "total_equity": Decimal("0")
            },
            "expected_valid": False,
            "expected_errors": ["Zero total assets", "Zero total equity"]
        },

        # Large numbers (crores)
        {
            "name": "large_numbers",
            "data": {
                "total_assets": Decimal("1500000000000"),  # 1.5 lakh crores
                "total_liabilities": Decimal("900000000000"),  # 90k crores
                "total_equity": Decimal("600000000000")  # 60k crores
            },
            "expected_valid": True,
            "expected_errors": []
        },

        # Decimal precision issues
        {
            "name": "decimal_precision",
            "data": {
                "total_assets": Decimal("100000.123"),
                "total_liabilities": Decimal("60000.456"),
                "total_equity": Decimal("39999.667")  # Slight rounding difference
            },
            "expected_valid": True,  # Should pass with tolerance
            "expected_errors": []
        },

        # Missing required fields
        {
            "name": "missing_fields",
            "data": {
                "total_assets": Decimal("100000")
                # Missing total_liabilities and total_equity
            },
            "expected_valid": False,
            "expected_errors": ["Missing required balance sheet fields"]
        },

        # Non-numeric values
        {
            "name": "non_numeric_values",
            "data": {
                "total_assets": "invalid",
                "total_liabilities": Decimal("60000"),
                "total_equity": Decimal("40000")
            },
            "expected_valid": False,
            "expected_errors": ["Invalid numeric value for total_assets"]
        }
    ]


def create_xbrl_parsing_test_cases() -> List[Dict[str, Any]]:
    """Create XBRL parsing test cases"""
    return [
        {
            "name": "valid_balance_sheet",
            "xbrl_content": create_sample_xbrl_balance_sheet(),
            "expected_success": True,
            "expected_statements": 1,
            "expected_data": {
                "total_assets": 1500000,
                "total_liabilities": 900000,
                "total_equity": 600000
            }
        },

        {
            "name": "valid_income_statement",
            "xbrl_content": create_sample_xbrl_income_statement(),
            "expected_success": True,
            "expected_statements": 1,
            "expected_data": {
                "total_revenue": 850000,
                "profit_after_tax": 250000,
                "basic_eps": 125.50
            }
        },

        {
            "name": "malformed_xbrl",
            "xbrl_content": create_malformed_xbrl_data(),
            "expected_success": False,
            "expected_statements": 0,
            "expected_error": "XML parsing error"
        },

        {
            "name": "negative_values",
            "xbrl_content": create_xbrl_with_negative_values(),
            "expected_success": True,
            "expected_statements": 1,
            "expected_data": {
                "total_assets": -100000,
                "total_liabilities": 60000,
                "total_equity": 40000
            }
        }
    ]
