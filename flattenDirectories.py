#!/usr/bin/env python

import os
import sys
import shutil
from argparse import ArgumentParser

parser = ArgumentParser(description='Flatten a directory.')
parser.add_argument('dest', help='destination directory')
args = parser.parse_args()

source_dir = os.getcwd()
destination_dir = args.dest

for root, dirs, files in os.walk(source_dir):
    for filename in files:
        source_path = os.path.join(root, filename)
        destination_path = os.path.join(destination_dir, filename)
        print('Copying {} to {}'.format(source_path, destination_path))
        shutil.copy(source_path, destination_path)