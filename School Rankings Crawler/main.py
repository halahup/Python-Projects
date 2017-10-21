import requests
from bs4 import BeautifulSoup
import pandas as pd


def main():

    # init
    schools = []
    addresses = []
    scores = []
    grades = []

    data = pd.DataFrame()

    # run the scrapper
    for page in range(1, 31):

        print("- - READING PAGE: {} - -".format(page))

        url = "https://www.greatschools.org/texas/austin/schools/?page=" + str(page)
        r = requests.get(url=url)
        soup = BeautifulSoup(r.text, 'html.parser')

        for school in soup.find_all(attrs={"class": "open-sans_sb mbs font-size-medium rs-schoolName"}):
            schools.append(school.text)

        for address in soup.find_all(attrs={"class": "hidden-xs font-size-small rs-schoolAddress"}):
            addresses.append(address.text)

        for score in soup.find_all(attrs={"class": "circle-rating--xtra-small"}):
            scores.append(score.text.strip())

        for grade in soup.find_all("div", class_="font-size-small mvm clearfix ptm hidden-xs"):
            grades.append(' '.join(grade.text.strip().split('\n')[3:]))

    # fix the missing scores
    for _ in range(len(schools) - len(scores)):
        scores.append("N/A")

    # build the data frame
    data["school_name"] = schools
    data["address"] = addresses
    data["score"] = scores
    data["grade"] = grades

    # save to csv
    data.to_csv("texas_schools.csv")


if __name__ == "__main__":
    main()
