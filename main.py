import requests
import json
from bs4 import BeautifulSoup
from random import choices
import os
from pyfiles.values import *


class Wisher:
    def __init__(self):

        self.fiftyfifty = {"weap4ff": weap4ff, "weap5ff": weap5ff,
                           "char4ff": char4ff, "char5ff": char5ff}

        self.url_Main = 'https://genshin-impact.fandom.com'
        self.url_Banner_list = '/wiki/Wishes/List'
        self.url_Standard = '/wiki/Wanderlust_Invocation'
        self.url_Beginners = '/wiki/Beginners%27_Wish'
        self.url_Characters = '/wiki/Category:Playable_Characters'
        self.url_Weapons = '/wiki/Weapons/Table'
        self.url_Images = 'https://static.wikia.nocookie.net/gensin-impact/images/f/ff/'

        self.currentbanner = ""
        self.reset_pull_history = True
        self.update_json = False

        self.banners = []
        self.all_banners = []
        self.characters = []
        self.all_5_stars, self.all_4_stars = [], []
        self.pity = {}

        self.__update()

    def __update(self):
        self.__reset_pull_histories()
        self.__update_jsons()
        self.__generate_5_and_4_star_lists()
        self.__update_pity()
        self.__update_media()

    def __reset_pull_histories(self):
        if self.reset_pull_history:
            self.character_pull_history = ["Albedo"] * 90
            with open(f'pyfiles/character_pulls.json', 'w', encoding='utf8') as file:
                json.dump(self.character_pull_history, file, indent=4)
            self.weapon_pull_history = ["The_Unforged"] * 90
            with open(f'pyfiles/weapon_pulls.json', 'w', encoding='utf8') as file:
                json.dump(self.weapon_pull_history, file, indent=4)
        else:
            if os.path.isfile('pyfiles/character_pulls.json'):
                with open('pyfiles/character_pulls.json', 'r', encoding='utf8') as file:
                    self.character_pull_history = json.load(file)
            else:
                with open('pyfiles/character_pulls.json', 'w') as fp:
                    fp.write("[]")
            if os.path.isfile('pyfiles/weapon_pulls.json'):
                with open('pyfiles/weapon_pulls.json', 'r', encoding='utf8') as file:
                    self.weapon_pull_history = json.load(file)
            else:
                with open('pyfiles/weapon_pulls.json', 'w') as fp:
                    fp.write("[]")

    def __update_jsons(self):
        if self.update_json:
            self.characters = self.__list_characters()
            self.all_banners = self.__list_banners()
            self.banners = self.__update_json()
        else:
            if os.path.isfile('pyfiles/banners.json'):
                with open('pyfiles/banners.json', 'r', encoding='utf8') as file:
                    self.banners = json.load(file)
            if os.path.isfile('pyfiles/characters.json'):
                with open('pyfiles/characters.json', 'r', encoding='utf8') as file:
                    self.characters = json.load(file)

    def __generate_5_and_4_star_lists(self):
        all_5_stars, all_4_stars = [], []
        for char in self.characters:
            if char["Attributes"]["Rarity"] == 5:
                all_5_stars.append(char["Name"])
            elif char["Attributes"]["Rarity"] == 4:
                all_4_stars.append(char["Name"])
        self.all_5_stars, self.all_4_stars = all_5_stars, all_4_stars

    def __update_pity(self):
        self.pity = {"char4": [i for i, item in enumerate(self.character_pull_history) if
                               item in set(self.all_4_stars + self.all_5_stars)][0],
                     "char5":
                         [i for i, item in enumerate(self.character_pull_history) if item in set(self.all_5_stars)][0],
                     "weap4": [i for i, item in enumerate(self.weapon_pull_history) if
                               item in set(self.all_4_stars + self.all_5_stars)][0],
                     "weap5": [i for i, item in enumerate(self.weapon_pull_history) if item in set(self.all_5_stars)][
                         0]}

    def __check_dup(self, list1, list2):
        for x in list1:
            for y in list2:
                if x == y:
                    return False
        self.placeholding = ""
        return True

    def __list_characters(self):
        response = requests.get(f'{self.url_Main}{self.url_Characters}')
        soup = BeautifulSoup(response.text, 'html.parser')
        wrappers = soup.find_all("div", {"class": "category-page__members-wrapper"})
        char_list = []
        for wrapper in wrappers:
            characters = wrapper.find_all("li", {"class": "category-page__member"})
            for char in characters:
                links = char.find_all("a")
                for link in links:
                    char_list.append(link['href'])
        char_list = char_list[1::2]
        char_list = [x for x in char_list if not "Traveler" in x]
        characters = self.characters
        for char in char_list:
            char_name = char.split("/")[-1]
            characters.append({})
            characters[-1]["Name"] = char_name
            characters[-1]["Attributes"] = {}
            response = requests.get(f'{self.url_Main}{char}')
            soup = BeautifulSoup(response.text, 'html.parser')
            characters[-1]["Attributes"]['Type'] = "Character"
            characters[-1]["Attributes"]['Rarity'] = int(
                soup.find("td", {"data-source": "rarity"}).find("img")['alt'][0])
            characters[-1]["Attributes"]['Weapon'] = soup.find("td", {"data-source": "weapon"}).find("a")['title']
            characters[-1]["Attributes"]['Vision'] = soup.find("td", {"data-source": "element"}).find("a")['title']

        response = requests.get(f'{self.url_Main}{self.url_Weapons}')
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find("tbody")
        trs = table.find_all("tr")
        for tr in trs:
            tds = tr.find_all("td")
            for i, td in enumerate(tds):
                if i == 1:
                    weapon_name = td.find('a')['title'].replace(" ", "_")
                    characters[-1]["Name"] = weapon_name
                    characters[-1]["Attributes"] = {}
                    characters[-1]["Attributes"]['Type'] = "Weapon"
                if i == 2:
                    characters[-1]["Attributes"]['Rarity'] = int(td.find('img')['alt'][0])
                if i == 3:
                    characters.append({})
                    break
        characters = characters[:-1]

        with open('pyfiles/characters.json', 'w', encoding='utf8') as file:
            json.dump(characters, file, indent=4)

        return characters

    def __list_banners(self):
        response = requests.get(f'{self.url_Main}{self.url_Banner_list}')
        soup = BeautifulSoup(response.text, 'html.parser')
        wikitables = soup.find_all("table", {"class": "wikitable"})
        banner_list = []
        for table in wikitables:
            trs = table.find_all("tr")
            for tr in trs:
                links = tr.find_all("a")
                for link in links:
                    banner_list.append(link['href'])
        return banner_list[::2]

    def __update_json(self):

        for i, banner in enumerate(self.all_banners):
            response = requests.get(f'{self.url_Main}{banner}')
            banner = "/".join(banner.split("/")[2:])
            self.banners.append({"Banner_name": banner,
                                 "Banner_content": {'Promoted': [], 'Characters': [], 'Weapons': []}})
            soup = BeautifulSoup(response.text, 'html.parser')
            wikitables = soup.find_all("table", {"class": "wikitable"})
            for j, table in enumerate(wikitables):
                cards = table.find_all("div", {"class": "card_image"})
                for card in cards:
                    links = card.find_all("a")
                    for link in links:
                        char = link['href'].split('/')[-1].replace("%27", "'")
                        for charloop in self.characters:
                            if charloop["Name"] == char:
                                if j == 0:
                                    self.banners[i]["Banner_content"]['Promoted'].append({"Name": char,
                                                                                          "Attributes": charloop[
                                                                                              "Attributes"]})
                                elif j == 1:
                                    self.banners[i]["Banner_content"]['Characters'].append({"Name": char,
                                                                                            "Attributes": charloop[
                                                                                                "Attributes"]})
                                elif j == 2:
                                    self.banners[i]["Banner_content"]['Weapons'].append({"Name": char,
                                                                                         "Attributes": charloop[
                                                                                             "Attributes"]})
        with open('pyfiles/banners.json', 'w', encoding='utf8') as file:
            json.dump(self.banners, file, indent=4)
        return self.banners

    def pull(self, amount):

        banner = 0
        for i, _ in enumerate(self.banners):
            if _["Banner_name"].replace("%27","") == self.currentbanner:
                banner = i
        banner_name = self.currentbanner

        if "Epitome" in banner_name:
            history = self.weapon_pull_history
            banner_type = "weapon"
            pitytype = "weap"
        else:
            history = self.character_pull_history
            banner_type = "character"
            pitytype = "char"

        banner_content = self.banners[banner]['Banner_content']
        five_star, four_star, three_star, five_star_promoted, four_star_promoted = [], [], [], [], []
        for content in banner_content:
            for char in banner_content[content]:
                if char['Attributes']['Rarity'] == 3:
                    three_star.append(char['Name'])
                elif char['Attributes']['Rarity'] == 4:
                    four_star.append(char['Name'])
                    if content == "Promoted":
                        four_star_promoted.append(char['Name'])
                elif char['Attributes']['Rarity'] == 5:
                    five_star.append(char['Name'])
                    if content == "Promoted":
                        five_star_promoted.append(char['Name'])

        for wish in range(amount):
            history = self.__pull_helper(history, pitytype, three_star, four_star, five_star, four_star_promoted, five_star_promoted)
            self.__update_pity()
            yield history[0], self.pity

        with open("pyfiles/values.py", 'w', encoding='UTF8') as file:
            file.write(f"weap4ff = {self.fiftyfifty['weap4ff']}\n")
            file.write(f"weap5ff = {self.fiftyfifty['weap5ff']}\n")
            file.write(f"char4ff = {self.fiftyfifty['char4ff']}\n")
            file.write(f"char5ff = {self.fiftyfifty['char5ff']}")
        with open(f'pyfiles/{banner_type}_pulls.json', 'w', encoding='utf8') as file:
            json.dump(history, file, indent=4)

    def __pull_helper(self, history, pitytype, three_star, four_star, five_star, four_star_promoted, five_star_promoted):
        star = choices([5, 4, 3], [0.6, 5.1, 94.3])[0]
        if self.pity[f"{pitytype}5"] >= 89:
            star = 5
        elif self.pity[f"{pitytype}4"] >= 9:
            if star == 3:
                star = 4

        if star == 3:
            history.insert(0, choices(three_star)[0])

        elif star == 4:
            if self.fiftyfifty[f'{pitytype}4ff']:
                history.insert(0, choices(four_star)[0])
                if history[0] not in four_star_promoted:
                    self.fiftyfifty[f'{pitytype}4ff'] = False
            else:
                history.insert(0, choices(four_star_promoted)[0])
                self.fiftyfifty[f'{pitytype}4ff'] = True

        elif star == 5:
            if self.fiftyfifty[f'{pitytype}5ff']:
                history.insert(0, choices(five_star)[0])
                if history[0] not in five_star_promoted:
                    self.fiftyfifty[f'{pitytype}5ff'] = False
            else:
                history.insert(0, choices(five_star_promoted)[0])
                self.fiftyfifty[f'{pitytype}5ff'] = True
        return history

    def __update_media(self):
        for banner in self.banners:

            if not "Epitome" in banner["Banner_name"]:
                banner_type = "character"
            else:
                banner_type = "weapon"

            if not os.path.isfile(f"static/images/banners/{banner_type}/{banner['Banner_name'].replace('/', ' ').replace('%27','')}.png"):
                response = requests.get(f"{self.url_Main}/wiki/{banner['Banner_name']}")
                soup = BeautifulSoup(response.text, 'html.parser')
                divs = list(soup.find_all("div", {"class": "mw-parser-output"}))
                image_url = divs[0].find("a")['href']
                with open(f"pyfiles/{banner_type}_banner_urls.txt", "a+") as file:
                    file.writelines(f"{image_url.split('/revision')[0]}\n")
                image = requests.get(image_url).content
                with open(f"static/images/banners/{banner_type}/{banner['Banner_name'].replace('/', ' ').replace('%27','')}.png", "wb") as file:
                    file.write(image)

        for char in self.characters:
            if not os.path.isfile(f"static/images/characters/{char['Name']}.png"):
                response = requests.get(f"{self.url_Main}/wiki/{char['Name']}")
                soup = BeautifulSoup(response.text, 'html.parser')
                divs = list(soup.find_all("figure", {"class": "pi-item pi-image"}))
                image_url = divs[0].find("a")["href"]
                image = requests.get(image_url).content
                with open(f"static/images/characters/{char['Name']}.png", "wb") as file:
                    file.write(image)
