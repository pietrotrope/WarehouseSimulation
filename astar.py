def astar(griglia, A, B):
    # first, let's look for the beginning position, there is better but it works
    (i_s, j_s) = A
    # and take the goal position (used in the heuristic)
    (i_e, j_e) = B

    width = len(griglia[0])
    height = len(griglia)

    heuristic = lambda i, j: abs(i_e - i) + abs(j_e - j)
    comp = lambda state: state[2] + state[3] # get the total cost

    # small variation for easier code, state is (coord_tuple, previous, path_cost, heuristic_cost)
    fringe = [((i_s, j_s), list(), 0, heuristic(i_s, j_s))]
    visited = {} # empty set

    # maybe limit to prevent too long search
    for lvar in range(500):

        # get first state (least cost)
        state = fringe.pop(0)

        # goal check
        (i, j) = state[0]
        if abs(i_e - i) + abs(j_e - j)<=1:
            path = [state[0]] + state[1]
            return path

        # set the cost (path is enough since the heuristic won't change)
        visited[(i, j)] = state[2] 

        # explore neighbor
        neighbor = list()
        if i > 0 and griglia[i-1][j] == 0:
            neighbor.append((i-1, j))
        if i+1 < height and griglia[i+1][j] == 0:
            neighbor.append((i+1, j))
        if j > 0 and griglia[i][j-1] == 0:
            neighbor.append((i, j-1))
        if j+1 < width and griglia[i][j+1] == 0:
            neighbor.append((i, j+1))

        for n in neighbor:
            next_cost = state[2] + 1
            if n in visited and visited[n] >= next_cost:
                continue
            fringe.append((n, [state[0]] + state[1], next_cost, heuristic(n[0], n[1])))

        # resort the list (SHOULD use a priority queue here to avoid re-sorting all the time)
        fringe.sort(key=comp)
    return []


def astar2(m,startp,endp):
    w=len(m[0])
    h = len(m)
    sx,sy = startp
    ex,ey = endp

    node = [None,sx,sy,0,abs(ex-sx)+abs(ey-sy)] 
    closeList = [node]
    createdList = {}
    createdList[sy*w+sx] = node
    k=0
    while(closeList):
        node = closeList.pop(0)
        x = node[1]
        y = node[2]
        l = node[3]+1
        k+=1
        #find neighbours 
        if k&1:
            neighbours = ((x,y+1),(x,y-1),(x+1,y),(x-1,y))
        else:
            neighbours = ((x+1,y),(x-1,y),(x,y+1),(x,y-1))
        for nx,ny in neighbours:
            if abs(nx-ex) + abs(ny-ey) <1:
                path = [(ex,ey)]
                while node:
                    path.append((node[1],node[2]))
                    node = node[0]
                return list(path)            
            if 0<=nx<w and 0<=ny<h and m[ny][nx]==0:
                if ny*w+nx not in createdList:
                    nn = (node,nx,ny,l,l+abs(nx-ex)+abs(ny-ey))
                    createdList[ny*w+nx] = nn
                    #adding to closelist ,using binary heap
                    nni = len(closeList)
                    closeList.append(nn)
                    while nni:
                        i = (nni-1)>>1
                        if closeList[i][4]>nn[4]:
                            closeList[i],closeList[nni] = nn,closeList[i]
                            nni = i
                        else:
                            break


    return []