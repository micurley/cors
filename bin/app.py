import os
import web
import requests
import json
from bs4 import BeautifulSoup
from urlparse import urlparse, urljoin, urlunsplit

try:
    from html import escape  # python 3.x
except ImportError:
    from cgi import escape  # python 2.x

urls = (
    '/([^?]*)', 'index',
)

app = web.application(urls, globals())
application = app.wsgifunc()

render = web.template.render(os.path.join(os.path.dirname(__file__), '../templates/'))

class index:
    def GET(self, tags = ''):
        input = web.input(url=None, callback=None)

        if(input.url == None):
            return render.index()

        url_parts = urlparse(input.url)

        # Removing params b/c I am peeling off the last element of the path
        referer = urlunsplit([
            url_parts.scheme,
            url_parts.netloc,
            '%s/' % ('/').join(url_parts.path.split('/')[:-1]),
            url_parts.query,
            url_parts.fragment,
        ])

        headers = {
            'Referer': referer,
        }

        resp = requests.get(input.url, headers=headers)

        soup = BeautifulSoup(resp.content)

        url = input.url
        for base in soup.find_all('base', href=True):
            url = base.attrs['href']

        for link in soup.find_all('a', href=True):
            full_url = urljoin(url, link.attrs["href"])
            link.attrs["href"] = full_url

        for link in soup.find_all('img', src=True):
            full_url = urljoin(url, link.attrs["src"])
            link.attrs["src"] = full_url

        soup = [soup]

        if tags == '':
            web.header('Content-Type', resp.headers['content-type'])
            return resp.content
        else:
            try:
                json_data = html_to_json(soup=soup, tags=tags, callback=input.callback)
                web.header('Content-Type', 'application/json')
                return json_data
            except:
                raise

    def POST(self, tags = ''):
        input = web.input(callback=None)
        content = web.data()

        if(content == None):
            return render.index()

        soup = BeautifulSoup(content)

        soup = [soup]

        if tags == '':
            return content
        else:
            try:
                json_data = html_to_json(soup=soup, tags=tags, callback=input.callback)
                web.header('Content-Type', 'application/json')
                return json_data
            except:
                raise

def convert_to_dict(element):
    new_dict = {
        'tag': element.name,
        'attrs': {},
        'contents': [],
    }

    try:
        new_dict['attrs'] = element.attrs
    except AttributeError:
        pass

    try:
        for child in element.children:
            result = convert_to_dict(child)
            if result:
                new_dict['contents'].append(result)

    except Exception as exp:
        new_dict = trim_string(element)

    return new_dict

def trim_string(s):
    try:
        return s.strip()
    except Exception:
        return s

def html_to_json(soup, tags=None, callback=None):
    clean = False
    as_json = False
    as_sorted = False
    sub_tags = None

    for tag in tags.split('/'):
        range = [0,None]
        if tag == ('sort'):
            as_sorted = True
            continue

        if tag == ('clean'):
            clean = True
            continue

        if tag.endswith('.json'):
            as_json = True
            tag = tag[0:-5]

        if tag.startswith('[') and tag.endswith(']'):
            range = map(int, tag[1:-1].split(',', 2))
            continue

        if tag.startswith('{') and tag.endswith('}'):
            sub_tags = tag[1:-1].split(',')
            continue

        if '.' in tag or '#' in tag or '[' in tag:
            new_soup = []
            for element in soup[range[0]:range[1]]:
                new_soup += element.select(tag)

            soup = new_soup
        elif tag:
            new_soup = []
            for element in soup[range[0]:range[1]]:
                print 'Tag Name: %s' % element.name
                new_soup += element.find_all(tag)

            soup = new_soup

    if(sub_tags):
        new_soup = []
        for element in soup:
            new_elements = []
            for new_tag in sub_tags:
                new_elements += element.find_all(new_tag)

            new_soup += new_elements

        soup = new_soup

    if as_json == False:
        return soup
    else:
        json_data = []

        for element in soup[range[0]:range[1]]:
            try:
                json_data.append(convert_to_dict(element))
            except Exception as exp:
                print "Couldn't convert %s: %s" % (element.name, exp)
                raise

        if as_sorted:
            json_data.sort(key=lambda k: k['contents'][0])

        if callback:
            return '%s(%s);' % (callback, json.dumps(json_data))

        return json.dumps(json_data, indent=4)

if __name__ == "__main__":
    app.run()