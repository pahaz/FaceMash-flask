import re
import requests as r

url_searcher = re.compile(r'(a id="profile_photo_link".+?)src="(.+?)" alt', re.UNICODE)

cookies = dict(remixrefkey='7ea_a2d737______8a', remixsid='7816d___________________________9b7b9e5d0d81fd2d2e1f3')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36'}

page = r.get("https://vk.com/id208057456", cookies=cookies, headers=headers)
print page
print page.text
match_obj = url_searcher.search(page.text)
print match_obj.group(2)
