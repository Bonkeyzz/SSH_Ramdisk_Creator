<h1 align="center">SSH Ramdisk Creator</h1>

<p align="center">
  <a href="https://github.com/Bonkeyzz/SSHRD_Script_bonk/graphs/contributors" target="_blank">
    <img src="https://img.shields.io/github/contributors/verygenericname/SSHRD_Script.svg" alt="Contributors">
  </a>
  <a href="https://github.com/Bonkeyzz/SSHRD_Script_bonk/commits/main" target="_blank">
    <img src="https://img.shields.io/github/commit-activity/w/verygenericname/SSHRD_Script.svg" alt="Commits">
  </a>
</p>

<p align="center">
Create iPhone/iPad OS SSH Ramdisks easily.
</p>

---

# Prerequsites

1. A computer running macOS/linux

# Cloning

Clone and cd into this repository: `git clone https://github.com/Bonkeyzz/SSHRD_Script_bonk --recursive && cd SSHRD_Script`.
If you have cloned this before, run `cd SSHRD_Script && git pull` to pull new changes

# Usage
```shell
usage: sshrd.py [-h] [--cpid CPID] [--model MODEL] [--product_type PRODUCT_TYPE] [--ios IOS]

SSHRD Ramdisk creation tool.

options:                                               
  -h, --help            show this help message and exit
  --cpid CPID, -c CPID  CPID of device (example 0x8000)
  --model MODEL, -m MODEL                              
                        Model of device (example n71ap)
  --product_type PRODUCT_TYPE, -pt PRODUCT_TYPE
                        Product type of device (example iPhone8,1)
  --ios IOS, -i IOS     iOS version for the ramdisk (example 15.7)
```
**Example:**
```shell
# This will create a ramdisk for iPhone8,2 (iPhone 6s+), Board 1 (BoardConfig: n66ap, CPID: 0x8000)
# With iOS version 15.7
./sshrd.py -c 0x8000 -m n66ap -pt iPhone8,2 -i 15.7
```

# Donate
Want to support my work? Buy me a coffee. :^)
<a href="https://paypal.me/bonkeyzz"></br>
<img src="https://raw.githubusercontent.com/andreostrovsky/donate-with-paypal/master/blue.svg" height="40"></a>

# Credits
- [verygenericname](https://github.com/verygenericname) for the shell script (original version)
- [tihmstar](https://github.com/tihmstar) for pzb/original iBoot64Patcher/img4tool
- [xerub](https://github.com/xerub) for img4lib and restored_external in the ramdisk
- [Cryptic](https://github.com/Cryptiiiic) for iBoot64Patcher fork
- [Nebula](https://github.com/itsnebulalol) for a bunch of QOL fixes to this script
