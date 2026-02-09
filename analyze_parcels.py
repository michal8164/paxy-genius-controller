import csv
import os
import glob

def load_exceptions(no_genius_dir):
    """Loads tracking numbers from all CSV files in the no_genius directory."""
    exceptions = set()
    csv_files = glob.glob(os.path.join(no_genius_dir, "*.csv"))
    
    for file_path in csv_files:
        try:
            with open(file_path, mode='r', encoding='utf-8') as f:
                # Some files might have headers, others might not. 
                # After inspection, they seems to have 'nr' or just numbers.
                # Let's handle both.
                reader = csv.reader(f)
                header = next(reader, None)
                if header and header[0].strip().lower() != 'nr':
                    # It was not a header but data
                    exceptions.add(header[0].strip())
                
                for row in reader:
                    if row:
                        exceptions.add(row[0].strip())
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            
    return exceptions

def load_emag_clubs(csv_path):
    """Loads tracking numbers from emag_clubs_01.csv where second column is '1'."""
    emag_clubs = set()
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                if len(row) >= 2 and row[1].strip() == '1':
                    emag_clubs.add(row[0].strip())
    except Exception as e:
        print(f"Warning: Could not read {csv_path}: {e}")
    return emag_clubs

def analyze_parcels(csv_path, exceptions, emag_clubs):
    """Analyzes parcels in the given CSV file under specified conditions."""
    discrepancies = []
    total_count = 0
    free_should_be_count = 0
    
    # Conditions:
    # ( (carrier_id in [24, 41, 49] AND type == "point" AND weight <= 20) OR trackingNr in emag_clubs )
    # AND NOT trackingNr in exceptions (no_genius)
    
    carrier_ids = {'24', '41', '49'}
    
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_count += 1
                
                tracking_nr = row['tracking_nr'].strip()
                carrier_id = row['carrier_id'].strip()
                p_type = row['type'].strip()
                try:
                    weight = float(row['weight'].strip())
                except (ValueError, TypeError):
                    weight = 0.0
                
                actual_free = row['free_transport'].strip()
                
                # Check base eligibility
                is_eligible_paxy = (
                    carrier_id in carrier_ids and
                    p_type == "point" and
                    weight <= 20
                )
                
                is_emag_club = tracking_nr in emag_clubs
                is_exception = tracking_nr in exceptions
                
                # Refined logic: ((Base or eMag) AND NOT Exception)
                should_be_free = "1" if ((is_eligible_paxy or is_emag_club) and not is_exception) else "0"
                
                if actual_free != should_be_free:
                    discrepancies.append({
                        'tracking_nr': tracking_nr,
                        'carrier_id': carrier_id,
                        'type': p_type,
                        'weight': weight,
                        'actual': actual_free,
                        'expected': should_be_free,
                        'is_exception': is_exception,
                        'is_emag_club': is_emag_club
                    })
                
                if should_be_free == "1":
                    free_should_be_count += 1
                    
    except Exception as e:
        print(f"Error reading {csv_path}: {e}")
        return None
        
    return {
        'total_analyzed': total_count,
        'free_should_be': free_should_be_count,
        'discrepancies': discrepancies
    }

def main():
    base_dir = "/var/www/python/genius-control/source"
    csv_path = os.path.join(base_dir, "parcel_dimension.csv")
    no_genius_dir = os.path.join(base_dir, "no_genius")
    emag_clubs_path = os.path.join(base_dir, "emag_clubs_01.csv")
    
    print("Loading data...")
    exceptions = load_exceptions(no_genius_dir)
    print(f"Loaded {len(exceptions)} unique tracking numbers as exceptions.")
    
    emag_clubs = load_emag_clubs(emag_clubs_path)
    print(f"Loaded {len(emag_clubs)} tracking numbers from eMag Club list.")
    
    print("Analyzing parcels...")
    result = analyze_parcels(csv_path, exceptions, emag_clubs)
    
    if result:
        print("\nAnalysis Summary:")
        print(f"Total parcels analyzed: {result['total_analyzed']}")
        print(f"Parcels that should be free: {result['free_should_be']}")
        print(f"Discrepancies found: {len(result['discrepancies'])}")
        
        if result['discrepancies']:
            print("\nFirst 20 discrepancies:")
            headers = f"{'Tracking Nr':<25} | {'Act':<3} | {'Exp':<3} | {'Exc':<5} | {'Club':<5}"
            print(headers)
            print("-" * len(headers))
            for d in result['discrepancies'][:20]:
                print(f"{d['tracking_nr']:<25} | {d['actual']:<3} | {d['expected']:<3} | {str(d['is_exception']):<5} | {str(d['is_emag_club']):<5}")

                
if __name__ == "__main__":
    main()
