import os
import re
from datetime import datetime
import sys

MAGIC = "###"
DNS_TABLE = {}
FILTERED_LOGS = []


def parse_line(line):
    results = {}
    results["timestamp"] = datetime.strptime(line[21:42], '%y-%m-%dT%H:%M:%S.%f')
    results["log"] = line
    return results


def process_line(parsed_line):
    if "log" not in parsed_line:
        raise ValueError("Parsed line doesn't have log")

    if parsed_line["log"].find("my role is") > 0:
        process_intro_log(parsed_line)
    else:
        parsed_line["ips"] = re.findall(r'(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.)(?:\d{1,3})', parsed_line["log"])


def process_intro_log(parsed_line):
    intro_pattern = ".*my role is (?P<hostname>[\w-]+), my IP is (?P<ip>[\d\.]+)"
    matched = re.match(intro_pattern, parsed_line["log"])

    if matched:
        ip = matched.group("ip")
        hostname = matched.group("hostname")
        DNS_TABLE[ip] = hostname
        print("DNS: ", ip, hostname)
    else:
        raise ValueError("{LOG_TYPE_INTRO} is malformed", )


def process_file(filename):
    temp_filename = "zil.log"
    os.system(f'grep \'{MAGIC}\' {filename} > /tmp/{temp_filename}')
    pos = filename.rfind('/')
    host = filename[filename.rfind('/', 0, pos) + 1:pos]
    with open(f"/tmp/{temp_filename}") as file:
        for line in file:
            try:
                parsed_line = parse_line(line.rstrip())
                process_line(parsed_line)
                parsed_line["host"] = host
                FILTERED_LOGS.append(parsed_line)
            except ValueError as err:
                print(err.args)


def process_folder(rootdir):
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            filename = os.path.join(subdir, file)
            print("Processing", filename)
            process_file(filename)

    # Sort based on timestamp
    filtered_sorted = sorted(FILTERED_LOGS, key=lambda x: x["timestamp"])

    for log in filtered_sorted:
        str = log["log"]
        if "ips" in log:
            for ip in log["ips"]:
                if ip in DNS_TABLE:
                    str = str.replace(ip, DNS_TABLE[ip])
        print(log["host"], str)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Please provide the root folder path")
    else:
        process_folder(sys.argv[1])
