from os import error
import numpy, json, sys

# globals
PATH="/Users/s.alirezadamghani/Desktop/sdamghan_vtr/ODIN_II/regression_test/benchmark/"

ERRORs= {
	"args_num":"[ERROR]: The parse program needs a path to a task file in JSON format!\n",
	"json_type":"[ERROR]: Not a valid JSON file!"
}

bench_skip_list = {"DEFAULT"}
str_attr_list = {"test_name", "architecture", "input_blif", "verilog", "warnings"}

def open_jsons(task):
	""" open and load echmap and synthesis results JSON file """
	techmap_path = PATH + str(task['techmap']) + "/techmap_result.json"
	synth_path = PATH + str(task['synthesis']) + "/synthesis_result.json"

	
	# load techmap results
	try:
		with open(techmap_path, "r") as techmap:
			techmap_json = json.load(techmap)
	except:
		print(ERRORs["json_type"] + f" ({techmap_path})")
		raise

	# load synthesis results
	try:
		with open(synth_path, "r") as synth:
			synth_json = json.load(synth)
	except:
		print(ERRORs["json_type"] + f" ({synth_path})")
		raise

	return techmap_json, synth_json


def compare(techmap, synth):
	""" compare techmap and synthsis results for each benchmark """
	
	comparison_results={}

	for bt in enumerate (techmap):
		comparison_record={}
		benchmark_name = bt[1]
		tech_bench_info = techmap[benchmark_name]
		synth_bench_info = synth[benchmark_name]

		if (benchmark_name not in synth):
			# a benchmark that didn't existed in synthesis results
			comparison_record["STATUS"] = "NEW"
			# only show the tech results not the comparison
			for attr in enumerate(tech_bench_info):
				attr_name = attr[1]
				# add a single comparision record
				comparison_record[attr_name] = tech_bench_info[attr_name]

		elif benchmark_name not in bench_skip_list:
			# we have the benchmark in both techmap and synthesis
			comparison_record["STATUS"] = "COMPARED"
			# show the difference plus both tech and synth results
			for attr in enumerate(tech_bench_info):
				attr_name = attr[1]
				attr_new_value={}

				if (attr_name in tech_bench_info) and (attr_name in synth_bench_info):
					if attr_name not in str_attr_list:
						tech_val = int(tech_bench_info[attr_name])
						synth_val= int(synth_bench_info[attr_name])				
						diff_val = tech_val - synth_val
						diff_percent = -1 if (synth_val == 0) else (diff_val / synth_val) * 100
						attr_new_value = {
							"Percent%": str('{:0.1f}%'.format(diff_percent)), 
							"Diff": str(diff_val), 
							"Techmap": str(tech_val), 
							"Synthesis": str(synth_val)
						}
					else:
						attr_new_value = {
							"Techmap":tech_bench_info[attr_name],
							"Synthesis":synth_bench_info[attr_name]
							}

				elif attr_name in synth_bench_info:
					attr_new_value = {"Synthesis":synth_bench_info[attr_name]}
				else:
					attr_new_value = {"Techmap":tech_bench_info[attr_name]}

				# add a single comparision record
				comparison_record[attr_name] = attr_new_value	

		# adding to the comparision results which will go to the json file			
		comparison_results[benchmark_name] = comparison_record



	print(benchmark_name, comparison_results.keys)
	# iterate over missed benchmarks in synthesis results which are not available in techmap results
	for bt in enumerate (synth):
		comparison_record={}
		benchmark_name = bt[1]	
		if (benchmark_name not in comparison_results) and (benchmark_name not in bench_skip_list):
			print(f"====>{benchmark_name}")
			# a benchmark that not exist in techmap results
			comparison_record["STATUS"] = "OLD"
			synth_bench_info = synth[benchmark_name]
			# only show the synth results not the comparison
			for attr in enumerate(synth_bench_info):
				attr_name = attr[1]
				comparison_record[attr_name] = synth_bench_info[attr_name]
			
		# adding to the comparision results which will go to the json file			
		comparison_results[benchmark_name] = comparison_record


	return (comparison_results)










# Main body
if __name__ == "__main__":
	# verify num of command line args
	if len(sys.argv) != 2:
		print(ERRORs["args_num"])
		exit()

	tasks=[]
	task_path = sys.argv[1]
	try:
		with open(task_path, 'r') as t:
			tasks = json.load(t)
	except:
		print(ERRORs["json_type"] + f" ({task_path})")
		exit()


	for task in enumerate (tasks):
		task_name = task[1]
		# open and load json files
		try:
			techmap, synth = open_jsons(tasks[task_name])
			print(f"Task {task_name} JSON files successfully loaded!\n")
			
		except:
			print(f"Task {task_name} JSON files load was unsuccessful!\n")

		to_json = compare(techmap, synth)

		with open(f"./data/{task_name}_compared.json", "r+") as output:
			serialized_json = json.dumps(to_json, indent=4, sort_keys=False)
			output.truncate(0)
			output.write(serialized_json)

