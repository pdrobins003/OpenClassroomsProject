# Section 1: Install and import needed packages
import os
import csv
import requests
from bs4 import BeautifulSoup

#Section 2: Define URL variable
url = 'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'

#Section 3: Send a GET request to scrape the designated website
response = requests.get(url)
soup = BeautifulSoup(response.content, 'lxml')

#Section 4: Create a list of info to pull from site
product_page_url = url
upc = soup.find('th', text='UPC').find_next_sibling('td').text
title = soup.find('h1').text
price_incl_tax = soup.find('th', text='Price (incl. tax)').find_next_sibling('td').text
price_excl_tax = soup.find('th', text='Price (excl. tax)').find_next_sibling('td').text
quantity_available = soup.find('th', text='Availability').find_next_sibling('td').text.strip()
# noinspection PyUnresolvedReferences
product_description = soup.find('meta', attrs={'name': 'description'})['content'].strip()
# noinspection PyUnresolvedReferences
category = soup.find('ul', class_='breadcrumb').find_all('a')[-1].text
# noinspection PyUnresolvedReferences
review_rating = soup.find('p', class_='star-rating')['class'][1]
# noinspection PyUnresolvedReferences
image_url = soup.find('img')['src']
image_url = 'https://books.toscrape.com' + image_url.replace('../..', '')

#Section 5: Prepare the data to match the requested column titles
data = [{
    'Product Page URL': product_page_url,
    'UPC': upc,
    'Book Title': title,
    'Price (including tax)': price_incl_tax,
    'Price (excluding tax)': price_excl_tax,
    'Quantity Available': quantity_available,
    'Product Description': product_description,
    'Category': category,
    'Review Rating': review_rating,
    'Image URL': image_url
}]

#Section 6: Write scraped data to csv file
with open('books.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Product Page URL', 'UPC', 'Book Title', 'Price (including tax)',
                  'Price (excluding tax)', 'Quantity Available', 'Product Description',
                  'Category', 'Review Rating', 'Image URL']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)

print("Data has been written to books.csv")



