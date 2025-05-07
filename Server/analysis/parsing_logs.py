    #!/usr/bin/env python3


import pandas as pd
import os
import json
import re # regular expression library 
import ast #to solve the double quotes issue


def parse_log_and_convert_to_excel(log_file_path):

    # Check if the corresponding Excel file already exists
    file_name = os.path.splitext(os.path.basename(log_file_path))[0]
    excel_file_path = os.path.join(os.path.dirname(log_file_path), f"{file_name}_parsed.xlsx")
    
    #skip the log file if the corresponding excel file already exists (done so that only the new log files are processed)
    if os.path.exists(excel_file_path):
        print(f"Excel file already exists for {log_file_path}. Skipping processing.")
        return

    # Read data from the .log file
    with open(log_file_path, 'r') as log_file:
        records = []
        inflight_line = None  


        for line in log_file: 
            if line.startswith("INFO:root:"):
                match = re.search(r'ID:(\d+),STAGE:(\d+),SEQUENCE:(\d+),DATA:(\{.*?\}\})', line) #searching tag wise for specific groups/digits using re.search. \{.*?\}\} used for finding the json data which has 2 }} at end 
                if match:
                    record = {'ID': match.group(1), 'Stage': match.group(2), 'Sequence': match.group(3)}
                    Jdata = ast.literal_eval(match.group(4)) #using this function instead of json.loads since the log file has single quotes and not double
                    

                    # Create a DataFrame for Json data
                    data = pd.DataFrame(Jdata)

                    #slitting the data based on source and utilizing the update function to get update the different values and keys in 'data'
                    if data['source'].iloc[0] == 'HAI Interface':
                        pageData = data.get('data', {}).get('page', "Radio Panel") 
                        record.update({  # filling the other columns when page is radio panel
                            'time': data['time'].iloc[0],   
                            'source': data['source'].iloc[0],
                            'destination-index': data['destination-index'].iloc[0],
                            'study-stage': data['study-stage'].iloc[0],
                            'decision-state': data['decision-state'].iloc[0],
                            'vitals-state': data['vitals-state'].iloc[0],
                            'airspace-state': data['airspace-state'].iloc[0],
                            'page':pageData,
                            'action': data['data']['action']
                        })
                    elif data['source'].iloc[0] == 'VitalsTask':
                        record.update({
                            'time': data['time'].iloc[0],
                            'source': data['source'].iloc[0],
                            'timer': data['timer'].iloc[0],
                            'data': data['data']
                        })

                    records.append(record)
                else:
                    action=line.split("INFO:root:")[1].strip()
                    if "simconnect" not in action.lower():
                        inflight_line=action
                    #print(inflight_line)
                    continue  # Skip to the next line
   
            if inflight_line:
                # log line following radio update to get time
                match = re.search(r'ID:(\d+),STAGE:(\d+),SEQUENCE:(\d+),DATA:(\{.*?\}\})', line) #searching tag wise for specific groups/digits using re.search. \{.*?\}\} used for finding the json data which has 2 }} at end 
                if match:
                    record = {'ID': match.group(1), 'Stage': match.group(2), 'Sequence': match.group(3)}
                    Jdata = ast.literal_eval(match.group(4)) 
        
                    record.update({
                        'time': data['time'].iloc[0],
                        'source': data['source'].iloc[0],
                        'page':"Inflight",
                        'action': inflight_line
                    }) 
                    records.append(record)
                inflight_line = None  # Reset the inflight_line flag
        
        # Check if there's any data to process
        if not records:
            print(f"The log file {log_file_path} is empty. No Excel file will be created.")
            return


        # Create a DataFrame for parsed data
        df = pd.DataFrame(records)

        # Extract the log file name without extension
        file_name = os.path.splitext(os.path.basename(log_file_path))[0]

        # Save the DataFrame to an Excel file with the same name as the log file
        excel_file_path = os.path.join(os.path.dirname(log_file_path), f"{file_name}_parsed.xlsx")
        df.to_excel(excel_file_path, index=False) #(don't want row index number and so setting index to false)


def process_all_log_files(folder_path):
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        
        # Check if the item is a directory/folder
        if os.path.isdir(item_path):
            print(f"Processing folder: {item}")  

            # Iterate through all files in the folder
            for file_name in os.listdir(item_path):
                file_path = os.path.join(item_path, file_name)

                # Process only .log files
                if os.path.isfile(file_path) and file_name.endswith('.log'):
                    # Call the function to parse and convert
                    parse_log_and_convert_to_excel(file_path)



if __name__ == "__main__":
    # Specify the path to the .log file and the desired Excel file
    # log_file_path = "/Users/sanyadoda/ONR-HAI/Server/100_1_1234.log"
    # excel_file_path = "/Users/sanyadoda/ONR-HAI/Server/100_1_1234.xlsx"

    # Specify the folder containing the log files
    folder_path = '/Users/sanyadoda/ONR-Medivac/Server/UserStudyLogs'

    # Process all log files in the specified folder
    process_all_log_files(folder_path)

    print("Parsing completed. Excel files saved")

    