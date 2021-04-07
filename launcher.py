import argparse

import FotoCasaScraping
import IdealistaScraping

parser = argparse.ArgumentParser(description='Scraping webs.')
parser.add_argument('url', type=str, help='Enter the url with filters apply')
parser.add_argument('--proxy', type=str, help="proxy to jump blocking")

args = parser.parse_args()

if "fotocasa" in args.url:
    FotoCasaScraping.main(args)
elif "idealista" in args.url:
    IdealistaScraping.main(args)
else:
    print("No se ha encontrado")