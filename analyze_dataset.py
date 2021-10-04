import json
import random
import math
from tqdm import tqdm
from argparse import ArgumentParser
from subprocess import check_output

parser = ArgumentParser(description='Get information of split')
parser.add_argument('file', help='Name of the split to be analyzed')

if __name__ == '__main__':
	args = parser.parse_args()
	entities, relations = set(), set()
	num_triplets = 0
	for line in open(args.file, 'r'):
		triplet = line.replace('\n', '').split('\t')
		h,r,t = triplet
		entities.add(h)
		entities.add(t)
		relations.add(r)
		num_triplets += 1
	print('#Entity   =', len(entities))
	print('#Relation =', len(relations))
	print('#Triplet  =', num_triplets)