import subprocess
from argparse import ArgumentParser
from shlex import quote
import os

FILE_INFO_CMD = "file -i {}"
FILE_CONVERT_CMD = "iconv -f {} -t utf-8 {} -o {}"
FILE_REMOVE_BITSTRING = "sed -i 's/^\xEF\xBB\xBF//' {}"

# This cript is used to convert UTF-16be and UTF-16le to UTF-8
# Author: Matti Eisenlohr & Lars van Rhijn
# Based on a script by Wei Xue
# Last modified: 27-02-2020
# This script required iconv, sed and the file command to be installed on the host

# Returns either utf-16be or utf-16le if the file is in that encoding, otherwise returns None
def get_file_encoding(file):
	encoding = subprocess.check_output(FILE_INFO_CMD.format(quote(file)), shell=True).decode()
	if "utf-16be" in encoding:
		return "utf-16be"
	elif "utf-16le" in encoding:
		return "utf-16le"
	else:
		return None

# Converts file in encoding to output file in encoding utf-8
def convert_to_utf8(file, output, encoding):
	result = subprocess.run(FILE_CONVERT_CMD.format(quote(encoding), quote(file), quote(output)))
	if result.returncode == 0:
		print("Conversion succesful!")
	else:
		print("Conversion failed with return code {}.".format(result.returncode))

	result = subprocess.run(FILE_REMOVE_BITSTRING.format(quote(output)))
	if result.returncode == 0:
		print("Bitstring removed succesfully!")
	else:
		print("Failed to remove bitstring from output file. Process returned {}.".format(result.returncode))

# Run as: python3 convertutf.py [tg_file_to_convert] -o [output_file_to_write_to]
if __name__ == "__main__":
	parser = ArgumentParser(description="Convert encoding to UTF-8")
	parser.add_argument("file", help="file to be converted")
	parser.add_argument("-o", "--output", help="output directory")
	args = parser.parse_args()

	encoding = get_file_encoding(args.file)
	if encoding is None:
		raise Exception("Encoding of {} unknown.".format(args.file))

	output_file = args.file.replace(".tg", "-utf8.tg")
	if args.output:
		output_file = os.path.join(args.output, os.path.basename(output_file))

	convert_to_utf8(args.file, output_file, encoding)