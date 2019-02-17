import re

import requests
from bs4 import BeautifulSoup


def fetch_recommendations(video_id):
    """Fetch youtube recommendations of a given video.

    Args:
        video_id (str): part of the url of the video that comes after
                        'https://youtube.com/watch?v='

    Yields:
        tuple: id of the recommended video, it's title

    """
    url = 'https://youtube.com/watch?v=' + video_id
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    lines = re.findall('"/watch\?v=.*title.*',
                       soup.prettify())
    for line in lines:
        url_match = re.search('/watch\?v=(.{11})', line)
        title_match = re.search('title="(.*)">', line)
        video_id = url_match.group(1)
        title = title_match.group(1)
        yield video_id, title
