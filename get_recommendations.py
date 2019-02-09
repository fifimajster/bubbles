import re

import requests
from bs4 import BeautifulSoup


def get_recommendations(url):
    """Get youtube recommendations of a given video.

    Args:
        url (str): url of the video for which to find recommendations;
                   has the form: /watch?v=xxxxxxxxxxx

    Yields:
        tuple: (url of the recommended video, it's title)

    """
    full_url = 'https://youtube.com' + url
    response = requests.get(full_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    lines = re.findall('"/watch\?v=.*title.*',
                       soup.prettify())
    for line in lines:
        url_match = re.search('/watch\?v=.{11}', line)
        title_match = re.search('title="(.*)">', line)
        yield url_match.group(0), title_match.group(1)


# if __name__ == '__main__':
#     url = sys.argv[1]
#     recoms = get_recommendations(url)
#     for recom in recoms:
#         print(recom)
