# Pipetting Robot
The Scienteens Lab is a Luxembourgish research lab for high school students. I programmed for them a pipetting robot intended to be used during public events or during workshops.      
This project consists of two applications: the painting and the explaining application.      
This project is not supposed to be used at home but the code and its resources are accessible for education purposes.      

This project was developed for Mac and a Raspbian operating systems. May not work properly on other operating systems.      

## Installation
This projects requires Python and some additional libraries. Xcode may need to be installed on your machine.      
To install the different requirements run: **bash install.sh**      
**To run only the Python applications, sshpass is not necessary.**      
Sshpass will not be installed with the given script as it is easy to cause security issues with it. It is required to run the robot.      
In install.sh, you can find how to install it.      

## Run
To run the painting application enter on your command line: **bash run.sh**      
To run the explaining application enter on your command line: **bash run_exp.sh**      
**The command line may return some errors concerning sshpass if not installed. These can be ignored. The applications should work fine nonetheless.**      

## File Structure

- Thesis: In this directory, you can find the thesis belonging to this project and images and screenshots of the different stages of development.
- bash_scripts: In this directory, the shell scripts that are not meant to be run outside of one of the applications are stored.
  - send.sh: Sends the painting done to the robot.
- creations: In this directory, the paintings and the instructions realised with the painting application are stored.
- examples: In this directory, instructions of paintings that can be loaded into the painting application are.
- exp_src: This is the directory containing the explaining application and its resources
- resources: In this directory, files used in both application are stored.
- robot_src: Contains the program run by the pipetting robot.
- src: Contains the painting application
- README.md: Help file to know how this repository works.
- install.sh: installs the different project dependencies (sshpass not included)
- run.sh: runs the painting application.
- run_exp.sh: runs the explaining application
