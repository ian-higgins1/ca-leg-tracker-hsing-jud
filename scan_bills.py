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
        except
