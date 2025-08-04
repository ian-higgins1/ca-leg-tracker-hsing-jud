import json
import os
from datetime import datetime

def main():
    print("🏛️ Starting California Legislative Bill Scan...")
    
    # Sample bills for testing
    sample_bills = [
        {
            'id': 1,
            'billNumber': 'AB-1234',
            'title': 'Housing Development Streamlining Act',
            'author': 'Garcia',
            'committees': ['Senate Housing', 'Senate Judiciary'],
            'currentStatus': 'Senate Appropriations',
            'analysisStatus': 'needs-analysis',
            'priority': 'medium',
            'dateAdded': datetime.now().strftime('%Y-%m-%d'),
            'notes': '',
            'summary': 'Streamlines housing development approval processes for affordable housing projects.'
        },
        {
            'id': 2,
            'billNumber': 'AB-5678',
            'title': 'Tenant Protection Enhancement',
            'author': 'Rodriguez',
            'committees': ['Senate Housing'],
            'currentStatus': 'Senate Appropriations',
            'analysisStatus': 'needs-analysis',
            'priority': 'medium',
            'dateAdded': datetime.now().strftime('%Y-%m-%d'),
            'notes': '',
            'summary': 'Expands tenant protections and rent stabilization measures statewide.'
        }
    ]
    
    # Save bills to JSON file
    data = {
        'last_updated': datetime.now().isoformat(),
        'bills': sample_bills
    }
