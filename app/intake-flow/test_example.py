"""
Test script demonstrating the Analytics Intake System
Run this to see example interactions and outputs
"""

import json
from datetime import datetime

def simulate_request_output():
    """
    Demonstrates the expected JSON output format for different request types
    """
    
    # Example 1: Sales Report Request
    sales_report_example = {
        "basic_info": {
            "name": "Sarah Johnson",
            "role": "Regional Sales Manager",
            "department": "Sales - West Coast", 
            "timeline": "End of this week",
            "collected_at": datetime.now().isoformat()
        },
        "request_type": "reports",
        "requirements": {
            "purpose": "Q2 sales performance analysis for executive review",
            "metrics": [
                "total_revenue",
                "conversion_rate", 
                "average_deal_size",
                "sales_cycle_length",
                "lead_sources"
            ],
            "data_sources": ["Salesforce CRM", "HubSpot", "Google Analytics"],
            "time_period": "Q2 2025 (April-June)",
            "filters": "West Coast region, Enterprise deals >$50K",
            "output_format": "Executive PowerPoint with data tables",
            "audience": "VP Sales, Regional Directors",
            "additional_notes": "Include comparison to Q1 and same period last year"
        },
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "session_id": "session_abc123",
            "status": "pending_review"
        }
    }
    
    # Example 2: Dashboard Update Request  
    dashboard_update_example = {
        "basic_info": {
            "name": "Mike Chen",
            "role": "VP of Marketing",
            "department": "Marketing",
            "timeline": "Next two weeks", 
            "collected_at": datetime.now().isoformat()
        },
        "request_type": "dashboard",
        "requirements": {
            "purpose": "Update existing executive marketing dashboard",
            "dashboard_name": "Marketing Performance Executive Dashboard",
            "dashboard_location": "Tableau Server - Executive Folder",
            "changes_needed": [
                "Add TikTok advertising metrics",
                "Include customer acquisition cost by channel",
                "Update attribution model for multi-touch"
            ],
            "new_visualizations": [
                "Social media ROI comparison chart",
                "Customer journey funnel with new touchpoints"
            ],
            "refresh_frequency": "Daily at 6 AM",
            "target_audience": "C-suite, Marketing leadership",
            "integration_needs": "Email alerts for CAC threshold breaches"
        },
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "session_id": "session_def456", 
            "status": "pending_review"
        }
    }
    
    # Example 3: Report Update Request
    report_update_example = {
        "basic_info": {
            "name": "Lisa Rodriguez",
            "role": "Content Director",
            "department": "Editorial",
            "timeline": "This month",
            "collected_at": datetime.now().isoformat()
        },
        "request_type": "updates",
        "requirements": {
            "existing_report_name": "Weekly Content Performance Report",
            "current_location": "Google Drive - Editorial Shared Folder",
            "current_frequency": "Weekly, sent Mondays",
            "changes_needed": [
                "Add video content metrics (YouTube, TikTok)",
                "Include engagement rate by content type", 
                "Add competitor benchmarking section"
            ],
            "reason_for_update": "Expanding video content strategy, need performance tracking",
            "new_data_sources": ["YouTube Analytics", "TikTok Analytics", "SEMrush"],
            "distribution_changes": "Add VP Product to recipient list",
            "format_changes": "Include executive summary at top"
        },
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "session_id": "session_ghi789",
            "status": "pending_review"
        }
    }
    
    # Save examples to demonstrate output
    examples = [
        ("sales_report_example.json", sales_report_example),
        ("dashboard_update_example.json", dashboard_update_example), 
        ("report_update_example.json", report_update_example)
    ]
    
    print("Analytics Intake System - Example Outputs")
    print("=" * 50)
    
    for filename, data in examples:
        print(f"\n📄 {filename}")
        print("-" * 30)
        
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Print summary
        basic_info = data['basic_info']
        requirements = data['requirements']
        
        print(f"Requester: {basic_info['name']} ({basic_info['role']})")
        print(f"Department: {basic_info['department']}")
        print(f"Request Type: {data['request_type']}")
        print(f"Timeline: {basic_info['timeline']}")
        
        if data['request_type'] == 'reports':
            print(f"Purpose: {requirements['purpose']}")
            print(f"Metrics: {len(requirements['metrics'])} metrics requested")
        elif data['request_type'] == 'dashboard':
            print(f"Dashboard: {requirements['dashboard_name']}")
            print(f"Changes: {len(requirements['changes_needed'])} changes requested")
        elif data['request_type'] == 'updates':
            print(f"Report: {requirements['existing_report_name']}")
            print(f"Changes: {len(requirements['changes_needed'])} changes requested")
            
        print(f"✅ Saved to {filename}")
    
    print(f"\n🎉 Generated {len(examples)} example analytics requests!")
    print("\nTo run the actual ADK system:")
    print("1. Set up your .env file with your Google API key")
    print("2. Get your API key from: https://aistudio.google.com/app/apikey")
    print("3. Run: adk web")
    print("4. Select 'analytics_intake_coordinator' from dropdown")
    print("5. Start chatting with the system!")


if __name__ == "__main__":
    simulate_request_output()