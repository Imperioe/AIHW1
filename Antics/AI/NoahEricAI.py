# -*- coding: latin-1 -*-
import random
import sys

sys.path.append("..")  # so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *


##
# @authors Eric Imperio and Noah Sperling
#
# Dr. Nuxoll's Booger class used as a starting point and for reference
#
# AIPlayer
# Description: The responsibility of this class is to interact with the game by
# deciding a valid move based on a given game state. This class has methods that
# will be implemented by students in Dr. Nuxoll's AI course.
#
# Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):
    # __init__
    # Description: Creates a new Player
    #
    # Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer, self).__init__(inputPlayerId, "NoahEricAi")
        # the coordinates of the agent's food and tunnel will be stored in these
        # variables (see getMove() below)
        self.myFood = None
        self.myTunnel = None


    ##
    # getPlacement
    #
    # The agent places the hill and tunnel for maximum access to food.
    # Grass is placed to slow enemy movement onto the AI's side.
    # Enemy food is placed as far away from the enemy tunnel and hill as possible
    #
    #Parameters
    #    self - current class object
    #    currentState - the current game state
    #
    #Return
    #    returns an array of tuples
    #
    ##
    def getPlacement(self, currentState):
        self.myFood = None
        self.myTunnel = None
        if currentState.phase == SETUP_PHASE_1:
            return [(2, 1), (7, 1), #anthill, tunnel
                    #grass
                    (0, 3), (1, 3), (2, 3), (3, 3),
                    (4, 3), (5, 3), (6, 3),
                    (7, 3), (8, 3)]
        elif currentState.phase == SETUP_PHASE_2:
            #food placement
            #numToPlace = 2
            moves = []
            #for i in range(0, numToPlace):
            move = None

            #spots on the board
            sequence = [(0,6),(9,6),(1,6),(8,6),(2,6),(7,6),(3,6),(6,6),(4,6),(5,6),
                        (0,7),(9,7),(1,7),(8,7),(2,7),(7,7),(3,7),(6,7),(4,7),(5,7),
                        (0,8),(9,8),(1,8),(8,8),(2,8),(7,8),(3,8),(6,8),(4,8),(5,8),
                        (0,9),(9,9),(1,9),(8,9),(2,9),(7,9),(3,9),(6,9),(4,9),(5,9)
                        ]

            #finds valid locations
            sequence1 = [s for s in sequence if currentState.board[s[0]][s[1]].constr == None]

            anthillcoords = (0,0)
            tunnelcoords = (0,0)
            for x in range(0,10):
                for y in range(6,10):
                    if currentState.board[x][y].constr != None:
                        if currentState.board[x][y].constr.type == ANTHILL:
                            anthillcoords = (x,y)
                        if currentState.board[x][y].constr.type == TUNNEL:
                            tunnelcoords = (x,y)


            farthest = 0
            farthestCoords = (0,0)
            for s in sequence1:
                toAntHill = abs(approxDist(s, anthillcoords))
                toTunnel = abs(approxDist(s, tunnelcoords))
                if toAntHill >= toTunnel:
                    if(toTunnel >= farthest):
                        farthest = toTunnel
                        farthestCoords = s
                else:
                    if(toAntHill >= farthest):
                        farthest = toAntHill
                        farthestCoords = s

            moves.append(farthestCoords)

            sequence2 = [s for s in sequence1 if s[0] != farthestCoords[0] and s[1] != farthestCoords[1]]

            farthest = 0
            farthestCoords = (0,0)
            for s in sequence2:
                toAntHill = abs(approxDist(s,anthillcoords))
                toTunnel = abs(approxDist(s, tunnelcoords))
                if toAntHill >= toTunnel:
                    if(toTunnel > farthest):
                        farthest = toTunnel
                        farthestCoords = s
                else:
                    if(toAntHill > farthest):
                        farthest = toAntHill
                        farthestCoords = s

            moves.append(farthestCoords)
            return moves
        else:
            return None  # should never happen


    ##
    # getMove
    #
    #Parameters:
    #    self - the AI class
    #    currentState - the current game state
    #
    #Return:
    #    a Move Object
    #
    # This agent gathers food and sends drones at the enemy hill
    #
    ##
    def getMove(self, currentState):
        myInv = getCurrPlayerInventory(currentState)
        me = currentState.whoseTurn
        self.hill = None
        self.foods = None

        # stores coordinates of tunnel, hill, foods and whether they are close to the tunnel or the anthill
        if (self.myTunnel == None):
            self.myTunnel = getConstrList(currentState, me, (TUNNEL,))[0]
        if (self.hill == None):
            self.hill = getConstrList(currentState, me, (ANTHILL,))[0]
        if (self.foods == None):
            self.foods = getConstrList(currentState, None, (FOOD,))
            self.food1 = self.foods[0]
            self.food2 = self.foods[1]

        numAnts = len(myInv.ants)
        numFood = myInv.foodCount
        if not getAntList(currentState, me, (WORKER,)): # no worker
            if numFood > 0:
                #Build Worker
                if (getAntAt(currentState, myInv.getAnthill().coords) is None):
                    return Move(BUILD, [myInv.getAnthill().coords], WORKER)
                else:
                    return Move(END, None, None)
        elif not len(getAntList(currentState, me, (WORKER,))) == 2:
            if (getAntAt(currentState, myInv.getAnthill().coords) is None):
                if numFood > 0:
                    return Move(BUILD, [myInv.getAnthill().coords], WORKER)

        # if the worker has already moved, we're done
        myWorker = None
        if getAntList(currentState, me, (WORKER,)):
            myWorker = getAntList(currentState, me, (WORKER,))[0]
        else:
            return Move(END, None, None)

        myQueen = myInv.getQueen()
        if (myQueen.coords == myInv.getAnthill().coords):
            return Move(MOVE_ANT, [myQueen.coords, (myQueen.coords[0], myQueen.coords[1]-1)], None)

        # if the hasn't moved, have her move in place so she will attack
        if (not myQueen.hasMoved):
            return Move(MOVE_ANT, [myQueen.coords], None)

        # if I have the foos and the anthill is unoccupied then
        # make a drone
        if (myInv.foodCount > 2 and len(getAntList(currentState, me, (DRONE,))) == 0):
            if (getAntAt(currentState, myInv.getAnthill().coords) is None):
                return Move(BUILD, [myInv.getAnthill().coords], DRONE)

        enemyAnthill = None
        # Move all my drones towards the enemy
        if currentState.inventories[PLAYER_TWO].ants == myInv.ants:
            for c in currentState.inventories[PLAYER_ONE].constrs:
                if c.type == ANTHILL:
                    enemyAnthill = c.coords
        else:
            for c in currentState.inventories[PLAYER_TWO].constrs:
                if c.type == ANTHILL:
                    enemyAnthill = c.coords

        myDrones = getAntList(currentState, me, (DRONE,))
        for d in myDrones:
            if not (d.hasMoved):
                if not d.coords == enemyAnthill:
                    path = createPathToward(currentState, d.coords,
                                            enemyAnthill, UNIT_STATS[DRONE][MOVEMENT])
                    return Move(MOVE_ANT, path, None)

        # New move method
        self.headingToFood1 = 0
        myWorkers = getAntList(currentState, me, (WORKER,))
        for w in myWorkers:
            if not (w.hasMoved):
                if not (w.carrying):
                        if (stepsToReach(currentState, self.food1.coords, w.coords) < stepsToReach(currentState,
                                                                                                   self.food2.coords,
                                                                                                   w.coords) and self.headingToFood1 == 0):
                            self.headingToFood1 = 1
                            path = createPathToward(currentState, w.coords,
                                                    self.food1.coords, UNIT_STATS[WORKER][MOVEMENT])
                            if not path == [w.coords]:
                              return Move(MOVE_ANT, path, None)
                            else:
                                path = createOtherPath(currentState, w.coords,
                                                      self.food1.coords, UNIT_STATS[WORKER][MOVEMENT])
                                return Move(MOVE_ANT, path, None)
                        else:
                            path = createPathToward(currentState, w.coords,
                                                    self.food2.coords, UNIT_STATS[WORKER][MOVEMENT])
                            if not path == [w.coords]:
                                return Move(MOVE_ANT, path, None)
                            else:
                                path = createOtherPath(currentState, w.coords,
                                                      self.food2.coords, UNIT_STATS[WORKER][MOVEMENT])
                                return Move(MOVE_ANT, path, None)

                else:
                    if (stepsToReach(currentState, self.myTunnel.coords, w.coords) < stepsToReach(
                            currentState,
                            self.hill.coords,
                            w.coords)):
                        path = createPathToward(currentState, w.coords,
                                                self.myTunnel.coords, UNIT_STATS[WORKER][MOVEMENT])
                        if not path == [w.coords]:
                            return Move(MOVE_ANT, path, None)
                        else:
                            path = createOtherPath(currentState, w.coords,
                                                   self.myTunnel.coords, UNIT_STATS[WORKER][MOVEMENT])
                            return Move(MOVE_ANT, path, None)
                    else:
                        path = createPathToward(currentState, w.coords,
                                                self.hill.coords, UNIT_STATS[WORKER][MOVEMENT])
                        if not path == [w.coords]:
                            return Move(MOVE_ANT, path, None)  # if the queen is on the anthill move her
                        else:
                            path = createOtherPath(currentState, w.coords,
                                                   self.hill.coords, UNIT_STATS[WORKER][MOVEMENT])
                            return Move(MOVE_ANT, path, None)

        return Move(END, None, None)


    ##
    # getAttack
    #
    #Parameters
    #    self - the current class object
    #    currentState - the current GameState
    #    attackingAnt - the ant that is attacking another ant
    #    enemyLocations - an array of enemy locations
    #
    #Return
    #    returns the first passed in enemy location to attack
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        return enemyLocations[0]  # don't care


    ##
    # registerWin
    #
    # This agent doesn't learn good
    #
    def registerWin(self, hasWon):
        # method templaste, not implemented
        pass

    ##
    # createOtherPath
    #
    # creates a legal path Away from the destination.
    # Does not make sure the queen wont move out of her zone
    #
    #Parameters
    #   currentState - currentState of the game
    #   sourceCoords - starting position (an x,y coord)
    #   targetCoords - destination position (an x,y coord)
    #   movement     - movement points to spend
    #
    # Return
    #   returns a path they moves away from the destination
    #
    def createOtherPath(currentState, sourceCoords, targetCoords, movement):
        distToTarget = approxDist(sourceCoords, targetCoords)
        path = [sourceCoords]
        curr = sourceCoords

        # keep adding steps to the path until movement runs out
        step = 0
        while (movement > 0):
            found = False  # was a new step found to add to the path
            for coord in listReachableAdjacent(currentState, sourceCoords, movement):
                # is this a step headed in the right direction?
                # only true change from Nuxolls createPathToward method
                if (approxDist(coord, targetCoords) >= distToTarget):

                    # how much movement does it cost to get there?
                    constr = getConstrAt(currentState, coord)
                    moveCost = 1  # default cost
                    if (constr != None):
                        moveCost = CONSTR_STATS[constr.type][MOVE_COST]
                    # if I have enough movement left then add it to the path
                    if (moveCost <= movement):
                        # add the step to the path
                        found = True
                        path.append(coord)

                        # restart the search from the new coordinate
                        movement = movement - moveCost
                        sourceCoords = coord
                        distToTarget = approxDist(sourceCoords, targetCoords)
                        break
            if (not found): break  # no usable steps found

        return path