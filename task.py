from environment import *
from random import randrange

class Task:
  def __init__(self, podPosition):
    self.podPosition=podPosition

def newTask():
  pos = podPositions[randrange(0,len(podPositions))]
  return Task(pos)

taskList = []
for i in range(100):
  taskList.append(newTask())