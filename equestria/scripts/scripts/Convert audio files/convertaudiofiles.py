import subprocess
from argparse import ArgumentParser
from shlex import quote
import string
import os

SOX_INFO_CMD = "sox --info -r {}"
SOX_CONVERT_CMD = "sox {} -r 16000 {}"

# This script is used to convert recordings into new recordings with ending -16khz & fs=16000
# Author: Lars van Rhijn
# Based on a Perl script by Wei Xue
# Last modified: 24-02-2020
# This script requires sox to be installed on the host

# Converts audio files to 16khz using the sox command
def convert_file_to_16khz(file_to_convert, converted_file):
	current_sample_rate = subprocess.check_output(SOX_INFO_CMD.format(quote(file_to_convert)), shell=True)
	if int(current_sample_rate.decode()) == 16000:
		print("The recording {} is already converted to 16khz.".format(file_to_convert))
	else:
		print("Converting {} to 16khz.".format(file_to_convert))
		result = subprocess.run(SOX_CONVERT_CMD.format(quote(file_to_convert), quote(converted_file)), shell=True)
		if result.returncode == 0:
			print("Conversion succesful!")
		else:
			print("Conversion failed with return code {}.".format(result.returncode))

# Run as: python3 convertaudiofiles.py [wav_file_to_convert] -o [output_file_to_write_to]
if __name__ == "__main__":
	parser = ArgumentParser(description="Convert audio files to 16khz")
	parser.add_argument("file_to_convert", help="file to convert to 16khz")
	parser.add_argument("-o", "--output", help="output directory")
	args = parser.parse_args()

	file_to_convert = args.file_to_convert

	output_file = file_to_convert.replace(".wav", "-16khz.wav")
	if args.output:
		output_file = os.path.join(args.output, os.path.basename(output_file))

	if ".wav" in file_to_convert:
		convert_file_to_16khz(file_to_convert, output_file)