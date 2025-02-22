import flowArcFirstTry as eh
import Neighbourhoods as nh
import classes
import visualization

file_path = 'new_test_instances.json'
doctors = 2
instance = eh.map_patient_data(file_path, doctors)
result = eh.opening_heuristic_greedy(instance)


print(result)

result_vns = nh.general_vns(result[0], result[1], ["N1", "N2", "N3"], time_limit=90)
print(result_vns[0])

print(f"Tardiness: {result_vns[1]}")

print(result_vns[2])

visualization.log_data_to_csv(file_path, doctors, result, result_vns[1], 'Variable Neighborhood Search', True, result_vns[2])