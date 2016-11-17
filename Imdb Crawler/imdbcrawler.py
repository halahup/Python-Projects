from bs4 import BeautifulSoup
import re
import urllib.request as url


class ImdbCrawler(object):

    pass


def main():

    movies_info = list()

    # for i in range(1, 301, 100):
    #     print(i)

    for i in range(1, 101, 100):
        request = url.urlopen('http://www.imdb.com/list/ls057823854/?start=' + str(i) +
                              '&view=detail&sort=listorian:asc')

        print('http://www.imdb.com/list/ls057823854/?start=' + str(i) + '&view=detail&sort=listorian:asc')

        soup = BeautifulSoup(request.read(), 'html.parser')
        info = soup.find_all("div", attrs={"class": "info"})

        # 0 is for the iterator over 100 movies in the loop
        name = info[0].find_next("a").string
        year = info[0].find_next("span").string
        description = info[0].find_all("div", attrs={"class": "item_description"})[0].text
        score = info[0].find_all("span", attrs={"class": "rating-rating"})[0].text

        print(info[0])


if __name__ == "__main__":
    main()
