import collections
from ortools.sat.python import cp_model
import json

def main(path, num_doctors):

    with open(path, "r") as file:
        patients = json.load(file)

    num_patients = len(patients)

    # Computes horizon dynamically as the sum of all durations.
    sum_of_processing_time = 0
    max_arrival_time = 0
    for patient in patients:
        sum_of_processing_time += patient["realized_processing_time"]
        max_arrival_time = max(max_arrival_time, patient["arrival_time"])
    horizon = sum_of_processing_time + max_arrival_time

    # Creates the model.
    model = cp_model.CpModel()

    # Entscheidungsvariablen
    start_times = {}
    end_times = {}
    machine_assignments = {}
    tardiness = {}
    intervals = {}
    is_on_doctor = {}

    for j in patients:
        start_times[j["patient_id"]] = model.NewIntVar(0, 1000, f'start_{j["patient_id"]}')
        end_times[j["patient_id"]] = model.NewIntVar(0, 1000, f'end_{j["patient_id"]}')
        machine_assignments[j["patient_id"]] = model.NewIntVar(0, num_doctors - 1, f'machine_{j["patient_id"]}')
        tardiness[j["patient_id"]] = model.NewIntVar(0, 1000, f'tardiness_{j["patient_id"]}')
        intervals[j["patient_id"]] = model.NewIntervalVar(start_times[j["patient_id"]], j["realized_processing_time"], end_times[j["patient_id"]], f'interval_{j["patient_id"]}')
        for d in range(num_doctors):
            is_on_doctor[j["patient_id"]-1][d] = model.new_bool_var("isOnDoc")
        
    # Constraints
    for j in patients:
        model.add(start_times[j["patient_id"]] >= j["arrival_time"])
        model.add(end_times[j["patient_id"]] == start_times[j["patient_id"]] + j["realized_processing_time"])
        model.add(tardiness[j["patient_id"]] >= end_times[j["patient_id"]] - (j["arrival_time"]+j["max_wait_time"]))
        model.add(sum(is_on_doctor[j["patient_id"]][d] for d in range(num_doctors)) == 1)

    """for m in range(num_doctors):
        machine_intervals = []
        for j in patients:
            interval_var = model.new_optional_interval_var(start_times[j["patient_id"]], j["realized_processing_time"], end_times[j["patient_id"]], False, f'machine_interval_{j["patient_id"]}_{m}')
            machine_intervals.append(interval_var)
        model.AddNoOverlap(machine_intervals)"""
    
     # Machine Intervals nach Doktor organisieren
    machine_intervals = collections.defaultdict(list)
    for m in range(num_doctors):
        for j in patients:
            interval_var = model.new_optional_interval_var(start_times[j["patient_id"]], j["realized_processing_time"], end_times[j["patient_id"]], f'machine_interval_{j["patient_id"]}_{m}')
            machine_intervals[m].append(interval_var)

    # NoOverlap Constraints für jeden Doktor
    for m in range(num_doctors):
        model.add_no_overlap(machine_intervals[m])

    """#Jeder patient muss genau einmal behandelt werden
    for p in range(num_patients):
        is_present_sum = 0
        for m in range(num_doctors):
            is_present_sum += machine_intervals[m][p].is_present
        model.Add(is_present_sum == 1)"""
    
    print(machine_intervals)

    # Zielfunktion
    model.Minimize(sum(tardiness.values()))
    # Solver
    
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print('Solution:')
        for j in patients:
            print(f'Job {j["patient_id"]}: Start={solver.Value(start_times[j["patient_id"]])}, End={solver.Value(end_times[j["patient_id"]])}, Machine={solver.Value(machine_assignments[j["patient_id"]])}, Tardiness={solver.Value(tardiness[j["patient_id"]])}')
        print(f'Total Tardiness: {solver.ObjectiveValue()}')
    else:
        print('No solution found.')

        
main("new_test_instances_short.json", 2)
