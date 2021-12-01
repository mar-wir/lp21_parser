from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
import pandas as pd
import mypy
import pprint
import json


class Parser:
    def __init__(self, canton_of_choice: str = "sh"):

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

            #        self.faecher = self.get_faecher(self.canton_url)

            #        self.k_details_dict = self.dictapply(self.faecher, self.get_k_groups)

            ##flatten the dictionary containing all the links
            #        norm = pd.json_normalize(self.k_details_dict, sep="_")
            #        self.k_details_dict = norm.to_dict(orient="records")[0]

            ##apply the function 'combineaply' recursively to each lowest dict level
            ##combineapply calls the df extraction func and combines all df's

            #        self.k_df_dict = self.dictapply(self.k_details_dict, self.combineapply)

            #        user_ids = []
            #        frames = []

            #        for user_id, d in self.k_df_dict.items():
            #            user_ids.append(user_id)
            #            frames.append(d)
            #        final_frame = pd.concat(frames, keys=user_ids).reset_index()
            #        final_frame.to_csv("lp_parse_export.csv")
            #        print(final_frame)

            test = self.get_k_details(
                "https://sh.lehrplan.ch/index.php?code=a|5|0|1|3|2"
            )
            print(test)
            test.to_csv("test.csv")

    def w_dict_to_json(
        self, dic: dict, filename: str = "unnamed_dict_export.json"
    ) -> None:
        with open(filename, "w", encoding="UTF-8") as fp:
            json.dump(
                dic,
                fp,
                sort_keys=True,
                indent=4,
                separators=(",", ": "),
                ensure_ascii=False,
            )

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
                    # komp_dict[str(i.string)] = self.canton_url + '/' + i.get('href')
                    komp_dict.append(self.canton_url + "/" + i.get("href"))

            except:
                pass
        return komp_dict

    # applies arbitrary function 'applyfunc' to values of nested dicts
    def dictapply(self, basedict: dict, applyfunc, memdict: dict = dict()):
        for k, v in basedict.items():
            if isinstance(v, dict):
                self.dictapply(v, applyfunc, basedict)
            else:
                basedict[k] = applyfunc(v)
        return basedict

    def combineapply(self, url_list: list) -> pd.DataFrame:
        outlist = [self.get_k_details(i) for i in url_list]
        return pd.concat(outlist)

    ##### get all details for each kompetenz header
    def get_k_details(self, k_link: str) -> pd.DataFrame:
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
        # remove breaks and possible whitespaces
        # as I split on periods, I try to remove excess ones
        kompetenz_text = [
            k.text.strip("\n")
            .strip(" ")
            .strip()
            .replace("z.B.", "zum Beispiel")
            .replace("z. B.", "zum Beispiel")
            .replace(". (", " (")
            .replace(".(", " (")
            .replace("​", "")  # strange char
            .replace("...", "___")
            .replace("u.a.", "unter anderem")
            .replace("Fr.", "Fr")
            .replace("Rp.", "Rp")
            .replace("bzgl.", "bezüglich")
            .replace("vs.", "versus")
            .replace("inkl.", "inklusive")
            .replace("v.a.", "vor allem")
            .replace("bzw.", "beziehungsweise")
            for k in kompetenz_text
        ]
        # find periods preceeded by numbers, sub by comma (german num sep)
        kompetenz_text = [re.sub(r"(\d)\.", r"\1,", k) for k in kompetenz_text]

        # separate into individual sub kompetenzen by the periods, works well
        kompetenz_text = [k.strip(".").split(".") for k in kompetenz_text]

        # put the dot back where it belongs
        kompetenz_text = [[str(i) + "." for i in k] for k in kompetenz_text]

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

    def polish_df(df):

        df["str_criteria"] = df["k_text"].str.contains(
            "zeigen|stellen|lernen|nehmen|setzen|reflektieren|erkunden|machen|erzählen|erhalten|wissen|entwickeln|verfügen|sind bereit|sammeln|ordnen|erforschen|beschreiben|kennen|experimentieren|erfahren|entscheiden|lassen sich|suchen|erkennen|verwenden|können|Erweiterung|verstehen"
        )

        df["Index"] = df.index
        onlyF_df = df.loc[df.str_criteria == False]
        onlyF_df = onlyF_df[["Index", "k_text"]]
        onlyT_df = df.loc[df.str_criteria == True]
        onlyF_df["Index"] = onlyF_df["Index"] - 1
        result = (
            pd.merge(onlyT_df, onlyF_df, how="left", on=["Index"])
            .reset_index()
            .fillna("")
        )
        result["k_text"] = result["k_text_x"] + " " + result["k_text_y"]
        result[["Fach", "Fach_Detail"]] = result["level_0"].str.split(
            "_", 1, expand=True
        )
        result = result.drop(
            columns=[
                "index",
                "Index",
                "k_text_x",
                "k_text_y",
                "str_criteria",
                "Unnamed: 0",
                "level_0",
                "level_1",
            ]
        ).fillna("NA")
        result = result[
            [
                "Fach",
                "Fach_Detail",
                "k_group",
                "k_subgroup",
                "k_subgroup_code",
                "k_code",
                "zyklus",
                "k_text_code",
                "qverweis",
                "k_text",
            ]
        ]
        return result


# print(get_k_details("https://sh.lehrplan.ch/index.php?code=a|1|11|6|3|1"))
aaa = Parser()
# pprint.pprint(aaa.k_df_dict)
