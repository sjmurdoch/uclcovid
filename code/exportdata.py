import sys
import math
import json
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

DEBUG=False
MONDAY = 0
DATE_LABEL = 'date'
DATASET_NAMES = ['staff.on', 'staff.off', 'student.on', 'student.off',
                 'staff7.on', 'staff7.off', 'student7.on', 'student7.off',
                 'stafftotal.on', 'stafftotal.off', 'studenttotal.on', 'studenttotal.off']

## These figures need smoothing over the weekend
SMOOTHED_NAMES = ['staff.on', 'staff.off', 'student.on', 'student.off']

def debug_log(*args):
    if DEBUG:
        print(*args, file=sys.stderr)

def parse_file(fh):
    soup = BeautifulSoup(fh, 'html.parser')
    table = soup.select_one('#current-confirmed-cases-covid-19 > div.site-content.wrapper > div > div > div > article > div > table')
    data = {}
    for i, tag in enumerate(table.find_all(["td","th"])):
        if i in TEXT_FIELDS:
            assert(tag.string == TEXT_FIELDS[i])
        elif i in DATA_FIELDS:
            data[DATA_FIELDS[i]] = int(tag.string)

    return table, data

def extract_df():
    p = Path('../data')
    duplicates = p / 'duplicates'
    duplicates.mkdir(exist_ok=True)
    original = p / 'original'
    last_data = None

    ## Data to build into PANDAS dataframe
    pd_data = []

    tfh = open(p / 'original-tables.html', "w")
    tfh.write('<html><head><meta charset="UTF-8"></head><body>\n')
    for file in sorted(original.glob("covid-*.html")):
        debug_log("Loading from", file)

        with file.open() as fh:
            file_date = datetime.strptime(file.name, "covid-%Y-%m-%dT%H-%M-%S.html").date()
            if file_date.weekday() == 0:
                ## Monday, data is correct as of Friday 5pm
                data_date = file_date - timedelta(days = 3)
            else:
                ## other days, data is correct as of previous day at 5pm
                data_date = file_date - timedelta(days = 1)
            table, data = parse_file(fh)

        if data != last_data:
            debug_log("New data at", file_date)
            tfh.write("<h2> Data published on " + file_date.strftime("%Y-%m-%d (%A)") + "</h2>")
            tfh.write(str(table))

            pd_row = []
            pd_row.append(data_date)
            for n in DATASET_NAMES:
                pd_row.append(data[n])
            pd_data.append(pd_row)

            last_data = data
        else:
            debug_log("File is a duplicate", file.name)
            #file.rename(duplicates / file.name)
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
    with open("../data/covid_raw.csv", "w") as csvfile:
        df.to_csv(csvfile, line_terminator="\r\n")

    ## Export raw data to JSON
    with open("../data/covid_raw.json", "w") as jsonfile:
        to_json(df, jsonfile)

    ## Export smoothed data to CSV
    with open("../data/covid.csv", "w") as csvfile:
        df_smoothed.to_csv(csvfile, line_terminator="\r\n")

    ## Export smoothed data to JSON
    with open("../data/covid.json", "w") as jsonfile:
        to_json(df_smoothed, jsonfile)

def add_weekend(df):
    ## Add weekend data
    extra_rows = []
    df_smoothed = df.copy()
    for d in df_smoothed.index:
        if d.weekday() == MONDAY:
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
    export(df, df_smoothed)

if __name__=="__main__":
    main()
