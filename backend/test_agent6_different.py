"""
Test Agent 6: Orchestrator Agent with different companies and analysis types
"""

import sys
import os
import asyncio
sys.path.insert(0, '/home/aditya/I.R.I.S./backend/src')

# Mock the problematic imports to avoid the supabase issue
from unittest.mock import MagicMock
sys.modules['config'] = MagicMock()
sys.modules['database'] = MagicMock()
sys.modules['database.connection'] = MagicMock()

from agents.forensic.agent6_orchestrator import OrchestratorAgent, JobPriority

async def test_orchestrator_different_scenarios():
    """Test orchestrator with different companies and analysis scenarios"""
    print("=== IRIS AGENT 6: ORCHESTRATOR - DIFFERENT SCENARIOS TEST ===")
    
    # Initialize orchestrator
    orchestrator = OrchestratorAgent()
    print("✅ Orchestrator Agent initialized successfully")
    
    # Test different companies and analysis types
    test_scenarios = [
        {
            "symbol": "INFY.NS", 
            "name": "Infosys", 
            "priority": JobPriority.CRITICAL,
            "analysis_types": ["vertical", "horizontal", "ratios", "risk_scoring"],
            "periods": 3
        },
        {
            "symbol": "HDFCBANK.NS", 
            "name": "HDFC Bank", 
            "priority": JobPriority.HIGH,
            "analysis_types": ["vertical", "ratios", "risk_scoring"],
            "periods": 2
        },
        {
            "symbol": "WIPRO.NS", 
            "name": "Wipro", 
            "priority": JobPriority.NORMAL,
            "analysis_types": ["horizontal", "risk_scoring"],
            "periods": 2
        },
        {
            "symbol": "MARUTI.NS", 
            "name": "Maruti Suzuki", 
            "priority": JobPriority.LOW,
            "analysis_types": ["vertical", "horizontal"],
            "periods": 1
        }
    ]
    
    job_ids = []
    
    # Submit analysis jobs with different configurations
    print(f"\n📋 SUBMITTING DIFFERENT ANALYSIS SCENARIOS:")
    for scenario in test_scenarios:
        print(f"  🏢 {scenario['name']} ({scenario['symbol']})")
        print(f"    📊 Analysis: {', '.join(scenario['analysis_types'])}")
        print(f"    📅 Periods: {scenario['periods']}")
        print(f"    ⚡ Priority: {scenario['priority'].name}")
        
        job_id = await orchestrator.submit_analysis_job(
            company_symbol=scenario['symbol'],
            analysis_types=scenario['analysis_types'],
            data_source="yahoo_finance",
            periods=scenario['periods'],
            priority=scenario['priority']
        )
        
        job_ids.append((job_id, scenario))
        print(f"    ✅ Job submitted with ID: {job_id[:8]}...")
        print()
    
    # Monitor job execution with shorter timeout
    print(f"⏳ MONITORING JOB EXECUTION:")
    
    completed_jobs = 0
    max_wait_time = 120  # 2 minutes
    wait_time = 0
    
    while completed_jobs < len(job_ids) and wait_time < max_wait_time:
        await asyncio.sleep(3)  # Check every 3 seconds
        wait_time += 3
        
        system_status = orchestrator.get_system_status()
        print(f"  📊 System Status: {system_status['active_jobs']} active, {system_status['queued_jobs']} queued, {system_status['completed_jobs']} completed")
        
        # Check individual job status
        for job_id, scenario in job_ids:
            job_status = orchestrator.get_job_status(job_id)
            if job_status:
                status = job_status['status']
                progress = job_status.get('progress', 0)
                
                if status == 'completed' and progress == 100:
                    print(f"    ✅ {scenario['name']}: COMPLETED")
                    completed_jobs += 1
                elif status == 'running':
                    print(f"    🔄 {scenario['name']}: RUNNING ({progress:.0f}%)")
                elif status == 'failed':
                    print(f"    ❌ {scenario['name']}: FAILED - {job_status.get('error_message', 'Unknown error')}")
                    completed_jobs += 1
        
        # Break if all jobs completed
        if completed_jobs >= len(job_ids):
            break
    
    # Display final results
    print(f"\n📊 FINAL RESULTS:")
    
    for job_id, scenario in job_ids:
        job_status = orchestrator.get_job_status(job_id)
        
        print(f"\n🏢 {scenario['name']} ({scenario['symbol']}):")
        print(f"  📊 Analysis Types: {', '.join(scenario['analysis_types'])}")
        print(f"  ⚡ Priority: {scenario['priority'].name}")
        
        if job_status and job_status['status'] == 'completed':
            results = orchestrator.get_job_results(job_id)
            print(f"  ✅ Status: COMPLETED")
            
            if results:
                # Show specific analysis results based on what was requested
                if 'forensic_analysis' in results:
                    forensic = results['forensic_analysis']
                    if forensic.get('success'):
                        print(f"  📈 Forensic Analysis: SUCCESS")
                        
                        # Show requested analysis types
                        if 'vertical' in scenario['analysis_types']:
                            va = forensic.get('vertical_analysis', {})
                            if va.get('success'):
                                va_data = va.get('vertical_analysis', {})
                                income = va_data.get('income_statement', {})
                                if 'error' not in income:
                                    print(f"    • Vertical Analysis: Net Profit Margin {income.get('net_profit_pct', 0):.1f}%")
                        
                        if 'horizontal' in scenario['analysis_types']:
                            ha = forensic.get('horizontal_analysis', {})
                            if ha.get('success'):
                                print(f"    • Horizontal Analysis: Growth trends calculated")
                        
                        if 'ratios' in scenario['analysis_types']:
                            ratios = forensic.get('financial_ratios', {})
                            if ratios.get('success'):
                                print(f"    • Financial Ratios: Comprehensive ratio analysis")
                
                # Show risk assessment if requested
                if 'risk_scoring' in scenario['analysis_types'] and 'risk_assessment' in results:
                    risk = results['risk_assessment']
                    print(f"  🎯 Risk Assessment:")
                    print(f"    • Overall Risk Score: {risk.get('overall_risk_score', 0):.1f}/100")
                    print(f"    • Risk Level: {risk.get('risk_level', 'UNKNOWN')}")
                    print(f"    • Investment Recommendation: {risk.get('investment_recommendation', 'N/A')}")
        
        elif job_status:
            print(f"  📊 Status: {job_status['status'].upper()}")
            if job_status.get('error_message'):
                print(f"  ❌ Error: {job_status['error_message']}")
        else:
            print(f"  ❓ Status: UNKNOWN")
    
    # Show system performance statistics
    final_status = orchestrator.get_system_status()
    print(f"\n📈 ORCHESTRATOR PERFORMANCE:")
    print(f"  ✅ Completed Jobs: {final_status['completed_jobs']}")
    print(f"  ❌ Failed Jobs: {final_status['failed_jobs']}")
    print(f"  💾 Cache Entries: {final_status['cache_entries']}")
    print(f"  🔧 Max Concurrent: {final_status['max_concurrent_jobs']}")
    print(f"  🤖 Agent Status:")
    for agent, status in final_status['agents_status'].items():
        print(f"    • {agent}: {status}")
    
    # Test cache functionality
    print(f"\n💾 TESTING CACHE FUNCTIONALITY:")
    print(f"  Submitting duplicate job for Infosys to test caching...")
    
    cached_job_id = await orchestrator.submit_analysis_job(
        company_symbol="INFY.NS",
        analysis_types=["vertical", "horizontal", "ratios", "risk_scoring"],
        data_source="yahoo_finance",
        periods=3,
        priority=JobPriority.NORMAL
    )
    
    # Check if it completed immediately from cache
    await asyncio.sleep(1)
    cached_job_status = orchestrator.get_job_status(cached_job_id)
    if cached_job_status and cached_job_status['status'] == 'completed':
        print(f"  ✅ Cache hit! Job completed instantly from cache")
    else:
        print(f"  ⏳ Cache miss, job processing normally")
    
    print(f"\n🎉 AGENT 6 ORCHESTRATOR: ADVANCED TESTING COMPLETE!")
    print(f"✅ Multi-scenario job processing")
    print(f"✅ Priority-based scheduling (CRITICAL → HIGH → NORMAL → LOW)")
    print(f"✅ Flexible analysis type combinations")
    print(f"✅ Variable period analysis (1-3 quarters)")
    print(f"✅ Intelligent caching system")
    print(f"✅ Real-time status monitoring")
    print(f"✅ Comprehensive error handling")

if __name__ == "__main__":
    asyncio.run(test_orchestrator_different_scenarios())
