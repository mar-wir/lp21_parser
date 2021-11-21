from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
import pandas as pd
import mypy
import pprint

# bla.find('iframe', class_='blabla')['src']

###### Menu Items
# site = 'https://sh.lehrplan.ch/'
# drop_categories = ['Überblick', 'Grundlagen']
# hdr = {'User-Agent': 'Mozilla/5.0'}
# req = Request(site,headers=hdr)
# page = urlopen(req)
# soup = BeautifulSoup(page, features = "lxml")
#
# menu = soup.find_all(class_='parent_menu')
#
# categories = dict()
# for i in menu:
#    categories[i.contents[0]] = site + (i.attrs.get('href'))
#
# for i in drop_categories:
#    categories.pop(i)
#
# for i, k in categories.items():
#    print(i)
#    print(k)



###### Kompetenz übergruppen Items
#main_site = 'https://sh.lehrplan.ch/'
#site = 'https://sh.lehrplan.ch/index.php?code=b|1|11'
#hdr = {'User-Agent': 'Mozilla/5.0'}
#req = Request(site,headers=hdr)
#page = urlopen(req)
#soup = BeautifulSoup(page, features = "lxml")
#
#menu = soup.find_all(class_='dreieck_mit')
#
#faecher = dict()
#for i in menu:
#    faecher[str(i.contents[0].string)] = main_site+ i.contents[0].get('href')
#
#for i, k in faecher.items():
#    print(i)
#    print(k)


class Parser:

    def __init__(self, canton_of_choice: str = 'sh'):

        self.canton_of_choice = canton_of_choice
        self.hdr = {"User-Agent": "Mozilla/5.0"}
        self.main_site = 'https://www.lehrplan21.ch/'
        self.canton_links = self.get_canton_sites()
        self.canton_url = [s for s in self.canton_links if self.canton_of_choice in s][0]
        if self.canton_url == None:
            raise Exception("No canton link could be found in the canton list with the provided acronym. Check your spelling!")

        self.faecher = self.get_faecher(self.canton_url)
        #self.my_dictionary = {k: self.get_k_groups(v) for k, v in self.faecher.items()}



    ##### Canton Link List
    def get_canton_sites(self):
        req = Request(self.main_site, headers=self.hdr)
        page = urlopen(req)
        soup = BeautifulSoup(page, features = "lxml")
        all_a = soup.find_all('a')
        canton_links=[]

        for link in all_a:
            l = link.get('href')
            if type(l) != 'NoneType':
                canton_links.append(str(l).replace('http:', 'https:'))
        links = [k for k in canton_links if '.lehrplan.ch' in k]
        return list(set(links)) #return unique entries

    ##### Fach Items
    def get_faecher(self, f_url: str) -> dict:
        req = Request(f_url, headers=self.hdr)
        page = urlopen(req)
        soup = BeautifulSoup(page, features = "lxml")

        menu = soup.find_all(class_='dreieck_mit')

        faecher = dict()
        for i in menu:
            f_link = self.canton_url + '/' + i.contents[0].get('href')
            level_test = self.get_k_groups(f_link)
            if not level_test:
                level_test = self.get_faecher(f_link)
                faecher[str(i.contents[0].string)] = level_test
            else:
                faecher[str(i.contents[0].string)] = f_link
        if 'Grundlagen' in list(faecher.keys()):
            del faecher['Grundlagen']
        return faecher

    #### get all kompetenzen headers and links for each fach
    def get_k_groups(self, fach: str) -> list:
        req = Request(fach,headers=self.hdr)
        page = urlopen(req)
        soup = BeautifulSoup(page, features = "lxml")

        menu = soup.find_all('a')
        #komp_dict = dict()
        komp_dict = []
        for i in menu:
            try:
                if 'Die Schülerinnen und Schüler' in i.string:
                    #komp_dict[str(i.string)] = self.canton_url + '/' + i.get('href')
                    komp_dict.append(self.canton_url + '/' + i.get('href'))

            except:
                pass
        return komp_dict



##### get all details for each kompetenz header
def get_k_details(k_link: str) -> pd.DataFrame:

    main_site = "https://sh.lehrplan.ch/"
    hdr = {"User-Agent": "Mozilla/5.0"}
    req = Request(k_link, headers=hdr)
    page = urlopen(req)
    soup = BeautifulSoup(page, features="lxml")

    # extract kompetenz atributes
    kompetenz_group_code = soup.find(class_="two columns kcode alpha").text
    kompetenz_tags = soup.find_all(class_="kompetenzbereich columns")
    kompetenz_tags = [o.text for o in kompetenz_tags]
    kompetenz_group = kompetenz_tags[0]  # 1 attr
    kompetenz_subgroup = kompetenz_tags[1]  # 1 attr
    kompetenz_subgroup_code = soup.find(
        class_="two columns htacode alpha"
    ).text  # 1 attr
    kompetenz_code = soup.find(class_="tooltip font_ganzercode").text  # 1 attr

    standard_table_row = soup.find_all(class_="twelve columns komp_table")
    zyklus = []  # as many as komp table rows
    komp_code = []  # as many as komp table rows
    querverweis = []  # as many as komp table rows
    querverweis_link = []  # as many as komp table rows

    for i in standard_table_row:

        for num in range(1, 5):
            #finds all zyklus, cumbersome because class names
            try:
                zyk = i.find(
                    class_="tooltip one column komp_cell marker_z" + str(num)
                ).get("title")
                #append just the number
                zyklus.append(int(re.findall(r"\d+", zyk)[0]))
            except:
                pass

        try:
            #sometimes NoneType, so in try except
            komp_code.append(
                i.find(
                    class_="tooltip one column komp_cell kompetenz_lit"
                ).get("title")
            )
            querverweis.append(
                i.find(class_="querv").find(class_="tooltip").get("title")
            )
            querverweis_link.append(
                i.find(class_="querv").find(class_="tooltip").get("href")
            )
        except:
            querverweis.append("NA")
            querverweis_link.append("NA")

    # Format text
    # has as many enties as komp table rows (x sentences per row)
    kompetenz_text = soup.find_all(
        class_="eight columns komp_cell kompetenz_text"
    )
    # remove breaks and possible whitespaces
    kompetenz_text = [
        k.text.strip("\n").strip(" ").replace("z.B.", "zum Beispiel")
        for k in kompetenz_text
    ]
    # separate into individual sub kompetenzen by the dot
    kompetenz_text = [k.strip(".").split(".") for k in kompetenz_text]
    # put the dot back where it belongs
    kompetenz_text = [[i + "." for i in k] for k in kompetenz_text]

    # build up Pandas dataframe
    row_rep = len(kompetenz_text)  # the info per row will get exploded out
    df = pd.DataFrame()
    df["k_group"] = [kompetenz_group] * row_rep
    df["k_subgroup"] = [kompetenz_subgroup] * row_rep
    df["k_subgroup_code"] = [kompetenz_subgroup_code] * row_rep
    df["k_code"] = [kompetenz_code] * row_rep
    df["zyklus"] = zyklus
    df["k_text_code"] = komp_code
    df["k_text"] = kompetenz_text
    df["qverweis"] = querverweis
    df["qverweis_link"] = querverweis_link

    # spread row attributes to each of its text contents
    df = df.explode("k_text").reset_index(drop=True)
    return df


#print(get_k_details("https://sh.lehrplan.ch/index.php?code=a|1|11|6|3|1"))
aaa = Parser()
pprint.pprint(aaa.faecher)
#pprint.pprint(aaa.my_dictionary)
