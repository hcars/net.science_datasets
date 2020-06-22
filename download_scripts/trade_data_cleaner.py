import csv
base_file = '../trade_networks/year_origin_destination_sitc_rev2.tsv'

base_fp = open(base_file, 'r')

for line in base_fp:
    line_split = line.strip('\n').split('\t')
    if line_split[0].isnumeric():
        with open('../trade_networks/trade-' + line_split[0] + '.csv', 'a', newline='') as individual_entry:
            csv_writer = csv.writer(individual_entry)
            csv_writer.writerow(line_split[1:])
