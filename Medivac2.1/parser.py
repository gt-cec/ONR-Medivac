import os
import re
import ast

BASE_DIR =  '/Users/sanyadoda/ONR-Medivac/Medivac2.1_logs'   #path/to/participants

# Regex to capture ANY section dict
any_pattern = re.compile(r"ANY:(\{.*\})")

def parse_line(line):
    """Extract page, action, timestamp from ANY field."""
    match = any_pattern.search(line)
    if not match:
        return None
    try:
        data_dict = ast.literal_eval(match.group(1))  # parse into dict
        page_info = data_dict.get("page", {})
        action = page_info.get("action", "")
        page = page_info.get("page", page_info.get("sensor", ""))  # handle page or sensor key
        timestamp = data_dict.get("timestamp", "")
        return page, action, timestamp
    except Exception as e:
        print(f"Parse error: {e} in line {line[:100]}")
        return None

def process_log_file(log_file, output_file):
    with open(log_file, "r") as infile, open(output_file, "w") as outfile:
        outfile.write("page,action,timestamp\n")
        for line in infile:
            parsed = parse_line(line)
            if parsed:
                page, action, timestamp = parsed
                outfile.write(f"{page},{action},{timestamp}\n")

def main():
    for participant_id in os.listdir(BASE_DIR):
        participant_folder = os.path.join(BASE_DIR, participant_id)
        if not os.path.isdir(participant_folder):
            continue

        for log_file in os.listdir(participant_folder):
            if log_file.endswith(".log"):
                log_path = os.path.join(participant_folder, log_file)
                output_path = os.path.join(participant_folder, log_file.replace(".log", "_parsed.csv"))
                process_log_file(log_path, output_path)
                print(f"Processed {log_file} -> {output_path}")

if __name__ == "__main__":
    main()
