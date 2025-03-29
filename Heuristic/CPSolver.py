import json
from ortools.sat.python import cp_model
import visualization as vs
import time
import numpy as np

def solveCPdeterministic (filepath, numDocs, runtime):

    #Instanz importieren:
    with open(filepath, "r") as file:
        patients = json.load(file)
    
    # Erstelle das CP-Solver-Modell
    model = cp_model.CpModel()
    
    #Variablen kreieren:
    start_vars = {}
    end_vars = {}
    tardiness_vars = {}
    due_dates = {}
    durations = {}
    arrival_time = {}
    weight = {}
    isPresent = {}
    
    doctor_intervals = {}
    for m in range(numDocs):
        doctor_intervals[m] = []

    isPresentInterval = {}
    for i, patient in enumerate(patients):
        isPresentInterval[i] = []

    #Berechne Horizont dynamisch als Summe aller Behandlungszeiten plus späteste Ankunftszeit
    sum_of_processing_time = 0
    max_arrival_time = 0
    for patient in patients:
        sum_of_processing_time += patient["realized_processing_time"]
        max_arrival_time = max(max_arrival_time, patient["arrival_time"])
    horizon = sum_of_processing_time + max_arrival_time

    
    #Erstelle Variablen und Konstanten für jeden Patienten
    for i, patient in enumerate(patients):
        #Konstanten
        arrival_time[i] = model.new_constant(patient["arrival_time"])
        due_dates[i] = model.new_constant(patient["max_wait_time"] + patient["arrival_time"])
        durations[i] = model.new_constant(patient["realized_processing_time"])
        weight[i] = model.new_constant(patient["weight"])

        start_vars[i] = {}
        end_vars[i] = {}
        tardiness_vars[i] = {}
        isPresent[i] = {} 

        for m in range(numDocs):
            #Variablen
            start_vars[i][m] = model.new_int_var(patient["arrival_time"], horizon, f"start{m}_{i}")
            end_vars[i][m] = model.new_int_var(patient["arrival_time"], horizon, f"end{m}_{i}")
            tardiness_vars[i][m] = model.new_int_var(0, horizon, f"tardiness{m}_{i}")
            isPresent[i][m] = model.new_int_var(0, 1, f"isPresent{m}_{i}")        
            
            #Hinzufügen als Intervalle
            patientInterval = model.new_optional_interval_var(start_vars[i][m], durations[i], end_vars[i][m], isPresent[i][m], f"interval_{m}_{i}")
            isPresentInterval[i].append(isPresent[i][m])
            doctor_intervals[m].append(patientInterval)
    #Constraint: Jeder Patient nur einmal
    for i, patient in enumerate(patients):    
        model.add_linear_constraint(linear_expr=sum(isPresentInterval[i]), lb=1, ub=1)

    
    #Constraints:
    for i, patient in enumerate(patients):
        for m in range(numDocs):
            #Endzeit = Startzeit + Bearbeitungszeit
            model.add(end_vars[i][m] == start_vars[i][m] + durations[i])
            
            #Tardiness berechnen
            model.add(tardiness_vars[i][m] >= start_vars[i][m] - due_dates[i]).only_enforce_if(isPresent[i][m])
            model.add(tardiness_vars[i][m] == 0).only_enforce_if(isPresent[i][m].Not())
    
    #Constraint: Keine Überlappung
    for m in range(numDocs):
        model.add_no_overlap(doctor_intervals[m])

    #Zielfunktion: Minimierung der Gewichteten Verspätung
    counter = 0
    #Horizont für weighted Tardiness um den Faktor des maximalen Gewichts multiplizieren
    weighted_horizon = horizon*4
    weighted_tardiness = []
    for i, patient in enumerate (patients):
        for m in range(numDocs):
            weighted_tardiness.append(model.new_int_var(0, weighted_horizon, f"weighted_tardiness_{i}_{m}"))
            model.add_multiplication_equality(weighted_tardiness[counter], [tardiness_vars[i][m], weight[i]])
            counter= counter+1
    model.minimize(sum(weighted_tardiness))
    
    #Solver auswählen
    solver = cp_model.CpSolver()
    #Maximale Laufzeit
    solver.parameters.max_time_in_seconds = runtime
    st = time.time()
    #Solven
    status = solver.Solve(model)

    #Ausgabe der Ergebnisse
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        et = time.time()
        schedule = {}
        for m in range(numDocs):
            schedule[m] = []
        print(f"ExecutionTime: {et-st}")
        if status == cp_model.OPTIMAL:
            print("Optimale Lösung gefunden:")
        else:
            print("Feasible Lösung gefunden:")
        for i in range(len(patients)):
            for m in range(numDocs):
                if solver.Value(isPresent[i][m]):
                    thisPatient = (i+1, solver.Value(start_vars[i][m]), solver.Value(end_vars[i][m]))
                    schedule[m].append(thisPatient)
                    print (f"Patient {i+1}: Start={solver.Value(start_vars[i][m])}, End={solver.Value(end_vars[i][m])}, Tardiness={solver.Value(tardiness_vars[i][m])}, Doctor = {m}, isPresent ={solver.Value(isPresent[i][m])}")
        print(f"Gesamte gewichtete Tardiness: {solver.ObjectiveValue()}")
        vs.visualizeCPDeterministic(schedule, solver.ObjectiveValue(), et-st)
        vs.log_data_to_csv(filepath, numDocs,'n/a', solver.ObjectiveValue(), 'CPSolver', 1, et-st)
    else:
        print("Keine Lösung gefunden.")


def solveCPDynamic (waitingRoom, earliestStart):
    #Anzahl der Doktoren auslesen
    numDocs = len(waitingRoom)
    
    #Patienten in ein Array schreiben und sortieren
    patientsUnsorted = []
    for m in range(numDocs):
        for i in range(len(waitingRoom[m+1])):
            patientsUnsorted.append(waitingRoom[m+1][i])
    patients = sorted(patientsUnsorted, key=lambda x: x[0])
    
    # Erstelle das CP-Solver-Modell
    model = cp_model.CpModel()
    
    #Variablen kreieren:
    start_vars = {}
    end_vars = {}
    tardiness_vars = {}
    due_dates = {}
    durations = {}
    arrival_time = {}
    weight = {}
    isPresent = {}
    
    doctor_intervals = {}
    for m in range(numDocs):
        doctor_intervals[m] = []

    isPresentInterval = {}
    for i in range(len(patients)):
        isPresentInterval[i] = []

    #Berechne Horizont dynamisch als Summe aller Behandlungszeiten plus späteste Ankunftszeit
    sum_of_processing_time = 0
    max_arrival_time = 0
    for i, patient in enumerate(patients):
            sum_of_processing_time += patients[i][8]
            max_arrival_time = max(max_arrival_time, patients[i][1])
    horizon = sum_of_processing_time + max_arrival_time

    
    #Erstelle Variablen und Konstanten für jeden Patienten
    for i, patient in enumerate(patients):
        #Konstanten
        arrival_time[i] = model.new_constant(patients[i][1])
        due_dates[i] = model.new_constant(patients[i][5])
        durations[i] = model.new_constant(patients[i][8])
        weight[i] = model.new_constant(patients[i][7])

        start_vars[i] = {}
        end_vars[i] = {}
        tardiness_vars[i] = {}
        isPresent[i] = {} 

        for m in range(numDocs):
            #Variablen
            start_vars[i][m] = model.new_int_var(earliestStart[m], horizon, f"start{m}_{i}")
            end_vars[i][m] = model.new_int_var(earliestStart[m], horizon, f"end{m}_{i}")
            tardiness_vars[i][m] = model.new_int_var(0, horizon, f"tardiness{m}_{i}")
            isPresent[i][m] = model.new_int_var(0, 1, f"isPresent{m}_{i}")        
            
            #Hinzufügen als Intervalle
            patientInterval = model.new_optional_interval_var(start_vars[i][m], durations[i], end_vars[i][m], isPresent[i][m], f"interval_{m}_{i}")
            isPresentInterval[i].append(isPresent[i][m])
            doctor_intervals[m].append(patientInterval)
    #Constraint: Jeden Patienten nur einmal einplanen
    for i, patient in enumerate(patients):    
        model.add_linear_constraint(linear_expr=sum(isPresentInterval[i]), lb=1, ub=1)

    
    #Constraints
    for i, patient in enumerate(patients):
        for m in range(numDocs):
            #Endzeit = Startzeit + Bearbeitungszeit
            model.add(end_vars[i][m] == start_vars[i][m] + durations[i])
            
            #Tardiness berechnen
            model.add(tardiness_vars[i][m] >= start_vars[i][m] - due_dates[i]).only_enforce_if(isPresent[i][m])
            model.add(tardiness_vars[i][m] == 0).only_enforce_if(isPresent[i][m].Not())
    
    #Constraint: Keine Überlappung
    for m in range(numDocs):
        model.add_no_overlap(doctor_intervals[m])

    #Zielfunktion: Minimierung der Gewichteten Verspätung
    counter = 0
    #Horizont für weighted Tardiness um den Faktor des maximalen Gewichts multiplizieren
    weighted_horizon = horizon*4
    weighted_tardiness = []
    for i, patient in enumerate (patients):
        for m in range(numDocs):
            weighted_tardiness.append(model.new_int_var(0, weighted_horizon, f"weighted_tardiness_{i}_{m}"))
            model.add_multiplication_equality(weighted_tardiness[counter], [tardiness_vars[i][m], weight[i]])
            counter= counter+1
    model.minimize(sum(weighted_tardiness))
    
    #Solver auswählen
    solver = cp_model.CpSolver()
    #Maximale Laufzeit
    solver.parameters.max_time_in_seconds = 20
    #Start der Solving Time
    st = time.time()
    #Solven
    status = solver.Solve(model)

    #Ausgabe der Ergebnisse
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        #Ende der Solving Time
        et = time.time()
        
        schedule = {}
        numP = {}

        for m in range(numDocs):
            schedule[m] = []
            numP[m+1] = []

        print(f"ExecutionTime: {et-st}")
        if status == cp_model.OPTIMAL:
            print("Optimale Lösung gefunden:")
        else:
            print("Feasible Lösung gefunden:")
        for i, patient in enumerate(patients):
            for m in range(numDocs):
                if solver.Value(isPresent[i][m]):
                    thisPatient = (i+1, patients[i][1], patients[i][2], solver.Value(start_vars[i][m]), solver.Value(end_vars[i][m]), patients[i][5], solver.Value(tardiness_vars[i][m]), patients[i][7], patients[i][8])
                    schedule[m].append(thisPatient)
                    print (f"Patient {i+1}: Start={solver.Value(start_vars[i][m])}, End={solver.Value(end_vars[i][m])}, Tardiness={solver.Value(tardiness_vars[i][m])}, Doctor = {m}, isPresent ={solver.Value(isPresent[i][m])}")
        print(f"Gesamte gewichtete Tardiness: {solver.ObjectiveValue()}")
        for m in range(numDocs):
            numP[m+1] = np.array(schedule[m])
        vs.visualizeCPDynamic(schedule, solver.ObjectiveValue(), et-st)
        vs.log_data_to_csv_ND(numDocs, solver.ObjectiveValue(), 'CPSolver', et-st)
        return numP, solver.ObjectiveValue()
    else:
        print("Keine Lösung gefunden.")

solveCPdeterministic("new_test_instances_short.json", 2, 20)