import csv
import json

def get_node_table(in_file, out_file, delimiter=","):
    nodes = set([])
    with open(in_file, 'r') as in_fp:
         reader = csv.reader(in_fp, delimiter=delimiter)
         for line in reader:
             for i in range(min(2, len(line))):
                 nodes.add(line[i])
    with open(out_file, 'w') as out_fp:
         for node in nodes:
             out_fp.write(node + '\n')



def write_dict(out_filename):
    # Example: {"url": "http://networksciencebook.com/translations/en/resources/data.html", "directed": false, "attributed": false, "reference": "Yu et al., (2008). High-quality binary protein interaction map of the yeast interactome network. Science, 322(5898), 104-110."}
    url = input("Enter url: ").strip(" ")
    directed = bool(input("Is directed? "))
    attributed = bool(input("Is attributed? "))
    reference = input("Source reference: ").strip(" ")
    dict_metadata = {"url": url, "directed":directed, "attributed":attributed, "reference":reference}
    with open(out_filename, 'w') as fp:
         json.dump(dict_metadata, fp)


def strip_attributes(in_file, out_file, delimiter=","):
    lines = []
    with open(in_file, 'r') as in_fp:
         reader = csv.reader(in_fp, delimiter=delimiter)
         for line in reader:
             curr_line = line[:min(2, len(line))]
             lines.append(curr_line)          
    with open(out_file, 'w', newline='') as out_fp:
         writer = csv.writer(out_fp, delimiter=delimiter)
         for line in lines:
             writer.writerow(line)

