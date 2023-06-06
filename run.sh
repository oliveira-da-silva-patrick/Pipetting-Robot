#!/bin/sh

# next expected painting code
next_code=0

# get the next code
if [ -d "./creations/" ]; then
    next_code=$(ls ./creations/ | wc -l)
fi

# check if this os is mac or a different one
if [[ "$OSTYPE" == "darwin"* ]]; then
    python3 ./src/ui_mac.py & # execute in parallel the mac version
else
    python3 ./src/ui_rasp.py & # execute in parallel the raspbian version
fi

# send the robot.py script to the robot
sshpass -p "maker" scp ./robot_src/robot.py robot@ev3dev.local:/home/robot/

# connect and control the robot
# store the next code in save.txt
# execute the robot.py script in the robot
sshpass -p "maker" ssh robot@ev3dev.local << EOF
    echo $next_code > save.txt
    brickrun -r --directory="/home/robot/" "/home/robot/robot.py" 
EOF



