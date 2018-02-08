from __future__ import print_function
import sys
from flask import Flask
from flask import render_template, url_for, request, redirect
import os
from app.aux import Agent

app = Flask(__name__)

@app.route('/home', methods=['GET', 'POST'])
def home():
	player = Agent.Human('X')
	riAgent = Agent.Agent('O')
	game = Agent.Game(player, riAgent)

	if request.method == 'GET':
		return render_template(
			'home.html',
			board=""
		)
	elif request.method == 'POST':
		boardState = request.form['board']
		print(boardState)
		moves = boardState.split(";")
		for i in range(0, len(moves) - 2):
			move = moves[i].split(")")[0].split("(")[1].split(",")
			playerSymbol = moves[i].split(")")[1]
			x = int(move[0])
			y = int(move[1])
			game.board.place(playerSymbol, x, y)

		lastMove = boardState.split(";")[-2].split(")")[0].split("(")[1].split(",")
		x = int(lastMove[0])
		y = int(lastMove[1])
		status, moveX, moveY = game.makeMove(player, x, y)
		print(status)
		if status is not "False":
			return render_template(
				'home.html',
				board=boardState,
				outcome=status
		)
		#Agent make move, add to boardState
		status, moveX, moveY = game.makeMove(riAgent)
		boardState += "(" + str(moveX) + "," + str(moveY) + ")O;"
		print(status)
		print(str(moveX))
		if status is not "False":
			return render_template(
				'home.html',
				board=boardState,
				outcome=status
		)

		return render_template(
			'home.html',
			board=boardState,
			outcome="None"
		)


