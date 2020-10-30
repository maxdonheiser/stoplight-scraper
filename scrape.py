import requests
from bs4 import BeautifulSoup
from py_mini_racer import py_mini_racer
from datetime import date
import os
import csv
import re

payload = {
    'id': 4,
    'L': 0,
    'type': 538601,
    'tx_flmshelter_sheltermap[controller]': 'Shelter',
    'tx_flmshelter_sheltermap[action]': 'show',
}

data = {
    'id': 4,
    'L': 0,
    'type': 538601,
    'tx_flmshelter_sheltermap[controller]': 'Shelter',
    'tx_flmshelter_sheltermap[action]': 'show',
    'tx_flmshelter_sheltermap[term]': None,
    'tx_flmshelter_sheltermap[radius]': 160,
    'tx_flmshelter_sheltermap[shelterLanguage]': 0,
    'tx_flmshelter_sheltermap[shelterBoys]': 0,
    'tx_flmshelter_sheltermap[accessibility]': 'false',
    'tx_flmshelter_sheltermap[petsallowed]': 'false',
    'tx_flmshelter_sheltermap[twentyfour7]': 'false',
    'tx_flmshelter_sheltermap[signlanguage]': 'false'
}

terms = {
    'he' : 35325,
    'nrw' : 44287
}

urls = {
    'he' : 'https://www.frauenhaeuser-hessen.de/index.php',
    'nrw' : 'https://www.frauen-info-netz.de/index.php',
    'mv' : 'https://www.gewaltfrei-zuhause-in-mv.de/%C3%BCber-die-lag/einrichtungen-hilfe-vor-ort/freie-frauenhaus-pl%C3%A4tze/'
}

def scrape_mv(url):
    
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    rows = soup.find('table').find_all('tr')
    raw_dict = []
    for tr in rows:
        td = tr.find_all('td')
        row = [tr.text.replace('\n','').replace('\xa0','').strip().lower() for tr in td]
        raw_dict.append(row)

    data_dict = []

    for item in raw_dict[1:]:

        fp = 0
        if item[1] == 'x':
            fp = 1

        d = {'name' : item[0],
            'free-places' : fp,
            'date' : date.today()}

        data_dict.append(d)
    
    return data_dict

def scrape(b):
    
    if b == 'mv':
        
        data_dict = scrape_mv(urls[b])
        return data_dict
    
    data['tx_flmshelter_sheltermap[term]'] = terms[b]
    r = requests.post(urls[b], params=payload, data=data)
    soup = BeautifulSoup(r.text, 'lxml')
    script = soup.find('script')
    ctx = py_mini_racer.MiniRacer()
    raw_dict = ctx.eval(script.string + ' shelterMap;')
    data_dict = [{k : d[k] for k in ['name','free-women','free-children','free-places']} for d in raw_dict]
    for item in data_dict:

        fp = item['free-places']
        fp = re.search('(?<=title\=\").*(?=\" src)',fp).group(0)
        item['free-places'] = fp
        item['date'] = date.today()

    return data_dict

def update(b):

    d = scrape(b)

    fpath = './data/' + b + '.csv'

    if os.path.exists(fpath):

        f = open(fpath, 'a', encoding='utf8')
        keys = d[0].keys()
        writer = csv.DictWriter(f, fieldnames=keys)

    else:

        f = open(fpath, 'w', encoding='utf8')
        keys = d[0].keys()
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()

    writer.writerows(d)
    f.close()

def main():

    for b in urls.keys():
        update(b)

if __name__=='__main__':
    main()
    
