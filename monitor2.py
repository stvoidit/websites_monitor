from models import Users, Websites, Links, ProjectsTitles, db
from sqlalchemy import or_, any_, create_engine
from sqlalchemy.orm import sessionmaker
import requests
import re

fb = create_engine(db.get_engine().url)
Session = sessionmaker(bind=fb)
s = Session()

h = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'ru,en;q=0.9',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Host': 'www.1whois.ru',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 YaBrowser/19.3.0.2485 Yowser/2.5 Safari/537.36'
}


def hosting_cheak(hosts):
    for id_ in hosts:
        domain = s.query(Websites).filter(Websites.id == id_).one()
        url = 'http://www.1whois.ru/?url={}'.format(domain.domain)
        try:
            h.update({'Referer': 'http://www.1whois.ru/?url={}'.format(domain)})
            r = requests.get(url, headers=h, timeout=60)
        except requests.exceptions.ReadTimeout:
            continue
        try:
            hname = re.findall(
                'Location.*width="18" height="12">(.*). <a onclick=', r.text)[0].strip()
        except IndexError:
            hname = None
        try:
            ip = re.findall(
                'IP адрес.*<noindex><b><a href=./.url=(.*).>.*</a></b> <a ', r.text)[0].strip()
        except IndexError:
            ip = None

        if ip:
            url = 'https://rest.db.ripe.net/search.json?query-string={}&type-filter=inetnum&flags=no-filtering&source=RIPE'.format(
                ip)
            r = requests.get(url).json()
            data = r['objects']['object']
            mail_list = set([])
            for row in data:
                for atr in row['attributes']['attribute']:
                    if '@' in atr['value']:
                        [mail_list.add(
                            x.strip()) if '@' in x else None for x in atr['value'].split()]
            emails_list = ";".join(mail_list)
        else:
            emails_list = None

        domain.hosting = hname
        domain.ip = ip
        domain.email = emails_list
        s.commit()
