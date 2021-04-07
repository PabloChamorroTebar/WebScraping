import argparse
import json
import time
import chromedriver_autoinstaller
from bs4 import BeautifulSoup
from selenium import webdriver
import random
import re
import MatchingField
#from pwn import *


from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys


def main(args):

    print(
        "--------------------------------------------------------------------------------------------------------------------------------\n" +
        "██╗██████╗ ███████╗ █████╗ ██╗     ██╗███████╗████████╗ █████╗     ███████╗ ██████╗██████╗  █████╗ ██████╗ ██╗███╗   ██╗ ██████╗\n"+
        "██║██╔══██╗██╔════╝██╔══██╗██║     ██║██╔════╝╚══██╔══╝██╔══██╗    ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║██╔════╝ \n"+
        "██║██║  ██║█████╗  ███████║██║     ██║███████╗   ██║   ███████║    ███████╗██║     ██████╔╝███████║██████╔╝██║██╔██╗ ██║██║  ███╗\n"+
        "██║██║  ██║██╔══╝  ██╔══██║██║     ██║╚════██║   ██║   ██╔══██║    ╚════██║██║     ██╔══██╗██╔══██║██╔═══╝ ██║██║╚██╗██║██║   ██║\n"+
        "██║██████╔╝███████╗██║  ██║███████╗██║███████║   ██║   ██║  ██║    ███████║╚██████╗██║  ██║██║  ██║██║     ██║██║ ╚████║╚██████╔╝\n"+
        "╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝    ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═════╝ \n"+
        "----------------------------------------------------------------------------------------------------------------------------------\n")


    # Global variables
    chromedriver_autoinstaller.install()
    global driver
    global idealista_base_path
    idealista_base_path = "https://www.idealista.com"

    url, driver = initVariables(args)

    #linksList = obtainLinks(url)
    data_homes = obtainDataHomes(linksList=[])
    driver.close()
    writeDataToFile(data_homes)
    time.sleep(2)


def initVariables(args):

    # Variables set up
    print(args.url)
    url = args.url
    if args.proxy:
        proxy = args.proxy

    if proxy:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server=socks5://%s' % proxy)
        driver = webdriver.Chrome(chrome_options=chrome_options)
    else:
        driver = webdriver.Chrome()

    return url, driver


def obtainLinks(url):

    driver.get(url)
    time.sleep(20)

    try:
        driver.find_element_by_xpath('//*[@id="didomi-notice-agree-button"]').click()
    except:
        print("Button not found")

    linksList = set()

    # Obtain all homes
    #p = log.progress("Homes")
    #p.status("Getting home links")
    #time.sleep(0.5)

    for i in range(1, 20):
        htmlText = driver.page_source
        soup = BeautifulSoup(htmlText, 'html.parser')
        homes = soup.find_all('a', class_="item-link")
        for home in homes:
            if home['href'] and home["href"].startswith("/inmueble"):
                linksList.add(home['href'])
        ActionChains(driver).key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
        time.sleep(0.5)

    #p.success("%d links obtained", len(linksList))

    return linksList


def obtainDataHomes(linksList):

    #p = log.progress("Home")
    linksList = ["/inmueble/89943824/?xtmc=1_1_zonas-infantiles&xtcr=0"]
    counter = 1
    data_homes = []
    for link in linksList:
        #p.status("Obtain vivienda [%d] data" % counter)
        data_homes.append(obtainDatahome(link))
        counter += 1

        #Borrar
        return

    #p.success("Homes data collected")

    return data_homes


def obtainDatahome(link):

    data_home = dict()
    url = idealista_base_path + link
    driver.get(url)
    time.sleep(40)
    htmlText = driver.page_source
    soup = BeautifulSoup(htmlText, 'html.parser')

    try:
        home_type = driver.find_element_by_xpath('//*[@id="main"]/div/main/section[1]/div[2]/h1/span')
        location = driver.find_element_by_xpath('//*[@id="main"]/div/main/section[1]/div[2]/span/span').text.split(",")[0]
        price = soup.find("span", class_="info-data-price").find("span", class_="txt-bold").text.replace(" €",
                "").replace(".", "")
        house_size = re.findall(r'[0-9]+', soup.find("div", class_="info-features").find_all("span")[0].text)
        rooms = re.findall(r'[0-9]+', soup.find("div", class_="info-features").find_all("span")[1].text)
        data_home["price"] = price
        data_home["rooms"] = rooms
        data_home["house_size"] = house_size
        data_home["location"] = location
        data_home["type"] = home_type

        for feature in driver.find_element_by_xpath('//*[@id="details"]/div[1]/div[1]/div/ul').find_element("li"):
            field = matchingField(feature.text)
            if field is not None:
                data_home[field[0]] = field[1]
        try:
            driver.find_element_by_xpath('//*[@id="details"]/div[1]/div[2]/div')
            for feature in driver.find_element_by_xpath('//*[@id="details"]/div[1]/div[2]/div/ul').find_element("li"):
                field = matchingField(feature.text)
                if field is not None:
                    data_home[field[0]] = field[1]
        except:
            print("[INFO]: Piso %s sin Equipamiento" % idealista_base_path + link)

        try:
            driver.find_element_by_xpath('//*[@id="details"]/div[1]/div[3]/div')
            for feature in driver.find_element_by_xpath('//*[@id="details"]/div[1]/div[3]/div/ul').find_element("li"):
                field = matchingField(feature.text)
                if field is not None:
                    data_home[field[0]] = field[1]
        except:
            print("[INFO]: Piso %s sin Otras Caracteristicas" % idealista_base_path + link)


    except Exception as ex:
        print(ex)
        print("[ERROR]: Piso %s con html distinto" % idealista_base_path + link)
        data_home["price"] = "N/A"
        data_home["rooms"] = "N/A"
        data_home["house_size"] = "N/A"
        data_home["location"] = "N/A"
        data_home["type"] = "N/A"


    return data_home


def writeDataToFile(data_homes):

    #p = log.progress("Data")

    #p.status("Inserting data into %s file" % outputFile)

    print(data_homes)

    with open("data/data" + str(random.randint(100000000, 999999999)) + ".json", 'w') as outfile:
        json.dump(data_homes, outfile, ensure_ascii=False)

    #p.success("Insert data into %s file" % outputFile)