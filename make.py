# This script creates a sample metadata repository by reading current metadata from
# the data API

'''
Creates a sample metadata repository by reading current metadata from the data API

Usage:
  make.pl [--db=DBASEID] [--limit=LIMIT] [--width=WIDTH] [--featured] [--compatible]

Options:
  --db=DBASEID:          database [default: 2]

  --limit=LIMIT:         how many elements per dimension to extract

  --width=WIDTH:         value width in the yaml file [default: 100]

  --featured:            Extract only featured indicators (provides a shorter list)

  --compatible:          be fully compatible with standard PyYAML, producing
                         less legible YAML output; see README for details.
'''

import yaml
import wbgapi as wb
import os
import sys
import logging
from docopt import docopt

logging.basicConfig(level=logging.INFO)

config = docopt(__doc__)
config['--width'] = int(config['--width'])
wb.db = config['--db']

elementMax = config['--limit'] # or 20

# reference lists of all economies and time elements in this database
economies = list(wb.economy.Series().index)
time      = list(wb.time.Series().index)

yaml_dump_params = {'sort_keys': False, 'width': config['--width']}
if not config['--compatible']:
    yaml_dump_params['strict_whitespace'] = False

# extract and cleanup a selection of indicator metadata. Includes series-economy metadata where available
if config['--featured']:
    series_list = [row['id'] for row in wb.fetch('indicators', {'source': wb.db, 'featured': 1})]
else:
    series_list = list(wb.series.Series().index)
# series_list = []
n = 0
for elem in series_list:
    if elementMax and n >= elementMax:
        break

    n += 1
    meta1 = wb.get('indicators/{}'.format(elem), {'source': wb.db})
    meta2 = wb.series.metadata.get(elem, economies=economies, time=time)
    meta3 = meta2.metadata

    # There are two name and description fields, but we want only one with the name 'description'
    meta1['description'] = meta1.pop('sourceNote')
    meta3['name'] = meta3.pop('IndicatorName')
    meta3['description'] = meta3.pop('Longdefinition')

    meta1.update(meta3)
    if meta2.economies:
        meta1['economies'] = meta2.economies

    if meta2.time:
        meta1['time'] = meta2.time

    domain = elem.split('.')[0]
    path = 'series/{}'.format(domain)
    try:
        os.makedirs(path)
    except FileExistsError:
        pass

    path = '{}/{}.yaml'.format(path, elem)
    print('Saving {}'.format(path))
    with open(path, 'w') as fd:
        yaml.dump(meta1, fd, **yaml_dump_params)

# extract and cleanup economy metadata
economy_list = list(wb.economy.Series().index)
n = 0

for elem in economy_list:
    if elementMax and n >= elementMax:
        break

    n += 1
    meta1 = wb.get('country/{}'.format(elem))
    try:
        meta2 = wb.economy.metadata.get(elem)
        meta3 = meta2.metadata
    except:
        meta3 = {}

    # harmonize
    meta1['region'] = meta1['region']['id']
    meta1['adminregion'] = meta1['adminregion']['id']
    meta1['incomelevel'] = meta1.pop('incomeLevel')['id']
    meta1['lendingtype'] = meta1.pop('lendingType')['id']

    if meta1['longitude']:
        meta1['longitude'] = float(meta1['longitude'])

    if meta1['latitude']:
        meta1['latitude'] = float(meta1['latitude'])

    fields_to_remove = ['ShortName', 'TableName', '2-alphacode', 'WB-2code', 'Lendingcategory']
    try:
        for field in fields_to_remove:
            meta3.pop(field)
    except:
        pass
        
    meta1.update(meta3)

    path = 'economy'
    try:
        os.makedirs(path)
    except FileExistsError:
        pass

    path = '{}/{}.yaml'.format(path, elem)
    print('Saving {}'.format(path))
    with open(path, 'w') as fd:
        yaml.dump(meta1, fd, **yaml_dump_params)
