import os
import re

MAGIC = "ARTEM_SAEED"

LOG_TYPE_INTRO = "INTRO"

def parse_line(line):
    line_pattern = "(?:\[[^\]]*\])(?:\[(?P<timestamp>[^\]]*)\])(?:\[[^\]]*\])(?:\[[^\]]*\]) ARTEM_SAEED (?P<log_type>[A-Z]+) (?P<log>.*)"
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

    log_type = parsed_line["log_type"]
    if log_type == LOG_TYPE_INTRO:
        process_intro(parsed_line)
    else:
        raise ValueError(f"Log type {log_type} is unknown")

def process_intro(parsed_line):
    print(parsed_line["log"])

def process_file(filename):
    os.system(f'grep {MAGIC} {filename} > /tmp/{filename}')
    parsed = []
    with open(f"/tmp/{filename}") as file:
        for line in file:
            try:
                parsed_line = parse_line(line.rstrip())
                process_line(parsed_line)
            except ValueError as err:
                print(err.args)


if __name__ == "__main__":
    process_file("sample.log")