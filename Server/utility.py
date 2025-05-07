import datetime
from pathlib import Path
import re


def clean(s):
    return re.sub(r'[^A-Za-z0-9]+', '', s)

# writes data to a log file
def log(data, study_participant_id, study_stage, sequence):
    page = data.get("page")
    action = data.get("action")
    timestamp = data.get("timestamp")

    # Folder path: logs/YYYY-MM-DD_PARTICIPANT_ID/
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    folder_path = Path(f"logs/{today_str}_{study_participant_id}")
    folder_path.mkdir(parents=True, exist_ok=True)

    # Log file based on study stage
    log_file = folder_path / f"{study_stage}.log"

    # Format log entry
    log_string = (
        f"{datetime.datetime.now().timestamp()},ID:{study_participant_id},"
        f"STAGE:{study_stage},SEQUENCE:{sequence},"
        f"DATA:{{'page':'{page}','action':'{action}','timestamp':{timestamp}}},"
        f"ANY:{data}"
    )
    # Write to log file (append)
    with log_file.open("a+") as f:
        f.write(log_string + "\n")
    return {"status": "success", "logged": log_string}, 200