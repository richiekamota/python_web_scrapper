from datetime import datetime
import re
import json
import requests
from bs4 import BeautifulSoup

class Product:
    def __init__(self):
        self.title = None
        self.price = None
        self.imageUrl = None
        self.capacityMB = None
        self.colour = None
        self.availabilityText = None
        self.isAvailable = None
        self.shippingText = None
        self.shippingDate = None

    def standard_date_format(self, date_str):
        matches = re.findall(r'(\d{1,2}) (\w+) (\d{4})|\d{4}-\d{2}-\d{2}|\s*(\d+)(?:[a-z]{2})?\s+(?:of\s+)?([a-z]{3})\s+(\d{4})|tomorrow', date_str)
        dates = [datetime.strptime(match, '%Y-%m-%d') for match in matches]
        return dates[0].strftime('%Y-%m-%d')

    def remove_duplicates(self, array):
        seen = set()
        unique_array = []
        for item in array:
            if item not in seen:
                unique_array.append(item)
                seen.add(item)
        return unique_array

class Scrape:
    def __init__(self):
        self.myproducts = []

    def run(self):
        url = 'https://www.magpiehq.com/developer-challenge/smartphones'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        pages = len(soup.select('#pages .px-6'))

        for i in range(1, pages + 1):
            page_url = f'{url}/?page={i}'
            response = requests.get(page_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            products = soup.select('.product')

            for product in products:
                title = product.select_one('.text-blue-600').get_text()
                cur_price = product.select_one('.text-lg').get_text()
                price = float(re.sub(r'[^\d.]', '', cur_price))
                capacity = int(product.select_one('.product-capacity').get_text()) * 1000
                img_url = product.select_one('img')['src']
                image_url = img_url.replace('..', 'https://www.magpiehq.com/developer-challenge/smartphones')
                availability_text = product.select('.bg-white div')[2].get_text()
                is_available = 'In Stock' in availability_text
                shipping_text = product.select('.bg-white div')[-1].get_text()
                shipping_date = ''
                if 'Unavailable for delivery' not in shipping_text and 'Free Shipping' not in shipping_text and 'Free Delivery' not in shipping_text and 'In Stock' not in shipping_text and shipping_text.strip():
                    shipping_date = Product().standard_date_format(shipping_text)

                product_instance = Product()
                product_instance.title = title
                product_instance.price = price
                product_instance.imageUrl = image_url
                product_instance.capacityMB = capacity
                product_instance.availabilityText = availability_text
                product_instance.isAvailable = is_available
                product_instance.shippingText = shipping_text
                product_instance.shippingDate = shipping_date

                self.myproducts.append(product_instance)

        self.myproducts = Product().remove_duplicates(self.myproducts)
        with open('output.json', 'w') as file:
            json.dump([vars(product) for product in self.myproducts], file)

if __name__ == "__main__":
    scrape = Scrape()
    scrape.run()
