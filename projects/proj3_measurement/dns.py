import subprocess
import json
def run_dig(hostname_filename, output_filename, dns_query_server=None):
	with open(hostname_filename, 'r') as fp:
	 	hostnames = []
	 	line = fp.readline()
	 	while line != "":
	 		#print(line)
	 		hostnames += [line.split("\n")[0]]
	 		line = fp.readline()
	# hostnames = hostname_filename
		all_digs = []
		for host in hostnames:
			print(host)
			if dns_query_server == None:
				output = subprocess.check_output("dig +trace +tries=1 +nofail " + host + " 2>&1", shell=True)
				dig_dict = parse_no_dns_server(host, output)
				# print(output)
				all_digs += [dig_dict]
			else:
				output = subprocess.check_output("dig " + host + " @" + dns_query_server + " 2>&1", shell=True)
				# print(output)
				dig_dict = parse_with_dns_server(host, output)
				all_digs += [dig_dict]

		print(all_digs)

	with open(output_filename, 'w') as fp:
		json.dump(all_digs, fp)

		
def parse_no_dns_server(host, output):
	lines = output.split("\n")
	dig_dict = {}
	dig_dict["Name"] = host
	queries = []
	success = False
	current_dict = {}
	for i in range(2, len(lines)):
		tokens = lines[i].split()
		if len(tokens) <= 1:
			continue
		if tokens[1] == "Received":
			current_dict["Time"] = tokens[-2]
			queries += [current_dict]
			current_dict = {}
			continue
		elif tokens[0] == ";" or tokens[0] == ";;":
			continue
		current_answer = {}
		current_answer["Queried name"] = tokens[0]
		current_answer["Data"] = tokens[4]
		current_answer["Type"] = tokens[3]
		if tokens[3] == "A":
			success = True
		current_answer["TTL"] = tokens[1]
		if "Answers" not in current_dict:
			current_dict["Answers"] = []
		current_dict["Answers"] += [current_answer]
	if success:
		dig_dict["Success"] = True
		dig_dict["Queries"] = queries
	return dig_dict

def parse_with_dns_server(host, output):
	data = output.split("SECTION:")
	name_parts = data[1].split(';')[1].split('.')
	name = name_parts[0] + "." + name_parts[1]
	host_to_queries = {}
	host_to_queries['Name'] = name
	success = True
	answers = data[2].split(';;')[0]
	info = data[2].split(';;')[1:]
	for a in answers.split('\n'):
		if a == "":
			continue
		tokens = a.split()
		ans = tokens[0]
		ttl = tokens[1]
		typ = tokens[2]
		if tokens[3] != 'A':
			success = False
			break
		data = tokens[4]
		if 'Queries' not in host_to_queries:
			host_to_queries['Queries'] = [{}]
			host_to_queries['Queries'][0]['Answers'] = [{'Queried name': ans, 'Data': data, 'Type': typ, 'TTL': ttl}]
		else:
			i = len(host_to_queries['Queries'])
			host_to_queries['Queries'][0]['Answers'] += [{'Queried name': ans, 'Data': data, 'Type': typ, 'TTL': ttl}]
	if success:
		time = info[0].split()[2]
		host_to_queries['Success'] = success
		host_to_queries['Queries'][0]['Time'] = time
	else:
		host_to_queries['Name'] = host_to_queries['Name'].split('\\')[0]
		host_to_queries['Success'] = success
	return host_to_queries

#print(run_dig(["google.com"], "dig_ouput_test.json"))

# def get_average_ttls(filename):

# def get_average_times(filename):

# def generate_time_cdfs(json_filename, output_filename):


# def count_different_dns_responses(filename1, filename2):

run_dig('part3_test_host_filename.txt', 'placeholder.txt', '8.8.8.8')
