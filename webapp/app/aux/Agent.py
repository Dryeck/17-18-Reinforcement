#Jared Gruneiro
#Senior Design
#Tic Tac Toe Reinforcement Learning 
#October 10, 2017

MARKERS = ['X', 'O']

from random import randint
import copy
import ast
import random
import numpy as np

class Board(object):

	def __init__(self):
		self.dim = 15
		self.state = []
		self.newBoard()
		self.inARow = 5

	# For testing, shouldn't be used, prefer to use the printBoard method in the Game class
	def printBoard(self):
		print("-------------------------------------------------------------------------------------------------------")
		for i in range(0, self.dim):
			for j in range(0, self.dim):
				print("| " + self.state[i][j] + " | "),
			print("")
		print("-------------------------------------------------------------------------------------------------------")

	#Clear Board
	def newBoard(self):
		self.state = []
		for i in range(0, self.dim):
			row = []
			for j in range(0, self.dim):
				row.append(' ')
			self.state.append(row)

	#Return the state of the board as an array of arrays
	def getState(self):
		return self.state

	#Place a marker on the board (make a move)
	def place(self, marker, x, y):
		x = (int)(x)
		y = (int)(y)
		if marker in MARKERS and self.state[y][x] not in MARKERS:
			self.state[y][x] = marker

	# Returns winner's marker if there is a winner, and None if the game can continue.  The function
	# looks at each spot on the board, and if its not null, checks in all surrounding directions
	# to see if it is part of a 5 (or more) in a row.
	def checkForWin(self):
		for i in range(self.dim):
			for j in range(self.dim):
				if self.state[i][j] in MARKERS:
					marker = self.state[i][j]
					horzCount = 1
					vertCount = 1
					topLeftDiagCount = 1
					botLeftDiagCount = 1
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
					while bot < self.dim:
						if self.state[bot][j] is marker:
							vertCount += 1
							bot += 1
						else:
							break

					if vertCount >= self.inARow:
						return marker

					#Check horizontal
					while left > -1:
						if self.state[i][left] is marker:
							horzCount += 1
							left -= 1
						else:
							break
					while right < self.dim:
						if self.state[i][right] is marker:
							horzCount += 1
							right += 1
						else:
							break

					if horzCount >= self.inARow:
						return marker

					#Check diagonal (top left to bottom right)
					while tlI > 0 and tlJ > 0:
						if self.state[tlI][tlJ] is marker:
							topLeftDiagCount += 1
							tlI -= 1
							tlJ -= 1
						else:
							break
					while brI < self.dim and brJ < self.dim:
						if self.state[brI][brJ] is marker:
							topLeftDiagCount += 1
							brI += 1
							brJ += 1
						else:
							break

					if topLeftDiagCount >= self.inARow:
						return marker

					#Check diagonal (bottom left to top right)
					while blI < self.dim and blJ > 0:
						if self.state[blI][blJ] is marker:
							botLeftDiagCount += 1
							blI += 1
							blJ -= 1
						else:
							break
					while trI > 0 and trJ < self.dim:
						if self.state[trI][trJ] is marker:
							botLeftDiagCount += 1
							trI -= 1
							trJ += 1
						else:
							break

					if botLeftDiagCount >= self.inARow:
						return marker

		return None

#alphaBoard is the format that the board needs to be in to be processed by the NN agent
class alphaBoard(object):
    """board for the game"""

    def __init__(self, **kwargs):
        self.width = int(kwargs.get('width', 15))
        self.height = int(kwargs.get('height', 15))
        # board states stored as a dict,
        # key: move as location on the board,
        # value: player as pieces type
        self.states = {}
        # need how many pieces in a row to win
        self.n_in_row = int(kwargs.get('n_in_row', 5))
        self.players = [1, 2]  # player1 and player2

    def init_board(self, start_player=0):
        if self.width < self.n_in_row or self.height < self.n_in_row:
            raise Exception('board width and height can not be '
                            'less than {}'.format(self.n_in_row))
        self.current_player = self.players[start_player]  # start player
        # keep available moves in a list
        self.availables = list(range(self.width * self.height))
        self.states = {}
        self.last_move = -1

    def move_to_location(self, move):
        """
        3*3 board's moves like:
        6 7 8
        3 4 5
        0 1 2
        and move 5's location is (1,2)
        """
        h = move // self.width
        w = move % self.width
        return [h, w]

    def location_to_move(self, location):
        if(len(location) != 2):
            return -1
        h = location[0]
        w = location[1]
        move = h * self.width + w
        if(move not in range(self.width * self.height)):
            return -1
        return move

    def current_state(self):
        """return the board state from the perspective of the current player.
        state shape: 4*width*height
        """

        square_state = np.zeros((4, self.width, self.height))
        if self.states:
            moves, players = np.array(list(zip(*self.states.items())))
            move_curr = moves[players == self.current_player]
            move_oppo = moves[players != self.current_player]
            square_state[0][move_curr // self.width,
                            move_curr % self.height] = 1.0
            square_state[1][move_oppo // self.width,
                            move_oppo % self.height] = 1.0
            # indicate the last move location
            square_state[2][self.last_move // self.width,
                            self.last_move % self.height] = 1.0
        if len(self.states) % 2 == 0:
            square_state[3][:, :] = 1.0  # indicate the colour to play
        return square_state[:, ::-1, :]

    def do_move(self, move):
        self.states[move] = self.current_player
        self.availables.remove(move)
        self.current_player = (
            self.players[0] if self.current_player == self.players[1]
            else self.players[1]
        )
        self.last_move = move

    def has_a_winner(self):
        width = self.width
        height = self.height
        states = self.states
        n = self.n_in_row

        moved = list(set(range(width * height)) - set(self.availables))
        if(len(moved) < self.n_in_row + 2):
            return False, -1

        for m in moved:
            h = m // width
            w = m % width
            player = states[m]

            if (w in range(width - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n))) == 1):
                return True, player

            if (h in range(height - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n * width, width))) == 1):
                return True, player

            if (w in range(width - n + 1) and h in range(height - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n * (width + 1), width + 1))) == 1):
                return True, player

            if (w in range(n - 1, width) and h in range(height - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n * (width - 1), width - 1))) == 1):
                return True, player

        return False, -1

    def game_end(self):
        """Check whether the game is ended or not"""
        win, winner = self.has_a_winner()
        if win:
            return True, winner
        elif not len(self.availables):
            return True, -1
        return False, -1

    def get_current_player(self):
        return self.current_player

#Take the board given and turn it into an alphaBoard to be processed by the NN agent
def convertBoard(oldBoard, lastX, lastY):
	newBoard = alphaBoard(width=oldBoard.dim, height=oldBoard.dim, n_in_row=oldBoard.inARow)
	newBoard.init_board(1)
	lastLocation = (oldBoard.dim - 1 - lastY) * oldBoard.dim + lastX
	newBoard.last_move = lastLocation
	# print(str(newBoard.availables))
	#Convert X's and O's on the board to 1's and 2's
	for i in range(oldBoard.dim - 1, -1, -1):
		for j in range(0, oldBoard.dim):
			location = (oldBoard.dim - i - 1) * oldBoard.dim + j
			if oldBoard.state[i][j] is 'X':
				newBoard.states[location] = 1
				newBoard.availables.remove(location)
			elif oldBoard.state[i][j] is 'O':
				newBoard.states[location] = 2
				newBoard.availables.remove(location)
	return newBoard

class Game(object):

	def __init__(self, p1, p2):
		self.board = Board()
		self.p1 = p1
		self.p2 = p2
		self.lastMove = self.p2
		self.nextMove = self.p1
		self.winner = None

	#Tells the designated player to make a move
	def makeMove(self, player, lastX=None, lastY=None):
		x, y = -1, -1
		if isinstance(player, Human):
			self.board.place(player.marker, lastX, lastY)
		else:
			alphaB = convertBoard(self.board, lastX, lastY)
			location = player.chooseMove(alphaB)
			x = location % self.board.dim
			y = (int)(self.board.dim - 1 - ((location - x) / self.board.dim))
			print("placing at " + str(x) + " and " + str(y))
			self.board.place(player.marker, x, y)

		#Update whose turn it is
		self.nextMove = self.lastMove
		self.lastMove = player

		#Check if the game was won, tied, or can continue
		self.printBoard()
		result = self.board.checkForWin()

		#If there is a winner, update value functions for any that were agents.
		if result == player.marker:
			return self.gameOver(player.marker, x, y)
		elif result == 'Draw':
			return self.gameOver('Draw', x, y)
		else:
			return "False", x, y

	#Print out the board state.  If an agent is taking a turn, shows the value of making each possible move.
	def printBoard(self):
		st = self.board.getState()
		print("   ", end="")
		for i in range(self.board.dim):
			if i < 10:
				print("  " + str(i) + "   ", end="")
			else:
				print("  " + str(i) + "  ", end="")
		print("")
		print("   -----------------------------------------------------------------------------------------")
		for i in range(self.board.dim):
			print(str(i) + " ", end="")
			if i < 10:
				print(" ", end="")
			for j in range(self.board.dim):
				print("| " + st[i][j] + " | ", end=""),
			print(" " + str(i), end="")
			print("")
		print("   -----------------------------------------------------------------------------------------")

	def gameOver(self, status, x, y):
		self.printBoard()
		if status is 'Draw':
			print('Draw!')
			return "Draw", x, y
		else:
			print("Game over! The winner was " + status)
			if status is self.p1.marker:
				self.winner = self.p1
				return "Win", x, y
			else:
				self.winner = self.p2
				print("returning")
				return "Loss", x, y

	def start(self):
		self.makeMove(self.nextMove)

# def findFeatures(state, p1Marker, p2Marker):

# 	p1Five = 0
# 	p2Five = 0

# 	p1OpenFour = 0
# 	p2OpenFour = 0

# 	p1HOpenFour = 0
# 	p2HOpenFour = 0

# 	p1BOpenFour = 0
# 	p2BOpenFour = 0

# 	p1BHOpenFour = 0
# 	p2BHOpenFour = 0

# 	p1OpenThree = 0
# 	p2OpenThree = 0

# 	p1HOpenThree = 0
# 	p2HOpenThree = 0

# 	p1BOpenThree = 0
# 	p2BOpenThree = 0

# 	p1BHOpenThree = 0
# 	p2BHOpenThree = 0

# 	p1OpenTwo = 0
# 	p2OpenTwo = 0

# 	for i in range(0, 15):
# 		for j in range(0, 15):
# 			if state[i][j] in MARKERS:

# 				#FIVES
# 				#Five to the bottom
# 				if i < 11:
# 					if state[i][j] == state[i+1][j] == state[i+2][j] == state[i+3][j] == state[i+4][j]:
# 						if state[i][j] == p1Marker:
# 							p1Five +=1
# 						else:
# 							p2Five +=1
# 				#Five to the right
# 				if j < 11:
# 					if state[i][j] == state[i][j+1] == state[i][j+2] == state[i][j+3] == state[i][j+4]:
# 						if state[i][j] == p1Marker:
# 							p1Five +=1
# 						else:
# 							p2Five +=1
# 				#Five to the upper right
# 				if i > 3 and j < 11:
# 					if state[i][j] == state[i-1][j+1] == state[i-2][j+2] == state[i-3][j+3] == state[i-4][j+4]:
# 						if state[i][j] == p1Marker:
# 							p1Five +=1
# 						else:
# 							p2Five +=1
# 				#Five to the lower right
# 				if i < 11 and j < 11:
# 					if state[i][j] == state[i+1][j+1] == state[i+2][j+2] == state[i+3][j+3] == state[i+4][j+4]:
# 						if state[i][j] == p1Marker:
# 							p1Five +=1
# 						else:
# 							p2Five +=1
# 				#OPEN FOURS
# 				if i > 0 and i < 11:
# 					#Open Four to the bottom
# 					if state[i][j] == state[i+1][j] == state[i+2][j] == state[i+3][j] and state[i-1][j] not in MARKERS and state[i+4][j] not in MARKERS:
# 						if state[i][j] == p1Marker:
# 							p1OpenFour += 1
# 						else:
# 							p2OpenFour += 1
# 				if j < 11 and j > 0:
# 					#Open Four to the right
# 					if state[i][j] == state[i][j+1] == state[i][j+2] == state[i][j+3] and state[i][j-1] not in MARKERS and state[i][j+4] not in MARKERS:
# 						if state[i][j] == p1Marker:
# 							p1OpenFour += 1
# 						else:
# 							p2OpenFour += 1
# 					#Open Four to the upper right
# 					if i > 3 and i < 14:
# 						if state[i][j] == state[i-1][j+1] == state[i-2][j+2] == state[i-3][j+3] and state[i+1][j-1] not in MARKERS and state[i-4][j+4] not in MARKERS:
# 							if state[i][j] == p1Marker:
# 								p1OpenFour += 1
# 							else:
# 								p2OpenFour += 1
# 					#Open Four to the lower right
# 					if i < 11 and i > 0:
# 						if state[i][j] == state[i+1][j+1] == state[i+2][j+2] == state[i+3][j+3] and state[i-1][j-1] not in MARKERS and state[i+4][j+4] not in MARKERS:
# 							if state[i][j] == p1Marker:
# 								p1OpenFour += 1
# 							else:
# 								p2OpenFour += 1

# 				#BROKEN OPEN FOURS
# 				if i < 10 and i > 0:
# 					#Broken Open Four to the bottom
# 					if (state[i][j] == state[i+2][j] == state[i+3][j] == state[i+4][j] and state[i+1][j] not in MARKERS) or (state[i][j] == state[i+1][j] == state[i+3][j] == state[i+4][j] and state[i+2][j] not in MARKERS) or (state[i][j] == state[i+1][j] == state[i+2][j] == state[i+4][j] and state[i+3][j] not in MARKERS) and state[i-1][j] not in MARKERS and state[i+5][j] not in MARKERS:
# 						if state[i][j] == p1Marker:
# 							p1BOpenFour += 1
# 						else:
# 							p2BOpenFour += 1
# 				if j < 10:
# 					#Broken Open four to the right
# 					if (state[i][j] == state[i][j+2] == state[i][j+3] == state[i][j+4] and state[i][j+1] not in MARKERS) or (state[i][j] == state[i][j+1] == state[i][j+3] == state[i][j+4] and state[i][j+2] not in MARKERS) or (state[i][j] == state[i][j+1] == state[i][j+2] == state[i][j+4] and state[i][j+3] not in MARKERS) and state[i][j-1] not in MARKERS and state[i][j+5] not in MARKERS:
# 						if state[i][j] == p1Marker:
# 							p1BOpenFour += 1
# 						else:
# 							p2BOpenFour += 1
# 					#Broken Open four to the upper right
# 					if i > 4 and i < 14:
# 						if (state[i][j] == state[i-2][j+2] == state[i-3][j+3] == state[i-4][j+4] and state[i-1][j+1] not in MARKERS) or (state[i][j] == state[i-1][j+1] == state[i-3][j+3] == state[i-4][j+4] and state[i-2][j+2] not in MARKERS) or (state[i][j] == state[i-1][j+1] == state[i-2][j+2] == state[i-4][j+4] and state[i-3][j+3] not in MARKERS) and state[i+1][j-1] not in MARKERS and state[i-5][j+5] not in MARKERS:
# 							if state[i][j] == p1Marker:
# 								p1BOpenFour += 1
# 							else:
# 								p2BOpenFour += 1
# 					#Broken Open four to the lower right
# 					if i < 10 and i > 0:
# 						if (state[i][j] == state[i+2][j+2] == state[i+3][j+3] == state[i+4][j+4] and state[i+1][j+1] not in MARKERS) or (state[i][j] == state[i+1][j+1] == state[i+3][j+3] == state[i+4][j+4] and state[i+2][j+2] not in MARKERS) or (state[i][j] == state[i+1][j+1] == state[i+2][j+2] == state[i+4][j+4] and state[i+3][j+3] not in MARKERS) and state[i-1][j-1] not in MARKERS and state[i+5][j+5] not in MARKERS:
# 							if state[i][j] == p1Marker:
# 								p1BOpenFour += 1
# 							else:
# 								p2BOpenFour += 1

# 				#HALF OPEN FOURS
# 				if i < 12:
# 					#Half Open Four to the bottom
# 					if state[i][j] == state[i+1][j] == state[i+2][j] == state[i+3][j]:
# 						if i is 0:
# 							if state[i+4][j] not in MARKERS:
# 								if state[i][j] == p1Marker:
# 									p1HOpenFour += 1
# 								else:
# 									p2HOpenFour += 1
# 						if i is 11:
# 							if state[i-1][j] not in MARKERS:
# 								if state[i][j] == p1Marker:
# 									p1HOpenFour += 1
# 								else:
# 									p2HOpenFour += 1
# 						else:
# 							if (state[i-1][j] not in MARKERS and state[i+4][j] in MARKERS) or (state[i-1][j] in MARKERS and state[i+4][j] not in MARKERS):
# 								if state[i][j] == p1Marker:
# 									p1HOpenFour += 1
# 								else:
# 									p2HOpenFour += 1
# 				if j < 12:
# 					#Half Open Four to the right
# 					if state[i][j] == state[i][j+1] == state[i][j+2] == state[i][j+3]:
# 						if j is 0:
# 							if state[i][j+4] not in MARKERS:
# 								if state[i][j] == p1Marker:
# 									p1HOpenFour += 1
# 								else:
# 									p2HOpenFour += 1
# 						if j is 11:
# 							if state[i][j-1] not in MARKERS:
# 								if state[i][j] == p1Marker:
# 									p1HOpenFour += 1
# 								else:
# 									p2HOpenFour += 1
# 						else:
# 							if (state[i][j-1] not in MARKERS and state[i][j+4] in MARKERS) or (state[i][j-1] in MARKERS and state[i][j+4] not in MARKERS):
# 								if state[i][j] == p1Marker:
# 									p1HOpenFour += 1
# 								else:
# 									p2HOpenFour += 1
# 					if i > 2:
# 						#Half Open Four to the upper right
# 						if state[i][j] == state[i-1][j+1] == state[i-2][j+2] == state[i-3][j+3]:
# 							if j is 0:
# 								if i > 3:
# 									if state[i-4][j+4] not in MARKERS:
# 										if state[i][j] == p1Marker:
# 											p1HOpenFour += 1
# 										else:
# 											p2HOpenFour += 1
# 							elif j is 11:
# 								if i < 14:
# 									if state[i+1][j-1] not in MARKERS:
# 										if state[i][j] == p1Marker:
# 											p1HOpenFour += 1
# 										else:
# 											p2HOpenFour += 1
# 							elif i is 14:
# 								if j < 11:
# 									if state[i-4][j+4] not in MARKERS:
# 										if state[i][j] == p1Marker:
# 											p1HOpenFour += 1
# 										else:
# 											p2HOpenFour += 1
# 							elif i is 3:
# 								if j > 0:
# 									if state[i+1][j-1] not in MARKERS:
# 										if state[i][j] == p1Marker:
# 											p1HOpenFour += 1
# 										else:
# 											p2HOpenFour += 1

# 							else:
# 								if (state[i+1][j-1] not in MARKERS and state[i-4][j+4] in MARKERS) or (state[i+1][j-1] in MARKERS and state[i-4][j+4] not in MARKERS):
# 									if state[i][j] == p1Marker:
# 										p1HOpenFour += 1
# 									else:
# 										p2HOpenFour += 1
# 					if i < 12:
# 						#Half Open Four to the lower right
# 						if state[i][j] == state[i+1][j+1] == state[i+2][j+2] == state[i+3][j+3]:
# 							if j is 0:
# 								if i < 11:
# 									if state[i+4][j+4] not in MARKERS:
# 										if state[i][j] == p1Marker:
# 											p1HOpenFour += 1
# 										else:
# 											p2HOpenFour += 1
# 							elif j is 11:
# 								if i > 0:
# 									if state[i-1][j-1] not in MARKERS:
# 										if state[i][j] == p1Marker:
# 											p1HOpenFour += 1
# 										else:
# 											p2HOpenFour += 1
# 							elif i is 0:
# 								if j < 11:
# 									if state[i+4][j+4] not in MARKERS:
# 										if state[i][j] == p1Marker:
# 											p1HOpenFour += 1
# 										else:
# 											p2HOpenFour += 1
# 							elif i is 11:
# 								if j > 0:
# 									if state[i-1][j-1] not in MARKERS:
# 										if state[i][j] == p1Marker:
# 											p1HOpenFour += 1
# 										else:
# 											p2HOpenFour += 1

# 							else:
# 								if (state[i-1][j-1] not in MARKERS and state[i+4][j+4] in MARKERS) or (state[i-1][j-1] in MARKERS and state[i+4][j+4] not in MARKERS):
# 									if state[i][j] == p1Marker:
# 										p1HOpenFour += 1
# 									else:
# 										p2HOpenFour += 1

# 				#OPEN THREES
# 				if i > 0 and i < 12:
# 					#Open Three to the bottom
# 					if state[i][j] == state[i+1][j] == state[i+2][j] and state[i-1][j] not in MARKERS and state[i+3][j] not in MARKERS:
# 						if state[i][j] == p1Marker:
# 							p1OpenThree += 1
# 						else:
# 							p2OpenThree += 1
# 				if j < 12 and j > 0:
# 					#Open Three to the right
# 					if state[i][j] == state[i][j+1] == state[i][j+2] and state[i][j-1] not in MARKERS and state[i][j+3] not in MARKERS:
# 						if state[i][j] == p1Marker:
# 							p1OpenThree += 1
# 						else:
# 							p2OpenThree += 1
# 					#Open Three to the upper right
# 					if i > 2 and i < 14:
# 						if state[i][j] == state[i-1][j+1] == state[i-2][j+2] and state[i+1][j-1] not in MARKERS and state[i-3][j+3] not in MARKERS:
# 							if state[i][j] == p1Marker:
# 								p1OpenThree += 1
# 							else:
# 								p2OpenThree += 1
# 					#Open Three to the lower right
# 					if i < 12 and i > 0:
# 						if state[i][j] == state[i+1][j+1] == state[i+2][j+2] and state[i-1][j-1] not in MARKERS and state[i+3][j+3] not in MARKERS:
# 							if state[i][j] == p1Marker:
# 								p1OpenThree += 1
# 							else:
# 								p2OpenThree += 1

# 				#BROKEN OPEN THREES
# 				if i < 11 and i > 0:
# 					#Broken Open Three to the bottom
# 					if (state[i][j] == state[i+2][j] == state[i+3][j] and state[i+1][j] not in MARKERS) or (state[i][j] == state[i+1][j] == state[i+3][j] and state[i+2][j] not in MARKERS) and state[i-1][j] not in MARKERS and state[i+4][j] not in MARKERS:
# 						if state[i][j] == p1Marker:
# 							p1BOpenThree += 1
# 						else:
# 							p2BOpenThree += 1
# 				if j < 11 and j > 0:
# 					#Broken Open Three to the right
# 					if (state[i][j] == state[i][j+2] == state[i][j+3] and state[i][j+1] not in MARKERS) or (state[i][j] == state[i][j+1] == state[i][j+3] and state[i][j+2] not in MARKERS) and state[i][j-1] not in MARKERS and state[i][j+4] not in MARKERS:
# 						if state[i][j] == p1Marker:
# 							p1BOpenThree += 1
# 						else:
# 							p2BOpenThree += 1
# 					#Broken Open Three to the upper right
# 					if i > 3 and i < 14:
# 						if (state[i][j] == state[i-2][j+2] == state[i-3][j+3] and state[i-1][j+1] not in MARKERS) or (state[i][j] == state[i-1][j+1] == state[i-3][j+3] and state[i-2][j+2] not in MARKERS) and state[i+1][j-1] not in MARKERS and state[i-4][j+4] not in MARKERS:
# 							if state[i][j] == p1Marker:
# 								p1BOpenThree += 1
# 							else:
# 								p2BOpenThree += 1
# 					#Broken Open Three to the lower right
# 					if i < 11 and i > 0:
# 						if (state[i][j] == state[i+2][j+2] == state[i+3][j+3] and state[i+1][j+1] not in MARKERS) or (state[i][j] == state[i+1][j+1] == state[i+3][j+3] and state[i+2][j+2] not in MARKERS) and state[i-1][j-1] not in MARKERS and state[i+4][j+4] not in MARKERS:
# 							if state[i][j] == p1Marker:
# 								p1BOpenThree += 1
# 							else:
# 								p2BOpenThree += 1

# 				#HALF OPEN THREES
# 				if i < 13:
# 					#Half Open Three to the bottom
# 					if state[i][j] == state[i+1][j] == state[i+2][j]:
# 						if i is 0:
# 							if state[i+3][j] not in MARKERS:
# 								if state[i][j] == p1Marker:
# 									p1HOpenThree += 1
# 								else:
# 									p2HOpenThree += 1
# 						if i is 12:
# 							if state[i-1][j] not in MARKERS:
# 								if state[i][j] == p1Marker:
# 									p1HOpenThree += 1
# 								else:
# 									p2HOpenThree += 1
# 						else:
# 							if (state[i-1][j] not in MARKERS and state[i+3][j] in MARKERS) or (state[i-1][j] in MARKERS and state[i+3][j] not in MARKERS):
# 								if state[i][j] == p1Marker:
# 									p1HOpenThree += 1
# 								else:
# 									p2HOpenThree += 1
# 				if j < 13:
# 					#Half Open Three to the right
# 					if state[i][j] == state[i][j+1] == state[i][j+2]:
# 						if j is 0:
# 							if state[i][j+3] not in MARKERS:
# 								if state[i][j] == p1Marker:
# 									p1HOpenThree += 1
# 								else:
# 									p2HOpenThree += 1
# 						if j is 12:
# 							if state[i][j-1] not in MARKERS:
# 								if state[i][j] == p1Marker:
# 									p1HOpenThree += 1
# 								else:
# 									p2HOpenThree += 1
# 						else:
# 							if (state[i][j-1] not in MARKERS and state[i][j+3] in MARKERS) or (state[i][j-1] in MARKERS and state[i][j+3] not in MARKERS):
# 								if state[i][j] == p1Marker:
# 									p1HOpenThree += 1
# 								else:
# 									p2HOpenThree += 1
# 					if i > 1:
# 						#Half Open Three to the upper right
# 						if state[i][j] == state[i-1][j+1] == state[i-2][j+2]:
# 							if j is 0:
# 								if i > 2:
# 									if state[i-3][j+3] not in MARKERS:
# 										if state[i][j] == p1Marker:
# 											p1HOpenThree += 1
# 										else:
# 											p2HOpenThree += 1
# 							elif j is 12:
# 								if i < 14:
# 									if state[i+1][j-1] not in MARKERS:
# 										if state[i][j] == p1Marker:
# 											p1HOpenThree += 1
# 										else:
# 											p2HOpenThree += 1
# 							elif i is 14:
# 								if j < 12:
# 									if state[i-3][j+3] not in MARKERS:
# 										if state[i][j] == p1Marker:
# 											p1HOpenThree += 1
# 										else:
# 											p2HOpenThree += 1
# 							elif i is 2:
# 								if j > 0:
# 									if state[i+1][j-1] not in MARKERS:
# 										if state[i][j] == p1Marker:
# 											p1HOpenThree += 1
# 										else:
# 											p2HOpenThree += 1
# 							else:
# 								if (state[i+1][j-1] not in MARKERS and state[i-3][j+3] in MARKERS) or (state[i+1][j-1] in MARKERS and state[i-3][j+3] not in MARKERS):
# 									if state[i][j] == p1Marker:
# 										p1HOpenThree += 1
# 									else:
# 										p2HOpenThree += 1
# 					if i < 13:
# 						#Half Open Three to the lower right
# 						if state[i][j] == state[i+1][j+1] == state[i+2][j+2]:
# 							if j is 0:
# 								if i < 12:
# 									if state[i+3][j+3] not in MARKERS:
# 										if state[i][j] == p1Marker:
# 											p1HOpenThree += 1
# 										else:
# 											p2HOpenThree += 1
# 							elif j is 12:
# 								if i > 0:
# 									if state[i-1][j-1] not in MARKERS:
# 										if state[i][j] == p1Marker:
# 											p1HOpenThree += 1
# 										else:
# 											p2HOpenThree += 1
# 							elif i is 0:
# 								if j < 12:
# 									if state[i+3][j+3] not in MARKERS:
# 										if state[i][j] == p1Marker:
# 											p1HOpenThree += 1
# 										else:
# 											p2HOpenThree += 1
# 							elif i is 12:
# 								if j > 0:
# 									if state[i-1][j-1] not in MARKERS:
# 										if state[i][j] == p1Marker:
# 											p1HOpenThree += 1
# 										else:
# 											p2HOpenThree += 1
# 							else:
# 								if (state[i-1][j-1] not in MARKERS and state[i+3][j+3] in MARKERS) or (state[i-1][j-1] in MARKERS and state[i+3][j+3] not in MARKERS):
# 									if state[i][j] == p1Marker:
# 										p1HOpenThree += 1
# 									else:
# 										p2HOpenThree += 1
# 				#OPEN TWOS
# 				#Open Two to the bottom
# 				if i > 0 and i < 13:
# 					if state[i][j] is state[i+1][j] and state[i-1][j] not in MARKERS and state[i+2][j] not in MARKERS:
# 						if state[i][j] is p1Marker:
# 							p1OpenTwo += 1
# 						else:
# 							p2OpenTwo += 1
# 					#Open Two to the lower right
# 					if j > 0 and j < 13:
# 						if state[i][j] is state[i+1][j+1] and state[i-1][j-1] not in MARKERS and state[i+2][j+2] not in MARKERS:
# 							if state[i][j] is p1Marker:
# 								p1OpenTwo += 1
# 							else:
# 								p2OpenTwo += 1
# 				#Open Two to the right
# 				if j > 0 and j < 13:
# 					if state[i][j] is state[i][j+1] and state[i][j-1] not in MARKERS and state[i][j+2] not in MARKERS:
# 						if state[i][j] is p1Marker:
# 							p1OpenTwo += 1
# 						else:
# 							p2OpenTwo += 1
# 					#Open Two to the upper right
# 					if i > 1 and i < 14:
# 						if state[i][j] is state[i-1][j+1] and state[i+1][j+1] not in MARKERS and state[i-2][j+2] not in MARKERS:
# 							if state[i][j] is p1Marker:
# 								p1OpenTwo += 1
# 							else:
# 								p2OpenTwo += 1

# 	dict = {}
# 	dict['p1Five'] = p1Five
# 	dict['p2Five'] = p2Five
# 	dict['p1OpenFour'] = p1OpenFour
# 	dict['p2OpenFour'] = p2OpenFour
# 	dict['p1HOpenFour'] = p1HOpenFour
# 	dict['p2HOpenFour'] = p2HOpenFour
# 	dict['p1BOpenFour'] = p1BOpenFour
# 	dict['p2BOpenFour'] = p2BOpenFour
# 	dict['p1OpenThree'] = p1OpenThree
# 	dict['p2OpenThree'] = p2OpenThree
# 	dict['p1HOpenThree'] = p1HOpenThree
# 	dict['p2HOpenThree'] = p2HOpenThree
# 	dict['p1BOpenThree'] = p1BOpenThree
# 	dict['p2BOpenThree'] = p2BOpenThree
# 	dict['p1OpenTwo'] = p1OpenTwo
# 	dict['p2OpenTwo'] = p2OpenTwo

# 	return dict

class Agent(object):

	#Alpha is the weight for backing up values, and epsilon is the chance of an exploratory move
	def __init__(self, marker, random=False):
		self.epsilon = 0.2
		self.alpha = 0.99
		self.marker = marker
		self.lastState = []
		self.random=random
		self.lastFeatures = {}
		self.lastValue = 0
		self.coeffsDict = {}

		self.initCoeffs()

	def initCoeffs(self):
		#I made these up
		self.coeffsDict['p1Five'] = 1000
		self.coeffsDict['p2Five'] = -100
		self.coeffsDict['p1OpenFour'] = 2
		self.coeffsDict['p1BOpenFour'] = 1
		self.coeffsDict['p1HOpenFour'] = .8
		self.coeffsDict['p1OpenThree'] = 1
		self.coeffsDict['p1BOpenThree'] = .3
		self.coeffsDict['p1HOpenThree'] = .2
		self.coeffsDict['p1OpenTwo'] = .05
		self.coeffsDict['p2OpenFour'] = -100
		self.coeffsDict['p2BOpenFour'] = -3
		self.coeffsDict['p2HOpenFour'] = -1.5
		self.coeffsDict['p2OpenThree'] = -3
		self.coeffsDict['p2BOpenThree'] = -.5
		self.coeffsDict['p2HOpenThree'] = -.4
		self.coeffsDict['p2OpenTwo'] = -.07

	#Take a state, and determine a value for it based on feature presence and coefficients.
	def approximateStateValue(self, featureDict):
		sum = 0
		for key in self.coeffsDict:
			sum += self.coeffsDict[key] * featureDict[key]
		return sum

	def updateWeights(self, currentState):
		otherMarker = MARKERS[0]
		if self.marker is MARKERS[0]:
			otherMarker = MARKERS[1]

		#Get the current board features
		features = findFeatures(currentState, self.marker, otherMarker)
		#Set featureDiff to contain the change in the quantity of each feature since the last turn
		featureDiff = {}
		for key in features:
			featureDiff[key] = self.lastFeatures[key] - features[key]

		#Set diffStateVal to the change in state value since the last turn
		currentStateVal = self.approximateStateValue(features)
		diffStateVal = self.lastValue - currentStateVal

		print("value of last state was " + str(self.lastValue))
		print("value of current state is " + str(currentStateVal))

		#If the state improved, don't update weights, because we assume the weights were good to begin with
		if diffStateVal <= 0:
			return 0

		#print("state got worse; updating weights")

		#Never change a weight by more than this percentage of its last value
		maxWeightChangePercent = 0.1

		for key in self.lastFeatures:
			if self.lastFeatures[key] > 0:
				print("updating weight for " + str(key))
				#Randomly choose whether to increase or decrease a weight, since we don't know if it was over or undervalued
				direction = random.choice([-1,1])
				#Weight the amount of the change based on how greatly the value changed in proportion to its previous value
				tempStateVal = currentStateVal
				if abs(currentStateVal) < 1:
					tempStateVal = 1
				changeFactor = diffStateVal / tempStateVal * self.lastFeatures[key]
				if abs(changeFactor) > maxWeightChangePercent:
					changeFactor = maxWeightChangePercent
				#Update the weight
				print("change amount is: " + str(changeFactor))
				print("previous weight for " + str(key) + ": " + str(self.coeffsDict[key]))
				if direction is 1:
					changeFactor = changeFactor * (10/9)
				self.coeffsDict[key] += self.coeffsDict[key] * changeFactor * direction * self.alpha
				print("new weight for " + str(key) + ": " + str(self.coeffsDict[key]))

	def printWeights(self):
		for key in self.coeffsDict:
			print("weight of " + str(key) + " is " + str(self.coeffsDict[key]))

	#Reduce the value of epsilon and alpha over time; After 10,000 games, alpha is <0.02
	def updateVars(self):
		self.epsilon = self.epsilon * .9999
		self.alpha = self.alpha * .9999

	def locationBias(self, moveX, moveY):
		middleX = 7
		middleY = 7
		bias = .08
		diffX = abs(moveX - middleX)
		diffY = abs(moveY - middleY)
		
		bias -= (diffX + diffY) * .005

		rand = random.randint(-4, 4) / 100
		bias += rand

		return bias


	#Make a greedy move, aka, take the best action in the given scenario based on the value function
	def greedyMove(self, currentState, board):
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
					valueOfState = self.approximateStateValue(featureDict) + self.locationBias(i, j)
					info = {}
					info['value'] = valueOfState
					info['x'] = j
					info['y'] = i
					info['features'] = featureDict
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

		try:
			x = possibilities[maxState]['x']
			y = possibilities[maxState]['y']
		except KeyError:
 			return -1,-1
		self.lastValue = possibilities[maxState]['value']

		self.lastFeatures = possibilities[maxState]['features']

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
	def chooseMove(self, currentState, board):
		rVal = randint(1,100)
		decrVal = float(rVal) / 100

		# if self.random:
		# 	x,y = self.exploratoryMove(currentState)
		# elif decrVal <= self.epsilon:
		# 	x,y = self.exploratoryMove(currentState)
		# else:
		x,y = self.greedyMove(currentState, board)
		self.updateVars()

		return x,y

class Human(object):

	def __init__(self, marker):
		self.marker = marker

	#Humans input a move in the form of 0,1 where 0 is the row and 1 is the column
	def chooseMove(self, currentState, board):
		move = input('Move: ')
		move = move.split(',')
		x = move[0]
		y = move[1]
		return int(x),int(y)
