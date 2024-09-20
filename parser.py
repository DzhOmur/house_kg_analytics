import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from tqdm import tqdm
import time
import os
import csv


def get_url()->None:
  print('\nLoading URLS and saving as file')
  print('___ LOAD URLS ___')

  sub_url = []
  for page in tqdm(range(1, int(input('How many pages do you want? '))+1)):
    url = f'https://www.house.kg/kupit-kvartiru?page={page}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    objects = soup.find("div", class_="listings-wrapper")
    lincs = objects.find_all('div', class_="left-image")
    for ur in lincs:
      sub_url.append(ur.find('a')['href'])
  print(f'___ Received {len(sub_url)} URLS ___')

  urls = []
  for i in sub_url:
    urls.append("https://www.house.kg" + i)

  pd.DataFrame(urls, columns=['URLS']).to_csv('urls.csv', index=False)
  print('\nFILE "urls.csv" SAVED\n')



def get_data(ur:str)->dict:
  
  response = requests.get(ur)
  soup = BeautifulSoup(response.text, "html.parser")
  objects = soup.find('div', class_='details-main')
  atr_dict = {}

  try: 
    header_details = soup.find('div', class_ = 'details-header').find('h1').text.replace('\n', '').strip()
    atr_dict['header_details'] = header_details
  except Exception:
    pass

  try: 
    address = soup.find('div', class_ = 'address').text.replace('\n', '').strip()
    atr_dict['address'] = address
  except Exception:
    pass

  try: 
    latitude = soup.find('div', id = 'map2gis').attrs['data-lat']
    longitude = soup.find('div', id = 'map2gis').attrs['data-lon']
    atr_dict['latitude'] = latitude
    atr_dict['longitude'] = longitude
  except Exception:
    pass

  try: 
    user_name = soup.find('div', class_ = 'user-info').find('a').text
    atr_dict['user_name'] = user_name
  except Exception:
    pass

  try: 
    user_url = soup.find('div', class_ = 'user-info').find('a')['href']
    atr_dict['user_url'] = 'https://www.house.kg' + user_url
  except Exception:
    pass

  try: 
    tel_number = soup.find('div', class_ = 'number').text
    atr_dict['tel_number'] = tel_number
  except Exception:
    pass
 
  try:
    atributs = objects.find_all('div', class_ = 'info-row')
    for atr in atributs:
      key = atr.find('div', class_='label').text.strip().replace('\n', '')
      val = atr.find('div', class_='info').text.strip().replace('\n', '')
      atr_dict[key] = val     
  except Exception:
    pass
    
  try:
    views = soup.find('span', class_ = 'view-count').text.replace('\xa0', '')
    atr_dict['views'] = views
  except Exception:
    pass

  try: 
    hearts = soup.find('span', class_ = 'favourite-count table-comments').text.replace('\xa0', '')
    atr_dict['hearts'] = hearts
  except Exception:
    pass

  try: 
    num_of_comments = soup.find('span', class_ = 'comments-count table-comments').text.replace('\xa0', '')
    atr_dict['num_of_comments'] = num_of_comments
  except Exception:
    pass
  
  try: 
    publicated = soup.find('span', class_ = 'added-span').text
    atr_dict['publicated'] = publicated
  except Exception:
    pass

  try: 
    upped = soup.find('span', class_ = 'upped-span').text
    atr_dict['upped'] = upped
  except Exception:
    pass

  try: 
    description = soup.find('div', class_ = 'description').find('p').text.replace('\n', '')
    atr_dict['description'] = description
  except Exception:
    pass

  try: 
    pictures = objects.find('div', class_ = 'right').find_all('a')
    urls = []
    for pics in pictures:
      if pics.get('href'):
        urls.append(pics['href'])

    atr_dict['pictures'] = urls     
  except Exception:
    pass

  return atr_dict


#PROCESS
print('#########___START PARSING SCRIPT ___#########')
current_time = time.localtime()
formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", current_time)
print()
print(f"Current date and time {formatted_time}")
print('\n#######################################################\n')

print('###### Do you want to get the URLS? ######')
while True:
  answer = input('Write Y or N: ')
  if (answer == 'Y') or (answer == 'N'):
    break
  else:
    print('\t\t!!! INVALID INPUT !!! Please re-enter !!!')


if answer=='Y':
  get_url()
elif answer=='N':
  if 'urls.csv' in os.listdir():
    pass
  else:
    print("!!! <urls.csv> file not found! Let's run the script for getting URLS!")
    get_url()

print('\t\tPARSING')
if "error_urls.csv" in os.listdir():
  answer = input('Do you want to PARS invalid URRLS? Y/N ')
  if answer.strip() == 'Y':
    urls = pd.read_csv('error_urls.csv').URLS.to_list()
  else:  
    urls = pd.read_csv('urls.csv').URLS.to_list()
else:
  urls = pd.read_csv('urls.csv').URLS.to_list()

apartments = []
error_urls = []
for url in tqdm(urls):
  try:
    apartments.append(get_data(url))
  except Exception:
    url_index = urls.index(url)
    print('!!!___ERRROR___!!!')
    print(f'With url index: {url_index}')
    print(f'With url: {url}')
    error_urls.append(url)


df = pd.DataFrame(apartments)
print('___ DATA INFO ___\n')
print(df.info())
print(f'\n\nNumber of unique phone numbers: {df.tel_number.unique().shape[0]} / {df.shape[0]}\n')
df.to_csv(f'house_kg_.csv', index=False)
print(f'___ File << house_kg_{formatted_time}.csv >> saved ___')

if len(error_urls) > 0:
  print('THERE ARE INVALID URLS')
  pd.DataFrame(error_urls, columns=['URLS']).to_csv('error_urls.csv', index=False)
  print('\nFILE "error_urls.csv" SAVED')


print('\n\t\tEND\n')

print (df.columns)