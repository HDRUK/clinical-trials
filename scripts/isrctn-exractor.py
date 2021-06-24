import requests
from datetime import datetime

import xmltodict, json
import pandas as pd
from collections import MutableMapping


TRIALS_DATA_FORMAT = "internal"
RECRUITMENT_COUNTRY = '"United Kingdom"'
LIMIT = 6000


API_URL_1 = "https://www.isrctn.com/api/query/format/{FORMAT}?q=recruitmentCountry: {COUNTRY} AND dateApplied GE 2000-01-01T00:00:00 AND dateApplied LT 2012-01-01T00:00:00 &limit={LIM}".format(
    FORMAT=TRIALS_DATA_FORMAT, COUNTRY=RECRUITMENT_COUNTRY, LIM=LIMIT
)
API_URL_2 = "https://www.isrctn.com/api/query/format/{FORMAT}?q=recruitmentCountry GE {COUNTRY} AND dateApplied GE 2012-01-01T00:00:00 AND dateApplied LT 2022-01-01T00:00:00 &limit={LIM}".format(
    FORMAT=TRIALS_DATA_FORMAT, COUNTRY=RECRUITMENT_COUNTRY, LIM=LIMIT
)


def get_api_data(url):
    data = requests.get(url)
    return data


def save_as_xml(data, filename):
    print("Saving XML data....")
    with open(filename, "wb") as file:
        file.write(data.content)


def print_xml_line(filename):
    # print first 10 lines
    with open(
        filename,
    ) as f:
        for x in range(1):
            print(f.readline().strip())


def flatten_json(y):
    out = {}

    def flatten(x, name=""):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + "_")
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + "_")
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


def delete_keys_from_dict(dictionary, keys):
    keys_set = set(keys)

    modified_dict = {}
    for key, value in dictionary.items():
        if key not in keys_set:
            if isinstance(value, MutableMapping):
                modified_dict[key] = delete_keys_from_dict(value, keys_set)
            else:
                modified_dict[key] = value
    return modified_dict


def xml_to_json_and_df(xml_filename, json_filename, indent=2):
    with open(xml_filename, encoding="utf-8") as xmlfile:
        doc = xmltodict.parse(xmlfile.read())

    with open(json_filename, "w") as jsonfile:
        json.dump(doc, jsonfile, indent=indent)

    with open(json_filename) as jsonfile:
        doc_dict = json.load(jsonfile)

    # Flattened
    doc_flat = doc_dict["allTrials"]["fullTrial"]

    # TODO: Dropping trialCentres as it gives many columns (need to fix)
    keys_to_remove = ["@xmlns", "trialCentres"]

    # Deleting description from intervention as it is causing error in csv
    for i in range(len(doc_flat)):
        del doc_flat[i]["trial"]["interventions"]["intervention"]["description"]

    for i in range(len(doc_flat)):
        doc_flat[i] = delete_keys_from_dict(doc_flat[i], keys_to_remove)
        doc_flat[i] = flatten_json(doc_flat[i])
    doc_flat_df = pd.DataFrame(doc_flat)

    doc_flat_df = doc_flat_df.dropna(how="all", axis=1)

    doc_flat_df = doc_flat_df.loc[
        :, ~doc_flat_df.columns.str.contains("xmlns", case=False)
    ]

    return doc_flat_df


def merge_dfs(df1, df2, outfile):
    merged_df = df1.append([df2])
    merged_df = merged_df.drop_duplicates(
        subset=["trial_externalRefs_eudraCTNumber"]
    )
    merged_df.to_csv(outfile, index=False)


def main():

    startTime = datetime.now()
    print(f"##### Fetching started at {startTime} #####")

    # fetching First Query
    print("Fetching First Query...")
    isrctn_data_1 = get_api_data(API_URL_1)
    save_as_xml(isrctn_data_1, "data/ISRCTN/isrctn_1.xml")
    print("1st Query DONE")
    print_xml_line("data/ISRCTN/isrctn_1.xml")

    # fetching Second Query
    print("Fetching Second Query...")
    isrctn_data_2 = get_api_data(API_URL_2)
    save_as_xml(isrctn_data_2, "data/ISRCTN/isrctn_2.xml")
    print_xml_line("data/ISRCTN/isrctn_2.xml")
    print("Second Query DONE")

    endTime = datetime.now()
    print(f"##### Fetching ended at {endTime} #####")

    print("Execution time of query:", endTime - startTime)

    isrctn_1_df = xml_to_json_and_df(
        "data/ISRCTN/isrctn_1.xml", "data/ISRCTN/isrctn_1.json"
    )
    isrctn_2_df = xml_to_json_and_df(
        "data/ISRCTN/isrctn_2.xml", "data/ISRCTN/isrctn_2.json"
    )

    merge_dfs(isrctn_1_df, isrctn_2_df, "data/ISRCTN/isrctn.csv")


if __name__ == "__main__":
    main()
