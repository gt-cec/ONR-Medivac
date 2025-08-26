import os
import re
import ast
import csv
from collections import defaultdict

BASE_DIR =  '/Users/sanyadoda/ONR-Medivac/Medivac2.1/Logs'   #path/to/participants_logs

any_pattern = re.compile(r"ANY:(\{.*\})")

def parse_line(line):
    """Extract dictionary from ANY field."""
    match = any_pattern.search(line)
    if not match:
        return None
    try:
        return ast.literal_eval(match.group(1))
    except Exception as e:
        print(f"Parse error: {e} in line {line[:100]}")
        return None

def process_log_file(log_file, participant_id, stage, summary_data, detailed_rows):
    current_vital = None

    with open(log_file, "r") as infile:
        for line in infile:
            data_dict = parse_line(line)
            if not data_dict:
                continue

            page_info = data_dict.get("page", {})
            timestamp = data_dict.get("timestamp", "")
            action = page_info.get("action", "")

            # --- Vitals episode tracking ---
            # New vital prompt
            if "log vitals prompted" in action:
                # Close previous if left open
                if current_vital:
                    summary_data[(participant_id, stage)]["prompts"] += 1
                    if current_vital.get("submitted"):
                        summary_data[(participant_id, stage)]["submits"] += 1
                    current_vital = None

                current_vital = {
                    "prompt": action,
                    "prompt_time": timestamp,
                    "submitted": "",
                    "sensor_actions": []
                }
                summary_data[(participant_id, stage)]["prompts"] += 1

            # If in a vital block
            if current_vital:
                if "sensor" in page_info:
                    current_vital["sensor_actions"].append({
                        "sensor": page_info.get("sensor", ""),
                        "action": page_info.get("action", ""),
                        "value": page_info.get("value", ""),
                        "timestamp": timestamp
                    })
                if action == "submit":
                    current_vital["submitted"] = timestamp
                    summary_data[(participant_id, stage)]["submits"] += 1
                    # Add detailed rows
                    for sensor in current_vital["sensor_actions"]:
                        detailed_rows.append([
                            participant_id, stage,
                            current_vital["prompt"],
                            current_vital["prompt_time"],
                            sensor["sensor"],
                            sensor["action"],
                            sensor["value"],
                            sensor["timestamp"],
                            current_vital["submitted"]
                        ])
                    current_vital = None

def main():
    summary_data = defaultdict(lambda: {"prompts": 0, "submits": 0})
    detailed_rows = []

    for participant_id in os.listdir(BASE_DIR):
        participant_folder = os.path.join(BASE_DIR, participant_id)
        if not os.path.isdir(participant_folder):
            continue

        for log_file in os.listdir(participant_folder):
            if log_file.endswith(".log"):
                # Extract stage from filename or inside logs
                stage = None
                with open(os.path.join(participant_folder, log_file)) as f:
                    for line in f:
                        if "STAGE:" in line:
                            stage = line.split("STAGE:")[1].split(",")[0]
                            break
                if not stage:
                    stage = "unknown"

                process_log_file(
                    os.path.join(participant_folder, log_file),
                    participant_id,
                    stage,
                    summary_data,
                    detailed_rows
                )

    # --- Write summary file ---
    with open(os.path.join(BASE_DIR, "all_vitals_summary.csv"), "w", newline="") as sfile:
        swriter = csv.writer(sfile)
        swriter.writerow(["ID", "Scenario", "VitalPrompts", "SubmittedCount"])
        for (pid, stage), counts in summary_data.items():
            swriter.writerow([pid, stage, counts["prompts"], counts["submits"]])

    # --- Write detailed file ---
    with open(os.path.join(BASE_DIR, "all_vitals_detailed.csv"), "w", newline="") as dfile:
        dwriter = csv.writer(dfile)
        dwriter.writerow([
            "ID", "Scenario", "VitalPrompt", "PromptTimestamp",
            "Sensor", "Action", "Value", "SensorTimestamp", "Submitted"
        ])
        dwriter.writerows(detailed_rows)

    print("✅ Combined vitals files created at:")
    print("  - all_vitals_summary.csv")
    print("  - all_vitals_detailed.csv")

if __name__ == "__main__":
    main()
