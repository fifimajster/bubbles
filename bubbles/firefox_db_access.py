#!/usr/bin/ipython3 -i
"""
Notes:
    Ensure that no other instances of this script are running
    and no firefox instances with profile 'bubbles'.

"""

import glob
import json
import os
import re
import sqlite3
import subprocess
import textwrap
from shutil import copyfile


PROC_NAME = 'firefox -P bubbles youtube.com'
SAVED_IDS_PATH = os.path.join(os.getenv('HOME'), '.bubbles')


def _get_db_cursor(db_name, profile='bubbles', use_copy=True):
    """Copy database and return it's cursor.

    Args:
        db_name: {places|cookies} name of the database
        profile: name of your firefox profile
        use_copy: should use a copy instead of the original database

    Returns:
        Cursor for the copied database.

    """
    home = os.getenv('HOME')
    wildcard = f'.mozilla/firefox/{profile}/{db_name}.sqlite'
    absolute_wildcard = os.path.join(home, wildcard)
    filename = glob.glob(absolute_wildcard)[0]

    if use_copy:
        copy_filename = filename + '_copy'
        copyfile(filename, copy_filename)
        filename = copy_filename

    conn = sqlite3.connect(filename)
    return conn.cursor()


def set_youtube_id(youtube_id, origin_attributes='', profile='bubbles'):
    cursor = _get_db_cursor('cookies', profile=profile, use_copy=False)
    cursor.execute("update moz_cookies "
                   "set value=? "
                   "where baseDomain='youtube.com' "
                   "    and originAttributes=? "
                   "    and name='VISITOR_INFO1_LIVE';",
                   (youtube_id, origin_attributes))
    cursor.connection.commit()
    cursor.connection.close()


def get_youtube_id(origin_attributes='', profile='bubbles'):
    cursor = _get_db_cursor('cookies', profile=profile)
    cursor.execute("select value from moz_cookies "
                   "where baseDomain='youtube.com' "
                   "     and originAttributes=? "
                   "     and name='VISITOR_INFO1_LIVE';",
                   (origin_attributes,))
    return cursor.fetchone()[0]


class FirefoxInstance:
    def __init__(self):
        # youtube_ids is a list of pairs (id, description)

        with open(SAVED_IDS_PATH, 'r') as json_file:
            self.youtube_ids = json.load(json_file)

        for i, youtube_id in enumerate(self.youtube_ids):
            print(f'{i:<3} {youtube_id[1]}')

        choice = input(textwrap.dedent("""
        type number to choose listed identity
        type 'n' to create a new one
        type id to import existing identity
        \n"""))

        if choice.isdigit():
            raw_id = self.youtube_ids[int(choice)][0]
        elif choice == 'n':
            raw_id = ''
        elif self._correct_id(choice):
            raw_id = choice
        else:
            print('incorrect id')
            return

        set_youtube_id(raw_id)

        self.process = subprocess.Popen(PROC_NAME.split())

    @staticmethod
    def _correct_id(raw_id):
        return re.match(r'[0-9A-Za-z-_]{11}', raw_id)

    def save(self):
        raw_id = get_youtube_id()
        if raw_id in (id_[0] for id_ in self.youtube_ids):
            ans = input('This id already exists. Do you want to update description? [Y/n]')
            if ans not in ['y', 'Y', '']:
                return
            for elem in self.youtube_ids:
                if elem[0] == raw_id:
                    self.youtube_ids.remove(elem)

        description = input('Description:\n')
        self.youtube_ids.append((raw_id, description))

        with open(SAVED_IDS_PATH, 'w') as json_file:
            json.dump(self.youtube_ids, json_file, indent=4)

    def close(self):
        self.process.kill()

    def list_ids(self):
        print(f'{"id":<13} description')
        print('-' * 30)
        for raw_id, description in self.youtube_ids:
            print(f'{raw_id:<13} {description}')


if __name__ == '__main__':
    if not os.path.exists(SAVED_IDS_PATH):
        with open(SAVED_IDS_PATH, 'w') as new_file:
            new_file.write('[]')

    print('')
    try:
        from pyfiglet import figlet_format
        print(figlet_format('Bubbles', font='graffiti'))
        print('')
    except ModuleNotFoundError:
        pass
    f = FirefoxInstance()
    s = f.save
    l = f.list_ids
    print("To save this identity, type 's()'.")
    print("To list all ids, type 'l()'.")
