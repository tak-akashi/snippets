# requestsとBeautifulSoupを使って、特定のURLのHTML及び傘下の全てを再帰的にスクレイピングを行うプログラム。
# ただし、指定したURLの傘下のみをスクレイピングする。
# 例: https://support.apple.com/ja-jp/guide/iphone の場合、
# https://support.apple.com/ja-jp/guide/iphone/ios18 等の下位URLのみを対象とする。
# また、サーバーに負荷をかけないよう、リクエスト間隔を2秒空ける。
# スクレイピングしたHTMLは、data/フォルダに保存される。
# また、エラーが発生した場合は、エラーメッセージを表示する。
# visitedに追加が一定回数以上ない場合には、プログラムを終了する。
# 同じURLを連続で訪問した回数をカウントし、閾値を超えたら終了する。
# 一定回数以上同じURLを訪問した場合は、スクレイピングを終了する。

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path
import time


consecutive_duplicates = 0  # 連続重複カウンター

def scrape_site(base_url, visited=None, max_depth=3, 
                max_consecutive_duplicates=10):
    global consecutive_duplicates
    
    if visited is None:
        visited = set()
    
    if max_depth <= 0:
        return
        
    if base_url in visited:
        consecutive_duplicates += 1
        if consecutive_duplicates >= max_consecutive_duplicates:
            print(f"連続重複回数が{max_consecutive_duplicates}回を超えたため、スクレイピングを終了します。")
            return
        return
    else:
        consecutive_duplicates = 0  # 新しいURLの場合はカウンターをリセット
        
    visited.add(base_url)
    
    try:
        # サイトへのリクエスト
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(base_url, headers=headers, timeout=30)
        response.raise_for_status()  # エラーチェック
        
        # レスポンスのエンコーディングを確認
        response.encoding = response.apparent_encoding
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # HTMLコンテンツの保存
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)  # dataディレクトリが存在しない場合は作成
        domain = urlparse(base_url).netloc
        filename = data_dir / f"scrape_{domain}_{abs(hash(base_url))}.html"
        filename.write_text(response.text, encoding="utf-8")
            
        # リンクの抽出と再帰的スクレイピング
        base_path = urlparse(base_url).path
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                absolute_url = urljoin(base_url, href)
                parsed_url = urlparse(absolute_url)
                # 同じドメインで、かつベースURLのパスで始まるURLのみを処理
                if (parsed_url.netloc == urlparse(base_url).netloc and 
                    parsed_url.path.startswith(base_path)):
                    print(f"スクレイピング中: {absolute_url}")
                    time.sleep(2)  # サーバー負荷軽減のための待機
                    scrape_site(absolute_url, visited, max_depth-1)
                    
    except requests.exceptions.RequestException as e:
        print(f"リクエストエラー: {base_url} - {str(e)}")
    except Exception as e:
        print(f"エラーが発生しました: {base_url} - {str(e)}")


if __name__ == '__main__':

    url = "https://" # scraping対象のURL


    MAX_DEPTH = 3  # 再帰スクレイピングの最大深さ
    MAX_CONSECUTIVE_DUPLICATES = 10  # 連続で重複したURLの最大許容回数

    scrape_site(url, 
                visited=None, 
                max_depth=MAX_DEPTH, 
                max_consecutive_duplicates=MAX_CONSECUTIVE_DUPLICATES)
