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

print("Scanning files...")

FILES = []

for full_path in glob.glob(os.path.join(PATH, '**'), recursive=True):
    if os.path.isdir(full_path):
        scan = os.scandir(full_path)
        for item in scan:
            if item.is_file():
                stat = item.stat()
                item_info = {
                    'path' : item.path,
                    'name' : item.name,
                    'size' : stat.st_size
                }
                FILES.append(item_info)

print("{} file{} found.".format(len(FILES), ['', 's'][int(len(FILES) > 1)]))

print("Would you like to search for duplicates?")

if input("[y/n] ") == 'y':
    print("Looking for duplicates...")

    DUPLICATE_CHECK = {}

    for item in FILES:
        if item['name'] in DUPLICATE_CHECK:
            DUPLICATE_CHECK[item['name']].append(item)
        else:
            DUPLICATE_CHECK[item['name']] = [item]

    DUPLICATE_COUNT = 0
    DUPLICATES = []

    for name in DUPLICATE_CHECK:
        count = len(DUPLICATE_CHECK[name])
        if count > 1:
            DUPLICATE_COUNT += count
            DUPLICATES.append(tuple(DUPLICATE_CHECK[name]))

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
        elif choice in [1, 2]:
            if choice == 1:
                print(
                    "You have chosen to tag the file names. Would you like to mark a preferred file for each set of duplicates?")
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
                        preferred = sorted(
                            dups, key=lambda x: x['size'], reverse=True)[0]
                    else:
                        print(
                            "Choose the preferred file from this set of duplicates:")
                        for i, item in enumerate(dups):
                            print('{} - {}'.format(i, item))

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

                for i, item in enumerate(dups):
                    path = item['path']
                    if choice == 1:
                        filename = path.split(os.sep)[-1]
                        path_to = path[:len(path) - len(filename)]
                        mod_name = "{}{}".format(
                            ['dup_', 'dup_pref_'][int(item == preferred)], filename)
                        modified = "{}{}".format(path_to, mod_name)
                        os.rename(path, modified)
                        item['path'] = modified
                        item['name'] = mod_name
                    if choice == 2:
                        if item != preferred:
                            os.remove(path)
                            FILES.remove(item)

                print("Done!")

            print("All finished! Looking nice and clean in here.")
    else:
        print("No duplicates found. It looks clean in here!")

print("Would you like to organize your files by type? (WARNING: Duplicate files will be renamed making them unable to be easily removed in the future. If you believe there are duplicate files please be sure to remove them prior to organizing by type.)")
if input("[y/n] ") == 'y':
    print("Organizing files...")
    FILE_PATH_BY_TYPE = {}

    for item in FILES:
        file_type = item['name'].split('.')[-1]
        if file_type in FILE_PATH_BY_TYPE:
            FILE_PATH_BY_TYPE[file_type].append(item)
        else:
            FILE_PATH_BY_TYPE[file_type] = [item]

    for f_type in FILE_PATH_BY_TYPE:
        type_dir = os.path.join(PATH, f_type)
        os.makedirs(type_dir)
        files = FILE_PATH_BY_TYPE[f_type]
        for i, item in enumerate(files):
            os.rename(item['path'], os.path.join(
                type_dir, item['path'].replace(os.sep, '+')))

print("All done here. Thanks for using tidy-up.")
