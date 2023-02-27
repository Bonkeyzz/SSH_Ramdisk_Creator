<h1 align="center">SSH Ramdisk Creator</h1>


<p align="center">
Create iPhone/iPad OS SSH Ramdisks easily.</br>
Based from <a href="https://github.com/verygenericname/SSHRD_Script">verygenericname's SSHRD_Script</a>.
</p>

---

# Prerequisites

1. A computer running macOS/linux
2. Python 3.x

### Python Modules
1. autodecrypt
2. argsparse
3. requests

# Cloning

1. Clone and cd into this repository: `git clone https://github.com/Bonkeyzz/SSH_Ramdisk_Creator --recursive && cd SSH_Ramdisk_Creator`.
If you have cloned this before, run `cd SSH_Ramdisk_Creator && git pull` to pull new changes
2. After being in the repo directory, do `pip install -r requirements.txt`

# Usage
```shell
usage: create_ssh_ramdisk.py [-h] --decrypt-mode DECRYPT_MODE --cpid CPID --model MODEL --product_type PRODUCT_TYPE --ios IOS [--boot-args BOOT_ARGS]

SSHRD Ramdisk creation tool.

options:
  -h, --help            show this help message and exit
  --decrypt-mode DECRYPT_MODE, -d DECRYPT_MODE
                        '0' is decryption using keys fetched online, '1' is decryption with Gaster
  --cpid CPID, -c CPID  CPID of device (example 0x8000)
  --model MODEL, -m MODEL
                        Model of device (example n71ap)
  --product_type PRODUCT_TYPE, -pt PRODUCT_TYPE
                        Product type of device (example iPhone8,1)
  --ios IOS, -i IOS     iOS version for the ramdisk (example 15.7)
  --boot-args BOOT_ARGS, -ba BOOT_ARGS
                        iOS arguments to execute during boot. Default: "rd=md0 debug=0x2014e -v wdt=-1"
```
**Example:**
```shell
# This will create a ramdisk for iPhone8,2 (iPhone 6s+), Board 1 (BoardConfig: n66ap, CPID: 0x8000)
# With iOS version 15.7. Keys will be fetched online.
./create_ssh_ramdisk.py -d 0 -c 0x8000 -m n66ap -pt iPhone8,2 -i 15.7
```
Ramdisks will be located in `final_ramdisk` once the program finishes. </br>
**NOTE: iOS 16.x is not supported yet. I will not be able to help with any errors occuring when trying to create a ramdisk for this version.**

# Donate
Feel free to donate if you wanna support my work!
<a href="https://paypal.me/bonkeyzz"></br>
<img src="https://raw.githubusercontent.com/andreostrovsky/donate-with-paypal/master/blue.svg" height="40"></a>

# Credits
- [verygenericname](https://github.com/verygenericname) for the shell script (original version)
- [tihmstar](https://github.com/tihmstar) for pzb/original iBoot64Patcher/img4tool
- [xerub](https://github.com/xerub) for img4lib and restored_external in the ramdisk
- [Cryptic](https://github.com/Cryptiiiic) for iBoot64Patcher fork
- [Nebula](https://github.com/itsnebulalol) for a bunch of QOL fixes to this script
