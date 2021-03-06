import collections
import math
import pickle
import sqlite3 as sql


class Graph:
	''' DataType to represent a graph. inspired by https://gist.github.com/econchick/4666413

	Class Attributes:
		self.vertices
		Type: set
		Stores the vertices's in the graph

		self.edges
		Type: dictionary
		Stores the connecting edges for each vertex

		self.weights
		Type: dictionary
		Stores a dictionary where the keys are tuples. Each tuple representing the distance
		between the two vertices in the tuple.

	'''

	def __init__(self):
		self.vertices = set()
		self.edges = collections.defaultdict(list)
		self.weights = {}

	def add_vertex(self, value):
		''' Add a new vertex to the graph '''
		self.vertices.add(value)

	def add_edge(self, from_vertex, to_vertex, distance):
		''' Adds a connection between two vertices by adding an entry to edges with
		the from and to node '''
		if from_vertex == to_vertex:
			pass
		self.edges[from_vertex].append(to_vertex)
		self.edges[to_vertex].append(from_vertex)
		self.weights[(from_vertex, to_vertex)] = distance
		self.weights[(to_vertex, from_vertex)] = distance


class Database:
	''' Database class which handles the storing and collection of data from "ECC_Building.sqlite3"

	I have used a database here instead of just creating the Graph on the fly. This does not save time when
	the code is run however in the long run this means that this code can be reused by just linking a different
	database file. As long as the database file contains the correct information the Algorithm should work as
	expected.

	Class Attributes
		self.connection
		Type: connection to 'ECC_Building.sqlite3'

		self.cursor
		Type: cursor
		Cursor to execute sql commands to database

	'''

	def __init__(self):
		self.connection = sql.connect('ECC_Building.sqlite3')
		self.cursor = self.connection.cursor()

	def add_vertex(self, vertex):
		''' Adds 'vertex' to the 'vertices' table in the database '''

		self.cursor.execute(('INSERT INTO Vertices VALUES (?)'), (vertex,))
		self.connection.commit()

	def add_edge(self, edge):
		''' Adds 'edge' to the 'Edges' table in the database '''

		pdata = pickle.dumps(edge, pickle.HIGHEST_PROTOCOL)
		self.cursor.execute(('INSERT INTO Edges VALUES (?)'), (pdata,))
		self.connection.commit()

	def get_edges(self):
		''' Gets all the edges from the 'Edges' table in ECC_Building.sqlite3 and returns them in a list '''

		edges = []

		self.cursor.execute('SELECT * FROM Edges')

		while True:
			pdata = self.cursor.fetchone()
			if not pdata:
				break
			else:
				edge = pickle.loads(pdata[0])
				edges.append(edge)

		return edges

	def get_vertices(self):
		''' Gets all the vertices from the 'vertices' table in ECC_Building.sqlite3 and returns them in a list '''

		vertices = []

		self.cursor.execute('SELECT * FROM Vertices')

		while True:
			vertex = self.cursor.fetchone()
			if not vertex:
				break
			else:
				vertices.append(vertex[0])

		return vertices


def dijkstra(graph, start_node):
	'''
	# Influenced by http://alexhwoods.com/dijkstra/
	Method variables:
		visited
		Type: set
		Stores the values of visited nodes

		progress
		Type: dictionary
		Stores a node value with the distance to that node from the start node
		Key = Vertex in graph
		Value = distance to Vertex from start

		predecessors
		Type: dictionary
		Key = Node
		Value = Node which traveled from to get to Key

	'''

	# initialize variables
	visited = set()

	# progress represents the distance from start to vertex. It is created with each distance
	# being equal to 'math.inf' this is because we do not know the distance to
	# any node yet.
	progress = dict.fromkeys(list(graph.vertices), math.inf)
	predecessors = dict.fromkeys(list(graph.vertices), None)

	# Update the start node in progress to the value 0.
	progress[start_node] = 0

	# While there is a node that is not in visited
	while visited != graph.vertices:
		# vertex becomes the closest node that has not yet been visited. It
		# will begin at 'start_node'
		vertex = min((set(progress.keys()) - visited), key=progress.get)

		# for each node which is not in visited
		for neighborNode in set(graph.edges[vertex]) - visited:
			# New path is set to the current distance value in 'progress[vertex]
			# plus the new weight distance'
			testPath = progress[vertex] + graph.weights[vertex, neighborNode]

			# If testPath is shorted than current path 'progress[neighborNode]'
			if testPath < progress[neighborNode]:
				# Update path to shorted 'testPath'
				progress[neighborNode] = testPath

				# Update previous vertex of the neighborNode
				predecessors[neighborNode] = vertex
		visited.add(vertex)
	return (progress, predecessors)


def short_path(graph, start, end):
	''' Uses the Dijkstra Method to return the shortest path from 'start' to 'end' '''

	if start not in graph.vertices or end not in graph.vertices:
		raise TypeError("Your starting point or destination is not in the graph")

	# Update progress and predecessors with the Dijkstra method
	progress, predecessors = dijkstra(graph, start)

	# initialize variables
	currentPath = []
	vertex = end

	while vertex != None:
		currentPath.append(vertex)
		vertex = predecessors[vertex]

	return currentPath[::-1], progress[end]

# if __name__ == '__main__':

############################## First Unit Testing graph ##################

	# Graph = Graph()
	# # Vertices's
	# Graph.add_vertex('a')
	# Graph.add_vertex('b')
	# Graph.add_vertex('c')
	# Graph.add_vertex('d')
	# Graph.add_vertex('e')
	# # Edges
	# Graph.add_edge('a', 'b', 5)
	# Graph.add_edge('a', 'c', 6)
	# Graph.add_edge('a', 'd', 10)
	# Graph.add_edge('b', 'd', 6)
	# Graph.add_edge('c', 'd', 6)
	# Graph.add_edge('d', 'e', 2)

############################## Second Unit Testing graph #################

	# db = Database()
	# Graph = Graph()

	# edges = db.get_edges() # get edges
	# vertices = db.get_vertices() # get vertices's

	# for edge in edges:
	# 	Graph.add_edge(edge[0], edge[1], edge[2])
	# for vertex in vertices:
	# 	Graph.add_vertex(vertex)

	# Unit testing loop to test all variations of

	# Unit Test for Dijkstra's Algorithm
	# for node in set(Graph.vertices):
	# 	for vertex in set(Graph.vertices):
	# 		print('From: {0}, To: {1}'.format(node, vertex), (short_path(Graph, node, vertex)))

	############################## Graph Stored in the database #################

	# Vertices: {'Main Entrance', 'ECG-13', 'ECG-14', 'First Floor Stairs', 'ECG-27', 'ECG-15'}

	# Edges: defaultdict(<class 'list'>, {'Main Entrance': ['ECG-15', 'ECG-27', 'First Floor Stairs'], 'ECG-14': ['ECG-13', 'ECG-15'], 'First Floor Stairs': ['ECG-15', 'ECG-27', 'Main Entrance'],
	# 'ECG-13': ['ECG-14', 'ECG-15'], 'ECG-27': ['Main Entrance', 'First Floor Stairs'], 'ECG-15': ['ECG-13', 'ECG-14', 'Main Entrance', 'First Floor Stairs']})

	# Weights: {('ECG-13', 'ECG-14'): 2, ('ECG-15', 'Main Entrance'): 5, ('ECG-14', 'ECG-15'): 1, ('First Floor Stairs', 'ECG-27'): 4, ('ECG-15', 'First Floor Stairs'): 2, 
	# ('ECG-27', 'First Floor Stairs'): 4, ('ECG-15', 'ECG-14'): 1, ('ECG-14', 'ECG-13'): 2, ('First Floor Stairs', 'ECG-15'): 2, ('ECG-13', 'ECG-15'): 4, 
	# ('First Floor Stairs', 'Main Entrance'): 3, ('ECG-27', 'Main Entrance'): 1, ('Main Entrance', 'ECG-15'): 5, ('ECG-15', 'ECG-13'): 4, ('Main Entrance', 'First Floor Stairs'): 3, ('Main Entrance', 'ECG-27'): 1}
