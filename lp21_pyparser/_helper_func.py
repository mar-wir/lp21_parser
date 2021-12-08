import pandas as pd
import re


def extract_combine_df_from_dict(dic: dict) -> pd.DataFrame:
    user_ids = []
    frames = []
    for user_id, d in dic.items():
        user_ids.append(user_id)
        frames.append(d)
    final_frame = pd.concat(frames, keys=user_ids).reset_index()
    return final_frame


def w_dict_to_json(
    dic: dict, filename: str = "unnamed_dict_export.json"
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


# applies arbitrary function 'applyfunc' to values of nested dicts
def dictapply(basedict: dict, applyfunc, memdict: dict = dict()):
    for k, v in basedict.items():
        if isinstance(v, dict):
            dictapply(v, applyfunc, basedict)
        else:
            basedict[k] = applyfunc(v)
    return basedict


def k_text_formatter(k_text) -> str:

    kompetenz_text = k_text

    # remove breaks and possible whitespaces
    # as I split on periods, I try to remove excess ones
    kompetenz_text = [
        k.text.strip()
        .replace("Die Schülerinnen und Schüler ...", "")
        .replace("\n", "")
        .replace("\t", "")
        .replace("\r", "")
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
        .strip()
        for k in kompetenz_text
    ]
    # find periods preceeded by numbers, sub by comma (german num sep)
    kompetenz_text = [re.sub(r"(\d)\.", r"\1,", k) for k in kompetenz_text]

    # separate into individual sub kompetenzen by the periods, works well
    kompetenz_text = [k.strip(".").split(".") for k in kompetenz_text]

    # put stuff back where it belongs
    kompetenz_text = [
        [
            str(i)
            .replace("___", "...")
            .replace("Fr", "Fr.")
            .replace("Rp", "Rp.")
            + "."
            for i in k
        ]
        for k in kompetenz_text
    ]
    return kompetenz_text


def polish_df(df: pd.DataFrame) -> pd.DataFrame:

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
