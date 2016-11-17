from bs4 import BeautifulSoup
import urllib2
import graphlab
from graphlab import SArray


class ImdbCrawler(object):
    """
        Crawler class
    """
    def __init__(self):
        self.movie = dict()
        self.movies_info = list()

    def crawl(self):
        """
            Requests data from imdb list and stores in self.movie_info
        """
        # request for pages in the list
        for i in range(1, 8001, 100):


            try:

                print("Requesting: {}".format(i))

                request = urllib2.urlopen('http://www.imdb.com/list/ls057823854/?start=' + str(i) +
                                      '&view=detail&sort=listorian:asc')

                # parse the response
                soup = BeautifulSoup(request.read(), 'html.parser')

                # get all the info classes
                info = soup.find_all("div", attrs={"class": "info"})

                # extract the data from the soup
                for index, _ in enumerate(info):

                    try:
                        # iterate through the movies and gather data
                        name = info[index].find_next("a").string
                        year = info[index].find_next("span").string
                        description = info[index].find_all("div", attrs={"class": "item_description"})[0].text
                        score = info[index].find_all("span", attrs={"class": "rating-rating"})[0].text
                        director = info[index].find_all("div", attrs={"class": "secondary"})[0].text
                        stars = info[index].find_all("div", attrs={"class": "secondary"})[1].text

                    # some scores don't have scores
                    except IndexError:
                        score = "N/A"

                    # define the dictionary
                    self.movie = {"name": name, "year": year, "director": director, "stars": stars, "score": score,
                                    "description": description}

                    # append the dictionaries to the full list of the movies
                    self.movies_info.append(self.movie)

                # delete the urllib and soup objects to reset
                del request
                del soup
                del info

            except urllib2.httplib.BadStatusLine:
                print("Restarting the Crawl() due to: {}".format(urllib2.httplib.BadStatusLine.message))
                self.crawl()

    def write_to_console(self):
        """
            Prints the movie list
        """
        for i, movie in enumerate(self.movies_info):
            print(i, movie)

    def write_to_frame(self):
        """
            Creates an SFrame object and exports it for use in a different framework
        """
        # define the lists
        names = list()
        directors = list()
        years = list()
        summaries = list()
        stars = list()

        # break the data into the lists
        for movie in self.movies_info:
            names.append(str(movie['name'].encode('ascii', 'ignore')))
            directors.append(str(movie['director'].replace("Director: ", "").encode('ascii', 'ignore')))
            years.append(str(movie['year'].encode('ascii', 'ignore')))
            summaries.append(str(movie['description'].encode('ascii', 'ignore')))
            stars.append(str(movie['stars'].replace("Stars: ", "").encode('ascii', 'ignore')))

        # create the SFrame object
        frame = graphlab.SFrame({'name': SArray(names), 'description': summaries,
                                 'director': directors, 'year': years, 'stars': stars})

        # save the SFrame
        frame.save('Imdb Data')

        print("Done Saving to SFrame")


def main():

    crawler = ImdbCrawler()
    crawler.crawl()
    crawler.write_to_frame()

if __name__ == "__main__":
    main()
