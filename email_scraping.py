import json
from unicodedata import name
from bs4 import BeautifulSoup as bs
import pandas as pd
pd.set_option('display.max_colwidth', 500)
import time
import requests
import random
import gspread


data =[[]]


# List of URLs
def scrapeurl():
    # Accessing the Webpage
    page = requests.get(url)
    
    # Getting the webpage's content in pure html
    soup = bs(page.content,"html.parser")
    
    
    
    pass

urls = [f"https://peelidori.com/sale.html?p={i}/" for i in range(1,4)]

# List for Randomizing our request rate
rate = [i/10 for i in range(10)]

j=0
for url in urls:
    
    # Accessing the Webpage
    page = requests.get(url)
    
    # Getting the webpage's content in pure html
    soup = bs(page.content,"html.parser")
    
    
    for i in soup.find_all(class_='item product product-item'):
        
        url_temp = i.find("a")
        url_temp = url_temp['href'] 
        
        page_temp = requests.get(url_temp)
    
        so = bs(page_temp.content,"html.parser")
        img = []
        for imges in so.find(id ='owl-carousel-gallery').find_all("img"):
            img.append(imges.get('src'))
        #nam = so.find(class_='page-title').text
        #brand_name = so.find(class_='brand-name').find("a").text
        #so.find(class_='page-title').text
        #This is now syncronized
        category = so.find("td", attrs={"class":"col data","data-th":"Categories"}).text


        try:
            color = so.find("td", attrs={"class":"col data","data-th":"Color"}).text
        except:
            color = ""  
            
        
        pric = so.find("div",attrs={"class":"product-info-main"}).find("span",attrs={"class":"price-wrapper","data-price-type":"basePrice"}).text
        try:
            special_pric = so.find("div",attrs={"class":"product-info-main"}).find("span",attrs={"class":"price-wrapper","data-price-type":"oldPrice"}).text   
        except:
            
            special_pric = pric
            print(special_pric, " Not on Offer")
        else:
            print(special_pric," On Offer")
        #special_pric = pric
        
        
        
        #description = so.find("div", attrs={"class":"value" ,"itemprop":"description"}).text
              
        #des = so.find("script", attrs={"type":"application/ld+json"}).text
        kinesdes = json.loads(str(so.find("script", {"type":"application/ld+json"}).text), strict=False)
        #linesdes = json.loads(des)
        sku = kinesdes['sku']
        nam = kinesdes['name'].title()
        description = kinesdes['description']
        #img_link = kinesdes['image']
        img_link= img[0]
        
        try:
            additional_images = img[1]
        except:
            additional_images = "" 
        
        
        for i in range(2,len(img)):
            additional_images += "," + img[i]
        
        if category == "Saree":
            size = ["OSFA"]
        else:
            size = ["XS","S","M","L","XL"]

        for sizes in size:
            skun = sku + "-" + sizes
            data.append([skun,nam,description,color,url_temp,condition,pric,special_pric,avaliability,img_link,
                     gtin,mpn,brand_name,google_product_category,gender,identifier_exists,sizes,
                     additional_images,age_group])
        
       

df= pd.DataFrame(data)

worksheet.update(df.values.tolist())

df.to_excel("latest_price.xlsx")