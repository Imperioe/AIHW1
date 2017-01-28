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
    # The agent uses a hardcoded arrangement for phase 1 to provide maximum
    # protection to the queen.  Enemy food is placed randomly.
    #
    def getPlacement(self, currentState):
        self.myFood = None
        self.myTunnel = None
        if currentState.phase == SETUP_PHASE_1:
            return [(2, 1), (7, 1), #anthill/ tunnel
                    #grass
                    (0, 3), (1, 3), (2, 3), (3, 3), \
                    (4, 3), (5, 3), (6, 3), \
                    (7, 3), (8, 3)];
        elif currentState.phase == SETUP_PHASE_2:
            #numToPlace = 2
            moves = []
            #for i in range(0, numToPlace):
            move = None

            sequence = [(0,6),(9,6),(1,6),(8,6),(2,6),(7,6),(3,6),(6,6),(4,6),(5,6),
                        (0,7),(9,7),(1,7),(8,7),(2,7),(7,7),(3,7),(6,7),(4,7),(5,7),
                        (0,8),(9,8),(1,8),(8,8),(2,8),(7,8),(3,8),(6,8),(4,8),(5,8),
                        (0,9),(9,9),(1,9),(8,9),(2,9),(7,9),(3,9),(6,9),(4,9),(5,9)
                        ]

            sequence1 = [s for s in sequence if currentState.board[s[0]][s[1]].constr == None]
            print(sequence1)
            anthillcoords = (0,0)
            tunnelcoords = (0,0)
            for x in range(0,10):
                for y in range(6,10):
                    if currentState.board[x][y].constr != None:
                        if currentState.board[x][y].constr.type == ANTHILL:
                            anthillcoords = (x,y)
                        if currentState.board[x][y].constr.type == TUNNEL:
                            tunnelcoords = (x,y)

            print(anthillcoords)
            print(tunnelcoords)

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
            print(farthestCoords)

            sequence2 = [s for s in sequence1 if s[0] != farthestCoords[0] and s[1] != farthestCoords[1]]
            print(sequence2)

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
            print(farthestCoords)

                #count = 0
                #for index in sequence:
                #    if count == 2:
                #        break
                #    if currentState.board[index[0]][index[1]].constr == None:
                #        count+=1
                #        move = (index[0], index[1])
                #        moves.append(move)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                #        currentState.board[index[0]][index[1]].constr == True
                #moves.append(move)
            return moves
        else:
            return None  # should never happen

    ##
    # getMove
    #
    # This agent simply gathers food as fast as it can with its worker.  It
    # never attacks and never builds more ants.  The queen is never moved.
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
            # finds closest food to tunnel
            #for f in self.foods:
               ## distToTunnel = stepsToReach(currentState, self.myTunnel.coords, f.coords)
                #distToHill = stepsToReach(currentState, self.hill.coords, f.coords)
                #if (distToHill < distToTunnel):
                    #if (self.foodHill1 == None):
                        #self.foodHill1 = f
                    #else:
                        #self.foodHill2 = f
                #else:
                    #if (self.foodTunnel1 == None):
                        #self.foodTunnel1 = f
                    #else:
                        #self.foodTunnel2 = f


        self.headingToFood1 = 0
        myWorkers = getAntList(currentState, me, (WORKER,))
        for w in myWorkers:
            if not (w.hasMoved):
                if not (w.carrying):
                    if (stepsToReach(currentState, self.food1.coords, w.coords) < stepsToReach(currentState, self.food2.coords, w.coords) and headingToFood1 == 0):
                        self.headingToFood1 = 1
                        path = createPathToward(currentState, w.coords,
                                    self.food1.coords, UNIT_STATS[WORKER][MOVEMENT])
                        return Move(MOVE_ANT, path, None)
                    else:
                        path = createPathToward(currentState, w.coords,
                            self.food2.coords, UNIT_STATS[WORKER][MOVEMENT])
                        return Move(MOVE_ANT, path, None)
                else:
                    if (stepsToReach(currentState, self.tunnel, w.coords) < stepsToReach(currentState, self.anthill, w.coords)):
                        path = createPathToward(currentState, w.coords,
                            self.tunnel.coords, UNIT_STATS[WORKER][MOVEMENT])
                        return Move(MOVE_ANT, path, None)
                    else:
                        path = createPathToward(currentState, w.coords,
                           self.anthill.coords, UNIT_STATS[WORKER][MOVEMENT])
                        return Move(MOVE_ANT, path, None)  # if the queen is on the anthill move her

        myQueen = myInv.getQueen()
        if (myQueen.coords == myInv.getAnthill().coords):
            return Move(MOVE_ANT, [myQueen.coords, (myQueen.coords[0]+1, myQueen.coords[1])], None)

        # if the hasn't moved, have her move in place so she will attack
        if (not myQueen.hasMoved):
            return Move(MOVE_ANT, [myQueen.coords], None)

        # if I have the foos and the anthill is unoccupied then
        # make a drone
        if (myInv.foodCount > 2):
            if (getAntAt(currentState, myInv.getAnthill().coords) is None):
                return Move(BUILD, [myInv.getAnthill().coords], DRONE)

        # Move all my drones towards the enemy
        myDrones = getAntList(currentState, me, (DRONE,))
        for drone in myDrones:
            if not (drone.hasMoved):
                droneX = drone.coords[0]
                droneY = drone.coords[1]
                if (droneY < 9):
                    droneY += 1;
                else:
                    droneX += 1;
                if (droneX, droneY) in listReachableAdjacent(currentState, drone.coords, 3):
                    return Move(MOVE_ANT, [drone.coords, (droneX, droneY)], None)
                else:
                    return Move(MOVE_ANT, [drone.coords], None)


    ##
    # getAttack
    #
    # This agent never attacks
    #
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        return enemyLocations[0]  # don't care

    ##
    # registerWin
    #
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        # method templaste, not implemented
        pass
