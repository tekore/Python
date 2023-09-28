import os,sys,socket,requests,argparse,getpass,time,shutil
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Notes:
# - Precheck run, check the directory is writable, ufw is installed (precheck def)
# - RHEL api, download the correct image (Poll and wait for the build to be ready)

def download(file_name, url):
    filename = os.path.basename(url)
    dl_path = os.path.expanduser('./') + "/downloads/"
    os.makedirs(dl_path, exist_ok=True)
    abs_path = os.path.join(dl_path, filename)
    print("Downloading %s to: %s" %(file_name, abs_path))
    with requests.get(url, stream=True) as r:
        with open(abs_path, 'wb') as file:
            total_size, chunk_size = int(r.headers.get('Content-Length')), 10240000
            for i, chunk in enumerate(r.iter_content(chunk_size=chunk_size)):
                c = i * chunk_size / total_size * 100
                file.write(chunk)
                sys.stdout.write(f"\rDownloading {file_name} {round(c, 4)}%")
                time.sleep(.1)
                sys.stdout.flush()

def firewall(command):
    if command == 'open':
        os.popen("echo '%s' | sudo -S ufw allow to 0.0.0.0/0 port %s" %(password,args.p))
        return(print("Firewall port: %s opened." %(args.p)))
    elif command == 'close':
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
    download('vyos', 'https://legacy-lts-images.vyos.io/1.2.9-S1/vyos-1.2.9-S1-cloud-init-vmware.ova')
    firewall('open')
    try:
        serve()
    except KeyboardInterrupt:
        firewall('close')

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
