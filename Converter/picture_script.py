import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_all_links(url, soup):
    """ Get all links on a page """
    links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        full_url = urljoin(url, href)
        if full_url.startswith(url):
            links.add(full_url)
    return links

def download_images(url, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"Accessing {url}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to access {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img')
    urls = [img['src'] for img in img_tags if 'src' in img.attrs]

    print(f"Found {len(urls)} images on {url}")

    for img_url in urls:
        full_url = urljoin(url, img_url)
        print(f"Downloading {full_url}")
        try:
            img_response = requests.get(full_url, stream=True)
            img_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {full_url}: {e}")
            continue

        img_name = os.path.join(dest_folder, os.path.basename(full_url))
        try:
            with open(img_name, 'wb') as f:
                for chunk in img_response.iter_content(1024):
                    f.write(chunk)
            print(f"Saved {img_name}")
        except IOError as e:
            print(f"Failed to save {img_name}: {e}")

    # Return all links found on this page
    return get_all_links(url, soup)

def scrape_site(base_url, dest_folder):
    visited = set()
    to_visit = {base_url}

    while to_visit:
        url = to_visit.pop()
        if url in visited:
            continue

        visited.add(url)
        new_links = download_images(url, dest_folder)
        to_visit.update(new_links - visited)

base_url = "https://docs.adapty.io/docs/"
destination_folder = "/Users/liudmilanemkova/Desktop/Pictures"
scrape_site(base_url, destination_folder)
