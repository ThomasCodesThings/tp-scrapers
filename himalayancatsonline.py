from bs4 import BeautifulSoup
import requests
import time
import multiprocessing
import os
import json
import datetime

DELAY = 0

def loader(ch, cats):
    url = "https://www.himalayancatsonline.com/Lite/pp_searchresults.php?op=search&offset=0&db=pedigree&table=pedigree&hasparents=ignore&titles=ignore&gens=9&field=Name&pattern=" + ch + "&where=begin&gender=ignore&bornwhen=ignore&orderby=name"
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        table = soup.find('table', class_='search')
        if table is None:
            return
        rows = table.find_all('tr', class_=['result', 'altresult'])
        # Iterate through rows and extract the desired information
        for row in rows:
            # Find the <td> element within the row
            td_elements = row.find_all('td')
            # Check if there are at least two <td> elements in the current <tr>
            if len(td_elements) >= 2:
                # Get the second <td> element (index 1)
                td_element = td_elements[1]
                span_elements = td_element.find_all('span')
    
                # Initialize variables to store the text from "title" and "resultdetails" spans
                title_text = None
                resultdetails_text = None
                
                # Iterate through the <span> elements
                for span in span_elements:
        # Get the text within the <span> element
                    span_text = span.get_text(strip=True)
                    
                    # Check if the <span> has the class "title"
                    if 'title' in span.get('class', []):
                        title_text = span_text
                    elif 'resultdetails' in span.get('class', []):
                        resultdetails_text = span_text
                
                # Get the text between "title" and "resultdetails" spans
                text_between_spans = td_element.find_all(text=True, recursive=False)
                
                # Remove text inside square brackets [] within the <td> element
                text_between_spans = ''.join(part for part in text_between_spans if '[' not in part and ']' not in part)
                
                # If title span is missing, set title_text to None
                if title_text is None:
                    title_text = ''
                
                # If resultdetails span is missing, set resultdetails_text to None
                if resultdetails_text is None:
                    resultdetails_text = ''
                
                cats.append({
                    'name': text_between_spans,
                    'color': title_text,
                    'details': resultdetails_text
                })
              
        print(f"Loaded page {ch} -> {'OK' if r.status_code == 200 else 'Error'} ...")
    except Exception as e:
        print(f"Failed to fetch {url}: {str(e)}")
    if DELAY > 0:
        time.sleep(DELAY)

def generator():
    patterns = []
    for i in range(ord('a'), ord('z')+1):
        for j in range(ord('a'), ord('z')+1):
            ch = chr(i) + chr(j)
            patterns.append(ch)
    print(f"Length of patterns: {len(patterns)}")  
    return patterns

def saveJson(cats):
    print("Total cats: " + str(len(cats)))
    currentDateTime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    fileName = f"cats_{currentDateTime}.json"
    with open(fileName, 'w', encoding='utf-8') as outfile:
        json.dump(cats, outfile, indent=4, ensure_ascii=False)
    print(f"Saved to {fileName}")

if __name__ == "__main__":
    patterns = generator()
    with multiprocessing.Manager() as patternManager:
        print("Starting multiprocessing for urls...")
        # Create a list to store the responses
        cats = patternManager.list()

        # Create a pool of worker processes
        num_processes = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(processes=num_processes)

        # Pass the arguments in the correct order
        pool.starmap(loader, [(i, cats) for i in patterns])

        # Close the pool and wait for the work to finish
        pool.close()
        pool.join()

        urls = list(cats)
        print(f"Urls: {len(cats)}")
        saveJson(urls)
