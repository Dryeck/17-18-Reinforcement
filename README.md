# 17-18-Reinforcement
2017-18 Reinforcement Learning Senior Design Project

##How to play against the Agent

We have created a UI on a web page that one can run locally to play against the agent.  Two agents were trained using the AlphaZero algorithm, one for a 15x15 board and one for a 10x10.  The generated models were exported and are queried to make a move after each move made by the user.  Both are available for play on the webpage.  The 10x10 is stronger due to a decreased time needed to train it.

###Dependencies
Python3, Flask, Keras, numpy, Theano, Tensorflow

###Running
1. Set the flask entrypoint to mod_main.py by using `export FLASK_APP=mod_main.py`
2. Navigate to `webapp/app`
3. Start the server with `flask run`

##Team Members:

* Shruti Alavala 
* Jared Gruneiro
* Hannah Reed
* Mya Rios
* Parker Timmerman
* Michael Wynne
