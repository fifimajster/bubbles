import glob
import os
import re
import sqlite3
from collections import namedtuple
from datetime import datetime
from shutil import copyfile


VideoRecord = namedtuple('HistoryRecord', 'video_id visit_count last_visited')


class HistoryParser:
    @classmethod
    def get_db_cursor(cls):
        """Copy database with firefox's history, and return it's cursor.

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

    @classmethod
    def get_history(cls, time_limit):
        # database schema:
        # https://developer.mozilla.org/en-US/docs/Mozilla/Tech/Places/Database
        # todo checkout sessionstore.jsonlz4
        query = 'select url, visit_count, (lastModified / 1000000) as last_visited ' \
                'from moz_places join moz_annos ' \
                'where last_visited > {};'.format(time_limit)
        cursor = cls.get_db_cursor()
        cursor.execute(query)

        row = cursor.fetchone()
        while row:
            yield row
            row = cursor.fetchone()

    @classmethod
    def get_video_records(cls, time_limit=0):
        history = cls.get_history(time_limit)
        pattern = r'https://www\.(you|hook)tube\.com/watch\?v=(.{11})'
        for record in history:
            url = record[0]
            match = re.match(pattern, url)
            if match:
                video_id = match.group(2)
                human_readable_date = datetime.fromtimestamp(record[2]).isoformat()  # for debugging only
                yield VideoRecord(video_id=video_id,
                                  visit_count=record[1],
                                  last_visited=human_readable_date)
