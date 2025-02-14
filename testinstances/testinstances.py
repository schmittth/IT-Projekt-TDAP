import random
import json

# Dringlichkeitsstufen und zugehörige Werte
URGENCY_LEVELS = {
    1: {"weight": 1, "max_wait_time": 120},  # Wenig dringend
    2: {"weight": 2, "max_wait_time": 60},   # Normal
    3: {"weight": 3, "max_wait_time": 15},   # Dringend
    4: {"weight": 4, "max_wait_time": 0},    # Sehr dringend
}

# Generierung von Patientendaten für eine Testinstanz
def generate_patient_data(patient_id): 
    urgency_level = random.randint(1, 4)
    arrival_time_minutes = random.randint(0, 480)  # Zufällige Ankunftszeit in Minutes statt HH:MM

    return {
        "patient_id": patient_id,
        "arrival_time": arrival_time_minutes,                              
        "urgency_level": urgency_level,                                     # u     
        "weight": URGENCY_LEVELS[urgency_level]["weight"],                  # w
        "max_wait_time": URGENCY_LEVELS[urgency_level]["max_wait_time"],    # δ_j | d_j = r_j + δ_j
        "expected_processing_time": random.randint(5, 30),                  # p_a_j
        "realized_processing_time": random.randint(10, 40),                 # p_e_j
    }

# 50 Instanzen mit je max. 10 Patienten generieren
def generate_test_instances(num_instances=10, max_patients_per_instance=10): 
    test_instances = []
    patient_id = 1 
    for _ in range(num_instances):
        num_patients = random.randint(1, max_patients_per_instance) 
        instance = [generate_patient_data(patient_id + i) for i in range(num_patients)]
        patient_id += num_patients
        test_instances.append(instance)
    return test_instances

# Speichern der Testinstanzen in eine JSON-Datei
def save_to_file(data, filename="test_instances.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

# Main-Methode
if __name__ == "__main__":
    test_instances = generate_test_instances()
    
    save_to_file(test_instances)
    
    print("Testinstanz:")
    print(json.dumps(test_instances[0], indent=4))
