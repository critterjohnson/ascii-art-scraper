from lxml import html
from typing import List
import requests

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

headers = {
    "User-Agent": "JerryRig"
}

bans = [
    'ASCII Art Archive',
    ' ', 
    'ASCII art FAQ', 
    'ASCII artists', 
    'ASCII one line', 
    'ASCII table ',
    'ASCII table',
    'Read more', 
    'ASCII Art Links', 
    'Link To Us', 
    'Cookie policy', 
    'Privacy policy', 
    'Terms of Use', 
    'Injosoft', 
    'Enable/Disable Cookies (Opt-in)'
]

# GET CATEGORIES
rootPath = "https://www.asciiart.eu/"
categories = []

page = requests.get(rootPath, headers=headers)
tree = html.fromstring(page.text)
a = tree.xpath('//a/text()')
for link in a:
    if link not in categories and link not in bans:
        categories.append(link)

# GET SUBCATEGORIES AND GENERATE LINKS
basePath = "https://www.asciiart.eu/"
links = []

for category in categories:
    path = linkFormat(basePath + category)
    page = requests.get(path, headers=headers)
    tree = html.fromstring(page.text)
    a = tree.xpath('//a/text()')
    for link in a:
        if link not in categories and link not in bans:
            links.append(linkFormat(f"{path}/{link}"))

art = []
for link in links:
    page = requests.get(link, headers=headers)
    tree = html.fromstring(page.text)
    pres = tree.xpath('//pre/text()')
    for pre in pres:
        art.append(pre)

with open("art.txt", "w") as file:
    for artwork in art:
        file.write(artwork)
