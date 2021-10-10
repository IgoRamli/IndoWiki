import json
import random
import math
from tqdm import tqdm
from argparse import ArgumentParser
from subprocess import check_output

parser = ArgumentParser(description='Split KG triplets into train and test splits')
parser.add_argument('triplet_file', help='Name of the file where all triplets are stored')
parser.add_argument('--setting', choices=['transductive', 'inductive'], help='Sets the type of splits to be done')
parser.add_argument('--valid', type=int, default=5000, help='Number of total triplets that goes to the validation split')
parser.add_argument('--test', type=int, default=5000, help='Number of total triplets that goes to the test split')
parser.add_argument('--out-file-prefix', default='indowiki_transductive', help='Prefix of output file. Splits will be written as <out-file-prefix>_train.txt, <out-file-prefix>_valid.txt and <out-file-prefix>_test.txt')

def wc(filename):
    return int(check_output(["wc", "-l", filename]).split()[0])

def parse_triplets(args):
  triplets = []
  num_lines = wc(args.triplet_file)
  with open(args.triplet_file, 'r') as triplet_file:
    for line in tqdm(triplet_file, total=num_lines):
      triplets.append(line.replace('\n', '').split('\t')[:3])
  return triplets

def transductive_split(args, triplets):
  random.shuffle(triplets)

  len_total = len(triplets)
  len_valid = args.valid
  len_test = args.test
  return triplets[(len_valid+len_test):], \
       triplets[len_test:(len_test+len_valid)], \
       triplets[:len_test]

def generate_inductive(triplets, treshold):
  adj = {}
  for i,triplet in enumerate(triplets):
    h,_,t = triplet
    if h not in adj:
      adj[h] = []
    adj[h].append(i)
    if t not in adj:
      adj[t] = []
    adj[t].append(i)
  visited = [ 0 for i in triplets ]

  subset = []
  for i in tqdm(range(treshold)):
    tmp = max(visited)
    nxt = visited.index(tmp)

    h,_,t = triplets[nxt]
    for h2 in adj[h]:
      visited[h2] += 1
    for t2 in adj[t]:
      visited[t2] += 1
    subset.append(triplets[nxt])
    visited[nxt] = -1e9
  return subset

def split_triplets(triplets, sz_a):
  random.shuffle(triplets)

  len_total = len(triplets)

  a = generate_inductive(triplets, sz_a)
  a_entities = { h for h,_,_ in a }.union({ t for _,_,t in a })
  a = [ (h, r, t) for h,r,t in triplets \
            if h in a_entities \
            and t in a_entities ]
  b = [ (h, r, t) for h,r,t in triplets \
            if h not in a_entities \
            and t not in a_entities ]
  return a, b

def inductive_split(args, triplets):
  test, not_test = split_triplets(triplets, args.test)
  valid, train = split_triplets(not_test, args.valid)
  return train, valid, test

def write_to_out_file(args, train, valid, test):
  train_file_name = args.out_file_prefix + '_train.txt'
  with open(train_file_name, 'w+') as train_file:
    print('Writing to training file ({})'.format(train_file_name))
    for h, r, t in tqdm(train):
      train_file.write('{}\t{}\t{}\n'.format(h, r, t))

  valid_file_name = args.out_file_prefix + '_valid.txt'
  with open(valid_file_name, 'w+') as valid_file:
    print('Writing to test file ({})'.format(valid_file_name))
    for h, r, t in tqdm(valid):
      valid_file.write('{}\t{}\t{}\n'.format(h, r, t))

  test_file_name = args.out_file_prefix + '_test.txt'
  with open(test_file_name, 'w+') as test_file:
    print('Writing to test file ({})'.format(test_file_name))
    for h, r, t in tqdm(test):
      test_file.write('{}\t{}\t{}\n'.format(h, r, t))

if __name__ == '__main__':
  args = parser.parse_args()
  print('Parsing triplets')
  triplets = parse_triplets(args)
  print('Splitting dataset')
  if args.setting == 'transductive':
    train, valid, test = transductive_split(args, triplets)
  else:
    train, valid, test = inductive_split(args, triplets)
  print('Train size = {}; Validation size = {}; Test size = {}'.format(len(train), len(valid), len(test)))
  print('Writing splits')
  write_to_out_file(args, train, valid, test)
