import webbrowser
import os
import re
import csv
from datetime import datetime

#Wie viele Files sind im Loesungen Odner?
def get_next_filename_number(directory, filename_base="Loesung"):
    pattern = re.compile(rf"{filename_base}_(\d+)\.html")
    existing_numbers = []

    for filename in os.listdir(directory):
        match = pattern.match(filename)
        if match:
            existing_numbers.append(int(match.group(1)))

    if not existing_numbers:
        return 1

    return max(existing_numbers) + 1

#Visualisierung mit GoogleCharts in HTML
def visualize_schedule(schedule, total_cost, runTime, basisfilename):
    next_number = get_next_filename_number('./Loesungen', basisfilename)
    filename = os.path.join('./Loesungen', f"{basisfilename}_{next_number}.html")
    numberOfPatients = get_number_of_patients(schedule)
    numberOfDoctors = len(schedule)

    html_content = f"""
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">
    google.charts.load("current", {{packages:["timeline"]}});
    google.charts.setOnLoadCallback(drawChart);
    function drawChart() {{
        var container = document.getElementById('example3.1');
        var chart = new google.visualization.Timeline(container);
        var dataTable = new google.visualization.DataTable();
        dataTable.addColumn({{ type: 'string', id: 'DoctorNumber' }});
        dataTable.addColumn({{ type: 'string', id: 'PatientNumber' }});
        dataTable.addColumn({{ type: 'string', role: 'tooltip' }});
        dataTable.addColumn({{ type: 'date', id: 'Start' }});
        dataTable.addColumn({{ type: 'date', id: 'End' }});

        dataTable.addRows(["""
    
    for doctor, patient_data in schedule.items():
        for row in patient_data:
            patient_id = row[0]
            start_time = row[3]
            end_time = row[4]
            html_content += f"""
                ['Doctor {doctor}' , 'Patient {patient_id}', 'Duration of Treatment {end_time - start_time}, Patient {patient_id}', new Date(0,0,0,0,0, {start_time}), new Date(0,0,0,0,0, {end_time})],
            """
    html_content += """
        ]);
        chart.draw(dataTable);
        }"""
    html_content += f"""
        </script>
        <div><p>Weighted Tardiness: {total_cost}; Number of Doctors: {numberOfDoctors}; Number of Patients: {numberOfPatients}; Runtime: {runTime}</p></div>
        <div id=\"example3.1\" style=\"height: 1000px;\"></div>
    """

    # Datei speichern
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html_content)

    print(f"HTML-Datei '{filename}' wurde erfolgreich erstellt.")
    webbrowser.open(filename)

#Schreibe relevante Daten in die Log.csv
def log_data_to_csv(file_path, doctors, greedy_solution, result_vns, meta_heuristic, isDeterministic, completion_time, log_file_path="Log.csv"):
    # Aktuelles Datum und Zeit abrufen
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Weighted Tardiness aus der Greedy-Lösung extrahieren
    weighted_tardiness_greedy = greedy_solution[1]

    #Identifiziere ob Eintrag ein Deterministischer Durchlauf war
    if isDeterministic:
        yesNo = "Yes"
    else:
        yesNo = "No"

    # Daten für die CSV-Datei vorbereiten
    data = [now, file_path, doctors, weighted_tardiness_greedy, meta_heuristic, result_vns, yesNo, completion_time]

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
            writer.writerow(["Datum und Zeit", "filePath", "Doktoren", "Weighted Tardiness after Opening","Used Meta-heuristic", "Weighted Tardiness after Meta-Heuristic", "Deterministic", "Completion Time in seconds"]) #Header schreiben
        writer.writerow(data)

    print(f"Daten wurden in '{log_file_path}' gespeichert.")

#Gib Anzahl der Patienten zurück
def get_number_of_patients(schedule_dict):

    max_patient_id = 0
    for patient_data in schedule_dict.values():
        for row in patient_data:
            patient_id = row[0]
            max_patient_id = max(max_patient_id, patient_id)

    return max_patient_id