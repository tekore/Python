import os,socket,time,requests,argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Notes:
# - Precheck run, check the directory is writable, ufw is installed (precheck def)
# - Download the VYOS image from the webpage (no api but there is a weblink)
# - RHEL api, download the correct image (Poll and wait for the build to be ready)
# - Shuts down the web server
# - Closes the ports on the firewall after the webserver has been shut down

def firewall():
    #os.popen("sudo ufw status")
    print(os.popen("sudo ufw status").read())
    print(os.popen("sudo ufw allow to 0.0.0.0/0 port 8000").read())
    print(os.popen("sudo ufw status").read())
    print(os.popen("sudo ufw --force delete allow 8000").read())
    return(print("Function to open/close firewall port: %s" %(args.p)))

def serve():
    HOST_IP = socket.gethostbyname(socket.gethostname())
    httpd = HTTPServer((HOST_IP, args.p), SimpleHTTPRequestHandler)
    os.environ['IP'] = HOST_IP
    print(os.getenv('IP'))
    firewall()
    print("WebServer is running on http://%s:%s" %(HOST_IP,args.p))
    httpd.serve_forever()

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
    serve()
#url = ""
#filename = os.path.basename(url)
#dl_path = os.path.join(print(os.path.expanduser('~')), "tmp")
#os.makedirs(dl_path, exist_ok=True)
#abs_path = os.path.join(dl_path, filename)
#with requests.get(url, stream=True) as r, open(abs_path, "wb") as f:
#    for chunk in r.iter_content(chunk_size=1024):
#        f.write(chunk)
