import json
import random
import webbrowser
from ortools.sat.python import cp_model
import visualization as vs


def erstelle_cp_solver_modell(instanz_dateipfad, num_doctors):
    # Lade Patientendaten
    with open(instanz_dateipfad, "r") as file:
        patients = json.load(file)

    num_patients = len(patients)

    # Erstelle das CP-Solver-Modell
    model = cp_model.CpModel()

    # Variablen erstellen
    start_vars = {}
    end_vars = {}
    tardiness_vars = {}
    doctor_vars = {}

    for i, patient in enumerate(patients):
        start_vars[i] = model.NewIntVar(patient["arrival_time"], 1000, f"start_{i}")
        end_vars[i] = model.NewIntVar(patient["arrival_time"], 1000, f"end_{i}")
        tardiness_vars[i] = model.NewIntVar(0, 1000, f"tardiness_{i}")
        doctor_vars[i] = model.NewIntVar(0, num_doctors - 1, f"doctor_{i}")

    # Constraints hinzufügen
    for i, patient in enumerate(patients):
        model.Add(end_vars[i] == start_vars[i] + patient["realized_processing_time"])
        due_date = patient["arrival_time"] + patient["max_wait_time"]
        model.Add(tardiness_vars[i] >= start_vars[i] - due_date)
        model.Add(tardiness_vars[i] >= 0)

    # Keine Überlappung von Patienten bei gleichem Arzt
    for d in range(num_doctors):
        interval_vars = []
        for i in range(num_patients):
            processing_time = patients[i]["realized_processing_time"]
            is_doctor_d = model.NewBoolVar(f"is_doctor_{i}_d_{d}")
            model.Add(doctor_vars[i] == d).OnlyEnforceIf(is_doctor_d)
            interval_vars.append(model.NewOptionalIntervalVar(
                start_vars[i],
                processing_time,
                end_vars[i],
                is_doctor_d,  # Verwende die Boolesche Variable
                f"interval_{i}_doctor_{d}"
            ))
        model.AddNoOverlap(interval_vars)
    # Zielfunktion: Minimierung der gewichteten Tardiness
    weighted_tardiness = []
    for i, patient in enumerate(patients):
        weighted_tardiness.append(tardiness_vars[i] * patient["weight"])
    model.Minimize(sum(weighted_tardiness))

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("Lösung gefunden:")
        for i in range(len(patients)):
            print(f"Patient {i+1}: Start={solver.Value(start_vars[i])}, End={solver.Value(end_vars[i])}, Tardiness={solver.Value(tardiness_vars[i])}, Arzt={solver.Value(doctor_vars[i])}")
        print(f"Gesamte gewichtete Tardiness: {solver.ObjectiveValue()}")
    else:
        print("Keine Lösung gefunden.")
    


# Modell lösen
"""def solveCP(model, start_vars, end_vars, tardiness_vars, doctor_vars, patients):
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("Lösung gefunden:")
        for i in range(len(patients)):
            print(f"Patient {i+1}: Start={solver.Value(start_vars[i])}, End={solver.Value(end_vars[i])}, Tardiness={solver.Value(tardiness_vars[i])}, Arzt={solver.Value(doctor_vars[i])}")
        print(f"Gesamte gewichtete Tardiness: {solver.ObjectiveValue()}")
    else:
        print("Keine Lösung gefunden.")"""
    

#Ausführen
def executeCP (filePath, doctors):
    model, start_vars, end_vars, tardiness_vars, doctor_vars, patients = erstelle_cp_solver_modell(filePath, doctors)
    """assigned_tasks, tardiness =""" 
    solveCP(model, start_vars, end_vars, tardiness_vars, doctor_vars, patients)
    #vs.visualizeCP(assigned_tasks, tardiness)