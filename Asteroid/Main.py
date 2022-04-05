# Import
from if3_game.engine import init, Layer
from Asteroid import Spaceship, RESOLUTION, Asteroid, AsteroidGame
from random import randint

# Variables 

init(RESOLUTION, "Asteroid") #initialiser la fenêtre ( dimension et titre)

game = AsteroidGame() #instancier/ créer un objet ( de nom "game") de type game

#game.debug = True



game.run() #appelle la méthode run de la fonction game. Lance le jeu.

