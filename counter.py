import requests
import time
from datetime import datetime
from colors import *

def get_total_headless_henk_versions(data):
    total_headless_henk = 0
    brands = data.get('brands', {})
    for brand in brands.values():
        headless_henk = brand.get('Headless-Henk', {})
        for version_count in headless_henk.values():
            total_headless_henk += version_count
    return total_headless_henk

def get_total_userscripts(data):
    total_userscripts = 0
    brands = data.get('brands', {})
    for brand in brands.values():
        userscripts = brand.get('Userscript', {})
        for userscript_count in userscripts.values():
            total_userscripts += userscript_count
    return total_userscripts

def main():
    old_headless_henk = 0
    old_userscripts = 0

    while True:
        try:
            response = requests.get('https://chief.placenl.nl/api/stats')
            data = response.json()

            total_headless_henk = get_total_headless_henk_versions(data)
            total_userscripts = get_total_userscripts(data)

            # Clear previous output
            print("\033[H\033[J", end='')

            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f'Current Date and Time: {current_datetime}')
            print(f'Total Headless-Henk versions: {AQUA}{total_headless_henk}{RESET}')
            print(f'Total Userscripts: {AQUA}{total_userscripts}{RESET}')

            old_headless_henk = total_headless_henk
            old_userscripts = total_userscripts
        except Exception as e:
            print(f'Error occurred: {e}')

        time.sleep(1)

if __name__ == "__main__":
    main()