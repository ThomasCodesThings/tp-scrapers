from bs4 import BeautifulSoup
import requests
import time
import multiprocessing
import os
import json
import datetime

DELAY = 1

def isInvalidLink(id):
    url = f"https://bengalpedigrees.com/viewcat.php?catid={id}"
    r = requests.get(url)
    if(r.status_code >= 300):
        print(f"Failed to fetch {url}: {r.status_code}")
        return True
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find_all('table', recursive=True)[-1]
    return isInvalid(soup)

def isInvalid(soup):
    name_td = soup.find('td', attrs={'width': '80'}, text='Name: ')
    if name_td:
        sibling = name_td.find_next_sibling('td')
        if sibling.text.strip() == "View Ped":
            return True
        
    return False

def findValidId():
    start = 1000000
    end = 1  # Change the end value to the lowest possible ID
    
    while start >= end:
        mid = (start + end) // 2
        print(f"Checking id: {mid}...")
        if not isInvalidLink(mid):
            end = mid + 1  # Go to the lower half
        else:
            start = mid - 1  # Go to the upper half
        if DELAY > 0:
            time.sleep(DELAY)

    return start

def saveJson(cats):
    print("Total cats: " + str(len(cats)))
    currentDateTime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    fileName = f"cats_{currentDateTime}.json"
    with open(fileName, 'w', encoding='utf-8') as outfile:
        json.dump(cats, outfile, indent=4, ensure_ascii=False)
    print(f"Saved to {fileName}")

def loader(i, cats):
    try:
        url = f"https://bengalpedigrees.com/viewcat.php?catid={i}"
        r = requests.get(url)
        if(r.status_code >= 300):
            print(f"Failed to fetch {url}: {r.status_code}")
            return
        print(f"Loaded page {i} -> {'OK' if r.status_code == 200 else 'Error'} ...")
        soup = BeautifulSoup(r.text, 'html.parser')
        table = soup.find_all('table', recursive=True)[-1]

        #params
        name = ''
        sex = ''
        breed = ''
        reg = ''
        reg_alt = ''
        dob = ''
        color = ''
        color_alt = ''
        eyes = ''
        sire = ''
        dam = ''

        #find all td elements
        name_td = soup.find('td', attrs={'width': '80'}, text='Name: ')
        sex_td = soup.find('td', attrs={'width': '80'}, text='Sex: ')
        breed_td = soup.find('td', attrs={'width': '80'}, text='Breed: ')
        reg_td = soup.find('td', attrs={'width': '80'}, text='Reg Num: ')
        reg_alt_td = soup.find('td', attrs={'width': '80'}, text='Alt Reg: ')
        dob_td = soup.find('td', attrs={'width': '80'}, text='DOB: ')
        color_td = soup.find('td', attrs={'width': '80'}, text='Color: ')
        color_alt_td = soup.find('td', attrs={'width': '80'}, text='Alt Color: ')
        eyes_td = soup.find('td', attrs={'width': '80'}, text='Eyes: ')
        sire_td = soup.find('td', attrs={'width': '80'}, text='Sire: ')
        dam_td = soup.find('td', attrs={'width': '80'}, text='Dam: ')

        if name_td:
            name = name_td.find_next_sibling('td').strip().replace("View Ped", "")

        if sex_td:
            sex = name_td.find_next_sibling('td').text.strip()
        
        if breed_td:
            breed = breed_td.find_next_sibling('td').text.strip()
        
        if reg_td:
            reg = reg_td.find_next_sibling('td').text.strip()

        if reg_alt_td:
            reg_alt = reg_alt_td.find_next_sibling('td').text.strip()

        if dob_td:
            dob = dob_td.find_next_sibling('td').text.strip()

        if color_td:
            color = color_td.find_next_sibling('td').text.strip()

        if color_alt_td:
            color_alt = color_alt_td.find_next_sibling('td').text.strip()

        if eyes_td:
            eyes = eyes_td.find_next_sibling('td').text.strip()
        
        if sire_td:
            sire = sire_td.find_next_sibling('td').text.replace("View Info", "").replace("View Ped", "").strip()

        if dam_td:
            dam = dam_td.find_next_sibling('td').text.replace("View Info", "").replace("View Ped", "").strip()

        cats.append({
            'id': i,
            'name': name,
            'sex': sex,
            'breed': breed,
            'reg': reg,
            'reg_alt': reg_alt,
            'dob': dob,
            'color': color,
            'color_alt': color_alt,
            'eyes': eyes,
            'sire': sire,
            'dam': dam
        })


    except Exception as e:
        print(f"Failed to fetch {url}: {str(e)}")

if __name__ == "__main__":
    validId = findValidId()
    print(f"Last valid id: {validId}")
    ids = list(range(1, validId + 1))
    with multiprocessing.Manager() as patternManager:
        print("Starting multiprocessing for urls...")
        # Create a list to store the responses
        cats = patternManager.list()

        # Create a pool of worker processes
        num_processes = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(processes=num_processes)

        # Pass the arguments in the correct order
        pool.starmap(loader, [(i, cats) for i in ids])

        # Close the pool and wait for the work to finish
        pool.close()
        pool.join()

        urls = list(cats)
        print(f"Urls: {len(cats)}")
        saveJson(urls)