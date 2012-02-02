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
from pipes import quote

def run_command(commandline):
    p=subprocess.Popen(shlex.split(commandline),stderr=subprocess.PIPE,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
    if p.wait() != 0:
        sys.stderr.write('ERROR IN: %s\n%s\n\n' % (commandline,p.communicate()[1]))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert a directory tree from flac to ogg and copy the rest')
    parser.add_argument('input', action='store', type=str, help='<old directory>')
    parser.add_argument('output', action='store', nargs='?',type=str, default=None, help='<new directory (default == same name as old)>')
    parser.add_argument('-t', action='store', type=int, default=multiprocessing.cpu_count(), help='Number of concurrent processes (default <number of cores>)')
    parser.add_argument('-q', action='store', type=str, default=8, help='Oggenc quality (default 8)')
    parser.add_argument('-o', action='store', type=str, default='', help='Oggenc extra options')
    parser.add_argument('-e', action='append', type=str, default=[], help='Extra file extension to recode')
    args=parser.parse_args()

    #Sanitize input
    if args.output == None:
        args.output = os.path.basename(args.input.rstrip("/"))
    if args.input[-1] != '/':
        args.input+='/'
    if args.output[-1] != '/':
        args.output+='/'

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
            print('Creating %s' % (name))
            try: os.mkdir(os.path.join(root, name).replace(args.input,args.output,1))
            except OSError: 
                if(not os.path.isdir(os.path.join(root, name).replace(args.input,args.output,1))):
                    sys.stderr.write("Could not create %s\n" % (os.path.join(root, name).replace(args.input,args.output,1)))
                    exit(1)

        #Create directories and copy files
        for name in files:
            input_file=os.path.join(root, name)
            output_file=os.path.join(root, name).replace(args.input,args.output,1)

            if name.split('.')[-1].lower() in ['wav','aiff','flac','pcm','raw']+args.e:
                output_file=output_file.rpartition('.')[0]+'.ogg'
                commandlines.append('oggenc -Q -q %s %s -o %s %s' % (args.q,args.o,quote(output_file),quote(input_file)))
            else:
                print("Copying %s" % (input_file))
                shutil.copy(input_file,output_file)

    #Clear queue
    total_commands=str(len(commandlines))
    while len(commandlines) > 0:
        for i in range(0,len(process_pool)):
            if process_pool[i].is_alive() == False:
                sys.stdout.write('\r%s/%s files left to encode' % (str(len(commandlines)),total_commands))
                process_pool[i] = Process(target=run_command, args=(commandlines.pop(),))
                process_pool[i].start()
        time.sleep(0.1)
    print("")
