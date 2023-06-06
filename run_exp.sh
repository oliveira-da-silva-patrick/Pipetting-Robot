#!/bin/sh

# check if this os is mac or a different one
if [[ "$OSTYPE" == "darwin"* ]]; then
    python3 ./exp_src/exp_mac.py 
fi