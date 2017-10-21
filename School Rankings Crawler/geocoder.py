import requests
import pandas as pd


def main():
    url = 'https://maps.googleapis.com/maps/api/geocode/json'

    data = pd.read_csv("texas_schools.csv")
    addresses = data["address"]
    locations = []

    for address in addresses:
        try:
            print("PARSING: {}".format(address))

            params = {'sensor': 'false', 'address': address}
            r = requests.get(url, params=params)
            results = r.json()['results']
            location = results[0]['geometry']['location']
            locations.append("({},{})".format(location['lat'], location['lng']))

        except IndexError:
            locations.append("N/A")

    data["location"] = locations
    data.to_csv("texas_schools.csv")


if __name__ == "__main__":
    main()
