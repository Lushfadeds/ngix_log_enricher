import argparse
import json
import re
import sys
from typing import Any, Dict, Optional
from datetime import datetime
from user_agents import parse as parse_user_agent

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
        
        # Parse time_local into a standard format
        # Keep raw time_local, and add normalized ISO8601 timestamp
        try:
            entry["timestamp"] = datetime.strptime(
                entry["time_local"], "%d/%b/%Y:%H:%M:%S %z"
            ).isoformat()
        except (ValueError, KeyError):
            entry["timestamp"] = None


        return entry

class UserAgentEnricher:
    """Enrich log entries with user agent details."""

    def enrich(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Add user agent details to the log entry."""
        ua_string = entry.get("http_user_agent", "")

        # Treat both "" and "-" as missing
        if not ua_string or ua_string == "-":
            entry.update({
                "ua_browser": None,
                "ua_browser_version": None,
                "ua_os": None,
                "ua_os_version": None,
                "ua_device": None,
                "ua_is_mobile": False,
                "ua_is_tablet": False,
                "ua_is_pc": False,
                "ua_is_bot": False,
            })
            return entry

        # Try parsing a valid UA string
        try:
            user_agent = parse_user_agent(ua_string)
            entry["ua_browser"] = user_agent.browser.family
            entry["ua_browser_version"] = user_agent.browser.version_string
            entry["ua_os"] = user_agent.os.family
            entry["ua_os_version"] = user_agent.os.version_string
            entry["ua_device"] = user_agent.device.family
            entry["ua_is_mobile"] = user_agent.is_mobile
            entry["ua_is_tablet"] = user_agent.is_tablet
            entry["ua_is_pc"] = user_agent.is_pc
            entry["ua_is_bot"] = user_agent.is_bot
        except Exception as e:
            print(f"Warning: Failed to parse User-Agent '{ua_string}': {e}", file=sys.stderr)
            entry.update({
                "ua_browser": None,
                "ua_browser_version": None,
                "ua_os": None,
                "ua_os_version": None,
                "ua_device": None,
                "ua_is_mobile": False,
                "ua_is_tablet": False,
                "ua_is_pc": False,
                "ua_is_bot": False,
            })

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
    records: list[dict[str, Any]] = []

    skipped = 0
    
    # Try to read the input file
    try:
        with open(args.in_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):  # NEW: track line numbers
                entry = log_parser.parse_line(line)
                if entry:
                    records.append(entry)
                else:
                    skipped += 1
                    print(f"Warning: skipped line {line_num}", file=sys.stderr)
    except FileNotFoundError:
        print(f"Error: Input file not found -> {args.in_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error while reading {args.in_path}: {e}", file=sys.stderr)
        sys.exit(1)
    
        
        
    print("--- End of file content ---")
    
    
    
    # enrich parsed records with User-Agent fields
    enricher = UserAgentEnricher()                  
    records = [enricher.enrich(e) for e in records] 
    
    # Try to write to the output file
    try:
        with open(args.out_path, "w", encoding="utf-8") as out:
            json.dump(records, out, indent=2)
    except Exception as e:
        print(f"Error while writing to {args.out_path}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Processed {len(records)} entries, skipped {skipped} invalid lines.")
    print(f"Output written to {args.out_path}")
    

if __name__ == "__main__":
    main()
