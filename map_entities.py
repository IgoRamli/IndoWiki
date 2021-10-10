from tqdm import tqdm
from argparse import ArgumentParser
from subprocess import check_output

def wc(filename):
    return int(check_output(["wc", "-l", filename]).split()[0])

parser = ArgumentParser(description='Creates the entity description file for IndoWiki')
parser.add_argument('wiki_file', help='Filename of Wikipedia extracted content')
parser.add_argument('title_file', help='Filename of entity ID - title mapping')
parser.add_argument('--out-file', default='indowiki_text.txt', help='Filename of the resulting description file')
parser.add_argument('--missing-file', default='', help='(Optional) Log file to record missing entities')
parser.add_argument('--unused-file', default='', help='(Optional) Log file to record unused Wikipedia articles')

def parse_entity_desc(args):
  print('Extracting Wikipedia content')
  entity_desc = {}
  
  num_lines = wc(args.wiki_file)
  with open(args.wiki_file, 'r') as f:
    buffer = ''
    title = None
    for line in tqdm(f, total=num_lines):
      if line.isspace():
        if title is not None:
          entity_desc[title] = buffer
        buffer = ''
        title = None
      elif title is None:
        title = line[:-2]
      else:
        buffer += line.replace('\n', '')
    if title is not None:
      entity_desc[title] = buffer
  return entity_desc

def write_to_file(args, entity_desc):
  print('Mapping IDs with descriptions')
  missing_ents = []
  used_titles = set()
  with open(args.out_file, 'w+') as out_file:
    num_lines = wc(args.title_file)
    with open(args.title_file, 'r') as title_file:
      for line in tqdm(title_file, total=num_lines):
        k, v = line.split('\t')
        title = v.replace('\n', '')
        entity_id = k
        try:
          desc = entity_desc[title]
          used_titles.add(title)
          out_file.write('{}\t{}\n'.format(entity_id, desc))
        except:
          missing_ents.append((entity_id, title))
  return missing_ents, used_titles

if __name__ == '__main__':
  args = parser.parse_args()
  entity_desc = parse_entity_desc(args)
  print('{} articles extracted'.format(len(entity_desc)))
  missing_ents, used_titles = write_to_file(args, entity_desc)
  print('{} entities do not have an entry in the given Wikipedia file and will not be included'.format(len(missing_ents)))
  unused_titles = set(entity_desc.keys()) - used_titles
  print('{} articles are not linked to any WikiData entities'.format(len(unused_titles)))
  if args.missing_file is not '':
    print('Writing missing entities')
    with open(args.missing_file, 'w+') as missing_file:
      for k, v in tqdm(missing_ents):
        missing_file.write('{}\t{}\n'.format(k, v))
    print('See \'{}\' for a full list of missing entities'.format(args.missing_file))
  if args.unused_file is not '':
    print('Writing unused articles')
    with open(args.unused_file, 'w+') as unused_file:
      for k in tqdm(unused_titles):
        unused_file.write('{}\n'.format(k))
    print('See \'{}\' for a full list of unused articles'.format(args.unused_file))
