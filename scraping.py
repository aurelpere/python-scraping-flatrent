#!/usr/bin/python3
# coding: utf-8
"""
this is scraping.py
"""
import datetime
import argparse
import re
import random
import html
import matplotlib.pyplot as plt
import seaborn as sns
import bs4
import pandas as pd
import requests

header1 = {'Connection':'close',
            "Accept":
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Encoding":
            "gzip, deflate, br",
            "Accept-Language":
            "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
            "Host":
            "www.wg-gesucht.de",
            "Sec-Fetch-Dest":
            "document",
            "Sec-Fetch-Mode":
            "navigate",
            "Sec-Fetch-Site":
            "cross-site",
            "Te":
            "trailers",
            "Upgrade-Insecure-Requests":
            "1",
            "User-Agent":
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0",}
header2 = {'Connection':'close',
           "Accept":
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding":
            "gzip, deflate, br",
            "Accept-Language":
            "fr-fr",
            "Host":
            "www.wg-gesucht.de",
            "User-Agent":
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 \
             (KHTML, like Gecko) Version/15.1 Safari/605.1.15",}
header3 = {'Connection':'close',
           "Accept":
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/\
             avif,image/webp,image/apng,*/*;q=0.8,application/\
             signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Device-Memory": "8",
            "Downlink": "1.5",
            "Dpr": "1",
            "Ect": "4g",
            "Host": "www.wg-gesucht.de",
            "Rtt": "100",
            "Sec-Ch-Prefers-Color-Scheme": "light",
            "Sec-Ch-Ua":
            '"Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96',
            "Sec-Ch-Ua-Arch": '"x86"',
            "Sec-Ch-Ua-Full-Version": '"96.0.4664.45"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Model": '""',
            "Sec-Ch-Ua-Platform": '"macOS"',
            "Sec-Ch-Ua-Platform-Version": '"10.15.7"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent":
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 \
                 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
            "Viewport-Width": "1280",}

headerlist = [header1, header2, header3]

dict_neighborhoods = {"Kreuzberg": "151",
                        "Charlottenburg": "126",
                        "Wilmersdorf": "192",
                        "Friedrichshain": "132",
                        "Lichtenberg": "153",
                        "Marzahn": "162",
                        "Hellersdorf": "139",
                        "Mitte": "163",
                        "Neukölln": "165",
                        "Pankow": "170",
                        "Reinickendorf": "173",
                        "Spandau": "180",
                        "Steglitz": "181",
                        "Zehlendorf": "194",
                        "Tempelhof": "183",
                        "Schöneberg": "178",
                        "Treptow": "185",
                        "Köpenick": "150",}
list_neighborhoods = ["Kreuzberg",
                        "Charlottenburg",
                        "Friedrichshain",
                        "Mitte",
                        "Neukölln",
                        "Pankow",
                        "Schöneberg",]
# 'Tempelhof','Spandau,Wilmersdorf','Marzahn', 'Hellersdorf','Köpenick','Treptow',
# 'Steglitz','Zehlendorf','Reinickendorf','Lichtenberg'

listsocks5=['213.152.176.251',
            '196.247.50.59',
            '165.231.210.171',
            '66.151.209.203',
            '109.202.99.35',
            '185.236.42.34',
            '185.236.42.42',
            '196.196.232.3',]

class Static():
    "static methods class"
    @staticmethod
    def process_response(response):
        "process response with bs4 from request call"
        soup = bs4.BeautifulSoup(response.text, features="html.parser")
        souplist = soup.find_all(attrs={"class": "col-xs-3"})
        souptxt=''
        for soupitem in souplist:
            souptxt += html.unescape(str(soupitem))
        list1 = re.findall(r"(?<=<b>)(\d{2,4})(?=\s€)", souptxt)
        list2 = re.findall(r"(?<=<b>)(\d{2,4})(?=\sm²)", souptxt)
        return (list1, list2)

    @staticmethod
    def plot_dataframes(dataframe):
        "plot dataframes with seaborn"
        bplot = sns.boxplot(width=0.5, data=dataframe)
        bplot.set_xlabel("neighborhood of Berlin", fontsize=14)
        bplot.set_ylabel("price in €/m2", fontsize=14)
        bplot.tick_params(labelsize=10)
        return plt.show()

class ScrapingBerlinRent():
    "scraping flat rent of Berlin object"

    def __init__(self, neighborhoodlist, comparelist=False):
        "init"
        self.neighborhoodlist = list(neighborhoodlist)
        if comparelist:
            for neighborhood in list_neighborhoods:
                # pylint: disable=expression-not-assigned
                self.neighborhoodlist.append(
                    neighborhood
                ) if neighborhood not in self.neighborhoodlist else self.neighborhoodlist
        self.neighborhood = self.neighborhoodlist[0]
        self.surf_table = []
        self.price_table = []
        self.page_nb = 0
        self.start_url = "https://www.wg-gesucht.de/wohnungen-in-Berlin.8.2.1."
        self.middle_url = ".html?offer_filter=1&city_id=8&noDeact=1&categories%5B%5D=2&rent_types%5B%5D=0&ot%5B%5D="
        self.url_to_get = f'{self.start_url}{self.page_nb}{self.middle_url}{dict_neighborhoods[self.neighborhood]}'
        self.start = None
        self.proc = None

    def initialisation(self):
        "print start of scraping process"
        self.start = datetime.datetime.now()
        self.surf_table = []
        self.price_table = []
        print("-- Initialisation --")
        print(f"neighborhood: {self.neighborhood}")

    def end(self):
        "print end of scraping process"
        # TEMPS PASSE
        self.page_nb = 0
        endtime = datetime.datetime.now()
        time_elapsed = str(endtime - self.start)
        print("\n")
        print("-- TIME ELAPSED --")
        print(time_elapsed)

    def process_lists(self, list1, list2):
        "process lists obtained from soup"
        if len(list1) == len(list2):
            self.surf_table.extend(list2)
            self.price_table.extend(list1)
            self.page_nb += 1
            self.url_to_get = f'{self.start_url}{self.page_nb}{self.middle_url}{dict_neighborhoods[self.neighborhood]}'
            print(self.url_to_get)
        else:
            print("listes de longueurs differentes")

    def scrape_price_surface(self, neighborhood):
        """
        Export all prices and surface from a neighborhood(neighborhood) www.wg-gesucht.de,
        neighborhood is a string
        Return a tuple of the list of price and the list of surface
        """
        self.neighborhood = neighborhood
        #INITIALISATION
        self.initialisation()
        # CRAWLING ET PARSEING
        while len(self.price_table) < 84:
            with open('._','r',encoding='utf-8') as fileo:
                credentials=fileo.readlines()
                credentials0=credentials[0].strip("\n").strip(' ')
                credentials1=credentials[1].strip("\n").strip(' ')
            header=random.choice(headerlist)
            socks5 = random.choice(listsocks5)
            proxy = {'http': f'socks5h://{credentials0}:{credentials1}@{socks5}:1080',
                       'https': f'socks5h://{credentials0}:{credentials1}@{socks5}:1080'}
            req = requests.session()
            # pylint: disable=no-member
            retry = requests.packages.urllib3.util.retry.Retry(connect=3, backoff_factor=0.5)
            adapter = requests.adapters.HTTPAdapter(max_retries=retry)
            req.mount('http://', adapter)
            req.mount('https://', adapter)
            req.headers['Connection'] = 'close'
            try:
                response = req.get(url=self.url_to_get, headers=header,proxies=proxy)
            except Exception as err:
                print (err)
                print (f'proxy en question : {socks5}')
            (list1, list2) = Static.process_response(response)
            req.close()
            if response.status_code == 200:
                print(f"Page: {self.page_nb}")
                self.process_lists(list1, list2)
            else:
                print(f"Page #{self.page_nb} : inaccessible")
        self.end()
        return (self.price_table, self.surf_table)

    def compute(self):
        "plot the results"
        print(self.neighborhoodlist)
        listdf = []
        for neighborhood in self.neighborhoodlist:
            data = self.scrape_price_surface(neighborhood)
            df0 = pd.DataFrame({"prix": data[0], "surf": data[1]})
            df0["prix"] = df0["prix"].astype("float64")
            df0["surf"] = df0["surf"].astype("float64")
            df0[neighborhood] = df0["prix"] / df0["surf"]
            df0 = df0.drop(["prix", "surf"], axis=1)
            listdf.append(df0)
        result = pd.concat(listdf)
        result = result.rename_axis("pricem", axis=0)
        result = result.rename_axis("neighborhood", axis="columns")
        return result

    def computeandplot(self):
        "compute and plot"
        Static.plot_dataframes(self.compute())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
        python scraping.py -q neighborhood1 neighborhood2 --compare
        """)

    parser.add_argument('-n',
                        '--neighborhood',
                        required=False,
                        default=('Kreuzberg',),
                        nargs="*",
                        metavar='neighborhood',
                        type=str,
                        help='Berlin neighborhoods to scrape eg -q Kreuzberg')
    parser.add_argument('-c',
                        '--compare',
                        action='store_true',
                        required=False,
                        default=False,
                        help='''if you want to compare the scraped neighborhood to
                                a set of other neighborhoods included in the script
                                eg python scraping.py -q Kreuzberg --compare''')

    arguments = vars(parser.parse_args())
    ScrapingBerlinRent(tuple(arguments['neighborhood']),
                        arguments['compare']).computeandplot()
