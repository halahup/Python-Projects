#!/usr/local/bin/python2

from bs4 import BeautifulSoup
import urllib
import re
import datetime
import math
import csv


class Issue(object):

    def __init__(self, name="N/A", today_high="N/A", today_low="N/A", volume="N/A", fifty_two_vol="N/A",
                 fifty_low="N/A", fifty_high="N/A", market_cap="N/A", beta="N/A"):
        self.name = name
        self.today_high = today_high
        self.today_low = today_low
        self.volume = volume
        self.fifty_two_vol = fifty_two_vol
        self.fifty_low = fifty_low
        self.fifty_high = fifty_high
        self.market_cap = market_cap
        self.beta = beta


class NasdaqCrawler(object):

    _address = "http://www.nasdaq.com/symbol/"

    def __init__(self, tickers):
        """
            Initializes the NasdaqCrawler object
            Args:
                tickers: list of the tickers to fetch the data for
        """
        self.tickers = tickers

    def fetch_data(self):
        """
            Fetches data from http://www.nasdaq.com/symbol/TICKER
            Returns:
                list of issues initialized with:
                    name, today_high, today_low, volume, fifty_two_vol, fifty_low, fifty_high, market_cap, beta
        """

        # create the list for issues
        list_of_issues = list()

        # unpack the array of tickers
        for ticker in self.tickers:

            # fetch the data from NASDAQ
            request = urllib.urlopen(self._address + ticker)
            soup = BeautifulSoup(request.read(), 'html.parser')

            # Correction on Best Bid - Ask
            best_bid_ask = soup.find_all("a", attrs={"id": "best_bid_ask"})
            correction = 0
            if len(best_bid_ask) == 0:
                correction = -2

            # Get the stats for the stock
            # Today's High
            today_high = soup.find_all("label", attrs={"id": "Label3"})[0].string.replace(u'\xa0', '').\
                replace('$', '').encode('ascii')

            # Today's Low
            today_low = soup.find_all("label", attrs={"id": "Label1"})[0].string.replace(u'\xa0', '').\
                replace('$', '').encode('ascii')

            # Today's Volume
            volume_label_name = ticker.upper() + "_Volume"
            volume = soup.find_all("label", attrs={"id": "" + volume_label_name + ""})[0].string.replace(u'\xa0', '').\
                encode('ascii')

            # 52 week Volume average
            fifty_two_vol = soup.find_all("td")[35 + correction].string.replace(u'\xa0', '').encode('ascii')

            # 52 week high and low
            fifty_high_low = soup.find_all("td")[39 + correction].string.lstrip().rstrip().replace(u'\xa0', '').\
                encode('ascii')
            try:
                fifty_high = re.findall('\d+\.\d+', fifty_high_low)[0]
                fifty_low = re.findall('\d+\.\d+', fifty_high_low)[1]
            except IndexError:
                fifty_high = "N/A"
                fifty_low = "N/A"

            # Market Capacity
            market_cap = soup.find_all("td")[41 + correction].string.replace(u'\xa0', '').replace('$ ', '').\
                encode('ascii')

            # beta = soup.find_all("td")[57 + correction + special_dividend_correction].string.replace(u'\xa0', '').\
            #    encode('ascii')

            beta = soup.find_all("a", attrs={"id": "beta"})[0].parent.find_next("td").string.replace(u'\xa0', '').\
                replace('$ ', '').encode('ascii')

            # create the Issue instances and append to the issue list
            list_of_issues.append(Issue(name=ticker,
                                        today_high=today_high,
                                        today_low=today_low,
                                        volume=volume,
                                        fifty_two_vol=fifty_two_vol,
                                        fifty_high=fifty_high,
                                        fifty_low=fifty_low,
                                        market_cap=market_cap,
                                        beta=beta))

        # return the list of issues
        return list_of_issues


class DividendData(object):

    """
        Class to hold the data of the upcoming dividend of an issue
    """

    def __init__(self, name, ex_dividend_date, dividend_per_share, record_date, payment_date, price):

        self.name = name
        self.ex_dividend_date = ex_dividend_date
        self.dividend_per_share = dividend_per_share
        self.record_date = record_date
        self.payment_date = payment_date
        self.price = price


class DividendCrawler(object):

    _link_address = "http://www.nasdaq.com/dividend-stocks/dividend-calendar.aspx?date="

    @staticmethod
    def prepare_date(date_shift=0):
        """
            Takes current date and modifies the day to be of the next date, ex-dividend date

            Args:
                date_shift: shift for the date
            Returns:
                current date + 1 in string format
        """
        # get the current date
        current_year = datetime.datetime.now().date().year
        current_month = datetime.datetime.now().date().month

        # 30 vs 31 day months
        if current_month % 2 == 1:
            mod = 30
        else:
            mod = 31

        # if over the weekend the date goes over the month
        if datetime.datetime.now().date().day + 1 + date_shift > mod:

            # add the shift to the date and jump to the next month
            target_ex_dividend_day = (datetime.datetime.now().date().day + 1 + date_shift) % mod
            current_month = (datetime.datetime.now().date().month + 1) % 12

            # if the month rolls over to the next year
            if datetime.datetime.now().date().month + 1 > 12:

                # increment the year
                current_year += 1

        # the date didn't go over the month
        else:
            target_ex_dividend_day = datetime.datetime.now().date().day + 1 + date_shift

        # return the next day date in string format
        return datetime.date(year=current_year, month=current_month, day=target_ex_dividend_day).strftime("%Y-%b-%d")

    def fetch_dividend_schedule_data(self, date_shift=0):
        """
            Fetches data from 'http://www.nasdaq.com/dividend-stocks/dividend-calendar.aspx?date='
            with appended date specified as a next day from the request

            Args:
                date_shift: a shift for date for cases like request for saturday ex-dividend date

            Returns:
                A list of Issue objects
        """
        # Create request object
        request = urllib.urlopen(self._link_address + DividendCrawler.prepare_date(date_shift))
        print "Fetching : {}".format(self._link_address + DividendCrawler.prepare_date(date_shift))
        soup = BeautifulSoup(request.read(), 'html.parser')

        # define the lists
        list_of_issues = list()
        list_of_names = list()
        list_of_ex_dividend_dates = list()
        list_of_dividend_per_share = list()
        list_of_record_dates = list()
        list_of_payment_dates = list()

        # parse the data from the website
        for tr in soup.find_all('tr')[3:]:
            tds = tr.find_all('td')

            for index, element in enumerate(tds):
                if index == 0:
                    list_of_names.append(unicode(element.string).replace(u'\xa0', '').encode("ascii"))
                elif index == 1:
                    list_of_ex_dividend_dates.append(unicode(element.string).replace(u'\xa0', '').encode("ascii"))
                elif index == 2:
                    list_of_dividend_per_share.append(unicode(element.string).replace(u'\xa0', '').encode("ascii"))
                elif index == 3:
                    pass
                elif index == 4:
                    list_of_record_dates.append(unicode(element.string).replace(u'\xa0', '').encode("ascii"))
                elif index == 5:
                    pass
                elif index == 6:
                    list_of_payment_dates.append(unicode(element.string).replace(u'\xa0', '').encode("ascii"))

        # peal last 2 None objects from the list of the names
        list_of_names = list_of_names[:len(list_of_names) - 2]

        assert len(list_of_names) == len(list_of_ex_dividend_dates)

        # construct the list of Issue objects and return it
        for index in range(len(list_of_names)):

            list_of_issues.append(
                DividendData(name=list_of_names[index],
                             ex_dividend_date=list_of_ex_dividend_dates[index],
                             payment_date=list_of_payment_dates[index],
                             dividend_per_share=list_of_dividend_per_share[index],
                             record_date=list_of_record_dates[index],
                             price=DividendCrawler.fetch_price_of_issue(list_of_names[index])))

        return list_of_issues

    @staticmethod
    def extract_ticker(issue_name):
        """
            Extracts the ticker from the dividend schedule string
            Args:
                Name of the issue taken from the list of the dividend schedule
            Returns:
                ticker; i.e. FB
        """
        index = issue_name.find("(") + 1
        issue_name_list = list(issue_name)
        issue_name_list[index - 1] = " "
        issue_name = "".join(issue_name_list)
        secondary_index = issue_name.find("(") + 1

        if secondary_index != 0:
            return issue_name[secondary_index:len(issue_name) - 1]

        else:
            return issue_name[index:len(issue_name) - 1]

    @staticmethod
    def fetch_price_of_issue(issue_name):
        """
            Fetches the price of the desired issue
            Args:
                issue_name: TICKER of the issue
            Returns:
                price of the issue as string
        """
        # extract the ticker
        ticker = DividendCrawler.extract_ticker(issue_name)

        # request for the data
        request = urllib.urlopen("http://www.nasdaq.com/symbol/" + ticker)
        soup = BeautifulSoup(request.read(), 'html.parser')

        if len(soup.find_all("div", {"class": "qwidget-dollar"})) != 0:
            return soup.find_all("div", {"class": "qwidget-dollar"})[0].string
        else:

            # if no price specified return 0 to raise the zero division exception
            return 0


def main():

    date_shift = 0

    # Instantiate the dividend schedule crawler and fetch the schedule for tomorrow
    dividend_crawler = DividendCrawler()
    dividend_candidates = []

    # if the candidates list is empty -> add 1 to the date
    while len(dividend_candidates) == 0:
        dividend_candidates = dividend_crawler.fetch_dividend_schedule_data(date_shift)
        date_shift += 1

    # if the candidates list is not empty
    # get the list of tickers from the schedule
    list_of_tickers = list()
    for issue in dividend_candidates:
        list_of_tickers.append(DividendCrawler.extract_ticker(issue.name))

    # instantiate the general crawler and fetch the data on every issue in the dividend schedule
    crawler = NasdaqCrawler(list_of_tickers)
    issues = crawler.fetch_data()

    # print the date
    print "###################################"
    print "| Ex-Dividend Date: ", DividendCrawler.prepare_date(date_shift - 1), " |"
    print "###################################"

    # print the data
    print "TICKER | Today High | Today Low | Today Volume | 52 wk Volume | 52 wk High | 52 wk Low |" + \
          " Beta | Dividend | One Day Yield | Market Capital. |"

    print "========================================================================================" + \
          "===================================================="

    with open("{}.csv".format(DividendCrawler.prepare_date(date_shift - 1)), "w") as csvfile:
        writer = csv.writer(csvfile)

        # header
        writer.writerow(["name", "today_high", "today_low", "today_volume", "52_wk_volume", "52_wk_high", "52_wk_low",
                         "market_cap", "beta", "dividend_per_share", "one_day_yield"])

        for index, issue in enumerate(issues):

            # Some issues don't have price to them so we return 0 from the price fetching method
            # To avoid the zero division error we use try except statement
            try:
                one_day_yield = math.ceil((float(dividend_candidates[index].dividend_per_share) /
                                           float(dividend_candidates[index].price.replace('$', '')) * 100) * 100) / 100
            except ZeroDivisionError:
                one_day_yield = "N/A"

            # print the data
            print "{0:^6} {1:^15} {2:^10} {3:^13} {4:^15} {5:^12} {6:^12} {8:^5} {9:^9} {10:^15} {7:^20}".\
                format(issue.name, issue.today_high, issue.today_low, issue.volume,
                       issue.fifty_two_vol, issue.fifty_high, issue.fifty_low,
                       issue.market_cap, issue.beta,
                       dividend_candidates[index].dividend_per_share,
                       one_day_yield)

            # write the csv file
            data = [issue.name, issue.today_high, issue.today_low, issue.volume, issue.fifty_two_vol,
                    issue.fifty_high, issue.fifty_low, issue.market_cap, issue.beta,
                    dividend_candidates[index].dividend_per_share, one_day_yield]
            writer.writerow(data)

    # feedback
    print("Data written to CSV")

    # TODO: Calculate the 52 wk Spread between 52 wk high and 52 wk low
    return 0

if __name__ == "__main__":
    main()
