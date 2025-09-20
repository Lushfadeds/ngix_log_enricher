import argparse

def main():
    parser = argparse.ArgumentParser(description="Nginx log parser and data enricher")
    parser.add_argument("--in", dest="in_path", required=True, help="Input Nginx log file")
    parser.add_argument("--out", dest="out_path", required=True, help="Output JSON file")
    args = parser.parse_args()

    print(f"Reading from {args.in_path}")
    print(f"Will write to {args.out_path}")
    with open(args.in_path, "r", encoding="utf-8") as f:
        for line in f:
            print(line.strip())

    print("--- End of file content ---")

if __name__ == "__main__":
    main()
