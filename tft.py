#!/usr/bin/python
 
# Copyright 2015 Sascha Peilicke
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'Sascha Peilicke <saschpe@mailbox.org>'
__version__ = '0.0.2'

import argparse
import datetime
import locale
import os
import re
import sys
import subprocess

# Not set by default on Windows:
locale.setlocale(locale.LC_ALL, '')


DEFAULT_TFS_ITEMSPEC_PREFIX = '$/HDE/Branches/404'

TF_DIR_DELETED_FOLDERS_TEMPLATE = 'tf dir "{0}" /folders /deleted'
TF_INFO_TEMPLATE = 'tf info "{0}"'
TF_INFO_LAST_MODIFIED_RE = re.compile('Last modified: (.*)\r')
TF_DESTROY_TEMPLATE = 'tf destroy "{0}"'


def destroy(args):
    tf_dir_cmd = TF_DIR_DELETED_FOLDERS_TEMPLATE.format(args.itemspec)
    if args.verbose and args.verbose > 0:
        print('Executing \'{0}\''.format(tf_dir_cmd))
    try:
        output = str(subprocess.check_output(tf_dir_cmd, shell=True), 'cp1252')
        if (output.startswith('No items found under')):
            if args.verbose:
                print(output[:-1])  # Print output minus last newline
            return
    except subprocess.CalledProcessError as e:
        if args.verbose:
            print(str(e.output[:-1], 'cp1252'))  # Print output minus last newline
        return
    lines = output.split('\r\n')
    # Containing folder is always the first output line of 'tf dir'
    absolute_folder_path = lines[0][:-1]
    folders_to_recurse = [] # Cache folders for breadth-first recursion
    for line in lines[1:]:
        if len(line) is 0:
            break; # Reached the end of the listing, only metadata follows...
        elif ';X' in line:
            item = line.split(';X')[0][1:]  # Items look like '$123;X456', we care for 123
            absolute_item_path = '{0}/{1}'.format(absolute_folder_path, item)
            tf_info_cmd = TF_INFO_TEMPLATE.format(absolute_item_path)
            output = str(subprocess.check_output(tf_info_cmd, shell=True), 'cp1252')
            result = TF_INFO_LAST_MODIFIED_RE.search(output)
            if (result):
                delta = datetime.datetime.now() - datetime.datetime.strptime(result.group(1), '%A, %d. %B %Y %H:%M:%S')
                if delta.days > args.destroy_after:
                    tf_destroy_cmd = TF_DESTROY_TEMPLATE.format(absolute_item_path)
                    if args.no_prompt:
                        tf_destroy_cmd += ' /noprompt'
                    if args.verbose and args.verbose < 2:
                        tf_destroy_cmd += ' /silent'
                    if args.dry_run:
                        print('Dry run: {0} ({1} days old), executing \'{2}\''.format(absolute_item_path, delta.days, tf_destroy_cmd))
                    else:
                        if args.verbose and args.verbose > 0:
                            print('Found {0} ({1} days old), executing \'{2}\''.format(absolute_item_path, delta.days, tf_destroy_cmd))
                        subprocess.call(tf_destroy_cmd, stdin=sys.stdin, stdout=sys.stdout, shell=True)
        elif args.recursive: # Must be a folder, store for recursion (if desired)
            folders_to_recurse.append('{0}/{1}'.format(absolute_folder_path, line[1:]))
    if len(folders_to_recurse) > 0:
        for folder in folders_to_recurse:
            args.itemspec = folder
            destroy(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Team Foundation Server commandline utility. Implements some useful commands otherwise missing from tf.exe.')
    parser.add_argument('-v', '--verbose', action='count', help='enable verbose output [-v or -vv]')
    parser.add_argument('-n', '--no-prompt', action='store_true', help='do not ask for confirmation')
    parser.add_argument('-D', '--dry-run', action='store_true', help='only print commands, dont execute them.')

    subparsers = parser.add_subparsers(help='sub-command help')

    parser_destroy = subparsers.add_parser('destroy', help='permanently destroy itemspecs')
    parser_destroy.add_argument('itemspec', nargs='?', default=DEFAULT_TFS_ITEMSPEC_PREFIX, help='TFS itemspec [default: {0}]'.format(DEFAULT_TFS_ITEMSPEC_PREFIX))
    parser_destroy.add_argument('-r', '--recursive', action='store_true', help='recursively destroy')
    parser_destroy.add_argument('-d', '--destroy-after', default=30, type=int, help='destroy itemspecs older than N days [default: 30]')
    parser_destroy.set_defaults(func=destroy)
    
    args = parser.parse_args()
    args.func(args)
