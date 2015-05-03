import paramiko,sys,re,time,subprocess,getpass,os

def main(argv):	
	os.system('cls') #on windows
	mins = 0
	
	print ("\n[info] "+time.strftime("%d/%m/%Y %H:%M:%S") +"\n")
	
	print ("""
                               _       _   
 ______  _____   ___  ___ _ __(_)_ __ | |_ 
|_  /\ \/ / __| / __|/ __| '__| | '_ \| __|
 / /  >  < (__  \__ \ (__| |  | | |_) | |_ 
/___|/_/\_\___| |___/\___|_|  |_| .__/ \__|
                                |_|        
""")

	user = raw_input('Username : ')
	passwd = getpass.getpass(prompt='Password : ')

	while mins != -1:
		q = raw_input('script #>')
		if "quit" in q:
			mins = -1
		if "exit" in q:
			mins = -1
		else:
			case(q)
	
	os.system('cls') #on windows

def sshto(host,command):
	output = ''
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(host, username=user, password=passwd)

	print  "\n[info] executing : \""+ command + "\" on " + nslookup(host)
	stdin, stdout, stderr = ssh.exec_command(command)
	stdin.flush()
	for line in stdout:
		# print line.strip('\n')
		output+=str(line)
	ssh.close()
	return output

def sshtoEnter(host,command):
	output = ''
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(host, username=user, password=passwd)

	print  "\n[info] executing : \""+ command + "\" on " + nslookup(host)
	chan = ssh.invoke_shell()
	chan.send(command + '\n')
	time.sleep(5)
	chan.send('\r')
	ssh.close()

	print "[info] completed : \""+ command + "\" on " + nslookup(host)

	return output

def checkBadlink(interface,output):
	for line in output.splitlines():
		if interface in line:
			if 'down' in line:
				print "[Response] interface is down"
			elif 'up' in line:
				print "[Response] interface is up"
	print('\n')

def nslookup(ip):
	output = ""
	ns = subprocess.Popen(["nslookup",ip], stdout=subprocess.PIPE)
	outns, err = ns.communicate()
	for line in outns.splitlines():
		if 'Non-existent' in line:
			output = ip
			break
		elif 'Name' in line:
			for ls in line.split():
				if 'Name' not in ls:
					output = ls
	return output

def checkNotRespon(ip):
	ping = subprocess.Popen(["ping",ip], stdout=subprocess.PIPE)
	print "\n[info] Pinging... "+nslookup(ip)
	outping, err = ping.communicate()
	fail = outping.count('Request timed out')+outping.count('Destination net unreachable')
	if fail==4:
		print "[Response] Device is not reachable"
	elif fail>=1:
		print "[Response] Possibly link is intermittent"
	else:
		print "[Response] Device is reachable"

	for line in outping.splitlines():
		if "Minimum" in line:
			print "[Response] "+line

	print('\n')

def checkBGP(peer,output):
	for line in output.splitlines():
		if peer in line:
			if 'Active' or 'Idle' in line:
				print "[Response] BGP is down"
			elif 'Admin' in line:
				print "[Response] BGP is administratively down"
			else:
				print "[Response] BGP is up"
	print('\n')

def checkErr(output):
	for line in output.splitlines():
		if "counters" in line:
			if "never" in line:
				print "[Response] Link has never been cleared"
			else:
				print "[Response] It has been " + line.split()[-1] + " since last counter cleared"
		if "input" in line:
			print "[Response] Link is seeing :-\n[Response] " + line
		if "output" in line:
			print "[Response] " + line
	pass


################################################################################
#							 options and selections.
################################################################################

def ping(expres):
	# ping 128.58.XXX.XXX
	checkNotRespon(expres.split()[-1])

def stats(expres):
	#stats se0/0/0 128.58.XXX.XXX
	checkErr(sshto(expres.split()[-1],'sh int '+expres.split()[1]+' | i inte|err'))

def clearcounter(expres):
	#clear counter se0/0 128.58.XXX.XXX
	sshtoEnter(expres.split()[-1],'clear counter ' + expres.split()[-2])

def case(semantic):
	if "stats" in semantic:
		stats(semantic)
	elif "clear counter" in semantic:
		clearcounter(semantic)
	elif "ping" in semantic:
		ping(semantic)
	elif "\r" in semantic:
		pass
	else:
		print "[info] sorry but feature "+semantic+" has not been implemented"
	

user = ' '
passwd = ' '
ippat = re.compile('[0-9]+(?:\.[0-9]+){3}')

if __name__ == "__main__":
	main(sys.argv)


	# case("stats se0/0/0 128.58.246.214")
	# case("clear counter se0/0/0 128.58.246.214")
	# case("stats se0/0/0 128.58.246.214")
	# print sshto('128.58.246.214','sh log')
	# case ("ping 128.58.246.214")
	#time.sleep(60) #60 Second Sleep