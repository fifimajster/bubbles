import shlex
import subprocess
import time
import logging

from py2neo import Graph, Node, Relationship
from src.youtube_proxy import fetch_recommendations
from multiprocessing.pool import ThreadPool
from src.history_parser import get_video_records
from src.common import ensure_neo4j_running, unix_to_timestamp


# logging.getLogger().setLevel(logging.DEBUG) # just for testing


class GraphUpdater:
    def __init__(self):
        """

        Note:
            There should be only one GraphUpdater running at a time.

        """
        ensure_neo4j_running()
        self.graph = Graph(password='myyyk')
        self.workers = ThreadPool(processes=50)
        if not self._get_node('Meta'):
            meta_node = Node('Meta', last_update_from_history=0)
            self.graph.create(meta_node)

    def update_with_browser_history(self, all_records=False):
        """

        Note:
            Can skip some records if time.time() is
            out of sync with firefox timestamps.

        """
        with self.graph.begin() as tx:
            meta = self._get_node('Meta')
            last_update = meta['last_update_from_history'] \
                if not all_records else 0

            timestamp = unix_to_timestamp(last_update)
            logging.info(f'Updating with records younger than {timestamp}...')

            for record in get_video_records(last_update):
                self._insert_record(tx, record)

            meta['last_update_from_history'] = time.time()
            tx.push(meta)

    def _insert_record(self, tx, record):
        node = self._get_node('Video', video_id=record['video_id'])
        if node is None:
            new_node = Node('Video', **record, dist_from_watched=0)
            tx.create(new_node)
            logging.debug(f'Created new node {new_node}')
        else:
            # such video already exists so only update
            node.update(record)
            tx.push(node)
            logging.debug(f'Updated node {node}')

    def _get_node(self, node_type, **kwargs):
        return self.graph.nodes.match(node_type, **kwargs).first()

    # def save_recommendations(self, video_record):
    #     tx = self.graph.begin()
    #     watched_video = Node('Video',
    #                          **video_record,
    #                          watched=True)
    #     tx.create(watched_video)
    #     recommendations = fetch_recommendations(watched_video.)
    #     for id, title in []:
    #         pass
    #
    #
    #     tx.commit()



