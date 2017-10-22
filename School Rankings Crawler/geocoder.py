import requests
import pandas as pd


def main():
    cities = ["san-antonio", "dallas", "fort-worth"]
    url = 'https://maps.googleapis.com/maps/api/geocode/json'

    for city in cities:

        print(" ##### CITY: {} #####".format(city))

        data = pd.read_csv(city + "_schools.csv")
        addresses = data["address"]
        latitudes = []
        longitudes = []

        for address in addresses:
            try:
                print("PARSING: {}".format(address))

                params = {'sensor': 'false', 'address': address}
                r = requests.get(url, params=params)
                results = r.json()['results']
                location = results[0]['geometry']['location']
                latitudes.append(location['lat'])
                longitudes.append(location['lng'])

            except IndexError:
                longitudes.append("N/A")
                latitudes.append("N/A")

        data["lat"] = latitudes
        data["long"] = longitudes

        data.to_csv(city + "_schools.csv")


if __name__ == "__main__":
    main()
