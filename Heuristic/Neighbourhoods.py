import itertools
import copy
import visualization

def test(loesung, instance):
    test, tardiness = berechne_neuen_ablaufplan(loesung,instance)
    visualization.visualize_schedule_perDoc(test, tardiness, instance.doctors, len(instance.patients))
    print(loesung)
    print(instance)

#Zugriff über: aufgeteilt = one_array_per_doc(schedule);
"""Folgendermaßen sieht der Output aus: {1: [(486, 505, 3, 1), (505, 533, 5, 1), (533, 546, 10, 1), (546, 561, 12, 1), (561, 572, 17, 1), (572, 587, 18, 1), (587, 604, 16, 1), (604, 614, 22, 1), (614, 625, 25, 1), (625, 649, 27, 1), (649, 659, 31, 1), (659, 678, 33, 1), (678, 701, 37, 1), (701, 723, 41, 1), (723, 733, 43, 1), (733, 753, 45, 1), (753, 768, 48, 1), (768, 779, 51, 1), (779, 789, 53, 1), (789, 794, 54, 1), (794, 808, 56, 1)], 2: [(486, 508, 2, 2), (508, 531, 6, 2), (531, 547, 8, 2), (547, 560, 13, 2), (560, 584, 15, 2), (584, 604, 21, 2), (604, 623, 23, 2), (623, 644, 26, 2), (644, 658, 29, 2), (658, 675, 32, 2), (675, 693, 35, 2), (693, 717, 39, 2), (717, 742, 42, 2), (742, 756, 46, 2), (756, 774, 49, 2), (774, 799, 52, 2), (799, 813, 57, 2)], 3: [(486, 498, 1, 3), (498, 513, 4, 3), (513, 532, 7, 3), (532, 541, 9, 3), (541, 550, 11, 3), (550, 574, 14, 3), (574, 590, 20, 3), (590, 604, 19, 3), (604, 628, 24, 3), (628, 648, 28, 3), (648, 666, 30, 3), (666, 677, 34, 3), (677, 689, 36, 3), (689, 699, 38, 3), (699, 724, 40, 3), (724, 742, 44, 3), (742, 761, 47, 3), (761, 785, 50, 3), (785, 803, 55, 3)]}"""
def one_array_per_doc(loesung):

    # Finde die maximale Arzt-ID, um die Größe des Arrays zu bestimmen
    max_arzt_id = max(tupel[3] for tupel in loesung)

    # Erstelle eine Liste von leeren Listen für jeden Arzt
    ergebnisse = [[] for _ in range(max_arzt_id)]

    for start_zeit, end_zeit, patient, arzt in loesung:
        ergebnisse[arzt - 1].append((start_zeit, end_zeit, patient, arzt))  # Arzt-ID - 1 für Index

    return ergebnisse


def berechne_neuen_ablaufplan(schedule, instanz):

    arzt_zuordnung = one_array_per_doc(schedule)  # Wandelt den Ablaufplan in eine Liste von Listen um
    print(arzt_zuordnung)
    best_Schedule = copy.deepcopy(arzt_zuordnung)
    overallTardiness = 0

    for arzt_index in range(len(arzt_zuordnung)): # Iteriere über die Indizes der Ärzte
        if arzt_zuordnung[arzt_index]: # Überprüfe ob der Arzt Patienten hat
            patienten_liste = arzt_zuordnung[arzt_index]
            patienten_indizes = list(range(len(patienten_liste)))
            arzt_id = patienten_liste[0][3] # Ermittle die Arzt-ID aus dem ersten Tupel

            weightedTardinessDoc = weighted_tardiness_per_doc(patienten_liste, instanz)
            print(weightedTardinessDoc)

            for index_patient1, index_patient2 in itertools.combinations(patienten_indizes, 2):
                new_Solution = tausche_patienten(patienten_liste, index_patient1, index_patient2, instanz, arzt_id)
                new_Tardiness = weighted_tardiness_per_doc(new_Solution, instanz)

                if new_Tardiness < weightedTardinessDoc:
                    print("Bessere Loesung gefunden")
                    print(new_Tardiness)
                    print(new_Solution)
                    weightedTardinessDoc = new_Tardiness
                    best_Schedule[arzt_index] = new_Solution
                    best_Schedule[arzt_index] = sorted(best_Schedule[arzt_index], key=lambda x: x[0])
        print(f"weightedTardinessDoc: {weightedTardinessDoc}")            
        overallTardiness = overallTardiness + weightedTardinessDoc
    print(f"overallTardiness:{overallTardiness}")
    return best_Schedule, overallTardiness


def weighted_tardiness_per_doc(ablaufplan, instanz):
    gesamte_verspaetung = 0

    for start_zeit, end_zeit, patient_id, _ in ablaufplan:
        patient_index = patient_id - 1
        due_date = instanz.due_dates[patient_index]
        weight = instanz.weights[patient_index]
        

        verspaetung = max(0, start_zeit - due_date)
        gewichtete_verspaetung = verspaetung * weight
        gesamte_verspaetung += gewichtete_verspaetung

    return gesamte_verspaetung


def tausche_patienten(alte_loesung, index_patient1, index_patient2, instanz, arzt):
    neue_loesung = []
    arzt_id = alte_loesung[0][3]
    arzt_verfuegbarkeit = 0

    # Patienten vor den zu tauschenden Patienten kopieren
    for i in range(min(index_patient1, index_patient2)):
        neue_loesung.append(alte_loesung[i])
        arzt_verfuegbarkeit = alte_loesung[i][1]

    # Patienteninformationen abrufen
    patient_id1 = alte_loesung[index_patient1][2]
    patient_id2 = alte_loesung[index_patient2][2]

    release_time1 = instanz.patients[patient_id1-1][0]  # -1 für Indexzugriff
    bearbeitungszeit1 = instanz.patients[patient_id1-1][1]
    due_date1 = instanz.due_dates[patient_id1-1]

    release_time2 = instanz.patients[patient_id2-1][0]
    bearbeitungszeit2 = instanz.patients[patient_id2-1][1]
    due_date2 = instanz.due_dates[patient_id2-1]

    # Ersten Patienten tauschen und einplanen
    start_zeit1 = max(arzt_verfuegbarkeit, release_time2)  # Release-Zeit des ZWEITEN Patienten beachten!
    if start_zeit1 > due_date2 + 120:  # Due-Date des ZWEITEN Patienten beachten!
        print("Tausch war nicht möglich")
        return alte_loesung  # Tausch nicht möglich

    end_zeit1 = start_zeit1 + bearbeitungszeit2  # Bearbeitungszeit des ZWEITEN Patienten!
    neue_loesung.append((start_zeit1, end_zeit1, patient_id2, arzt))
    arzt_verfuegbarkeit = end_zeit1

    # Zweiten Patienten tauschen und einplanen
    start_zeit2 = max(arzt_verfuegbarkeit, release_time1)  # Release-Zeit des ERSTEN Patienten beachten!
    if start_zeit2 > due_date1 + 120:  # Due-Date des ERSTEN Patienten beachten!
        print("Tausch war nicht möglich")
        return alte_loesung  # Tausch nicht möglich

    end_zeit2 = start_zeit2 + bearbeitungszeit1  # Bearbeitungszeit des ERSTEN Patienten!
    neue_loesung.append((start_zeit2, end_zeit2, patient_id1, arzt))
    arzt_verfuegbarkeit = end_zeit2

     # Verbleibende Patienten kopieren und einplanen (KORRIGIERT)
    for i in range(len(alte_loesung)):
        if i != index_patient1 and i != index_patient2:  # Überspringe die bereits getauschten Patienten
            patient_id = alte_loesung[i][2]
            release_time = instanz.patients[patient_id - 1][0]
            bearbeitungszeit = instanz.patients[patient_id - 1][1]
            due_date = instanz.due_dates[patient_id - 1]

            start_zeit = max(arzt_verfuegbarkeit, release_time)
            if start_zeit > due_date + 120:
                print("Tausch war nicht möglich")
                return alte_loesung

            end_zeit = start_zeit + bearbeitungszeit
            neue_loesung.append((start_zeit, end_zeit, patient_id, arzt))
            arzt_verfuegbarkeit = end_zeit

    return neue_loesung