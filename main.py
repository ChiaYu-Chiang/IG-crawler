# cookie自動抓取
import time
import random
import json
import requests
import re
import os
from hashlib import md5
from pyquery import PyQuery as pq

url_base = 'https://www.instagram.com/'
uri_account = 'https://www.instagram.com/graphql/query/?query_hash=a5164aed103f24b03e7b7747a2d94e3c&variables=%7B%22id%22%3A%22{user_id}%22%2C%22first%22%3A12%2C%22after%22%3A%22{cursor}%22%7D'
uri_hashtag = 'https://www.instagram.com/graphql/query/?query_hash=c769cb6c71b24c8a86590b22402fda50&variables=%7B%22tag_name%22%3A%22{user_id}%22%2C%22first%22%3A12%2C%22after%22%3A%22{cursor}%22%7D'
# 請更改cookie_data內的訊息，以成功獲取已追蹤非公開帳號的權限
cookie_data = 'mid=XsvsoAALAAEYyrG6CF67BSwQ829S; fbm_124024574287414=base_domain=.instagram.com; fbsr_124024574287414=KukIXT55vhLdHf7sGB8Jwbp2v1E9Vkn9_I-54fr7rWc.eyJ1c2VyX2lkIjoiMTAwMDAwMzEyNDUyNDExIiwiY29kZSI6IkFRQ1ZweWFoRzVxcjFfR29DbnBXWGRhb0pXTFJ5YzNIdnlUa2xZR3FZbWVDcUFXZEdDeXRHY3pEZ3ZBQjJxbzJ6REc1c3VVZzdOMWh1ektVTzNfYnF1dnk5ZldUQTZpbDE3SEJ4ZU05X0RIRzBONjJ2eW5Tb2h2cjJ4dUVuSnlBbDRBQVRfeXNCdzJwQkVramJYZ1g5djdiamhCS1RZYllyOFZpOGhrUlpWcVVoZXBPVTdHRnVrUTd4WTQwY3RkVG5CZjhKUXV2LWVDVnhJSXl4Y1pfOVdDYnFTb1M1U2syb1p0NXFpZzI3amM1UjgzcUlQLTVzelg0SmdqbmlRRmwxbXNaYVVXUlNlVklxVWNoYXNjbmhPdkxnWGM4c0E0VmpUanNTUF9WSzhOZ2tyMlVVanViMHNmbldtU3hndnZBalhPWWZWMng2ci1yUTBXUTJvb2RCZC1oIiwib2F1dGhfdG9rZW4iOiJFQUFCd3pMaXhuallCQUZGa1AyY2NiQU1jR1pBSWEyUmp5cEE4M0FSUFZCWGFicGZaQUl4M2h1NlpBVU1ZbFRneVBNaVBmVUNMaWlMYW9USzJXR2k2dGhtQTVGc2NiTlBUSzBRV1BhZDZINDlqeTFjOFVvazJaQ2VCWkNrNGg5N0J2MWtLd1hLcHNiVFpBMTFZZ29JQU1RQUg4S1ZhWUl1Mkl2MGVSSjFCbEpBbjJtVGVZcGxYa24iLCJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImlzc3VlZF9hdCI6MTU5MDQyMzA0NX0; csrftoken=CAlYWJxx2K2Cpmvc9KWHmzN7dIoLuArs; ds_user_id=1637446255; sessionid=1637446255%3A9QqyGWXg8CetM9%3A17; shbid=3317; shbts=1591975326.7713547'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    # 透過cookie取得權限
    'cookie': cookie_data
}


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
                    # append()增加url於urls尾端
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
    user_id = re.sub('#', '', user_name)
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

    dirpath = r'.\ig\{0}'.format(user)  # r'C:\Users\s8792\Downloads\ig\{0}'
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
                download_obj(content, file_path)        # 如果檔案不存在就執行下載
                print('第{0}張下載完成： '.format(i+1) + urls[i])
            else:
                print('第{0}張下載完成： '.format(i + 1) + urls[i])
        except Exception as e:
            print(e)
            print('此檔案下載失敗!')


user_name = input('請輸入ig帳號或tag：')
start = time.time()
main(user_name)
print('下載已完成!!!! ヽ(●´∀`●)ﾉ')
end = time.time()
spend = end - start
hour = spend // 3600
minu = (spend - 3600 * hour) // 60
sec = spend - 3600 * hour - 60 * minu
print(f'一共花費了{int(hour)}小時{int(minu)}分鐘{int(sec)}秒')
