import os
from bs4 import BeautifulSoup
import html2text
from pathlib import Path


def html_to_markdown(
        data_dir="data", output_dir="data/markdown",
        ignore_links=False, ignore_images=False):
    # dataディレクトリ内のすべてのHTMLファイルを取得
    data_path = Path(data_dir)
    output_path = Path(output_dir)
    
    html_files = list(data_path.glob('*.html'))
    
    # 各HTMLファイルを処理
    for html_file in html_files:
        # HTMLファイルを読み込み
        html_content = html_file.read_text(encoding='utf-8')
        
        # BeautifulSoupでパース
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 不要なタグを削除
        for tag in soup(['script', 'style', 'header', 'footer', 'nav']):
            tag.decompose()
            
        # HTML to Markdown変換
        h = html2text.HTML2Text()
        h.ignore_links = ignore_links
        h.ignore_images = ignore_images
        markdown_content = h.handle(str(soup))
        
        # outputディレクトリが存在しない場合は作成
        output_path.mkdir(parents=True, exist_ok=True)

        # Markdownファイルとして保存
        markdown_file = output_path / f"{html_file.stem}.md"
        markdown_file.write_text(markdown_content, encoding='utf-8')
            
        print(f"変換完了: {html_file.name} -> {markdown_file.name}")


if __name__ == '__main__':

    # 変換実行
    html_to_markdown()
