#!/usr/bin/env python3

'''
Licensed under GPLv3

Written by adis@blad.is
'''

import argparse
from multiprocessing import Process
import multiprocessing
import subprocess
import shlex
import time
import sys
import os
import shutil
import os.path

parser = argparse.ArgumentParser(description='Convert a directory tree from flac to ogg and copy the rest')
parser.add_argument('input', action='store', type=str)
parser.add_argument('output', action='store', type=str)
parser.add_argument('-t', action='store_true', default=multiprocessing.cpu_count(), help='Number of concurrent processes (default <number of cores>)')
parser.add_argument('-q', action='store_true', default=8, help='Oggenc quality (default 8)')
parser.add_argument('-o', action='store_true', default="", help='Oggenc extra options')
args=parser.parse_args()

def run_command(commandline):
    p=subprocess.Popen(shlex.split(commandline),stderr=subprocess.PIPE,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
    if p.wait() != 0:
        sys.stderr.write('ERROR IN: %s\n%s\n\n' % (commandline,p.communicate()[1]))

if __name__ == '__main__':

    #Sanitize input
    if args.input[-1] != "/":
        args.input+="/"
    if args.output[-1] != "/":
        args.output+="/"

    #Does the new dir exist
    if(not os.path.isdir(args.output)):
        os.mkdir(args.output)

    #Create a process pool
    process_pool=list()
    for i in range(0,args.t):
        process_pool.append(Process())

    #Create a queue for commands to be run
    commandlines=list()
    for root, dirs, files in os.walk(args.input):
        for name in dirs:
            print("Creating %s" % (name))
            try: os.mkdir(os.path.join(root, name).replace(args.input,args.output,1))
            except OSError: pass #Already exists                

        #Create directories and copy files
        for name in files:

            input_file=os.path.join(root, name)
            output_file=os.path.join(root, name).replace(args.input,args.output,1)

            if name.split(".")[-1].lower() == "flac":
                output_file=output_file.rstrip("flac")+"ogg"
                commandline="oggenc "
                commandline+="-Q -q %s " % (args.q)
                commandline+=args.o
                commandline+=" -o "+output_file.replace(" ","\ ")+" "+input_file.replace(" ","\ ")
                commandlines.append(commandline)
            else:
                print("Copying %s" % (name))
                shutil.copy(input_file,output_file)

    #Clear queue
    while len(commandlines) > 0:
        for i in range(0,len(process_pool)):
            if process_pool[i].is_alive() == False:
                print(str(len(commandlines)) + " files left to encode")
                process_pool[i] = Process(target=run_command, args=(commandlines.pop(),))
                process_pool[i].start()
        time.sleep(0.1)
