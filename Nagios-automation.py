import os,sys,re,subprocess,pty,getpass,time,argparse,json,threading,select
from queue import Queue
from subprocess import DEVNULL

#################################
#   Last updated - 28/04/2023   #
#################################

class Prerun:
    def __init__(self, monitoring_user, monitoring_secret, fixable_alerts):
        self.monitoring_user = monitoring_user
        self.monitoring_secret = monitoring_secret
        self.fixable_alerts = fixable_alerts

    def get_dump(self):
        print("Downloading JSON monitoring dump...")
        mprocess = subprocess.Popen("sshpass -f .p.pfile ssh -q -o StrictHostKeyChecking=no <DOMAIN>\\\\%s@<NAGIOS_HOST>.<DOMAIN> 'rm -f ./dump.* && wget -O dump.monitoring --no-check-certificate \"https://<NAGIOS_HOST>.<DOMAIN>:<PORT>/<REDACTED>?view_name=<REDACTED>&output_format=JSON&_username=%s&_secret=%s\" && cat dump.*' > mondump.json" %(args.u, self.monitoring_user, self.monitoring_secret), stdout=subprocess.DEVNULL,stderr=DEVNULL, shell=True, bufsize=0)
        mprocess.wait()
        print("Monitoring JSON dump has been downloaded.\nSearching for the Monitoring dump in the current directory..")
        p = [i for i in os.listdir("./") if i.endswith(".json")]
        if len(p) >1:
            sys.exit("Multiple .json files in the current directory, please only allow one.")
        elif len(p) <1:
            sys.exit("No .json files in the current directory.")
        file = open(p[0], 'r')
        mon_file = json.load(file)
        file.close()
        print("JSON file found: %s/%s" %(os.getcwd(),p[0]))
        return(mon_file)

    def build_dict(self):
        mon_file, stores = self.get_dump(), []
        for p in mon_file[1:]:
            stores.append(dict({"Store": p[1], "Host": p[2], "Alert": p[3], "Detail": p[4], "Alert Age": p[5], "Last checked": p[6]}))
        return(stores)

    def pre_summary(self, dict_list):
        file = open("Prerun_Summary_%s" %(time.strftime("%H:%M:%S", time.localtime())), "w+")
        file.write("### Monitoring Script Prerun Summary ###\n\nThe following stores will be accessed.")
        for i in dict_list:
                if args.critonly is True and re.search("CRIT", i.get("Detail")) and i['Alert'] in fixable_alerts:
                    file.write("\n%s\n- %s: %s %s" %(i['Store'], i['Host'], i['Alert'], i['Detail']))
                if args.critonly is False and i['Alert'] in fixable_alerts:
                    file.write("\n%s\n- %s: %s %s" %(i['Store'], i['Host'], i['Alert'], i['Detail']))
        file.close()
        print("\nThe file %s/%s has been created.\nPlease read this file to ensure you're happy with the changes before using the --commit flag." %(os.getcwd(),file.name))
        Postrun.cleanup(self)

    def pre(self):
        print("### Monitoring Script ###")
        self.pfile()
        dict_list = self.build_dict()
        alerts = list(set([i['Alert'] for i in dict_list]))
        if args.commit is False:
            self.pre_summary(dict_list)
        print("\n### Pre Run ###\nFixable Alerts:")
        for a in fixable_alerts:
            if args.critonly is True:
                print(a,"-", len([i for i in dict_list if i['Alert'] == a and (re.search("CRIT", i['Detail']))]))
            else:
                print(a,"-", len([i for i in dict_list if i['Alert'] == a]))
        print("\nThis script will now cycle through the stores and clear the above alerts.\n")
        try:
            for i in range(9,0,-1):
                print("Count down:", i, end='\r')
                time.sleep(1)
        except KeyboardInterrupt:
            print("KeyboardInterrupt, Exiting..")
            Postrun().cleanup()
        return(dict_list, alerts)

    def pfile(self):
        for i in os.listdir("./"):
            if i.endswith(".pfile"):
                os.remove(i)
        pfile = open("./.p.pfile", "w")
        pfile.write(password)

class Store:
    def varlog(self):
        self.pin.write("logrotate -f -v /etc/logrotate.conf; journalctl --vacuum-size=5M\n")

    def ddata(self):
        if self.host == '<REDACTED>':
            self.pin.write("<REDACTED>\n")
        elif self.host == '<REDACTED>':
            self.pin.write("<REDACTED>\n")
        else:
            print("Skipping %s alert '<REDACTED>', fix not implemented yet." %(self.host))
            skippedhosts.append("%s, %s, %s" %(self.store, self.host, self.alert))

    def wagent(self):
        self.pin.write("service <REDACTED> restart\n")

    def pd(self):
        self.pin.write("service <REDACTED> restart\n")

    def cdump(self):
        self.pin.write("cd <REDACTED>\n ls -la\n rm -r ./<REDACTED>\n ls -la\n")

    def makestore(self):
        n = re.split("<DOMAIN>j-|-\D", self.store, maxsplit=2)
        sshstore = self.host.strip('"')+".s"+n[1]
        return(sshstore)

    def sudo(self, process):
        timeout = time.time() + 30
        self.pin.write("sudo -p 'Enter pls\n")
        self.pin.write("' su\n")
        y = select.poll()
        y.register(process.stdout,select.POLLIN)
        while time.time() < timeout:
            while y.poll(1000):
                line = process.stdout.readline()
                if re.search("(?<!')Enter pls", line):
                    self.pin.write(password + "\n")
                    time.sleep(1)
                    self.pin.write("whoami\n")
                if re.search(r"root@", line):
                    return(process)
        raise RuntimeError("Sudo Timeout for store: %s" %(self.store))

    def connect(self):
        with lock:
            task = queue.get(block=True)
        self.store = task.get("Store")
        self.host =  task.get("Host")
        self.alert =  task.get("Alert")
        self.detail =  task.get("Detail")
        store = self.makestore()
        master, slave = pty.openpty()
        self.pin = os.fdopen(master, "w")
        print("\nInitialising SSH connection to %s:" %(store))
        process = subprocess.Popen('sshpass -f .p.pfile ssh -o ConnectTimeout=60 -o StrictHostKeyChecking=no <DOMAIN>\\\\%s@%s' %(args.u,store),stdin=slave,stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True, universal_newlines=1, bufsize=0)
        try:
            process.stdout.readlines(1)[0]
        except:
            errorhosts.append(store)
            process.terminate()
            self.clean()
            return(print("ERROR: Unable to connect to store: %s." %(store)))
        print("SSH Successful for store: %s.\nSudoing up for store: %s" %(store,store))
        try:
            self.sudo(process)
        except RuntimeError:
            skippedhosts.append("%s %s %s" %(self.store,self.host,self.alert))
            process.terminate()
            self.clean()
            return(print("SUDO TIMEOUT! for store: %s\nStore didn't sudo up within 30 seconds. Skipping Store." %(store)))
        print("Sudo successful for store: %s. Running commands.." %(store))
        menu = {'<REDACTED>' : self.ddata,
                '<REDACTED>' : self.wagent,
                'fs_/var/log' : self.varlog,
                '<REDACTED>' : self.cdump,
                '<REDACTED>' : self.pd
               }
        menu[self.alert]()
        self.pin.write("exit\nexit\n")
        file = open("Debug-output", "a")
        while args.debug:
            line = process.stdout.readline()
            file.write(line)
            if not line:
                break
        print("Success! Closing SSH session for store %s" %(store))
        process.communicate()
        donehosts.append("%s:  %s" %(store,self.alert))
        self.clean()

    def clean(self):
        self.pin.close()
        sema.release()

class Postrun:
    def create_file(self):
        file = open("Postrun_Summary_%s"%(time.strftime("%H:%M:%S", time.localtime())), "w+")
        files.append(file.name)
        file.write("### Monitoring Script Postrun Summary ###\n")
        if errorhosts:
            file.write("\nUnable to SSH to the following stores:\n")
            for r in errorhosts:
                file.write("- %s\n" %(r))
        if donehosts:
            file.write("\nFixed the following alerts:\n")
            for i in donehosts:
                file.write("- %s\n" %(i))
        if skippedhosts:
            file.write("\nSkipped the following hosts:\n")
            for i in skippedhosts:
                file.write("- %s\n" %(i))
        file.close()

    def summary(self):
        self.create_file()
        if files:
            print("\n### Summary ###\nNumber of alerts fixed: %s\nOutput files created:" % (len(donehosts)))
            for a in files:
                print("- ",os.getcwd()+"/"+a)
        self.cleanup()

    def cleanup(self):
        sys.stdout.flush()
        for i in os.listdir("./"):
            if i.endswith(".pfile"):
                os.remove(i)
        sys.exit()

def args():
    parser = argparse.ArgumentParser(prog='Monitoring automation script', description="This scipt is designed to download a JSON formatted dump from the main nagios instance, build a (thread safe) queue of all fixable monitoring alerts and SSH into each host to fix the alert.")
    parser.add_argument('-u', type=str, required=True, help="The user to SSH as")
    parser.add_argument('--critonly', action='store_true', help="Only action the critical alerts")
    parser.add_argument('--commit', action='store_true', help="Commmit the changes outlined in the Prerun Summary")
    parser.add_argument('--debug', action='store_true', help="Write all output to a file called 'Debug-output'")
    parser.add_argument('--threads', type=int, default=5, help="Number of cocurrent threads, the default is 5 (Use With Caution!)")
    args = parser.parse_args()
    return(args)

def buildqueue():
    for i in dict_list:
        if args.critonly is True and re.search("CRIT", i.get("Detail")) and i['Alert'] in fixable_alerts:
            queue.put(i, block=True, timeout=None)
        if args.critonly is False and i['Alert'] in fixable_alerts:
            queue.put(i, block=True, timeout=None)

if __name__ == '__main__':
    args = args()
    monitoring_user = "<REDACTED>"
    monitoring_secret = "<REDACTED>"
    fixable_alerts = ['<REDACTED>', 'fs_/var/log', '<REDACTED>', '<REDACTED>']
    password = getpass.getpass('Enter your password to enable the monitoring dump to be downloaded:')
    donehosts, skippedhosts, errorhosts, files, jobs, queue, lock, sema = [], [], [], [], [], Queue(), threading.Lock(), threading.Semaphore(value=args.threads)
    dict_list, alerts = Prerun(monitoring_user, monitoring_secret, fixable_alerts).pre()
    buildqueue()
    while not queue.empty():
        try:
            sema.acquire(blocking=True)
            t = threading.Thread(target=Store().connect, args=(), daemon=True)
            t.start()
            jobs.append(t)
            queue.task_done()
        except KeyboardInterrupt:
            print("KeyboardInterrupt, Exiting..")
            Postrun().cleanup()
    print("### Waiting for all threads to complete their tasks ###")
    for i in jobs:
        i.join()
    Postrun().summary()
