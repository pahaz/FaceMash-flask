import urllib
import requests as r
import json, re, time, os

url1 = 'https://api.vk.com/method/groups.getMembers?group_id=' #1647015
url2 = '&fields=sex'
vk_id = 'https://vk.com/id'
url_searcher = re.compile(r'(a id="profile_photo_link".+?)src="(.+?)" alt', re.UNICODE)

mm_1234course = ['56775171', '41731262', '28942034', '19180862']
dmm = ['1647015']
#				FIIT-201, ..KN-103, .....KN-102, ....KN-101, ....FIIT-101, ..PI-101, ....FP-101, .
vk_groups_id = ['41677454', '56927668', '56873080', '56869985', '56868706', '56842778', '57230141'] + mm_1234course + dmm

cookies = dict(remixsid='3e6f961f36937d06e73ca74049aa63500b004cec71df04aeee760')
headers = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53'}


def main():

	# open files with vk_id's of males and females
	with open(os.path.join(os.path.dirname(__file__), 'data\\female.txt').replace('\\','/'), "a+") as female:
		with open(os.path.join(os.path.dirname(__file__), 'data\\male.txt').replace('\\','/'), "a+") as male:

			# creating sets of vk_id's of males and females (TO UPDATE ONCE!)
			male_set = set()
			female_set = set()
			for line in male:
				male_set.add(int(line[:-1]))
			for line in female:
				female_set.add(int(line[:-1]))

			# sets for new males&females to download their photo_url's 
			new_male_set = set()
			new_female_set = set()

			# for each group in vk_groups_id update male_set and female_set
			for group in vk_groups_id:
				str_json = urllib.urlopen(url1 + str(group) + url2).read()
				for user in json.loads(str_json)["response"]["users"]:
					if (user["uid"] not in male_set) and (user["uid"] not in female_set):
						if user["sex"] == 1:
							female_set.add(user["uid"])
							new_female_set.add(user["uid"])
							female.write(str(user["uid"]) + "\n")
						elif user["sex"] == 2:
							male_set.add(user["uid"])
							new_male_set.add(user["uid"])
							male.write(str(user["uid"]) + "\n")

	'''
	"uncomment if your last attemp failed (vk banned you :( ))"
	# open files with photo (urls) of males&females for appending NEW items
	with open(os.path.join(os.path.dirname(__file__), 'data\\female_photo.txt').replace('\\','/'), "a+") as female_photo:
		with open(os.path.join(os.path.dirname(__file__), 'data\\male_photo.txt').replace('\\','/'), "a+") as male_photo:
			
			old_set = set()
			i = 1
			for line in male_photo.read().split():
				if i:
					old_set.add(int(line))
				i = (i + 1) % 2

			new_male_set = male_set - old_set
			
			old_set = set()
			i = 1
			for line in female_photo.read().split():
				if i:
					old_set.add(int(line))
				i = (i + 1) % 2

			new_female_set = female_set - old_set
	'''


	# open files with photo (urls) of males&females for appending NEW items
	with open(os.path.join(os.path.dirname(__file__), 'data\\female_photo.txt').replace('\\','/'), "a+") as female_photo:
		with open(os.path.join(os.path.dirname(__file__), 'data\\male_photo.txt').replace('\\','/'), "a+") as male_photo:
			
			for m_id in new_male_set:
				time.sleep(1.01)
				page = r.get(vk_id + str(m_id), cookies=cookies)#, headers=headers)
				match_obj = re.search(url_searcher, page.text)
				if not match_obj:
					print 'Error: ' + vk_id + str(m_id)
					continue
				male_photo.write(str(m_id) + " " + match_obj.group(2) + "\n")

			for f_id in new_female_set:
				time.sleep(1.01)
				page = r.get(vk_id + str(f_id), cookies=cookies)#, headers=headers)
				match_obj = re.search(url_searcher, page.text)
				if not match_obj:
					print 'Error(fe): ' + vk_id + str(f_id)
					continue
				female_photo.write(str(f_id) + " " + match_obj.group(2) + "\n")


if __name__ == '__main__':
	main()
