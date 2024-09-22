import csv

def read(args):
    with open(args[0], 'r') as file_csv:
        raw_data = csv.reader(file_csv)
        return list(raw_data)