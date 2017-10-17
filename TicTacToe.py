#Jared Gruneiro
#Senior Design
#Tic Tac Toe Reinforcement Learning 
#October 10, 2017

MARKERS = ['X', 'O']

from random import randint
import copy
import ast
from math import floor
import time

class Board(object):

	def __init__(self):
		self.state = []
		self.newBoard()

	#Clear Board
	def newBoard(self):
		self.state = []
		for i in range(3):
			row = ['', '', '']
			self.state.append(row)

	#Return the state of the board as an array of arrays
	def getState(self):
		return self.state

	#Aux function to make the check winner function cleaner
	def getNicknames(self):
		nicknames = {
			"topLeft": self.state[0][0],
			"topMid": self.state[0][1],
			"topRight": self.state[0][2],
			"midLeft": self.state[1][0],
			"midMid": self.state[1][1],
			"midRight": self.state[1][2],
			"botLeft": self.state[2][0],
			"botMid": self.state[2][1],
			"botRight": self.state[2][2],
		}
		return nicknames

	#Place a marker on the board (make a move)
	def place(self, marker, x, y):
		if marker in MARKERS and self.state[y][x] not in MARKERS:
			self.state[y][x] = marker

	# Returns winner's marker if there is a winner, None if the game can
	# continue, and 'Draw' if it is a tie.
	def checkForWin(self):
		nn = self.getNicknames()

		topLeft = nn['topLeft']
		topMid = nn['topMid']
		topRight = nn['topRight']
		midLeft = nn['midLeft']
		midMid = nn['midMid']
		midRight = nn['midRight']
		botLeft = nn['botLeft']
		botMid = nn['botMid']
		botRight = nn['botRight']

		if topLeft in MARKERS:
			if (topLeft == topMid == topRight) or (topLeft == midMid == botRight) or (topLeft == midLeft == botLeft):
				return topLeft
		if topMid in MARKERS:
			if (topMid == midMid == botMid):
				return topMid
		if topRight in MARKERS:
			if (topRight == midRight == botRight):
				return topRight
		if midLeft in MARKERS:
			if (midLeft == midMid == midRight):
				return midLeft
		if midMid in MARKERS:
			if (midMid == topRight == botLeft):
				return midMid
		if botLeft in MARKERS:
			if (botLeft == botMid == botRight):
				return botLeft
		for key, value in nn.items():
			if value not in MARKERS:
				return None
		return 'Draw'

class Game(object):

	def __init__(self, p1, p2):
		self.board = Board()
		self.p1 = p1
		self.p2 = p2
		self.lastMove, self.nextMove = self.chooseFirst(self.p1, self.p2)
		self.winner = None

		self.p1.lastState = self.board.getState()
		self.p2.lastState = self.board.getState()

	def chooseFirst(self, p1, p2):
		random = randint(0,1)
		if random is 0:
			return p1, p2
		return p2, p1

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
		vals = []

		if isinstance(self.nextMove, Agent):
			for i in range(3):
				for j in range(3):
					if st[i][j] is '':
						temp = copy.deepcopy(st)
						temp[i][j] = self.nextMove.marker
						if str(temp) in self.nextMove.stateValues:
							vals.append(round(self.nextMove.stateValues[str(temp)], 2))
						else:
							vals.append('')
					else:
						vals.append(st[i][j])
		else:
			for i in range(3):
				for j in range(3):
						vals.append(st[i][j])

		valsPretty = []
		for item in vals:
			if item is '':
				valsPretty.append("      ")
			elif type(item) is float:
				valsPretty.append(" " + str(item) + "  ")
			else:
				valsPretty.append("  " + item + "   ")

		print("---------------------------")
		print("| " + valsPretty[0] + " | " +
			  valsPretty[1] + " | " + valsPretty[2] + " |")
		print("| " + str(valsPretty[3]) + " | " +
			  valsPretty[4] + " | " + valsPretty[5] + " |")
		print("| " + str(valsPretty[6]) + " | " +
			  valsPretty[7] + " | " + valsPretty[8] + " |")
		print("---------------------------")

	def gameOver(self, status):
		if not(isinstance(self.p1, Agent) and isinstance(self.p2, Agent)):
			self.printBoard()
			if status is 'Draw':
				print('Draw!')
			else:
				print("Game over! The winner was " + status)


		if status is self.p1.marker:
			self.winner = self.p1
		elif status is self.p2.marker:
			self.winner = self.p2

	def start(self):
		self.makeMove(self.nextMove)

class Agent(object):

	#Alpha is the weight for backing up values, and epsilon is the chance of an exploratory move
	def __init__(self, marker, random=False):
		self.stateValues = {}
		self.epsilon = 0.1
		self.alpha = 0.99
		self.marker = marker
		self.lastState = []
		self.random=random

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

		for i in range(3):
			for j in range(3):
				if currentState[i][j] not in MARKERS:
					possibleState = copy.deepcopy(currentState)
					possibleState[i][j] = self.marker
					if str(possibleState) in self.stateValues:
						possibilities[str(possibleState)] = self.stateValues[str(possibleState)]
					else:
						self.stateValues[str(possibleState)] = 0.5
						possibilities[str(possibleState)] = 0.5

		# Look through all possible moves to find the one with the highest value.
		maxState = None
		maxValue = -10

		for key, value in possibilities.items():
			if value > maxValue:
				maxState = key
				maxValue = value
			elif value == maxValue:
				choice = randint(0,1)
				if choice is 0:
					maxState = key
					maxValue = value

		# Figure out where to place the marker to get to that state. (Could optimize this step out later)
		x = y = 0
		maxState = ast.literal_eval(maxState)
		for i in range(3):
			for j in range(3):
				if currentState[i][j] != maxState[i][j]:
					x = j
					y = i

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
		for i in range(3):
			for j in range(3):
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

		if self.random:
			x,y = self.exploratoryMove(currentState)
		elif decrVal <= self.epsilon:
			x,y = self.exploratoryMove(currentState)
		else:
			x,y = self.greedyMove(currentState)

		self.updateVars()
		return x,y

class Human(object):

	def __init__(self, marker):
		self.marker = marker

	#Humans input a move in the form of 0,1 where 0 is the row and 1 is the column
	def chooseMove(self, state):
		move = input('Move: ')
		x = move[0]
		y = move[1]
		return x,y

def main():
	p1 = Agent(MARKERS[0])
	p2 = Agent(MARKERS[1])
	r2 = Agent(MARKERS[1], True)

	currentp1Wins = 0
	currentDraws = 0
	p1Wins = []
	p1States = []
	draws = []
	keepTrackStep = 1000
	roundNum = 0
	totalRounds = 5000
	percent = totalRounds / 100
	printCount = -1
	estTime = 0
	lastTime = time.time()

	while roundNum < totalRounds:
		if roundNum % percent is 0:
			printCount += 1
			if printCount is 5:
				curTime = time.time()
				estTime = curTime - lastTime
				lastTime = curTime
				multFactor = (totalRounds - roundNum) / (percent * 5)
				estRemaining = estTime * multFactor
				print(str(floor(roundNum / percent)) + "% done. " + "Time remaining: ~" + str(floor(estRemaining * 100) / 100) + " seconds")
				printCount = 0
		game = Game(p1, r2)
		game.start()
		if game.winner is p1:
			currentp1Wins += 1
		elif game.winner is None:
			currentDraws += 1
		roundNum += 1
		if roundNum % keepTrackStep is 0:
			p1Wins.append(currentp1Wins)
			p1States.append(str(len(p1.stateValues)))
			draws.append(currentDraws)
			currentDraws = 0
			currentp1Wins = 0
	for i in range(totalRounds / keepTrackStep):
		print("In games " + str(i * keepTrackStep) + "-" + str((i+1) * keepTrackStep) + ", p1 won " + str(p1Wins[i]) + " games, which is " + str(float(p1Wins[i]) / keepTrackStep) + "%")
		print("There were " + str(draws[i]) + " draws.")
		print("Total number of states seen: " + str(p1States[i]))
	p2 = Human(MARKERS[1])

	while True:
		game = Game(p1, p2)
		game.start()

main()