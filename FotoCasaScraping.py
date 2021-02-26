import argparse
import json
import time
import chromedriver_autoinstaller
from bs4 import BeautifulSoup
from selenium import webdriver
#from pwn import *

from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

print(
"-------------------------------------------------------------------------------------------------------------------------------------\n"
"███████╗ ██████╗ ████████╗ ██████╗  ██████╗ █████╗ ███████╗ █████╗     ███████╗ ██████╗██████╗  █████╗ ██████╗ ██╗███╗   ██╗ ██████╗\n"+
"██╔════╝██╔═══██╗╚══██╔══╝██╔═══██╗██╔════╝██╔══██╗██╔════╝██╔══██╗    ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║██╔════╝\n"+
"█████╗  ██║   ██║   ██║   ██║   ██║██║     ███████║███████╗███████║    ███████╗██║     ██████╔╝███████║██████╔╝██║██╔██╗ ██║██║  ███╗\n"+
"██╔══╝  ██║   ██║   ██║   ██║   ██║██║     ██╔══██║╚════██║██╔══██║    ╚════██║██║     ██╔══██╗██╔══██║██╔═══╝ ██║██║╚██╗██║██║   ██║\n"+
"██║     ╚██████╔╝   ██║   ╚██████╔╝╚██████╗██║  ██║███████║██║  ██║    ███████║╚██████╗██║  ██║██║  ██║██║     ██║██║ ╚████║╚██████╔╝\n"+
"╚═╝      ╚═════╝    ╚═╝    ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═════╝\n"
"-------------------------------------------------------------------------------------------------------------------------------------\n")

# Global variables
chromedriver_autoinstaller.install()
driver = webdriver.Chrome()
fotocasa_base_path = "https://www.fotocasa.es"
proxy = None


def initVariables(args):

    # Variables set up
    url = args.url
    if args.output:
        outputFile = args.output
    else:
        outputFile = "data.json"
    proxy = args.proxy

    return url, outputFile


def obtainDatahome(link):

    data_home = dict()
    url = fotocasa_base_path + link
    driver.get(url)
    time.sleep(0.5)
    htmlText = driver.page_source
    soup = BeautifulSoup(htmlText, 'html.parser')
    price = soup.find("span", class_="re-DetailHeader-price").text
    rooms = soup.find_all("li", class_="re-DetailHeader-featuresItem")[0].find("span", class_=False).find(
        "span").text
    bathrooms = soup.find_all("li", class_="re-DetailHeader-featuresItem")[1].find("span", class_=False).find(
        "span").text
    house_size = soup.find_all("li", class_="re-DetailHeader-featuresItem")[2].find("span", class_=False).find(
        "span").text
    data_home["price"] = price
    data_home["rooms"] = rooms
    data_home["bathrooms"] = bathrooms
    data_home["house_size"] = house_size
    for feature in soup.find_all("div", class_="re-DetailFeaturesList-featureContent"):
        data_home[feature.find("p", class_="re-DetailFeaturesList-featureLabel").text] = feature.find("p",
                                                                                                      class_="re-DetailFeaturesList-featureValue").text

    for extraFeature in soup.find_all("li", class_="re-DetailExtras-listItem"):
        data_home[extraFeature.text] = True

    return data_home


def writeDataToFile(data_homes,outputFile):

    #p = log.progress("Data")

    #p.status("Inserting data into %s file" % outputFile)

    with open(outputFile, 'w') as outfile:
        json.dump(data_homes, outfile, ensure_ascii=False)

    #p.success("Insert data into %s file" % outputFile)


def obtainLinks(url):

    driver.get(url)
    time.sleep(8)

    try:
        driver.find_element_by_css_selector("*[data-testid='TcfAccept']").click()
    except:
        print("Button not found")
        driver.find_element_by_css_selector("*[data-testid='TcfAccept']")

    linksList = set()

    # Obtain all homes
    #p = log.progress("Homes")
    #p.status("Getting home links")
    #time.sleep(0.5)

    for i in range(1, 20):
        htmlText = driver.page_source
        soup = BeautifulSoup(htmlText, 'html.parser')
        homes = soup.find_all('a', class_="re-Card-link")
        for home in homes:
            if home['href'] and home["href"].startswith("/es/"):
                linksList.add(home['href'])
        ActionChains(driver).key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
        time.sleep(0.5)

    #p.success("%d links obtained", len(linksList))

    return linksList


def obtainDataHomes(linksList):

    #p = log.progress("Home")
    counter = 1
    data_homes = []
    for link in linksList:
        #p.status("Obtain vivienda [%d] data" % counter)
        data_homes.append(obtainDatahome(link))
        counter += 1

    #p.success("Homes data collected")

    return data_homes


def main(args):

    url,outputFile = initVariables(args)

    linksList = obtainLinks(url)
    data_homes = obtainDataHomes(linksList)
    driver.close()
    writeDataToFile(data_homes, outputFile)
    time.sleep(2)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Scraping fotocasa web.')
    parser.add_argument('url', type=str, help='Enter the url with filters apply')
    parser.add_argument('--output', type=str, help="file with saved data (data.json by default)")
    parser.add_argument('--proxy', type=str, help="proxy to jump blocking")

    args = parser.parse_args()

    main(args)
