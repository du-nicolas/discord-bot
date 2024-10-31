import requests
from creds import API_KEY
import CDKScraper as cdks

API_URL = "https://api.isthereanydeal.com"
LOOKUP_ENDPOINT = "/games/lookup/v1"
SEARCH_ENDPOINT = "/games/search/v1"
PRICES_ENDPOINT = "/games/prices/v2"

class GameDeal:
    __title = None
    __id = None
    __bestDeals = None
    __CDKeysDeal = None
    __type = None



    def __init__(self, title: str = None, id: str = None, deals = None):
        if id == None and deals == None:
            self.search_game_title(title)



    def search_game_title(self, searchTerm: str):
        """
        return tuple of title, id, deals
        """
        url = "".join((API_URL, SEARCH_ENDPOINT))
        params = {'key': API_KEY,
                    'title': searchTerm}
        response = requests.get(url, params = params)

        if response.status_code == 200:
            for data in response.json():
                self.find_deals(data['title'], data['id'], data['type'])
                if self.__bestDeals:
                    self.__title = data['title']
                    self.__id = data['id'] 
                    self.__type = data['type']
                    return
            print(f"No game with deals found")

        else:
            print(f"Failed to retrieve game data for title: status code {response.status_code}")



    def find_deals(self, title: str, id: str, type: str):
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
        
        if self.__CDKeysDeal:
            self.__CDKeysDeal.refresh()
            bestDeals.append(self.__CDKeysDeal.get_details())
        else:
            CDKeysDeal = self.find_CDKeys_Deal(title, type)
            if CDKeysDeal:
                self.__CDKeysDeal = CDKeysDeal
                bestDeals.append(CDKeysDeal.get_details())

        # top cheapest deals from least to greatest price
        bestDeals.sort(key = lambda deal: deal['price'])
                    
        self.__bestDeals = bestDeals[:numDeals]
    


    def refresh_deals(self):
        self.find_deals(self.__title, self.__id, self.__type)



    def find_CDKeys_Deal(self, title, type):
        CDKeysDeal = cdks.CDKScraper(title, type)
        
        if CDKeysDeal.get_gameFound():
            return CDKeysDeal
        return None



    def get_best_deals(self):
        return self.__bestDeals

    def get_id(self):
        return self.__id
    
    def get_title(self):
        return self.__title

    def print_info(self):
        print(f"Title: {self.__title}, id: {self.__id}, deals: {self.__bestDeals}, Type: {self.__type}")

    def isValid(self):
        return self.__id and self.__title

    def __eq__(self, other):
        if other != None and isinstance(other, GameDeal):
            return self.__id == other.__id
        return False
        
