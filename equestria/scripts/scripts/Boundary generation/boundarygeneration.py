import subprocess
from argparse import ArgumentParser
from shlex import quote
import os

MAKE_PHONE_DIRECTORY = "mkdir -p {} || exit 1;"
MAKE_WORD_DIRECTORY = "mkdir -p {} || exit 1;"
GENERATE_PHONE_BOUNDARY = "perl ./phone_boundary.pl {}/{}/ali.1.ctm \ {}/{}/segments {}/{}.txt  {}/lang || exit 1;"
GENERATE_WORD_BOUNDARY = "perl ./word_boundary.pl {}/{}  {} \ {} {}/lang  || exit 1;"

# This script is used to generate boundaries for phonetics and regular words
# Author: Matti Eisenlohr
# Based on a script by Wei Xue
# Last modified: 02-03-2020

#Make directories for phone boundaries and word boundaries
def make_directories(phonedir, worddir):
	result = subprocess.run(MAKE_PHONE_DIRECTORY.format(quote(phonedir)))
	if result.returncode == 0:
		print("Created phone directory successfully!")
	else:
		print("Creation of phone directory failed with return code {}.".format(result.returncode))

	result = subprocess.run(GENERATE_WORD_BOUNDARY.format(quote(worddir)))
	if result.returncode == 0:
		print("Created word directory successfully!")
	else:
		print("Creation of word directory failed with return code {}.".format(result.returncode))

# Generates boundaries for phonetics and words
def generate_boundaries(aligndir, aimdir, phonedir, worddir):
	result = subprocess.run(GENERATE_PHONE_BOUNDARY.format(quote(aligndir), quote(aimdir), quote(aligndir), quote(aimdir), quote(phonedir), quote(aimdir), quote(datadir)))
	if result.returncode == 0:
		print("Phone boundary generation successful!")
	else:
		print("Phone boundary generation failed with return code {}.".format(result.returncode))

	result = subprocess.run(GENERATE_WORD_BOUNDARY.format(quote(aligndir), quote(aimdir), quote(worddir), quote(aimdir), quote(datadir)))
	if result.returncode == 0:
		print("word boundary generation successful!")
	else:
		print("Word boundary generation failed with return code {}.".format(result.returncode))

# Run as: python3 boundarygeneration.py [aligndir] [phone_tier_name] [word_tier_name] [datadir]
if __name__ == "__main__":
	parser = ArgumentParser(description="Generate phone boundaries and word boundaries")
	parser.add_argument("aligndir", help="Directory containing alignments")
	parser.add_argument("phone_tier_name", help="Tier for phonetics")
	parser.add_argument("word_tier_name", help="Tier for words")
	parser.add_argument("datadir",help="Data directory")
	args = parser.parse_args()
	
	phonedir = args.aligndir+"/"+args.phone_tier_name
	worddir = args.aligndir+"/"+args.word_tier_name
	
	list_of_matching_folders = []
	
	for foldername in os.listdir(aligndir)
		if os.path.isdir(foldername) and foldername.endswith("-16khz"):
			list_of_matching_folders += [foldername,]
	
	for foldername in list_of_matching_folders
		aimdir = os.path.basename(foldername)
		generate_boundaries(args.aligndir, aimdir, phonedir, worddir)