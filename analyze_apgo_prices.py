import csv
import os
from collections import defaultdict

def analyze_apgo_prices(csv_path):
    """
    Analyzes prices for username 'Apgo' in the given CSV file.
    Groups by (weight, carrier_id, type, free_transport) and checks for price deviations.
    """
    if not os.path.exists(csv_path):
        print(f"Error: File {csv_path} not found.")
        return

    # Dictionary to store prices for each group
    # Key: (weight, carrier_id, type, free_transport)
    # Value: list of dictionaries containing price and tracking_nr
    price_groups = defaultdict(list)

    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['username'].strip() != 'Apgo':
                    continue

                try:
                    weight = float(row['weight'].strip())
                except (ValueError, TypeError):
                    weight = 0.0
                
                carrier_id = row['carrier_id'].strip()
                p_type = row['type'].strip()
                free_transport = row['free_transport'].strip()
                price = row['price'].strip()
                tracking_nr = row['tracking_nr'].strip()
                dimension_id = row['dimension_id'].strip()

                # Grouping key
                key = (weight, carrier_id, p_type, free_transport)
                
                price_groups[key].append({
                    'price': price,
                    'tracking_nr': tracking_nr,
                    'dimension_id': dimension_id
                })

    except Exception as e:
        print(f"Error reading {csv_path}: {e}")
        return

    deviations_found = False
    
    print(f"{'Weight':<10} | {'Carrier':<8} | {'Type':<10} | {'Free':<5} | {'Prices found'}")
    print("-" * 65)

    for key, items in price_groups.items():
        unique_prices = set(item['price'] for item in items)
        
        if len(unique_prices) > 1:
            deviations_found = True
            weight, carrier_id, p_type, free_transport = key
            
            # Print the group header
            print(f"{weight:<10} | {carrier_id:<8} | {p_type:<10} | {free_transport:<5} | {', '.join(sorted(list(unique_prices)))}")
            
            # Print details for each price
            price_details = defaultdict(list)
            for item in items:
                price_details[item['price']].append(item)
            
            for pr, details in price_details.items():
                print(f"  Price: {pr} ({len(details)} parcels)")
                # Show first 3 tracking numbers as examples
                examples = [d['tracking_nr'] for d in details[:3]]
                dimensions = set(d['dimension_id'] for d in details)
                print(f"    Dimensions: {', '.join(dimensions)}")
                print(f"    Examples: {', '.join(examples)}")
            print()

    if not deviations_found:
        print("No price deviations found for user 'Apgo' based on the specified criteria.")

def main():
    base_dir = "/var/www/python/genius-control/source"
    csv_path = os.path.join(base_dir, "parcel_dimension.csv")
    
    print("Starting price analysis for user 'Apgo'...")
    analyze_apgo_prices(csv_path)

if __name__ == "__main__":
    main()
