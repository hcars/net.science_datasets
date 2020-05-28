import urllib.request
import json
__author__ = "Henry Carscadden"
__email__ = 'hlc5v@virginia.edu'
"""
This file downloads datasets from Harvard Dataverse.
"""



base = 'https://dataverse.harvard.edu'
rows = 10
start = 0
page = 1
condition = True # emulate do-while
while (condition):
    url = base + '/api/search?q=*&type=file&fq=fileTag:"GraphML"' + "&start=" + str(start)
    data = json.load(urllib.request.urlopen(url))
    total = data['data']['total_count']
    # TODO: Write in download and clean code here
    print("=== Page", page, "===")
    print("start:", start, " total:", total)
    for i in data['data']['items']:
        print("- ", i['name'], "(" + i['type'] + ")")
    start += rows
    page += 1
    condition = start < total