#!/bin/sh

# check if this os is mac or a different one
if [[ "$OSTYPE" == "darwin"* ]]; then
    # if you want to run this program with the robot, you need to install sshpass
    # homebrew does not allow installing sshpass
    # to only use the program without the robot, execute this script and run the program
    # and ignore the error messages concerning the missing sshpass library
    # to run this program with the robot, you need to install sshpass manually
    # by following this link: https://gist.github.com/arunoda/7790979

    # install homebrew
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" 
    brew install python3 # install python
    brew install python3-tk # install tkinter
    brew install python3-numpy # install numpy
    pip3 install pillow # install pillow
    sudo chmod +x ./bash_scripts/send.sh # give execution right to the send bash script
else
    # to run this script: bash install_linux.sh
    # update and upgrade apt-get
    sudo apt-get update
    sudo apt-get upgrade
    sudo apt install python3 # install python
    sudo apt install python3-tk # install tkinter
    sudo apt install python3-numpy # install numpy
    sudo apt install python3-pip # install python pip
    pip3 install pillow # install pillow
    sudo apt-get install python3-pil python3-pil.imagetk # install pillow image tkinter
    sudo apt-get install sshpass # install sshpass
    sudo chmod +x ./bash_scripts/send.sh # give execution right to the send bash script
fi