import io
import csv

def convert_csv(csv_file):
    csv_content = ""
    csv_reader = csv.reader(io.StringIO(csv_file))
    csv_content = [row for row in csv_reader]

    print(f' return convert csv : {csv_content}')
    return csv_content