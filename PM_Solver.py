import json
import random
import webbrowser
from ortools.sat.python import cp_model


# Lade Patientendaten aus test_instances.json
with open("test_instances1.json", "r") as file:
    test_instances = json.load(file)

# Flache Liste aller Patienten (da in Gruppen gespeichert)
all_patients = [patient for instance in test_instances for patient in instance]

num_doctors = 10  # Anzahl der verfügbaren Ärzte
num_patients = len(all_patients)

# Planungshorizont bestimmen (Summe aller Behandlungszeiten)
horizon = max(p["arrival_time"] + p["expected_processing_time"] for p in all_patients) + 100  

model = cp_model.CpModel()

# Variablen für jeden Patienten: Startzeit, Endzeit, Doktor und Intervall
all_tasks = {}
doctor_to_intervals = {d: [] for d in range(num_doctors)}
patients_tardiness = []

for patient_id, patient in enumerate(all_patients):
    start = model.NewIntVar(0, horizon, f"start_{patient_id}")
    end = model.NewIntVar(0, horizon, f"end_{patient_id}")
    doctor = model.NewIntVar(0, num_doctors - 1, f"doctor_{patient_id}")
    tardiness = model.NewIntVar(0, horizon, f"tardiness_{patient_id}")
    patients_tardiness.append(tardiness)

    # Frühestmögliche Startzeit
    model.Add(start >= patient["arrival_time"])

    # Endzeit ist Startzeit plus erwartete Behandlungsdauer
    model.Add(end == start + patient["expected_processing_time"])

    # Tardiness (Verspätung, falls über max. Wartezeit)
    model.Add(tardiness >= end - (patient["arrival_time"] + patient["max_wait_time"]))
    model.Add(tardiness >= 0)

    # Optionale Intervalle für jeden Doktor
    for d in range(num_doctors):
        is_assigned = model.NewBoolVar(f"isAssigned_{patient_id}_{d}")
        optional_interval = model.NewOptionalIntervalVar(
            start, patient["expected_processing_time"], end, is_assigned, f"optionalInterval_{patient_id}_{d}"
        )
        doctor_to_intervals[d].append(optional_interval)
        model.Add(doctor == d).OnlyEnforceIf(is_assigned)
        model.Add(doctor != d).OnlyEnforceIf(is_assigned.Not())

    # Globales Intervall für den Patienten
    interval = model.NewIntervalVar(start, patient["expected_processing_time"], end, f"interval_{patient_id}")
    all_tasks[patient_id] = (start, end, doctor, interval)

# Füge Disjunktiv-Bedingungen für Doktoren hinzu (keine Überschneidungen)
for intervals in doctor_to_intervals.values():
    model.AddNoOverlap(intervals)

# Zielfunktion: Minimierung der gewichteten Summe der Verspätungen
model.Minimize(sum(t * (5 - all_patients[p]["weight"]) for p, t in enumerate(patients_tardiness)))

# Modell lösen
solver = cp_model.CpSolver()
solver.parameters.log_search_progress = True
status = solver.Solve(model)

if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    print(f"Solution Sum of Weighted Tardiness: {solver.ObjectiveValue()}")
    assigned_tasks = {d: [] for d in range(num_doctors)}
    
    for patient_id, task in all_tasks.items():
        start_time = solver.Value(task[0])
        duration = all_patients[patient_id]["expected_processing_time"]
        doctor_id = solver.Value(task[2])
        assigned_tasks[doctor_id].append((patient_id, start_time, duration))
    
    # HTML-Gantt-Chart generieren
    with open("schedule.html", "w") as f:
        f.write("""
        <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
        <script type="text/javascript">
        google.charts.load('current', {packages:['timeline']});
        google.charts.setOnLoadCallback(drawChart);
        function drawChart() {
            var data = new google.visualization.DataTable();
            data.addColumn('string', 'Doctor');
            data.addColumn('string', 'Patient');
            data.addColumn('date', 'Start');
            data.addColumn('date', 'End');
            data.addRows([
        """)

        for doctor_id, tasks in assigned_tasks.items():
            for patient_id, start, duration in tasks:
                f.write(f"['Doctor {doctor_id}', 'Patient {patient_id}', new Date(0,0,0,0,0,{start}), new Date(0,0,0,0,0,{start + duration})],\n")

        f.write("""
            ]);
            var options = { height: 500 };
            var chart = new google.visualization.Timeline(document.getElementById('chart_div'));
            chart.draw(data, options);
        }
        </script>
        <div><p>Tardiness: """ + str(solver.ObjectiveValue()) + """</p></div>
        <div id="chart_div" style="width: 100%; height: 500px;"></div>
        """)

    webbrowser.open("schedule.html")
else:
    print("No solution found.")
