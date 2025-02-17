import webbrowser
import os
import re

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

#Visualisierung mit Google in HTML für Greedy
def visualize_schedule(schedule, total_cost, numberOfDoctors, numberOfPatients, basisfilename="Greedy_Loesung.html"):
    next_number = get_next_filename_number('./Loesungen', basisfilename)
    filename = os.path.join('./Loesungen', f"{basisfilename}_{next_number}.html")

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

        // Beispiel für das Hinzufügen von Daten zum Zeitplan
        dataTable.addRows(["""
    
    for start, end, patient, doctor in schedule:
        html_content += f"""
            ['Doctor {doctor}' , 'Patient {patient}', 'Duration of Treatment {end - start}, Patient {patient}', new Date(0,0,0,0,0, {start}), new Date(0,0,0,0,0, {end})],
        """
    html_content += """
        ]);
        chart.draw(dataTable);
        }"""
    html_content += f"""
        </script>
        <div><p>Weighted Tardiness: {total_cost}; Number of Doctors: {numberOfDoctors}; Number of Patients: {numberOfPatients}</p></div>
        <div id=\"example3.1\" style=\"height: 1000px;\"></div>
    """

    # Datei speichern
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html_content)

    print(f"HTML-Datei '{filename}' wurde erfolgreich erstellt.")
    webbrowser.open(filename)

def visualize_schedule_perDoc(schedule, total_cost, numberOfDoctors, numberOfPatients, basisfilename="N1_LS_Loesung.html"):
    next_number = get_next_filename_number('./Loesungen', basisfilename)
    filename = os.path.join('./Loesungen', f"{basisfilename}_{next_number}.html")

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

    for doc_schedule in schedule:  # Iteriere über die Ärzte
        for start, end, patient, doctor in doc_schedule:
            html_content += f"""
                ['Doctor {doctor}' , 'Patient {patient}', 'Duration of Treatment {end - start}, Patient {patient}', new Date(0,0,0,0,0, {start}), new Date(0,0,0,0,0, {end})],
            """

    html_content += """
        ]);
        chart.draw(dataTable);
        }"""
    html_content += f"""
        </script>
        <div><p>Weighted Tardiness: {total_cost}; Number of Doctors: {numberOfDoctors}; Number of Patients: {numberOfPatients}</p></div>
        <div id=\"example3.1\" style=\"height: 1000px;\"></div>
    """

    # Datei speichern
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html_content)

    print(f"HTML-Datei '{filename}' wurde erfolgreich erstellt.")
    webbrowser.open(filename)