import random

# PASSAGE
# c_w - completeness weight
# dfb_w - distance from begining of the document weight
# d_w - density weight
# tfidf_w - tf-idf weight
# wo_w - word order weight

class Genetic:
	def __init__(self, settings, output):
		self.population_size = settings['POPULATION_SIZE']
		self.children_count = settings['CHILDREN_COUNT']
		self.mutation_possibility = settings['MUTATION_POSSIBILITY']
		self.output = open(output, 'w')

	# c_w, dfb_w, d_w. tfidf_w, wo_w
	def init_population(self):
		random.seed()
		self.population = []
		for i in range(self.population_size):
			species = [1.0 + random.random() / 2.0, 1.0 + random.random() / 2.0, 1.0 + random.random() / 2.0, 1.0 + random.random() / 2.0, 1.0 + random.random() / 2.0]
			self.population.append(species)
		self.fitness = None
		return self.population[:]

	def crossing(self):
		self.children = []
		self.sorted_population = sorted([(self.fitness[i], self.population[i]) for i in range(self.population_size)],\
					key=lambda _tuple : _tuple[0], reverse=True)
		for i in range(self.children_count / 2):
			crossing_point = random.randint(1, 4)
			parent1 = random.randint(0, self.population_size / 4)
			parent2 = random.randint(0, self.population_size - 1)
			self.children.append(self.sorted_population[parent1][1][:crossing_point] \
					+ self.sorted_population[parent2][1][crossing_point:])
			self.children.append(self.sorted_population[parent2][1][:crossing_point] \
					+ self.sorted_population[parent1][1][crossing_point:])

	def mutation(self):
		for i in range(self.children_count):
			if random.random() > self.mutation_possibility:
				continue
			mutation_factory =  1.0 + (0.5 - random.random()) / 5.0 # mutation_factory is in [0.9 .. 1.1]
			mutation_position = random.randint(0, 4)
			self.children[i][mutation_position] *= mutation_factory
		for i in range(self.population_size):
			if random.random() > self.mutation_possibility:
				continue
			mutation_factory = 1.0 + (0.5 - random.random()) / 5.0
			mutation_position = random.randint(0, 4)
			self.population[i][mutation_position] *= mutation_factory

	def selection(self):
		# we took the best half of population, and add children 
		self.population = [species for fitness, species in self.sorted_population][:self.population_size / 2] + self.children
		self.population = self.population[:self.population_size]

	def set_fitness(self, fitness):
		self.fitness = fitness[:]

	def get_population(self):
		return self.population[:]

	def print_best(self):
		index = self.fitness.index(max(self.fitness))
		result = ' '.join(map(str, self.population[index] + [self.fitness[index]]))
		print result
		self.output.write(result + '\n')
