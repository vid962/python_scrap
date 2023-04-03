import pandas as pd
import requests
from bs4 import BeautifulSoup
import scraper_helper

# eng header
# text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8

# extracted the headers of website from chrome network tab
headers = """accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
accept-encoding: gzip, deflate, br
accept-language: en-GB,en-US;q=0.9,en;q=0.8
cache-control: max-age=0
cookie: PHPSESSID=14cakhmscle13lsv1tq4qj12oj; pw_virt6_persistence=460917258.35918.0000
sec-ch-ua: "Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
sec-fetch-dest: document
sec-fetch-mode: navigate
sec-fetch-site: none
sec-fetch-user: ?1
upgrade-insecure-requests: 1
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"""
# using scraper_helper library to convert the string headers into dictionary, saves alot of time
headers = scraper_helper.get_dict(headers, strip_cookie=False)

# Set the URL and language code
URL_language = 'https://ects.coi.pw.edu.pl/menu2/changelang/lang/eng'

# Make subsequent request to actual page with saved cookies and headers
response = requests.get(URL_language, headers=headers, )
soup = BeautifulSoup(response.content, "html.parser")

table = soup.find(name='table')

data_frame_data = []
for a_tag in table.find_all('a'):
    link = a_tag.get('href').strip()

    link = f'https://ects.coi.pw.edu.pl{link}'

    subject = a_tag.get_text().strip()
    req = requests.get(link, headers=headers, )
    print(link, req.status_code)
    soup = BeautifulSoup(req.text, 'html.parser')

    # extracting all tables and faculty name
    tables = soup.find('div', {'id': 'content'})
    table1 = tables.findChildren('table')[0]
    facult = table1.findChildren('tr')[1].findChildren('td')[1].string

    # iterating through each table row to extract semester, name and ects
    data_table = tables.findChildren('table')[1]
    semester = ''
    for tr in data_table.findChildren('tr'):
        if len(tr.findChildren('td')) > 0 and tr.findChildren('td')[0].findChildren('h3'):
            semester = tr.findChildren('td')[0].findChildren('h3')[0].get_text(strip=True)
            print(semester)
        if len(tr.findChildren('td')) > 1:
            try:
                name = tr.findChildren('td')[2].get_text(strip=True)
                ects = tr.findChildren('td')[3].get_text(strip=True)
                if name != '∑=':
                    subjects = {'Subject': subject,
                                'Link': link,
                                'Faculty': facult,
                                'Semester': semester.replace(':', ''),
                                'Name': name,
                                'Ect': ects
                                }
                    data_frame_data.append(subjects)
            except Exception as e:
                print(e)

# creating pandas dataframe
dataframe = pd.DataFrame(data_frame_data, index=list(range(len(data_frame_data))))
print(dataframe)
print(dataframe.shape)

# CSV export
# dataframe.to_csv('ect_data.csv', index=False)

