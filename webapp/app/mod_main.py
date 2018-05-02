from __future__ import print_function
import sys
import os
import pickle
from flask import Flask
from flask import render_template, url_for, request, redirect
from app.aux import Agent
from app.aux import mcts_alphaZero
from app.aux.policy_value_net_keras import PolicyValueNet

app = Flask(__name__)

#Run this command before starting server:
#export THEANO_FLAGS='floatX=float32, mode=FAST_RUN'

@app.route('/home', methods=['GET', 'POST'])
def home():
	#If the page is loaded for the first time (not a move in the game), 
	#then end here, have agent move, and render the page
	if request.method == 'GET':
		player = Agent.Human('x')
		model_file = "current_policy_5000.model"
		model_file2 = "current_policy_10_10_v2_2400.model"
		best_policy = PolicyValueNet(15, 15, model_file = model_file)
		best_policy2 = PolicyValueNet(10, 10, pooling=False, model_file = model_file2)

		riAgent = mcts_alphaZero.MCTSPlayer('O', best_policy.policy_value_fn, c_puct=5, n_playout=400)  # set larger n_playout for better performance
		riAgent2 = mcts_alphaZero.MCTSPlayer('O', best_policy2.policy_value_fn, c_puct=5, n_playout=400)  # set larger n_playout for better performance

		game = Agent.Game(player, riAgent, 15)
		game2 = Agent.Game(player, riAgent2, 10)

		status, moveX, moveY = game.makeMove(riAgent, 0, 0)
		status2, moveX2, moveY2 = game2.makeMove(riAgent2, 0, 0)

		boardState = "(" + str(moveX) + "," + str(moveY) + ")O;"
		boardState2 = "(" + str(moveX) + "," + str(moveY) + ")O;"

		return render_template(
			'home.html',
			board=boardState,
			board2=boardState2
		)

	#Else, if a move is received:
	elif request.method == 'POST':

		#Initialize human player
		player = Agent.Human('X')
		#Receive the board state (where pieces are on the board), received during the page request
		boardLabel = request.form['boardLabel']
		board = request.form['board']
		board2 = request.form['board2']

		if boardLabel == "board":
			#File to load neural network agent from
			model_file = "current_policy_5000.model"
			best_policy = PolicyValueNet(15, 15, model_file = model_file)
			#Initialize the agent
			riAgent = mcts_alphaZero.MCTSPlayer('O', best_policy.policy_value_fn, c_puct=5, n_playout=400)  # set larger n_playout for better performance
			boardState = board
			#Create a game between the human and the agent
			game = Agent.Game(player, riAgent, 15)

		else:
			#File to load neural network agent from
			model_file = "current_policy_10_10_v2_2400.model"
			best_policy = PolicyValueNet(10, 10, pooling=False, model_file = model_file)
			#Initialize the agent
			riAgent = mcts_alphaZero.MCTSPlayer('O', best_policy.policy_value_fn, c_puct=5, n_playout=400)  # set larger n_playout for better performance
			boardState = board2
			#Create a game between the human and the agent
			game = Agent.Game(player, riAgent, 10)

		#Split the board into moves; parse them, and place them onto the board for the game created above
		moves = boardState.split(";")
		for i in range(0, len(moves) - 2):
			move = moves[i].split(")")[0].split("(")[1].split(",")
			playerSymbol = moves[i].split(")")[1]
			x = int(move[0])
			y = int(float(move[1]))
			game.board.place(playerSymbol, x, y)

		#Get the most recently made move (which is the move the player just submitted), then
		#place it and see if the game is over
		lastMove = boardState.split(";")[-2].split(")")[0].split("(")[1].split(",")
		x = int(lastMove[0])
		y = int(lastMove[1])
		status, moveX, moveY = game.makeMove(player, x, y)


		#If the game ended, end here and render with a 'you win' message
		if status is not "False":
			if boardLabel == "board":
				return render_template(
					'home.html',
					board=boardState,
					board2=board2,
					outcome=status
			)
			else:
				return render_template(
					'home.html',
					board=board,
					board2=boardState,
					outcome=status
			)

		#Agent make move, add to boardState
		if boardLabel == "board":
			status, moveX, moveY = game.makeMove(riAgent, x, y)
		else:
			status, moveX, moveY = game.makeMove(riAgent, x, y)
		boardState += "(" + str(moveX) + "," + str(moveY) + ")O;"

		#If the agent wins, end here and render with a 'you lose' message
		if status is not "False":
			if boardLabel == "board":
				return render_template(
					'home.html',
					board=boardState,
					board2=board2,
					outcome=status
			)
			else:
				return render_template(
					'home.html',
					board=board,
					board2=boardState,
					outcome=status
			)

		#Render the board state
		if boardLabel == "board":
			return render_template(
				'home.html',
				board=boardState,
				board2=board2,
				outcome=status
		)
		else:
			return render_template(
				'home.html',
				board=board,
				board2=boardState,
				outcome=status
		)

@app.route('/projdesc', methods=['GET'])
def projdesc():
	return render_template(
		'proj-desc.html'
	)

@app.route('/team', methods=['GET'])
def team():
	return render_template(
		'team.html'
	)
