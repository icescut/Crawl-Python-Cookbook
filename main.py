# encoding: utf-8

from urllib.request import urlopen
from bs4 import BeautifulSoup
from config import *
import os, re


def get_first_level_title(div):
    """
    遍历一级标题，保存标题及链接
    """
    global contents, current_level
    for li in div.find_all("li", {"class": "toctree-l1"}):
        item = {}
        # 1. 标题
        item["chapter"] = li.a.string
        # 2. 添加层级，方便排序
        href = li.a["href"]
        if href == COPYRIGHT_HREF or href == PREFACE_HREF:
            item["level"] = (0, 0)
            current_level = 0
        else:
            current_level += 1
            item["level"] = (current_level, 0)
        # 3. 章节页面url
        item["url"] = BASE_URL + href
        contents.append(item)

        # 获取子章节标题
        get_second_level_title(li.find_all("li", {"class": "toctree-l2"}))


def get_second_level_title(lis):
    """
    遍历子章节标题，保存标题及链接
    """
    global contents, current_level
    sub_level = 1
    for li in lis:
        item = {}
        # 1. 标题
        item["chapter"] = li.a.string
        # 2. 添加层级，方便排序
        item["level"] = (current_level, sub_level)
        sub_level += 1
        # 3. 章节页面url
        item["url"] = BASE_URL + li.a["href"]
        contents.append(item)


def save_to_html(item):
    # 0. 获取html内容
    html = urlopen(item["url"])
    bs_obj = BeautifulSoup(html, "html.parser")

    # 1. 获取内容主体
    rst_content = bs_obj.find("div", {"class": "rst-content"})
    # 2. 删除导航及底部信息
    rst_content.find("div", {"role": "navigation"}).decompose()
    rst_content.footer.decompose()

    # 3. 如果是子章节，将H1替换为H2，将H2替换为H3
    level = item["level"][0]
    sub_level = item["level"][1]

    if level != 0:
        for h2 in rst_content.find_all("h2"):
            h2.name = "h3"
        for h1 in rst_content.find_all("h1"):
            h1.name = "h2"

    # 4. 加上头尾
    body_part = rst_content.prettify()
    if sub_level != 0:
        header_part = HTML_HEADER % bs_obj.h2.get_text()
    else:
        header_part = HTML_HEADER % bs_obj.h1.get_text()
    footer_part = HTML_FOOTER

    # 保存到文件
    # return header_part + body_part + footer_part
    file_name = correct_file_name(str(level) + "-" + str(sub_level) + "-" + item["chapter"] + ".html")
    file_name = DOWNLOAD_PATH + os.sep + file_name
    with open(os.path.abspath(file_name), "w", encoding="utf-8") as f:
        f.write(header_part + body_part + footer_part)


def make_download_dir():
    if os.path.exists(DOWNLOAD_PATH) == False:
        os.makedirs(DOWNLOAD_PATH)


def correct_file_name(file_name):
    rex = re.compile(r'[\\/:*?"<>|\r\n]+')
    invalid_strs = rex.findall(file_name)
    if invalid_strs:
        for invalid_str in invalid_strs:
            file_name = file_name.replace(invalid_str, '_')
    return file_name

# def write_to_html()

if __name__ == "__main__":

    # item = {
    #     "chapter": "1.1 解压序列赋值给多个变量",
    #     "url": "http://python3-cookbook.readthedocs.io/zh_CN/latest/c01/p01_unpack_sequence_into_separate_variables.html",
    #     "level": (1, 1),
    # }
    # make_download_dir()
    # save_to_html(item)
    make_download_dir()
    contents = []
    html = urlopen(CONTENTS_URL)
    bs_obj = BeautifulSoup(html, "html.parser")
    get_first_level_title(bs_obj.find(id="python-cookbook-3rd-edition-documentation"))

    count = 1
    for item in contents:
        print(item["level"], item["chapter"], item["url"], sep=" : ")
        if item["level"][0] == 0 or item["level"][0] == 16:
            save_to_html(item)
        count += 1
