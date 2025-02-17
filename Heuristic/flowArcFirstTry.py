import networkx as nx
import visualization
import json
from classes import Instances


#Aktuell nicht genutzt 
def construct_arc_flow_graph(instance):
    G = nx.DiGraph()
    N = set()
    A = []
    P = {t: False for t in range(instance.T+1)}
    P[instance.T] = True

    for r_j, _ in instance.patients:
        P[r_j] = True

    patient_arcs = {j: [] for j in range(len(instance.patients))}
    for t in range(instance.T):
        if P[t]:
            for j, (r_j, p_j) in enumerate(instance.patients):
                if r_j <= t and t + p_j <= instance.T:
                    P[t + p_j] = True
                    patient_arcs[j].append((t, t + p_j))
    
    for t in range(instance.T + 1):
        if P[t]:
            N.add(t)
            G.add_node(t)
    
    sorted_N = sorted(N)
    for i in range(len(sorted_N) - 1):
        A.append((sorted_N[i], sorted_N[i+1], 0))
    
    for j, arcs in patient_arcs.items():
        for (start, end) in arcs:
            A.append((start, end, j+1))
    
    for (u, v, label) in A:
        G.add_edge(u, v, patient=label)
    
    return G, N, A

#Greedy Eröffnungsheuristik
def opening_heuristic_greedy(instance):
    patients_sorted = sorted(enumerate(instance.patients), key=lambda x: (x[1][0], instance.weights[x[0]]))
    doctor_completion = [0] * instance.doctors
    schedule = []
    total_cost = 0

    for j, (rj, pj) in patients_sorted:
        min_doctor = min(range(instance.doctors), key=lambda d: doctor_completion[d])
        sj = max(rj, doctor_completion[min_doctor])
        doctor_completion[min_doctor] = sj + pj
        Tj = max(0, sj - instance.due_dates[j])
        total_cost += instance.weights[j] * Tj
        schedule.append((sj, sj + pj, j + 1, min_doctor + 1))
    
    return schedule, total_cost

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
        patients.append((patient['arrival_time'], patient['realized_processing_time']))
        weights.append(patient['weight'])
        due_dates.append(patient['arrival_time'] + patient['max_wait_time'])

    #T Berechnen:
    max_release = max(patients, key=lambda tupel: tupel[0])[0]
    max_treatment = max(patients, key=lambda tupel: tupel[1])[1]
    sum_overPatients = sum(x for x,_ in patients)
    T = (1/doctors) * sum_overPatients + ((doctors-1)/doctors) * max_treatment + max_release
    
    #Instanz objekt generieren
    instance = Instances(patients, doctors, due_dates, weights, T)
    return instance

file_path = 'new_test_instances.json'
print("Wie viel Doktoren arbeiten heute?")
doctors = int(input())

instance = map_patient_data(file_path, doctors)

print("Patienten:", instance.patients)
print("Anzahl der Doktoren:", instance.doctors)
print("Maximale Laufzeit:", instance.T)
print("Gewichte:", instance.weights)
print("Späteste Behandlungszeiten:", instance.due_dates)
print(len(instance.patients))

schedule, total_cost = opening_heuristic_greedy(instance)
visualization.visualize_schedule(schedule, total_cost, instance.doctors, len(instance.patients))
print(schedule)

print("Optimierter Zeitplan:")
for start, end, patient, doctor in schedule:
    print(f"Patient {patient} von {start} bis {end} mit Arzt {doctor}")
print(f"Gesamtkosten: {total_cost}")
