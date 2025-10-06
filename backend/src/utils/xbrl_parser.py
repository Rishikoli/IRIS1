"""
Project IRIS - XBRL Parser Utility
Parse XBRL financial statements for testing and validation
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal, InvalidOperation
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class XBRLParser:
    """XBRL parser for financial statement data"""

    def __init__(self):
        self.namespaces = {
            'xbrli': 'http://www.xbrl.org/2003/instance',
            'xbrldi': 'http://xbrl.org/2006/xbrldi'
        }

    def parse_xbrl_data(self, xbrl_content: str) -> Dict[str, Any]:
        """Parse XBRL content and extract financial data"""
        try:
            # Parse XML
            root = ET.fromstring(xbrl_content)

            # Register namespaces for XPath
            for prefix, uri in self.namespaces.items():
                ET.register_namespace(prefix, uri)

            result = {
                "success": True,
                "entity_info": self._extract_entity_info(root),
                "contexts": self._extract_contexts(root),
                "units": self._extract_units(root),
                "financial_data": self._extract_financial_data(root),
                "metadata": {
                    "parsed_at": datetime.now().isoformat(),
                    "xbrl_version": "2.1"
                }
            }

            return result

        except ET.ParseError as e:
            logger.error(f"XBRL parsing error: {e}")
            return {
                "success": False,
                "error": f"XML parsing error: {str(e)}",
                "error_type": "parse_error"
            }

        except Exception as e:
            logger.error(f"Unexpected XBRL parsing error: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_type": "unexpected_error"
            }

    def _extract_entity_info(self, root: ET.Element) -> Dict[str, Any]:
        """Extract entity information from XBRL"""
        entity_info = {}

        # Find entity element using namespace-aware search
        entity_elem = root.find('.//{http://www.xbrl.org/2003/instance}entity')
        if entity_elem is not None:
            # Extract identifier
            identifier_elem = entity_elem.find('.//{http://www.xbrl.org/2003/instance}identifier')
            if identifier_elem is not None:
                entity_info["identifier"] = identifier_elem.text
                entity_info["identifier_scheme"] = identifier_elem.get("scheme")

            # Extract segments if present
            segment_elem = entity_elem.find('.//{http://www.xbrl.org/2003/instance}segment')
            if segment_elem is not None:
                entity_info["segments"] = self._extract_segments(segment_elem)

        return entity_info

    def _extract_contexts(self, root: ET.Element) -> Dict[str, Any]:
        """Extract context information from XBRL"""
        contexts = {}

        # Find all context elements using namespace-aware search
        context_elems = root.findall('.//{http://www.xbrl.org/2003/instance}context')
        for context_elem in context_elems:
            context_id = context_elem.get("id")
            if context_id:
                contexts[context_id] = {
                    "entity": self._extract_context_entity(context_elem),
                    "period": self._extract_context_period(context_elem),
                    "scenario": self._extract_context_scenario(context_elem)
                }

        return contexts

    def _extract_context_entity(self, context_elem: ET.Element) -> Dict[str, Any]:
        """Extract entity from context"""
        entity_info = {}

        entity_elem = context_elem.find('xbrli:entity', self.namespaces)
        if entity_elem is not None:
            identifier_elem = entity_elem.find('xbrli:identifier', self.namespaces)
            if identifier_elem is not None:
                entity_info["identifier"] = identifier_elem.text
                entity_info["scheme"] = identifier_elem.get("scheme")

        return entity_info

    def _extract_context_period(self, context_elem: ET.Element) -> Dict[str, Any]:
        """Extract period from context"""
        period_info = {}

        period_elem = context_elem.find('xbrli:period', self.namespaces)
        if period_elem is not None:
            # Check for instant (balance sheet date)
            instant_elem = period_elem.find('xbrli:instant', self.namespaces)
            if instant_elem is not None:
                period_info["type"] = "instant"
                period_info["date"] = instant_elem.text

            # Check for duration (income statement period)
            start_date_elem = period_elem.find('xbrli:startDate', self.namespaces)
            end_date_elem = period_elem.find('xbrli:endDate', self.namespaces)
            if start_date_elem is not None and end_date_elem is not None:
                period_info["type"] = "duration"
                period_info["start_date"] = start_date_elem.text
                period_info["end_date"] = end_date_elem.text

        return period_info

    def _extract_context_scenario(self, context_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """Extract scenario from context (if present)"""
        scenario_elem = context_elem.find('xbrli:scenario', self.namespaces)
        if scenario_elem is not None:
            return {"dimensions": self._extract_dimensions(scenario_elem)}
        return None

    def _extract_dimensions(self, scenario_elem: ET.Element) -> Dict[str, Any]:
        """Extract dimension information"""
        dimensions = {}

        # Find explicit members
        explicit_members = scenario_elem.findall('.//xbrldi:explicitMember', self.namespaces)
        for member in explicit_members:
            dimension = member.get("dimension")
            value = member.text
            if dimension:
                dimensions[dimension] = value

        return dimensions

    def _extract_units(self, root: ET.Element) -> Dict[str, Any]:
        """Extract unit information from XBRL"""
        units = {}

        unit_elems = root.findall('.//{http://www.xbrl.org/2003/instance}unit')
        for unit_elem in unit_elems:
            unit_id = unit_elem.get("id")
            if unit_id:
                # Extract measure
                measure_elem = unit_elem.find('.//{http://www.xbrl.org/2003/instance}measure')
                if measure_elem is not None:
                    units[unit_id] = {
                        "measure": measure_elem.text,
                        "multipliers": self._extract_unit_multipliers(unit_elem)
                    }

        return units

    def _extract_unit_multipliers(self, unit_elem: ET.Element) -> List[Dict[str, Any]]:
        """Extract unit multipliers"""
        multipliers = []

        divide_elem = unit_elem.find('xbrli:divide', self.namespaces)
        if divide_elem is not None:
            numerator = divide_elem.find('xbrli:numerator/xbrli:measure', self.namespaces)
            denominator = divide_elem.find('xbrli:denominator/xbrli:measure', self.namespaces)

            if numerator is not None and denominator is not None:
                multipliers.append({
                    "type": "divide",
                    "numerator": numerator.text,
                    "denominator": denominator.text
                })

        return multipliers

    def _extract_financial_data(self, root: ET.Element) -> Dict[str, Any]:
        """Extract financial data from XBRL"""
        financial_data = {}

        # Find all non-XBRL elements (these contain the actual data)
        for elem in root.iter():
            # Skip XBRL infrastructure elements
            if elem.tag.startswith('{http://www.xbrl.org/2003/instance}'):
                continue

            if elem.tag.startswith('{http://xbrl.org/2006/xbrldi}'):
                continue

            # Extract financial data
            tag_name = elem.tag.split('}')[-1]  # Remove namespace
            context_ref = elem.get("contextRef")
            unit_ref = elem.get("unitRef")
            decimals = elem.get("decimals")
            value = elem.text

            if value and context_ref:
                data_point = {
                    "value": self._safe_decimal(value),
                    "context": context_ref,
                    "unit": unit_ref,
                    "decimals": decimals,
                    "tag": tag_name
                }

                if tag_name not in financial_data:
                    financial_data[tag_name] = []
                financial_data[tag_name].append(data_point)

        return financial_data

    def _safe_decimal(self, value) -> Optional[Decimal]:
        """Safely convert string to Decimal"""
        if value is None:
            return None
            
        try:
            # Handle comma separators and negative values
            if isinstance(value, str):
                import re
                cleaned_value = value.replace(",", "").strip()
                # Remove any non-numeric characters except decimal point and minus sign
                cleaned_value = re.sub(r'[^0-9.-]', '', cleaned_value)
                return Decimal(cleaned_value) if cleaned_value else None
            else:
                return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            logger.warning(f"Could not convert '{value}' to Decimal")
            return None

    def _extract_segments(self, segment_elem: ET.Element) -> Dict[str, Any]:
        """Extract segment information"""
        segments = {}

        # Find explicit members in segments
        explicit_members = segment_elem.findall('.//xbrldi:explicitMember', self.namespaces)
        for member in explicit_members:
            dimension = member.get("dimension")
            value = member.text
            if dimension:
                segments[dimension] = value

        return segments


def normalize_xbrl_to_standard_schema(xbrl_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert XBRL data to standard financial statement schema"""
    normalized_statements = []

    try:
        # Extract contexts and financial data
        contexts = xbrl_data.get("contexts", {})
        financial_data = xbrl_data.get("financial_data", {})

        # Group data by context (reporting period)
        for context_id, context_info in contexts.items():
            statement = {
                "statement_id": f"xbrl_{context_id}",
                "source": "xbrl",
                "context_id": context_id,
                "period_info": context_info,
                "extracted_at": datetime.now().isoformat()
            }

            # Extract balance sheet data
            if "Assets" in str(financial_data).lower() or "Equity" in str(financial_data).lower():
                bs_data = _extract_balance_sheet_data(financial_data, context_id)
                if bs_data:
                    statement.update({
                        "statement_type": "balance_sheet",
                        "data": bs_data
                    })
                    normalized_statements.append(statement)

            # Extract income statement data
            if "Revenue" in str(financial_data).lower() or "Profit" in str(financial_data).lower():
                is_data = _extract_income_statement_data(financial_data, context_id)
                if is_data:
                    statement.update({
                        "statement_type": "income_statement",
                        "data": is_data
                    })
                    normalized_statements.append(statement)

            # Extract cash flow data
            if "Cash" in str(financial_data).lower():
                cf_data = _extract_cash_flow_data(financial_data, context_id)
                if cf_data:
                    statement.update({
                        "statement_type": "cash_flow",
                        "data": cf_data
                    })
                    normalized_statements.append(statement)

    except Exception as e:
        logger.error(f"Error normalizing XBRL data: {e}")
        return []

    return normalized_statements


def _extract_balance_sheet_data(financial_data: Dict[str, Any], context_id: str) -> Optional[Dict[str, Any]]:
    """Extract balance sheet data for specific context"""
    balance_sheet = {}

    # Find data points for this context
    for tag_name, data_points in financial_data.items():
        for data_point in data_points:
            if data_point.get("context") == context_id and data_point.get("value") is not None:
                value = data_point["value"]

                # Map XBRL tags to standard fields
                tag_lower = tag_name.lower()

                if "totalassets" in tag_lower or "assets" in tag_lower:
                    balance_sheet["total_assets"] = float(value)
                elif "totalliabilities" in tag_lower or "liabilities" in tag_lower:
                    balance_sheet["total_liabilities"] = float(value)
                elif "totalstockholdersequity" in tag_lower or "equity" in tag_lower:
                    balance_sheet["total_equity"] = float(value)
                elif "propertyplantequipment" in tag_lower:
                    balance_sheet["property_plant_equipment"] = float(value)
                elif "currentassets" in tag_lower:
                    balance_sheet["current_assets"] = float(value)
                elif "currentliabilities" in tag_lower:
                    balance_sheet["current_liabilities"] = float(value)
                elif "noncurrentassets" in tag_lower:
                    balance_sheet["non_current_assets"] = float(value)
                elif "noncurrentliabilities" in tag_lower:
                    balance_sheet["non_current_liabilities"] = float(value)

    # Only return if we have the three main components
    if all(key in balance_sheet for key in ["total_assets", "total_liabilities", "total_equity"]):
        balance_sheet["currency"] = "INR"
        balance_sheet["units"] = "crores"
        return balance_sheet

    return None


def _extract_income_statement_data(financial_data: Dict[str, Any], context_id: str) -> Optional[Dict[str, Any]]:
    """Extract income statement data for specific context"""
    income_statement = {}

    # Find data points for this context
    for tag_name, data_points in financial_data.items():
        for data_point in data_points:
            if data_point.get("context") == context_id and data_point.get("value") is not None:
                value = data_point["value"]

                # Map XBRL tags to standard fields
                tag_lower = tag_name.lower()

                if "revenue" in tag_lower or "totalrevenue" in tag_lower:
                    income_statement["total_revenue"] = float(value)
                elif "costofrevenue" in tag_lower or "costofmaterials" in tag_lower:
                    income_statement["cost_of_revenue"] = float(value)
                elif "grossprofit" in tag_lower:
                    income_statement["gross_profit"] = float(value)
                elif "operatingincome" in tag_lower:
                    income_statement["operating_income"] = float(value)
                elif "netincome" in tag_lower or "profitaftertax" in tag_lower:
                    income_statement["net_profit"] = float(value)
                elif "taxexpense" in tag_lower:
                    income_statement["tax_expense"] = float(value)
                elif "interestexpense" in tag_lower or "financecosts" in tag_lower:
                    income_statement["interest_expense"] = float(value)
                elif "basiceps" in tag_lower:
                    income_statement["basic_eps"] = float(value)
                elif "dilutedeps" in tag_lower:
                    income_statement["diluted_eps"] = float(value)

    # Only return if we have key components
    if "total_revenue" in income_statement and "net_profit" in income_statement:
        income_statement["currency"] = "INR"
        income_statement["units"] = "crores"
        return income_statement

    return None


def _extract_cash_flow_data(financial_data: Dict[str, Any], context_id: str) -> Optional[Dict[str, Any]]:
    """Extract cash flow data for specific context"""
    cash_flow = {}

    # Find data points for this context
    for tag_name, data_points in financial_data.items():
        for data_point in data_points:
            if data_point.get("context") == context_id and data_point.get("value") is not None:
                value = data_point["value"]

                # Map XBRL tags to standard fields
                tag_lower = tag_name.lower()

                if "netcash" in tag_lower:
                    if "operating" in tag_lower:
                        cash_flow["net_cash_from_operating_activities"] = float(value)
                    elif "investing" in tag_lower:
                        cash_flow["net_cash_from_investing_activities"] = float(value)
                    elif "financing" in tag_lower:
                        cash_flow["net_cash_from_financing_activities"] = float(value)
                elif "cashatend" in tag_lower or "cashatbeginning" in tag_lower:
                    if "end" in tag_lower:
                        cash_flow["cash_at_end"] = float(value)
                    elif "beginning" in tag_lower:
                        cash_flow["cash_at_beginning"] = float(value)

    # Only return if we have key components
    if len(cash_flow) >= 2:  # At least net cash and ending balance
        cash_flow["currency"] = "INR"
        cash_flow["units"] = "crores"
        return cash_flow

    return None
