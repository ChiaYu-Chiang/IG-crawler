import time
import random
import json
import requests
import re
import os
from hashlib import md5
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_cookies():
    username = input('請輸入你的帳號: ')
    password = input('請輸入你的密碼: ')

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.implicitly_wait(5)
    driver.get("https://www.instagram.com/accounts/login/")

    driver.find_element_by_name("username").send_keys(username)
    driver.find_element_by_name("password").send_keys(password)
    driver.find_element_by_class_name(
        "Igw0E.IwRSH.eGOV_._4EzTm.bkEs3.CovQj.jKUp7.DhRcB").click()
    time.sleep(5)

    driver.find_element_by_class_name("sqdOP.L3NKy.y3zKF").click()
    driver.implicitly_wait(5)

    cookie = [item["name"] + "=" + item["value"]
              for item in driver.get_cookies()]
    cookiestr = ';'.join(item for item in cookie)

    driver.quit()
    return cookiestr


def download_obj(data, path):
    with open(path, 'wb') as f:
        f.write(data)
        f.close()


def get_json(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        print(e)
        time.sleep(60 + float(random.randint(1, 4000)) / 100)
        return get_json(url)


def get_html(url):
    response = requests.get(url, headers=headers)
    return response.text


def get_content(url):
    response = requests.get(url, headers=headers, timeout=10)
    return response.content


def get_user_urls(html):
    urls = []
    user_id = re.findall('"profilePage_([0-9]+)"', html, re.S)[0]
    print('user_id : ' + user_id)
    doc = pq(html)     # 初始化PyQuery對象之後，會把html文檔補全
    items = doc('script[type="text/javascript"]').items()
    # 取script[type="text/javascript"]包含節點內部
    # 取多個doc節點的屬性值(id="屬性值")，要怎麽做呢？這就要結合items()方法來實現。items()方法是返回的節點的生成器generator object PyQuery.items：
    for item in items:
        # text()如果沒參數，則是獲取屬性的文本值
        # 如果有參數，則是改變或者添加節點的屬性值
        # strip()去除首尾空格
        # startswith()用於檢查字串是否是以指定字串開頭，是則True，否則False
        if item.text().strip().startswith('window._sharedData'):
            js_data = json.loads(item.text()[21:-1], encoding='utf-8')
            edges = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]
            page_info = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]['page_info']
            cursor = page_info['end_cursor']
            flag = page_info['has_next_page']   # flag = true/false
            for edge in edges:
                if edge['node']['display_url']:
                    display_url = edge['node']['display_url']
                    print(display_url)
                    urls.append(display_url)
            print(cursor, flag)
    while flag:  # 當還有下一頁時
        url = uri_account.format(user_id=user_id, cursor=cursor)
        js_data = get_json(url)
        infos = js_data['data']['user']['edge_owner_to_timeline_media']['edges']
        cursor = js_data['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
        flag = js_data['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']
        for info in infos:
            if info['node']['is_video']:
                video_url = info['node']['video_url']
                if video_url:
                    print(video_url)
                    urls.append(video_url)
            else:
                if info['node']['display_url']:
                    display_url = info['node']['display_url']
                    print(display_url)
                    urls.append(display_url)
        print(cursor, flag)
        # if count > 2000, turn on
        # time.sleep(4 + float(random.randint(1, 800)) / 200)
    return urls


def get_tag_urls(html):
    urls = []
    user_id = re.sub('#', '', target_name)
    print('user_id：' + user_id)
    doc = pq(html)      # 初始化PyQuery對象之後，會把html文檔補全
    items = doc('script[type="text/javascript"]').items()
    # 取script[type="text/javascript"]包含節點內部
    # 取多個doc節點的屬性值(id="屬性值")，要怎麽做呢？這就要結合items()方法來實現。items()方法是返回的節點的生成器generator object PyQuery.items：
    for item in items:
        # text()如果沒參數，則是獲取屬性的文本值
        # 如果有參數，則是改變或者添加節點的屬性值
        # strip()去除首尾空格
        # startswith()用於檢查字串是否是以指定字串開頭，是則True，否則False
        if item.text().strip().startswith('window._sharedData'):
            # loads()解碼JSON數據轉為python字典
            js_data = json.loads(item.text()[21:-1], encoding='utf-8')
            edges = js_data["entry_data"]["TagPage"][0]["graphql"]["hashtag"]["edge_hashtag_to_media"]["edges"]
            page_info = js_data["entry_data"]["TagPage"][0]["graphql"]["hashtag"]["edge_hashtag_to_media"]["page_info"]
            cursor = page_info['end_cursor']
            flag = page_info['has_next_page']
            for edge in edges:
                if edge['node']['display_url']:
                    # display_url圖片網址
                    display_url = edge['node']['display_url']
                    print(display_url)
                    # append()增加url於url_list尾端
                    urls.append(display_url)
            print(cursor, flag)
    while flag:
        url = uri_hashtag.format(user_id=user_id, cursor=cursor)
        js_data = get_json(url)
        infos = js_data['data']['hashtag']['edge_hashtag_to_media']['edges']
        cursor = js_data['data']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
        flag = js_data['data']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page']
        for info in infos:
            if info['node']['is_video']:
                video_url = info['node']['display_url']     # ['video_url']
                if video_url:
                    print(video_url)
                    urls.append(video_url)
            else:
                if info['node']['display_url']:
                    display_url = info['node']['display_url']
                    print(display_url)
                    urls.append(display_url)
        print(cursor, flag)
        # if count > 2000, turn on
        time.sleep(4 + float(random.randint(1, 800))/200)
    return urls


def main(user):
    url_affix = user
    # 判斷hashtag/account
    m = re.match('#', user)
    if m:
        url_affix = re.sub('#', 'explore/tags/', user)
    url = url_base + url_affix + '/'
    html = get_html(url)
    if url_affix == user:
        urls = get_user_urls(html)
    else:
        urls = get_tag_urls(html)

    dirpath = r'.\ig\{0}'.format(user)
    # 若要改指定位置，參考→r'C:\Users\s8792\Downloads\ig\{0}'
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    for i in range(len(urls)):
        print('\n正在下載第{0}張： '.format(i+1) +
              urls[i], ' 還剩{0}張'.format(len(urls) - i - 1))
        try:
            content = get_content(urls[i])
            ext = re.findall('.jpg?', urls[i])  # 判斷副檔名
            urlext = 'jpg' if ext else 'mp4'
            file_path = r'.\ig\{0}\{1}.{2}'.format(
                user, md5(content).hexdigest(), urlext)
            if not os.path.exists(file_path):
                download_obj(content, file_path)
                print('第{0}張下載完成： '.format(i+1) + urls[i])
            else:
                print('第{0}張下載完成： '.format(i + 1) + urls[i])
        except Exception as e:
            print(e)
            print('此檔案下載失敗!')


url_base = 'https://www.instagram.com/'
uri_account = 'https://www.instagram.com/graphql/query/?query_hash=a5164aed103f24b03e7b7747a2d94e3c&variables=%7B%22id%22%3A%22{user_id}%22%2C%22first%22%3A12%2C%22after%22%3A%22{cursor}%22%7D'
uri_hashtag = 'https://www.instagram.com/graphql/query/?query_hash=c769cb6c71b24c8a86590b22402fda50&variables=%7B%22tag_name%22%3A%22{user_id}%22%2C%22first%22%3A12%2C%22after%22%3A%22{cursor}%22%7D'
# 呼叫get_cookies()以取得cookie
cookie_data = get_cookies()
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    # 透過cookie取得權限
    'cookie': cookie_data
}

target_name = input('請輸入ig帳號或tag：')
start = time.time()
main(target_name)
print('下載已完成!!!! ヽ(●´∀`●)ﾉ')
end = time.time()
spend = end - start
hour = spend // 3600
minu = (spend - 3600 * hour) // 60
sec = spend - 3600 * hour - 60 * minu
print(f'一共花費了{int(hour)}小時{int(minu)}分鐘{int(sec)}秒')
