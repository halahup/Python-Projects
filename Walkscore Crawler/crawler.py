import urllib.request
from bs4 import BeautifulSoup
import re
import csv
import sys


class Crawler:
    """
        Crawles out to walkscore.com and scraps the data about complexes
    """
    def __init__(self, city, state):
        self.city = city
        self.state = state
        self.url = "https://www.walkscore.com/apartments/featured/" + state.upper() + "/" + city
        self.soup = None
        self.data = None

    @staticmethod
    def get_list_of_cities():
        request = urllib.request.urlopen("https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population")
        soup = BeautifulSoup(request.read(), "html.parser")
        cities = soup.find_all("table")[3].find_all("td", attrs={"align": "left"})

        for i in range(0, 608, 2):
            city = cities[i].text.lstrip()
            # state = cities[i+1].text.lstrip()
            print(city)

    def crawl(self):

        # TODO: scrap the number of bedrooms

        # header
        print("city: {}, state: {}".format(self.city.upper(), self.state.upper()))

        self.data = list()

        for page in range(1, 1000):

            try:
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

                assert len(listings) != 0

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

                    # beds
                    try:
                        beds = listing.find_all("div", attrs={"class": "beds"})[0].text.lstrip().rstrip()

                    except IndexError:
                        print("Error")

                    entry = {"name": name, "price": price, "walkscore": walkscore, "beds": beds}

                    self.data.append(entry)

            # reached the end of the pages
            except AssertionError:
                print("{} pages has been scraped for {}".format(page, self.city.upper()))

                # save the CSV
                self.save_csv()
                return

            except urllib.error.HTTPError:
                print("No such city on walkscore.com or city/state is misspelled")
                return

    def save_csv(self):
        """
            Writes the data into the csv
        """
        with open("{}_{}.csv".format(self.city.upper(), self.state.upper()), "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Name", "Price", "Walkscore", "Beds"])
            for entry in self.data:
                data = [entry["name"], entry["price"], entry["walkscore"], entry["beds"]]
                writer.writerow(data)

        print("Data written to CSV")


def main():

    # call 1 word city: python3 crawler.py Austin, TX
    # call 2 word cities: python3 crawler.py New_York, NY
    assert len(sys.argv) == 3

    # initialize the crawler
    crawler = Crawler(sys.argv[1], sys.argv[2])

    # launch
    crawler.crawl()

    # Crawler.get_list_of_cities()


if __name__ == "__main__":
    main()
