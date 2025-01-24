# 
# generate_capability_map - Generate a capability map from a *.cap file
# Copyright (C) 2025 Oliver Bossert
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import re
from io import StringIO
import csv
import math
from anytree import Node, RenderTree, PostOrderIter

from tree2svg import Tree2SVG

def read_capability_map(filename, capaname):
	with open(filename) as file:
		lines = file.readlines()
	return process_capability_map(lines, capaname)

def process_capability_map(lines, capaname):
	level = 0
	lastnodes = []
	root = Node(capaname)
	mode = 0
	csvdata = ""
	for line in lines:
		stripline = line.rstrip() 
		print(stripline)
		
		if re.match("^---", stripline):
			mode = mode + 1
		else:
			if mode == 0:
				thislevel = 0
				space = re.search("^\s*", stripline)
				stripline = stripline.lstrip()
				if space:
					print(len(space.group()))
					thislevel = len(space.group())
				print(len(lastnodes))
				if thislevel <= level:
					if thislevel == 0:
						if len(lastnodes) <= thislevel:
							lastnodes.append(Node(stripline, parent=root))
						else:
							lastnodes[thislevel] =  Node(stripline, parent=root)
					else:
						if len(lastnodes) <= thislevel:
							lastnodes.append(Node(stripline, parent=lastnodes[thislevel-1]))
						else:
							lastnodes[thislevel] =  Node(stripline, parent=lastnodes[thislevel-1])
				else:
					if len(lastnodes) <= thislevel:
						lastnodes.append(Node(stripline, parent=lastnodes[thislevel-1]))
					else:
						lastnodes[thislevel] =  Node(stripline, parent=lastnodes[thislevel-1])
			
			elif mode == 1:
				csvdata = csvdata + line

	# Convert data into dataset
	#print (csvdata)
	f = StringIO(csvdata)
	reader = csv.reader(f, delimiter=',')
	data = []
	for row in reader:
	    print('\t'.join(row))
	    if len(row) == 3:
		    data.append(row)

	for pre, fill, node in RenderTree(root):
		print("%s%s" % (pre, node.name))

	return root, data



def is_in_database(database, name):
	for row in database:
		if len(row) > 0:
			if (row[0] == name):
				return True
	return False

def get_from_database(database, name, key):
	for row in database:
		if len(row) > 0:
			if (row[0] == name and row[1]==key):
				return row[2]
	return -999

def get_all_keys_from_database(database):
	ids = {}
	for row in database:
		ids.update({row[1] : 1})
	return list(ids.keys())


		
def prune(tree, target, current):
	if current >= target:
		tree.children = []

	return tree

def summarize(database, tree):
	all_keys = get_all_keys_from_database(database)
	for node in PostOrderIter(tree):
		if not is_in_database(database, node.name) :
			average = {}
			count = {}
			for key in all_keys:
				average[key] = 0
				count[key] = 0
			for subnode in node.children:
				for key in all_keys:
					value = get_from_database(database, subnode.name, key)
					if value != -999:
						average[key] = average[key] + float(value)
						count[key] = count[key] + 1
			for key in all_keys:
				if count[key] > 0:
					database.append([node.name, key, str(average[key]/count[key])])


	return database

		
def restrict_capability_map(tree, database, level):
	# Summarize database based on averages
	database = summarize(database, tree)

	# Prune the tree 
	#tree = prune(tree, level, 1)
	for node in PostOrderIter(tree):
		if node.depth > float(level):
			print("Pruning "+node.name)
			node.children=[]
	return tree, database
		
		
import sys	
import argparse
 
parser = argparse.ArgumentParser(description="Parser for capability map files",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-o", "--output", default="output.svg", help="Output filename for svg file")
parser.add_argument("-t", "--title", default="Enterprise Architecture capability map", help="Title of the map")
parser.add_argument("-c", "--criteria", default="", help="Criteria used for color coding")
parser.add_argument("-r", "--restrict", default="0", help="Restrict to a certain level")
parser.add_argument("-m", "--max", default="10", help="Max value for color coding")
parser.add_argument("-x", "--map", default="heatmap", help="Mapping for color coding")

parser.add_argument("-b", "--bubble", default="", help="Criteria used for bubble")
parser.add_argument("-n", "--bubblemax", default="10", help="Maximum value for bubbles")
parser.add_argument("-y", "--bubblemap", default="heatmap", help="Color mapping for bubbles")

parser.add_argument("-l", "--height", default="210", help="Color mapping for bubbles")
parser.add_argument("-w", "--width", default="300", help="Color mapping for bubbles")

parser.add_argument("input", help="Input file name .cap")

args = parser.parse_args()
#config = vars(args)
#print(config)
		

#(tree, database) = read_capability_map("personal.cap", "Enterprise Architecture capabilities")
(tree, database) = read_capability_map(args.input, args.title)

if args.restrict != "0":
	(tree, database) = restrict_capability_map(tree, database, args.restrict)

svgtree = Tree2SVG(tree, database, args.output, args.criteria, args.width, args.height, args)
svgtree.render()
svgtree.save()





