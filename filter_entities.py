import json
from tqdm import tqdm
from argparse import ArgumentParser

from qwikidata.entity import WikidataItem
from qwikidata.json_dump import WikidataJsonDump
from qwikidata.utils import dump_entities_to_json

parser = ArgumentParser(description='Process a full JSON dump and extract entities only available in the specified wiki')
parser.add_argument('in_file', help='Filename of JSON dump')
parser.add_argument('--sitelink', default='idwiki', help='ID of Wikisite')

def iterate_entities(wjd, out_file):
  out_file.write('[\n')
  entities_cnt = 0
  for ii, entity_dict in tqdm(enumerate(wjd)):
    entity_id = entity_dict['id']
    entity_type = entity_dict['type']

    if entity_type == 'item':
      item = WikidataItem(entity_dict)
      sitelinks = item.get_sitelinks(prefix=args.sitelink)
      if args.sitelink in sitelinks:
        # Item exists in Wikipedia bahasa indonesia
        title = sitelinks[args.sitelink]['title']
        if entities_cnt > 0:
          out_file.write(',\n')
        out_file.write(json.dumps(item._entity_dict))
        entities_cnt += 1
  out_file.write('\n]')
  return entities_cnt

args = parser.parse_args()
dump_id = args.in_file.split('.')[0]
out_filename = '{}-{}.json'.format(dump_id, args.sitelink)

wjd = WikidataJsonDump(args.in_file)
print('Filtering entities:')
with open(out_filename, 'w+') as f:
  total_count = iterate_entities(wjd, f)
print('No. of filtered entities:', total_count)