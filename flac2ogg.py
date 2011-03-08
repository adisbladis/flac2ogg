#!/usr/bin/env python

'''
Copy a directory tree and recode all flacs to ogg

Licensed under GPLv2
Written by Adam Hose <adisbladis@m68k.se>
'''

import os
import re
import shutil
import sys

def usage():
	print("Usage: %s /source /target [quality (man oggenc, default=8)] [Oggenc params]" % (sys.argv[0]))
	sys.exit(1)

try:
	source=sys.argv[1]
	target=sys.argv[2]
except:
	usage()
try: quality=sys.argv[3]
except: quality=8
try: params=sys.argv[4]
except: params=""


def handler(lol,old_dir,files):

	new_dir=old_dir
	new_dir=new_dir.replace(source,target)

	try: os.mkdir(new_dir)
	except: print(new_dir + " exists, skipping creation")

	for file in files:
		filetype = file.split(".")[-1]

		#Try to create if directory
		if(os.path.isdir(old_dir + "/" + file)):
			try: os.mkdir(new_dir + "/" + file)
			except: new_dir + "/" + file + " exists, skipping"
		elif filetype == "flac" or filetype == "FLAC":
			print("Recoding " + file)
			infile = old_dir + "/" + file
			outfile = new_dir + "/" + file
			outfile = outfile.replace('.flac', '.ogg')
			os.system("oggenc -q %s %s -o \"%s\" \"%s\"" % (quality, params, outfile, infile))
		else:
			print("Copying " + file)
			shutil.copy(old_dir + "/" + file, new_dir + "/" + file)

os.path.walk(source,handler,"lol")
