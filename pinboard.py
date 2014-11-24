import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, json, configparser, time, html.parser, socket, re
from bs4 import BeautifulSoup
from http.cookiejar import CookieJar

config = configparser.ConfigParser()
config.read(['auth.cfg'])
API_KEY = config.get('auth', 'token')
IGNORE_TAG = 'dont_fix'
FIXED_TAG = 'fixed'
LAST_PROCESSED_FILENAME = '.lastprocessed'
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DEFAULT_DATETIME = '0001-01-01T00:00:00Z'

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
    add_url = base_url + '?' + urllib.parse.urlencode(params)
    print(urllib.request.urlopen(add_url).read().decode("utf-8"))

def get_bookmarks(last_processed_datetime):
    params = {
        'auth_token': API_KEY,
        'format': 'json',
        'fromdt': last_processed_datetime
    }
    base_url = "https://api.pinboard.in/v1/posts/all"
    get_url = base_url + '?' + urllib.parse.urlencode(params)
    response = urllib.request.urlopen(get_url)
    return json.loads(response.read().decode("utf-8"))

def get_title(url):
    cj = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    req = urllib.request.Request(url, headers={'User-Agent' : "Magic Browser"})
    print('opening ' + url)
    con = opener.open(req)
    if is_html(con.getheader('Content-Type')):
        BS = BeautifulSoup(con)
        h = html.parser.HTMLParser()
        return h.unescape(BS.find('title').text)
    else:
        raise Exception("Not HTML!")

def has_html_entities(title):
    print("start entities")
    h = html.parser.HTMLParser()
    return title != h.unescape(title)

def should_ignore(tags):
    return IGNORE_TAG in tags.split()

def should_process(bookmark):
    title = bookmark['description']
    if should_ignore(bookmark['tags']):
        print('ignoring ' + bookmark['description'])
        return False;
    return title == 'Untitled' or 'http://' in title or has_html_entities(title)

def is_html(header):
    return re.match('text/html', header)

def add_tag(tags, tag):
    tags_list = tags.split()
    tags_list.append(tag)
    return ' '.join(tags_list)

def already_processed(tags):
    tags_list = tags.split()
    return IGNORE_TAG in tags_list or FIXED_TAG in tags_list

def get_last_processed_datetime():
    try:
        with open(LAST_PROCESSED_FILENAME, 'r') as f:
            date = f.read()
            if len(date) != 20:
                return DEFAULT_DATETIME
            else:
                return date
    except FileNotFoundError as e:
        return DEFAULT_DATETIME

def write_last_processed_datetime():
    with open(LAST_PROCESSED_FILENAME, 'w') as f:
        f.write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

def fix_bookmarks():
    bookmarks = get_bookmarks(get_last_processed_datetime())
    count = 0
    for bookmark in bookmarks:
        if (already_processed(bookmark['tags'])):
            # we've already processed up to this point
            break
        if should_process(bookmark):
            print("should process")
            count = count + 1
            try:
                print("start title")
                title = get_title(bookmark['href'])
                print("end title")
            except Exception as e:
                print(e)
                # Add ignore tag
                add_bookmark(bookmark['href'], bookmark['description'], bookmark['time'], add_tag(bookmark['tags'], IGNORE_TAG))
                continue
            print(bookmark['href'] + ' ' + title)
            print("sleeping")
            time.sleep(3)
            print("adding")
            add_bookmark(bookmark['href'], title, bookmark['time'], add_tag(bookmark['tags'], FIXED_TAG))
            print("done adding")
        else:
            print("should not process")
    print(count)
    write_last_processed_datetime()

fix_bookmarks()