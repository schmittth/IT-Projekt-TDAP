import numpy as np
import pandas as pd
import json
import os
import Neighbourhoods as nh
import flowArcFirstTry as eh
from itertools import product
import numpy as np

# file_path = 'Heuristic\hongkong\group_3\gruppe_3_hongkong_1.json.json'
# doctors = 9
# instance = eh.map_patient_data(file_path, doctors)
# start_time_array = np.full(doctors, 0)



def grid_search_sa(group_name, hospital, doctors, time_limit):
    # Definiere die Wertebereiche für die Parameter
    counter = 1
    start_temperatures = [100]
    imax_values = [150, 250, 1000]
    cooling_rates = [0.95, 0.98, 0.99]
    min_temperatures = [0.01]

    # Alle Parameterkombinationen erstellen
    parameter_combinations = list(product(start_temperatures, imax_values, cooling_rates, min_temperatures))
    print(len(parameter_combinations))

    best_solution = None
    best_parameters = None
    lowest_tardiness = float('inf')  # Initialisiere mit einem sehr hohen Wert

    # Iteriere über alle Kombinationen
    for start_temperature, Imax, cooling_rate, min_temperature in parameter_combinations:
        sol_list = []

        # Führe den Prozess für jede Parameterkombination aus
        # for json_file in os.listdir(os.path.join(hospital, group_name)):
        #     if json_file.endswith('.json'):
        json_file = f"gruppe_{group_name[-1]}_hongkong_1.json.json"
        file_path = os.path.join(hospital, group_name, json_file)
        instance = eh.map_patient_data(file_path, doctors)
        start_time_array = np.full(doctors, 0)
        result = eh.opening_heuristic_greedy(instance)
                
        res = nh.simulated_annealing(
                    schedule=result[0],
                    total_tardiness=result[1],
                    start_time_array=start_time_array,
                    Imax=Imax,
                    cooling_rate=cooling_rate,
                    min_temperature=min_temperature,
                    start_temperature=start_temperature,
                    time_limit=time_limit,
                    Max_d=12000,
                    deterministic=True
                )

        sol_list.append(("instanz", res[1], res[2]))
        counter +=1
        print(f"{counter}: {res[1]} mit {res[2]}")

        # Überprüfe die beste Lösung basierend auf der Zielfunktion res[1]
        current_tardiness = sum([sol[1] for sol in sol_list])
        if current_tardiness < lowest_tardiness:
            lowest_tardiness = current_tardiness
            best_solution = sol_list
            best_parameters = (start_temperature, Imax, cooling_rate, min_temperature)
            print(f"Momentane beste Parameter: {best_parameters}")
        

    return best_solution, best_parameters

# Beispielaufruf
print("ARLAAARM")
best_solution, best_parameters = grid_search_sa(group_name='group_4', hospital='Heuristic/hongkong', doctors=2, time_limit=300)
print(f"Beste Parameter: {best_parameters}")

# process_json_files_in_group_sa("group_1", "italien", 7, 50, 300)