import shlex
import subprocess
from datetime import datetime


def run_neo4j_command(cmd):
    """Run command using neo4j binary.

    Args:
        cmd (str): { console | start | stop | restart | status | version }

    Returns:
        int: shell return code

    """
    neo4j_dir = 'neo4j-community-3.5.2'
    full_cmd = f'{neo4j_dir}/bin/neo4j {cmd}'
    parsed_cmd = shlex.split(full_cmd)
    return subprocess.call(parsed_cmd)


def ensure_neo4j_running():
    if run_neo4j_command('status') == 0:
        return
    ret_code = run_neo4j_command('start')
    if ret_code != 0:
        raise RuntimeError("Couldn't start neo4j.")


def unix_to_timestamp(unix_seconds):   # delete?
    return datetime.fromtimestamp(unix_seconds).isoformat()
