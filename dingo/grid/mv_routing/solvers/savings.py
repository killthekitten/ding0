"""
    Copyright 2016 openego development group
    Licensed under GNU General Public License 3.0. See the LICENSE file at the
    top-level directory of this distribution or obtain a copy of the license at
    http://www.gnu.org/licenses/gpl-3.0.txt
    
    Based on code by Romulo Oliveira copyright (C) 2015,
    https://github.com/RomuloOliveira/monte-carlo-cvrp
    Originally licensed under the Apache License, Version 2.0. You may obtain a
    copy of the license at http://www.apache.org/licenses/LICENSE-2.0
"""

import operator
import time

from models import models
from solvers.base import BaseSolution, BaseSolver

class SavingsSolution(BaseSolution):
    """Solution class for a Clarke and Wright Savings parallel algorithm"""

    def __init__(self, cvrp_problem):
        super(SavingsSolution, self).__init__(cvrp_problem)
        
        self._nodes = {x.name(): models.Node(x.name(), x.demand()) for x in cvrp_problem.nodes()}
        self._routes = [models.Route(cvrp_problem, cvrp_problem.capacity()) for _ in range(len(self._nodes) - 1)]

        for i, node in enumerate([node for node in list(self._nodes.values()) if node.name() != cvrp_problem.depot().name()]):
            self._routes[i].allocate([node])

    def clone(self):
        """Returns a deep copy of self

        Clones:
            routes
            allocation
            nodes
        """

        new_solution = self.__class__(self._problem)

        # Clone routes
        for index, r in enumerate(self._routes):
            new_route = new_solution._routes[index] = models.Route(self._problem, self._problem.capacity())
            for node in r.nodes():
                # Insert new node on new route
                new_node = new_solution._nodes[node.name()]
                new_route.allocate([new_node])

        # remove empty routes from new solution
        new_solution._routes = [route for route in new_solution._routes if route._nodes]
        
        return new_solution

    def is_complete(self):
        """Returns True if this is a complete solution, i.e, all nodes are allocated
        TO BE REVIEWED
        """
        allocated = all(
            [node.route_allocation() is not None for node in list(self._nodes.values()) if node.name() != self._problem.depot().name()]
        )

        #valid_routes = len(self._routes) == self._vehicles
        valid_routes = len(self._routes) == 1 #workaround: try to use only one route (otherwise process will stop if no of vehicles is reached)

        valid_demands = all([route.demand() <= route.capacity() for route in self._routes])
        ##### NEW CAPACITY DEFINITION / CHECK CONSTRAINTS HERE
        #valid_tech_constraints = all([route.tech_constraints_satisfied() for route in self._routes])
        
        #if allocated and valid_routes and valid_demands:
        #    print('xxx')
        return allocated and valid_routes and valid_demands
        #return allocated and valid_demands

    def process(self, pair):
        """Processes a pair of nodes into the current solution

        MUST CREATE A NEW INSTANCE, NOT CHANGE ANY INSTANCE ATTRIBUTES

        Returns a new instance (deep copy) of self object
        """
        a, b = pair

        new_solution = self.clone()

        i, j = new_solution.get_pair((a, b))

        route_i = i.route_allocation()
        route_j = j.route_allocation()

        inserted = False

        if ((route_i is not None and route_j is not None) and (route_i != route_j)):
            if route_i._nodes.index(i) == 0 and route_j._nodes.index(j) == len(route_j._nodes) - 1:
                if route_j.can_allocate(route_i._nodes):
                    route_j.allocate(route_i._nodes)

                    if i.route_allocation() != j.route_allocation():
                        raise Exception('wtf')

                    inserted = True
            elif route_j._nodes.index(j) == 0 and route_i._nodes.index(i) == len(route_i._nodes) - 1:
                if route_i.can_allocate(route_j._nodes):
                    route_i.allocate(route_j._nodes)

                    if i.route_allocation() != j.route_allocation():
                        raise Exception('wtf j')

                    inserted = True

        new_solution._routes = [route for route in new_solution._routes if route._nodes]

        return new_solution, inserted

    def can_process(self, pairs):
        """Returns True if this solution can process `pairs`

        Parameters:
            pairs: List of pairs
        """
        i, j = pairs

        # Neither points are in a route
        if i.route_allocation() is None or j.route_allocation() is None:
            return True

        if self._allocated == len(list(self._problem.nodes())) - 1: # All nodes in a route
            return False

        return False

class ClarkeWrightSolver(BaseSolver):
    """Clark and Wright Savings algorithm solver class"""
    def compute_savings_list(self, graph):
        """Compute Clarke and Wright savings list

        A saving list is a matrix containing the saving amount S between i and j

        S is calculated by S = d(0,i) + d(0,j) - d(i,j) (CLARKE; WRIGHT, 1964)
        """

        savings_list = {}

        for i, j in graph.edges():
            t = (i, j)

            if i == graph.depot() or j == graph.depot():
                continue

            savings_list[t] = graph.distance(graph.depot(), i) + graph.distance(graph.depot(), j) - graph.distance(i, j)

        sorted_savings_list = sorted(list(savings_list.items()), key=operator.itemgetter(1), reverse=True)

        return [nodes for nodes, saving in sorted_savings_list]

    def solve(self, graph, timeout):
        """Solves the CVRP problem using Clarke and Wright Savings methods

        Parameters:
            graph: Graph instance
            timeout: max processing time in seconds

        Returns a solution (SavingsSolution class))
        """
        savings_list = self.compute_savings_list(graph)

        solution = SavingsSolution(graph)

        start = time.time()

        for i, j in savings_list[:]:
            #if i.name() == 28 or j.name() == 28:
            #    print('xxx')
            if solution.is_complete():
                break

            if solution.can_process((i, j)):
                solution, inserted = solution.process((i, j))

                if inserted:
                    savings_list.remove((i, j))

            if time.time() - start > timeout:
                break

        return solution