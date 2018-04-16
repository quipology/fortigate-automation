__author__ = 'Bobby Williams'

import argparse, sys, os, re, random, time
import paramiko
import threading
import getpass

#===========#
# Functions #
#===========#


def print_menu():
	print(30 * '-' + 'MENU' + 30 * '-')
	print('1.) Download configs from all firewalls (recommended)')
	print('2.) Create a new address object')
	print('3.) Add an existing address object to an existing address object-group')
	print('4.) Create a new service object')
	print('5.) Create a new firewall policy/rule')
	print('6.) Mimic an existing address object\'s policy membership')
	print('7.) *Switch to another VDOM (Current VDOM is {})'.format(vdom.capitalize()))
	print('8.) Exit')
	print('-' * 64)
def initiate_config_update(config=None):
	print('Downloading the running configuration from the devices.')
	print('Please wait..')
	time_start = time.time()
	threads = []
	for i in config:
		t = threading.Thread(target=get_current_configs, args=(config[i][2], config[i][0], config[i][1]))
		threads.append(t)
		t.start()
	for i in threads:
		i.join()
	time_stop = time.time()
	total_time = (time_stop - time_start) / 60
	total_time = str(total_time)
	total_time = total_time[:4] 
	print('Download of configurations complete!')
	print('Total time to download all configs = {} minutes'.format(total_time))
def get_current_configs(ip, filename, devicename):
  #--------------------------------------------
  #  SSH to device and grab the latest configs:
  #--------------------------------------------
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
		ssh.connect(ip, username=user, password=pwd, port=22)
	except:
		print('SSH connection failed - check authentication..')
	session = ssh.invoke_shell()
	time.sleep(2)
	print('Starting configuration download from {}..'.format(devicename))
	output = session.recv(65535)
	time.sleep(1.3)
	session.send("show | grep ''\n")
	time.sleep(1.3)
	while session.recv_ready():
		output += session.recv(65535)
		time.sleep(1.3)
	with open(filename, 'w') as fo:
		fo.write(output)
	session.send('exit\n')
	print('Configuration download from {} is complete!'.format(devicename))
	ssh.close()
def src_file_chk():
	# Check that config source files are present:
	while True:
		fw_config_file_names = ['GBTS_MFGGBTS01F.txt', 'GBTS_MFGGBTS02F.txt', 'GBTS_MFGGBTS03F.txt', 'GBTS_MFGGBTS04F.txt', 'GBTS_MFGGBTS05F.txt', 'GBTS_MFGGBTS06F.txt']
		valid_files = []
		missing_files = []
		file_check = os.listdir('device_configs')
		for i in file_check:
			if i in fw_config_file_names:
				valid_files.append(i)
		time.sleep(1)
		if len(valid_files) != 6:
			for i in fw_config_file_names:
				if i not in valid_files:
					missing_files.append(i)
			for i in missing_files:
				print("{} is missing from local dir 'device_configs'".format(i))
			print('Initiating config download..')
			initiate_config_update(config=fw_config)
			time.sleep(1)
		else:
			break
def gen_uuid():
  #----------------
  #  Generate UUID:
  #----------------
	uuid_pool = '0123456789abcdef'
	uuid_pool = list(uuid_pool)
	uuid_octet1 = random.sample(uuid_pool, 8)
	uuid_octet1 = ''.join(uuid_octet1)
	uuid_octet2 = random.sample(uuid_pool, 4)
	uuid_octet2 = ''.join(uuid_octet2)
	uuid_octet3 = random.sample(uuid_pool, 4)
	uuid_octet3 = ''.join(uuid_octet3)
	uuid_octet4 = random.sample(uuid_pool, 4)
	uuid_octet4 = ''.join(uuid_octet4)
	uuid_octet5 = random.sample(uuid_pool, 12)
	uuid_octet5 = ''.join(uuid_octet5)
	uuid = '{}-{}-{}-{}-{}'.format(uuid_octet1, uuid_octet2, uuid_octet3, uuid_octet4, uuid_octet5)
	return uuid
def add_addr_obj_to_objgrp(vdom=None, config=None):
  #-----------------------------------------------
  #  Add existing object to existing object-group:
  #-----------------------------------------------
	# Get object name:
	addr_obj_name = raw_input("Enter address object name(s) separated by commas: ")
	while ' ' in addr_obj_name:
		print('No spaces allowed..commas only (ex. abc,def,..)')
		addr_obj_name = raw_input("Enter address object name(s) separated by commas: ")
	addr_obj_names = addr_obj_name.split(',')
	
	# Get object-group name:
	print("What are the name(s) of the object group(s) you'd like to add the object(s) to (separated by commas)?: ")
	obj_grp = raw_input("> ")
	while ' ' in obj_grp:
		print('No spaces allowed..commas only (ex. abc,def,..)')
		print("What are the name(s) of the object group(s) you'd like to add the object(s) to (separated by commas)?: ")
		obj_grp = raw_input("> ")
	obj_grp_names = obj_grp.split(',')

	for i in config:
		with open(config[i][0], 'r') as fi:
			data = fi.read()
			pattern = r'config vdom\r\nedit {}(\n|\r)(.*\n|\r)+?config web-proxy global'.format(vdom.capitalize())
			vdom_data = re.search(pattern, data, flags=re.IGNORECASE)
			if vdom_data:
				vdom_data = vdom_data.group()
				# Loop through each object-group:
				for grp in obj_grp_names:
					obj_grp_data_pattern = r'    edit "{}"(\n|\r)(.*\n|\r)+?    next'.format(grp)
					obj_grp_data = re.search(obj_grp_data_pattern, vdom_data)
					if obj_grp_data:
						obj_grp_data = obj_grp_data.group()
						lines = obj_grp_data.splitlines()
						new_lines = []
						for x in lines:
							if 'set member' in x:
								# Loop through each address object:
								for obj in addr_obj_names:
									x += ' "{}"'.format(obj)
								new_lines.append(x)
							else:
								new_lines.append(x)
						with open(config[i][3]+config[i][1]+'_{}.txt'.format(vdom.capitalize()), 'a') as fo:
							fo.write('\n\n\n')
							fo.write('config firewall addrgrp\n')
							for y in new_lines:
								fo.write('{}\n'.format(y))
							fo.write('next\n')
							fo.write('end\n')
					else:
						with open(config[i][3]+config[i][1]+'_{}.txt'.format(vdom.capitalize()), 'a') as fo:
							fo.write('\n\n\n')
							fo.write('No object-group found for this VDOM\n')
			else:
				with open(config[i][3]+config[i][1]+'_{}.txt'.format(vdom.capitalize()), 'a') as fo:
					fo.write('\n\n\n')
					fo.write('No object-group found for this VDOM\n')

	print("Execution Complete - check '\\generated' for the results.")
def create_addr_obj(vdom=None, config=None):
	# Get object name:
	addr_obj_name = raw_input("Enter address object name: ")
	while ' ' in addr_obj_name:
		print('No spaces allowed..')
		addr_obj_name = raw_input("Enter address object name: ")

	# Get object subnet:
	addr_obj_subnet = raw_input("Enter IP/subnet mask (ex. 1.1.1.0/24): ")
	while '/' not in addr_obj_subnet:
		print("Invalid, please enter in prefix format")
		addr_obj_subnet = raw_input("Enter IP/subnet mask (ex. 1.1.1.0/24): ")

	#Add a comment/description:
	addr_obj_comment = raw_input('Enter comment/description: ')

	# Add new object to an object group?:
	obj_grp = None
	while True:
		print("Do you wish to add this new object to an existing address object group? (y/n)")
		add_to_obj_grp = raw_input("> ")
		if add_to_obj_grp.upper() == 'Y':
			print("What's the name of the address object group you'd like to add this new object to?: ")
			obj_grp = raw_input("> ")
			break
		elif add_to_obj_grp.upper() == 'N':
			break
		else:
			print("Invalid selection..")
	
	# If adding to an existing object group:
	if obj_grp != None:
		for i in config:
			uuid = gen_uuid()
			with open(config[i][3]+config[i][1]+'_{}.txt'.format(vdom.capitalize()), 'a') as fo:
				fo.write('\n\n\n')
				fo.write('config firewall address\n')
				fo.write(' edit "{}"\n'.format(addr_obj_name))
				fo.write('  set uuid {}\n'.format(uuid))
				fo.write('  set comment "{}"\n'.format(addr_obj_comment))
				fo.write('  set subnet {}\n'.format(addr_obj_subnet))
				fo.write('next\n')
				fo.write('end\n')

			with open(config[i][0], 'r') as fi:
				data = fi.read()
				pattern = r'config vdom\r\nedit {}(\n|\r)(.*\n|\r)+?config web-proxy global'.format(vdom.capitalize())
				vdom_data = re.search(pattern, data, flags=re.IGNORECASE)
				if vdom_data:
					vdom_data = vdom_data.group()
					obj_grp_data_pattern = r'    edit "{}"\r(.*\n|\r)+?    next'.format(obj_grp)
					obj_grp_data = re.search(obj_grp_data_pattern, vdom_data)
					if obj_grp_data:
						obj_grp_data = obj_grp_data.group()
						lines = obj_grp_data.splitlines()
						new_lines = []
						for x in lines:
							if 'set member' in x:
								new_lines.append(x +' "{}"'.format(addr_obj_name))
							else:
								new_lines.append(x)
						# Remove any blank spaces at the beginning of any new lines:
						new_lines = [t.replace('    ', '') for t in new_lines]
						new_lines = [t.replace('        ', '') for t in new_lines]
						with open(config[i][3]+config[i][1]+'_{}.txt'.format(vdom.capitalize()), 'a') as fo:
							fo.write('\n')
							fo.write('config firewall addrgrp\n')
							for y in new_lines:
								fo.write(' {}\n'.format(y))
							fo.write('end\n')
	# If not adding to an existing object group:
	else:
		for i in config:
			uuid = gen_uuid()
			with open(config[i][3]+config[i][1]+'_{}.txt'.format(vdom.capitalize()), 'a') as fo:
				fo.write('\n\n\n')
				fo.write('config firewall address\n')
				fo.write(' edit "{}"\n'.format(addr_obj_name))
				fo.write('  set uuid {}\n'.format(uuid))
				fo.write('  set comment "{}"\n'.format(addr_obj_comment))
				fo.write('  set subnet {}\n'.format(addr_obj_subnet))
				fo.write('next\n')
				fo.write('end\n')
	
	print("Execution Complete - check '\\generated' for the results.")		 
def create_service_obj(vdom=None, config=None):
  #------------------------------
  #  Create a new service object:
  #------------------------------
	# Default values:
	set_color = 'set color 1\n'
	
	# Get object name:
	srv_obj_name = raw_input("Enter service object name: ")
	while ' ' in srv_obj_name:
		print('No spaces allowed..')
		srv_obj_name = raw_input("Enter service object name: ")

	# Get comment:
	srv_obj_comment = raw_input('Enter service object comment: ')

	# Get protocol:
	while True:
		print('Select service protocol:')
		print('a) - TCP')
		print('b) - UDP')
		print('c) - TCP & UDP')
		srv_protocol = raw_input('> ')
		if srv_protocol.upper() == 'A':
			srv_protocol = 'A'
			# Get TCP port/port range:
			print("What's the TCP destination port or port range?")
			print("(Ex. 443 | 8080-8081):")
			srv_tcp_port = raw_input('> ')
			srv_udp_port = None
			break
		elif srv_protocol.upper() == 'B':
			srv_protocol = 'B'
			# Get UDP port/ port range:
			print("What's the UDP destination port or port range?")
			print("(Ex. 500 or 7000-7500):")
			srv_udp_port = raw_input('> ')
			srv_tcp_port = None
			break
		elif srv_protocol.upper() == 'C':
			srv_protocol = 'C'
			# Get TCP port/port range:
			print("What's the TCP destination port or port range?")
			print("(Ex. 443 or 8080-8081):")
			srv_tcp_port = raw_input('> ')
			# Get UDP port/ port range:
			print("What's the UDP destination port or port range?")
			print("(Ex. 500 or 7000-7500):")
			srv_udp_port = raw_input('> ')
			break
		else:
			print('Invalid selection, try again..')

	# Add new object to an object group?:
	obj_grp = None
	while True:
		print("Do you wish to add this new service object to an existing object group? (y/n)")
		add_to_obj_grp = raw_input("> ")
		if add_to_obj_grp.upper() == 'Y':
			print("What's the name of the service object group you'd like to add this new object to?: ")
			obj_grp = raw_input("> ")
			break
		elif add_to_obj_grp.upper() == 'N':
			break
		else:
			print("Invalid selection..")
	
	# If adding to an existing object group:
	if obj_grp != None:
		for i in config:
			with open(config[i][3]+config[i][1]+'_{}.txt'.format(vdom.capitalize()), 'a') as fo:
				fo.write('\n\n\n')
				fo.write('config firewall service custom\n')
				fo.write(' edit "{}"\n'.format(srv_obj_name))
				fo.write('  set comment "{}"\n'.format(srv_obj_comment))
				fo.write(set_color)
				if srv_tcp_port:
					fo.write('    set tcp-portrange {}\n'.format(srv_tcp_port))
				if srv_udp_port:
					fo.write('set udp-portrange {}\n'.format(srv_udp_port))
				fo.write('next\n')
				fo.write('end\n')

			with open(config[i][0], 'r') as fi:
				data = fi.read()
				pattern = r'config vdom\r\nedit {}(\n|\r)(.*\n|\r)+?config web-proxy global'.format(vdom.capitalize())
				vdom_data = re.search(pattern, data, flags=re.IGNORECASE)
				if vdom_data:
					vdom_data = vdom_data.group()
					obj_grp_data_pattern = r'    edit "{}"(\n|\r)(.*\n|\r)+?    next'.format(obj_grp)
					obj_grp_data = re.search(obj_grp_data_pattern, vdom_data)
					if obj_grp_data:
						obj_grp_data = obj_grp_data.group()
						lines = obj_grp_data.splitlines()
						new_lines = []
						for x in lines:
							if 'set member' in x:
								new_lines.append(x +' "{}"'.format(srv_obj_name))
							else:
								new_lines.append(x)
						# Remove any blank spaces at the beginning of any new lines:
						new_lines = [t.replace('    ', '') for t in new_lines]
						new_lines = [t.replace('        ', '') for t in new_lines]
						with open(config[i][3]+config[i][1]+'_{}.txt'.format(vdom.capitalize()), 'a') as fo:
							fo.write('\n')
							fo.write('config firewall service group\n')
							for y in new_lines:
								fo.write(' {}\n'.format(y))
							fo.write('end\n')
					else:
						with open(config[i][3]+config[i][1]+'_{}.txt'.format(vdom.capitalize()), 'a') as fo:
							fo.write('\n\n\n')
							fo.write('No object-group found for this VDOM\n')

	else:
		for i in config:
			with open(config[i][3]+config[i][1]+'_{}.txt'.format(vdom.capitalize()), 'a') as fo:
				fo.write('\n\n\n')
				fo.write('config firewall service custom\n')
				fo.write(' edit "{}"\n'.format(srv_obj_name))
				fo.write('  set comment "{}"\n'.format(srv_obj_comment))
				fo.write(set_color)
				if srv_tcp_port != None:
					fo.write('  set tcp-portrange {}\n'.format(srv_tcp_port))
				if srv_udp_port != None:
					fo.write('  set udp-portrange {}\n'.format(srv_udp_port))
				fo.write('next\n')
				fo.write('end\n')
	print("Execution Complete - check '\\generated' for the results.")
def create_policy(vdom=None, config=None, counter=None):
	# Get Flow info based on VDOM:
	if vdom.upper() == 'TRUSTED':
		while True:
			print('--------------------')
			print('| Choose your Flow: |')
			print('--------------------')
			print('a)  Trusted to Cores')
			print(' -->(port1)[FW](port5)-->\n')
			print('b)  Cores to Trusted')
			print(' -->(port5)[FW](port1)-->')
			flow = raw_input('> ')
			if flow.upper() == 'A':
				flow = 'A'
				break
			elif flow.upper() == 'B':
				flow = 'B'
				break
			else:
				print('Invalid selection..')
		# Determine flow based on user selection:		
		if flow == 'A':
			src_port = 'port1'
			dst_port = 'port5'
		elif flow == 'B':
			src_port = 'port5'
			dst_port = 'port1'
	elif vdom.upper() == 'UNTRUSTED':
		while True:
			print('--------------------')
			print('| Choose your Flow: |')
			print('--------------------')
			print('a)  Untrusted to Cores')
			print(' -->(port2)[FW](port6)-->\n')
			print('b)  Cores to Untrusted')
			print(' -->(port6)[FW](port2)-->')
			flow = raw_input('> ')
			if flow.upper() == 'A':
				flow = 'A'
				break
			elif flow.upper() == 'B':
				flow = 'B'
				break
			else:
				print('Invalid selection..')
		# Determine flow based on user selection:		
		if flow == 'A':
			src_port = 'port2'
			dst_port = 'port6'
		elif flow == 'B':
			src_port = 'port6'
			dst_port = 'port2'
	elif vdom.upper() == '3RDPARTY':
		while True:
			print('--------------------')
			print('| Choose your Flow: |')
			print('--------------------')
			print('a)  3rdParty to Cores')
			print(' -->(port3)[FW](port7)-->\n')
			print('b)  Cores to 3rdparty')
			print(' -->(port7)[FW](port3)-->')
			flow = raw_input('> ')
			if flow.upper() == 'A':
				flow = 'A'
				break
			elif flow.upper() == 'B':
				flow = 'B'
				break
			else:
				print('Invalid selection..')
		# Determine flow based on user selection:		
		if flow == 'A':
			src_port = 'port3'
			dst_port = 'port7'
		elif flow == 'B':
			src_port = 'port7'
			dst_port = 'port3'
	elif vdom.upper() == 'DATACENTER':
		while True:
			print('--------------------')
			print('| Choose your Flow: |')
			print('--------------------')
			print('a)  DataCenter to Cores')
			print(' -->(port4)[FW](port8)-->\n')
			print('b)  Cores to DataCenter')
			print(' -->(port8)[FW](port4)-->')
			flow = raw_input('> ')
			if flow.upper() == 'A':
				flow = 'A'
				break
			elif flow.upper() == 'B':
				flow = 'B'
				break
			else:
				print('Invalid selection..')
		# Determine flow based on user selection:		
		if flow == 'A':
			src_port = 'port4'
			dst_port = 'port8'
		elif flow == 'B':
			src_port = 'port8'
			dst_port = 'port4'
	elif vdom.upper() == 'DC2':
		while True:
			print('--------------------')
			print('| Choose your Flow: |')
			print('--------------------')
			print('a)  DC2 to Cores')
			print(' -->(port9)[FW](port10)-->\n')
			print('b)  Cores to DC2')
			print(' -->(port10)[FW](port9)-->')
			flow = raw_input('> ')
			if flow.upper() == 'A':
				flow = 'A'
				break
			elif flow.upper() == 'B':
				flow = 'B'
				break
			else:
				print('Invalid selection..')
		# Determine flow based on user selection:		
		if flow == 'A':
			src_port = 'port9'
			dst_port = 'port10'
		elif flow == 'B':
			src_port = 'port10'
			dst_port = 'port9'

	# Get policy details:	
	print("Enter the source address object name(s) seperated by commas:")
	sources = raw_input('> ')
	sources = sources.split(',')
	print("Enter the destination address object name(s) seperated by commas:")
	destinations = raw_input('> ')
	destinations = destinations.split(',')
	print("Enter the destination service object name(s) seperated by commas:")
	services = raw_input('> ')
	services = services.split(',')
	while True:
		print('------------------------')
		print("| Select policy action: |")
		print('------------------------')
		print('a) accept')
		print('b) deny')
		action = raw_input('> ')
		if action.upper() == 'A':
			action = 'accept'
			break
		elif action.upper() == 'B':
			action = 'deny'
			break
		else:
			print('Invalid selection..')
	print("Enter a comment for this policy:")
	comment = raw_input('> ')



	# Iterate through all firewalls:
	for i in config:
		new_id = None
		with open(config[i][0], 'r') as fi:
			data = fi.read()
			pattern = r'config vdom\r\nedit {}(\n|\r)(.*\n|\r)+?config firewall local-in-policy'.format(vdom.capitalize())
			vdom_data = re.search(pattern, data, flags=re.IGNORECASE)
			if vdom_data:
				vdom_data = vdom_data.group()
				policy_pattern = r'config firewall policy\r(.*\n|\r)+?end(\n|\r)'
				policy_data = re.search(policy_pattern, vdom_data)
				if policy_data:
					policy_data = policy_data.group()
					policy_ids = re.findall(r'    edit \d{1,5}', policy_data)
					if policy_ids:
						policy_ids = [x.replace('    ', '') for x in policy_ids]
						ids = []
						for x in policy_ids:
							x = x.split()
							ids.append(int(x[1]))
						new_id = max(ids) + (1 + counter)
		
		if new_id != None:
			with open(config[i][3]+config[i][1]+'_{}.txt'.format(vdom.capitalize()), 'a') as fo:
				fo.write('\n\n\n')
				fo.write('config firewall policy\n')
				fo.write(' edit {}\n'.format(new_id))
				fo.write('  set srcintf "{}"\n'.format(src_port))
				fo.write('  set dstintf "{}"\n'.format(dst_port))
				fo.write('  set srcaddr')
				for source in sources:
					fo.write(' "{}"'.format(source))
				fo.write('\n')
				fo.write('  set dstaddr')
				for destination in destinations:
					fo.write(' "{}"'.format(destination))
				fo.write('\n')
				fo.write('  set service')
				for service in services:
					fo.write(' "{}"'.format(service))
				fo.write('\n')
				fo.write('  set action {}\n'.format(action))
				fo.write('  set schedule "always"\n')
				fo.write('  set logtraffic all\n')
				fo.write('  set comments "{}"\n'.format(comment))
				fo.write('next\n')
				fo.write('end\n')
	print("Execution Complete - check '\\generated' for the results.")
def obj_policy_mimic(vdom=None, config=None):
   #-------------------------------------------------------
   #  Mimic an existing address object's policy membership:
   #-------------------------------------------------------

	# Get object name of source:
	print("What's the name of the source address object that you wish to mimic its policy membership?")
	source_policy = raw_input('> ')
	mimic = '"{}"'.format(source_policy)

	# Get list of address objects you wish to add to source object's policies:
	print("What are the names of the address objects you wish to add to source object's policies (seperated by commas)?")
	objs_to_add = raw_input('> ')
	while ' ' in objs_to_add:
		print('No spaces allowed..commas only (ex. abc,def,..)')
		print("What are the names of the address objects you wish to add to source object's policies (seperated by commas)?")
		objs_to_add = raw_input('> ')
	objs_to_add = objs_to_add.split(',')

	replacer = mimic
	for i in objs_to_add:
		replacer += ' "{}"'.format(i)

	for i in config:
		with open(config[i][0], 'r') as fi:
			data = fi.read()
			pattern = r'config vdom\r\nedit {}(\n|\r)(.*\n|\r)+?config firewall local-in-policy'.format(vdom.capitalize())
			vdom_data = re.search(pattern, data, flags=re.IGNORECASE)
			if vdom_data:
				vdom_data = vdom_data.group()
				fw_policies = re.search(r'config firewall policy\r|\n(.*\r|\n)+?config firewall local-in-policy', vdom_data)
				if fw_policies:
					fw_policies = fw_policies.group()
					pattern = r'edit \d{2,}[\s\S]*?next'
					found = re.findall(pattern, fw_policies)
					if source_policy not in fw_policies:
						print('"{}" not found on {} in VDOM {}'.format(source_policy, config[i][1], vdom.capitalize()))
					if found:
						for x in found:
							if mimic in x:
								y = x.replace(mimic, replacer)
								with open(config[i][-1]+config[i][1]+'_.txt', 'a') as fo:
									fo.write('\n\n')
									fo.write(y)
									fo.write('\nend\n')
	print("Execution Complete - check '\\generated' for the results.")							


	





#==============#
# Main Program #
#==============#
if __name__ == '__main__':

	version = '1.02'
	parser = argparse.ArgumentParser(description='[GBT Fortigate CLI Config Generator v{}]\nContact: Bobby Williams'.format(version), formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument('vdom', metavar='<vdom>', help='Enter the VDOM you wish to generate configs for:\n(3rdparty, datacenter, dc2, trusted, untrusted)')
	args = parser.parse_args()

	# Assign initial VDOM to a variable:
	vdom = args.vdom

	# Check to see if a valid VDOM was chosen:
	vdoms = ['3RDPARTY', 'DATACENTER', 'DC2', 'TRUSTED', 'UNTRUSTED']
	if args.vdom.upper() not in vdoms:
		print('Invalid VDOM, exiting..')
		sys.exit()

	# Check for 'device_configs' and 'generated' dir:
	is_dir = os.listdir('.')
	if 'device_configs' not in is_dir:
		print("Local 'device_configs' directory is missing, exiting..")
		sys.exit()
	elif 'generated' not in is_dir:
		print("Local 'generated' directory is missing, exiting..")
		sys.exit()
	# Firewall config source files:
	fw_config = {}
	fw_config['01'] = ['device_configs\\XXX01F.txt', 'XXX01F', '10.160.0.1', 'generated\\']
	fw_config['02'] = ['device_configs\\XXX02F.txt', 'XXX02F', '10.160.0.2', 'generated\\']
	fw_config['03'] = ['device_configs\\XXX03F.txt', 'XXX03F', '10.160.0.3', 'generated\\']
	fw_config['04'] = ['device_configs\\XXX04F.txt', 'XXX04F', '10.160.0.3', 'generated\\']
	fw_config['05'] = ['device_configs\\XXX05F.txt', 'XXX05F', '10.160.0.4', 'generated\\']
	fw_config['06'] = ['device_configs\\XXX06F.txt', 'XXX06F', '10.160.0.5', 'generated\\']

	# Get user credentials for SSH'ing into firewalls:
	user = raw_input('Username: ')
	pwd = getpass.getpass('Password: ')

	# Check if firewall configs are in 'device_configs' subdirectory:
	src_file_chk()

	counter = 0 # Counter for new policy rule(s) id.
	while True:
		# Display menu:
		print_menu()
		menu_selection = raw_input('> ')

		# Process selection:
		if menu_selection == '1':
			initiate_config_update(config=fw_config)
		elif menu_selection == '2':
			create_addr_obj(vdom=vdom, config=fw_config)
		elif menu_selection == '3':
			add_addr_obj_to_objgrp(vdom=vdom, config=fw_config)
		elif menu_selection == '4':
			create_service_obj(vdom=vdom, config=fw_config)
		elif menu_selection == '5':
			create_policy(vdom=vdom, config=fw_config, counter=counter)
			counter += 1
		elif menu_selection == '6':
			obj_policy_mimic(vdom=vdom, config=fw_config)
		elif menu_selection == '7':
			while True:
				print('Select a VDOM:')
				print('1.) Trusted')
				print('2.) Untrusted')
				print('3.) DataCenter')
				print('4.) DC2')
				print('5.) 3rdParty')
				choice = raw_input('> ')
				if choice == '1':
					vdom = 'trusted'
					print('{} is now the current VDOM'.format(vdom.capitalize()))
					break
				elif choice == '2':
					vdom = 'untrusted'
					print('{} is now the current VDOM'.format(vdom.capitalize()))
					break
				elif choice == '3':
					vdom = 'datacenter'
					print('{} is now the current VDOM'.format(vdom.capitalize()))
					break
				elif choice == '4':
					vdom = 'dc2'
					print('{} is now the current VDOM'.format(vdom.capitalize()))
					break
				elif choice == '5':
					vdom = '3rdparty'
					print('{} is now the current VDOM'.format(vdom.capitalize()))
					break
				else:
					print('Invalid selection, please try again..')
		elif menu_selection == '8':
			sys.exit()
		else:
			print('Invalid selection, please try again..')
	
