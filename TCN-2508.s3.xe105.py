from datetime import datetime
import re 

# Opening the log file
with open('/var/log/auth.log') as f:
	logs = f.readlines()
	

def parse_log(log_line):
	# This ensures the script processes only lines containing the string 'COMMAND'
	if "COMMAND" not in log_line:
		return None
		
	parts = log_line.split()
	
	# Extracting timestamp : datetime module to parse the timestamp 
	timestamp = datetime.fromisoformat(parts[0])
	
	#Extracting executing user (word after sudo)
	if "sudo:" in parts:
		sudo_index = parts.index("sudo:")
		executing_user = parts[sudo_index + 1]
		
	# Extracting executed command
	for i, p in enumerate(parts):
		if p.startswith("COMMAND"):
			cmd_index = i
	# The command could be split across two or more elements if it originally contained a space after using split()
	first = parts[cmd_index].split('=')[1] #returns the index of the part sratting with 'COMMAND'
	rest = parts[cmd_index + 1:] 
	cmd = " ".join([first] + rest) # combines the rest of the command 
	
	# returns a tuple of 3 elements
	return timestamp, executing_user, cmd


def parse_passwd(log_line):
	
	parts = log_line.split()
	
	# Extracting timestamp : datetime module to parse the timestamp 
	timestamp = datetime.fromisoformat(parts[0])
	
	# Case 1: sudo password change
	
	if "COMMAND=" in log_line and "passwd" in log_line:
		if "sudo:" in parts:
			sudo_index = parts.index("sudo:")
			executing_user = parts[sudo_index + 1]
		else:
			executing_user = None
            
		cmd_index = next((i for i, p in enumerate(parts) if p.startswith("COMMAND")), None)
		first = parts[cmd_index].split('=',1)[1]
		rest = parts[cmd_index + 1:]
		cmd = " ".join([first] + rest)
		target_user = rest[-1] if rest else None
		
		return timestamp, executing_user, target_user, cmd
        
       # Case 2: self-password change
	elif 'passwd' in log_line and 'password changed for' in log_line:
		match = re.search(r"password changed for (\S+)", log_line)
		if match:
			target_user = match.groups() 
			
            # Executing user is the system user running passwd
            # This is the user right after the timestamp
			executing_user = parts[1]
			
			cmd = "passwd"
			
			return timestamp, executing_user, target_user, cmd


def parse_su_log(log_line):
    
	if "su" not in log_line or "session opened for user" not in log_line:
		return None
	
	parts = log_line.split()
    
    # Extract timestamp
	timestamp = datetime.fromisoformat(parts[0])
    
	# Extract target and executing user using regex
	match = re.search(r"session opened for user (\S+)\(.*\) by (\S+)\(.*\)", log_line)
	if match:
		target_user, executing_user = match.groups()
		cmd = "su"
		
		return timestamp, executing_user, target_user, cmd
		
	return None

	

def command_usage():
	for log in logs:
		parsed = parse_log(log)
		#check if the tuple is not empty
		if parsed:
			# Unpack the tuple
			timestamp, executing_user, cmd = parsed
			print(f"Time: {timestamp} | Executing User: {executing_user} | Command: {cmd}")
			


def added_users():
	for log in logs:
		if 'adduser' in log or 'useradd' in log:
			parsed = parse_log(log)
			if parsed:
				# unpack tuple
				timestamp, executing_user, cmd = parsed
				# Extract new user (-1 ensures we print the last thing which is the new user)
				new_user = cmd.split()[-1]
				print(f"Time: {timestamp} | Executing User: {executing_user} | New User: {new_user} | Command: {cmd}")
			


def deleted_users():
	for log in logs:
		if 'deluser' in log or 'userdel' in log:
			parsed = parse_log(log)
			if parsed:
				# unpack tuple
				timestamp, executing_user, cmd = parsed
				# Extract new user (-1 ensures we print the last thing which is the new user)
				deleted_user = cmd.split()[-1]
				print(f"Time: {timestamp} | Executing User: {executing_user} | Deleted User: {deleted_user} | Command: {cmd}")
			

def passwd_ch():
	for log in logs:
		if 'passwd' in log:
			parsed = parse_passwd(log)
			if parsed:
				# unpack tuple
				timestamp, executing_user, target_user, cmd = parsed
				
				print(f"Time: {timestamp} | Executing User: {executing_user} | Target User: {target_user} | Command: {cmd}")
			

def su_usage():
	for log in logs:
		parsed = parse_su_log(log)
		if parsed:
			timestamp, executing_user, target_user, cmd = parsed
			print(f"Time: {timestamp} | Executing User: {executing_user} | Target User: {target_user} | Command: {cmd}")


def sudo_usage():
    for log in logs:
        if "sudo:" not in log or "COMMAND=" not in log:
            continue  # skip lines that are not sudo commands
        
        parsed = parse_log(log)
        if parsed:
            timestamp, executing_user, cmd = parsed
            print(f"Time: {timestamp} | Executing User: {executing_user} | Command: {cmd}")


def sudo_failed():
    for log in logs:
        if "sudo:" not in log or "COMMAND=" not in log:
            continue  # skip lines that are not sudo commands
        
        # Look for failure indicators usually authetication failures or incorrect passwords
        if "authentication failure" in log.lower() or "incorrect password" in log.lower():
            parsed = parse_log(log)
            if parsed:
                timestamp, executing_user, cmd = parsed
                print(f"ALERT! Failed sudo attempt!")
                print(f"Time: {timestamp} | Executing User: {executing_user} | Command: {cmd}\n")





def main():
	while True:
		print("\n1. Extract command usage \n2. New Users\n3. Deleted Users \n4. Password Changes \n5. SU Usage \n6. SUDO Usage \n7. Failed SUDO Usage \n8. Exit")
		choice = input("\nEnter your choice: ")
		
		if choice == '1':
			print("=== All sudo commands ===")
			command_usage()
		elif choice == '2':
			print("\n=== New Users ===")
			added_users()
		elif choice == '3':
			print("\n=== Deleted Users ===")
			deleted_users()
		elif choice == '4':
			print("\n=== Password Changes ===")
			passwd_ch()
		elif choice == '5':
			print("\n=== SU Usage ===")
			su_usage()
		elif choice == '6':
			print("\n=== SUDO Usage ===")
			sudo_usage()
		elif choice == '7':
			print("\n=== Failed SUDO usage ===")
			sudo_failed()
		elif choice	== '8':
			break 
		else:
			print("Invalid choice!")
		
		
main()	
		
		
		
		
		
		
		
		
		
