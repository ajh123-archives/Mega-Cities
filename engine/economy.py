from .settings import *


class Economy:
    def __init__(self, money):
        self.dict = {
            'grass': {'cost': 10, 'sell': -10},
            'grass_north': {'cost': 10, 'sell': -10},
            'grass_east': {'cost': 10, 'sell': -10},
            'grass_west': {'cost': 10, 'sell': -10},
            'grass_south': {'cost': 10, 'sell': -10},
            'dirt': {'cost': 0, 'sell': 0},
            'orange tulip:seed': {'cost': 50, 'sell': 0},
            'orange tulip:flower': {'cost': 0, 'sell': 150},
            'tree': {'cost': 100, 'sell': -50},
            'concrete': {'cost': 50, 'sell': 0},
            'house': {'cost': 0, 'sell': 0},
            }
        self.money = money
        print(f'''Current money: {self.money}''')

    def sell(self, tile_data):
        self.money += self.dict[tile_data]['sell']
        print(f'''Sold a {tile_data} for ${self.dict[tile_data]['sell']}''')
        print(f'''Money: {self.money}''')

    def buy(self, tile_data):
        self.money -= self.dict[tile_data]['cost']
        print(f'''Bought a {tile_data} for ${self.dict[tile_data]['cost']}''')
        print(f'''Money: {self.money}''')

    def check_transaction(self, tile_data):
        money = self.money
        result = money - self.dict[tile_data]['cost']
        if result > 0:
            return True
        else:
            print('Not enough money to buy item!')
            return False
