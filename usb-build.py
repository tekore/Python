import os,sys,requests,argparse,time

def download(url):
    dl_path = os.path.expanduser('./')
    os.makedirs(dl_path, exist_ok=True)
    abs_path = os.path.join(dl_path, "ubuntu.iso")
    print("Downloading %s to: %s" %('ubuntu.iso', abs_path))
    with requests.get(url, stream=True) as r:
        with open(abs_path, 'wb') as file:
            total_size, chunk_size = int(r.headers.get('Content-Length')), 10240000
            for i, chunk in enumerate(r.iter_content(chunk_size=chunk_size)):
                c = i * chunk_size / total_size * 100
                file.write(chunk)
                sys.stdout.write(f"\rDownloading ubuntu.iso {round(c, 4)}%")
                time.sleep(.1)
                sys.stdout.flush()
    print("\n## Download Complete ##\n")

def createiso():
    answer = input("\n@@@ All data will be overwritten on drive %s @@@\nContinue?\n" %(args.drive))
    if answer.lower() != "yes":
        sys.exit(print("Answer was not 'yes', Aborting."))
    sys.exit(print(drivelist))
    # TO DO:
    # Mount the ISO
    # Copy all files from the iso to the usb
    # Edit the grub file on the USB and add the cloud init file also

def cloudinit():
    print("def for the cloudinit file creation")

def main():
    print("### Ubuntu Bootable Drive Creator ###")
    if "ubuntu.iso" not in os.listdir("./"):
        download("https://releases.ubuntu.com/22.04.3/ubuntu-22.04.3-live-server-amd64.iso?_ga=2.8597237.1581741504.1704366440-994956064.1704119533")
    else:
        print("[INFO]: 'ubuntu.iso' in %s, this ISO will be used." %(os.getcwd()))
    createiso()

def prerun():
    if os.access("./", os.W_OK) is False:
        sys.exit(print("[ERROR]: %s is NOT writable! Exiting." %(os.getcwd())))
    drivelist = os.popen('lsblk | grep -v sda').read()
    if args.drive not in drivelist:
        sys.exit(print("[ERROR]: %s not present.\nPlug in the drive and use 'lsblk' to ensure it's recognised by the system." %(args.drive)))

def args():
    parser = argparse.ArgumentParser(prog='Ubuntu bootable USB creator', description="This scipt is designed to download Ubuntu server and create a bootable USB inclusive of a cloud-init configuration.")
    parser.add_argument('--drive', type=str, required=True, help="USB Drive to make bootable")
    return(parser.parse_args())

if __name__ == '__main__':
    args = args()
    drivelist = prerun()
    main()
