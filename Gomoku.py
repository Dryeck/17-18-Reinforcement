#Jared Gruneiro
#Senior Design
#Tic Tac Toe Reinforcement Learning 
#October 10, 2017

MARKERS = ['X', 'O']

from random import randint
import copy
import ast

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
			if isinstance(player, Agent):
				player.stateValues[str(self.board.getState())] = 1
			if isinstance(self.nextMove, Agent):
				self.nextMove.stateValues[str(self.nextMove.lastState)] = -1
			self.gameOver(player.marker)
		elif result == 'Draw':
			self.gameOver('Draw')
		else:
			self.makeMove(self.nextMove)

	#Print out the board state.  If an agent is taking a turn, shows the value of making each possible move.
	def printBoard(self):
		st = self.board.getState()

		print("-------------------------------------------------------------------------------------------------------")
		for i in range(15):
			for j in range(15):
				print("| " + st[i][j] + " | "),
			print("")
		print("-------------------------------------------------------------------------------------------------------")

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

class Agent(object):

	#Alpha is the weight for backing up values, and epsilon is the chance of an exploratory move
	def __init__(self, marker, random=False):
		self.stateValues = {}
		self.epsilon = 0.2
		self.alpha = 0.99
		self.marker = marker
		self.lastState = []
		self.random=random

	#Figure out how to approximate states
	def approximateState(state):
		return None
		#TODO
		#return approximatedState

	#Reduce the value of epsilon and alpha over time; After 10,000 games, alpha is <0.02
	def updateVars(self):
		self.epsilon = self.epsilon * .9999
		self.alpha = self.alpha * .9999

	#Make a greedy move, aka, take the best action in the given scenario based on the value function
	def greedyMove(self, currentState):
		possibilities = {}

		# For each open spot on the game board, consider moving there.  Get the value associated with each possible proposed
		# state from self.stateValues, and add that state/value to possibilities.  If it is not in self.stateValues, add it
		# with a value of 0.5.

		for i in range(15):
			for j in range(15):
				if currentState[i][j] not in MARKERS:
					possibleState = copy.deepcopy(currentState)
					possibleState[i][j] = self.marker
					possibleState = approximateState(possibleState)
					info = {}
					info['x'] = i
					info['y'] = j
					if str(possibleState) in self.stateValues:
						info['value'] = self.stateValues(str(possibleState['value']))
						possibilities[str(possibleState)] = info
					else:
						info['value'] = 0.5
						self.stateValues[str(possibleState)] = 0.5
						possibilities[str(possibleState)] = info

		# Look through all possible moves to find the one with the highest value.
		maxState = None
		maxValue = -10

		for key, value in possibilities.items():
			if value['value'] > maxValue:
				maxState = key
				maxValue = value['value']
			elif value['value'] == maxValue:
				choice = randint(0,1)
				if choice is 0:
					maxState = key
					maxValue = value['value']

		# Figure out where to place the marker to get to that state. (Could optimize this step out later)
		x = maxState['info']['x']
		y = maxState['info']['y']

		# Backup the value of the next state to the current state based on the alpha value.
		if str(currentState) in self.stateValues:
			self.stateValues[str(currentState)] += self.alpha * (self.stateValues[str(maxState)] - self.stateValues[str(currentState)])
		else:
			self.stateValues[str(currentState)] = 0.5

		# Return the coordinates of the optimal move to make.
		self.lastState = maxState
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

		temp = copy.deepcopy(currentState)
		temp[y][x] = self.marker
		self.lastState = temp

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
		# 	x,y = self.greedyMove(currentState)
		x,y = self.exploratoryMove(currentState)

		self.updateVars()
		return x,y

class Human(object):

	def __init__(self, marker):
		self.marker = marker

	#Humans input a move in the form of 0,1 where 0 is the row and 1 is the column
	def chooseMove(self,  currentState):
		move = input('Move: ')
		x = move[0]
		y = move[1]
		return x,y

def main():
	while True:
		p1 = Human('X')
		p2 = Agent('O')
		game = Game(p1, p2)
		game.start()

main()