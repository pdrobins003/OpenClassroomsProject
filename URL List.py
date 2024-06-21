#Section 1: Install and Import Needed Packages
import csv
import requests
from bs4 import BeautifulSoup

#Section 2: define variables & send request to get URL
url = 'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'

response = requests.get(url)
soup = BeautifulSoup(response.content, 'lxml')

#Section 3: Create a variable list
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
#Section 4: Write collected data to a csv file
base_url = 'https://books.toscrape.com/catalogue/page-{}.html'
page_number = 1
product_page_urls = []

#Section 5: Create indefinite loop
while True:
    url = base_url.format(page_number)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')

#Section 6: Check if statement true
    book_links = soup.select('h3 a')
    if not book_links:
        break  # Exit the loop if no book links are found (end of catalog)

#Section 7: Create loop for a list
    for link in book_links:
        # Extract the relative URL and construct the full URL
        relative_url = link['href']
        product_page_url = 'https://books.toscrape.com/catalogue/' + relative_url.replace('../../', '')
        product_page_urls.append(product_page_url)

    page_number += 1
#Section 8: Open and write a file with the desiginated info
with open('product_page_urls.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Product Page URL']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for url in product_page_urls:
        writer.writerow({'Product Page URL': url})

#Section 9: Print a message to alert done
print(f"{len(product_page_urls)} product page URLs have been written to product_page_urls.csv")



