from bs4 import BeautifulSoup
import urllib
import datetime
import math


class Issue(object):

    """
        Class to hold the issue of the upcoming dividend
    """

    def __init__(self, name, ex_dividend_date, dividend_per_share, record_date, payment_date, price):

        self.name = name
        self.ex_dividend_date = ex_dividend_date
        self.dividend_per_share = dividend_per_share
        self.record_date = record_date
        self.payment_date = payment_date
        self.price = price


class Crawler(object):

    _link_address = "http://www.nasdaq.com/dividend-stocks/dividend-calendar.aspx?date="

    @staticmethod
    def prepare_date():  # type: () -> str

        """
            Takes current date and modifies the day to be of the next date, ex-dividend date

            Returns:
                current date + 1 in string format
        """

        # get the current date
        current_year = datetime.datetime.now().date().year
        current_month = datetime.datetime.now().date().month

        # add 1 to the day of the date
        target_ex_dividend_day = datetime.datetime.now().date().day + 4

        # return the next day date in string format
        return datetime.date(year=current_year, month=current_month, day=target_ex_dividend_day).strftime("%Y-%b-%d")

    def fetch_dividend_schedule_data(self):

        # TODO: Fetch beta for the individual stocks to estimate the volatility

        """
            Fetches data from 'http://www.nasdaq.com/dividend-stocks/dividend-calendar.aspx?date='
            with appended date specified as a next day from the request

            Returns:
                A list of Issue objects
        """

        # Create request object
        request = urllib.urlopen(self._link_address + Crawler.prepare_date())
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
                Issue(name=list_of_names[index],
                      ex_dividend_date=list_of_ex_dividend_dates[index],
                      payment_date=list_of_payment_dates[index],
                      dividend_per_share=list_of_dividend_per_share[index],
                      record_date=list_of_record_dates[index],
                      price=Crawler.fetch_price_of_issue(list_of_names[index])))

        return list_of_issues

    @staticmethod
    def extract_ticker(issue_name):

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

        ticker = Crawler.extract_ticker(issue_name)

        request = urllib.urlopen("http://www.nasdaq.com/symbol/" + ticker)
        soup = BeautifulSoup(request.read(), 'html.parser')

        return soup.find_all("div", {"class": "qwidget-dollar"})[0].string


def main():

    basic_crawler = Crawler()
    issues = basic_crawler.fetch_dividend_schedule_data()

    for issue in issues:

        print '{:<50}  {:<7}  {:<5}  {:<0}   {:<0}'.format(issue.name,
                                                           issue.price,
                                                           math.ceil((float(issue.dividend_per_share) /
                                                                      float(issue.price.replace('$', '')) * 100) * 100) / 100,
                                                           issue.ex_dividend_date,
                                                           issue.record_date)

    # print list_of_prices

    return 0

main()
