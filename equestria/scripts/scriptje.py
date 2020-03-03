import sys
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print(BASE_DIR)

if len(sys.argv) < 3:
    print("not enough arguments")
    exit(0)


input_filename = sys.argv[1]
output_filename = sys.argv[2]
fr = open(input_filename, "r")

str1 = fr.readline()
str1 = str1 + "A"

fw = open(output_filename, "w")
fw.write(str1)
fw.write("TESTING")
fr.close()
fw.close()
time.sleep(10)
print("done")
