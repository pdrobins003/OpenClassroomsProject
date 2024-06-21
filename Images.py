#Section 1: Install and import needed packages
import os
import csv
import requests
from bs4 import BeautifulSoup
import subprocess

# Section 2: get url to main page to scrape each category
base_url = 'https://books.toscrape.com/catalogue/page-{}.html'
page_number = 1
product_page_urls = []

# Section 3: Loop the script to go through every category and get urls for each page
while True:
    # Section 2a: Construct the URL for the current page
    url = base_url.format(page_number)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')

    # Section 3b: Find all product page URLs on the current page, loop and exit loop if no book links are found (end of catalog)
    book_links = soup.select('h3 a')
    if not book_links:
        break

    # Section 3c: Extract the relative URL and construct the full URL
    for link in book_links:
        relative_url = link['href']
        product_page_url = 'https://books.toscrape.com/catalogue/' + relative_url.replace('../../', '')
        product_page_urls.append(product_page_url)

    page_number += 1

# Section 4: Write the info for the category urls to csv file
with open('product_page_urls.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Product Page URL']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for url in product_page_urls:
        writer.writerow({'Product Page URL': url})

print(f"{len(product_page_urls)} product page URLs have been written to product_page_urls.csv")

# Section 5: go back to the main site
base_site_url = 'https://books.toscrape.com/index.html'

# Section 6: get the main page
response = requests.get(base_site_url)
soup = BeautifulSoup(response.content, 'lxml')

# Section 7: Pull category urls
categories = soup.find('ul', class_='nav-list').find('ul').find_all('a')
category_urls = {cat.text.strip(): 'https://books.toscrape.com/' + cat['href'] for cat in categories}


# Section 8: Define info needed to be extracted and the return function
def extract_book_data(book_url):
    response = requests.get(book_url)
    soup = BeautifulSoup(response.content, 'lxml')

    product_page_url = book_url

    # Section 8a: Check if the elements exist and handle missing elements gracefully
    upc_element = soup.find('th', string='UPC')
    upc = upc_element.find_parent('tr').find_all('td')[0].text if upc_element else 'N/A'

    title = soup.find('h1').text if soup.find('h1') else 'N/A'

    price_incl_tax_element = soup.find('th', string='Price (incl. tax)')
    price_incl_tax = price_incl_tax_element.find_parent('tr').find_all('td')[
        0].text if price_incl_tax_element else 'N/A'

    price_excl_tax_element = soup.find('th', string='Price (excl. tax)')
    price_excl_tax = price_excl_tax_element.find_parent('tr').find_all('td')[
        0].text if price_excl_tax_element else 'N/A'

    quantity_available_element = soup.find('th', string='Availability')
    quantity_available = quantity_available_element.find_parent('tr').find_all('td')[
        0].text.strip() if quantity_available_element else 'N/A'

    product_description = soup.find('meta', attrs={'name': 'description'})['content'].strip() if soup.find('meta',
                                                                                                           attrs={
                                                                                                               'name': 'description'}) else 'N/A'

    category = soup.find('ul', class_='breadcrumb').find_all('a')[-1].text if soup.find('ul',
                                                                                        class_='breadcrumb') and soup.find(
        'ul', class_='breadcrumb').find_all('a') else 'N/A'

    review_rating_element = soup.find('p', class_='star-rating')
    review_rating = review_rating_element['class'][1] if review_rating_element else 'N/A'

    image_element = soup.find('img')
    image_url = 'https://books.toscrape.com/' + image_element['src'].replace('../', '') if image_element else 'N/A'

    return {
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
    }


# Section 9: Copy images of every page opened can use UPC # to reference pic to URL
def save_image(image_url, title, book_images='book_images'):
    # Create a directory for images if it doesn't exist
    if not os.path.exists(book_images):
        os.makedirs(book_images)

    # Section 10: Sanitize the title to remove any unsafe elements and create a file name
    image_filename = os.path.join(book_images, f"{title.replace('/', '_').replace(':', '').replace('?', '')}.jpg")

    print(f"Saving image to: {image_filename}")
    print(f"Image URL: {image_url}")

    # Section 11: Download and save images
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(image_filename, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"Image saved successfully: {image_filename}")
        else:
            print(f"Failed to retrieve image from {image_url}, status code {response.status_code}")
    except Exception as e:
        print(f"An error occurred while saving the image: {e}")


# Section 12: Define the category url loop
def extract_books_from_category(category_url):
    book_data = []
    page_url = category_url
    while page_url:
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, 'lxml')

        # Section 13: Scrape urls on current page
        book_links = soup.select('h3 a')
        for link in book_links:
            relative_url = link['href']
            book_url = 'https://books.toscrape.com/catalogue/' + relative_url.replace('../../', '')
            book_info = extract_book_data(book_url)
            book_data.append(book_info)

            # Section 14: Save the image of the book
            if book_info['Image URL'] != 'N/A':
                save_image(book_info['Image URL'], book_info['Book Title'])

        # Section 15: Scrape next page
        next_button = soup.find('li', class_='next')
        if next_button:
            next_page_url = next_button.find('a')['href']
            page_url = category_url.rsplit('/', 1)[0] + '/' + next_page_url
        else:
            page_url = None

    return book_data


# Section 16: Create a directory for the csv files
if not os.path.exists('book_data'):
    os.makedirs('book_data')

# Section 17: Loop for each category to get all data
for category_name, category_url in category_urls.items():
    print(f"Extracting data for category: {category_name}")
    books = extract_books_from_category(category_url)
    csv_file = os.path.join('book_data', f'{category_name}.csv')

    # Section 18: Write pulled data to csv file
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Product Page URL', 'UPC', 'Book Title', 'Price (including tax)',
                      'Price (excluding tax)', 'Quantity Available', 'Product Description',
                      'Category', 'Review Rating', 'Image URL']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(books)

    print(f"Data for category '{category_name}' has been written to {csv_file}")

print("Data extraction complete.")


# Section 19: Write requirement file
def create_requirements_file(output_file='requirements.txt'):
    with open(output_file, 'w') as file:
        result = subprocess.run(['pip', 'freeze'], stdout=subprocess.PIPE)
        file.write(result.stdout.decode('utf-8'))