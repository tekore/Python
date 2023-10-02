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
        "net-tools"
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
    'refresh_token': offline_token,
    }
    print("\nRequesting a Redhat access token using the supplied offline token.")
    token_request = requests.post("https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token", data=data)
    if token_request.status_code == 400:
        return(print("\n[ERROR]: Supplied offline token is invalid, unable to use RedHat Image Builder with the supplied token.\n"))
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
            print(poll.content)
            break
    image_url = json.loads(poll.content)['image_status']['upload_status']['options']['url']
    filename = os.path.basename('rhel.ova')
    dl_path = os.path.expanduser('./') + "downloads/"
    os.makedirs(dl_path, exist_ok=True)
    abs_path = os.path.join(dl_path, filename)
    with requests.get(image_url, stream=True) as r:
        with open(abs_path, 'wb') as file:
            total_size, chunk_size = int(r.headers.get('Content-Length')), 10240000
            for i, chunk in enumerate(r.iter_content(chunk_size=chunk_size)):
                c = i * chunk_size / total_size * 100
                file.write(chunk)
                sys.stdout.write(f"\rDownloading {filename} {round(c, 4)}%")
                time.sleep(.1)
                sys.stdout.flush()

def download(url):
    filename = os.path.basename('vyos.ova')
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
    print("\nWebServer is running on http://%s:%s" %(HOST_IP,args.p))
    httpd.serve_forever()

def main():
    print("\nStarting image downloads..")
    download("https://legacy-lts-images.vyos.io/1.2.9-S1/vyos-1.2.9-S1-cloud-init-vmware.ova")
    rhelib("https://console.redhat.com/api/image-builder/v1/compose")
    firewall('open')
    try:
        serve()
    except KeyboardInterrupt:
        firewall('close')

def prerun():
    # Make sure the:
    # directory writable
    # ufw is installed

    try:
        offline_token = os.getenv('OFFLINE_TOKEN')
    except:
        sys.exit(print('\n[ERROR]: No OFFLINE_TOKEN variable exported, please visit: https://access.redhat.com/management/api and export the generated offline token variable before running this script. (export OFFLINE_TOKEN="...")\n'))
    password = getpass.getpass('Enter the sudo password to configure the firewall:')
    return(password, offline_token)

def args():
    parser = argparse.ArgumentParser(prog='Image Download Automation', description="This scipt is designed to download Vyos and RedHat OS images and serve them over a local webserver.")
    megroup = parser.add_mutually_exclusive_group()
    parser.add_argument('--p', type=int,default=8000, help="Port for the webserver.")
    parser.add_argument('--offline_token', help="RedHat Image Builder Offline Token.")
    parser.add_argument('--organisation', type=int, required=True, help="RedHat Profile Key  Organisation Number. This can be found by clicking into the corresponding Profile Key you're using, (https://access.redhat.com/management/activation_keys).")
    parser.add_argument('--activation-key', type=str, required=True, help="RedHat Profile Key, (https://access.redhat.com/management/activation_keys).")
    megroup.add_argument('--vyosonly', action='store_true', help="Only download the Vyos Image.")
    megroup.add_argument('--rhelonly', action='store_true', help="Only download the RHEL Image.")
    megroup.add_argument('--truenasonly', action='store_true', help="Only download the TrueNas Image.")
    return(parser.parse_args())

if __name__ == '__main__':
    args = args()
    password, offline_token = prerun()
    main()
