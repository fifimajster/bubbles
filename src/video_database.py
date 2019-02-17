
import time

from py2neo import Graph, Node, Relationship
from src.youtube_proxy import fetch_recommendations
from multiprocessing.pool import ThreadPool
from src.history_parser import get_video_records


class GraphUpdater:
    def __init__(self):
        """

        Note:
            There should be only one GraphUpdater running at a time.

        """
        # todo start if not started already:
        # neo4j-community-3.5.2/bin/neo4j start
        self.graph = Graph(password='myyyk')
        self.workers = ThreadPool(processes=50)
        if not self._get_meta():
            meta_node = Node('Meta', last_update_from_history=0)
            self.graph.create(meta_node)

    def update_with_browser_history(self):
        """

        Note:
            Can skip some records if time.time() is
            out of sync with firefox timestamps.

        """
        with self.graph.begin() as tx:
            meta = self._get_meta()
            last_update = meta['last_update_from_history']

            for record in get_video_records(last_update):
                new_node = Node('Video', **record)
                # todo check if it already exists
                tx.create(new_node)

            meta['last_update_from_history'] = time.time()
            tx.push(meta)

    def _get_meta(self):
        return self.graph.nodes.match('Meta').first()

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



