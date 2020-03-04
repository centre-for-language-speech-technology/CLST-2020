import subprocess
from argparse import ArgumentParser
from shlex import quote

PRAAT_CMD = "praat --run converttextgrid.praat {}"

# This script is used to convert short textgrid to full textgrid using a praat script
# Author: Lars van Rhijn
# Last modified: 26-02-2020
# This script requires praat to be installed on the host and requires convertttextgrid.praat in the same directory as this script

def run_praat(input_folder):
	result = subprocess.run(PRAAT_CMD.format(quote(input_folder)), shell=True)
	if result.returncode == 0:
		print("Conversion succesful!")
	else:
		print("Conversion failed with return code {}.".format(result.returncode))

# Run as: python3 converttextgrid.py [folder_with_tg_files]
# The result of this script is all .tg files in the [folder_with_tg_files] are converted to full textgrid with the names appended -converted.tg
if __name__ == "__main__":
	parser = ArgumentParser(description="Convert audio files to full textgrid")
	parser.add_argument("input_folder", help="folder with wav files to be converted to full textgrid")
	args = parser.parse_args()

	run_praat(args.input_folder)