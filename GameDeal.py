import requests
from creds import API_KEY

API_URL = "https://api.isthereanydeal.com"
LOOKUP_ENDPOINT = "/games/lookup/v1"
SEARCH_ENDPOINT = "/games/search/v1"
PRICES_ENDPOINT = "/games/prices/v2"

class GameDeal:
    __title = None
    __id = None
    __bestDeals = None

    def __init__(self, title: str = None, id: str = None, deals = None):
        if id == None and deals == None:
            self.__title, self.__id, self.__bestDeals = GameDeal.search_game_title(title)
        else:
            self.__title = title
            self.__id = id
            self.__bestDeals = deals

    @staticmethod
    def search_game_title(searchTerm: str):
        """
        return tuple of title, id, deals
        """
        url = "".join((API_URL, SEARCH_ENDPOINT))
        params = {'key': API_KEY,
                    'title': searchTerm}
        response = requests.get(url, params = params)

        if response.status_code == 200:
            for data in response.json():
                deals = GameDeal.find_deals(data['title'], data['id'])
                if deals:
                    return data['title'], data['id'], deals
            
            print(f"No game with deals found")
            return None, None, None
        else:
            print(f"Failed to retrieve game data for title: status code {response.status_code}")
            return None, None, None

    @staticmethod
    def find_deals(title: str, id: str):
        """
        return best deals from cheapest to most expensive
        as a sorted array of dictionaries with keys 'store', 'price', 'voucher'
        """
        numDeals = 5 # max number of stores to return
        url = "".join((API_URL, PRICES_ENDPOINT))
        params = {'key': API_KEY,
                  'country': 'CA',
                  'nondeals': True,
                  'vouchers': True
                  }
        
        response = requests.post(url, params = params, json = [id])
        if response.status_code == 200:
            if response.json():
                data = response.json()[0]
            else:
                print("no prices found")
                return None
        else:
            print(f"Failed to get prices: status code {response.status_code}")
            return None
        
        
        deals = data['deals']
        bestDeals = [{'store': deal['shop']['name'],
                          'price': deal['price']['amount'], 
                          'voucher': deal['voucher'],
                          'url': deal['url']} for deal in deals]
        
        # top cheapest deals from least to greatest price
        bestDeals.sort(key = lambda deal: deal['price'])
                    
        return bestDeals[:numDeals]
    
    def refresh_deals(self):
        self.__bestDeals = GameDeal.find_deals(title = self.__title, id = self.__id)

    @staticmethod
    def lookup_game(title):
        # return tuple of title, id, deals from title parameter
        url = "".join((API_URL, LOOKUP_ENDPOINT))
        params = {'key': API_KEY,
                  'title': title}
        response = requests.get(url, params = params)
        if response.status_code == 200:
            if response.json()['found']:
                data = response.json()['game']
                deals = GameDeal.find_deals(data['title'], id = data['id'])
                return data['title'], data['id'], deals
            else:
                print(f'Game with title {title} not found')
        else:
            print(f'Failed to retrieve game data for {title}: status code {response.status_code}')
        return None

    def get_best_deals(self):
        return self.__bestDeals

    def get_id(self):
        return self.__id
    
    def get_title(self):
        return self.__title

    def print_info(self):
        print(f"Title: {self.__title}, id: {self.__id}, deals: {self.__bestDeals}")

    def isValid(self):
        return self.__id and self.__title

    def __eq__(self, other):
        if other != None and isinstance(other, GameDeal):
            return self.__id == other.__id
        return False
        
