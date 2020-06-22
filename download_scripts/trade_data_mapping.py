import csv
from glob import glob
import pickle
base_file = '../trade_networks/year_origin_destination_sitc_rev2.tsv'

base_fp = open(base_file, 'r')
def create_mapping():
    global base_fp
    country_codes = set([])
    for line in base_fp:
        line_split = line.strip('\n').split('\t')
        if line_split[0].isnumeric():
            country_codes.add(line_split[1])
    mapping = dict(zip(country_codes, range(len(country_codes))))
    with open('../trade_networks/mapping.pkl','wb') as country_mapping:
         pickle.dump(mapping, country_mapping)

def replace_ids():
    with open('../trade_networks/mapping.pkl', 'rb') as mapping:
          country_mapping = pickle.load(mapping)
    for file in glob('../trade_networks/trade-*'):
        lines = []
        with open(file, 'r') as unmapped_file:
              for line in unmapped_file:
                  line_data = line.strip('\n').split(',')
                  line_data[0] = country_mapping[line_data[0]]
                  line_data[1] = country_mapping[line_data[1]]
                  sitc_data = line_data[2]
                  line_data[2] = "{export_" + sitc_data + ":" + line_data[3] + "}"
                  lines.append(line_data[:3])
                  line_data[2] = "{import_" + sitc_data + ":" + line_data[4] + "}"
                  line_data = line_data[:3]
                  lines.append(line_data)
        with open('../trade_networks/new.' + file.split('/')[-1], 'w', newline='') as individual_entry:
            csv_writer = csv.writer(individual_entry)
            csv_writer.writerows(lines)
