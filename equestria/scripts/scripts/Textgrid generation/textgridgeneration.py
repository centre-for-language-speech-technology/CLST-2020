import subprocess
from argparse import ArgumentParser
from shlex import quote
import os


GENERATE_TEXTGRID = "perl ./generate_textgrid.pl {} {} str({}) str({})"


# This script is used to generate boundaries for phonetics and regular words
# Author: Matti Eisenlohr
# Based on a script by Wei Xue
# Last modified: 02-03-2020

# Generates textgrids
def generate_textgrid(aligndir, create_alignment_tier, phone_tier_name, word_tier_name):
	result = subprocess.run(GENERATE_TEXTGRID.format())
	if result.returncode == 0:
		print("Textgrid generation successful!")
	else:
		print("Textgrid generation failed with return code {}.".format(result.returncode))

# Run as: python3 textgridgeneration.py [main_folder_wav] [create_alignment_tier] [phone_tier_name] [word_tier_name]
if __name__ == "__main__":
	parser = ArgumentParser(description="Generate textgrids")
	parser.add_argument("main_folder_wav", help="Main folder containing the .wav files")
	parser.add_argument("create_alignment_tier",help="Tier created in the resulting file containing the phone/word alignment")
	parser.add_argument("phone_tier_name", help="Tier for phonetics")
	parser.add_argument("word_tier_name", help="Tier for words")
	args = parser.parse_args()
	
	generate_textgrid(args.main_folder_wav, args.create_alignment_tier, args.phone_tier_name, args.word_tier_name)
	