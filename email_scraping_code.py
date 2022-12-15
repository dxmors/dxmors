import random
import re
from collections import deque
import time
from urllib.parse import urlsplit
import keyboard
import gspread
import pandas as pd
import requests
from bs4 import BeautifulSoup

gc = gspread.service_account()

sh = gc.open("email_scraps")

urls_sheet = sh.worksheet("urls")
email_sheet = sh.worksheet("emails")
url_scrapped = sh.worksheet("url_scrapped")
data_sheet = sh.worksheet("data")



new_urls = deque(urls_sheet.col_values(1)) 


scraped_url =set(url_scrapped.col_values(1)) 

emails = set(email_sheet.col_values(1))  
main_flag = True
flag = True

def scrape(url,flag):
    temp_url = url
    scraped = set() 
    unscraped = deque()
    unscraped.append(url)
    parts = urlsplit(temp_url)
    #print(parts)
    base_url = "{0.scheme}://{0.netloc}".format(parts)
    if url in scraped_url:
        return
    scraped_url.add(url)
    
    while len(unscraped) and flag:
        
        if len(scraped)>20:
            break
        
        #rate = [i/100000 for i in range(10)]
        #time.sleep(random.choice(rate))
        
        url = unscraped.popleft()  
        scraped.add(url)

        #print(url)
        
        
        if '/' in parts.path:
            path = url[:url.rfind('/')+1]
        else:
            path = url

        print("Crawling URL %s" % url)
        try:
            response = requests.get(url,timeout=5)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
            continue
        
        #print("\nenter y to continue any other key to continue")
        while True:
            break
            if keyboard.is_pressed('y'):
                break
            if keyboard.is_pressed('n'):
                flag = False
                break
            time.sleep(0.1)
        
        if flag == False:
            break
        
        new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com", response.text, re.I))
        if new_emails:
            print(f"new emails found  \n{new_emails}")
        emails.update(new_emails) 

        try:
            soup = BeautifulSoup(response.content,"html.parser")
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
            continue
        
        

        for anchor in soup.find_all("a"):
            if "href" in anchor.attrs:
                link = anchor.attrs["href"]
            else:
                link = ''
            
            #print(link)

            if link.startswith('/'):
                link = base_url + link
                #print(link)
            elif not link.startswith('http'):
                link = path + link

            if not link.endswith(".gz") and not link.endswith(".pdf"):
                if not link in unscraped and not link in scraped:
                    temp_base_url = "{0.scheme}://{0.netloc}".format(urlsplit(link))
                    if not temp_base_url == base_url and not temp_base_url in new_urls:
                        #print(len(new_urls))
                        if len(new_urls) <2000:
                            new_urls.append(link)
                    if temp_base_url == base_url:
                        if "contact" in link or "mail" in link:
                            unscraped.append(link)
                    

def new_url(url):
    print(f"New URL is {url} \n\n Press \ny to continue \nn for next URL\ne to exit")
    
    while True:
        if keyboard.is_pressed('y'):
            scrape(url)
            break
        if keyboard.is_pressed('n'):
            break
        if keyboard.is_pressed('s'):
            global main_flag
            main_flag = False
            break
        time.sleep(0.1)




while flag and len(new_urls):
    url = new_urls.popleft()
    #print (url)
    #new_url(url,flag)
    
    try:       
        scrape(url,flag)
        time.sleep(1)
    #print(new_urls)
        email_sheet.update(pd.DataFrame(emails).values.tolist())
        urls_sheet.batch_clear(['A1:A2000'])
        urls_sheet.update(pd.DataFrame(list(new_urls)).values.tolist())
        url_scrapped.update(pd.DataFrame(scraped_url).values.tolist())
    except:
        continue
    
    
    if len(emails)>5000:
        exit()
        
email_list = list(emails)   
url_list = list(scraped_url)
link_list = list(new_urls)
data = [email_list,url_list,link_list]

data_df = pd.DataFrame(data).T

data_sheet.update(data_df.values.tolist())