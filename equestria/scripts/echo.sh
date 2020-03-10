#!/bin/sh

# Takes 5 command line options:
# 1,3 and 5 are strings
# 2 and 4 are integer

echo $1 > echo.sh.out
sleep $2
echo $3 >> echo.sh.out
sleep $4
echo $5 >> echo.sh.out
