#!/usr/bin/python3
# coding: utf-8

import requests
import bs4
import pandas as pd

import datetime
import argparse
import re
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import time
import random
import os
import subprocess
import multiprocessing

def listFiles(folder):
    'la fonction listFiles renvoie une liste des fichiers du répertoire folder'
    os.chdir(folder)
    files=[]
    a=os.listdir()
    b=[]
    for i in a:
        if os.path.isfile(i):
            files.append(i)
        else:
            b.append(i)
    return files
header1={
"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
"Accept-Encoding":"gzip, deflate, br",
"Accept-Language":"fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
"Host":"www.wg-gesucht.de",
"Sec-Fetch-Dest":"document",
"Sec-Fetch-Mode":"navigate",
"Sec-Fetch-Site":"cross-site",
"Te":"trailers",
"Upgrade-Insecure-Requests":"1",
"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0"}
header2={
"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
"Accept-Encoding":"gzip, deflate, br",
"Accept-Language":"fr-fr",
"Host":"www.wg-gesucht.de",
"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15"
}
header3={
"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
"Accept-Encoding":"gzip, deflate, br",
"Accept-Language":"fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
"Device-Memory":"8",
"Downlink":"1.5",
"Dpr":"1",
"Ect":"4g",
"Host":"www.wg-gesucht.de",
"Rtt":"100",
"Sec-Ch-Prefers-Color-Scheme":"light",
"Sec-Ch-Ua": '"Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96',
"Sec-Ch-Ua-Arch":'"x86"',
"Sec-Ch-Ua-Full-Version":'"96.0.4664.45"',
"Sec-Ch-Ua-Mobile":"?0",
"Sec-Ch-Ua-Model":'""',
"Sec-Ch-Ua-Platform":'"macOS"',
"Sec-Ch-Ua-Platform-Version":'"10.15.7"',
"Sec-Fetch-Dest":"document",
"Sec-Fetch-Mode":"navigate",
"Sec-Fetch-Site":"cross-site",
"Sec-Fetch-User":"?1",
"Upgrade-Insecure-Requests":"1",
"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
"Viewport-Width":"1280"
}

headerlist=[header1,header2,header3]
dict_quartiers = {'Kreuzberg': '151', 'Charlottenburg': '126', 'Wilmersdorf': '192', 'Friedrichshain': '132',
                  'Lichtenberg': '153', 'Marzahn': '162', 'Hellersdorf': '139', 'Mitte': '163', 'Neukölln': '165',
                  'Pankow': '170', 'Reinickendorf': '173', 'Spandau': '180', 'Steglitz': '181', 'Zehlendorf': '194',
                  'Tempelhof': '183', 'Schöneberg': '178', 'Treptow': '185', 'Köpenick': '150'}
list_quartiers= ['Kreuzberg', 'Charlottenburg', 'Friedrichshain', 'Mitte', 'Neukölln',
                  'Pankow', 'Schöneberg']#Tempelhof,Spandau,Wilmersdorf,'Marzahn', 'Hellersdorf','Köpenick','Treptow','Steglitz','Zehlendorf','Reinickendorf','Lichtenberg'
listvpn=listFiles('/Users/macbook/Downloads/ovpn/ovpn_tcp')
r = re.compile("^de.*")
listvpnde = list(filter(r.match, listvpn))

def startvpn():
    vpn = random.choice(listvpnde)
    os.system("openvpn --config /Users/macbook/Downloads/ovpn/ovpn_tcp/"+vpn+" --auth-user-pass /Users/macbook/Downloads/login.conf --verb 0")

def compute_avg_price(quartier):
    """
    Export all prices and surface from a neighborhood(quartier) www.wg-gesucht.de,
    quartier is a string
    Return a tuple of the list of price and the list of surface
    """

    # INITIALISATION
    print('-- Initialisation --')
    print('quartier: {}'.format(quartier))
    start = datetime.datetime.now()
    price_table = []
    surf_table=[]
    base_url = 'https://www.wg-gesucht.de/wohnungen-in-Berlin.8.2.1.'
    page_nb = 0
    url_to_get = base_url + "{}".format(page_nb)+".html?offer_filter=1&city_id=8&noDeact=1&categories%5B%5D=2&rent_types%5B%5D=0&ot%5B%5D={}".format(dict_quartiers[quartier])

    patterne="(?<=\<b\>)(\d{2,4})(?=\s€)"

    patternm="(?<=\<b\>)(\d{2,4})(?=\sm²)"
    # CRAWLING ET PARSEING
    while len(price_table) < 75:
        header=random.choice(headerlist)
#        command=["openvpn","--config","/Users/macbook/Downloads/ovpn/ovpn_tcp/"+vpn,"--auth-user-pass","/Users/macbook/Downloads/login.conf","--verb","0"]
#        p = subprocess.Popen(command)
        p=multiprocessing.Process(target=startvpn)
        time.sleep(5)
        p.start()
        time.sleep(10)
        r = requests.session()
        response = r.get(url=url_to_get,headers=header)
        if response.status_code == 200:
            print('Page: {}'.format(page_nb))
            soup = bs4.BeautifulSoup(response.text, features='html.parser')
            souplist = soup.find_all(attrs={"class": "col-xs-3"})
            souptxt=''
            for i in souplist:
                souptxt+=str(i)
            list1=re.findall(patterne,souptxt)
            list2=re.findall(patternm,souptxt)
            if len(list1)==len(list2):
                surf_table.extend(list2)
                price_table.extend(list1)
                page_nb += 1
                url_to_get = base_url + "{}".format(page_nb) + ".html?offer_filter=1&city_id=8&noDeact=1&categories%5B%5D=2&rent_types%5B%5D=0&ot%5B%5D={}".format(dict_quartiers[quartier])
                print(url_to_get)
                print(surf_table)
                p.terminate()
                time.sleep(5)
            else:
                print('listes de longueurs differentes')
                p.terminate()
                time.sleep(5)
                break

        else:
            print('Page #{} : inaccessible'.format(page_nb))
            p.terminate()
            time.sleep(5)
            break
        p.terminate()
        time.sleep(5)
    p.terminate()
    time.sleep(5)
    # TEMPS PASSE
    end = datetime.datetime.now()
    time_elapsed = str(end - start)
    print('\n')
    print('-- TIME ELAPSED --')
    print(time_elapsed)
    return (price_table,surf_table)

# Pandas
if __name__ == "__main__":
    listdf=[]
    for i in list_quartiers:
        data=compute_avg_price(i)
        df=pd.DataFrame({'prix': data[0], 'surf': data[1]})
        df['prix']=df['prix'].astype('float64')
        df['surf']=df['surf'].astype('float64')
        df[i]=df['prix']/df['surf']
        df=df.drop(['prix','surf'],axis=1)
        listdf.append(df)
    result=pd.concat(listdf)
    result = result.rename_axis("pricem",axis=0)
    result = result.rename_axis("quartier",axis="columns")
    bplot=sns.boxplot(width=0.5, data=result )
    bplot.set_xlabel("quartier de Berlin",fontsize=14)
    bplot.set_ylabel("prix en €/m2",fontsize=14)
    bplot.tick_params(labelsize=10)
    plt.show()


