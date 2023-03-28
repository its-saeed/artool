import os
import re
from datetime import datetime

MAGIC = "ARTEM_SAEED"

LOG_TYPE_INTRO = "INTRO"
LOG_TYPE_DNS_TEST = "DNS_TEST"      # For testing this script
LOG_TYPE_DUMMY = "DUMMY"      # For testing this script
DNS_TABLE = {}
FILTERED_LOGS = []

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
    elif log_type == LOG_TYPE_DUMMY:
        process_dummy_log(parsed_line)
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
    log = parsed_line["log"]
    dns_test_pattern = "this is for dns test (?P<ip>[\d\.]+)"
    matched = re.match(dns_test_pattern, parsed_line["log"])
    if matched and "ip" in matched.groupdict():
        translate_ip(parsed_line, matched.group("ip"))
    else:
        raise ValueError(f"DNS test message is not parsable, {log}")

def process_dummy_log(parsed_line):
    #this is a dummy log 33.33.36.37 just for testing
    log = parsed_line["log"]
    dummy_pattern = "this is a dummy log (?P<ip>[\d\.]+) just for testing"
    matched = re.match(dummy_pattern, log)
    if matched and "ip" in matched.groupdict():
        translate_ip(parsed_line, matched.group("ip"))
    else:
        raise ValueError(f"Dummy message is not parsable, {log}")

def translate_ip(parsed_line, extracted_ip):
    if extracted_ip not in DNS_TABLE:
        parsed_line["needs_ip_resolve"] = True # let's try at the end to resolve this ip to address
        parsed_line["extracted_ip"] = extracted_ip # let's try at the end to resolve this ip to address
        print(f"{extracted_ip} is not in the DNS table yet")
    else:
        parsed_line["log"] = parsed_line["log"].replace(extracted_ip, DNS_TABLE[extracted_ip])


def process_file(filename):
    temp_filename = "zil.log"
    os.system(f'grep {MAGIC} {filename} > /tmp/{temp_filename}')
    with open(f"/tmp/{temp_filename}") as file:
        for line in file:
            try:
                parsed_line = parse_line(line.rstrip())
                process_line(parsed_line)
                FILTERED_LOGS.append(parsed_line)
            except ValueError as err:
                print(err.args)

def process_folder(rootdir):
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            filename = os.path.join(subdir, file)
            print("Processing", filename)
            process_file(filename)

    # Last try to resolve IP addresses
    for parsed in FILTERED_LOGS:
        if "needs_ip_resolve" in parsed:
            translate_ip(parsed, parsed["extracted_ip"])
        
    # Sort based on timestamp
    filtered_sorted = sorted(FILTERED_LOGS, key=lambda x: datetime.strptime(x["timestamp"], '%y-%m-%dT%H:%M:%S.%f'))

    for log in filtered_sorted:
        print(log["timestamp"], log["log"])

if __name__ == "__main__":
    process_folder("sample_logs")