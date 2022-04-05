#!/usr/bin/python3
# coding: utf-8
"""
this is test_scraping.py
"""
import sys
import io
import matplotlib
import matplotlib.pyplot as plt
import requests
from scraping import Static
from scraping import ScrapingBerlinRent
import pytest
matplotlib.use("Agg")

def test_process_response():
    "process response with bs4 from request call"
    start_url = "https://www.wg-gesucht.de/wohnungen-in-Berlin.8.2.1."
    middle_url = ".html?offer_filter=1&city_id=8&noDeact=1&categories\
                  %5B%5D=2&rent_types%5B%5D=0&ot%5B%5D="
    url_to_get = f'{start_url}0{middle_url}151'
    # https://github.com/getsentry/responses#id4
    response = requests.get(url_to_get)
    mockedcontent='<div class="col-xs-3"><b>220 €</b></div><div class="col-xs-3 text-right"><b>57 m²</b></div>'.encode('utf-8')
    # pylint: disable=protected-access
    response._content=mockedcontent
    list1, list2 = Static.process_response(response)
    assert '220' in list1
    assert '57' in list2

def test_classscrapingberlinrent():
    "test ScrapingBerlinRent class"
    test = ScrapingBerlinRent(['Charlottenburg'])
    assert test.neighborhoodlist == ['Charlottenburg']
    assert test.neighborhood == 'Charlottenburg'
    assert not test.surf_table
    assert not test.price_table
    assert test.page_nb == 0
    assert test.start_url == "https://www.wg-gesucht.de/wohnungen-in-Berlin.8.2.1."
    assert test.middle_url == ".html?offer_filter=1&city_id=8&noDeact=1&categories%5B%5D=2&rent_types%5B%5D=0&ot%5B%5D="
    assert test.url_to_get == f'{test.start_url}{test.page_nb}{test.middle_url}126'
    assert test.start is None
    assert test.proc is None
    test2 = ScrapingBerlinRent(['Kreuzberg'], True)
    assert test2.neighborhoodlist == [  "Kreuzberg",
                                        "Charlottenburg",
                                        "Friedrichshain",
                                        "Mitte",
                                        "Neukölln",
                                        "Pankow",]
                                        #"Schöneberg",]
    test3 = ScrapingBerlinRent(['Tempelhof'], True)
    assert test3.neighborhoodlist == [  "Tempelhof","Kreuzberg", "Charlottenburg",
                                        "Friedrichshain", "Mitte", "Neukölln",
                                        "Pankow",] #"Schöneberg",]

def test_initialisation():
    "test initialisation function"
    test = ScrapingBerlinRent(['Kreuzberg'])
    captured_output = io.StringIO()
    sys.stdout = captured_output
    test.initialisation()
    sys.stdout = sys.__stdout__
    print(captured_output.getvalue())
    assert "-- Initialisation --" in captured_output.getvalue()
    assert "neighborhood: Kreuzberg" in captured_output.getvalue()

def test_end():
    "test end function"
    test = ScrapingBerlinRent(['Kreuzberg'])
    test.initialisation()
    captured_output = io.StringIO()
    sys.stdout = captured_output
    test.end()
    sys.stdout = sys.__stdout__
    print(captured_output.getvalue())
    assert "-- TIME ELAPSED --" in captured_output.getvalue()

def test_process_lists():
    "test process_lists function"
    test = ScrapingBerlinRent(['Kreuzberg'])
    list1 = ['100']
    list2 = ['50']
    test.process_lists(list1, list2)
    assert test.surf_table == ['50']
    assert test.price_table == ['100']
    assert test.page_nb == 1
    assert test.url_to_get == f'{test.start_url}1{test.middle_url}151'

def test_scrape_price_surface():
    "test of scrape_price_surface function"
    test = ScrapingBerlinRent(['Kreuzberg'])
    test_kreuzberg = test.scrape_price_surface('Kreuzberg')
    assert isinstance(test_kreuzberg[0], list)
    assert isinstance(test_kreuzberg[1], list)
    assert len(test_kreuzberg[0]) == 84
    assert len(test_kreuzberg[1]) == 84
    intlist0 = [s for s in test_kreuzberg[0] if s.isdigit()]
    intlist1 = [s for s in test_kreuzberg[1] if s.isdigit()]
    assert len(intlist0) == 84
    assert len(intlist1) == 84

def test_compute():
    "test of compute function"
    test = ScrapingBerlinRent(['Kreuzberg'],comparelist=True)
    dftest = test.compute()
    assert dftest.column.name == 'pricem'
    assert dftest.index.name == 'neighborhood'
    assert len(dftest) == 75
    assert dftest.columns == ["Kreuzberg", "Charlottenburg", "Friedrichshain", "Mitte",] #"Neukölln",
                                #"Pankow", "Schöneberg", "Tempelhof"]
# pylint: disable=undefined-variable
@pytest.mark.filterwarnings("ignore:Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.:UserWarning")
def test_plotdataframes():
    "test of plotdataframes function"
    test = ScrapingBerlinRent(['Kreuzberg'])
    dftest = test.compute()
    Static.plot_dataframes(dftest)
    x_plot, y_plot = plt.gca().lines[0].get_xydata()  # get axis handle
    print(x_plot)
    print(y_plot)
    assert len(x_plot) == 1
    assert len(y_plot) == 75
