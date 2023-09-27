import os,sys,socket,requests,argparse,getpass
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

# Notes:
# - Precheck run, check the directory is writable, ufw is installed (precheck def)
# - Download the VYOS image from the webpage (no api but there is a weblink)
# - RHEL api, download the correct image (Poll and wait for the build to be ready)

def vyos_download():
    url = 'https://legacy-lts-images.vyos.io/1.2.9-S1/vyos-1.2.9-S1-cloud-init-vmware.ova'
    filename = os.path.basename(url)
    dl_path = os.path.expanduser('~') + "/vyos"
    os.makedirs(dl_path, exist_ok=True)
    abs_path = os.path.join(dl_path, filename)
    print("Downloading the Vyos image to %s" %(abs_path))
    with requests.get(url) as r, open(abs_path, "wb") as f:
        f.write(r.content)

def rhel_download():
    print("")

def truenas_download():
    print("")

def openfirewall():
    os.popen("echo '%s' | sudo -S ufw allow to 0.0.0.0/0 port %s" %(password,args.p))
    return(print("Firewall port: %s opened." %(args.p)))
    
def closefirewall():
    os.popen("echo '%s' | sudo -S ufw --force delete allow %s" %(password,args.p))
    return(print("Firewall port: %s closed." %(args.p)))

def serve():
    HOST_IP = socket.gethostbyname(socket.gethostname())
    httpd = HTTPServer((HOST_IP, args.p), SimpleHTTPRequestHandler)
    os.environ['IP'] = HOST_IP
    print("Enviroment Variable set for: %s" %(os.getenv('IP')))
    print("WebServer is running on http://%s:%s" %(HOST_IP,args.p))
    httpd.serve_forever()

def main():
    vyos_download()
    rhel_download()
    openfirewall()
    try:
        serve()
    except KeyboardInterrupt:
        closefirewall()

def args():
    parser = argparse.ArgumentParser(prog='Image Download Automation', description="This scipt is designed to download and serve Vyos,RedHat and other Linux OS images.")
    megroup = parser.add_mutually_exclusive_group()
    parser.add_argument('--p', type=int,default=8000 ,help="Port for the webserver.")
    megroup.add_argument('--vyosonly', action='store_true', help="Only download the Vyos Image.")
    megroup.add_argument('--rhelonly', action='store_true', help="Only download the RHEL Image.")
    megroup.add_argument('--truenasonly', action='store_true', help="Only download the TrueNas Image.")
    return(parser.parse_args())

if __name__ == '__main__':
    args = args()
    password = getpass.getpass('Enter the sudo password to configure the firewall:')
    main()
