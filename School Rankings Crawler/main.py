import requests
from bs4 import BeautifulSoup
import pandas as pd


def main():

    # define the cities and pages lists
    cities = ["austin", "houston", "san-antonio", "dallas", "fort-worth"]
    pages = [31, 79, 44, 37, 23]

    for i, city in enumerate(cities):

        print("##### SCRAPING CITY: {} #####".format(city))

        # init
        schools = []
        addresses = []
        scores = []
        districts = []
        grades = []

        data = pd.DataFrame()

        # run the scrapper
        for page in range(1, pages[i]):

            print("- - READING PAGE: {} - -".format(page))

            url = "https://www.greatschools.org/texas/" + city + "/schools/?page=" + str(page)
            r = requests.get(url=url)
            soup = BeautifulSoup(r.text, 'html.parser')

            for school in soup.find_all(attrs={"class": "open-sans_sb mbs font-size-medium rs-schoolName"}):
                schools.append(school.text)

            for address in soup.find_all(attrs={"class": "hidden-xs font-size-small rs-schoolAddress"}):
                addresses.append(address.text)

            for score in soup.find_all(attrs={"class": "circle-rating--xtra-small"}):
                scores.append(score.text.strip())

            for grade in soup.find_all("div", class_="font-size-small mvm clearfix ptm hidden-xs"):

                if grade.text.strip().split('\n')[0] == 'No reviews: ':
                    grades.append(str(grade.text.strip().split('\n')[5]))
                    districts.append(grade.text.strip().split('\n')[4])

                    # print(grade.text.strip().split('\n')[5], grade.text.strip().split('\n')[4])

                else:
                    grades.append(str(grade.text.strip().split('\n')[4]))
                    districts.append(grade.text.strip().split('\n')[3])

                    # print(grade.text.strip().split('\n')[4], grade.text.strip().split('\n')[3])

        # fix the missing scores
        for _ in range(len(schools) - len(scores)):
            scores.append("N/A")

        # build the data frame
        data["school_name"] = schools
        data["address"] = addresses
        data["score"] = scores
        data["district"] = districts
        data["grade"] = grades

        # save to csv
        data.to_csv(city + "_schools.csv")


if __name__ == "__main__":
    main()
