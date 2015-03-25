#!/usr/bin/env python3

'''
Licensed under GPLv3

Written by adis@blad.is
'''

import concurrent.futures
from pipes import quote
import multiprocessing
import subprocess
import argparse
import os.path
import shutil
import shlex
import time
import sys
import os


def run_command(cmd):
    p = subprocess.Popen(shlex.split(cmd),
                         stderr=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE)
    if p.wait() != 0:
        sys.stderr.write('ERROR IN: %s\n%s\n\n' % (cmd, p.communicate()[1]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert directory tree from flac -> ogg')
    parser.add_argument('input', action='store', type=str, help='<old directory>')
    parser.add_argument('output', action='store', nargs='?', type=str, default=None, help='<new directory (default == same name as old)>')
    parser.add_argument('-t', action='store', type=int, default=multiprocessing.cpu_count(), help='Number of concurrent processes (default <number of cores>)')
    parser.add_argument('-q', action='store', type=str, default=8, help='Oggenc quality (default 8)')
    parser.add_argument('-o', action='store', type=str, default='', help='Oggenc extra options')
    parser.add_argument('-e', action='append', type=str, default=[], help='Extra file extension to recode')
    args = parser.parse_args()

    # Sanitize input
    if args.output is None:
        args.output = os.path.basename(args.input.rstrip('/'))
    if not args.input.endswith('/'):
        args.input += '/'
    if not args.output.endswith('/'):
        args.output += '/'

    if(not os.path.isdir(args.output)):
        os.mkdir(args.output)

    # Create a queue for commands to be run
    commandlines = []
    for root, dirs, files in os.walk(args.input):

        print('Creating dirs')
        for name in dirs:
            try:
                os.mkdir(os.path.join(root, name).replace(args.input, args.output, 1))
            except OSError:
                if(not os.path.isdir(os.path.join(root, name).replace(args.input, args.output, 1))):
                    sys.stderr.write('Could not create %s\n' % (os.path.join(root, name).replace(args.input, args.output, 1)))
                    exit(1)

        # Create directories and copy files
        print('Copying files')
        for name in files:
            input_file = os.path.join(root, name)
            output_file = os.path.join(root, name).replace(args.input, args.output, 1)

            if name.split('.')[-1].lower() in ['wav', 'aiff', 'flac', 'pcm', 'raw']+args.e:
                output_file = output_file.rpartition('.')[0] + '.ogg'
                commandlines.append('oggenc -Q -q %s %s -o %s %s' % (args.q, args.o, quote(output_file), quote(input_file)))
            else:
                shutil.copy(input_file, output_file)

    print('Converting files')
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.t) as e:
        for cmd in commandlines:
            e.submit(run_command, cmd)
