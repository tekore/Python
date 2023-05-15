import os,sys,re,subprocess,pty,getpass,time,argparse,threading,select
from queue import Queue

class Prerun:
    def files(self):
        hostfile, commandfile = [i for i in os.listdir("./") if i.endswith(".hosts")], [i for i in os.listdir("./") if i.endswith(".commands")]
        if len(hostfile or commandfile) >1:
            sys.exit("Multiple .hosts or .commands files in the current directory, please only allow one of each.")
        elif len(hostfile) <1:
            sys.exit("No .hosts file in the current directory.")
        elif len(commandfile) <1:
            sys.exit("No .commands file in the current directory.")
        return(hostfile, commandfile)

    def pre(self):
        hostfile, commandfile = self.files()
        hostfile, commandfile = open(hostfile[0], "r"), open(commandfile[0], "r")
        queue = Queue()
        print("\n### Pre Run Summary ###\nThe following commands will be ran against the following hosts:\n\n# Commands:")
        for i in commandfile:
            print(i)
        print("# Hosts:")
        for i in hostfile:
            print("-",i, end="")
            queue.put(i, block=True, timeout=None)
        hostfile.close()
        commandfile.close()
        try:
            self.password = getpass.getpass('\nThis script will now cycle through the hosts and run the commands.\n\nEnter your password to commit these changes:')
            self.pfile()
        except KeyboardInterrupt:
            print("KeyboardInterrupt, Exiting..")
            Postrun().cleanup()
        return(self.password, queue)

    def pfile(self):
        for i in os.listdir("./"):
            if i.endswith(".pfile"):
                os.remove(i)
        pfile = open("./.p.pfile", "w")
        pfile.write(self.password)

class Host:
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
        raise RuntimeError("Sudo Timeout for host: %s" %(self.host))

    def connect(self):
        with lock:
            self.host = queue.get(block=True)
        commandfile = open([i for i in os.listdir("./") if i.endswith(".commands")][0], "r")
        master, slave = pty.openpty()
        self.pin = os.fdopen(master, "w")
        print("Initialising SSH connection to host: %s" %(self.host))
        process = subprocess.Popen('sshpass -f .p.pfile ssh -o ConnectTimeout=60 -o StrictHostKeyChecking=no <DOMAIN>\\\\%s@%s' %(args.u,self.host),stdin=slave,stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True, universal_newlines=1, bufsize=0)
        try:
            process.stdout.readlines(1)[0]
        except:
            errorhosts.append(self.host)
            process.terminate()
            self.clean()
            return(print("ERROR: Unable to connect to host: %s" %(self.host)))
        print("SSH Successful for host: %sSudoing up for host: %s" %(self.host,self.host))
        try:
            self.sudo(process)
        except RuntimeError:
            skippedhosts.append("%s" %(self.host))
            process.terminate()
            self.clean()
            return(print("SUDO TIMEOUT! for host: %sHost didn't sudo up within 30 seconds. Skipping Host." %(self.host)))
        print("Sudo successful for host: %sRunning commands.." %(self.host))
        for i in commandfile:
            self.pin.write(i + "\n")
        commandfile.close()
        self.pin.write("exit\nexit\n")
        file = open("Debug-output", "a")
        while args.debug:
            line = process.stdout.readline()
            file.write(line)
            if not line:
                break
        print("Success! Closing SSH session for host %s" %(self.host))
        process.communicate()
        donehosts.append("%s" %(self.host))
        self.clean()

    def clean(self):
        self.pin.close()
        sema.release()

class Postrun:
    def summary(self):
        print("\n### Post Run Summary ###\n")
        if errorhosts:
            print("Unable to SSH to the following hosts:")
            for i in errorhosts:
                print("-",i, end="")
        if skippedhosts:
            print("Skipped the following hosts:")
            for i in skippedhosts:
                print("-",i, end="")
        if donehosts:
            print("Successfully ran against the following hosts:")
            for i in donehosts:
                print("-",i, end="")
        self.cleanup()

    def cleanup(self):
        sys.stdout.flush()
        for i in os.listdir("./"):
            if i.endswith(".pfile"):
                os.remove(i)
        sys.exit()

def args():
    parser = argparse.ArgumentParser(prog='SSH automation script', description="SSH automation script. For this script to work it requires two files; One for hosts with one host per line and one for commands with one command per line. If you wish to run against a host multiple times, include it multiple times in the .hosts file.")
    parser.add_argument('-u', type=str, required=True, help="The user to SSH as")
    parser.add_argument('--debug', action='store_true', help="Write all output to a file called 'Debug-output'")
    parser.add_argument('--threads', type=int, default=5, help="Number of cocurrent threads, the default is 5 (Use With Caution!)")
    args = parser.parse_args()
    return(args)

if __name__ == '__main__':
    args = args()
    donehosts, skippedhosts, errorhosts, files, jobs, lock, sema = [], [], [], [], [], threading.Lock(), threading.Semaphore(value=args.threads)
    password, queue = Prerun().pre()
    while not queue.empty():
        try:
            sema.acquire(blocking=True)
            t = threading.Thread(target=Host().connect, args=(), daemon=True)
            t.start()
            jobs.append(t)
            queue.task_done()
        except KeyboardInterrupt:
            print("KeyboardInterrupt, Exiting..")
            Postrun().cleanup()
    while any(i.is_alive() for i in jobs):
        print("\n### Waiting for all threads to complete their tasks ###\n")
        time.sleep(5)
    Postrun().summary()
