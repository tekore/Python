import os,sys,socket,requests,argparse,getpass,time,json
from http.server import HTTPServer, SimpleHTTPRequestHandler

def rhelib(url):
    rhelib_JSON = {
    "distribution": "rhel-92",
    "image_name": "rhel9",
    "image_requests": [
      {
        "architecture": "x86_64",
        "image_type": "vsphere-ova",
        "upload_request": {
          "type": "aws.s3",
          "options": {}
        }
      }
    ],
    "customizations": {
      "packages": [
        "vim-enhanced",
        "yum-utils",
        "net-tools",
        "open-vm-tools",
        "cloud-init"
      ],
      "subscription": {
        "activation-key": '"' + str(args.activation_key) + '"',
        "insights": True,
        "rhc": True,
        "organization": args.organisation,
        "server-url": "subscription.rhsm.redhat.com",
        "base-url": "https://cdn.redhat.com/"
      }
    }
    }
    data = {
    'grant_type': 'refresh_token',
    'client_id': 'rhsm-api',
    'refresh_token': args.offline_token,
    }
    print("\nRequesting a Redhat access token using the supplied offline token.")
    token_request = requests.post("https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token", data=data)
    if token_request.status_code == 400:
        return(print("\n[ERROR]: The offline token is invalid, unable to use RedHat Image Builder with the supplied token.\n"))
    print("Access token recived, Requesting the Redhat Image..")
    headers = {
    'Authorization': 'Bearer ' + json.loads(token_request.content)['access_token'],
    'Content-Type': 'application/json',
    }
    d = requests.post('https://console.redhat.com/api/image-builder/v1/compose', headers=headers, data=json.dumps(rhelib_JSON))
    while True:
        headers = {'Authorization': 'Bearer ' + json.loads(token_request.content)['access_token']}
        poll = requests.get('https://console.redhat.com/api/image-builder/v1/composes/' + json.loads(d.content)['id'], headers=headers)
        print("Build Status: %s" %(json.loads(poll.content)['image_status']['status']), end='\r')
        time.sleep(.1)
        if json.loads(poll.content)['image_status']['status'] == 'success':
            break
    image_url = json.loads(poll.content)['image_status']['upload_status']['options']['url']
    filename = os.path.basename('rhel.ova')
    download(image_url, filename)

def vyos(url):
    filename = os.path.basename('vyos.ova')
    download(url, filename)

def ubuntu(url):
    filename = os.path.basename('ubuntu.ova')
    download(url, filename)

def download(url, filename):
    dl_path = os.path.expanduser('./') + "downloads/"
    os.makedirs(dl_path, exist_ok=True)
    abs_path = os.path.join(dl_path, filename)
    print("Downloading %s to: %s" %(filename, abs_path))
    with requests.get(url, stream=True) as r:
        with open(abs_path, 'wb') as file:
            total_size, chunk_size = int(r.headers.get('Content-Length')), 10240000
            for i, chunk in enumerate(r.iter_content(chunk_size=chunk_size)):
                c = i * chunk_size / total_size * 100
                file.write(chunk)
                sys.stdout.write(f"\rDownloading {filename} {round(c, 4)}%")
                time.sleep(.1)
                sys.stdout.flush()
    print("\n## Download Complete ##\n")

def firewall(command):
    if command == 'open':
        os.popen("echo '%s' | sudo -S ufw allow to 0.0.0.0/0 port %s" %(password,args.p))
        return(print("\nFirewall port: %s opened." %(args.p)))
    elif command == 'close':
        os.popen("echo '%s' | sudo -S ufw --force delete allow %s" %(password,args.p))
        return(print("\nFirewall port: %s closed." %(args.p)))

def serve():
    HOST_IP = socket.gethostbyname(socket.gethostname())
    httpd = HTTPServer((HOST_IP, args.p), SimpleHTTPRequestHandler)
    print("\nWebServer is running on http://%s:%s" %(HOST_IP, args.p))
    httpd.serve_forever()

def main():
    if args.serveonly is False:
        print("\nStarting Image Downloads..")
        if args.vyos is True:
            vyos("https://legacy-lts-images.vyos.io/1.2.9-S1/vyos-1.2.9-S1-cloud-init-vmware.ova")
        if args.ubuntu is True:
            ubuntu("https://cloud-images.ubuntu.com/lunar/current/lunar-server-cloudimg-amd64.ova")
        if args.rhel is True:
            rhelib("https://console.redhat.com/api/image-builder/v1/compose")
    firewall('open')
    try:
        serve()
    except KeyboardInterrupt:
        firewall('close')

def prerun():
    if not any([args.vyos, args.ubuntu, args.rhel, args.serveonly]):
        sys.exit(print("\nOVA Image Downloader: [ERROR]: At least one of the following flags is required '--vyos' '--ubuntu' '--rhel'"))
    elif args.rhel is True and not args.RHEL:
        sys.exit(print("\nOVA Image Downloader: [INFO]: To download the RedHat OVA Image please use the 'RHEL' flag along with the required flags '--organisation', '--activation_key', '--offline_token'. (Example: python3 Auto-downloads.py --rhel RHEL --organisation 12335678 --activation-key redhat-server --offline-token eyJhbGciOi....)"))
    elif os.path.exists("/usr/sbin/ufw") is False:
        sys.exit(print("ufw NOT installed! Exiting."))
    elif os.access("./", os.W_OK) is False:
        sys.exit(print("%s is NOT writable! Exiting." %(os.getcwd())))
    elif args.serveonly is False and os.path.exists("./downloads") and len(os.listdir("./downloads")) > 0:
        answer = input("\n@@@ Files will be overwritten in %s/downloads @@@\nContinue?\n" %(os.getcwd()))
        if answer.lower() != "yes":
            sys.exit(print("Answer was not 'yes', Aborting.."))
    password = getpass.getpass('Enter the sudo password to configure the firewall:')
    return(password)

def args():
    parser = argparse.ArgumentParser(prog='OVA Image Downloader', description="This scipt is designed to download Vyos, Ubuntu and RedHat OVA images and serve them on a local webserver.")
    parser.add_argument('--p', type=int,default=8000, help="Webserver port. This will default to 8000 if not set.")
    parser.add_argument('--serveonly', action='store_true', help="Skip the image downloads, start the webserver only.")
    subparsers = parser.add_subparsers(dest="RHEL", help='Parser for the RHEL flag')
    rhel_parser = subparsers.add_parser('RHEL', help="RHEL data for the image builder")
    parser.add_argument('--vyos', action='store_true', help="Download the VyOS OVA Image.")
    parser.add_argument('--ubuntu', action='store_true', help="Download the Ubuntu OVA Image.")
    parser.add_argument('--rhel', action='store_true', help="Download the RHEL9 OVA Image.")
    rhel_parser.add_argument('--organisation', type=int, required=True, help="RedHat organisation ID. This can be found under the 'Activation Keys' heading, (https://console.redhat.com/insights/connector/activation-keys).")
    rhel_parser.add_argument('--activation-key', type=str, required=True, help="RedHat Profile Key, (https://console.redhat.com/insights/connector/activation-keys).")
    rhel_parser.add_argument('--offline-token', type=str, required=True, help="RedHat Image Builder Offline Token, (https://access.redhat.com/management/api).")
    return(parser.parse_args())

if __name__ == '__main__':
    args = args()
    password = prerun()
    main()
