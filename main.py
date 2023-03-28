import os
import re

MAGIC = "ARTEM_SAEED"

LOG_TYPE_INTRO = "INTRO"
LOG_TYPE_DNS_TEST = "DNS_TEST"      # For testing this script
DNS_TABLE = {}
FILTERED_LOGS = {}

def parse_line(line):
    line_pattern = "(?:\[[^\]]*\])(?:\[(?P<timestamp>[^\]]*)\])(?:\[[^\]]*\])(?:\[[^\]]*\]) ARTEM_SAEED (?P<log_type>[A-Z_]+) (?P<log>.*)"
    matched = re.match(line_pattern, line)
    
    results = {}
    if matched:
        results["timestamp"] = matched.group("timestamp")
        results["log_type"] = matched.group("log_type")
        results["log"] = matched.group("log")
    else:
        raise ValueError("Line is not parsable", line)
    
    return results

def process_line(parsed_line):
    if "log_type" not in parsed_line:
        raise ValueError("Parsed line doesn't have log_type")

    if "log" not in parsed_line:
        raise ValueError("Parsed line doesn't have log")

    log_type = parsed_line["log_type"]
    if log_type == LOG_TYPE_INTRO:
        process_intro_log(parsed_line)
    elif log_type == LOG_TYPE_DNS_TEST:
        process_dns_test_log(parsed_line)
    else:
        raise ValueError(f"Log type {log_type} is unknown")

def process_intro_log(parsed_line):
    intro_pattern = "my role is (?P<hostname>[\w-]+), my IP is (?P<ip>[\d\.]+)"
    matched = re.match(intro_pattern, parsed_line["log"])
    
    if matched:
        ip = matched.group("ip")
        hostname = matched.group("hostname")
        DNS_TABLE[ip] = hostname
    else:
        raise ValueError("{LOG_TYPE_INTRO} is malformed", )

def process_dns_test_log(parsed_line):
    intro_pattern = "this is for dns test (?P<ip>[\d\.]+)"
    matched = re.match(intro_pattern, parsed_line["log"])
    print(matched.group("ip"))
    ip = matched.group("ip")
    parsed_line["log"] = parsed_line["log"].replace(ip, DNS_TABLE[ip])

def process_file(filename):
    os.system(f'grep {MAGIC} {filename} > /tmp/{filename}')
    with open(f"/tmp/{filename}") as file:
        for line in file:
            try:
                parsed_line = parse_line(line.rstrip())
                process_line(parsed_line)
                FILTERED_LOGS[parsed_line["timestamp"]] = parsed_line["log"]
            except ValueError as err:
                print(err.args)

    print(FILTERED_LOGS)

if __name__ == "__main__":
    process_file("sample.log")