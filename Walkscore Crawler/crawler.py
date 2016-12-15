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

                # feedback for the user
                print("PROCESSING PAGE ", page)

                # parse the page
                self.soup = BeautifulSoup(request.read(), 'html.parser')

                # listings on the page
                listings = self.soup.find_all("div", attrs={"class": "listing-wrap"})

                # make sure we haven't reached the end of the pages
                assert len(listings) != 0

                # for every listing
                for listing in listings:

                    # price
                    price_html = listing.find_all("div", attrs={"class": "price"})

                    # if "Contact" instead of price - set price as n/a
                    if "Contact" in price_html[0].text:
                        price = "N/A"

                    # also if the price field doesn't include "from" - just strip
                    elif "from" not in price_html[0].text and "Contact" not in price_html[0].text:
                        price = listing.find_all("div", attrs={"class": "price"})[0].text.lstrip().rstrip()

                    # if there is "from" - cut the string and strip
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
                        beds = "N/A"

                    # create the data frame
                    entry = {"name": name, "price": price, "walkscore": walkscore, "beds": beds}

                    # append the entries to the list
                    self.data.append(entry)

            # reached the end of the pages
            except AssertionError:

                # feedback
                print("{} pages has been scraped for {}".format(page, self.city.upper()))

                # save the CSV
                self.save_csv()
                return

            # no such page on the walkscore.com
            except urllib.error.HTTPError:
                print("No such city on walkscore.com or city/state is misspelled")
                return

    def save_csv(self):
        """
            Writes the data into the csv
        """
        with open("{}_{}.csv".format(self.city.upper(), self.state.upper()), "w", newline='') as csvfile:
            writer = csv.writer(csvfile)

            # header
            writer.writerow(["Name", "Price", "Walkscore", "Beds"])

            # write the data
            for entry in self.data:
                data = [entry["name"], entry["price"], entry["walkscore"], entry["beds"]]
                writer.writerow(data)

        # feedback
        print("Data written to CSV")


def main():

    # call 1 word city: python3 crawler.py Austin, TX
    # call 2 word cities: python3 crawler.py New_York, NY
    assert len(sys.argv) == 3

    # initialize the crawler
    crawler = Crawler(sys.argv[1], sys.argv[2])

    # launch
    crawler.crawl()

if __name__ == "__main__":
    main()
