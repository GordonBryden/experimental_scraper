import requests
from bs4 import BeautifulSoup
import re
import sqlite3
import os

aviation_website = 'http://www.caa.co.uk/Data-and-analysis/UK-aviation-market/Airports/Datasets/UK-airport-data/'
nhs_website = 'http://www.isdscotland.org/Health-Topics/Workforce/'
mod_website = 'https://www.gov.uk/government/collections/location-of-all-uk-regular-service-and-civilian-personnel-quarterly-statistics-index'
mod_corrected_website = 'https://www.gov.uk/government/statistics/location-of-uk-regular-service-and-civilian-personnel-quarterly-statistics-'
housing_website = 'https://www.ros.gov.uk/property-data/property-statistics/quarterly-house-price-statistics'
sfc_website = 'http://www.sfc.ac.uk/publications-statistics/reports-publications/reports-publications.aspx'

aviation_pattern = "(?<=Data-and-analysis/UK-aviation-market/Airports/Datasets/UK-Airport-data/Airport-data-).*"
nhs_pattern = "(?<=Health-Topics/Workforce/Publications/).*\\.pdf"
mod_pattern = "(?<=/government/statistics/location-of-uk-regular-service-and-civilian-personnel-quarterly-statistics-).*"
second_mod_pattern = "(?<=/government/uploads/system/uploads/attachment_data/file/).*"
housing_pattern = "(?<=https://www.ros.gov.uk/__data/assets/excel_doc/).*"
sfc_pattern = "(?<=SFCST).*"
mod_pattern_2 = "(?<=).*"

def get_key_links (website,pattern):
    response = requests.get(website)
    soup = BeautifulSoup(response.text,"html.parser")
    links = [a.attrs.get('href') for a in soup.body.select('a')]
    key_links = []
    for line in links:
            try:
                if re.search(pattern,line):
                    key_links.append(re.search(pattern,line).group(0))
            except:
                print("possible error")
                    
    return key_links


aviation_links = sorted(get_key_links(aviation_website,aviation_pattern),reverse=True)
nhs_links = get_key_links(nhs_website,nhs_pattern)
mod_links = get_key_links(mod_website,mod_pattern)

mod_corrected_website = 'https://www.gov.uk/government/statistics/location-of-uk-regular-service-and-civilian-personnel-quarterly-statistics-' + mod_links[0]

latest_mod_links = get_key_links(mod_corrected_website,second_mod_pattern)
housing_links = get_key_links(housing_website,housing_pattern)
sfc_links = get_key_links(sfc_website,sfc_pattern)

#Set up the database cursor
dir_path = os.path.dirname(os.path.abspath(__file__))
db = sqlite3.connect(os.path.join(dir_path, 'webcrawler_data'))
cursor = db.cursor()


id1 = 1
website1 = "aviation"
result1 = str(aviation_links)
id2 = 2
website2 = "nhs"
result2 = str(nhs_links)
id3 = 3
website3 = "mod"
result3 = str(latest_mod_links)
id4 = 4
website4 = "housing"
result4 = str(housing_links)
id5 = 5
website5 = "sfc"
result5 = str(sfc_links)


need_to_send_email = False
file = open('crawler.txt','w') 


cursor = cursor.execute('''SELECT result FROM crawler WHERE id = 1''')
e = cursor.fetchall()
#print(str(aviation_links))
if(e[0][0] == result1):
    print(id1 , "no change")
else:
    need_to_send_email = True
    file.write('New Aviation Links\n')
    for entry in aviation_links:
        file.write(entry + '\n')


cursor = cursor.execute('''SELECT result FROM crawler WHERE id = 2''')
e = cursor.fetchall()
#print(str(aviation_links))
if(e[0][0] == result2):
    print(id2 , "no change")
else:
    need_to_send_email = True
    file.write('\nNew NHS Links\n')
    for entry in nhs_links:
        file.write(entry + '\n') 


cursor = cursor.execute('''SELECT result FROM crawler WHERE id = 3''')
e = cursor.fetchall()
#print(str(aviation_links))
if(e[0][0] == result3):
    print(id3 , "no change")
else:
    need_to_send_email = True
    file.write('\nNew MOD Links\n')
    for entry in latest_mod_links:
        file.write(entry + '\n')



cursor = cursor.execute('''SELECT result FROM crawler WHERE id = 4''')
e = cursor.fetchall()
#print(str(aviation_links))
if(e[0][0] == result4):
    print(id4 , "no change")
else:
    need_to_send_email = True
    file.write('\nHousing Links\n')
    for entry in housing_links:
        file.write(entry + '\n')



cursor = cursor.execute('''SELECT result FROM crawler WHERE id = 5''')
e = cursor.fetchall()
#print(str(aviation_links))
if(e[0][0] == result5):
    print(id5 , "no change")
else:
    need_to_send_email = True
    file.write('\nSFC Links\n')
    for entry in sfc_links:
        file.write(entry + '\n')


file.close() 



cursor.execute('''UPDATE crawler SET result = ? WHERE id = 1 ''', 
               (result1,))
cursor.execute('''UPDATE crawler SET result = ? WHERE id = 2 ''', 
               (result2,))
cursor.execute('''UPDATE crawler SET result = ? WHERE id = 3 ''', 
               (result3,))
cursor.execute('''UPDATE crawler SET result = ? WHERE id = 4 ''', 
               (result4,))
cursor.execute('''UPDATE crawler SET result = ? WHERE id = 5 ''', 
               (result5,))
db.commit()



import smtplib
from email.mime.text import MIMEText


#if need_to_send_email:
fp = open('crawler.txt', 'r')
msg = MIMEText(fp.read())
fp.close 
msg['Subject'] = 'Websites were updated'
msg['From'] = 'xxx@gmail.com'
msg['To'] = 'yyy@gmail.com'
s = smtplib.SMTP('smtp.gmail.com', 587)
s.starttls()
s.login('xxx@gmail.com','zzz')
s.sendmail('xxx@gmail.com', 'yyy@gmail.com',msg.as_string())
s.quit()


db.close()
