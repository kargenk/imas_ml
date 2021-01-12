from bs4 import BeautifulSoup
import re
from urllib.error import HTTPError
from urllib.request import urlopen


def get_title(url: str) -> str:
    """get web page title with h1 tag.

    Args:
        url (str): web page url

    Returns:
        str: title of web page

    Examples:
        >>> get_title('https://million-comments.herokuapp.com/')
        <h1>ログイン</h1>
    """

    # サーバにアクセスできたか
    try:
        html = urlopen(url)
    except HTTPError as e:
        print(e)
        return None

    # ページのコンテンツを取得できたか
    try:
        bs = BeautifulSoup(html.read(), 'html.parser')
        title = bs.body.h1
    except AttributeError as e:
        print(e)
        return None

    return title


def get_idol_links(url: str, idol: str = '') -> list:
    """
    get character page links with a href tag.
    if not set idol name, get all links.

    Args:
        url (str): web page url
        idol (str, optional): idol name, defaults to ''

    Returns:
        list: links from url

    Examples:
        >>> get_idol_links('https://imas.gamedbs.jp/mlth/', '白石 紬')
        ['https://imas.gamedbs.jp/mlth/chara/show/51']
    """

    html = urlopen(url)
    bs = BeautifulSoup(html.read(), 'html.parser')
    results = bs.find_all('a', {'title': re.compile(f'.*{idol}.*')})
    links = [res.attrs['href'] for res in results]

    return links


if __name__ == '__main__':
    url = 'https://imas.gamedbs.jp/mlth/'  # ミリシタDB
    title = get_title(url)
    print(title)

    print(get_idol_links(url, '白石 紬'))
