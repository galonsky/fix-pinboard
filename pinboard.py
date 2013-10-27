import urllib, urllib2, json, ConfigParser, time, HTMLParser
from BeautifulSoup import BeautifulSoup
from cookielib import CookieJar

config = ConfigParser.ConfigParser()
config.read(['auth.cfg'])
API_KEY = config.get('auth', 'token')

def add_bookmark(url, title, datetime):
    params = {
        'url': url,
        'description': title.encode('utf8'),
        'dt': datetime,
        'format': 'json',
        'auth_token': API_KEY
    }
    base_url = "https://api.pinboard.in/v1/posts/add"
    add_url = base_url + '?' + urllib.urlencode(params)
    print urllib2.urlopen(add_url).read()

def get_bookmarks():
    params = {
        'auth_token': API_KEY,
        'format': 'json'
    }
    base_url = "https://api.pinboard.in/v1/posts/all"
    get_url = base_url + '?' + urllib.urlencode(params)
    return json.load(urllib2.urlopen(get_url))

def get_title(url):
    cj = CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})
    con = opener.open(req)
    BS = BeautifulSoup(con)
    h = HTMLParser.HTMLParser()
    return h.unescape(BS.find('title').text)

def has_html_entities(title):
    h = HTMLParser.HTMLParser()
    return title != h.unescape(title)

def should_process(title):
    return title == 'Untitled' or 'http://' in title or has_html_entities(title)

def fix_bookmarks():
    bookmarks = get_bookmarks()
    count = 0
    for bookmark in bookmarks:
        if should_process(bookmark['description']):
            count = count + 1
            try:
                title = get_title(bookmark['href'])
            except:
                continue
            print bookmark['href'] + ' ' + title
            time.sleep(3)
            add_bookmark(bookmark['href'], title, bookmark['time'])
    print count

fix_bookmarks()