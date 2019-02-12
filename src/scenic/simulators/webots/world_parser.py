
import sys
import io
import time

import numpy as np

import antlr4
from antlr4.error.ErrorListener import ErrorListener
from scenic.simulators.webots.WBTLexer import WBTLexer
from scenic.simulators.webots.WBTParser import WBTParser
from scenic.simulators.webots.WBTVisitor import WBTVisitor

### Setup

## Classes representing various types of VRML nodes 

class Node:
	"""A generic VRML node"""
	def __init__(self, nodeType, attrs):
		self.nodeType = nodeType
		self.attrs = attrs

## Classes for parsing with ANTLR

# Error handling

class ErrorReporter(ErrorListener):
	"""ANTLR listener for reporting parse errors"""
	def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
		raise Exception(f'Parse error at {line}:{column}: {msg}')

# Walking the parse tree and extracting values

class Evaluator(WBTVisitor):
	"""Constructs an object representing the given value from the parse tree"""
	def __init__(self, nodeClasses):
		super().__init__()
		# Dictionary indicating which types of nodes have specialized classes
		self.nodeClasses = nodeClasses

	def visitNode(self, node):
		nodeType = node.Identifier().getText()
		attrs = self.visitNodeBody(node.nodeBody())
		if nodeType in self.nodeClasses:
			nodeClass = self.nodeClasses[nodeType]
			nodeObj = nodeClass(attrs)
		else:
			nodeObj = Node(nodeType, attrs)
		return nodeObj

	def visitNodeBody(self, body):
		return {attr.Identifier().getText(): self.visitValue(attr.value())
			for attr in body.attribute()}

	def visitValue(self, val):
		return self.visit(val.getChild(0))

	def visitVector(self, vec):
		return np.array([float(n.getText()) for n in vec.Number()])

	def visitVectorWithNewlines(self, vec):
		return self.visitVector(vec)

	def visitString(self, string):
		return string.getText()[1:-1]	# strip off quotes

	def visitArray(self, array):
		return [self.visit(val) for val in array.children
			if not isinstance(val, antlr4.tree.Tree.TerminalNode)]

	def visitBoolean(self, boolean):
		return boolean.getText() == 'TRUE'

def parse(path):
	"""Parse a world from a WBT file"""
	# Open file
	charStream = antlr4.FileStream(path)

	# Set up lexer and parser
	errorListener = ErrorReporter()
	lexer = WBTLexer(charStream)
	lexer.addErrorListener(errorListener)
	tokenStream = antlr4.CommonTokenStream(lexer)
	parser = WBTParser(tokenStream)
	parser.addErrorListener(errorListener)

	# Parse file
	return parser.world()

def findNodeTypesIn(types, world, nodeClasses={}):
	"""Find all nodes of the given types in a world"""
	evaluator = Evaluator(nodeClasses)
	types = tuple(types)
	instances = {ty: [] for ty in types}
	for node in world.children:
		if isinstance(node, WBTParser.DefnContext):
			node = node.node()
		nodeType = node.Identifier().getText()
		if nodeType in instances:
			val = evaluator.visitNode(node)
			instances[nodeType].append(val)
	return tuple(instances[ty] for ty in types)
