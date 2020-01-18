# -*- coding: utf-8 -*-

__author__ = 'Sjur Spjeld Klemetsen, Ola Flesche Hellenes'
__email__ = 'sjkl@nmbu.no, olhellen@nmbu.no'

from src.biosim import Geography as Geo
import random as rd
import textwrap


class Map:
    """
    Map of the islands biography containing all the cells from Geography
    Makes a dictionary with coordinate tuples as key and instance classes
    as values
    """

    def __init__(self, land_string):
        self.island = {}
        self.create_map(land_string)

    def create_map(self, land_string):
        """
        Method that creates a map as a dictionary with coordinates as keys and
        cell instance as value
        :param land_string: string
        :return: dict
        """
        area_list = []
        for i in land_string:
            area_list.append(i.strip())
        while '' in area_list:
            area_list.remove('')
        self.check_string(land_string)

        rows = len(land_string.split('\n'))
        cols = int(len(area_list) / rows)
        coordinates = [(x, y) for x in range(rows) for y in range(cols)]

        for ind, val in enumerate(area_list):
            if val == 'O':
                area_list[ind] = Geo.Ocean()
            elif val == 'M':
                area_list[ind] = Geo.Mountain()
            elif val == 'D':
                area_list[ind] = Geo.Desert()
            elif val == 'S':
                area_list[ind] = Geo.Savannah()
            else:
                area_list[ind] = Geo.Jungle()

        for ind, val in enumerate(area_list):
            self.island[coordinates[ind]] = area_list[ind]
        return self.island

    @staticmethod
    def check_string(string):
        """
        Check if the edges at the map is ocean
        Check if the input string is one of the allowed categories
        Check if all the rows of the map have the same length
        :return: ValueError or nothing
        """
        s = textwrap.dedent(string)
        rows = s.split('\n')
        for i in rows[0]:
            if i is not 'O':
                raise ValueError('The edges of the map must be ocean')
        for i in rows[-1]:
            if i is not 'O':
                raise ValueError('The edges of the map must be ocean')

        accepted_landscape = ['J', 'S', 'D', 'M', 'O']
        for string in rows:
            for cell in string:
                if cell not in accepted_landscape:
                    raise ValueError('That is an invalid landscape')

        for i in rows:
            if i[0] is not 'O':
                raise ValueError('The edges of the map must be ocean')
            elif i[-1] is not 'O':
                raise ValueError('The edges of the map must be ocean')

        n_first_row = len(rows[0])
        for ind, val in enumerate(rows):
            if len(rows[ind]) != n_first_row:
                raise ValueError('All rows must have equal length')

    def check_input_in_sim(self, pos):
        if pos not in self.island.keys():
            raise ValueError('The coordinates does not exist on the map')
        elif isinstance(self.island[pos], Geo.Ocean):
            raise ValueError('Animals cannot be located in Ocean cells')
        elif isinstance(self.island[pos], Geo.Mountain):
            raise ValueError('Animals cannot be located in Mountain cells')

    def populate_map(self, pos, pop):
        """
        A method that populate the map with animals in a cell
        :return:
        """
        self.island[pos].populate_cell(pop)

    @staticmethod
    def find_neighbor_cells(position):
        """
        Method to find the neighbouring cells of a position
        :param position: Tuple
        :return: List
        """
        neighbours = [(position[0] + 1, position[1]),  # S
                      (position[0] - 1, position[1]),  # N
                      (position[0], position[1] + 1),  # E
                      (position[0], position[1] - 1)]  # W
        return neighbours

    def migrate_to(self, position):
        """
        Calculates which neighbour cell animal migrates to
        :return: tuple
        """
        neigh = self.find_neighbor_cells(position)
        propensity_list = []
        for cell in neigh:
            propensity_list.append(self.island[cell].propensity_herb())
        if sum(propensity_list) == 0:
            return position

        sum_propen = sum(propensity_list)
        p = []
        for prop in propensity_list:
            p.append(prop / sum_propen)

        prob = 0
        probability = []
        for i in p:
            prob += i
            probability.append(prob)

        prob = []
        for x, y in zip(neigh, probability):
            prob.append((x, y))

        a = rd.random()
        if a <= prob[0][1]:
            return prob[0][0]
        elif prob[0][1] < a <= prob[1][1]:
            return prob[1][0]
        elif prob[1][1] < a <= prob[2][1]:
            return prob[2][0]
        else:
            return prob[3][0]

    def move(self):
        """
        The animals move from one cell to another
        :return:
        """
        for loc, cell in self.island.items():
            moving_animals = cell.check_migration()
            for animal in moving_animals:
                new_cell = self.migrate_to(loc)
                self.island[new_cell].add_animal(animal)
                animal.animal_moved = True
            cell.remove_animals(moving_animals)

        for loc, cell in self.island.items():
            for animal in cell.pop_total:
                animal.animal_moved = False

    def get_landscape_type(self, position):
        """
        A method that gives you the landscape instance in a certain class
        :param position:
        :return:
        """
        return self.island[position]

    def annual_cycle(self):
        """
        An annual cycle on the map where every cell and animal on
        the map goes through yearly changes
        1) Fodder grow
        2) Animal eat
        3) Procreation
        4) Migration
        5) Aging
        6) Loss of weight
        7) Death
        """
        for coord, land in self.island.items():
            land.fodder_growth()
            land.herbivore_eat()
            land.carnivore_eat()
            land.animal_mating()
        self.move()
        for coord, land in self.island.items():
            land.age_weightloss()
            land.animals_die()


if __name__ == "__main__":
    area_type = '''\
                    OOOOOOOOOOOOOOOOOOOOO
                    OOOOOOOOSMMMMJJJJJJJO
                    OSSSSSJJJJMMJJJJJJJOO
                    OSSSSSSSSSMMJJJJJJOOO
                    OSSSSSJJJJJJJJJJJJOOO
                    OSSSSSJJJDDJJJSJJJOOO
                    OSSJJJJJDDDJJJSSSSOOO
                    OOSSSSJJJDDJJJSOOOOOO
                    OSSSJJJJJDDJJJJJJJOOO
                    OSSSSJJJJDDJJJJOOOOOO
                    OOSSSSJJJJJJJJOOOOOOO
                    OOOSSSSJJJJJJJOOOOOOO
                    OOOOOOOOOOOOOOOOOOOOO'''
    m = Map(area_type)
    m.populate_map((2, 8), [Carnivore(age=10, weight=50) for _ in range(1000)])
    m.populate_map((2, 8), [Herbivore(age=15, weight=30) for _ in range(1000)])
    print(m.island[1, 8].total_pop())
    print(m.island[2, 8].total_pop())
    print(m.island[3, 8].total_pop())
    print(m.island[2, 9].total_pop())
    print(m.island[2, 7].total_pop())
    rd.seed(1)
    m.annual_cycle()
    print('\n')
    print(m.island[1, 8].total_pop())
    print(m.island[2, 8].total_pop())
    print(m.island[3, 8].total_pop())
    print(m.island[2, 9].total_pop())
    print(m.island[2, 7].total_pop())
    print('\n')
    #print(m.island[2, 10].total_pop())
    #print(m.island[2, 6].total_pop())
    #print(m.island[4, 8].total_pop())








