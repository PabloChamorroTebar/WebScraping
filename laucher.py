import argparse

import FotoCasaScraping

parser = argparse.ArgumentParser(description='Scraping fotocasa web.')
parser.add_argument('url', type=str, help='Enter the url with filters apply')
parser.add_argument('--output', type=str, help="file with saved data (data.json by default)")
parser.add_argument('--proxy', type=str, help="proxy to jump blocking")

args = parser.parse_args()

if "fotocasa" in args.url:
    FotoCasaScraping.main(args)
elif "idealista" in args.url:
    print("Idealista")
else:
    print("No se ha encontrado")