# coding=utf-8
"""
Implementation of a DAG.
"""

from __future__ import division

import logging
import heapq
from itertools import tee, islice, cycle, chain
from collections import namedtuple
import operator

# FIXME: temp while prototyping. Do not PR
import sys
lbgeom_path = "/app/ladybug-geometry/"
if lbgeom_path not in sys.path:
    sys.path.insert(0, lbgeom_path)

# Geometry classes
from ladybug_geometry.geometry2d.pointvector import Point2D
from ladybug_geometry.geometry2d.line import LineSegment2D
from ladybug_geometry.geometry2d.ray import Ray2D
from ladybug_geometry import intersection2d


def _vector2hash(vector, tol=4):
    #  FIXME: find a better way of hashing spatial coordinates
    # myhash = "("
    # for i in range(len(vector)):
    #     coordinate = vector[i]
    #     myhash += str(round(coordinate, tol))
    #     if i < len(vector)-1:
    #         myhash += ","
    # myhash += ")"
    myhash = vector.__repr__()
    return myhash


class _Node(object):
    """Private Node class for DAG containment"""
    def __init__(self, key, val, adj_lst):
        self.key = key
        self.val = val
        self.adj_lst = adj_lst  # adj_lst: ['key1', 'key2' ....  'keyn']

    def num_children(self):
        return len(self.adj_lst)

    def __repr__(self):
        #return 'key: {}; val: {}'.format(self.key, self.val)
        return self.key

class PolygonDAG(object):
    """Private dictionary that coordinates point hashing"""
    def __init__(self):
        self.dag = {}
        self.keys = []
        self.num_node = 0

    def get_segment_adj(self, val):
        key = _vector2hash(val)
        if key in self.dag:
            return self.dag[key].adj_lst

    def add_segment_adj(self, val, adj_lst):
        """Instantiate _AdjGraphNode, we creates key = num_node
        """
        # Make the key
        key = _vector2hash(val)
        if key in self.dag:
            self.dag[key].adj_lst += adj_lst

        # Add to DAG
        self.dag[key] = _Node(key, val, adj_lst)
        self.num_node += 1



# class AdjGraph(object):
#     """
#     # Graph as adjacency list
#     #Good ref for adj graphs: http://interactivepython.org/runestone/static/pythonds/Graphs/Implementation.html
#     #adj_graph is a dict like this:
#     #{key1: _AdjGraphNode.adj_lst = [2,4],
#     # key2: _AdjGraphNode.adj_lst = [3,4],
#     # key3: _AdjGraphNode.adj_lst = [4],
#     # key4: _AdjGraphNode.adj_lst = [1]}

#     Graph
#     1     4
#        /  |
#     2     3

#     Adj Matrix:
#     [[x 1 2 3 4],
#      [1 - - - -],
#      [2 - - - x],
#      [3 - - - x],
#      [4 - - - -]]
#     """

#     def __init__(self,adj_graph=None):
#         self.adj_graph = adj_graph if adj_graph != None else {}
#         self.num_node = len(self.adj_graph.keys())
#     def vector2hash(self,vector,tol=4):
#         #Tolerance set to
#         myhash = "("
#         for i in xrange(len(vector)):
#             coordinate = vector[i]
#             myhash += str(round(coordinate,tol))
#             if i < len(vector)-1:
#                 myhash += ","
#         myhash += ")"
#         return myhash
#     def add_node(self,key,value,is_out_edge=False):
#         #_AdjGraphNode is a private class
#         #Instantiate _AdjGraphNode, we creates key = num_node
#         if key in self.adj_graph:
#             n = self.adj_graph[key]
#             print n.id, ' key already exists in adj_graph!'
#             return self.adj_graph[key]
#         id = len(self.adj_graph.keys())
#         adj_graph_node = _AdjGraphNode(key,value,id,is_out_edge)
#         #Now add it to the adj_graph
#         self.adj_graph[key] = adj_graph_node
#         self.num_node += 1
#         return adj_graph_node
#     def __getitem__(self,k):
#         if k in self.adj_graph:
#             return self.adj_graph[k]
#         else:
#             return None
#     def keylst_2_nodelst(self,keylst):
#         return map(lambda k: self.adj_graph[k],keylst)
#     def add_directed_edge(self,key,key2add):
#         #This function will add existing node key to adjacency list of
#         #another node indicating a directed edge
#         if key in self.adj_graph and key2add in self.adj_graph:
#             node = self.adj_graph[key]
#             if key2add in node.adj_lst or key2add == key:
#                 print 'key2add already in adj list or self-intersection'
#                 return None
#             node.adj_lst.append(key2add)
#         else:
#             print 'key not in adj graph'
#     def recurse_ccw(self,refn,nextn,lok,cycle,count):
#         def get_ccw_angle(prev_dir,next_dir):
#             #Input prev_dir vector and next_dir vector in CCW ordering
#             #Output CCW angle between them in radians

#             #Reverse prev_dir order for angle checking
#             #We create a new vector b/c must be ccw order for reflex check
#             reverse_prev_dir = prev_dir * -1.0
#             #Use the dot product to find the angle
#             dotprod = rc.Geometry.Vector3d.Multiply(reverse_prev_dir,next_dir)
#             try:
#                 cos_angle = dotprod/(prev_dir.Length * next_dir.Length)
#             except ZeroDivisionError:
#                 print 'ZeroDivisionError'
#                 cos_angle = 0.0

#             # Get angle from dot product
#             # This will be between 0 and pi
#             # b/c -1 < cos theta < 1
#             dotrad = math.acos(cos_angle)

#             #Use 2d cross product (axby - bxay) to see if next_vector is right/left
#             #This requires ccw ordering of vectors
#             #If cross is positive (for ccw ordering) then next_vector is to left (inner)
#             #If cross is negative (for ccw ordering) then next_vector is to right (outer)
#             #If cross is equal then zero vector, then vectors are colinear. Assume inner.

#             cross_z_sign = prev_dir[0] * next_dir[1] - prev_dir[1] * next_dir[0]
#             #print 'deg: ', round(math.degrees(dotrad),2)
#             #If reflex we must subtract 2pi from it to get reflex angle
#             if cross_z_sign < 0.0:
#                 dotrad = 2*math.pi - dotrad
#             return dotrad

#         if True: pass #weird code folding glitch neccessitatest this
#         #Input list of keys
#         #output key with most ccw
#         #Base case
#         #print 'startid, chkid:', cycle[0].id, nextn.id
#         cycle.append(nextn)
#         cycle_id_lst = map(lambda n: n.id, cycle)
#         if nextn.id == cycle_id_lst[0] or count > 20:
#             return cycle

#         #print 'cycle', cycle_id_lst

#         #reference direction vector
#         ref_edge_dir =  nextn.value - refn.value

#         min_rad = float("Inf")
#         min_node = None

#         for i in xrange(len(lok)):
#             k = lok[i]
#             n2chk = self.adj_graph[k]
#             #Make sure we don't backtrack
#             if n2chk.id == cycle_id_lst[-2]:
#                 continue
#             chk_edge_dir = n2chk.value - nextn.value
#             #print 'chkccw', refn.id, '--', nextn.id, '--->', n2chk.id
#             rad = get_ccw_angle(ref_edge_dir,chk_edge_dir)
#             if rad < min_rad:
#                 min_rad = rad
#                 min_node = n2chk
#             #print '---'
#         #print 'min is', n2chk.id,':', round(math.degrees(rad),2)
#         #print '---'
#         alok = min_node.adj_lst

#         return self.recurse_ccw(nextn,min_node,alok,cycle,count+1)
#     def find_most_ccw_cycle(self):
#         #def helper_most_ccw(lok):

#         #Input adjacency graph
#         #Output loc: listof (listof (listof pts in closed cycle))
#         LOC = []
#         keylst = self.get_sorted_keylst()
#         for i in xrange(len(keylst)):
#             key = keylst[i]
#             root_node = self.adj_graph[key]
#             if not root_node.is_out_edge:
#                 continue

#             #Identify the next node on outer edge
#             #b/c outer edge vertexes are placed first in adj graph
#             #worst complexity <= O(n)
#             for i in xrange(root_node.num_neighbor()):
#                 adj_key = root_node.adj_lst[i]
#                 neighbor = self.adj_graph[adj_key]
#                 if neighbor.is_out_edge:
#                     next_node = neighbor
#                     break

#             #Now we recursively check most ccw
#             n_adj_lst = next_node.adj_lst
#             cycle = [root_node]
#             try:
#                 cycle = self.recurse_ccw(root_node,next_node,n_adj_lst,cycle,0)
#             except:
#                 pass
#             #print '-------\n-----FINISHED CYCLE\n', cycle, '---\---\n'
#             LOC.append(cycle)
#         #print '-'
#         return LOC
#     def get_sorted_keylst(self):
#         valuelst = self.adj_graph.values()
#         valuelst.sort(key=lambda v: v.id)
#         keylst = map(lambda v: v.key,valuelst)
#         return keylst
#     def is_near_zero(self,num,eps=1E-10):
#         return abs(float(num)) < eps
#     def __repr__(self):
#         keylst = self.get_sorted_keylst()
#         strgraph = ""
#         for i in xrange(len(keylst)):
#             key = keylst[i]
#             node = self.adj_graph[key]
#             strgraph += str(node.id) + ': '
#             strgraph += str(map(lambda k: self.adj_graph[k].id,node.adj_lst))
#             strgraph += '\n'
#         return strgraph
#     def __contains__(self,key):
#         return self.adj_graph.has_key(key)