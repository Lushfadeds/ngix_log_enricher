import argparse
import json
import sys
def main():
    parser = argparse.ArgumentParser(description="Nginx log parser and data enricher")
    parser.add_argument("--in", dest="in_path", required=True, help="Input Nginx log file")
    parser.add_argument("--out", dest="out_path", required=True, help="Output JSON file")
    args = parser.parse_args()

    print(f"Reading from {args.in_path}")
    print(f"Will write to {args.out_path}")
    
    # Read lines into a list of dicts
    records = []
    # Try to read the input file
    try:
        with open(args.in_path, "r", encoding="utf-8") as f:
            for line in f:
                records.append({"raw_line": line.strip()})
    except FileNotFoundError:
        print(f"Error: Input file not found -> {args.in_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error while reading {args.in_path}: {e}", file=sys.stderr)
        sys.exit(1)

    print("--- End of file content ---")
    
    # Try to write to the output file
    try:
        with open(args.out_path, "w", encoding="utf-8") as out:
            json.dump(records, out, indent=2)
    except Exception as e:
        print(f"Error while writing to {args.out_path}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Processed {len(records)} lines")
    print(f"Output written to {args.out_path}")
    

if __name__ == "__main__":
    main()
