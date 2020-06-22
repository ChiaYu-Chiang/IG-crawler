# IG_crawler

## 功能：

### 下載指定對象的照片與影片
- 此程式在執行時會存取使用者於instagram網頁的cookie。
- 註:hashtag搜尋之影片只會以照片形式下載。

## 操作方式：

1. 執行程式後，依提示輸入使用者的instagram帳號密碼。
> - 目前僅提供一般帳號登入方式，不支援fb登入
2. 待其自動取得cookie後，輸入欲搜尋之目標。
> - 目標帳號(ex. jjlin)或hashtag(ex. #taiwan)
3. Wait & Enjoy It

## 注意事項：

```python
# if count > 2000, turn on
time.sleep(4 + float(random.randint(1, 800)) / 200)
```
此行code存在於get_user_urls()與get_tag_urls()，可自由選擇是否使用。
