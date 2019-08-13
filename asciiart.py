import random
import requests
import json
import datetime
from typing import List
from html.parser import HTMLParser

# --- CONSTANTS

headers = {
    "User-Agent": "AsciiArt"
}

bans = [
    'sexual',
    'ascii art archive',
    ' ',
    'home',
    'ascii art faq',
    'ascii artists',
    'ascii one line',
    'ascii table ',
    'ascii table',
    'read more',
    'ascii art links',
    'link to us',
    'cookie policy',
    'color themes',
    'privacy policy',
    'terms of use',
    'injosoft',
    'enable/disable cookies (opt-in)'
]

rootPath = "https://www.asciiart.eu/"


# --- HELPER FUNCTIONS

def replaceAll(string: str, replace: List[str], replace_with: str) -> str:
    for thing in replace:
        string = string.replace(thing, replace_with)
    return string

def listIn(string: str, check: List[str]) -> bool:
    for thing in check:
        if thing in string:
            return False
    return True

def linkFormat(string: str) -> str:
    if string[-1] == "-":
        string = string[:-1]
    return string.replace(" ", "-").replace("&", "and").lower()

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.a_list = []
        self.pre_list = []
        self.handling_a = False
        self.handling_pre = False

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.handling_a = True
        elif tag == "pre":
            self.handling_pre = True

    def handle_endtag(self, tag):
        if tag == "a":
            self.handling_a = False
        elif tag == "pre":
            self.handling_pre = False
    
    def handle_data(self, data):
        if self.handling_a:
            self.a_list.append(data)
        elif self.handling_pre:
            self.pre_list.append(data)
    
    def reset_list(self):
        self.a_list = []
        self.pre_list = []

def get_categories(path=rootPath) -> List[str]:
    parser = Parser()

    # GET CATEGORIES
    categories = []

    page = requests.get(path, headers=headers)
    parser.feed(page.text)
    a = parser.a_list
    for link in a:
        if link not in categories and link.lower() not in bans:
            categories.append(link)

    parser.reset()
    parser.reset_list()

    return categories

def get_subcategories(category:str, path=rootPath) -> dict:
    parser = Parser()
    
    categories = get_categories()

    subcategories = {}

    path = linkFormat(path + category)
    page = requests.get(path, headers=headers)
    parser.feed(page.text)
    a = parser.a_list
    
    for link in a:
        if link not in categories and link.lower() not in bans:
            subcategories[link] = linkFormat(f"{path}/{link}")
    
    return subcategories

def build_link_json():
    links = {"last_fetched": str(datetime.datetime.now()), "categories": {}}
    
    categories = get_categories()
    for category in categories:
        links["categories"][category] = get_subcategories(category)
    
    json_string = json.dumps(links)
    
    with open("links_json.json", "w") as file:
        file.write(json_string)

def build_art_json():
    parser = Parser()

    final = {}
    with open("links_json.json", "r") as file:
        link_json = json.load(file)["categories"]
    for category, subcategory in link_json.items():
        final[category] = {}
        for sub, link in subcategory.items():
            print(f"category:{category}, sub:{sub}, link:{link}")
            final[category][sub] = {}
            page = requests.get(link, headers=headers)
            parser.feed(page.text)
            pres = parser.pre_list
            for pre in pres:
                final[category][sub] = {
                    "height": len(pre.split("\n")), 
                    "art": pre
                }
            parser.reset()
            parser.reset_list()
    with open("final_art.json", "w") as file:
        file.write(json.dumps(final))

def get_art(line_height=0):
    random.seed()

    with open("links_json.json", "r") as file:
        link_json = json.load(file)["categories"]

    parser = Parser()

    subcategories = link_json[list(link_json.keys())[random.randint(0, len(link_json.keys()) - 1)]]

    try:
        link = subcategories[list(subcategories.keys())[random.randint(0, len(subcategories.keys()) - 1)]]
    except ValueError:
        link = "https://www.asciiart.eu/animals/fish"
    
    if link[:-1] == "@":
        link = link[:-1]
        categories = get_categories(link)
        for category in categories:
            sub_subcategories = get_subcategories(category, link+"/")
            try:
                link = sub_subcategories[list(sub_subcategories.keys())[random.randint(0, len(sub_subcategories.keys()) - 1)]]
            except ValueError:
                link = "https://www.asciiart.eu/animals/fish"


    page = requests.get(link, headers=headers)
    parser.feed(page.text)
    pres = parser.pre_list
        
    try:
        art = pres[random.randint(0, len(pres) - 1)]
    except ValueError:
        art = get_art(line_height)

    art_lines = art.split("\n")
    if len(art_lines) < line_height or len(art) == 1:
        return get_art(line_height)
    return art

def get_artworks(count:int, line_height=0):
    if count == 1:
        return get_art(line_height)
    else:
        return get_art(line_height) + "\n" + get_artworks(count-1, line_height)

        
# --- LAMBDA
def lambda_handler(event=None, context=None) -> dict:
    line_height = 0
    count = 1
    if event is not None and "queryStringParameters" in event.keys(): 
        if event["queryStringParameters"] is not None:
            if "line_height" in event["queryStringParameters"].keys():
                line_height = int(event["queryStringParameters"]["line_height"])
            if "count" in event["queryStringParameters"].keys():
                count_param = int(event["queryStringParameters"]["count"])
                if count_param > 0:
                    count = count_param
    
    art = get_artworks(count, line_height)

    return {
        "statusCode": 200,
        "headers": {"content-type": "text/html"},
        "body": f"<html><body><pre>{art}<pre></body></html>"
    }
