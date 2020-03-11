#!/bin/sh

# Takes 5 command line options:
# 1,3 and 5 are strings
# 2 and 4 are integer

OUTPUT="outputs/echo.sh.out"

echo $1 > $OUTPUT
sleep $2
echo $3 >> $OUTPUT
sleep $4
echo $5 >> $OUTPUT
