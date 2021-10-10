import json
import random
import math
from tqdm import tqdm
from argparse import ArgumentParser
from subprocess import check_output

parser = ArgumentParser(description='Check if train and test split is inductive (No shared entity)')
parser.add_argument('train_file', help='Name of the file containing train split')
parser.add_argument('valid_file', help='Name of the file containing validation split')
parser.add_argument('test_file', help='Name of the file containing test split')

def check_inductivity(train, valid, test):
	train_valid = valid.isdisjoint(train)
	train_test = test.isdisjoint(train)
	valid_test = test.isdisjoint(valid)
	return train_valid, train_test, valid_test

if __name__ == '__main__':
	args = parser.parse_args()
	train_entities, valid_entities, test_entities = set(), set(), set()
	for line in open(args.train_file, 'r'):
		triplet = line.replace('\n', '').split('\t')
		h,_,t = triplet
		train_entities.add(h)
		train_entities.add(t)
	for line in open(args.valid_file, 'r'):
		triplet = line.replace('\n', '').split('\t')
		h,_,t = triplet
		valid_entities.add(h)
		valid_entities.add(t)
	for line in open(args.test_file, 'r'):
		triplet = line.replace('\n', '').split('\t')
		h,_,t = triplet
		test_entities.add(h)
		test_entities.add(t)

	train_valid, train_test, valid_test = check_inductivity(train_entities, valid_entities, test_entities)
	print('***** Result *****')
	if train_valid:
		print('Training and validation split are disjoint :D')
	else:
		print('Training and validation split are NOT disjoint :(')
	if train_test:
		print('Training and testing split are disjoint :D')
	else:
		print('Training and testing split are NOT disjoint :(')
	if valid_test:
		print('Validation and testing split are disjoint :D')
	else:
		print('Validation and testing split are NOT disjoint :(')