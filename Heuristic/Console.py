import os


def executeConsole ():
    filePath, doctors = chooseInstanceAndDoctors()
    runTime = chooseRunTime()

    return filePath, doctors, runTime


def chooseInstanceAndDoctors ():
    print('Welche der vorhandenen Instanzen wollen sie importieren?')
    liste = liste_json_dateien()

    print('Folgende Instanzen wurden im Ordner gefunden:')
    for index, datei in enumerate(liste, start=1):
        print(f"{index}: {datei}")

    number = int(input())

    chosenInput = liste[number-1]

    print("Wie viel Doktoren arbeiten heute?")
    doctors = int(input())

    return(chosenInput, doctors)

def chooseRunTime():
    print('Welche Laufzeitbeschränkung (in sekunden) soll angewandt werden?')

    runTime = int(input())

    return runTime



def liste_json_dateien():

    json_dateipfade = []
    for datei in os.listdir():
        if datei.endswith(".json"):
            json_dateipfade.append(datei)  # relativen Dateipfad hinzufügen

    return json_dateipfade
