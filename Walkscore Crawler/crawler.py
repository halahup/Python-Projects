import urllib.request
from bs4 import BeautifulSoup
import re


class Crawler:

    def __init__(self, city, state):
        self.city = city
        self.state = state
        self.url = "https://www.walkscore.com/apartments/featured/" + state + "/" + city
        self.soup = None

    def crawl(self):

        data = list()

        for page in range(1, 32):

            # request the page
            if page == 1:
                request = urllib.request.urlopen(self.url)

            else:
                request = urllib.request.urlopen(self.url + "/p" + str(page))

            print("PROCESSING PAGE ", page)

            # parse the page
            self.soup = BeautifulSoup(request.read(), 'html.parser')

            # listings on the page
            listings = self.soup.find_all("div", attrs={"class": "listing-wrap"})

            # print(listings)

            for listing in listings:

                # price
                price_html = listing.find_all("div", attrs={"class": "price"})

                # if "Contact" instead of price - set price as n/a
                if "Contact" in price_html[0].text:
                    price = "N/A"

                elif "from" not in price_html[0].text and "Contact" not in price_html[0].text:
                    price = listing.find_all("div", attrs={"class": "price"})[0].text.lstrip().rstrip()

                else:
                    price = listing.find_all("div", attrs={"class": "price"})[0].text[7:].rstrip()

                # names
                try:
                    name = listing.find_all("div", attrs={"class": "name"})[0].text.lstrip().rstrip()
                except IndexError:
                    name = "N/A"

                # walkscore
                try:
                    walkscore = listing.find_all("div", attrs={"class": "walk-score"})[0].text[10:].lstrip().rstrip()
                except IndexError:
                    walkscore = "N/A"

                entry = {"name": name, "price": price, "walkscore": walkscore}

                data.append(entry)

        print(data)


def main():

    crawler = Crawler("Austin", "TX")
    crawler.crawl()

    pass


if __name__ == "__main__":
    main()