import requests
from lxml import html

response = requests.get("https://www.worldometers.info/coronavirus/")
byte_data = response.content 
source_code = html.fromstring(byte_data) 
tree = source_code.xpath('//*[@id="maincounter-wrap"]/div/span')
tree2 = source_code.xpath('//*[@id="maincounter-wrap"][2]/div/span')

response2 = requests.get("https://www.cdc.gov/coronavirus/2019-ncov/cases-in-us.html")
byte_data2 = response2.content 
source_code2 = html.fromstring(byte_data2) 
tree3 = source_code2.xpath('/html/body/div[6]/main/div[3]/div/div[3]/div[1]/div/div/div/div[2]/table/tbody/tr[1]/td')
tree4 = source_code2.xpath('/html/body/div[6]/main/div[3]/div/div[3]/div[1]/div/div/div/div[2]/table/tbody/tr[3]/td')
print("Global Cases: ",tree[0].text_content()) 
print("Global Deaths: ",tree2[0].text_content())
print("United States Cases: ",tree3[0].text_content())
print("US Pending Cases: ",tree4[0].text_content())
