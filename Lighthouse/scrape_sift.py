import requests
from bs4 import BeautifulSoup


def main():
    r = requests.get('https://foc.justsift.com/search')

    soup = BeautifulSoup(r.text, 'html.parser')

    print(soup.prettify())

    images = soup.find_all('img')
    print(len(images))
    return 0

if __name__ == "__main__":
    main()