import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def create_timeline(file_path, scenario_name):
    # Read the Excel file
    df = pd.read_excel(file_path)
    
    # Convert Unix timestamp to datetime
    df['Time'] = pd.to_datetime(df['Time'], unit='s')
    
    # Get start and end times
    start_time = df['Time'].min()
    end_time = df['Time'].max()
    
    # Calculate relative times in seconds
    df['RelativeTime'] = (df['Time'] - start_time).dt.total_seconds()
    scenario_duration = (end_time - start_time).total_seconds()
    
    # Initialize lists to store events
    events = []
    
    # Function to add event
    def add_event(name, start, end=None, color='blue'):
        events.append({'name': name, 'start': start, 'end': end, 'color': color})
    
    # Add start and end times
    add_event('Scenario Start', 0, color='green')
    add_event('Scenario End', scenario_duration, color='red')
    
    # Find radio updates
    radio_updates = df[df['Action'].str.contains('inflight radio update asked', case=False, na=False) or df['Action'].str.contains('transmit button pressed', case=False, na=False)]
    for _, row in radio_updates.iterrows():
        add_event('Radio Update', row['RelativeTime'], color='purple')
    
    # Find vitals prompts
    vitals_prompts = df[df['Action'].str.contains('vitals prompt', case=False, na=False)]
    for _, row in vitals_prompts.iterrows():
        add_event('Vitals Prompt', row['RelativeTime'], color='orange')
    
    # Find emergency events and responses
    emergency_start = df[df['Action'].str.contains('emergency start', case=False, na=False)]
    emergency_end = df[df['Action'].str.contains('emergency end', case=False, na=False)]
    for _, start_row in emergency_start.iterrows():
        end_row = emergency_end[emergency_end['Time'] > start_row['Time']].iloc[0]
        add_event('Emergency', start_row['RelativeTime'], end_row['RelativeTime'], color='yellow')
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(15, 8))
    
    # Plot events
    for event in events:
        if event['end'] is None:
            ax.scatter(event['start'] / 60, 0, color=event['color'], s=100, zorder=5)
            ax.annotate(event['name'], (event['start'] / 60, 0), xytext=(0, 10), 
                        textcoords='offset points', ha='center', va='bottom', rotation=45)
        else:
            ax.plot([event['start'] / 60, event['end'] / 60], [0, 0], color=event['color'], linewidth=10, solid_capstyle='butt')
            ax.annotate(event['name'], (event['start'] / 60, 0), xytext=(0, 10), 
                        textcoords='offset points', ha='left', va='bottom', rotation=45)
    
    # Set up the axis
    ax.set_ylim(-1, 1)
    ax.yaxis.set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Format x-axis
    ax.set_xlabel('Time (minutes)')
    ax.set_xticks(range(0, int(scenario_duration / 60) + 1, 5))
    ax.set_xticklabels([f'{x}:00' for x in range(0, int(scenario_duration / 60) + 1, 5)])
    plt.xticks(rotation=45)
    
    # Add grid lines
    ax.grid(True, axis='x', linestyle='--', alpha=0.7)
    
    # Set title and adjust layout
    plt.title(f'Timeline for {scenario_name}')
    plt.tight_layout()
    
    # Show the plot
    plt.show()


create_timeline('path_to_scenario1_data.xlsx', 'Scenario 1')
create_timeline('path_to_scenario2_data.xlsx', 'Scenario 2')
create_timeline('path_to_scenario3_data.xlsx', 'Scenario 3')