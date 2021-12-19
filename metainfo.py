# Script for extracting metadata about the metadata API

'''
Extracts metadata about the metadata system

Usage:
  metainfo.py [--concept=CONCEPT] [--quick] [--limit=RANGE] CSV

Options:
  --concept=CONCEPT:         The concept to analyze - series or economy [default: series]

  --quick:                   Just report field definitions, not their actual counts (faster but misleading and less informative)

  --limit=RANGE:             Limit to specified databases (single ID or FIRST:LAST inclusive)

'''

import pandas as pd
import wbgapi as wb
from docopt import docopt
import logging
import sys

config = docopt(__doc__)
concept = config['--concept']

df = pd.DataFrame()
df.index.name = 'metatype'
dummy = pd.Series(dtype='int64')


# this flag causes the outer loop to exit if the user types ctrl-C
# that way the script will at least save a partial CSV file
# as opposed to quitting immediately with no save
sysInterrupt = False

sources = [row for row in wb.source.list()]
if config['--limit']:
    source_id_list = [row['id'] for row in sources]
    if ':' in config['--limit']:
        (first,last) = config['--limit'].split(':')
        first = source_id_list.index(first) if first else 0
        last  = source_id_list.index(last) if last else len(sources)-1
        sources = sources[first:last+1]
    else:
        sources = sources[source_id_list.index(config['--limit'])]

for db in sources:
    if sysInterrupt:
        break

    # note: metatypes endpoint frequently returns what looks like valid fields even when
    # metadataavailability flag is False. We trust the flag
    if db['metadataavailability'] == 'Y':
        if config['--quick']:
            concept_value = concept.title()
            if concept_value == 'Economy':
                concept_value = 'Country'

            try:
                result = {row['id']: row['metatype'] for row in wb.fetch('sources/{}/metatypes'.format(db['id']), concepts=True)}
                for elem in result[concept_value]:
                    df.loc[elem['id'], db['id']] = 1
            except KeyError:
                logging.warning('Concept key {} missing in {}'.format(concept_value, db['id']))

        elif concept.lower() == 'series':
            # This code iterates through each indicator and fetches its metadata. This is not a very efficient
            # way to count metadata instances. The API has an endpoint for fetching metadata and the metatype
            # level e.g: api.worldbank.org/v2/sources/2/series/all/metatypes/License_Type/metadata which is
            # documented here: https://datahelpdesk.worldbank.org/knowledgebase/articles/1886695-metadata-api-queries
            # However, it currently only works for the WDI and tends to time out for other databases.
            # (see JIRA ticket https://jira.worldbank.org/jira/projects/APII/issues/APII-414)
            print('Fetching metadata for {} {}'.format(db['id'], db['name']))
            for i in wb.series.list(db=db['id']):
                try:
                    # this call fails a lot from the API side, so we need to catch exceptions
                    for (k,v) in wb.series.metadata.get(i['id'], db=db['id']).metadata.items():
                        if v.strip():
                            df.loc[k, db['id']] = df.get(db['id'], dummy).fillna(0).get(k, 0) + 1
                except KeyboardInterrupt:
                    print("Operation terminated by Ctrl-C")
                    sysInterrupt = True
                    break
                except:
                    logging.warning("Can't get metadata for {} in {}".format(i['id'], db['id']))

        elif concept.lower() == 'economy':
            # same design as above but for economies, and with the same caveats and limitations
            print('Fetching metadata for {} {}'.format(db['id'], db['name']))
            for i in wb.economy.list(db=db['id']):
                try:
                    for (k,v) in wb.economy.metadata.get(i['id'], db=db['id']).metadata.items():
                        if v.strip():
                            df.loc[k, db['id']] = df.get(db['id'], dummy).fillna(0).get(k, 0) + 1
                except KeyboardInterrupt:
                    print("Operation terminated by Ctrl-C")
                    sysInterrupt = True
                    break
                except:
                    logging.warning("Can't get metadata for {} in {}".format(i['id'], db['id']))
        else:
            raise NotImplementedError

df.to_csv(config['CSV'])
