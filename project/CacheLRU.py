#!/usr/bin/env python
# -*- coding: utf-8 -*-

class CacheLRU():
	def __init__(self, size):
		self.items = {}
		self.key_order = []
		self.size = size
		self.items_count = 0

	def add(self, key, value):
		if key in self.items:
			return
		elif self.items_count == self.size:
			key_to_delete = self.key_order[0]
			del self.items[key_to_delete]
			self.key_order.pop(0)
		else:
			self.items_count += 1
			
		self.items[key] = value
		self.key_order.append(key)

	def has_key(self, key):
		return key in self.items

	def get(self, key):
		# TODO move key to end of the list
		self.key_order.remove(key)
		self.key_order.append(key)
		return self.items[key]
