#!/usr/bin/env python3
"""
Focused test to identify horizontal analysis issues
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🔍 DEBUGGING HORIZONTAL ANALYSIS")
print("=" * 40)

# Simple implementation to debug step by step
class DebugForensicAnalysisAgent:
    def horizontal_analysis(self, financial_statements):
        """Debug version of horizontal analysis"""
        print(f"\n📊 DEBUG: horizontal_analysis input")
        print(f"Number of statements: {len(financial_statements)}")

        # Debug: Print input data structure
        for i, stmt in enumerate(financial_statements):
            print(f"Statement {i}:")
            print(f"  Period: {stmt.get('period_end')}")
            print(f"  Data keys: {list(stmt.get('data', {}).keys())}")

        try:
            # Sort statements by period - THIS IS THE ISSUE
            print(f"\n🔧 Sorting statements by period_end...")
            sorted_statements = sorted(financial_statements,
                                     key=lambda x: x.get("period_end", ""))

            print("Sorted periods:")
            for i, stmt in enumerate(sorted_statements):
                print(f"  {i}: {stmt.get('period_end')} - {stmt.get('statement_type')}")

            horizontal_results = {}

            for i in range(1, len(sorted_statements)):
                current = sorted_statements[i]
                previous = sorted_statements[i-1]

                print(f"\n🔍 Comparing periods {i-1} to {i}:")
                print(f"  Previous: {previous.get('period_end')} - {previous.get('statement_type')}")
                print(f"  Current: {current.get('period_end')} - {current.get('statement_type')}")

                period_key = f"{previous.get('period_end')}_to_{current.get('period_end')}"
                print(f"  Period key: {period_key}")

                growth_rates = self._calculate_growth_rates(
                    previous.get("data", {}),
                    current.get("data", {})
                )

                print(f"  Growth rates calculated: {len(growth_rates)} metrics")
                horizontal_results[period_key] = growth_rates

            return {
                "success": True,
                "horizontal_analysis": horizontal_results,
                "debug_info": {
                    "input_count": len(financial_statements),
                    "sorted_count": len(sorted_statements),
                    "comparisons_made": len(sorted_statements) - 1
                }
            }

        except Exception as e:
            print(f"❌ Error in horizontal analysis: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}

    def _calculate_growth_rates(self, previous, current):
        """Calculate growth rates between two periods"""
        print("  📈 Calculating growth rates...")
        print(f"    Previous data keys: {list(previous.keys())}")
        print(f"    Current data keys: {list(current.keys())}")

        growth_rates = {}

        key_metrics = [
            "total_revenue", "gross_profit", "operating_income", "net_profit",
            "total_assets", "total_liabilities", "total_equity"
        ]

        for metric in key_metrics:
            prev_value = previous.get(metric, 0)
            curr_value = current.get(metric, 0)

            print(f"    {metric}: prev={prev_value}, curr={curr_value}")

            if prev_value != 0:
                growth_rate = ((curr_value - prev_value) / prev_value) * 100
                growth_rates[f"{metric}_growth_pct"] = round(growth_rate, 2)
                print(f"      Growth: {growth_rate:.2f}%")
            else:
                growth_rates[f"{metric}_growth_pct"] = None
                print(f"      Growth: N/A (prev=0)")

        return growth_rates

# Test data that should work
test_financial_data = [
    {
        'statement_type': 'income_statement',
        'period_end': '2022-03-31',
        'data': {
            'total_revenue': 900000,
            'gross_profit': 350000,
            'operating_income': 175000,
            'net_profit': 130000,
            'total_assets': 1800000,
            'total_liabilities': 900000,
            'total_equity': 900000
        }
    },
    {
        'statement_type': 'income_statement',
        'period_end': '2023-03-31',
        'data': {
            'total_revenue': 1000000,
            'gross_profit': 400000,
            'operating_income': 200000,
            'net_profit': 150000,
            'total_assets': 2000000,
            'total_liabilities': 1000000,
            'total_equity': 1000000
        }
    }
]

def main():
    print("Creating debug agent...")
    agent = DebugForensicAnalysisAgent()

    print(f"\nTesting with {len(test_financial_data)} statements...")
    result = agent.horizontal_analysis(test_financial_data)

    print(f"\n✅ Success: {result.get('success', False)}")
    if result.get('success'):
        ha = result.get('horizontal_analysis', {})
        print(f"\n📈 Results: {len(ha)} period comparisons")

        for period, metrics in ha.items():
            print(f"\nPeriod: {period}")
            for key, value in metrics.items():
                if value is not None:
                    print(f"  {key}: {value:.2f}%")
                else:
                    print(f"  {key}: N/A")

        debug_info = result.get('debug_info', {})
        print(f"\n🔧 Debug info: {debug_info}")

if __name__ == "__main__":
    main()
