# WarehouseSimulation

In the context of Smart Warehouses, where autonomous robots perform tasks of object transportation, it's essential to identify the optimal scheduling strategy to minimize the operating costs and avoid collisions that may occur on the path of two or more robots. The literature describes problems in this class as Multi-Robot Task Allocation problems (MRTA); such problems are NP-hard, which requires efficient heuristics. 

In this project, we focus on the task allocation process and the collision avoidance technique, intending to improve the heuristic proposed by P. Yang et al. We used standard A* to perform route planning.
Various task allocation methods were compared: Genetic Algorithm (GA), two techniques based on randomness, a greedy approach, and customization of the greedy approach in which agents can negotiate a task. For the collision avoidance problem, we introduced a cooperative mechanism discussed in the report.
