import argparse
import json
import re
import sys
from typing import Any, Dict, Optional

class NginxLogParser:
    """Parser for Nginx access logs in combined format."""

    def __init__(self):
        # Regex for Nginx combined log format
        self.log_pattern = re.compile(
            r'(?P<remote_addr>\S+) - (?P<remote_user>\S+) \[(?P<time_local>[^\]]+)\] '
            r'"(?P<request>[^"]*)" (?P<status>\d+) (?P<body_bytes_sent>\S+) '
            r'"(?P<http_referer>[^"]*)" "(?P<http_user_agent>[^"]*)"'
        )

    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single log line into a dictionary of fields."""
        line = line.strip()
        if not line:
            return None

        match = self.log_pattern.match(line)
        if not match:
            return None

        entry = match.groupdict()

        # Convert status to int
        try:
            entry["status"] = int(entry["status"])
        except (ValueError, KeyError):
            entry["status"] = 0

        # Convert body_bytes_sent to int (handle "-" as 0)
        try:
            bytes_sent = entry.get("body_bytes_sent", "0")
            entry["body_bytes_sent"] = int(bytes_sent) if bytes_sent != "-" else 0
        except ValueError:
            entry["body_bytes_sent"] = 0
            
        # Split request into method, path, protocol
        request_parts = entry.get("request", "").split(" ")
        if len(request_parts) == 3:
            entry["method"], entry["path"], entry["protocol"] = request_parts
        else:
            entry["method"], entry["path"], entry["protocol"] = "", "", ""

        return entry

def main():
    parser = argparse.ArgumentParser(description="Nginx log parser and data enricher")
    parser.add_argument("--in", dest="in_path", required=True, help="Input Nginx log file")
    parser.add_argument("--out", dest="out_path", required=True, help="Output JSON file")
    args = parser.parse_args()

    print(f"Reading from {args.in_path}")
    print(f"Will write to {args.out_path}")
    
    # Read lines into a list of dicts
    log_parser = NginxLogParser()
    records = []
    # Try to read the input file
    try:
        with open(args.in_path, "r", encoding="utf-8") as f:
            for line in f:
                entry = log_parser.parse_line(line)
                if entry:
                    records.append(entry)
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
