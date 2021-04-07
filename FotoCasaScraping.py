import argparse
import json
import time
import chromedriver_autoinstaller
from bs4 import BeautifulSoup
from selenium import webdriver
from MatchingField import machingPpalFieldFotoCasa, machingAuxFieldFotoCasa, checkFotoCasaFieldFound
import random
import MatchingField

from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys


def main(args):

    print(
        "-------------------------------------------------------------------------------------------------------------------------------------\n"
        "███████╗ ██████╗ ████████╗ ██████╗  ██████╗ █████╗ ███████╗ █████╗     ███████╗ ██████╗██████╗  █████╗ ██████╗ ██╗███╗   ██╗ ██████╗\n" +
        "██╔════╝██╔═══██╗╚══██╔══╝██╔═══██╗██╔════╝██╔══██╗██╔════╝██╔══██╗    ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║██╔════╝\n" +
        "█████╗  ██║   ██║   ██║   ██║   ██║██║     ███████║███████╗███████║    ███████╗██║     ██████╔╝███████║██████╔╝██║██╔██╗ ██║██║  ███╗\n" +
        "██╔══╝  ██║   ██║   ██║   ██║   ██║██║     ██╔══██║╚════██║██╔══██║    ╚════██║██║     ██╔══██╗██╔══██║██╔═══╝ ██║██║╚██╗██║██║   ██║\n" +
        "██║     ╚██████╔╝   ██║   ╚██████╔╝╚██████╗██║  ██║███████║██║  ██║    ███████║╚██████╗██║  ██║██║  ██║██║     ██║██║ ╚████║╚██████╔╝\n" +
        "╚═╝      ╚═════╝    ╚═╝    ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═════╝\n"
        "-------------------------------------------------------------------------------------------------------------------------------------\n")


    # Global variables
    chromedriver_autoinstaller.install()
    global driver
    driver = webdriver.Chrome()
    global fotocasa_base_path
    fotocasa_base_path = "https://www.fotocasa.es"

    url = initVariables(args)

    linksList = obtainLinks(url)
    data_homes = obtainDataHomes(linksList)
    driver.close()
    writeDataToFile(data_homes)
    time.sleep(2)


def initVariables(args):

    # Variables set up
    url = args.url
    proxy = args.proxy

    return url


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
    for i in range(1, 20):
        htmlText = driver.page_source
        soup = BeautifulSoup(htmlText, 'html.parser')
        homes = soup.find_all('a', class_="re-Card-link")
        for home in homes:
            if home['href'] and home["href"].startswith("/es/"):
                linksList.add(home['href'])
        ActionChains(driver).key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
        time.sleep(0.5)

    return linksList


def obtainDataHomes(linksList):

    counter = 1
    data_homes = []
    for link in linksList:
        data_homes.append(obtainDatahome(link))
        counter += 1

    return data_homes


def obtainDatahome(link):

    data_home = dict()
    url = fotocasa_base_path + link
    driver.get(url)
    time.sleep(0.5)
    htmlText = driver.page_source
    soup = BeautifulSoup(htmlText, 'html.parser')

    try:
        price = soup.find("span", class_="re-DetailHeader-price").text.replace(" €", "").replace(".", "")
        rooms = soup.find_all("li", class_="re-DetailHeader-featuresItem")[0].find("span", class_=False).find(
            "span").text
        bathrooms = soup.find_all("li", class_="re-DetailHeader-featuresItem")[1].find("span", class_=False).find(
            "span").text
        house_size = soup.find_all("li", class_="re-DetailHeader-featuresItem")[2].find("span", class_=False).find(
            "span").text
        location = soup.find("span", class_="re-Breadcrumb-text").text


        data_home["price"] = price
        data_home["rooms"] = rooms
        data_home["bathrooms"] = bathrooms
        data_home["house_size"] = house_size
        data_home["location"] = location

        for feature in soup.find_all("div", class_="re-DetailFeaturesList-featureContent"):
            #print(feature)
            if feature.find("p", class_="re-DetailFeaturesList-featureLabel") is not None:
                #print("Caracteristica %s y valor %s" %  (feature.find("p", class_="re-DetailFeaturesList-featureLabel").text, feature.find("p",class_="re-DetailFeaturesList-featureValue").text) )
                field = machingPpalFieldFotoCasa(feature.find("p", class_="re-DetailFeaturesList-featureLabel").text,
                                     feature.find("p",class_="re-DetailFeaturesList-featureValue").text)
                if field is not None:
                    data_home[field[0]] = field[1]

        for extraFeature in soup.find_all("li", class_="re-DetailExtras-listItem"):
            #print("Field %s" % extraFeature.text)
            field = machingAuxFieldFotoCasa(extraFeature.text)
            if field is not None:
                data_home[field[0]] = field[1]

        data_home = checkFotoCasaFieldFound(data_home)

    except Exception as ex:
        print(ex)
        print("[ERROR]: Piso %s con html distinto" % fotocasa_base_path + link)
        data_home["price"] = "N/A"
        data_home["rooms"] = "N/A"
        data_home["house_size"] = "N/A"
        data_home["location"] = "N/A"
        data_home["type"] = "N/A"



    return data_home


def writeDataToFile(data_homes):

    with open("data/data" + str(random.randint(100000000,999999999)) + ".json", 'w', encoding='utf-8') as outfile:
        json.dump(data_homes, outfile, ensure_ascii=False)