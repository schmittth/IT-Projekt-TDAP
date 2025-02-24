import numpy as np
from copy import deepcopy
from itertools import combinations


def calculate_start_and_endtimes_per_doc(schedule, key):
    for i in range(len(schedule[key])):
        if i == 0:
            schedule[key][0, [4]] = schedule[key][0, [1]] + schedule[key][0, [2]]
            schedule[key][0, [3]] = schedule[key][0, [1]]
        else:
            schedule[key][i, [3]] = max(schedule[key][i-1, [4]], schedule[key][i, [1]])
            schedule[key][i, [4]] = schedule[key][i, [3]] + schedule[key][i, [2]]
    
    # Berechne das Maximum aus 0 und der Differenz der 4. und 6. Spalte
    result = np.maximum(0, schedule[key][:, 3] - schedule[key][:, 5])

    # Weisen Sie das Ergebnis der 7. Spalte zu
    schedule[key][:, 6] = result    

def weighted_tardiness_per_doc(schedule, key):
    # Wähle die Spalten 7 und 8 (Index 6 und 7) aus
    Tardiness = schedule[key][:, 6]
    weight = schedule[key][:, 7]

    # Multipliziere die beiden Spalten elementweise und summiere die Ergebnisse
    return np.sum(Tardiness * weight)

def swap_patients_by_doc_N1(schedule, key, patient_1, patient_2, Max_d):
    temp_schedule = deepcopy(schedule)
    temp_schedule[key][[patient_1, patient_2]] = temp_schedule[key][[patient_2, patient_1]]
    calculate_start_and_endtimes_per_doc(schedule=temp_schedule, key=key)

    # Prüfen, ob beide Bedingungen erfüllt sind
    if feasibility_check(temp_schedule, key, patient_1, Max_d=Max_d) and feasibility_check(temp_schedule, key, patient_2, Max_d=Max_d):
        return temp_schedule  # Neues Schedule zurückgeben, wenn beide Bedingungen erfüllt sind
    else:
        return schedule  # Ursprüngliches Schedule zurückgeben, wenn eine Bedingung nicht erfüllt ist

def insert_patient_by_doc_N2(schedule, key, insert_patient_id, in_front_of_patient_id, Max_d):
    temp_schedule = deepcopy(schedule)
    
    # Bestimme die Indizes des zu verschiebenden und des Zielpatienten basierend auf dem Wert in der ersten Spalte
    insert_index = np.where(temp_schedule[key][:, 0] == insert_patient_id)[0][0]
    in_front_of_index = np.where(temp_schedule[key][:, 0] == in_front_of_patient_id)[0][0]
    
    # Hole die Daten des Patienten, der eingefügt werden soll
    patient_data = temp_schedule[key][insert_index, :]
    
    # Lösche den Patienten von seinem ursprünglichen Platz
    temp_schedule[key] = np.delete(temp_schedule[key], insert_index, axis=0)
    
    # Passe den Zielindex an, falls nötig, nachdem der Patient entfernt wurde
    if insert_index < in_front_of_index:
        in_front_of_index -= 1
    
    # Füge den Patienten vor dem Zielpatienten ein
    temp_schedule[key] = np.insert(temp_schedule[key], in_front_of_index, patient_data, axis=0)
    
    calculate_start_and_endtimes_per_doc(schedule=temp_schedule, key=key)

    # Neue Indizes nach Insert für patient_1 und Patient_2
    patient_1 = np.where(temp_schedule[key][:, 0] == insert_patient_id)[0][0]
    patient_2 = np.where(temp_schedule[key][:, 0] == in_front_of_patient_id)[0][0]
    
    # Prüfen, ob beide Bedingungen erfüllt sind
    if feasibility_check(temp_schedule, key, patient_1, Max_d=Max_d) and feasibility_check(temp_schedule, key, patient_2, Max_d=Max_d):
        return temp_schedule  # Neues Schedule zurückgeben, wenn beide Bedingungen erfüllt sind
    else:
        return schedule  # Ursprüngliches Schedule zurückgeben, wenn eine Bedingung nicht erfüllt ist


def swap_patients_between_docs_N3(schedule, patient_1, patient_2, Max_d):
    # patient_1 und patient_2 sind in der Form [key, patient_index]
    temp_schedule = deepcopy(schedule)

    key1, index1 = patient_1
    key2, index2 = patient_2

    # Hole die Patientendaten
    patient_data_1 = temp_schedule[key1][index1, :].copy()
    patient_data_2 = temp_schedule[key2][index2, :].copy()

    # Tausche die Patienten zwischen den Doktoren
    temp_schedule[key1][index1, :] = patient_data_2
    temp_schedule[key2][index2, :] = patient_data_1

    # Neuberechnung der Start- und Endzeiten für beide betroffenen Doktoren
    calculate_start_and_endtimes_per_doc(schedule=temp_schedule, key=key1)
    calculate_start_and_endtimes_per_doc(schedule=temp_schedule, key=key2)

        # Prüfen, ob beide Bedingungen erfüllt sind
    if feasibility_check(temp_schedule, key1, index1, Max_d=Max_d) and feasibility_check(temp_schedule, key2, index2, Max_d=Max_d):
        return temp_schedule  # Neues Schedule zurückgeben, wenn beide Bedingungen erfüllt sind
    else:
        return schedule  # Ursprüngliches Schedule zurückgeben, wenn eine Bedingung nicht erfüllt ist


def local_search(schedule, neighborhood, Max_d=120):
    temp_schedule = deepcopy(schedule)
    overall_tardiness = 0

    if neighborhood == "N1":
        for key in schedule:
            temp_schedule, lowest_tardiness = best_swap_N1(temp_schedule, key, Max_d=Max_d)
            overall_tardiness += lowest_tardiness
    if neighborhood == "N2":
        for key in schedule:
            temp_schedule, lowest_tardiness = best_insert_N2(temp_schedule, key, Max_d=Max_d)
            overall_tardiness += lowest_tardiness
    if neighborhood == "N3":
        # Erhalte alle möglichen Paare von Keys
        keys = list(temp_schedule.keys())
        key_pairs = combinations(keys, 2)
        # Durchlaufe alle möglichen Paare von Ärzten und führe den iterativen Swap durch
        for key1, key2 in key_pairs:
            temp_schedule, lowest_tardiness = best_swap_N3(temp_schedule, key1, key2)
        
        for key in temp_schedule:
            overall_tardiness += weighted_tardiness_per_doc(temp_schedule, key)

    return temp_schedule, overall_tardiness

    
def feasibility_check(schedule, key, index, Max_d):
    # Vergleiche neuer Start der Behandlungszeit mit due date + Max_d
    return schedule[key][index, [3]] < schedule[key][index, [5]]+Max_d

    

def best_swap_N1(schedule, key, Max_d = 120):
    # Anzahl der Patienten bei diesem Doktor
    num_patients = schedule[key].shape[0]
    
    # Initialisiere die Variablen für die beste Lösung
    best_schedule = deepcopy(schedule)
    lowest_tardiness = weighted_tardiness_per_doc(schedule, key)
    
    # Durchlaufe alle möglichen Paare von Patienten, vermeide doppelte Tauschoperationen
    for i in range(num_patients):
        for j in range(i + 1, num_patients):
            # Führe den Tausch durch
            temp_schedule = deepcopy(schedule)
            temp_schedule = swap_patients_by_doc_N1(temp_schedule, key, i, j, Max_d=Max_d)
            
            # Berechne den weighted tardiness für den getauschten Schedule
            tardiness = weighted_tardiness_per_doc(temp_schedule, key)
            
            # Aktualisiere die beste Lösung, wenn ein niedrigerer Wert gefunden wird
            if tardiness < lowest_tardiness:
                #print(f"Bessere Lösung für Doktor {key} gefunden: Tausch von {i} und {j}, von {lowest_tardiness} auf {tardiness}")
                lowest_tardiness = tardiness
                best_schedule = temp_schedule
    
    return best_schedule, lowest_tardiness

def best_insert_N2(schedule, key, Max_d = 120):
    # Anzahl der Patienten bei diesem Doktor
    num_patients = schedule[key].shape[0]
    
    # Initialisiere die Variablen für die beste Lösung
    best_schedule = deepcopy(schedule)
    lowest_tardiness = weighted_tardiness_per_doc(schedule, key)
    
    # Iteriere über alle möglichen Paare von Patienten-IDs
    for i in range(num_patients):
        for j in range(num_patients):
            if i != j:
                # Bestimme die Patienten-IDs
                patient_id_to_move = schedule[key][i, 0]
                patient_id_target = schedule[key][j, 0]
                
                # Führe die Einfügeoperation durch
                temp_schedule = insert_patient_by_doc_N2(schedule, key, patient_id_to_move, patient_id_target, Max_d=Max_d)
                
                # Berechne den weighted tardiness für den veränderten Schedule
                tardiness = weighted_tardiness_per_doc(temp_schedule, key)

                # Aktualisiere die beste Lösung, wenn ein niedrigerer Wert gefunden wird
                if tardiness < lowest_tardiness:
                    #print(f"Bessere Lösung für Doktor {key} gefunden: Insert von {i} vor {j}, von {lowest_tardiness} auf {tardiness}")
                    lowest_tardiness = tardiness
                    best_schedule = temp_schedule
    
    return best_schedule, lowest_tardiness


def best_swap_N3(schedule, key1, key2, Max_d = 120):
    # Anzahl der Patienten für die beiden Doktoren
    num_patients_key1 = schedule[key1].shape[0]
    num_patients_key2 = schedule[key2].shape[0]
    
    # Initialisiere die Variablen für die beste Lösung
    best_schedule = deepcopy(schedule)
    lowest_combined_tardiness = (
        weighted_tardiness_per_doc(schedule, key1) +
        weighted_tardiness_per_doc(schedule, key2)
    )
    
    # Durchlaufe alle möglichen Paare von Patienten zwischen den beiden Ärzten
    for i in range(num_patients_key1):
        for j in range(num_patients_key2):
            # Führe den Tausch durch
            swapped_schedule = swap_patients_between_docs_N3(schedule, [key1, i], [key2, j], Max_d=Max_d)
            
            # Berechne die kombinierten weighted tardiness für beide Doktoren
            combined_tardiness = (
                weighted_tardiness_per_doc(swapped_schedule, key1) +
                weighted_tardiness_per_doc(swapped_schedule, key2)
            )

            # Aktualisiere die beste Lösung, wenn ein niedrigerer Wert gefunden wird
            if combined_tardiness < lowest_combined_tardiness:
                #print(f"Bessere Lösung für Doktor {key1} und {key2} gefunden: Insert von {i} vor {j}, von {lowest_combined_tardiness} auf {combined_tardiness}")
                lowest_combined_tardiness = combined_tardiness
                best_schedule = swapped_schedule
    
    return best_schedule, lowest_combined_tardiness

from copy import deepcopy
import random

def random_shake(schedule, Max_d):
    temp_schedule = deepcopy(schedule)
    
    # Wähle eine zufällige Nachbarschaftsoperation: N1, N2 oder N3
    operation = random.choice(['N1', 'N2', 'N3'])
    keys = list(schedule.keys())
    if operation == 'N3' and len(keys)>1:
        # Randomly select two doctors and one patient from each for N3
        key1, key2 = random.sample(keys, 2)
        index1 = random.randint(0, temp_schedule[key1].shape[0] - 1)
        index2 = random.randint(0, temp_schedule[key2].shape[0] - 1)
        temp_schedule = swap_patients_between_docs_N3(temp_schedule, [key1, index1], [key2, index2],  Max_d=Max_d)

    elif operation == 'N1':
        # Randomly select a doctor and two patient indices for N1
        key = random.choice(keys)
        if temp_schedule[key].shape[0] > 1:
            i, j = random.sample(range(temp_schedule[key].shape[0]), 2)
            temp_schedule = swap_patients_by_doc_N1(temp_schedule, key, i, j, Max_d=Max_d)
    
    elif operation == 'N2':
        # Randomly select a doctor and two patient indices for N2
        key = random.choice(keys)
        if temp_schedule[key].shape[0] > 1:
            i, j = random.sample(range(temp_schedule[key].shape[0]), 2)
            patient_id_to_move = temp_schedule[key][i, 0]
            patient_id_target = temp_schedule[key][j, 0]
            temp_schedule = insert_patient_by_doc_N2(temp_schedule, key, patient_id_to_move, patient_id_target,  Max_d=Max_d)
    


    overall_tardiness = 0
    for key in temp_schedule:
        overall_tardiness += weighted_tardiness_per_doc(temp_schedule, key)
    
    return temp_schedule, overall_tardiness

def VND(schedule, overall_tardiness, neighborhoods, Max_d=120):
    current_schedule = deepcopy(schedule)
    current_tardiness = overall_tardiness
    improvement = True

    while improvement:
        improvement = False
        for neighborhood in neighborhoods:
            # Führe die lokale Suche für die aktuelle Nachbarschaft aus
            if neighborhood == "N1":
                new_schedule, _ = local_search(schedule, neighborhood="N1", Max_d=Max_d)
            elif neighborhood == "N2":
                new_schedule, _ = local_search(schedule, neighborhood="N2", Max_d=Max_d)
            elif neighborhood == "N3":
                new_schedule, _ = local_search(schedule, neighborhood="N3", Max_d=Max_d)
            else:
                continue

            # Vergleiche die neue und aktuelle Lösung
            if _ < current_tardiness:
                current_schedule = new_schedule
                current_tardiness = _
                improvement = True
                break  # Beginne die Suche erneut bei der ersten Nachbarschaft

    return current_schedule, current_tardiness

import time

def general_vns(initial_schedule, initial_tardiness ,neighborhoods, Max_d=120, no_improvement_limit=1000, time_limit = 60):
    current_schedule = deepcopy(initial_schedule)
    best_schedule = current_schedule
    best_schedule_tardiness = initial_tardiness
    no_improvement_count = 0

    start_time = time.time()
    

    completion_time = time.time() - start_time
    while completion_time <= time_limit:
        if not no_improvement_count <= no_improvement_limit:
            print(f"No improvement for {no_improvement_limit} iterations")
            completion_time = time.time() - start_time
            return best_schedule, best_schedule_tardiness, completion_time 
        
        # Shake: Erzeugen einer neuen Lösung durch eine zufällige Veränderung
        shaken_schedule, shaken_tardiness = random_shake(current_schedule, Max_d=Max_d)

        # VND: Anwenden der lokalen Optimierung
        vnd_schedule, vnd_tardiness = VND(shaken_schedule, shaken_tardiness ,neighborhoods, Max_d)

        # Bewertung der neuen Lösung
        if vnd_tardiness < best_schedule_tardiness:
            print(f"Bessere Lösung {completion_time}: {best_schedule_tardiness} auf {vnd_tardiness}")
            best_schedule = vnd_schedule
            best_schedule_tardiness = vnd_tardiness
            current_schedule = vnd_schedule
            no_improvement_count = 0  # Reset, da eine Verbesserung gefunden wurde
        else:
            no_improvement_count += 1
        completion_time = time.time() - start_time
        
    return best_schedule, best_schedule_tardiness, completion_time

import math

def simulated_annealing(schedule, total_tardiness, Imax=1000, cooling_rate=0.95, min_temperature=1.0, start_temperature=100, time_limit=600, Max_d=120):
    current_schedule = deepcopy(schedule) # Start solution (S) is the result from the opening heuristic
    current_tardiness = deepcopy(total_tardiness) # Calculate the makespan of the start solution
    # Input seed for reproducibility if necessary
    np.random.seed()
    random.seed()
    # Possibility to count not best but accepted solutions
    current_best_solution = current_schedule
    current_best_solution_tardiness = current_tardiness

    temperature =  start_temperature 
    cooling_rate = cooling_rate  
    min_temperature = min_temperature 
    start_time = time.time()
    Imax = Imax

    # Iterate while the temperature is sufficiently high
    while temperature > min_temperature:
        I = 1

        while I <= Imax:
            # If time limit is set and triggered, return solution
            if time_limit is not None and (time.time() - start_time) > time_limit:
                 return (current_best_solution, current_best_solution_tardiness, temperature)
                
            # Compute new_schedule according to the chosen neighborhood definition
            # Durchlaufe solange random_shake bis eine gültige Lösung erreicht ist
            # random_shake ist die Durchführung einer zufälligen Nachbarschaftsdefinition
            new_tardiness = current_tardiness
            while new_tardiness == current_tardiness:
                shaken_schedule, new_tardiness = random_shake(current_schedule, Max_d=Max_d)
            


            # Calculate the energy difference (Difference in Tardiness)
            delta = new_tardiness - current_tardiness
            if delta < 0:
                current_schedule = shaken_schedule # Set S = S' if the Tardiness of S' is better than S
                current_tardiness = new_tardiness
                    
                if current_tardiness < current_best_solution_tardiness:
                    print(f"Better Solution: {(time.time() - start_time)},{temperature}, {I} {current_best_solution_tardiness} to {current_tardiness}")
                    current_best_solution = deepcopy(current_schedule) # Set S* (currently best solution) to S'
                    current_best_solution_tardiness = deepcopy(current_tardiness)
            else:
                # Accept solutions with a certain probability
                acceptance_probability = math.exp(-delta / temperature) # Exponential function e^-delta/ temperature
                if random.random() < acceptance_probability:
                    #print(f"Accepted bad Solution")
                    current_schedule = deepcopy(shaken_schedule) # Set S = S' if the random variable is less than the exponential function

                # Increase iteration counter by 1
            I += 1
            # Cool down the temperature
        temperature *= cooling_rate
    return (current_best_solution, current_best_solution_tardiness, temperature)
    
    
    
