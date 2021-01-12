from bs4 import BeautifulSoup
import os
import re
import requests
import time


class Website:
    """
    Webサイトの構造についての情報クラス．

    Attributes:
        name (str): Webサイトの名前
        url (str): WebサイトのURL
        target_pattern (str): 抽出したい対象ページのURLに含まれるパターン
        absolute_url (bool): 対象のWebページが絶対パスか否か
        title_tag (str): Webサイトのtitleタグ
        body_tag (str): Webサイトのbodyタグ
    """

    def __init__(self, name: str, url: str, target_pattern: str,
                 absolute_url: bool, title_tag: str, body_tag: str) -> None:
        self.name = name
        self.url = url
        self.target_pattern = target_pattern
        self.absolute_url = absolute_url
        self.title_tag = title_tag
        self.body_tag = body_tag


class Content:
    """
    Webページの共通基底クラス．

    Attributes:
        url (str): WebサイトのURL
        title (str): Webサイトのタイトル
        body (str): Webサイトのbody
        img (set): Webサイトの画像集合
    """

    def __init__(self, url: str, title: str, body: str, img: set) -> None:
        self.url = url
        self.title = title
        self.body = body
        self.img = img

    def print(self) -> None:
        """Webページの情報を出力．"""
        print(f'URL: {self.url}')
        print(f'TITLE: {self.title}')
        print(f'BODY: {self.body}')
        print(f'IMAGE: {len(self.img)}')


class Crawler:
    """
    Webサイトのホームページから内部リンクを見つけ，コンテンツを取得するクラス．

    Attributes:
        site (Website): Webサイトの情報を格納したクラス
        visited (set): 訪問したURLの集合
        images_path (set): 取得する画像の集合
    """

    def __init__(self, site: Website) -> None:
        self.site = site
        self.visited = set()
        self.images_path = set()

    def get_page(self, url: str) -> BeautifulSoup:
        """
        GETリクエストを投げて，WEBページのコンテンツを格納したBeautiful Soupオブジェクトを取得．

        Args:
            url (str): 取得したいWebページのURL

        Returns:
            BeautifulSoup: Webページのコンテンツ
        """

        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            return None
        return BeautifulSoup(req.text, 'html.parser')

    def safe_get(self, page_obj: BeautifulSoup, selector: str) -> str:
        """
        Beautiful Soupオブジェクトとタグ/CSSセレクタからコンテンツ文字列を取得する．
        セレクタでオブジェクトが見つからなかった場合は空文字列を返す．

        Args:
            page_obj (BeautifulSoup): Webページのコンテンツを格納したオブジェクト
            selector (str): 抽出したいデータに関するタグ/CSSセレクタ

        Returns:
            str: コンテンツ文字列
        """

        selected_elems = page_obj.select(selector)

        if selected_elems and (len(selected_elems) > 0):
            return '\n'.join([elem.get_text() for elem in selected_elems])
        else:
            return ''

    def img_download(self, save_dir: str) -> None:
        """
        画像をダウンロードする

        Args:
            save_dir (str): 画像の保存先ディレクトリ
        """

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        for i, path in enumerate(self.images_path):
            img = requests.get(path).content
            with open(os.path.join(save_dir, f'{i}.png'), 'wb') as f:
                f.write(img)

            # 負荷対策，10枚保存すれば1[s]待つ
            if i % 10 == 0:
                time.sleep(1)

    def parse(self, url: str) -> None:
        """
        URLからコンテンツを抽出して，結果を出力

        Args:
            url (str): WebサイトのURL
        """

        bs = self.get_page(url)

        if bs:
            title = self.safe_get(bs, self.site.title_tag)
            body = self.safe_get(bs, self.site.body_tag)

            # 画像のリンクを取得
            img_obj = bs.find_all('a', {'href': re.compile('.*png')})
            images_path = set([img.attrs['href'] for img in img_obj])
            self.images_path |= images_path

            if (title != '') and (body != ''):
                content = Content(url, title, body, images_path)
                content.print()

    def crawl(self) -> None:
        """Webサイトのホームページからのリンクを取得"""

        bs = self.get_page(self.site.url)
        pattern = re.compile(self.site.target_pattern)
        target_pages = bs.find_all('a', href=pattern)
        count = 0

        for target_page in target_pages:
            target_page = target_page.attrs['href']

            # 訪れたページじゃなければ探索
            if target_page not in self.visited:
                self.visited.add(target_page)
                if not self.site.absolute_url:
                    target_page = f'{self.site.url}{target_page}'
                self.parse(target_page)

            # 負荷対策，10アクセスしたら1[s]待つ
            # break
            count += 1
            if count % 10 == 0:
                time.sleep(1)


if __name__ == '__main__':
    save_dir = '../data/'
    idol_list = ['haruka', 'chihaya', 'miki', 'yukiho', 'yayoi', 'makoto',
                 'iori', 'takane', 'ritsuko', 'azusa', 'ami', 'mami', 'hibiki',
                 'mirai', 'shizuka', 'tsubasa', 'kotoha', 'elena', 'minako',
                 'megumi', 'matsuri', 'serika', 'akane', 'anna', 'roco',
                 'yuriko', 'sayoko', 'arisa', 'umi', 'iku', 'tomoka', 'emily',
                 'shiho', 'ayumu', 'hinata', 'kana', 'nao', 'chizuru', 'konomi',
                 'tamaki', 'fuka', 'miya', 'noriko', 'mizuki', 'karen', 'rio',
                 'subaru', 'reika', 'momoko', 'julia', 'tsumugi', 'kaori',
                 'kotori', 'misaki', 'shika', 'reon', 'frederica', 'shiki']

    root = 'https://imas.gamedbs.jp/mlth/'
    base_tag = '#contents-main > section > section > article.d1_3 > '
    title_tag = base_tag + 'h2'
    body_tag = base_tag + 'div:nth-child(3) > ul > li:nth-child(2)'

    for i, name in enumerate(idol_list, start=1):
        million_theater_db = Website('ミリシタDB', root + f'chara/show/{i}/',
                                     target_pattern=f'(chara/show/{i}/)',
                                     absolute_url=True,
                                     title_tag=title_tag,
                                     body_tag=body_tag)
        crawler = Crawler(million_theater_db)
        crawler.crawl()
        crawler.img_download(os.path.join(save_dir, name))
