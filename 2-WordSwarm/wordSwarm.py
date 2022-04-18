# -*- coding: utf-8 -*-
"""

	This is the main WordSwarm program. It reads in a CSV file
	that contains a first column of words and subsequent columns
	with the words' frequency with each date specified by the 
	first row of the CSV file. 
	
	Arguments:
		-t <title>
			: Title to display in output. Quotes are required if
			   the title has more than one word
		-i <inputfile> 
			: CSV file to read (default: nGrams2plot.csv)
		-s
			: Should frames be saved as image files (default: false)
				Default directory is '../3-Postprocessing/frames/'
				if the -d argument is not used.
		-d <output directory of frames>
			: Directory to save output frame images. 
				-s not required when -d is used
				It is best practice to use quotes.
				A final '/' should be added to the directory
		-m <max word height>
			: A value that determines how big words are allowed to get.
				The default value is 2. Typically between 5-10.
				Tweak this parameter until the wordSwarm is large 
				enough to see, yet doesn't overflow the screen.
		-c <HexHue1_HexHue2>
			: Define the two hues that all words will be randomly colored
				with. Values are in hexdecimal between 0-255
				Example: "-c AA_00" will use red and blue hues
		-b <Start Date in YYYYMMDD>
			: If records in CSV start before what you would like to display
				then specify the desired start date
				Example: "-b 19900101" will start the animation on
				January 1st, 1990
		-e <End Date in YYYYMMDD>
			: If records in CSV go beyond what you would like to display
				then specify the desired end date
				Example "-e 20131231" will end the animation on
				December 31st, 2013
		-n <topN>
			: Display only the first topN words in the CSV file
				Example "-n 250" will plot up to only 250 words 
				even if the CSV file has >250 words
	
	This file is part of WordSwarm.

    WordSwarm is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    WordSwarm is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

	Copyright 2014 Michael Kane	
	
	PyBox2D Framework:

	This software is provided 'as-is', without any express or implied
	warranty.  In no event will the authors be held liable for any damages
	arising from the use of this software.
	Permission is granted to anyone to use this software for any purpose,
	including commercial applications, and to alter it and redistribute it
	freely, subject to the following restrictions:
	1. The origin of this software must not be misrepresented; you must not
	claim that you wrote the original software. If you use this software
	in a product, an acknowledgment in the product documentation would be
	appreciated but is not required.
	2. Altered source versions must be plainly marked as such, and must not be
	misrepresented as being the original software.
	3. This notice may not be removed or altered from any source distribution.	
	
	C++ version Copyright (c) 2006-2007 Erin Catto http://www.box2d.org
	Python version by Ken Lauer / sirkne at gmail dot com

"""

import sys, os, getopt # For system operations and argument parsing
import random
import re

# Import the PyBox2D/PyGame framework
sys.path.append('./framework') 
from framework import * # The abstracted PyBox2D framework
import pygame # The PyGame 'sub-framework'
from pygame.locals import * # Some parts of the PyGame framework to import locally

# Import WordSwarm modules
from wsWordObj import * # Module with a class for representing words
from wsNGrams  import * # Module for storing nGram time histories

class WordSwarm (Framework):

	# Settings
	name="WordSarm"
	saveFrames = False
	csvName = 'nGrams2plot.csv'
	saveFolder = '../3-Postprocessing/frames/'
	
	frameN = 0;
	shapes = [];
	fixtures = [];
	bodies = [];
	joints = [];
	wordObjs = []
	sun = []
	wordHue = (-1, -1)
	topN = sys.maxsize
	
	# Size of words (m)
	maxSize = 5
	minSize = 0.1
	
	# Sun strength
	frequency = 0.1
	damping = 2
	
	def __init__(self, argv):
	
		# Initialize pygame/pybox2d framework/world
		super(WordSwarm, self).__init__()
		self.world.gravity = (0,0);	
		startDateStr = None
		endDateStr = None
				
		# Parse arguments
		try:
			opts, args = getopt.getopt(argv,
					"hst:i:d:m:c:b:e:n:",["ifile="])
		except getopt.GetoptError:
			print ('Invalid argument')
			print(argv)
			print('try:')
			print ('wordSwarm.py -n <topN] -s -t <title> -i <inputfile> -d <outputFolder> -m <maxWordHeight> -c <HexHue1_HexHue2> -b <startDate YYYYMMDD> -e <endDate YYYYMMDD>')
			sys.exit(2)
			
		for opt, arg in opts:
			if opt == '-h':
				print ('wordSwarm.py -n <topN] -s -t <title> -i <inputfile> -d <outputFolder> -m <maxWordHeight> -c <HexHue1_HexHue2> -b <startDate YYYYMMDD> -e <endDate YYYYMMDD>')
				sys.exit()
			elif opt in ("-i", "--ifile"):
			
				print('Reading csv: %s' % arg)
				self.csvName = arg
				
			elif opt in ("-d"):
				self.saveFrames = True
				self.saveFolder = arg
				print('Saving frames to %s' % self.saveFolder)	
				
			elif opt in ("-s"):
				self.saveFrames = True
				print('Saving frames to %s' % self.saveFolder)	
				
			elif opt in ("-t"):
			
			
				print('WordSwarm title: %s' % arg)
				self.name = arg
				
			elif opt in ("-m"):
				self.maxSize = int(arg)
				print('Max word height set to: %d' % self.maxSize)
				
			elif opt in ("-c"):
				self.wordHue = (int(arg[0:2],16), int(arg[3:5],16))
				print('Words will have hues %d or %d' % (self.wordHue[0], self.wordHue[1]))
				
			elif opt in ("-b"):
				startDateStr = arg
				print('Starting animation at %s' % startDateStr)
				
			elif opt in ("-e"):
				endDateStr = arg
				print('Ending animation on %s' % endDateStr)
				
			elif opt in ("-n"):
				self.topN = int(arg)
				print('Displaying only the first %d results in csv' % self.topN)
		
		# Create output directory if required
		if self.saveFrames:
			if not os.path.exists(self.saveFolder):
				os.makedirs(self.saveFolder)
			else:
				self.purge(self.saveFolder, '.*')
		
		# Create ngrams database
		self.nGrams = wsNGrams(self.csvName, startDateStr, endDateStr, self.topN)	

		box_half_size = (0.5, 0.5)

		# Place word objects
		self.shapes = [None] * self.nGrams.nWords
		self.fixtures = [None] * self.nGrams.nWords
		self.bodies = [None] * self.nGrams.nWords
		self.joints = [None] * self.nGrams.nWords
		self.wordObjs = [None] * self.nGrams.nWords;
		for word_k in range(0, self.nGrams.nWords):
		
			# The centre of the universe
			self.sun.append(self.world.CreateStaticBody(
					position=b2Vec2(random.uniform(
							-45,65),0)));		
			
			# Create word object
			if self.nGrams.areColors == 'hue':
				self.wordObjs[word_k] = wsWordObj(
						self.nGrams.words[word_k], [self.nGrams.colors[word_k]])
			elif self.nGrams.areColors == 'rgb':
				self.wordObjs[word_k] = wsWordObj(
						self.nGrams.words[word_k], self.nGrams.colors[word_k])
			else:
				self.wordObjs[word_k] = wsWordObj(
						self.nGrams.words[word_k], self.wordHue)
			
			# Create body for word
			self.bodies[word_k] = self.world.CreateDynamicBody(
				position=(random.uniform(-60,70), random.uniform(-40,40) ))
				
			# Add fixture to body
			self.fixtures[word_k] = self.bodies[word_k].CreateFixture(
					b2FixtureDef( shape = b2PolygonShape( box = (
					box_half_size[0] / self.wordObjs[word_k].paddedAR,box_half_size[0]))))
				
			# Link word object to sun
			self.joints[word_k] = self.world.CreateJoint(
					b2DistanceJointDef(
						frequencyHz = self.frequency,
						dampingRatio = self.damping,
						bodyA=self.sun[word_k],
						bodyB=self.bodies[word_k],
						localAnchorA=(0,0),
						localAnchorB=(0,0),
						length = 0.5 ))

	# Removes files from a directory matching a pattern
	def purge(self, dir, pattern):
		for f in os.listdir(dir):
			if re.search(pattern, f):
				os.remove(os.path.join(dir, f))
		
	# Converts a size in (m) to a size in (px)
	def convertWorld2Screen(self, size_m):
		
		# Generate faux coordinates in (m)
		coord_m1 = size_m
		coord_m2 = list(size_m)
		coord_m2[0] = -coord_m2[0]
		coord_m2[1] = -coord_m2[1]
		
		# Convert faux coordinates to (px)
		coord_px1 = self.renderer.to_screen(coord_m1)
		coord_px2 = self.renderer.to_screen(coord_m2)
		
		# Calculate size from new coordinates
		size_p = [abs(coord_px1[0] - coord_px2[0]),
				abs(coord_px1[1] - coord_px2[1])]
	
		return size_p
		
	# Draw the date progress bar
	#@TODO Scale text and line weight with screen size
	def Draw_Date(self, date_k):
		months = ['','Jan','Feb','Mar','Apr','May','Jun',
				'Jul','Aug','Sep','Oct','Nov','Dec']
	
		color = (255,255,255)
		dateTxt = freetype.Font(None)
		dateTxt.size = 24
		dateTxt.fgcolor = color
	
		top = (int(self.screen.get_height()*0.075),int(self.screen.get_height()*0.125))
		bot = (int(self.screen.get_height()*0.075),int(self.screen.get_height()*(1-0.125)))
		
		self.screen.blit(dateTxt.render(self.name)[0], 
				(self.screen.get_height()*0.03, self.screen.get_height()*0.03))
		
		pygame.draw.line(self.screen, color, top, bot, 4)
		pygame.draw.line(self.screen, color, (top[0]-4, top[1]), (top[0]+4, top[1]), 4)
		pygame.draw.line(self.screen, color, (bot[0]-4, bot[1]), (bot[0]+4, bot[1]), 4)
				
		self.screen.blit(dateTxt.render('%s %04d'%(
				months[self.nGrams.dates[0].month],
				self.nGrams.dates[0].year))[0], 
				(self.screen.get_height()*0.03, top[1]-40))
				
		self.screen.blit(dateTxt.render('%s %04d'%(
				months[self.nGrams.dates[-1].month],
				self.nGrams.dates[-1].year))[0], 
				(self.screen.get_height()*0.03, bot[1]+20))
		
		progress = ( (self.nGrams.dates[date_k] - self.nGrams.dates[0]).total_seconds() /
				(self.nGrams.dates[-1] - self.nGrams.dates[0]).total_seconds() )
		
		pos = (top[0] + 1, int((bot[1] - top[1]) * progress + top[1]) )
		pygame.draw.circle(self.screen, color, pos, 8)
				
		self.screen.blit(dateTxt.render('%s %04d'%(
				months[self.nGrams.dates[date_k].month],
				self.nGrams.dates[date_k].year))[0], 
				(pos[0]+20, pos[1]-10))
				
		logo = pygame.transform.smoothscale(pygame.image.load(
				'../wordSwarm_light.png').convert_alpha(), (187, 99))
		self.screen.blit(logo, (1720,960))
				
	def Step(self, settings):
				
		self.screen.fill((0,0,0))
		
		self.frameN = self.frameN+1;
		
		# Update ngram date every n-frames
		nFrames = 30
		date_k = int(self.frameN / nFrames) + 1 # Date moving towards
		phase = (self.frameN % nFrames) / float(nFrames) # (0-1) way to new date		

		# Stop if at the end of the dataset
		if date_k == self.nGrams.nDates:
			print('WordSwarm animation complete')
			print('Hope you enjoyed the show!')
			exit()
		
		dateTxt = freetype.Font(None)
		dateTxt.size = 12
		dateTxt.fgcolor = (255,255,255)
		
		self.Draw_Date(date_k) # Draw the date
		
		# Update size of each word
		#@TODO There is a memory leak in creating the new bodies (it doesn't delete the old ones)
		for word_k in range(0, self.nGrams.nWords):
			
			# Calculate word sizes
			if phase == 1:
				newSize = (0,0)
				
				newSize[1] = (self.maxSize - self.minSize) * (self.nGrams.counts[word_k][date_k-1] / float(self.nGrams.maxCount)) + self.minSize
				
				newSize[0] = newSize[1] / self.wordObjs[word_k].paddedAR
				
				self.wordObjs[word_k].boxSize = self.convertWorld2Screen( newSize )
			else:
				newSize = list((0,0))
				newSize[1] = (self.maxSize - self.minSize) * (self.nGrams.counts[word_k][date_k] / float(self.nGrams.maxCount)) + self.minSize
				newSize[0] = newSize[1] / self.wordObjs[word_k].paddedAR
				
				oldSize = list((0,0))
				oldSize[1] = (self.maxSize - self.minSize) * (self.nGrams.counts[word_k][date_k-1] / float(self.nGrams.maxCount)) + self.minSize
				oldSize[0] = oldSize[1] / self.wordObjs[word_k].paddedAR
				
				size = list((0,0))
				size[0] = (newSize[0] - oldSize[0]) * phase + oldSize[0]
				size[1] = (newSize[1] - oldSize[1]) * phase + oldSize[1]
				
				self.wordObjs[word_k].boxSize = self.convertWorld2Screen( size )
				
			# Re-create fixture
			self.bodies[word_k].DestroyFixture(self.fixtures[word_k])
			self.fixtures[word_k] = None
			self.fixtures[word_k] = self.bodies[word_k].CreateFixture(
					b2FixtureDef(shape=b2PolygonShape(box=newSize)))
			
			# Redraw word in new shape
			pos = self.renderer.to_screen(self.bodies[word_k].position);	
			self.wordObjs[word_k].Draw(self.screen, pos)
			
		# Save frames to create film
		if self.saveFrames:
			pygame.image.save(self.screen, 
					self.saveFolder + int(self.frameN).__format__('')
					+ '.png')
		
		Framework.Step(self, settings);
			
			
if __name__=="__main__":
	main(WordSwarm,sys.argv[1:])
