import urllib, urllib2, json, ConfigParser, time, HTMLParser, socket, re
from BeautifulSoup import BeautifulSoup
from cookielib import CookieJar

config = ConfigParser.ConfigParser()
config.read(['auth.cfg'])
API_KEY = config.get('auth', 'token')

socket.setdefaulttimeout(3)

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
    print 'opening ' + url
    con = opener.open(req)
    info = con.info();
    if is_html(info.headers):
        BS = BeautifulSoup(con)
        h = HTMLParser.HTMLParser()
        return h.unescape(BS.find('title').text)
    else:
        raise Exception("Not HTML!")

def has_html_entities(title):
    print "start entities"
    h = HTMLParser.HTMLParser()
    return title != h.unescape(title)

def should_process(title):
    return title == 'Untitled' or 'http://' in title or has_html_entities(title)

def is_html(headers):
    for header in headers:
        if re.match('Content-[tT]ype: text/html', header):
            return True;
    return False;

def fix_bookmarks():
    bookmarks = get_bookmarks()
    count = 0
    for bookmark in bookmarks:
        if should_process(bookmark['description']):
            print "should process"
            count = count + 1
            try:
                print "start title"
                title = get_title(bookmark['href'])
                print "end title"
            except:
                continue
            print bookmark['href'] + ' ' + title
            print "sleeping"
            time.sleep(3)
            print "adding"
            add_bookmark(bookmark['href'], title, bookmark['time'])
            print "done adding"
        else:
            print "should not process"
    print count

fix_bookmarks()