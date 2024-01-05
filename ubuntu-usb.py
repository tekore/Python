import os,sys,requests,argparse,time

def download(url, filename):
    dl_path = os.path.expanduser('./')
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
    return(abs_path)

def createiso(filepath):
    answer = input("\n@@@ All data will be overwritten on drive %s @@@\nContinue?\n" %(args.drive))
    if answer.lower() != "yes":
        sys.exit(print("Answer was not 'yes', Aborting."))
    print(drivelist)

    # Mount the ISO
    iso_mount == "media/temp_iso"
    os.system("mkdir %s && mount -o rw,loop %s %s" %(iso_mount,filepath,iso_mount))

    # Copy all files from the iso to the usb
    cloudinit(iso_mount)
    os.system("dd if=%s of=%s bs=1M" %(iso_mount, args.drive))
    # Edit the grub file on the USB and add the cloud init file also
    
    # Unmount
    os.system("umount %s && rmdir %s" %(iso_mount))

def cloudinit():
    cloud-config == """
#cloud-config
users:
  - default
  - name: ${var.user-data.username}
    groups: sudo
    shell: /bin/bash
    ssh_authorized_keys: ${var.user-data.public-key}
    lock_passwd: false
    passwd: ${var.user-data.password-hash}
    sudo: ALL=(ALL) NOPASSWD:ALL
  - name: root
    shell: /bin/bash
    ssh_authorized_keys: ${var.user-data.public-key}
runcmd:
  - ${var.cloud-init-runcmd.ubuntu}
package_update: true
package_upgrade: true
"""
    with open("%s/ubuntu-cloud-init.yml" %(iso_mount),"w") as file:
        file.write(cloud-config)

def main():
    print("### Ubuntu Bootable Drive Creator ###")
    if "ubuntu.iso" not in os.listdir("./"):
        filepath = download("https://releases.ubuntu.com/22.04.3/ubuntu-22.04.3-live-server-amd64.iso?_ga=2.8597237.1581741504.1704366440-994956064.1704119533", "ubuntu.iso")
    else:
        print("[INFO]: 'ubuntu.iso' present in %s, using the already present ISO file." %(os.getcwd()))
    createiso(filepath)

def prerun():
    if os.access("./", os.W_OK) is False:
        sys.exit(print("[ERROR]: %s is NOT writable! Exiting." %(os.getcwd())))
    drivelist = os.popen('lsblk').read()
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
