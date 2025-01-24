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

import svgwrite
import re
import textwrap
import math

## Helper functions to calculate the gradients

def gaussian(x, a, b, c, d=0):
    return a * math.exp(-(x - b)**2 / (2 * c**2)) + d

def color(val, maximum=100, map=[], spread=1):
    maximum = float(maximum)
    r = sum([gaussian(val, p[1][0], p[0] * maximum, maximum/(spread*len(map))) for p in map])
    g = sum([gaussian(val, p[1][1], p[0] * maximum, maximum/(spread*len(map))) for p in map])
    b = sum([gaussian(val, p[1][2], p[0] * maximum, maximum/(spread*len(map))) for p in map])
    return "rgb(" + str(int(min(255.0, r*255.0))) + ", " + str(int(min(255.0, g*255.0))) + ", " + str(int(min(255.0, b*255.0))) + ")"


MAX_LENGTH=30
SHIFT_LINE=3



class Tree2SVG:

	width = 300.0
	height = 210.0
	padding = 10
	horizontal = True
	padding_level = [8, 8, 4, 2, 1]
	font_size = [4,4,3.5,3.5,3.0]
	criteria = ""
	
	colormap = {}
	
	colormap['heatmap'] = [
		    [0.0, (1, 0, 0)],
		    [0.10, (1, 0, 0)],
		    [0.5, (1, 0.75, 0)],
		    [0.9, (0, 1, 0)],
		    [1.0, (0, 1, 0)],
  		  ]

	colormap['blues'] = [
		    [0.0, (216/255, 230/255, 241/255)],
		    [0.5, (62/255, 132/255, 190/255)],
		    [1.0, (24/255, 52/255, 77/255)],
  		  ]

	

	def __init__(self, tree, database, svgfilename, criteria, width, height, args):
		
		self.filename = svgfilename
		self.tree = tree
		self.width = float(width)
		self.height = float(height) 

		self.database = database
		self.drawing = svgwrite.Drawing(svgfilename, size = (str(self.width)+"mm", str(self.height)+"mm"), profile='tiny')
		self.criteria = criteria
		self.args = args
		

	def get_value(self, nid, name, key):
		for row in self.database:
			#print("DB", nid, row[0], key, row[1], row[2])
			if (row[0] == nid or row[0] == name) and row[1] == key:
				return row[2]
		return ""

	def save(self):
		self.drawing.save()

	def render(self):
		self.render_tree(0,0,self.width,self.height, self.tree, self.horizontal)

	def getcolor(self, nid, name, last):
		boxcolor = 'white'
		#boxcolor = color(5, maximum=10, map=self.heatmap)
	
		value = self.get_value(nid,name,self.criteria)
		print(nid, name, value)
	
		if value != "":
			boxcolor = color(float(value), maximum=self.args.max, map=self.colormap[self.args.map])
		
		if (self.criteria == ""):
			boxcolor = "white"
	
		return boxcolor

	def getbubblecolor(self, nid, name, last):
		boxcolor = 'white'
		value = self.get_value(nid,name,self.args.bubble)
		print(nid, name, value)
	
		if value != "":
			boxcolor = color(float(value), maximum=self.args.bubblemax, map=self.colormap[self.args.bubblemap])
		
		if (self.args.bubble == ""):
			boxcolor = "white"
	
		return boxcolor

	def render_tree(self, x, y, width, height, captree, horizontal):

		pad = self.padding		
		lastpad = self.padding


		# Figure out if this is a node without any subnodes
		lastlevel = False
		fontcolor = "black"
		name = captree.name
		nid = ""

		result = re.match("\[(.+)\](.*)", name)
		if result:
			nid = result.group(1)
			name = result.group(2)
			
		for child in captree.children:
			if len(child.children) <= 0:
				lastlevel = True
			elif len(child.children) >= 0:
				lastlevel = False
				break

		boxcolor = self.getcolor(nid, name, lastlevel)
		print("Boxcolor", boxcolor)

		# Draw box
		self.drawing.add(self.drawing.rect((str(x)+'mm', str(y)+'mm'), (str(width)+'mm', str(height)+'mm'), fill=boxcolor, stroke='black'))
		print("rect: ", x, y, width, height)
		print("Depth: ", captree.depth)
		if captree.depth < len(self.padding_level):
			pad = self.padding_level[captree.depth]

		if captree.depth < len(self.padding_level) and captree.depth > 0:
			lastpad = self.padding_level[captree.depth-1]
		

		fontsize = lastpad/2
		if captree.depth < len(self.font_size):
			fontsize = self.font_size[captree.depth]

	
		# Reduce padding for last level of boxes
		if lastlevel:
			pad = pad * 2 / 3

		# Draw text		
		if len(captree.children) > 0:
			self.drawing.add(self.drawing.text(name, 
							   insert=(str(x)+'mm', str(y-0.25*lastpad)+'mm'), 
							   fill=fontcolor,  
							   font_size=str(fontsize)+"mm"))
		else:
			if len(name) < MAX_LENGTH:
				self.drawing.add(self.drawing.text(name, 
								   insert=(str(x+width/2)+'mm', str(y+height/2 + (lastpad/4))+'mm'), 
								   fill=fontcolor,  
								   font_size=str(fontsize)+"mm", 
								   text_anchor="middle"))
			else:
				# wraped = textwrap.shorten(name, width=30, placeholder="...")
				wraped = textwrap.wrap(name, width=30)
				add = (4 - len(wraped)) * lastpad/4
				for i in range(len(wraped)):
					self.drawing.add(self.drawing.text(wraped[i], 
									   insert=(str(x+width/2)+'mm', str(add + y+height/4 + i*SHIFT_LINE*(lastpad/4))+'mm'), 
									   fill=fontcolor,  
									   font_size=str(fontsize)+"mm", 
									   text_anchor="middle"))

		# Draw bubble
		if (self.args.bubble != ""):
			print("Creating bubble")
			bubblecolor = self.getbubblecolor(nid, name, lastlevel)
			if (bubblecolor!= "white" ):
				self.drawing.add(
					self.drawing.circle(center=(str(x+width)+"mm", str(y+height/2)+"mm"), r=15, fill=bubblecolor, stroke='black')
			)

		cnt = 0
		for child in captree.children:
			print(child.name)
			print(len(child.children))
			nx = x + 0.5 * pad
			ny = y + pad
			nwidth = width - 1 * pad
			nheight = height  - 1.5 * pad
			
			
			if len(captree.children) > 0:
				if horizontal:
					nheight = (height / (len(captree.children))) - 2 * pad
					ny = y + cnt * (nheight + 2* pad) + pad
					nheight = nheight + 0.5*pad
					if lastlevel:
						ny = y + cnt * (nheight + 2* pad) + 0.5 * pad
						ny = ny - cnt * 0.5 * pad
						nheight = nheight + 0.5 * pad
						

				else:
					nwidth = ( width / (len(captree.children) )) - 2 * pad
					nx = x + cnt * (nwidth + 2 * pad) + 0.5 * pad
					nwidth = nwidth + 1 * pad
				
			self.render_tree(nx, ny, nwidth, nheight, child, not horizontal)
			cnt = cnt + 1
			
		#return dwg
