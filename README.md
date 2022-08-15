[![Test-Lint-Format](https://github.com/aurelpere/python-scraping-flatrent/actions/workflows/main.yml/badge.svg)](https://github.com/aurelpere/python-scraping-flatrent/actions/workflows/main.yml) ![test-coverage badge](./coverage-badge.svg) [![Maintainability](https://api.codeclimate.com/v1/badges/26af1febe301da20bc2b/maintainability)](https://codeclimate.com/github/aurelpere/python-scraping-flatrent/maintainability)

# scraping
a scraping script to get rent data from wg-gesucht.de

## usage in command line:<br>
`python scraping.py -n neighborhood_to_scrape`<br>
>will scrape one neighborhood (neighborhood_to_scrape) and render a boxplot.   
<br>

`python scraping.py -n neighborhood_to_scrape --compare`<br>
>will scrape one neighborhood (neighborhood_to_scrape) and render a boxplot of this neighborhood and others main neighborhood of Berlin.   
<br>

`python scraping.py --compare`<br>
>will scrape and render a boxplot of main neighborhoods of Berlin.   
<br>

## results on 5/04/2022:<br>

<p align="center">
  <img src="boxplot_scraping.png" width="600" title="rent boxplot">
</p>
.
