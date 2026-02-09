import csv
import os

def analyze_free_dimensions(csv_path):
    """
    Checks if all parcels with free_dimension_id=1 have free_transport=1.
    """
    if not os.path.exists(csv_path):
        print(f"Error: File {csv_path} not found.")
        return

    total_free_dim_1 = 0
    missing_free_transport = []
    
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                free_dim_id = row['free_dimension_id'].strip()
                free_transport = row['free_transport'].strip()
                
                if free_dim_id == '1':
                    total_free_dim_1 += 1
                    if free_transport != '1':
                        missing_free_transport.append({
                            'tracking_nr': row['tracking_nr'].strip(),
                            'username': row['username'].strip(),
                            'free_transport': free_transport
                        })
    except Exception as e:
        print(f"Error reading {csv_path}: {e}")
        return

    print(f"Total parcels with free_dimension_id=1: {total_free_dim_1}")
    
    if missing_free_transport:
        print(f"Found {len(missing_free_transport)} parcels with free_dimension_id=1 BUT free_transport NOT equal to 1.")
        print("\nDiscrepancies:")
        print(f"{'Tracking Nr':<25} | {'Username':<15} | {'Free Transport'}")
        print("-" * 60)
        for d in missing_free_transport[:20]:
            print(f"{d['tracking_nr']:<25} | {d['username']:<15} | {d['free_transport']}")
        
        if len(missing_free_transport) > 20:
            print(f"... and {len(missing_free_transport) - 20} more.")
    else:
        print("Success: All parcels with free_dimension_id=1 have free_transport=1.")

def main():
    base_dir = "/var/www/python/genius-control/source"
    csv_path = os.path.join(base_dir, "parcel_dimension.csv")
    
    print("Checking free_dimension_id alignment...")
    analyze_free_dimensions(csv_path)

if __name__ == "__main__":
    main()
