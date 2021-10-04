import json
import random
from tqdm import tqdm
from argparse import ArgumentParser
from subprocess import check_output

from qwikidata.entity import WikidataItem
from qwikidata.json_dump import WikidataJsonDump
from qwikidata.utils import dump_entities_to_json

def wc(filename):
    return int(check_output(["wc", "-l", filename]).split()[0])

parser = ArgumentParser(description='Creates indowiki_triplets.txt, a list of valid knowledge graph relations')
parser.add_argument('dump_file', help='Filename of WikiData JSON dump')
parser.add_argument('desc_file', help='Filename of entity description file')
parser.add_argument('--out-file', default='titles.txt', help='The name of the mapping text file')

def parse_entities(args):
  print('Extracting Wikipedia content')
  entities = set()
  num_lines = wc(args.desc_file)
  with open(args.desc_file, 'r') as f:
    for line in tqdm(f, total=num_lines):
      entity_id = line.split('\t')[0]
      entities.add(entity_id)
  return entities

def parse_triplets(args, item, triplets, entities):
  if item.entity_id not in entities:
    return
  claims = item.get_truthy_claim_groups()
  for prop, ents in claims.items():
    for ent in ents:
      mainsnak = ent.mainsnak
      if mainsnak.value_datatype == 'wikibase-entityid':
        dataval = mainsnak.datavalue.value
        if dataval['entity-type'] == 'item':
          ent_id = dataval['id']
          if ent_id in entities:
            triplets.append((item.entity_id, prop, ent_id))

def extract_triplets(args, entities, dump_size):
  print('Extracting valid triplets')
  wjd = WikidataJsonDump(args.dump_file)
  triplets = []
  with open(args.out_file, 'w+') as out_file:
    for ii, entity_dict in tqdm(enumerate(wjd), total=dump_size):
      entity_id = entity_dict['id']
      entity_type = entity_dict['type']
      if entity_type == 'item':
        parse_triplets(args, WikidataItem(entity_dict), triplets, entities)
  return triplets

def write_to_out_file(args, triplets):
  with open(args.out_file, 'w+') as out_file:
    for h, r, t in tqdm(triplets):
      out_file.write('{}\t{}\t{}\n'.format(h, r, t))

def get_number_of_entities(args, wjd):
  return sum(1 for i in tqdm(enumerate(wjd)))

if __name__ == '__main__':
  args = parser.parse_args()
  wjd = WikidataJsonDump(args.dump_file)
  print('Detecting entities from dump file')
  dump_size = get_number_of_entities(args, wjd)
  print('{} entities detected from dump'.format(dump_size))
  print('Extracting valid entity IDs')
  entities = parse_entities(args)
  print('Extracting triplets')
  triplets = extract_triplets(args, entities, dump_size)
  random.shuffle(triplets)
  print('Dumping triplets to file')
  write_to_out_file(args, triplets)
  print('{} IDs mapped'.format(len(triplets)))