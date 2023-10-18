import json

file = 'bengalpedigrees_2023-10-18_17-19-08.json'

with open(file) as f:
    data = json.load(f)
    ids = []
    for cat in data:
        ids.append(cat['id'])

    #print missing ids 16355
    for i in range(1, max(ids)):
        if i not in ids:
            print(i)
