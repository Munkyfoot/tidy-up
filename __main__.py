import os
import sys
import glob

ARGS = sys.argv
PATH = os.getcwd()

for arg in ARGS:
    if arg == 'help':
        print('This tool helps with cleaning and organizing storage mediums.',
              'Run the script in the parent directory which you wish to tidy recursively and follow the prompts.')

print("Let's tidy this thing up! First, let's make sure we're in the right place.")
PATH_CORRECT = False
while PATH_CORRECT == False:
    path_input = input(
        "Where do you want to tidy up? (Leave blank to use current directory)\n")
    if len(path_input) == 0:
        path_input = os.getcwd()

    if os.path.isdir(path_input):
        print("Path '{}' is valid. Continue with this path?".format(path_input))
        if input("[y/n] ") == 'y':
            PATH = path_input
            PATH_CORRECT = True
    else:
        print("Path is invalid. Please try again.")

FILES = {}

for full_path in glob.glob(os.path.join(PATH, '**'), recursive=True):
    if os.path.isdir(full_path):
        scan = os.scandir(full_path)
        for item in scan:
            if item.is_file():
                stat = item.stat()
                meta = {
                    'mode' : stat.st_mode,
                    'size' : stat.st_size,
                    'last_mod' : stat.st_mtime,
                    'last_access' : stat.st_atime,
                    'created' : stat.st_ctime
                }
                if item.name in FILES:
                    FILES[item.name].append((item.path, meta))
                else:
                    FILES[item.name] = [(item.path, meta)]

for key in FILES:
    files = FILES[key]
    for f in files:
        path, meta = f
        print("{} --- {} --- {}".format(key, path, meta))
    