name: California Legislative Bill Scanner

on:
  schedule:
    # Run every day at 8:00 AM Pacific Time (3:00 PM UTC)
    - cron: '0 15 * * *'
  workflow_dispatch: # Allows manual triggering from GitHub UI
  push:
    paths:
      - 'scan_bills.py'
      - '.github/workflows/bill-scanner.yml'

jobs:
  scan-bills:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        pip install requests beautifulsoup4 lxml
        
    - name: Run bill scanner
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: |
        python scan_bills.py
        
    - name: Check for changes
      id: verify-changed-files
      run: |
        if [ -n "$(git status --porcelain)" ]; then
          echo "changed=true" >> $GITHUB_OUTPUT
        else
          echo "changed=false" >> $GITHUB_OUTPUT
        fi
        
    - name: Commit and push changes
      if: steps.verify-changed-files.outputs.changed == 'true'
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add bills.json
        git commit -m "🏛️ Daily legislative scan: $(date '+%Y-%m-%d %H:%M')"
        git push
        
    - name: Create scan summary
      if: always()
      run: |
        echo "## 📊 Legislative Scan Results" >> $GITHUB_STEP_SUMMARY
        echo "**Date:** $(date)" >> $GITHUB_STEP_SUMMARY
        if [ -f "scan_results.txt" ]; then
          cat scan_results.txt >> $GITHUB_STEP_SUMMARY
        else
          echo "No scan results file found" >> $GITHUB_STEP_SUMMARY
        fi
#!/usr/bin/env python3
"""
California Legislative Bill Scanner
Scans for Assembly bills that have passed through Senate Housing/Judiciary committees
and are currently in Senate Appropriations committee.
"""

import json
import requests
import time
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import re

class CALegislativeScanner:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CA-Legislative-Scanner/1.0 (Research Purpose)'
        })
        self.results = {
            'scan_date': datetime.now().isoformat(),
            'bills_found': 0,
            'new_bills': 0,
            'errors': []
        }
    
    def load_existing_bills(self) -> List[Dict]:
        """Load existing bills from JSON file."""
        try:
            if os.path.exists('bills.json'):
                with open('bills.json', 'r') as f:
                    data = json.load(f)
                    return data.get('bills', [])
            return []
        except Exception as e:
            self.results['errors'].append(f"Error loading existing bills: {str(e)}")
            return []
    
    def save_bills(self, bills: List[Dict]):
        """Save bills to JSON file."""
        try:
            data = {
                'last_updated': datetime.now().isoformat(),
                'bills': bills
            }
            with open('bills.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.results['errors'].append(f"Error saving bills: {str(e)}")
    
    def get_assembly_bills_from_leginfo(self) -> List[Dict]:
        """
        Scrape CA Legislative Information system for Assembly bills.
        This is a simplified version - you may need to adjust based on the actual site structure.
        """
        bills = []
        
        try:
            # Get current session year
            current_year = datetime.now().year
            if datetime.now().month <= 6:
                session_year = f"{current_year-1}-{str(current_year)[2:]}"
            else:
                session_year = f"{current_year}-{str(current_year+1)[2:]}"
            
            print(f"Scanning session: {session_year}")
            
            # Search for Assembly bills in Senate Appropriations
            # This URL structure may need adjustment based on actual CA legislative site
            search_url = f"https://leginfo.legislature.ca.gov/faces/billSearchClient.xhtml"
            
            # For demo purposes, we'll use mock data since the actual scraping
            # would require reverse engineering the CA legislative site's AJAX calls
            bills = self.get_mock_legislative_data()
            
        except Exception as e:
            self.results['errors'].append(f"Error scraping legislative data: {str(e)}")
            print(f"Error: {e}")
        
        return bills
    
    def get_mock_legislative_data(self) -> List[Dict]:
        """
        Mock data for demonstration. In production, this would be replaced
        with actual API calls or web scraping.
        """
        return [
            {
                'bill_number': 'AB-1234',
                'title': 'Housing Development Streamlining Act',
                'author': 'Garcia',
                'summary': 'Streamlines housing development approval processes for affordable housing projects.',
                'committees_passed': ['Senate Housing', 'Senate Judiciary'],
                'current_committee': 'Senate Appropriations',
                'status': 'In Committee',
                'last_action': '2025-07-25',
                'url': 'https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202520260AB1234'
            },
            {
                'bill_number': 'AB-5678',
                'title': 'Tenant Protection Enhancement',
                'author': 'Rodriguez',
                'summary': 'Expands tenant protections and rent stabilization measures statewide.',
                'committees_passed': ['Senate Housing'],
                'current_committee': 'Senate Appropriations',
                'status': 'In Committee',
                'last_action': '2025-07-24',
                'url': 'https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202520260AB5678'
            },
            {
                'bill_number': 'AB-9999',
                'title': 'Criminal Justice Reform Act',
                'author': 'Thompson',
                'summary': 'Reforms sentencing guidelines for non-violent offenses.',
                'committees_passed': ['Senate Judiciary'],
                'current_committee': 'Senate Appropriations',
                'status': 'In Committee',
                'last_action': '2025-07-23',
                'url': 'https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202520260AB9999'
            }
        ]
    
    def filter_relevant_bills(self, bills: List[Dict]) -> List[Dict]:
        """Filter bills that match our criteria."""
        relevant_bills = []
        
        for bill in bills:
            # Check if bill has passed through Housing OR Judiciary committees
            # AND is currently in Appropriations
            committees_passed = bill.get('committees_passed', [])
            current_committee = bill.get('current_committee', '')
            
            has_housing_or_judiciary = any(
                'Housing' in committee or 'Judiciary' in committee 
                for committee in committees_passed
            )
            
            is_in_appropriations = 'Appropriations' in current_committee
            
            if has_housing_or_judiciary and is_in_appropriations:
                relevant_bills.append(bill)
        
        return relevant_bills
    
    def convert_to_tracker_format(self, legislative_bill: Dict) -> Dict:
        """Convert legislative bill data to tracker format."""
        return {
            'id': None,  # Will be set when adding to existing bills
            'billNumber': legislative_bill['bill_number'],
            'title': legislative_bill['title'],
            'author': legislative_bill['author'],
            'committees': legislative_bill['committees_passed'],
            'currentStatus': legislative_bill['current_committee'],
            'analysisStatus': 'needs-analysis',
            'priority': 'medium',
            'dateAdded': datetime.now().strftime('%Y-%m-%d'),
            'notes': '',
            'summary': legislative_bill['summary'],
            'lastAction': legislative_bill.get('last_action', ''),
            'url': legislative_bill.get('url', '')
        }
    
    def scan_and_update(self):
        """Main scanning function."""
        print("🏛️ Starting California Legislative Bill Scan...")
        
        # Load existing bills
        existing_bills = self.load_existing_bills()
        existing_bill_numbers = {bill['billNumber'] for bill in existing_bills}
        
        print(f"📋 Currently tracking {len(existing_bills)} bills")
        
        # Get new legislative data
        legislative_bills = self.get_assembly_bills_from_leginfo()
        relevant_bills = self.filter_relevant_bills(legislative_bills)
        
        self.results['bills_found'] = len(relevant_bills)
        print(f"🔍 Found {len(relevant_bills)} bills matching criteria")
        
        # Convert and filter for new bills
        new_bills = []
        for leg_bill in relevant_bills:
            if leg_bill['bill_number'] not in existing_bill_numbers:
                tracker_bill = self.convert_to_tracker_format(leg_bill)
                new_bills.append(tracker_bill)
        
        # Add new bills to existing collection
        if new_bills:
            # Assign IDs to new bills
            max_id = max([bill.get('id', 0) for bill in existing_bills], default=0)
            for i, bill in enumerate(new_bills):
                bill['id'] = max_id + i + 1
            
            all_bills = existing_bills + new_bills
            self.save_bills(all_bills)
            
            self.results['new_bills'] = len(new_bills)
            print(f"✅ Added {len(new_bills)} new bills to tracker")
            
            # Print new bills for logging
            for bill in new_bills:
                print(f"  📝 {bill['billNumber']}: {bill['title']}")
        else:
            print("📊 No new bills found")
            self.save_bills(existing_bills)  # Update timestamp
        
        # Write results summary
        self.write_scan_summary()
        
        print("🎯 Scan complete!")
    
    def write_scan_summary(self):
        """Write scan results to file for GitHub Actions summary."""
        try:
            with open('scan_results.txt', 'w') as f:
                f.write(f"**Bills Found:** {self.results['bills_found']}\n")
                f.write(f"**New Bills Added:** {self.results['new_bills']}\n")
                
                if self.results['errors']:
                    f.write(f"**Errors:** {len(self.results['errors'])}\n")
                    for error in self.results['errors']:
                        f.write(f"- {error}\n")
                else:
                    f.write("**Status:** ✅ No errors\n")
                
                f.write(f"**Last Scan:** {self.results['scan_date']}\n")
        except Exception as e:
            print(f"Error writing summary: {e}")

def main():
    scanner = CALegislativeScanner()
    scanner.scan_and_update()

if __name__ == "__main__":
    main()
