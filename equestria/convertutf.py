import subprocess
from argparse import ArgumentParser
from shlex import quote
import string
import os

if __name__ == "__main__":
	parser = ArgumentParser(description="Convert encoding to UTF-8")
	parser.add_argument("from_encoding", help="old encoding")
	parser.add_argument("file", help="file to be converted")
	args = parser.parse_args()
	
	subprocess.check_call(['./convertutf.sh', args[0], args[1]])
