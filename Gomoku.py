#Jared Gruneiro
#Senior Design
#Tic Tac Toe Reinforcement Learning 
#October 10, 2017

MARKERS = ['X', 'O']

from random import randint
import copy
import ast
import random

class Board(object):

	def __init__(self):
		self.state = []
		self.newBoard()

	# For testing, shouldn't be used, prefer to use the printBoard method in the Game class
	def printBoard(self):
		print("-------------------------------------------------------------------------------------------------------")
		for i in range(15):
			for j in range(15):
				print("| " + self.state[i][j] + " | "),
			print("")
		print("-------------------------------------------------------------------------------------------------------")

	#Clear Board
	def newBoard(self):
		self.state = []
		for i in range(15):
			row = []
			for j in range(15):
				row.append(' ')
			self.state.append(row)

	#Return the state of the board as an array of arrays
	def getState(self):
		return self.state

	#Place a marker on the board (make a move)
	def place(self, marker, x, y):
		if marker in MARKERS and self.state[y][x] not in MARKERS:
			self.state[y][x] = marker

	# Returns winner's marker if there is a winner, and None if the game can continue.  The function
	# looks at each spot on the board, and if its not null, checks in all surrounding directions
	# to see if it is part of a 5 (or more) in a row.
	def checkForWin(self):
		for i in range(15):
			for j in range(15):
				if self.state[i][j] in MARKERS:
					marker = self.state[i][j]
					horzCount = 0
					vertCount = 0
					topLeftDiagCount = 0
					botLeftDiagCount = 0
					top = i - 1
					bot = i + 1
					left = j - 1
					right = j + 1
					#Top left i, top left j, top right i, etc...
					tlI = i - 1
					tlJ = j - 1
					trI = i - 1
					trJ = j + 1
					blI = i + 1
					blJ = j - 1
					brI = i + 1
					brJ = j + 1

					#Check vertical
					while top > -1:
						if self.state[top][j] is marker:
							vertCount += 1
							top -= 1
						else:
							break
					while bot < 15:
						if self.state[bot][j] is marker:
							vertCount += 1
							bot += 1
						else:
							break

					if vertCount >= 4:
						return marker

					#Check horizontal
					while left > -1:
						if self.state[i][left] is marker:
							horzCount += 1
							left -= 1
						else:
							break
					while right < 15:
						if self.state[i][right] is marker:
							horzCount += 1
							right += 1
						else:
							break

					if horzCount >= 4:
						return marker

					#Check diagonal (top left to bottom right)
					while tlI > 0 and tlJ > 0:
						if self.state[tlI][tlJ] is marker:
							topLeftDiagCount += 1
							tlI -= 1
							tlJ -= 1
						else:
							break
					while brI < 15 and brJ < 15:
						if self.state[brI][brJ] is marker:
							topLeftDiagCount += 1
							brI += 1
							brJ += 1
						else:
							break

					if topLeftDiagCount >= 4:
						return marker

					#Check diagonal (bottom left to top right)
					while blI < 15 and blJ > 0:
						if self.state[blI][blJ] is marker:
							botLeftDiagCount += 1
							blI += 1
							blJ -= 1
						else:
							break
					while trI > 0 and trJ < 15:
						if self.state[trI][trJ] is marker:
							botLeftDiagCount += 1
							trI -= 1
							trJ += 1
						else:
							break

					if botLeftDiagCount >= 4:
						return marker

		return None

class Game(object):

	def __init__(self, p1, p2):
		self.board = Board()
		self.p1 = p1
		self.p2 = p2
		self.lastMove = self.p2
		self.nextMove = self.p1
		self.winner = None

		self.p1.lastState = self.board.getState()
		self.p2.lastState = self.board.getState()

	#Tells the designated player to make a move
	def makeMove(self, player):
		#Print each turn only when a human is playing to reduce spam
		if not(isinstance(self.p1, Agent) and isinstance(self.p2, Agent)):
			self.printBoard()
		x, y = player.chooseMove(self.board.getState())
		self.board.place(player.marker, x, y)

		#Update whose turn it is
		self.nextMove = self.lastMove
		self.lastMove = player

		#Check if the game was won, tied, or can continue
		result = self.board.checkForWin()

		#If there is a winner, update value functions for any that were agents.
		if result == player.marker:
			self.gameOver(player.marker)
		elif result == 'Draw':
			self.gameOver('Draw')
		else:
			self.makeMove(self.nextMove)

	#Print out the board state.  If an agent is taking a turn, shows the value of making each possible move.
	def printBoard(self):
		st = self.board.getState()
		print("   ", end="")
		for i in range(15):
			if i < 10:
				print("  " + str(i) + "   ", end="")
			else:
				print("  " + str(i) + "  ", end="")
		print("")
		print("   -----------------------------------------------------------------------------------------")
		for i in range(15):
			print(str(i) + " ", end="")
			if i < 10:
				print(" ", end="")
			for j in range(15):
				print("| " + st[i][j] + " | ", end=""),
			print(" " + str(i), end="")
			print("")
		print("   -----------------------------------------------------------------------------------------")

	def gameOver(self, status):
		self.printBoard()
		if status is 'Draw':
			print('Draw!')
		else:
			print("Game over! The winner was " + status)
			if status is self.p1.marker:
				self.winner = self.p1
			else:
				self.winner = self.p2

	def start(self):
		self.makeMove(self.nextMove)

def findFeatures(state, p1Marker, p2Marker):

	p1OpenFour = 0
	p2OpenFour = 0

	p1HOpenFour = 0
	p2HOpenFour = 0

	p1BOpenFour = 0
	p2BOpenFour = 0

	p1BHOpenFour = 0
	p2BHOpenFour = 0

	p1OpenThree = 0
	p2OpenThree = 0

	p1HOpenThree = 0
	p2HOpenThree = 0

	p1BOpenThree = 0
	p2BOpenThree = 0

	p1BHOpenThree = 0
	p2BHOpenThree = 0

	for i in range(0, 15):
		for j in range(0, 15):
			if state[i][j] in MARKERS:

				#OPEN FOURS
				if i > 0 and i < 11:
					#Open Four to the bottom
					if state[i][j] == state[i+1][j] == state[i+2][j] == state[i+3][j] and state[i-1][j] not in MARKERS and state[i+4][j] not in MARKERS:
						if state[i][j] == p1Marker:
							p1OpenFour += 1
						else:
							p2OpenFour += 1
				if j < 11 and j > 0:
					#Open Four to the right
					if state[i][j] == state[i][j+1] == state[i][j+2] == state[i][j+3] and state[i][j-1] not in MARKERS and state[i][j+4] not in MARKERS:
						if state[i][j] == p1Marker:
							p1OpenFour += 1
						else:
							p2OpenFour += 1
					#Open Four to the upper right
					if i > 3 and i < 14:
						if state[i][j] == state[i-1][j+1] == state[i-2][j+2] == state[i-3][j+3] and state[i+1][j-1] not in MARKERS and state[i-4][j+4] not in MARKERS:
							if state[i][j] == p1Marker:
								p1OpenFour += 1
							else:
								p2OpenFour += 1
					#Open Four to the lower right
					if i < 11 and i > 0:
						if state[i][j] == state[i+1][j+1] == state[i+2][j+2] == state[i+3][j+3] and state[i-1][j-1] not in MARKERS and state[i+4][j+4] not in MARKERS:
							if state[i][j] == p1Marker:
								p1OpenFour += 1
							else:
								p2OpenFour += 1

				#BROKEN OPEN FOURS
				if i < 10 and i > 0:
					#Broken Open Four to the bottom
					if (state[i][j] == state[i+2][j] == state[i+3][j] == state[i+4][j] and state[i+1][j] not in MARKERS) or (state[i][j] == state[i+1][j] == state[i+3][j] == state[i+4][j] and state[i+2][j] not in MARKERS) or (state[i][j] == state[i+1][j] == state[i+2][j] == state[i+4][j] and state[i+3][j] not in MARKERS) and state[i-1][j] not in MARKERS and state[i+5][j] not in MARKERS:
						if state[i][j] == p1Marker:
							p1BOpenFour += 1
						else:
							p2BOpenFour += 1
				if j < 10:
					#Broken Open four to the right
					if (state[i][j] == state[i][j+2] == state[i][j+3] == state[i][j+4] and state[i][j+1] not in MARKERS) or (state[i][j] == state[i][j+1] == state[i][j+3] == state[i][j+4] and state[i][j+2] not in MARKERS) or (state[i][j] == state[i][j+1] == state[i][j+2] == state[i][j+4] and state[i][j+3] not in MARKERS) and state[i][j-1] not in MARKERS and state[i][j+5] not in MARKERS:
						if state[i][j] == p1Marker:
							p1BOpenFour += 1
						else:
							p2BOpenFour += 1
					#Broken Open four to the upper right
					if i > 4:
						if (state[i][j] == state[i-2][j+2] == state[i-3][j+3] == state[i-4][j+4] and state[i-1][j+1] not in MARKERS) or (state[i][j] == state[i-1][j+1] == state[i-3][j+3] == state[i-4][j+4] and state[i-2][j+2] not in MARKERS) or (state[i][j] == state[i-1][j+1] == state[i-2][j+2] == state[i-4][j+4] and state[i-3][j+3] not in MARKERS) and state[i+1][j-1] not in MARKERS and state[i-5][j+5] not in MARKERS:
							if state[i][j] == p1Marker:
								p1BOpenFour += 1
							else:
								p2BOpenFour += 1
					#Broken Open four to the lower right
					if i < 10:
						if (state[i][j] == state[i+2][j+2] == state[i+3][j+3] == state[i+4][j+4] and state[i+1][j+1] not in MARKERS) or (state[i][j] == state[i+1][j+1] == state[i+3][j+3] == state[i+4][j+4] and state[i+2][j+2] not in MARKERS) or (state[i][j] == state[i+1][j+1] == state[i+2][j+2] == state[i+4][j+4] and state[i+3][j+3] not in MARKERS) and state[i-1][j-1] not in MARKERS and state[i+5][j+5] not in MARKERS:
							if state[i][j] == p1Marker:
								p1BOpenFour += 1
							else:
								p2BOpenFour += 1

				#HALF OPEN FOURS
				if i < 12:
					#Half Open Four to the bottom
					if state[i][j] == state[i+1][j] == state[i+2][j] == state[i+3][j]:
						if i is 0:
							if state[i+4][j] not in MARKERS:
								if state[i][j] == p1Marker:
									p1HOpenFour += 1
								else:
									p2HOpenFour += 1
						if i is 11:
							if state[i-1][j] not in MARKERS:
								if state[i][j] == p1Marker:
									p1HOpenFour += 1
								else:
									p2HOpenFour += 1
						else:
							if (state[i-1][j] not in MARKERS and state[i+4][j] in MARKERS) or (state[i-1][j] in MARKERS and state[i+4][j] not in MARKERS):
								if state[i][j] == p1Marker:
									p1HOpenFour += 1
								else:
									p2HOpenFour += 1
				if j < 12:
					#Half Open Four to the right
					if state[i][j] == state[i][j+1] == state[i][j+2] == state[i][j+3]:
						if j is 0:
							if state[i][j+4] not in MARKERS:
								if state[i][j] == p1Marker:
									p1HOpenFour += 1
								else:
									p2HOpenFour += 1
						if j is 11:
							if state[i][j-1] not in MARKERS:
								if state[i][j] == p1Marker:
									p1HOpenFour += 1
								else:
									p2HOpenFour += 1
						else:
							if (state[i][j-1] not in MARKERS and state[i][j+4] in MARKERS) or (state[i][j-1] in MARKERS and state[i][j+4] not in MARKERS):
								if state[i][j] == p1Marker:
									p1HOpenFour += 1
								else:
									p2HOpenFour += 1
					if i > 2:
						#Half Open Four to the upper right
						if state[i][j] == state[i-1][j+1] == state[i-2][j+2] == state[i-3][j+3]:
							if j is 0:
								if i > 3:
									if state[i-4][j+4] not in MARKERS:
										if state[i][j] == p1Marker:
											p1HOpenFour += 1
										else:
											p2HOpenFour += 1
							elif j is 11:
								if i < 14:
									if state[i+1][j-1] not in MARKERS:
										if state[i][j] == p1Marker:
											p1HOpenFour += 1
										else:
											p2HOpenFour += 1
							elif i is 14:
								if j < 11:
									if state[i-4][j+4] not in MARKERS:
										if state[i][j] == p1Marker:
											p1HOpenFour += 1
										else:
											p2HOpenFour += 1
							elif i is 3:
								if j > 0:
									if state[i+1][j-1] not in MARKERS:
										if state[i][j] == p1Marker:
											p1HOpenFour += 1
										else:
											p2HOpenFour += 1

							else:
								if (state[i+1][j-1] not in MARKERS and state[i-4][j+4] in MARKERS) or (state[i+1][j-1] in MARKERS and state[i-4][j+4] not in MARKERS):
									if state[i][j] == p1Marker:
										p1HOpenFour += 1
									else:
										p2HOpenFour += 1
					if i < 12:
						#Half Open Four to the lower right
						if state[i][j] == state[i+1][j+1] == state[i+2][j+2] == state[i+3][j+3]:
							if j is 0:
								if i < 11:
									if state[i+4][j+4] not in MARKERS:
										if state[i][j] == p1Marker:
											p1HOpenFour += 1
										else:
											p2HOpenFour += 1
							elif j is 11:
								if i > 0:
									if state[i-1][j-1] not in MARKERS:
										if state[i][j] == p1Marker:
											p1HOpenFour += 1
										else:
											p2HOpenFour += 1
							elif i is 0:
								if j < 11:
									if state[i+4][j+4] not in MARKERS:
										if state[i][j] == p1Marker:
											p1HOpenFour += 1
										else:
											p2HOpenFour += 1
							elif i is 11:
								if j > 0:
									if state[i-1][j-1] not in MARKERS:
										if state[i][j] == p1Marker:
											p1HOpenFour += 1
										else:
											p2HOpenFour += 1

							else:
								if (state[i-1][j-1] not in MARKERS and state[i+4][j+4] in MARKERS) or (state[i-1][j-1] in MARKERS and state[i+4][j+4] not in MARKERS):
									if state[i][j] == p1Marker:
										p1HOpenFour += 1
									else:
										p2HOpenFour += 1

				#OPEN THREES
				if i > 0 and i < 12:
					#Open Three to the bottom
					if state[i][j] == state[i+1][j] == state[i+2][j] and state[i-1][j] not in MARKERS and state[i+3][j] not in MARKERS:
						if state[i][j] == p1Marker:
							p1OpenThree += 1
						else:
							p2OpenThree += 1
				if j < 12 and j > 0:
					#Open Three to the right
					if state[i][j] == state[i][j+1] == state[i][j+2] and state[i][j-1] not in MARKERS and state[i][j+3] not in MARKERS:
						if state[i][j] == p1Marker:
							p1OpenThree += 1
						else:
							p2OpenThree += 1
					#Open Three to the upper right
					if i > 2 and i < 14:
						if state[i][j] == state[i-1][j+1] == state[i-2][j+2] and state[i+1][j-1] not in MARKERS and state[i-3][j+3] not in MARKERS:
							if state[i][j] == p1Marker:
								p1OpenThree += 1
							else:
								p2OpenThree += 1
					#Open Three to the lower right
					if i < 12 and i > 0:
						if state[i][j] == state[i+1][j+1] == state[i+2][j+2] and state[i-1][j-1] not in MARKERS and state[i+3][j+3] not in MARKERS:
							if state[i][j] == p1Marker:
								p1OpenThree += 1
							else:
								p2OpenThree += 1

				#BROKEN OPEN THREES
				if i < 11 and i > 0:
					#Broken Open Three to the bottom
					if (state[i][j] == state[i+2][j] == state[i+3][j] and state[i+1][j] not in MARKERS) or (state[i][j] == state[i+1][j] == state[i+3][j] and state[i+2][j] not in MARKERS) and state[i-1][j] not in MARKERS and state[i+4][j] not in MARKERS:
						if state[i][j] == p1Marker:
							p1BOpenThree += 1
						else:
							p2BOpenThree += 1
				if j < 11 and j > 0:
					#Broken Open Three to the right
					if (state[i][j] == state[i][j+2] == state[i][j+3] and state[i][j+1] not in MARKERS) or (state[i][j] == state[i][j+1] == state[i][j+3] and state[i][j+2] not in MARKERS) and state[i][j-1] not in MARKERS and state[i][j+4] not in MARKERS:
						if state[i][j] == p1Marker:
							p1BOpenThree += 1
						else:
							p2BOpenThree += 1
					#Broken Open Three to the upper right
					if i > 3:
						if (state[i][j] == state[i-2][j+2] == state[i-3][j+3] and state[i-1][j+1] not in MARKERS) or (state[i][j] == state[i-1][j+1] == state[i-3][j+3] and state[i-2][j+2] not in MARKERS) and state[i+1][j-1] not in MARKERS and state[i-4][j+4] not in MARKERS:
							if state[i][j] == p1Marker:
								p1BOpenThree += 1
							else:
								p2BOpenThree += 1
					#Broken Open Three to the lower right
					if i < 11:
						if (state[i][j] == state[i+2][j+2] == state[i+3][j+3] and state[i+1][j+1] not in MARKERS) or (state[i][j] == state[i+1][j+1] == state[i+3][j+3] and state[i+2][j+2] not in MARKERS) and state[i-1][j-1] not in MARKERS and state[i+4][j+4] not in MARKERS:
							if state[i][j] == p1Marker:
								p1BOpenThree += 1
							else:
								p2BOpenThree += 1

				#HALF OPEN THREES
				if i < 13:
					#Half Open Three to the bottom
					if state[i][j] == state[i+1][j] == state[i+2][j]:
						if i is 0:
							if state[i+3][j] not in MARKERS:
								if state[i][j] == p1Marker:
									p1HOpenThree += 1
								else:
									p2HOpenThree += 1
						if i is 12:
							if state[i-1][j] not in MARKERS:
								if state[i][j] == p1Marker:
									p1HOpenThree += 1
								else:
									p2HOpenThree += 1
						else:
							if (state[i-1][j] not in MARKERS and state[i+3][j] in MARKERS) or (state[i-1][j] in MARKERS and state[i+3][j] not in MARKERS):
								if state[i][j] == p1Marker:
									p1HOpenThree += 1
								else:
									p2HOpenThree += 1
				if j < 13:
					#Half Open Three to the right
					if state[i][j] == state[i][j+1] == state[i][j+2]:
						if j is 0:
							if state[i][j+3] not in MARKERS:
								if state[i][j] == p1Marker:
									p1HOpenThree += 1
								else:
									p2HOpenThree += 1
						if j is 12:
							if state[i][j-1] not in MARKERS:
								if state[i][j] == p1Marker:
									p1HOpenThree += 1
								else:
									p2HOpenThree += 1
						else:
							if (state[i][j-1] not in MARKERS and state[i][j+3] in MARKERS) or (state[i][j-1] in MARKERS and state[i][j+3] not in MARKERS):
								if state[i][j] == p1Marker:
									p1HOpenThree += 1
								else:
									p2HOpenThree += 1
					if i > 1:
						#Half Open Three to the upper right
						if state[i][j] == state[i-1][j+1] == state[i-2][j+2]:
							if j is 0:
								if i > 2:
									if state[i-3][j+3] not in MARKERS:
										if state[i][j] == p1Marker:
											p1HOpenThree += 1
										else:
											p2HOpenThree += 1
							elif j is 12:
								if i < 14:
									if state[i+1][j-1] not in MARKERS:
										if state[i][j] == p1Marker:
											p1HOpenThree += 1
										else:
											p2HOpenThree += 1
							elif i is 14:
								if j < 12:
									if state[i-3][j+3] not in MARKERS:
										if state[i][j] == p1Marker:
											p1HOpenThree += 1
										else:
											p2HOpenThree += 1
							elif i is 2:
								if j > 0:
									if state[i+1][j-1] not in MARKERS:
										if state[i][j] == p1Marker:
											p1HOpenThree += 1
										else:
											p2HOpenThree += 1
							else:
								if (state[i+1][j-1] not in MARKERS and state[i-3][j+3] in MARKERS) or (state[i+1][j-1] in MARKERS and state[i-3][j+3] not in MARKERS):
									if state[i][j] == p1Marker:
										p1HOpenThree += 1
									else:
										p2HOpenThree += 1
					if i < 13:
						#Half Open Three to the lower right
						if state[i][j] == state[i+1][j+1] == state[i+2][j+2]:
							if j is 0:
								if i < 12:
									if state[i+3][j+3] not in MARKERS:
										if state[i][j] == p1Marker:
											p1HOpenThree += 1
										else:
											p2HOpenThree += 1
							elif j is 12:
								if i > 0:
									if state[i-1][j-1] not in MARKERS:
										if state[i][j] == p1Marker:
											p1HOpenThree += 1
										else:
											p2HOpenThree += 1
							elif i is 0:
								if j < 12:
									if state[i+3][j+3] not in MARKERS:
										if state[i][j] == p1Marker:
											p1HOpenThree += 1
										else:
											p2HOpenThree += 1
							elif i is 12:
								if j > 0:
									if state[i-1][j-1] not in MARKERS:
										if state[i][j] == p1Marker:
											p1HOpenThree += 1
										else:
											p2HOpenThree += 1
							else:
								if (state[i-1][j-1] not in MARKERS and state[i+3][j+3] in MARKERS) or (state[i-1][j-1] in MARKERS and state[i+3][j+3] not in MARKERS):
									if state[i][j] == p1Marker:
										p1HOpenThree += 1
									else:
										p2HOpenThree += 1

	dict = {}
	dict['p1OpenFour'] = p1OpenFour
	dict['p2OpenFour'] = p2OpenFour
	dict['p1HOpenFour'] = p1HOpenFour
	dict['p2HOpenFour'] = p2HOpenFour
	dict['p1BOpenFour'] = p1BOpenFour
	dict['p2BOpenFour'] = p2BOpenFour
	dict['p1OpenThree'] = p1OpenThree
	dict['p2OpenThree'] = p2OpenThree
	dict['p1HOpenThree'] = p1HOpenThree
	dict['p2HOpenThree'] = p2HOpenThree
	dict['p1BOpenThree'] = p1BOpenThree
	dict['p2BOpenThree'] = p2BOpenThree

	return dict

class Agent(object):

	#Alpha is the weight for backing up values, and epsilon is the chance of an exploratory move
	def __init__(self, marker, random=False):
		self.epsilon = 0.2
		self.alpha = 0.99
		self.marker = marker
		self.lastState = []
		self.random=random

	#Figure out how to approximate states
	def approximateStateValue(self, featureDict):
		#I made these up
		coeffsDict = {}
		coeffsDict['p1OpenFour'] = 5
		coeffsDict['p1BOpenFour'] = 1
		coeffsDict['p1HOpenFour'] = .8
		coeffsDict['p1OpenThree'] = 1
		coeffsDict['p1BOpenThree'] = .3
		coeffsDict['p1HOpenThree'] = .2
		coeffsDict['p2OpenFour'] = -100
		coeffsDict['p2BOpenFour'] = -3
		coeffsDict['p2HOpenFour'] = -1.5
		coeffsDict['p2OpenThree'] = -1
		coeffsDict['p2BOpenThree'] = -.5
		coeffsDict['p2HOpenThree'] = -.4

		sum = 0
		for key in coeffsDict:
			sum += coeffsDict[key] * featureDict[key]
		return sum

	#Reduce the value of epsilon and alpha over time; After 10,000 games, alpha is <0.02
	def updateVars(self):
		self.epsilon = self.epsilon * .9999
		self.alpha = self.alpha * .9999

	#Make a greedy move, aka, take the best action in the given scenario based on the value function
	def greedyMove(self, currentState):
		possibilities = {}

		for i in range(15):
			for j in range(15):
				if currentState[i][j] not in MARKERS:
					temp = copy.deepcopy(currentState)
					temp[i][j] = self.marker
					otherMarker = MARKERS[0]
					if self.marker is MARKERS[0]:
						otherMarker = MARKERS[1]
					featureDict = findFeatures(temp, self.marker, otherMarker)
					valueOfState = self.approximateStateValue(featureDict)
					info = {}
					info['value'] = valueOfState
					info['x'] = j
					info['y'] = i
					possibilities[str(temp)] = info
					

		# Look through all possible moves to find the one with the highest value.
		maxState = None
		maxValue = -10000

		keys = list(possibilities.keys())
		random.shuffle(keys)
		for key in keys:
			if possibilities[key]['value'] > maxValue:
				maxState = key
				maxValue = possibilities[key]['value']
			elif possibilities[key]['value'] == maxValue:
				choice = randint(0,1)
				if choice is 0:
					maxState = key
					maxValue = possibilities[key]['value']

		x = possibilities[maxState]['x']
		y = possibilities[maxState]['y']
		return x,y

	#Make a random, exploratory move
	def exploratoryMove(self, currentState):
		possibilities = []
		for i in range(15):
			for j in range(15):
				if currentState[i][j] not in MARKERS:
					move = (j, i)
					possibilities.append(move)

		choice = randint(0, len(possibilities) - 1)
		move = possibilities[choice]

		x = move[0]
		y = move[1]

		return x,y

	#Choose whether to make a greedy or exploratory move. Also, adjust alpha and epsilon.
	def chooseMove(self, currentState):
		rVal = randint(1,100)
		decrVal = float(rVal) / 100

		# if self.random:
		# 	x,y = self.exploratoryMove(currentState)
		# elif decrVal <= self.epsilon:
		# 	x,y = self.exploratoryMove(currentState)
		# else:
		x,y = self.greedyMove(currentState)

		return x,y

class Human(object):

	def __init__(self, marker):
		self.marker = marker

	#Humans input a move in the form of 0,1 where 0 is the row and 1 is the column
	def chooseMove(self,  currentState):
		move = input('Move: ')
		move = move.split(',')
		x = move[0]
		y = move[1]
		return int(x),int(y)

def main():
	while True:
		p1 = Human('X')
		p2 = Agent('O')
		game = Game(p1, p2)
		game.start()

main()