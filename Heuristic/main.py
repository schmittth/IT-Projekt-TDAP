import flowArcFirstTry as eh
import Neighbourhoods as nh
import classes

file_path = 'new_test_instances.json'
doctors = 8
instance = eh.map_patient_data(file_path, doctors)
result = eh.opening_heuristic_greedy(instance)

#print(result)

result_vns = nh.general_vns(result[0], result[1], ["N1", "N2", "N3"], time_limit=90, no_improvement_limit=1000)

result_sa = nh.simulated_annealing(result[0], result[1], time_limit=90, Imax=3000, cooling_rate=0.999, start_temperature=10)
print(result_vns[0])
print(result_sa[0])

print(f"VNS Tardiness: {result_vns[1]}")
print(f"SA Tardiness: {result_sa[1]} with temperature: {result_sa[2]}")

print(result_sa[0])

print(nh.weighted_tardiness_per_doc(result_sa[0], 1)+nh.weighted_tardiness_per_doc(result_sa[0], 2))
