import requests
from bs4 import BeautifulSoup
from re import sub

SEARCH_URL_PREFIX = "https://www.cdkeys.com/#q="
STORE_PAGE_URL_PREFIX = "https://www.cdkeys.com/pc/"
HEADERS = headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
class CDKScraper:
    __storeURL = None
    __price = None
    __inStock = None
    __gameFound = None
    __type = None
    def __init__(self, title, type):
        if type == "game":
            title = title + " pc steam"
        else:
            title = title + " pc dlc steam"
        self.__storeURL = STORE_PAGE_URL_PREFIX + to_slug(title)
        storePage = requests.get(self.__storeURL, headers = HEADERS)
        soup = BeautifulSoup(storePage.content, 'html.parser')
        
        if soup.find("h1", {"data-text": "404"}):
            self.__gameFound = False
            return
        self.__gameFound = True

        self.refresh_stock(soup)
        self.refresh_price(soup)
        self.__type = type
    

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


    def refresh(self, soup):
        self.refresh_stock(soup)
        self.refresh_price(soup)


    def print_info(self):
        print(f"URL: {self.__storeURL},\nPrice: {self.__price},\nIn Stock?: {self.__inStock},\nGame Found?: {self.__gameFound}")

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


