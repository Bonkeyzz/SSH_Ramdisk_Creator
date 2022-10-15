#!/usr/bin/env python3

import os, sys, subprocess
import argparse
import platform
import requests
import urllib.request
from os import path
import plistlib
import pathlib
import zipfile
from autodecrypt import scrapkeys, utils, decrypt_img
import glob
import shutil


def run_cmd(cmd):
    subp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    return subp.stdout.read().decode('utf-8')


def run_pcmd(cmd):
    print(run_cmd(cmd))


def clean_up():
    print("[*] Cleaning up...")
    files = glob.glob('temp_ramdisk/*')
    for file in files:
        os.remove(file)


def get_gaster(platform):
    base_url = f"https://nightly.link/verygenericname/gaster/workflows/makefile/main/gaster-{platform}.zip"
    print(f"[*] Downloading gaster for platform {platform}...")
    urllib.request.urlretrieve(base_url, f"{platform}/gaster-{platform}.zip")
    if os.path.isfile(f'{platform}/gaster-{platform}.zip'):
        print(f"[*] Downloaded! Extracting...")
        with zipfile.ZipFile(f'{platform}/gaster-{platform}.zip', 'r') as gaster_zip:
            gaster_zip.extractall(platform)
        print(f"[*] Cleaning up...")
        os.remove(f'{platform}/gaster-{platform}.zip')
    else:
        print(f"[!] Failed to download gaster for platform {platform}!")


def get_ipsw_url(product_type, ios_version):
    global ipsw_url
    ipsw_url = 'null'
    api_path = f'https://api.ipsw.me/v4/device/{product_type}?type=ipsw'
    resp = requests.get(api_path)
    if resp.status_code == 200 and resp.text:
        resp = resp.json()
        for firmware_list in resp['firmwares']:
            if firmware_list['version'] == ios_version:
                ipsw_url = firmware_list['url']
    return ipsw_url


# kerneldiff.py
# https://github.com/verygenericname/SSHRD_Script/blob/main/kerneldiff.py
def kernel_diff(original, patched, bpatchfile):
    sizeP = os.path.getsize(patched)
    sizeO = os.path.getsize(original)
    if sizeP != sizeO:
        print("[!] Size does not match, can't compare files!")
    p = open(patched, "rb").read()
    o = open(original, "rb").read()
    diff = []
    for i in range(sizeO):
        originalByte = o[i]
        patchedByte = p[i]
        if originalByte != patchedByte:
            diff.append([hex(i), hex(originalByte), hex(patchedByte)])
    diffFile = open(bpatchfile, 'w+')
    diffFile.write('#AMFI\n\n')
    for d in diff:
        data = str(d[0]) + " " + (str(d[1])) + " " + (str(d[2]))
        diffFile.write(data + '\n')
        print(data)


def get_build_id(product_type, ios_version):
    global build_id
    build_id = 'null'
    api_path = f'https://api.ipsw.me/v4/device/{product_type}?type=ipsw'
    resp = requests.get(api_path)
    if resp.status_code == 200 and resp.text:
        resp = resp.json()
        for firmware_list in resp['firmwares']:
            if firmware_list['version'] == ios_version:
                build_id = firmware_list['buildid']
    return build_id


def download_required_files():
    ipsw_url = get_ipsw_url(args['product_type'], args['ios'])
    print(f'URL: {ipsw_url}')
    run_pcmd(f"../{sys_platform}/pzb -g BuildManifest.plist {ipsw_url}")
    with open('BuildManifest.plist', 'rb') as build_manifest:
        build_manifest_plist = plistlib.load(build_manifest)
        codename: str = build_manifest_plist['BuildIdentities'][0]['Info']['BuildTrain']
        ibss_path: str = build_manifest_plist['BuildIdentities'][0]['Manifest']['iBSS']['Info']['Path']
        ibec_path: str = build_manifest_plist['BuildIdentities'][0]['Manifest']['iBEC']['Info']['Path']
        devicetree_path: str = build_manifest_plist['BuildIdentities'][0]['Manifest']['DeviceTree']['Info']['Path']

        restoreramdisk_path: str = build_manifest_plist['BuildIdentities'][0]['Manifest']['RestoreRamDisk']['Info'][
            'Path']
        kernelcache_path: str = build_manifest_plist['BuildIdentities'][0]['Manifest']['RestoreKernelCache']['Info'][
            'Path']
        trustcache_path: str = f'Firmware/{restoreramdisk_path}.trustcache'

        run_pcmd(f"../{sys_platform}/pzb -g {ibss_path} {ipsw_url}")
        run_pcmd(f"../{sys_platform}/pzb -g {ibec_path} {ipsw_url}")
        run_pcmd(f"../{sys_platform}/pzb -g {devicetree_path} {ipsw_url}")

        run_pcmd(f"../{sys_platform}/pzb -g {trustcache_path} {ipsw_url}")
        run_pcmd(f"../{sys_platform}/pzb -g {kernelcache_path} {ipsw_url}")
        run_pcmd(f"../{sys_platform}/pzb -g {restoreramdisk_path} {ipsw_url}")

        ibss_path = ibss_path.replace("Firmware/dfu/", "").replace("Firmware/all_flash/", "")
        ibec_path = ibec_path.replace("Firmware/dfu/", "").replace("Firmware/all_flash/", "")
        devicetree_path = devicetree_path.replace("Firmware/dfu/", "").replace("Firmware/all_flash/", "")
        trustcache_path = trustcache_path.replace("Firmware/", "")

        return ibss_path, ibec_path, kernelcache_path, restoreramdisk_path, trustcache_path, devicetree_path


def decrypt_boot_stages(ibss_path, ibec_path):
    ibec_decrypted_path = ibec_path.replace(".im4p", ".bin")
    ibss_decrypted_path = ibss_path.replace(".im4p", ".bin")
    print(f"Decryption mode: {args['decrypt-mode'] == 1: 'Gaster' : 'Autodecrypt'}")
    if args['decrypt-mode'] == 1:
        run_pcmd(f'../{sys_platform}/gaster pwn')
        run_pcmd(f'../{sys_platform}/gaster reset')
        run_pcmd(f'../{sys_platform}/gaster decrypt {ibss_path} {ibss_decrypted_path}')
        run_pcmd(f'../{sys_platform}/gaster decrypt {ibec_path} {ibec_decrypted_path}')
    else:
        build_id = get_build_id(args.product_type, args.ios)
        print(f'[*] Build ID: {build_id}')
        print(f'[*] Product Type: {args.product_type}\n')

        print("[!] Beginning decryption of iBSS and iBEC...\n")
        print(f'[*] iBSS Path: {ibss_path}')
        ivkey_ibss = scrapkeys.getkeys(args.product_type, build_id, ibss_path)
        iv_ibss, key_ibss = utils.split_key(ivkey_ibss)
        print(f'[*] IV: {iv_ibss}')
        print(f'[*] Key: {key_ibss}')
        magic_ibss = decrypt_img.get_image_type(ibss_path)
        decrypt_img.decrypt_img(ibss_path, magic_ibss, iv_ibss, key_ibss)

        print(f'[*] iBEC Path: {ibec_path}')
        ivkey_ibec = scrapkeys.getkeys(args.product_type, build_id, ibec_path)
        iv_ibec, key_ibec = utils.split_key(ivkey_ibec)
        print(f'[*] IV: {iv_ibec}')
        print(f'[*] Key: {key_ibec}')
        magic_ibec = decrypt_img.get_image_type(ibec_path)
        decrypt_img.decrypt_img(ibec_path, magic_ibec, iv_ibec, key_ibec)

    return ibss_decrypted_path, ibec_decrypted_path


def patch_files(ibss_decrypted_path, ibec_decrypted_path, kernelcache_path, devicetree_path, ramdisk_path,
                trustcache_path):
    run_pcmd(f'../{sys_platform}/iBoot64Patcher {ibss_decrypted_path} iBSS.patched')
    run_pcmd(
        f'../{sys_platform}/img4 -i iBSS.patched -o ../final_ramdisk/{args.ios}/{args.product_type}/{args.model}/ibss.img4 -M IM4M -A -T ibss')
    if args['boot-args']:
        boot_args = args['boot-args']
    else:
        boot_args = '"rd=md0 debug=0x2014e -v wdt=-1"'
    if args.cpid == "0x8960" or args.cpid == "0x7000" or args.cpid == "0x7001":
        boot_args = boot_args[:-1]
        boot_args += ' -restore"'
    print(f"[!] Boot arguments: {boot_args}")
    run_pcmd(f'../{sys_platform}/iBoot64Patcher {ibec_decrypted_path} iBEC.patched -b {boot_args} -n')
    run_pcmd(
        f'../{sys_platform}/img4 -i iBEC.patched -o ../final_ramdisk/{args.ios}/{args.product_type}/{args.model}/iBEC.img4 -M IM4M -A -T ibec')
    run_pcmd(f'../{sys_platform}/img4 -i {kernelcache_path} -o kcache.raw')
    run_pcmd(f'../{sys_platform}/Kernel64Patcher kcache.raw kcache.patched -a')
    kernel_diff('kcache.raw', 'kcache.patched', 'kcache.bpatch')
    is_linux = '-J' if sys_platform == 'Linux' else ''
    run_pcmd(
        f'../{sys_platform}/img4 -i {kernelcache_path} -o ../final_ramdisk/{args.ios}/{args.product_type}/{args.model}/kernelcache.img4 -M IM4M -T rkrn -P kcache.bpatch {is_linux}')
    run_pcmd(
        f'../{sys_platform}/img4 -i {devicetree_path} -o ../final_ramdisk/{args.ios}/{args.product_type}/{args.model}/devicetree.img4 -M IM4M -T rdtr')

    run_pcmd(
        f'../{sys_platform}/img4 -i {trustcache_path} -o ../final_ramdisk/{args.ios}/{args.product_type}/{args.model}/trustcache.img4 -M IM4M -T rtsc')
    run_pcmd(f'../{sys_platform}/img4 -i {ramdisk_path} -o ramdisk.dmg')
    patch_ramdisk('ramdisk.dmg')
    run_pcmd(
        f'../{sys_platform}/img4 -i ..other/logo.im4p -o ../final_ramdisk/{args.ios}/{args.product_type}/{args.model}/logo.img4 -A -T rlgo -M IM4M')


def patch_ramdisk(ramdisk_path):
    if sys_platform == 'Darwin':
        run_pcmd('hdiutil resize -size 210MB ramdisk.dmg')
        run_pcmd('hdiutil attach -mountpoint /tmp/SSHRD ramdisk.dmg')

        if args.model == 'j42dap':
            run_pcmd(f'../{sys_platform}/gtar -x --no-overwrite-dir -f ../sshtars/atvssh.tar.gz -C /tmp/SSHRD/')
        elif args.cpid == '0x8012':
            run_pcmd(f'../{sys_platform}/gtar -x --no-overwrite-dir -f ../sshtars/t2ssh.tar.gz -C /tmp/SSHRD/')
            print("[!] !!! T2 Ssh might hang and do nothing when booting !!!")
        else:
            run_pcmd(f'../{sys_platform}/gtar -x --no-overwrite-dir -f ../sshtars/ssh.tar.gz -C /tmp/SSHRD/')

        run_pcmd('hdiutil detach -force /tmp/SSHRD')
        run_pcmd('hdiutil resize -sectors min ramdisk.dmg')
    else:
        run_pcmd(f'../{sys_platform}/hfsplus ramdisk.dmg grow 210000000 > /dev/null')

        if args.model == 'j42dap':
            run_pcmd(f'../{sys_platform}/hfsplus ramdisk.dmg untar ../sshtars/atvssh.tar > /dev/null')
        elif args.cpid == '0x8012':
            run_pcmd(f'../{sys_platform}/hfsplus ramdisk.dmg untar ../sshtars/t2ssh.tar > /dev/null')
            print("[!] !!! T2 Ssh might hang and do nothing when booting !!!")
        else:
            run_pcmd(f'../{sys_platform}/hfsplus ramdisk.dmg untar ../sshtars/ssh.tar > /dev/null')
    run_pcmd(
        f'../{sys_platform}/img4 -i ramdisk.dmg -o ../final_ramdisk/{args.ios}/{args.product_type}/{args.model}/ramdisk.img4 -M IM4M -A -T rdsk')


if __name__ == '__main__':
    main_root_dir = os.path.dirname(__file__)
    sys_platform = platform.uname().system
    print(f"[*] System platform: {sys_platform}")
    if sys_platform == 'Windows':
        print("[*] This tool is not supported on Windows, it needs Linux or MacOS.")
        exit(1)
    os.system('clear')
    parser = argparse.ArgumentParser(description='SSHRD Ramdisk creation tool.')
    parser.add_argument('--decrypt-mode', '-d', type=int,
                        help="'0' is decryption using keys fetched online, '1' is decryption with Gaster",
                        required=True)
    parser.add_argument('--cpid', '-c', type=str, help='CPID of device (example 0x8000)', required=True)
    parser.add_argument('--model', '-m', type=str, help='Model of device (example n71ap)', required=True)
    parser.add_argument('--product_type', '-pt', type=str, help='Product type of device (example iPhone8,1)',
                        required=True)
    parser.add_argument('--ios', '-i', type=str, help='iOS version for the ramdisk (example 15.7)', required=True)
    parser.add_argument('--boot-args', '-ba', type=str,
                        help='iOS arguments to execute during boot. Default: "rd=md0 debug=0x2014e -v wdt=-1"')
    args = parser.parse_args()

    if not os.path.isfile(f'{sys_platform}/gaster') and args['decrypt-mode'] == 1:
        print("[!] gaster does not appear to exist! Downloading a new one...\n")
        get_gaster(sys_platform)

    pathlib.Path('temp_ramdisk').mkdir(exist_ok=True, parents=True)
    pathlib.Path('final_ramdisk').mkdir(exist_ok=True, parents=True)
    pathlib.Path(f'final_ramdisk/{args.ios}/{args.product_type}').mkdir(exist_ok=True, parents=True)

    if path.isdir(f'final_ramdisk/{args.ios}/{args.product_type}/{args.model}'):
        print(f'[!] data for {args.model} already exists! Recreating...')
        shutil.rmtree(f'final_ramdisk/{args.ios}/{args.product_type}/{args.model}')

    pathlib.Path(f'final_ramdisk/{args.ios}/{args.product_type}/{args.model}').mkdir(exist_ok=True, parents=True)

    os.chdir('temp_ramdisk')
    run_pcmd(f"../{sys_platform}/img4tool -e -s ..other/shsh/{args.cpid}.shsh -m IM4M")

    ibss_path, ibec_path, kernelcache_path, restoreramdisk_path, trustcache_path, devicetree_path = download_required_files()
    ibss_decrypted_path, ibec_decrypted_path = decrypt_boot_stages(ibss_path, ibec_path)
    patch_files(ibss_decrypted_path, ibec_decrypted_path, kernelcache_path, devicetree_path, restoreramdisk_path,
                trustcache_path)

    os.chdir('../')
    clean_up()
    print("[*] Done!")
    print("Python version was made by Bonkeyzz.")
    print("Original Shell script was made by verygenericname.")
