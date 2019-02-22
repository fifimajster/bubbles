import logging
import os
import shlex
import subprocess
import time
from datetime import datetime

import neobolt
from py2neo import Node

logger = logging.getLogger('bubbles')


def run_neo4j_command(cmd):
    """Run command using neo4j binary.

    Args:
        cmd (str): { console | start | stop | restart | status | version }

    Returns:
        int: shell return code

    """
    neo4j_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'neo4j-community-3.5.2',
        'bin/neo4j'
        )
    full_cmd = f'{neo4j_path} {cmd}'
    parsed_cmd = shlex.split(full_cmd)
    return subprocess.call(parsed_cmd)


def ensure_neo4j_running():
    """If neo4j server isn't running, start it.

    Raises:
        RuntimeError: if server couldn't be started

    """
    if run_neo4j_command('status') == 0:
        return
    ret_code = run_neo4j_command('start')
    if ret_code != 0:
        raise RuntimeError("Couldn't start neo4j.")


def unix_to_timestamp(unix_seconds):
    """Convert unix time to human readable format.

    Args:
        unix_seconds (float)

    Returns:
        str: timestamp

    """
    return datetime.fromtimestamp(unix_seconds).isoformat()


def wait_for_connection(graph):
    logger.info('Waiting for database connection...')
    while True:
        try:
            graph.begin()
            logger.info('Database connected.')
            return
        except neobolt.exceptions.ServiceUnavailable:
            time.sleep(0.1)


def setup_db_schema(graph):
    # Following part requires Neo4j Enterprise Edition :(
    # exist = 'CREATE CONSTRAINT ON (a:%s) ASSERT exists(a.%s)'
    # graph.run(exist % ('Video', 'video_id'))
    # graph.run(exist % ('Video', 'watch_dist'))
    # graph.run(exist % ('Video', 'recomms_update'))
    # graph.run(exist % ('Meta', 'last_update_from_history'))

    graph.schema.create_index('Video', 'video_id', 'watch_dist')

    graph.schema.create_uniqueness_constraint('Video', 'video_id')

    meta_node = Node('Meta', last_update_from_history=0)
    graph.create(meta_node)
    logger.info('Database schema created.')


graph_legend = """
    [node types]
    Meta:
        last_update_from_history (mandatory)
        
    Video:
        video_id (unique) (mandatory)
        title 
        visit_count
        last_visited
        watch_dist (mandatory)
        recomms_update (mandatory)
    
    """
