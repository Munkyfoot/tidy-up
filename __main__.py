import os
import sys
import glob
import filecmp

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

print("Scanning for duplicates...")

FILES = {}

for full_path in glob.glob(os.path.join(PATH, '**'), recursive=True):
    if os.path.isdir(full_path):
        scan = os.scandir(full_path)
        for item in scan:
            if item.is_file():
                stat = item.stat()
                meta = {
                    'mode': stat.st_mode,
                    'size': stat.st_size,
                    'last_mod': stat.st_mtime,
                    'last_access': stat.st_atime,
                    'created': stat.st_ctime
                }
                if item.name in FILES:
                    FILES[item.name].append((item.path, meta))
                else:
                    FILES[item.name] = [(item.path, meta)]

DUPLICATES = []
DUPLICATES_FULL_INFO = []

for key in FILES:
    files = FILES[key]
    if len(files) > 1:
        clones = []
        diff = []
        dups = []
        for f in files:
            f_path, f_meta = f
            dups.append(f)
            for c in files:
                c_path, c_meta = c
                if f_path == c_path:
                    continue

                if filecmp.cmp(f_path, c_path):
                    if f not in clones:
                        clones.append(f)
                else:
                    if f not in diff:
                        diff.append(f)

        outliers = [o for o in diff if o not in clones]

        DUPLICATES.append(tuple(dups))
        DUPLICATES_FULL_INFO.append({
            'clones': clones,
            'outliers': outliers
        })

DUPLICATE_COUNT = 0

for dups in DUPLICATES:
    DUPLICATE_COUNT += len(dups)

if DUPLICATE_COUNT > 0:
    print("You have {} instance{} of duplication over {} file{}.".format(len(DUPLICATES), [
        '', 's'][int(len(DUPLICATES) > 1)], DUPLICATE_COUNT, ['', 's'][int(DUPLICATE_COUNT > 1)]))

    print("How would you like to clean up these duplicates?",
          "0 - Do nothing.",
          "1 - Add 'dup' tag to file names (option to mark one as preferred)",
          "2 - Remove duplicates (select one to save)",
          sep='\n')

    choosing = True
    while choosing:
        choice = int(input())
        if choice in [0, 1, 2]:
            choosing = False
        else:
            print("Invalid choice.")

    if choice == 0:
        print("You have chosen to do nothing.")
        exit()
    elif choice in [1, 2]:
        if choice == 1:
            print("You have chosen to tag the file names. Would you like to mark a preferred file for each set of duplicates?")
            set_preferred = input("[y/n] ") == 'y'
        elif choice == 2:
            print(
                "You have chosen to remove unwanted duplicates. You will need to mark preferred files to save.")
            set_preferred = True

        if set_preferred:
            print(
                "Would you like to automatically mark the duplicates with the largest file size as preferred?")
            auto_set_preferred = input("[y/n] ") == 'y'

        for dups in DUPLICATES:
            preferred = None
            if set_preferred:
                if auto_set_preferred:
                    preferred = sorted(dups, key=lambda x: x[1]['size'], reverse=True)[0]
                else:
                    print("Choose the preferred file from this set of duplicates:")
                    for i, f in enumerate(dups):
                        print('{} - {}'.format(i, f))

                    choosing = True
                    while choosing:
                        pref = int(input())
                        if pref in range(len(dups)):
                            preferred = dups[pref]
                            choosing = False
                        else:
                            print("Invalid choice.")

            if choice == 1:
                print("Renaming files...")
            elif choice == 2:
                print("Removing unwanted duplicates...")

            for i, f in enumerate(dups):
                path, meta = f
                if choice == 1:
                    filename = path.split(os.sep)[-1]
                    path_to = path[:len(path) - len(filename)]
                    modified = "{}{}{}".format(
                        path_to, ['dup_', 'dup_pref_'][int(f == preferred)], filename)
                    os.rename(path, modified)
                if choice == 2:
                    if f != preferred:
                        os.remove(path)

            print("Done!")

        print("All finished! Looking nice and clean in here.")
else:
    print("No duplicates found. It looks clean in here!")
