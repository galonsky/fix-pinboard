import urllib, urllib2, json, ConfigParser, time, HTMLParser, socket, re
from BeautifulSoup import BeautifulSoup
from cookielib import CookieJar

config = ConfigParser.ConfigParser()
config.read(['auth.cfg'])
API_KEY = config.get('auth', 'token')
IGNORE_TAG = 'dont_fix'
FIXED_TAG = 'fixed'

socket.setdefaulttimeout(3)

def add_bookmark(url, title, datetime, tags):
    params = {
        'url': url,
        'description': title.encode('utf8'),
        'dt': datetime,
        'tags': tags,
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

def should_ignore(tags):
    return IGNORE_TAG in tags.split()

def should_process(bookmark):
    title = bookmark['description']
    if should_ignore(bookmark['tags']):
        print 'ignoring ' + bookmark['description']
        return False;
    return title == 'Untitled' or 'http://' in title or has_html_entities(title)

def is_html(headers):
    for header in headers:
        if re.match('Content-[tT]ype: text/html', header):
            return True;
    return False;

def add_tag(tags, tag):
    tags_list = tags.split()
    tags_list.append(tag)
    return ' '.join(tags_list)

def already_processed(tags):
    tags_list = tags.split()
    return IGNORE_TAG in tags_list or FIXED_TAG in tags_list

def fix_bookmarks():
    bookmarks = get_bookmarks()
    count = 0
    for bookmark in bookmarks:
        if (already_processed(bookmark['tags'])):
            # we've already processed up to this point
            break
        if should_process(bookmark):
            print "should process"
            count = count + 1
            try:
                print "start title"
                title = get_title(bookmark['href'])
                print "end title"
            except:
                # Add ignore tag
                add_bookmark(bookmark['href'], bookmark['description'], bookmark['time'], add_tag(bookmark['tags'], IGNORE_TAG))
                continue
            print bookmark['href'] + ' ' + title
            print "sleeping"
            time.sleep(3)
            print "adding"
            add_bookmark(bookmark['href'], title, bookmark['time'], add_tag(bookmark['tags'], FIXED_TAG))
            print "done adding"
        else:
            print "should not process"
    print count

fix_bookmarks()