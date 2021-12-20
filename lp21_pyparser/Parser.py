from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
import pandas as pd
import mypy
import json
import numpy as np
import sys
from rich.console import Console

if __name__ == "__main__":
    import _helper_func as _hf
else:
    from lp21_pyparser import _helper_func as _hf


class LP_Parser:
    def __init__(self, canton_of_choice: str = "sh"):
        self.console = Console()
        self.console.print(
            "\nWelcome to LP21 Pyparser!\n", style="bold underline"
        )
        self.console.print(
            "You chose the following [bold]Canton[/]: "
            + canton_of_choice
            + "\n"
        )

        with self.console.status(
            "[bold green]Working...", spinner="toggle10"
        ) as status:

            self.canton_of_choice = canton_of_choice
            self.hdr = {"User-Agent": "Mozilla/5.0"}
            self.main_site = "https://www.lehrplan21.ch/"
            self.canton_links = self.get_canton_sites()
            self.canton_url = [
                s for s in self.canton_links if self.canton_of_choice in s
            ][0]
            if self.canton_url == None:
                raise Exception(
                    "No canton link could be found in the canton list with the provided acronym. Check your spelling!"
                )

            # try go get the überfachliche kompetenzen
            self.console.log(
                "Attempting to get the Überfachliche Kompetenzen. This might not work for some Cantons."
            )
            try:
                ueber_df = self.get_ueber_k()
                console.log("Überfachliche Kompetenzen found!")
            except:
                self.console.log("Could not get Überfachliche Kompetenzen")

            # extract the url to each fach
            self.console.log("Extracting the URLs for each Fach...")
            self.faecher = self.get_faecher(self.canton_url)
            self.console.print(self.faecher)

            self.console.log(
                "Extracting the URLs for each sub page per Fach..."
            )
            # extract the url to the pages for each kompetenz group per fach
            self.k_details_dict = _hf.dictapply(
                self.faecher, self.get_k_groups
            )

            ##flatten the dictionary containing all the links
            # this will make combining the df's much easier (no nesting)
            norm = pd.json_normalize(self.k_details_dict, sep="_")
            self.k_details_dict = norm.to_dict(orient="records")[0]

            ##applies the func 'combineapply_k_details' recursively to each lowest dict level
            ##works also with nested df's with different levels, but don't recommend
            ##combineapply calls the df extraction func and combines all df's on each level
            self.console.log(
                "Extracting low level info (the actual Kompetenzen)..."
            )
            self.k_df_dict = _hf.dictapply(
                self.k_details_dict, self.combineapply_k_details
            )

            self.console.log("Combining all the Kompetenzen data frames...")
            # collect all the df's from the dict and combine
            final_frame = _hf.extract_combine_df_from_dict(self.k_df_dict)

            self.console.log("Making string corrections...")
            # rename cols, fix split kompetenzen if two entries instead one
            polished_df = _hf.polish_df(final_frame)

            try:
                polished_df = pd.concat([ueber_df, polished_df])
            except:
                pass

            console.log("Saving to csv")
            polished_df.to_csv("lp_parse_export.csv", index=False)

            console.print(polished_df)

    #########################################
    #########################################

    ##### Canton Link List
    def get_canton_sites(self):
        req = Request(self.main_site, headers=self.hdr)
        page = urlopen(req)
        soup = BeautifulSoup(page, features="lxml")
        all_a = soup.find_all("a")
        canton_links = []

        for link in all_a:
            l = link.get("href")
            if type(l) != "NoneType":
                canton_links.append(str(l).replace("http:", "https:"))
        links = [k for k in canton_links if ".lehrplan.ch" in k]
        return list(set(links))  # return unique entries

    # Get Überfachliche Kompetenzen
    def get_ueber_k(self) -> pd.DataFrame:
        url = self.canton_url + "/" + "index.php?code=e|200|3"
        req = Request(url, headers=self.hdr)
        page = urlopen(req)
        soup = BeautifulSoup(page, features="lxml")

        titels = []
        titel = soup.find_all(class_="ek_titel")
        [titels.append(i.contents[0].text) for i in titel]
        titels.remove(titels[0])

        detail = soup.find_all(class_="ek_absatz")
        codes = []
        subtitels = []
        ueberkomp = []
        komp_groups = []
        for i in detail:
            key = i.contents[0].contents[0].find("a").attrs.get("name")
            if "11" in key:
                utext = _hf.k_text_formatter(i)
                codes.append(key)
                # flatten list with [0]
                subtitels.append(utext[0][0])
                ueberkomp.append(utext[1])
                # get the number of groups there are
                komp_groups.append(int(key[3]))

        ngrps = max(komp_groups)
        titels = np.repeat(titels, ngrps)

        # build up dataframe and explode out
        ueber_df = pd.DataFrame()
        ueber_df["Fach"] = ["Überfachliche Kompetenzen"] * len(ueberkomp)
        ueber_df["Fach_Detail"] = ["NA"] * len(ueberkomp)
        ueber_df["k_group"] = titels
        ueber_df["k_subgroup"] = subtitels
        ueber_df["k_text"] = ueberkomp

        ueber_df = ueber_df.explode("k_text").reset_index(drop=True)

        return ueber_df

    ##### Fach Items
    def get_faecher(self, f_url: str) -> dict:
        req = Request(f_url, headers=self.hdr)
        page = urlopen(req)
        soup = BeautifulSoup(page, features="lxml")

        menu = soup.find_all(class_="dreieck_mit")

        faecher = dict()
        for i in menu:
            f_link = self.canton_url + "/" + i.contents[0].get("href")
            level_test = self.get_k_groups(f_link)
            if not level_test:
                level_test = self.get_faecher(f_link)
                faecher[str(i.contents[0].string)] = level_test
            else:
                faecher[str(i.contents[0].string)] = f_link

        if "Grundlagen" in list(faecher.keys()):
            del faecher["Grundlagen"]
        return faecher

    #### get all kompetenzen headers and links for each fach
    def get_k_groups(self, fach: str) -> list:
        req = Request(fach, headers=self.hdr)
        page = urlopen(req)
        soup = BeautifulSoup(page, features="lxml")

        menu = soup.find_all("a")
        # komp_dict = dict()
        komp_dict = []
        for i in menu:
            try:
                if "Die Schülerinnen und Schüler" in i.string:
                    komp_dict.append(self.canton_url + "/" + i.get("href"))

            except:
                pass
        return komp_dict

    def combineapply_k_details(self, url_list: list) -> pd.DataFrame:
        outlist = [self.get_k_details(i) for i in url_list]
        return pd.concat(outlist)

    ##### get all details for each kompetenz header
    def get_k_details(self, k_link: str) -> pd.DataFrame:
        self.console.log("Extracting data frame for: " + k_link)
        req = Request(k_link, headers=self.hdr)
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
        kompetenz_code = soup.find(
            class_="tooltip font_ganzercode"
        ).text  # 1 attr

        standard_table_row = soup.find_all(class_="twelve columns komp_table")
        zyklus = []  # as many as komp table rows
        komp_code = []  # as many as komp table rows
        querverweis = []  # as many as komp table rows

        for i in standard_table_row:

            # Some rows hold an 'arrow' if the 'Zyklus' starts later. Requires skipping.
            if i.find(
                class_="tooltip eight columns komp_cell kompetenz_text kompetenz_arrow_later"
            ):
                continue  # skip iteration

            for num in range(1, 4):
                # finds all zyklus, cumbersome because class names
                try:
                    zyk = i.find(
                        class_="tooltip one column komp_cell marker_z"
                        + str(num)
                    ).get("title")
                    # append just the number
                    zyklus.append(int(re.findall(r"\d+", zyk)[0]))
                except:
                    pass

            try:
                # sometimes NoneType, so in try except
                komp_code.append(
                    i.find(
                        class_="tooltip one column komp_cell kompetenz_lit"
                    ).get("title")
                )
                tmp = i.find(class_="querv").find_all(class_="tooltip")
                querverweis.append([k.get("title") for k in tmp])
            except:
                querverweis.append("NA")

        # Format text
        # has as many enties as komp table rows (x sentences per row)
        kompetenz_text = soup.find_all(
            class_="eight columns komp_cell kompetenz_text"
        )

        kompetenz_text = _hf.k_text_formatter(kompetenz_text)

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

        # spread row attributes to each of its text contents
        df = df.explode("k_text").reset_index(drop=True)
        return df


# sys arg should be the canton abbreviation
if __name__ == "__main__":
    print("Module called from a CLI.\n")
    if len(sys.argv) > 1:
        obj = LP_Parser(sys.argv[1])
    else:
        obj = LP_Parser()
