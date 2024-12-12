import pandas as pd
import numpy as np
import openpyxl

def save_large_dataframe_to_excel(df, file_name, rows_per_sheet=1000000):
    with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
        for i in range(0, len(df), rows_per_sheet):
            # Write data to separate sheets for every chunk of `rows_per_sheet`
            df.iloc[i:i + rows_per_sheet].to_excel(writer, sheet_name=f'Sheet_{i // rows_per_sheet + 1}', index=False)

def load_distance(file):
    data = pd.read_excel(file)
    print("Loading distances data from " + file)
    # save_large_dataframe_to_excel(data, 'output_large.xlsx')

    nodes = sorted(set(data['from_node']).union(set(data['to_node'])))
    node_count = len(nodes)

    node_to_idx = {node: idx for idx, node in enumerate(nodes)}

    distance_matrix = np.zeros((node_count, node_count))
    time_matrix = np.zeros((node_count, node_count))

    np.fill_diagonal(distance_matrix, 0)

    count = 0
    for _, row in data.iterrows():
        from_idx = node_to_idx[row['from_node']]
        to_idx = node_to_idx[row['to_node']]
        distance_matrix[from_idx, to_idx] = row['distance']
        distance_matrix[to_idx, from_idx] = row['distance']
        time_matrix[from_idx, to_idx] = row['spend_tm']
        time_matrix[to_idx, from_idx] = row['spend_tm']
        count += 1
        if count == node_count:
            count = 0

    for i in range(node_count):
        distance_matrix[i, i] = np.finfo(float).eps
        time_matrix[i, i] = np.finfo(float).eps

    return distance_matrix, time_matrix

def load_location(file1, file2):
    """
    time_windows[(ID, start, end)]
    time_windows[0] = (0, 0, 0)
    package[(ID, weight, volume)]
    packages[0] = (0, 0, 0)
    """
    data1 = pd.read_excel(file1)
    data2 = pd.read_excel(file2)
    data = pd.concat([data1, data2], ignore_index=True)
    location = data[['ID', 'type', 'lng', 'lat']]

    time_windows = data[['ID', 'first_receive_tm', 'last_receive_tm']]
    packages = data[['ID', 'pack_total_weight', 'pack_total_volume']]
    
    return location, time_windows, packages


def load_vehicle(file):
    df = pd.read_csv(file)
    return df