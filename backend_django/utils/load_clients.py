from evrptw.models import Client
from utils.utils_loaddata import load_location
from django.http import HttpResponseBadRequest

def load_initial_clients():
    if Client.objects.exists():
        print("Data already loaded. Skipping initial load.")
        return

    print("Loading initial client data...")
    try:
        locations, time_windows, packages = load_location(
            '~/EVRPTW_website/backend_django/data/input_node.xlsx',
            '~/EVRPTW_website/backend_django/data/m.xlsx')
    except Exception as e:
        print(f"Error loading data files: {e}")
        return HttpResponseBadRequest("Error loading data files")
    time_windows_all = time_windows.set_index('ID')[['first_receive_tm', 'last_receive_tm']].apply(tuple, axis=1).to_dict()
    packages_all = packages.set_index('ID')[['pack_total_weight', 'pack_total_volume']].apply(tuple, axis=1).to_dict()
    id_to_location = {row['ID']: (row['lat'], row['lng']) for _, row in locations.iterrows()}

    entries = []
    entries.append(
            Client(
                node_id = 0,
                is_depot=True,
                is_charger=False,
                package_weight=0,
                package_volume=0,
                location_lat=id_to_location[0][0],
                location_lng=id_to_location[0][1],
                timewindow_start=0,
                timewindow_end=960,
                serve_time=30,
                cluster_id=0,
            ))
    for i in range(1, 1001):  # Generating 1101 entries
        entries.append(
            Client(
                node_id = i,
                is_depot=False,
                is_charger=False,
                package_weight=packages_all[i][0],
                package_volume=packages_all[i][1],
                location_lat=id_to_location[i][0],
                location_lng=id_to_location[i][1],
                timewindow_start=time_windows_all[i][0],
                timewindow_end=time_windows_all[i][1],
                serve_time=30,
                cluster_id=0,
            ))

    for i in range(1001, 1101):  # Generating 1101 entries
        entries.append(
            Client(
                node_id = i,
                is_depot=False,
                is_charger=True,
                package_weight=0,
                package_volume=0,
                location_lat=id_to_location[i][0],
                location_lng=id_to_location[i][1],
                timewindow_start=0,
                timewindow_end=960,
                serve_time=30,
                cluster_id=0,
            ))
    
    Client.objects.bulk_create(entries)
    print(f"{len(entries)} clients successfully loaded.")