import flowArcFirstTry as eh
import Neighbourhoods as nh
import classes
import visualization
import Console



filePath, doctors, runTime = Console.executeConsole()
instance = eh.map_patient_data(filePath, doctors)
result = eh.opening_heuristic_greedy(instance)


print(result)

result_vns = nh.general_vns(result[0], result[1], ["N1", "N2", "N3"], time_limit = runTime)
print(result_vns[0])

visualization.visualize_schedule(result_vns[0], result_vns[1], result_vns[2])

print(f"Tardiness: {result_vns[1]}")

print(result_vns[2])

visualization.log_data_to_csv(filePath, len(result_vns[0]), result, result_vns[1], 'Variable Neighborhood Search', True, result_vns[2])