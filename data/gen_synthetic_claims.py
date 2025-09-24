#!/usr/bin/env python3
"""
Synthetic Claims Generator
Generates 10 JSON claim objects for testing purposes.
"""

import json
import uuid
import random
from datetime import datetime, timedelta
from pathlib import Path


def generate_claim_item():
    """Generate a single claim item (medical service/treatment)."""
    services = [
        {"code": "01010", "desc": "Allgemeine Beratung", "typical_amount": 45.50},
        {"code": "01020", "desc": "Ausführliche Beratung", "typical_amount": 78.20},
        {"code": "01030", "desc": "Körperliche Untersuchung", "typical_amount": 25.30},
        {"code": "02100", "desc": "Labor Grunduntersuchung", "typical_amount": 32.10},
        {"code": "03210", "desc": "Röntgen Thorax", "typical_amount": 89.40},
        {"code": "04110", "desc": "Physiotherapie", "typical_amount": 55.75},
    ]
    
    service = random.choice(services)
    # Add some variance to typical amounts
    amount_variance = random.uniform(0.8, 1.2)
    
    return {
        "date": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
        "provider": f"Praxis Dr. {random.choice(['Mueller', 'Schmidt', 'Weber', 'Wagner', 'Becker'])}",
        "code": service["code"],
        "description": service["desc"],
        "net_amount": round(service["typical_amount"] * amount_variance, 2),
        "currency": "EUR"
    }


def generate_synthetic_claim():
    """Generate a single synthetic claim object."""
    claim_id = f"CLM-{uuid.uuid4().hex[:8].upper()}"
    customer_id = f"CUST-{random.randint(100000, 999999)}"
    
    # Generate 1-4 items per claim
    num_items = random.randint(1, 4)
    items = [generate_claim_item() for _ in range(num_items)]
    
    claim = {
        "claim_id": claim_id,
        "customer_id": customer_id,
        "policy_number": f"POL-{random.randint(1000000, 9999999)}",
        "policy_type": random.choice(["hallesche_nk_select_s", "tk_statutory"]),
        "items": items,
        "documents": [],  # Will be populated when documents are uploaded
        "status": "received",
        "created_at": (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat(),
        "total_claimed": round(sum(item["net_amount"] for item in items), 2),
        "customer_info": {
            "name": f"{random.choice(['Max', 'Anna', 'Peter', 'Lisa', 'Thomas'])} {random.choice(['Müller', 'Schmidt', 'Weber', 'Wagner', 'Becker'])}",
            "dob": f"{random.randint(1950, 2000)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "address": f"Musterstraße {random.randint(1, 100)}, {random.randint(10000, 99999)} Musterstadt"
        }
    }
    
    return claim


def main():
    """Generate 10 synthetic claims and save them to data/synthetic/"""
    output_dir = Path("data/synthetic")
    output_dir.mkdir(exist_ok=True)
    
    print("Generating 10 synthetic claims...")
    
    for i in range(1, 11):
        claim = generate_synthetic_claim()
        filename = f"claim_{i:03d}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(claim, f, indent=2, ensure_ascii=False)
        
        print(f"Generated: {filename} (ID: {claim['claim_id']}, Total: €{claim['total_claimed']})")
    
    print(f"\nSuccessfully generated 10 synthetic claims in {output_dir}/")


if __name__ == "__main__":
    main()
