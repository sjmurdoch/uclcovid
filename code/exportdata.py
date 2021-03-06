## NOTES
## Data was not published on 2021-03-31 (Wednesday) -- not yet corrected but appears to be 3 staff on-campus cases

import sys
import re
import math
import json
import hashlib
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime, timedelta, date
from collections import defaultdict

DATA_FIELDS = {
    9: "staff.on",
    10: "staff.off",
    11: "student.on",
    12: "student.off",

    14: "staff7.on",
    15: "staff7.off",
    16: "student7.on",
    17: "student7.off",

    19: "stafftotal.on",
    20: "stafftotal.off",
    21: "studenttotal.on",
    22: "studenttotal.off",
}
TEXT_FIELDS = {
    1: "Staff",
    2: "Students",
    4: "On campus *",
    5: "Off campus **",
    6: "On campus *",
    7: "Off campus **",
    8: "New cases in last counted 24 hour period ***",
    13: "New cases in last counted 7 day period ***",
    18: "Total cases since 28 Sept 2020 (start of Term 1)",
}

DEBUG = False
MONDAY = 0
DATE_LABEL = 'date'
DATASET_NAMES = ['staff.on', 'staff.off', 'student.on', 'student.off',
                 'staff7.on', 'staff7.off', 'student7.on', 'student7.off',
                 'stafftotal.on', 'stafftotal.off', 'studenttotal.on', 'studenttotal.off']
DATE_UPDATED = 'date.updated'

## These figures need smoothing over the weekend
SMOOTHED_NAMES = ['staff.on', 'staff.off', 'student.on', 'student.off']

def debug_log(*args):
    if DEBUG:
        print(*args, file=sys.stderr)

def cleanup_value(tag, file_date, field_index):
    if tag.string == "New cases in last 24 hours ***" and field_index == 8:
        return TEXT_FIELDS[8]
    elif tag.string == "New cases in last 7 days ***" and field_index == 13:
        return TEXT_FIELDS[13]

    s = " ".join(tag.stripped_strings)
    if ((file_date == date(2020,10,27) or file_date == date(2020,10,28))
        and field_index in set([19, 20, 21, 22])):
        ## Totals published 2020-10-27 had a dagger symbol
        ## "The total now includes an additional 89 positive student cases that were confirmed
        ## by the UCL COVID-19 testing programme. These are mainly cases of symptomatic students
        ## in university accomodation who did not update Connect to Protect with their
        ## positive test result."
        return s.replace("\u2020", "")
    elif ((file_date == date(2020,11,5) or file_date == date(2020,11,6))
        and field_index == 16):
        ## 7-day total was revised on 2020-11-05
        ## "This number has been updated following a review of historic cases on Connect to Protect"
        return s.replace("\u2020", "")
    else:
        return s

def parse_html_date(groups, file_date):
    year = groups[2]
    if year is None:
        if groups[1] in set(["October", "November", "December"]):
            year = "2020"
        else:
            year = "2021"

    html_date = datetime.strptime(groups[0] + " " + groups[1] + " " + year,
                  "%d %B %Y").date()
    return html_date

DATE_RE = re.compile(r"\(last update \w+\s(\d+)\s(\w+)(?:\s(\d+))?\)")
def parse_file(fh, file_date = None):
    soup = BeautifulSoup(fh, 'html.parser')
    header = soup.select_one('.box > h2:nth-child(1)')
    table = soup.select_one('#current-confirmed-cases-covid-19 > div.site-content.wrapper > div > div > div > article > div > table')
    data = {}
    if header.string == "Daily reported coronavirus cases (last update Tuesday\xa05\xa0January)":
        ## Handle data for start of term
        all_tags = table.find_all(["td","th"])
        data["staff.on"] = int(cleanup_value(all_tags[9], file_date, 9))
        data["staff.off"] = int(cleanup_value(all_tags[10], file_date, 10))
        data["student.on"] = int(cleanup_value(all_tags[11], file_date, 11))
        data["student.off"] = int(cleanup_value(all_tags[12], file_date, 12))
        data["stafftotal.on"] = int(cleanup_value(all_tags[14], file_date, 13))
        data["stafftotal.off"] = int(cleanup_value(all_tags[15], file_date, 14))
        data["studenttotal.on"] = int(cleanup_value(all_tags[16], file_date, 15))
        data["studenttotal.off"] = int(cleanup_value(all_tags[17], file_date, 16))
        data[DATE_UPDATED] = date(2021, 1, 5)
        return table, data

    match = DATE_RE.search(header.string)
    assert(match)
    html_date = parse_html_date(match.groups(), file_date)
    data[DATE_UPDATED] = html_date

    for i, tag in enumerate(table.find_all(["td","th"])):
        if i in TEXT_FIELDS:
            assert(cleanup_value(tag, file_date, i) == TEXT_FIELDS[i])
        elif i in DATA_FIELDS:
            data[DATA_FIELDS[i]] = int(cleanup_value(tag, file_date, i))

    return table, data

def extract_df():
    p = Path('../data')
    duplicates = p / 'duplicates'
    duplicates.mkdir(exist_ok=True)
    original = p / 'original'
    last_data = None
    last_hash = None
    ## File date of the last file read
    last_date = None

    ## Data to build into PANDAS dataframe
    pd_data = []

    tfh = open(p / 'original-tables.html', "w", newline='', encoding="utf-8")
    tfh.write('<html><head><meta charset="UTF-8"></head><body>\n')
    for file in sorted(original.glob("covid-*.html")):
        debug_log("Loading from", file)

        with file.open("rb") as fh:
            data = fh.read()
            if len(data) == 0:
                continue
            hash = hashlib.sha256()
            hash.update(data)
            file_hash = hash.hexdigest()

        if file_hash == last_hash:
            debug_log("File is a duplicate (hash)", file.name)
            file.rename(duplicates / file.name)
            continue
        else:
            last_hash = file_hash

        with file.open("rb") as fh:
            file_date = datetime.strptime(file.name, "covid-%Y-%m-%dT%H-%M-%S.html").date()
            if file_date.weekday() == 0:
                ## Monday, data is correct as of Friday 5pm
                data_date = file_date - timedelta(days = 3)
            else:
                ## other days, data is correct as of previous day at 5pm
                data_date = file_date - timedelta(days = 1)
            table, data = parse_file(fh, file_date)

        if data != last_data:
            ## Check if data has changed but file date has not
            is_extra = (file_date == last_date)
            if is_extra:
                 debug_log("Extra data at", file_date)
            last_date = file_date

            debug_log("New data at", file_date)
            if is_extra:
                tfh.write('<h2 style="color: red">Extra data published on ' + file_date.strftime("%Y-%m-%d (%A)") + "</h2>\n")
            else:
                tfh.write("<h2>Data published on " + file_date.strftime("%Y-%m-%d (%A)") + "</h2>\n")
            tfh.write("<code>"+file.name+"</code>\n")
            tfh.write(str(table))

            if (data[DATE_UPDATED] != file_date):
                debug_log("Date mismatch at " + str(data[DATE_UPDATED]) +
                            " (html) and " + str(file_date) + "(file name)")

            pd_row = []
            pd_row.append(pd.to_datetime(data_date))
            for n in DATASET_NAMES:
                pd_row.append(data.get(n, np.nan))

            if is_extra:
                ## If we have seen this date before, overwrite last entry
                pd_data[-1] = pd_row
            else:
                ## Otherwise add the entry to the end
                pd_data.append(pd_row)

            last_data = data
        else:
            debug_log("File is a duplicate (data)", file.name)

    tfh.write('</body></html>')
    tfh.close()

    ## Create the PANDAS data frame
    df = pd.DataFrame(pd_data, columns = [DATE_LABEL] + DATASET_NAMES, dtype='float64')
    df.set_index(DATE_LABEL, inplace=True, verify_integrity=True)

    return df

def to_json(df, jsonfile):
    datasets = defaultdict(list)
    for n, rows in df.iteritems():
        ds = datasets[n]
        for d, v in rows.iteritems():
            if not math.isnan(v):
                ds.append((d.strftime("%Y-%m-%d"), v))
    json.dump(datasets, jsonfile, sort_keys=True, indent=4)

def export(df, df_smoothed):
    ## Export raw data to CSV
    with open("../data/covid_raw.csv", "w", newline='') as csvfile:
        df.to_csv(csvfile, line_terminator="\r\n")

    ## Export raw data to JSON
    with open("../data/covid_raw.json", "w", newline='') as jsonfile:
        to_json(df, jsonfile)

    ## Export smoothed data to CSV
    with open("../data/covid.csv", "w", newline='') as csvfile:
        df_smoothed.to_csv(csvfile, line_terminator="\r\n")

    ## Export smoothed data to JSON
    with open("../data/covid.json", "w", newline='') as jsonfile:
        to_json(df_smoothed, jsonfile)

def add_weekend(df):
    ## Add weekend data
    extra_rows = []
    df_smoothed = df.copy()
    for d in df_smoothed.index:
        if d.strftime("%Y-%m-%d") == '2021-01-04':
            ## Handle data for start of term
            extra = df_smoothed.loc[d, SMOOTHED_NAMES] / 18.0
            df_smoothed.loc[d, SMOOTHED_NAMES] = extra
            for i in range(17,0,-1):
                entry_date = d - timedelta(days = i)
                extra_rows.append([entry_date] + list(extra))
        elif d.strftime("%Y-%m-%d") == '2021-04-12':
            ## Handle data over Easter
            extra = df_smoothed.loc[d, SMOOTHED_NAMES] / 12.0
            df_smoothed.loc[d, SMOOTHED_NAMES] = extra
            for i in range(11,0,-1):
                entry_date = d - timedelta(days = i)
                extra_rows.append([entry_date] + list(extra))
        elif d.weekday() == MONDAY:
            ## Share weekend + Monday data over three days
            extra = df_smoothed.loc[d, SMOOTHED_NAMES] / 3.0
            ## Replace Monday data with its share
            df_smoothed.loc[d, SMOOTHED_NAMES] = extra
            ## Add in Saturday and Sunday's data
            for i in [2, 1]:
                entry_date = d - timedelta(days = i)
                extra_rows.append([entry_date] + list(extra))

    extra_df = pd.DataFrame(extra_rows, columns=[DATE_LABEL] + SMOOTHED_NAMES, dtype='float64')
    extra_df.set_index(DATE_LABEL, inplace=True, verify_integrity=True)
    df_smoothed = pd.concat([df_smoothed, extra_df])
    df_smoothed.sort_index(inplace=True)

    return df_smoothed

def main():
    df = extract_df()
    df_smoothed = add_weekend(df)

    ## Compute and export rolling daily statistics
    rolling = df.loc[:,["staff.on","staff.off","student.on","student.off"]].rolling("7D", min_periods=5).sum().dropna()
    rolling.rename(columns=lambda x: x.replace(".", "rolling7."), inplace=True)
    df_rolling = pd.concat([df_smoothed, rolling], axis=1)

    export(df, df_rolling)


if __name__=="__main__":
    main()
