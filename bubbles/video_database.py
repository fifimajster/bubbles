import logging
import time
from multiprocessing.pool import ThreadPool

from py2neo import Graph, Node, Relationship

from bubbles.common import ensure_neo4j_running, unix_to_timestamp, wait_for_connection, setup_db_schema
from bubbles.history_parser import get_video_records
from bubbles.youtube_proxy import fetch_recomms

logger = logging.getLogger('bubbles')

Recommends = Relationship.type('RECOMMENDS')


class GraphUpdater:
    def __init__(self):
        """

        Note:
            There should be only one GraphUpdater running at a time.

        """
        ensure_neo4j_running()
        self.graph = Graph(password='myyyk')
        wait_for_connection(self.graph)
        self.workers = ThreadPool(processes=50)
        if not self._get_node('Meta'):
            setup_db_schema(self.graph)

    def update_with_browser_history(self, only_new_records=True):
        """

        Note:
            Can skip some records if time.time() is
            out of sync with firefox timestamps.

        """
        meta = self._get_node('Meta')
        last_update = meta['last_update_from_history'] \
            if only_new_records else 0

        timestamp = unix_to_timestamp(last_update)
        logger.info(f'Updating with records younger than {timestamp}...')

        for video_info in get_video_records(last_update):
            # todo maybe first put them all to some buffer and then insert
            video_info['watch_dist'] = 0
            tx = self.graph.begin(autocommit=True)
            self._update_record(tx, video_info)

        meta['last_update_from_history'] = time.time()
        self.graph.push(meta)

    def update_recomms(self, node):
        watch_dist = node['watch_dist']
        with self.graph.begin() as tx:
            for video_id, title in fetch_recomms(node['video_id']):
                video_info = {
                    'video_id': video_id,
                    'title': title,
                    'watch_dist': watch_dist + 1
                }
                recommended_node = self._update_record(tx, video_info)
                rel = Recommends(node, recommended_node)
                tx.create(rel)
            node['recomms_update'] = time.time()
            tx.push(node)

    def _update_record(self, tx, info):
        node = self._get_node('Video',
                              video_id=info['video_id'])
        if node is None:
            # create new node
            new_node = Node('Video', **info, recomms_update=0)
            tx.create(new_node)
            logger.debug(f'Created new node {new_node}')
            return new_node
        else:
            # update node
            # distance from watched can only go down
            # todo update visit_count
            info['watch_dist'] = min(info['watch_dist'],
                                     node['watch_dist'])
            node.update(info)
            tx.push(node)
            logger.debug(f'Updated node {node}')
            return node

    def _get_node(self, node_type, **kwargs):
        """Returns one node from database that matches given info.

        If nothing matched, returns None.

        Args:
            node_type (str): { Video | Meta }
            **kwargs: node fields that will be matched

        Returns:
            Node | None: -

        """
        match = self.graph.nodes.match(node_type, **kwargs)
        return match.first()
