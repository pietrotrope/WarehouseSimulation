from configuration import *

griglia = [[0 for x in range(nCols)] for y in range(nRows)]

offsetFromTop = 2
offsetFromLeft = 5

podPositions = []
pickingStationPositions = []

for x in range(1, 7):
  for y in range(4):
    for i in range(10):
      griglia[x*4-offsetFromTop][i+y*12+offsetFromLeft]=3
      griglia[x*4-offsetFromTop+1][i+y*12+offsetFromLeft]=3
      podPositions.append((x*4-offsetFromTop,i+y*12+offsetFromLeft))
      podPositions.append((x*4-offsetFromTop+1,i+y*12+offsetFromLeft))

for x in range(22):
  griglia[x+offsetFromTop][0]=2
  griglia[x+offsetFromTop][1]=2
  pickingStationPositions.append((x+offsetFromTop,1))

pickingStationPositions.append((offsetFromTop,0))
pickingStationPositions.append((offsetFromTop+22,0))
