import os
import pandas as pd
import numpy as np
from collections import defaultdict

def process_all_xlsx_files(folder_path):
    all_data = []  # List to store data from all folders
    # Emergency response time (for scenario 2 and 3):
    #stage2_data = defaultdict(lambda: defaultdict(list(lambda: defaultdict(lambda: "not found"))))
    stage2_data = defaultdict(lambda: defaultdict(list))
    stage3_data = defaultdict(lambda: defaultdict(list))
    stage4_data = defaultdict(lambda: defaultdict(list))
    

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        
        # Check if the item is a directory/folder
        if os.path.isdir(item_path):
            print(f"Processing folder: {item}")
            # Iterate through all files in the folder
            for file_name in os.listdir(item_path):
                file_path = os.path.join(item_path, file_name)
                # Process only .xlsx files
                if os.path.isfile(file_path) and file_name.endswith('.xlsx'):
                    # Call the function to extract data and extend all_data
                    file_data, file_stage2_data, file_stage3_data,file_stage4_data  = process_excel_file(file_path) # 4 different excel files
                    all_data.extend(file_data)
                    
                    # Merge stage data
                    for user_id, actions in file_stage2_data.items():
                        for action, times in actions.items():
                            stage2_data[user_id][action].extend(times)
                    for user_id, actions in file_stage3_data.items():
                        for action, times in actions.items():
                            stage3_data[user_id][action].extend(times)
                    for user_id, actions in file_stage4_data.items():
                        for action, times in actions.items():
                            if isinstance(times, list):
                                stage4_data[user_id][action].extend(times)
                            else:
                                stage4_data[user_id][action] = times  # It's a float or single value


    # Combine all data into a single dataframe
    final_df = pd.concat(all_data, ignore_index=True)


    # Write to Excel
    output_path = os.path.join(folder_path, 'Interface_Logs_data.xlsx')
    final_df.to_excel(output_path, index=False)
    print(f"Data has been written to {output_path}")

    """   # Create and save Scenario 3 Excel file
    stage3_df = pd.DataFrame(stage3_data).T.reset_index() # transpose to get ID's as rows and reseting index to make ID a normal columnn instead of index
    stage3_df.columns = ['ID'] + list(stage3_df.columns[1:])  #column names (ID and the phrase)
    stage3_output_path = os.path.join(folder_path, 'stage3_data.xlsx')
    stage3_df.to_excel(stage3_output_path, index=False) # index set to false to not get the assigned index(0,1..) 
    print(f"Stage 3 data has been written to {stage3_output_path}") """
    """ 
    # Create and save Stage 2 Excel file
    stage2_df = create_stage_dataframe(stage2_data,2)
    stage2_output_path = os.path.join(folder_path, 'stage2_data.xlsx')
    stage2_df.to_excel(stage2_output_path, index=False)
    print(f"Stage 2 data has been written to {stage2_output_path}")

    # Create and save Stage 3 Excel file
    stage3_df = create_stage_dataframe(stage3_data,3)
    stage3_output_path = os.path.join(folder_path, 'stage3_data.xlsx')
    stage3_df.to_excel(stage3_output_path, index=False)
    print(f"Stage 3 data has been written to {stage3_output_path}") """

    # Create and save Stage 4 Excel file
    stage4_df = create_stage_dataframe(stage4_data,4)
    stage4_output_path = os.path.join(folder_path, 'stage4_data.xlsx')
    stage4_df.to_excel(stage4_output_path, index=False)
    print(f"Stage 4 data has been written to {stage4_output_path}")

def create_stage_dataframe(stage_data, stage_number):
    # Get all unique actions across all users
    all_actions = set()
    for user_actions in stage_data.values():
        all_actions.update(user_actions.keys())
    
    # Create a list of dictionaries for the DataFrame
    data_list = []
    for user_id, user_actions in stage_data.items():
        user_dict = {'ID': user_id, 'First Row Time': user_actions.get('first_row_time', [''])[0]}
        if stage_number == 2:
            user_dict['Vitals State 1 Time'] = user_actions.get('vitals_state_1', [''])[0]
            user_dict['Vitals State 0 Time'] = user_actions.get('vitals_state_0', [''])[0]
        if stage_number == 4:
            user_dict['Vitals State 1 stage4'] = user_actions.get('vitals_state_1_stage4', [''])[0]
            user_dict['Vitals State 0 stage4'] = user_actions.get('vitals_state_0_stage4', [''])[0]
        for action in all_actions:
            if action not in ['first_row_time', 'vitals_state_1', 'vitals_state_0']:
                times = user_actions.get(action, [])
                for i, time in enumerate(times, 1):
                    user_dict[f"{action} - Occurrence {i}"] = time
        data_list.append(user_dict)
    
    # Create DataFrame
    df = pd.DataFrame(data_list)
    
    # Reorder columns to have 'ID' and 'First Row Time' first
    columns = ['ID', 'First Row Time']
    if stage_number == 2:
        columns.extend(['Vitals State 1 Time', 'Vitals State 0 Time'])
    columns.extend([col for col in df.columns if col not in columns])
    df = df[columns]
    
    return df
    

def process_excel_file(file_path):
    # Read the Excel file
    df = pd.read_excel(file_path)
    df = pd.DataFrame(df)

    # Clean column names
    df.columns = df.columns.str.strip()

    stage2_data = defaultdict(lambda: defaultdict(list))
    stage3_data = defaultdict(lambda: defaultdict(list))
    stage4_data = defaultdict(lambda: defaultdict(list))

    try:
        #id = df['ID'].iloc[0]
        first_row_time = df['time'].iloc[0]
    except KeyError:
        print(f"KeyError occurred when trying df['ID'] or df['time'] in file {file_path}")
        return [], stage2_data, stage3_data, stage4_data

    vitals_state_1_time = None
    vitals_state_0_time = None
    pressure_warning_start = None
    pressure_warning_end = None
    engine_failure_start = None
    engine_failure_end = None
    medevac_transmit_time = None
    reroute_oldforth_time = None
    vitals_state_1_stage4 = None
    vitals_state_0_stage4 = None
    scenario = df['Stage'].iloc[0]
    sequence = df['Sequence'].iloc[0]
    i=0

    # Initialize an empty list to store data
    data_list = []
    asked_times = []
    start_times = []
    complete_times = []
    radio_updates_times=[]
    prompt_times = []
    logging_times = []
    submit_times = []
    vitals_logging_times=[]
   

    # Iterate through the rows to look for when radio update asked
    for i, row in df.iterrows():
        # Skip rows where user ID is 0
        if row.get('ID') == 0:
            continue

        id = row.get('ID')
        if 'inflight radio update asked' in str(row['action']).lower().strip() or 'transmit button pressed' in str(row['action']).lower().strip():
            asked_time = row['time']
            asked_times.append(asked_time)

            # Look for start and complete times after radio update asked
            start_time = 'not found'
            complete_time = 'not found'
            radio_updates_time='not found'
            for j, next_row in df.iloc[i+1:].iterrows():
                if ('radio panel opened' in str(next_row['action']).lower() or 'callsign set to' in str(next_row['action']).lower()) and start_time == 'not found':
                    start_time = next_row['time']
                if 'nasxgstransmitting' in str(next_row['action']).lower() or 'nasxgs transmitting' in str(next_row['action']).lower() and complete_time == 'not found':
                    complete_time = next_row['time']
                    radio_updates_time= (complete_time - start_time)*1000
                    break
                if 'inflight radio update asked' in str(row['action']).lower().strip() or 'transmit button pressed' in str(row['action']).lower().strip()  and start_time == 'not found' and complete_time == 'not found':  # missed update or if another radio update asked before completion of  the previous one 
                    break

            start_times.append(start_time)
            complete_times.append(complete_time)
            radio_updates_times.append(radio_updates_time)

        # Iterate through the rows to look for when vitals prompt was displayed
        if 'displaying vitals prompt' in str(row['action']).lower().strip():
            prompt_time = row['time']
            prompt_times.append(prompt_time)

        logging_time = 'not found'
        submit_time = 'not found'
        vitals_logging_time='not found'

        # Iterate through the rows to look for when began and completed logging  (not looking for time after the prompt since some anticipated vitals would come and to include if the ones that were logged at a later time and the other prompt came )
        if i != 0 and 'VitalsTask' in str(row['source']) and 'opened sensor' in str(row['data']).lower() and 'heart rate' in str(row['data']).lower() and logging_time == 'not found':
            logging_time = row['time']
            
            for j, next_row in df.iloc[i+1:].iterrows(): # Look for the time of submit after starting the logging 
                if ('submit succeeded' in str(next_row['data']).lower() and submit_time == 'not found'):
                    submit_time = next_row['time']
                    vitals_logging_time = (submit_time - logging_time) # in s
                    break
                # if 'displaying vitals prompt' in str(row['action']).lower().strip() and logging_time == 'not found' and submit_time == 'not found':  # missed vital or if another vitals prompt showed up before completion of the previous one 
                #     break
            
            logging_times.append(logging_time)
            submit_times.append(submit_time)
            vitals_logging_times.append(vitals_logging_time)

        # Emergency response time (for scenario 2 and 3 and 4):
        log=str(row['action']).strip()
        if scenario == 2:
            stage2_data[id]['first_row_time'].append(first_row_time)
            if 'administer' in log.lower():
                stage2_data[id][log].append(row['time'])
            if vitals_state_1_time is None and row['vitals-state'] == 1:
                vitals_state_1_time = row['time']
                stage2_data[id]['vitals_state_1'].append(vitals_state_1_time)
            if vitals_state_1_time is not None and vitals_state_0_time is None and row['vitals-state'] == 0:
                vitals_state_0_time = row['time']
                stage2_data[id]['vitals_state_0'].append(vitals_state_0_time)
        elif scenario == 3:
            stage3_data[id]['first_row_time'].append(first_row_time)
            if "tank emergency" in log.lower():
                stage3_data[id][log].append(row['time'])
        elif scenario == 4:
            stage4_data[id]['first_row_time'].append(first_row_time)
            log_lower = log.lower()

            # Pressure warning start
            if pressure_warning_start is None and (
                'pressure miscalibrated warning' in log_lower or 
                'pressure warning alert activated' in log_lower): 
                pressure_warning_start = row['time']
                stage4_data[id]['pressure_warning_start'].append(pressure_warning_start)

            # Pressure warning end
            if pressure_warning_end is None and (
                'pressure warning alert close button pressed' in log_lower
            ):  
                pressure_warning_end= row['time']
                stage4_data[id]['pressure_warning_end'].append(pressure_warning_end)

            # Engine failure alert start
            if engine_failure_start is None and (
                'show engine failure alert' in log_lower or
                'engine failure' in log_lower
            ):
                engine_failure_start= row['time']
                stage4_data[id]['engine_failure_start'].append(engine_failure_start)

            # Engine failure alert end
            if engine_failure_end is None and (
                'engine failure emergency- close button pressed' in log_lower
            ):
                engine_failure_end= row['time']
                stage4_data[id]['engine_failure_end'].append(engine_failure_end)

            # MEDEVAC transmitting time after engine failure closed
            if engine_failure_end is not None and medevac_transmit_time is None and (
                'medevactransmitting' in log_lower
            ):
                medevac_transmit_time= row['time']
                stage4_data[id]['medevac_transmit_time'].append(medevac_transmit_time)

            # Reroute to Oldforth time after engine failure closed
            if engine_failure_end is not None and reroute_oldforth_time is None and (
                'reroute to oldforth' in log_lower
            ):
                reroute_oldforth_time= row['time']
                stage4_data[id]['reroute_oldforth_time'].append(reroute_oldforth_time) 
            if vitals_state_1_stage4 is None and row['vitals-state'] == 1.0:
                vitals_state_1_stage4 = row['time']
                stage4_data[id]['vitals_state_1_stage4'].append(vitals_state_1_stage4)
            if vitals_state_1_stage4 is not None and vitals_state_0_stage4 is None and row['vitals-state'] == 0.0:
                vitals_state_0_stage4 = row['time']
                stage4_data[id]['vitals_state_0_stage4'].append(vitals_state_0_stage4)


    # Create a dataframe for the user and scenario
    lists = {
        'ID': id,
        'Scenario': scenario,
        'Sequence': sequence,
        'Asked': asked_times,
        'Started': start_times,
        'Completed': complete_times,
        'UpdateTime': radio_updates_times,
        'VitalsPrompt': prompt_times,
        'StartedLogging': logging_times,
        'Submitted': submit_times,
        'LogTime': vitals_logging_times
    }

    # Function to safely get length or return 1 for scalars
    def safe_len(obj):
        if isinstance(obj, (list, np.ndarray, pd.Series)):
            return len(obj)
        return 1  # Return 1 for scalar values

    # Find the maximum length of all lists
    max_length = max(safe_len(lst) for lst in lists.values())

    # Function to safely get item or return the item itself for scalars
    def safe_get(obj, index):
        if isinstance(obj, (list, np.ndarray, pd.Series)):
            return obj[index] if index < len(obj) else None
        return obj  # Return the item itself if it's a scalar

    # Iterate through the range of the longest list
    for i in range(max_length):
        row = {}
        for key, value in lists.items():
            row[key] = safe_get(value, i)
        data_list.append(row)

    # Create the DataFrame from the list of dictionaries
    user_data = pd.DataFrame(data_list)

    return [user_data],stage2_data, stage3_data, stage4_data

if __name__ == "__main__":
    folder_path = '/Users/sanyadoda/ONR-Medivac/Server/UserStudyLogs'
    process_all_xlsx_files(folder_path)