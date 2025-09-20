import argparse
import json

def main():
    parser = argparse.ArgumentParser(description="Nginx log parser and data enricher")
    parser.add_argument("--in", dest="in_path", required=True, help="Input Nginx log file")
    parser.add_argument("--out", dest="out_path", required=True, help="Output JSON file")
    args = parser.parse_args()

    print(f"Reading from {args.in_path}")
    print(f"Will write to {args.out_path}")
    
    # Read lines into a list of dicts
    records = []
    with open(args.in_path, "r", encoding="utf-8") as f:
        for line in f:
            records.append({"raw_line": line.strip()})

    print("--- End of file content ---")
    
    # Write records to output file in JSON format
    with open(args.out_path, "w", encoding="utf-8") as out:
        json.dump(records, out, indent=2)

    print(f"Processed {len(records)} lines")
    print(f"Output written to {args.out_path}")
    

if __name__ == "__main__":
    main()
