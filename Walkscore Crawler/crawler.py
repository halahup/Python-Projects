import urllib.request

def main():

    url = "https://www.walkscore.com/apartments/featured/"
    city = "TX/Austin"

    request = urllib.request.Request(url + city)
    print(request.data)

    pass


if __name__ == "__main__":
    main()