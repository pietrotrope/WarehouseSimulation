from environment import *
from random import randrange
from configuration import *
from task import *
from astar import *

class Agent:
  def __init__(self, position):
    self.position = position
    self.updatePosition(self.position)
    self.task = None
    self.path = [] 
  
  def updatePosition(self, newPosition):
    if griglia[newPosition[0]][newPosition[1]]==0:
      curPos = self.position
      griglia[curPos[0]][curPos[1]] = 0
      self.position = newPosition
      curPos = self.position
      griglia[curPos[0]][curPos[1]] = 1
  
  def move(self):
    self.chooseTask()

    if self.path == []:
      self.path = astar(griglia, self.position, self.task.podPosition)
      print(self.path)
    if self.path != []:
      nextMove = self.path.pop()
      if nextMove != None:
        self.updatePosition(nextMove)
  
  def chooseTask(self):
    if self.task == None:
      if len(taskList)>0:

        self.task = taskList.pop(0)
        griglia[self.task.podPosition[0]][self.task.podPosition[1]]=4
