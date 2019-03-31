#!/usr/bin/python3

import argparse
import glob
import json
import os
import re
import sqlite3
from shutil import copyfile


def _get_filename_safely(relative_wildcard):
    """Get absolute filename if it exists.

    Arguments:
        relative_wildcard {str} -- wildcard that will be matched, relative to home directory

    Raises:
        IOError -- if no file was found

    Returns:
        str -- absolute filename
    """

    home = os.getenv('HOME')
    absolute_wildcard = os.path.join(home, relative_wildcard)
    match = glob.glob(absolute_wildcard)
    if not match:
        raise IOError(f'No {absolute_wildcard} found.')
    return match[0]


def _get_db_cursor(db_name, profile, use_copy=True):
    """Return cursor to database.

    Arguments:
        db_name {str} -- {places|cookies} name of the database
        profile {str} -- name of your firefox profile

    Keyword Arguments:
        use_copy {bool} -- should use a copy instead of the original database (default: {True})

    Returns:
        sqlite3.Cursor -- Cursor for the copied database.
    """

    filename = _get_filename_safely(
        f'.mozilla/firefox/{profile}/{db_name}.sqlite')

    if use_copy:
        copy_filename = filename + '_copy'
        copyfile(filename, copy_filename)
        filename = copy_filename

    conn = sqlite3.connect(filename)
    return conn.cursor()


def get_container_identities(profile):
    """Get data about firefox containers.

    Arguments:
        profile {str} -- firefox profile from which to get profiles
    """

    filename = _get_filename_safely(
        f'.mozilla/firefox/{profile}/containers.json')
    with open(filename) as file:
        container_data = json.load(file)
    for identity in container_data['identities']:
        if identity['public']:
            yield identity


def set_youtube_id(profile, origin_attributes, youtube_id):
    cursor = _get_db_cursor('cookies', profile, use_copy=False)
    cursor.execute("update moz_cookies "
                   "set value=? "
                   "where baseDomain='youtube.com' "
                   "    and originAttributes=? "
                   "    and name='VISITOR_INFO1_LIVE';",
                   (youtube_id, origin_attributes))
    cursor.connection.commit()
    cursor.connection.close()


def get_youtube_id(cursor, origin_attributes):
    cursor.execute("select value from moz_cookies "
                   "where baseDomain='youtube.com' "
                   "     and originAttributes=? "
                   "     and name='VISITOR_INFO1_LIVE';",
                   (origin_attributes,))
    result = cursor.fetchone()
    return result[0] if result else None


def _correct_id(raw_id):
    return re.match(r'[0-9A-Za-z-_]{11}', raw_id)


def main(profile):
    print('')
    try:
        from pyfiglet import figlet_format
        print(figlet_format('Bubbles', font='graffiti'))
    except ModuleNotFoundError:
        pass

    # print all youtube identities
    cursor = _get_db_cursor('cookies', profile=profile)
    print(f'{"id":<13} name')
    print('-' * 30)
    raw_id = get_youtube_id(cursor, '')
    if raw_id is not None:
        print(f'{raw_id:<13} default')
    for identity in get_container_identities(profile):
        userContextId = identity['userContextId']
        name = identity['name']
        raw_id = get_youtube_id(cursor, f'^userContextId={userContextId}')
        if raw_id is not None:
            print(f'{raw_id:<13} {name}')
    print('')

    # get container name
    name = input(
        "Type container name, for which you'd like to set youtube id.\n")
    userContextId = None
    for identity in get_container_identities(profile):
        if identity['name'] == name:
            userContextId = identity['userContextId']
            break
    if userContextId is None:
        print('Incorrect name.')
        return

    # get youtube id
    youtube_id = input(
        "Type youtube id you'd like to set. (it's a 11 character text)\n")
    if not _correct_id(youtube_id):
        print('Incorrect id.\n')
        return

    # set youtube id to chosen container
    set_youtube_id(profile, f'^userContextId={userContextId}', youtube_id)
    print('Id set successfully.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--profile', default='*.default',
                        help='name of your firefox profile')
    args = parser.parse_args()

    try:
        main(args.profile)
    except OSError as err:
        print(err)
    except sqlite3.OperationalError:
        print("Couldn't set id, you must close firefox.")
