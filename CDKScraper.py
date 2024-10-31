import requests
from bs4 import BeautifulSoup
from re import sub

SEARCH_URL_PREFIX = "https://www.cdkeys.com/#q="
STORE_PAGE_URL_PREFIX = "https://www.cdkeys.com/pc/"
GAME_URL_SUFFIXES = ["-pc-steam", "-pc-cd-key-steam", "-pc-cd-key"]
DLC_URL_SUFFIXES = ["-pc-dlc steam", "-dlc-steam-cd-key"]
STORE_PAGE_URL_SUFFIXES = {
                "game": [" pc steam", " pc cd key steam", " pc cd key"],
                "dlc": [" pc dlc steam", " dlc steam cd key"]
}
HEADERS = headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
class CDKScraper:
    __storeURL = None
    __price = None
    __inStock = None
    __gameFound = None
    __type = None



    def __init__(self, title, type): 
        for suffix in STORE_PAGE_URL_SUFFIXES[type]:
            soup = self.get_soup(title + suffix)
            if soup:
                break
    
        if not soup:            
            self.__gameFound = False
            return

        self.__gameFound = True

        self.refresh_stock(soup)
        self.refresh_price(soup)
        self.__type = type
    


    def get_soup(self, title):
        url = STORE_PAGE_URL_PREFIX + to_slug(title)
        storePage = requests.get(url, headers = HEADERS)
        soup = BeautifulSoup(storePage.content, 'html.parser')

        if soup.find("h1", {"data-text": "404"}):
            return None
        
        self.__storeURL = url
        return soup



    def refresh_price(self, soup):
        priceString = soup.find("span", class_="price").get_text().strip()
        if priceString:
            self.__price = float(priceString[3:])
        


    def refresh_stock(self, soup):
        for div in soup.find_all("div", title_="Availability"):
            if div.get("title") == "product-usps-text":
                if div.get_text() == "Currently Out Of Stock":
                    self.__inStock = False
                    break
        self.__inStock = True



    def refresh(self):
        storePage = requests.get(self.__storeURL, headers = HEADERS)
        soup = BeautifulSoup(storePage.content, 'html.parser')
        self.refresh_stock(soup)
        self.refresh_price(soup)



    def print_info(self):
        print(f"URL: {self.__storeURL},\nPrice: {self.__price},\nIn Stock?: {self.__inStock},\nGame Found?: {self.__gameFound}")

    def get_details(self):
        shopName = "CDKeys"
        if not self.get_inStock():
                shopName = shopName + " (Out of Stock)"
        return {'store': shopName,
                "price": self.__price,
                "voucher": None, 
                "url": self.__storeURL}

    def get_inStock(self):
        return self.__inStock
    def get_price(self):
        return self.__price
    def get_gameFound(self):
        return self.__gameFound
    def get_URL(self):
        return self.__storeURL


def to_slug(s):
    """
    remove non-alphanumeric characters and replace space with dash
    """
    s = s.lower()
    s = sub(r'[^a-z0-9\s]','', s)
    s = sub(r'\s+', '-', s)
    return s


