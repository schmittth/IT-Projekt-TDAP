import networkx as nx
import numpy as np
import visualization
import json
from classes import Instance


#Greedy Eröffnungsheuristik
def opening_heuristic_greedy(instance):
    sorted_patients = sorted(instance.patients, key=lambda x: x[1])
    patients_sorted = [(i, patient) for i, patient in enumerate(sorted_patients)]
    doctor_completion = [0] * instance.doctors
    schedule = {}
    total_cost = 0

    for doc in range(1, instance.doctors + 1):
        schedule[doc] = []

    for j, (id, rj, pj) in patients_sorted:
        available_doctors = []
        for d in range(instance.doctors):
            if doctor_completion[d] <= rj:
                available_doctors.append(d)

        if available_doctors:
            if len(available_doctors) == 1:
                min_doctor = available_doctors[0]
            else:
                # Berechne die Arztgewichtung dynamisch
                doctor_weights = []
                for d in available_doctors:
                    doctor_weight = sum(row[2] for row in schedule.get(d + 1, []))  # Summiere Bearbeitungszeiten
                    doctor_weights.append(doctor_weight)
                min_doctor = available_doctors[doctor_weights.index(min(doctor_weights))]

            sj = rj
        else:
            min_doctor = min(range(instance.doctors), key=lambda d: doctor_completion[d])
            sj = max(rj, doctor_completion[min_doctor])

        doctor_completion[min_doctor] = sj + pj
        Tj = max(0, sj - instance.due_dates[j])
        total_cost += instance.weights[j] * Tj
        add_entry(schedule, min_doctor + 1, [id, rj, pj, sj, sj + pj, instance.due_dates[j], max(0, sj - instance.due_dates[j]), instance.weights[j]])

    for doctor in schedule:
        schedule[doctor] = np.array(schedule[doctor])

    return schedule, total_cost

#Patient einplanen
def add_entry(schedule, doctor, entry):
    if doctor not in schedule:
        schedule[doctor] = []
    schedule[doctor].append(entry)

#Mapping der JSON Daten auf die benötigte Datenstruktur
def map_patient_data(json_file_path, doctors):

    with open(json_file_path, 'r') as f:
        data = json.load(f)

    patients = []
    weights = []
    due_dates = []
    T = int
    doctors = doctors

    for patient in data:
        patients.append((patient['patient_id'], patient['arrival_time'], patient['realized_processing_time']))
        weights.append(patient['weight'])
        due_dates.append(patient['arrival_time'] + patient['max_wait_time'])


    #T Berechnen:
    #max_release = max(patients, key=lambda tupel: tupel[0])[0]
    max_release = max(patients, key=lambda tupel: tupel[1])[1]
    max_treatment = max(patients, key=lambda tupel: tupel[2])[2]
    sum_overPatients = sum(x for _,x,_ in patients)
    T = (1/doctors) * sum_overPatients + ((doctors-1)/doctors) * max_treatment + max_release
    
    #Instanz objekt generieren
    instance = Instance(patients, doctors, due_dates, weights, T)
    return instance

