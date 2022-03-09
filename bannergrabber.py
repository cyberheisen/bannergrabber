#!/usr/bin/python3
import re
from os.path import exists
import sys
from subprocess import check_output

number_of_nmap = 0

def readfile(filename):
    f = open(filename,"r")
    data = f.readlines()
    return data

def parse_targets(data):
    # Creating a dict object with each port as the key. Ip addresses are key values
    targets = {}
    for d in data:
        if '#' not in d[0]:
            ip_address = []
            ip_address.append(d.split()[3])
            port = d.split()[2]
            if port not in targets:
                targets[port] = ip_address
            else:
                targets[port].extend(ip_address)
    return targets

def create_nmap_scans(targets):
    # We will generate an nmap scan command for each port with the required targets
    nmap_commands = []
    for port in targets:
        scan_targets = []
        for ip in targets[port]:
            scan_targets.append(ip)
        command = "nmap -sV -Pn -p" + str(port) + " " + ' '.join(scan_targets)
        nmap_commands.append(command)
        number_of_nmap = len(nmap_commands)
    print("%s total Nmap commands to be executed" % number_of_nmap)
    return nmap_commands

def run_nmap(command):
    #this runs an instance of nmap as a subprocess of this script
    results = check_output(command,shell=True)
    return results

def get_banner(results):
    # We now parse the resulting nmap stdout which has been captured to extract the specific values required
    banner_results = []
    regex_port='(\d\d?\d?\d?\d?)\/tcp'
    regex_banner = 'tcp\s(open|filtered).*'
    regex_host = '.*'
    results_array = results.decode("utf-8").split("Nmap scan report for ")

    for host in results_array[1:]:
        target = re.search(regex_host, host).group(0)
        port = re.search(regex_port, host).group(1)
        banner = ""
        #regex was acting quirky, so bare with me here...
        banner_array = re.search(regex_banner, host).group(0).split()
        length = len(banner)
        service = banner_array[2]
        count = 3
        while count < len(banner_array):
            banner = banner + " " + banner_array[count]
            count = count +1

        results = str(target) + "," + str(port) + "," + service + "," + str(banner)
        banner_results.append(results)
    return banner_results

def output_to_csv(banner,filename):
    # now we just print to the screen and $profit
    newfile = filename.split('.')
    newfile = newfile[0] + ".csv"
    if not exists(newfile):
        print("creating output file: %s" % newfile)
        f = open(newfile,'w')
        f.write("HOST,PORT,SERVICE,BANNER\n")
    else:
        f = open(newfile,'a')
        for results in banner:
            f.write(results + "\n")
    f.close()
    return

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        count = 1
        # Read the masscan data file
        data = readfile(filename)

        # parse those targets by port
        targets = parse_targets(data)

        # Generate nmap commands for the targets based on the port to be queried
        nmap_commands = create_nmap_scans(targets)     
        number_of_nmap = len(nmap_commands)
        for command in nmap_commands:
            print("(%i of %i) executing: %s" % (count,number_of_nmap,command))
            #run the required nmap scans, one for each port
            results = run_nmap(command)
            # get the banner information
            banner = get_banner(results)
            #output the nmap results to the stdout
            output_to_csv(banner,filename)
            count = count + 1
        
    else:
        print("usage: %s: MASSCAN OUTPUT FILE" % sys.argv[0])
    exit()
