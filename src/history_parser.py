import glob
import os
import re
import sqlite3
from datetime import datetime
from shutil import copyfile


def _get_db_cursor():
    """Copy database with firefox history, and return it's cursor.

    Returns:
        Cursor for the copied database.

    """
    home = os.getenv('HOME')
    wildcard = '.mozilla/firefox/*.default/places.sqlite'
    absolute_wildcard = os.path.join(home, wildcard)
    history_original = glob.glob(absolute_wildcard)[0]
    history_copy = history_original + '_copy'

    copyfile(history_original, history_copy)
    conn = sqlite3.connect(history_copy)
    return conn.cursor()


def _get_history(time_limit=0):
    """Get latest records from firefox history.

    Args:
        time_limit (float): only get records later than this
                            (it's in UNIX seconds)
                            if not specified, gets all history

    Yields:
        tuple: URL, visit_count, last_visited (in UNIX seconds)

    """
    # database schema:
    # https://developer.mozilla.org/en-US/docs/Mozilla/Tech/Places/Database
    # todo checkout sessionstore.jsonlz4
    # todo check if lastModified really is the time of the last visit
    query = 'select url, visit_count, (lastModified / 1000000) as last_visited ' \
            'from moz_places join moz_annos ' \
            'where last_visited > {};'.format(time_limit)
    cursor = _get_db_cursor()
    cursor.execute(query)

    row = cursor.fetchone()
    while row:
        yield row
        row = cursor.fetchone()


def get_video_records(time_limit=0):
    """Gets latest videos from browser's history.

    Args:
        time_limit (float): only get records later than this
                            (it's in UNIX seconds)
                            if not specified, gets all history

    Yields:
        dict: video info

    """
    history = _get_history(time_limit)
    # todo add support for more browsers?
    pattern = r'https://www\.(you|hook)tube\.com/watch\?v=(.{11})'
    for record in history:
        url = record[0]
        match = re.match(pattern, url)
        if match:
            video_id = match.group(2)
            yield {
                'video_id': video_id,
                'visit_count': record[1],
                'last_visited': record[2]
            }


def _unix_to_timestamp(unix_seconds):   # delete?
    return datetime.fromtimestamp(unix_seconds).isoformat()
