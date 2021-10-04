import json
import random
import math
from tqdm import tqdm
from argparse import ArgumentParser
from subprocess import check_output

parser = ArgumentParser(description='Check if train and test split is inductive (No shared entity)')
parser.add_argument('train_file', help='Name of the train split')
parser.add_argument('test_file', help='Name of the test split')

if __name__ == '__main__':
	args = parser.parse_args()
	train_entities, test_entities = set(), set()
	for line in open(args.train_file, 'r'):
		triplet = line.replace('\n', '').split('\t')
		h,_,t = triplet
		train_entities.add(h)
		train_entities.add(t)
	for line in open(args.test_file, 'r'):
		triplet = line.replace('\n', '').split('\t')
		h,_,t = triplet
		test_entities.add(h)
		test_entities.add(t)
	if test_entities.isdisjoint(train_entities):
		print('Splits are disjoint :D')
	else:
		print('Splits are NOT disjoint :(')