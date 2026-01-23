#!/usr/bin/env python3
"""
Script to fetch device models from Gizwits API and save them as JSON files.
This helps create missing attribute model files for devices.
"""
import asyncio
import aiohttp
import json
import sys

GIZWITS_APP_ID = "c3703c4888ec4736a3a0d9425c321604"
TOKEN = "b0c7ae238f4641f5bfa771e732107033"  # From logs
REGION = "eu"

# Product keys that need model files
MISSING_PRODUCT_KEYS = [
    "6a5c47b3ea364ecb841b47f5997a1775",  # P_38ADE0
    "5ab6019f2dbb4ae7a42b48d2b8ce0530",  # Doser Aquaium
]

async def fetch_product_info(product_key: str):
    """Fetch product information from Gizwits API."""
    url = f"https://euapi.gizwits.com/app/products/{product_key}"
    headers = {
        "X-Gizwits-User-token": TOKEN,
        "X-Gizwits-Application-Id": GIZWITS_APP_ID,
        "Accept": "application/json",
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, timeout=10) as response:
                result = await response.text()
                print(f"\n=== Product Key: {product_key} ===")
                print(f"Status: {response.status}")
                print(f"Response: {result}")
                
                if response.status == 200:
                    data = json.loads(result)
                    return product_key, data
                else:
                    print(f"Failed to fetch product info for {product_key}")
                    return product_key, None
        except Exception as e:
            print(f"Error fetching product {product_key}: {e}")
            return product_key, None

async def main():
    """Main function to fetch all missing models."""
    print("Fetching missing device models from Gizwits API...")
    
    tasks = [fetch_product_info(pk) for pk in MISSING_PRODUCT_KEYS]
    results = await asyncio.gather(*tasks)
    
    for product_key, data in results:
        if data:
            # Save to file
            filename = f"custom_components/jebao_aqua/models/{product_key}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\nSaved model file: {filename}")
        else:
            print(f"\nFailed to fetch model for {product_key}")
    
    print("\nDone!")

if __name__ == "__main__":
    asyncio.run(main())