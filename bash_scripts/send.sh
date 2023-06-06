#! /bin/bash

# send the file passed as argument to the robot
sshpass -p "maker" scp $1 robot@ev3dev.local:/home/robot/queue/
