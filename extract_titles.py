import json
from tqdm import tqdm
from argparse import ArgumentParser

from qwikidata.entity import WikidataItem
from qwikidata.json_dump import WikidataJsonDump
from qwikidata.utils import dump_entities_to_json

parser = ArgumentParser(description='Creates a mapping between WikiData entity ID and it\'s corresponding title')
parser.add_argument('dump_file', help='Filename of WikiData JSON dump')
parser.add_argument('--sitelink', default='idwiki', help='The ID of Wikisite whose title name should be used')
parser.add_argument('--out-file', default='titles.txt', help='The name of the mapping text file')

entities = set()

def parse_title(args, item, out_file):
  entity_id = item.entity_id
  entity_int = int(entity_id[1:])
  sitelinks = item.get_sitelinks(prefix=args.sitelink)
  if args.sitelink in sitelinks:
    # Item exists in Wikipedia bahasa indonesia
    title = sitelinks[args.sitelink]['title']
    out_file.write('{}\t{}\n'.format(entity_id, title))
    entities.add(entity_int)

def iterate_entities(args, wjd, out_file):
  entity_cnt = 0
  for ii, entity_dict in tqdm(enumerate(wjd)):
    entity_id = entity_dict['id']
    entity_type = entity_dict['type']
    if entity_id in entities:
    	continue

    if entity_type == 'item':
      parse_title(args, WikidataItem(entity_dict), out_file)
    entity_cnt += 1
  return entity_cnt

if __name__ == '__main__':
	args = parser.parse_args()
	wjd = WikidataJsonDump(args.dump_file)
	print('Extracting entities')
	with open(args.out_file, 'w+') as out_file:
		iterate_entities(args, wjd, out_file)
	print('{} IDs mapped'.format(len(entities)))