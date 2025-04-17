import numpy as np
import pandas as pd
import json
import csv
from datetime import datetime
import os
import Neighbourhoods as nh
import flowArcFirstTry as eh
from itertools import product
import numpy as np
import time

def log_data_to_csv(file_path, doctors, start_solution, end_solution, start_temperature, Imax, cooling_rate , min_temperature, completion_time, log_file_path="Log_grid_search.csv"):
    # Aktuelles Datum und Zeit abrufen
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    start_solution = start_solution
    
    # Daten für die CSV-Datei vorbereiten
    data = [now, file_path, doctors, start_solution, end_solution, start_temperature, Imax, cooling_rate, min_temperature, completion_time]
 
    # In die CSV-Datei schreiben oder anhängen
    file_exists = False
    try:
        with open(log_file_path, 'r', newline='') as csvfile:
            file_exists = True
    except FileNotFoundError:
        pass
 
    with open(log_file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["Datum und Zeit", "filePath", "Doktoren", "start_solution", "end_solution", "start_temperature","Imax", "cooling_rate", "min_temperature", "completion_time"])
        writer.writerow(data)
 
    print(f"Daten wurden in '{log_file_path}' gespeichert.")

def grid_search_sa(group_name, hospital, doctors, day, time_limit):
    # Definiere die Wertebereiche für die Parameter
    ## Vorsicht, alle werden in jeder Kombinationsmöglichkeit durchgegangen
    counter = 1
    start_temperatures = [100]
    imax_values = [100, 150, 250, 1000]
    cooling_rates = [0.95, 0.98, 0.99]
    min_temperatures = [0.01]
    sol_overview = []

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
        hosp_only_string = hospital.split('/')[1]
        json_file = f"gruppe_{group_name[-1]}_{hosp_only_string}_{day}.json.json"
        file_path = os.path.join(hospital, group_name, json_file)
        instance = eh.map_patient_data(file_path, doctors)
        start_time_array = np.full(doctors, 0)
        result = eh.opening_heuristic_greedy(instance)
        
        start_time_measurement = time.time()
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
        sol_overview.append((res[1], res[2],(time.time() - start_time_measurement), start_temperature, Imax, cooling_rate, min_temperature))
        log_data_to_csv(f"{hosp_only_string}_{group_name}_{day}", doctors, result[1], res[1],start_temperature=start_temperature, Imax=Imax, cooling_rate=cooling_rate, min_temperature=min_temperature, completion_time=(time.time() - start_time_measurement))
        # csv Schreibfunc hier
        # write to csv: (hospital, group, )

        counter +=1
        print(f"{counter}: {res[1]} mit {res[2]}")

        # Überprüfe die beste Lösung basierend auf der Zielfunktion res[1]
        current_tardiness = sum([sol[1] for sol in sol_list])
        if current_tardiness < lowest_tardiness:
            lowest_tardiness = current_tardiness
            best_solution = sol_list
            best_parameters = (start_temperature, Imax, cooling_rate, min_temperature)
            print(f"Momentane beste Parameter: {best_parameters}")
        

    return best_solution, best_parameters, sol_overview

########################################################################################

# Beispielaufruf
group_name = "group_2"
day = 1
# hospital = "Heuristic/italien"
hospital = "Heuristic/hongkong"
doctors = 2
# Für Tests bezüglich dynamisch
time_limit = 600

best_solution, best_parameters, sol_overview = grid_search_sa(group_name=group_name, hospital=hospital, doctors=doctors, day=day, time_limit=time_limit)
print("-----------------Ergebnisse-----------------")
print(f"Beste Parameter: {best_parameters}")
print(sol_overview)
