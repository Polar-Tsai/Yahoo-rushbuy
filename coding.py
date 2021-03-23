import pandas as pd
import os
import time
import requests
from bs4 import BeautifulSoup
import re

# 將 localtime 格式化為 %Y (2019)
local_year = time.strftime("%Y", time.localtime())
# 將 localtime 格式化為 %m%d (1203)
local_date = time.strftime("%m%d", time.localtime())
# 將 localtime 格式化為 _%H-%M-%S (_時-分-秒）
local_time = time.strftime("_%H-%M-%S", time.localtime())

base = "yahoo!shp" + "/" + str(local_year) + "/" + str(local_date)

if not os.path.exists(base):
    os.makedirs(base)

# 存成pandas
# I
table = {
    "商品名稱" : [],
    "商品編號" : [],
    "商品價格" : [],
    "商品連結" : []
}


# 母連結
url = "https://tw.buy.yahoo.com/rushbuy"

# 找出html並篩選出欲取得資料
response = requests.get(url, verify = False)
# print(response.status_code) # 網頁顯示正常: 200
html = BeautifulSoup(response.text)
# print(html)

# 時段檔次顯示(待用for-in)
Time_Wrappers = html.find_all("div", class_ = "RushbuyItemContainer__startTime___CdUpb")

for tw in Time_Wrappers:
    print(tw.text)
## 時段跑不出來
    # 顯示商品資料，參考tabelog
    rs = html.find_all("li", class_ = "RushbuyItem__RushbuyItem___3uXsE")

    for texts in rs:
        name = texts.find("h3", class_ = "RushbuyItem__promotionTitle___3aNWT")
        print("商品名稱:", name.text)
        prices = texts.find("div", class_ = "RushbuyItem__priceInfor___2o7VL")
        # 抓子連結
        link = texts.find("a")
        print("商品連結:", link["href"])   
        pno = link["href"].split("=")[-1]
        print("商品編號:", pno)
        table["商品名稱"].append(name.text)
        table["商品連結"].append(link["href"])
        table["商品編號"].append(pno)
        for price in prices:
            price1 = price.select("span")[0].text[1:]
            # 使用re(正規表達式)去除,
            price = re.sub(",", "", price1)
            # 解決價格出現xx的狀況
            if "X" not in str(price):
                print("商品價格:", price)
                table["商品價格"].append(price)
            else:
                # 掏出子連結進行價格萃取
                curl = link["href"]
                cresponse = requests.get(curl, verify = False)
                chtml = BeautifulSoup(cresponse.text)
                urltype = link["href"].split("?")[-1].split("=")[0]
                if urltype == "gdid":
                    cprice1 = chtml.find("div", class_ = "HeroInfo__mainPrice___1xP9H")
                else:
                    cprice1 = chtml.find("div", class_ = "HeroInfo__mainPrice___H9A5r")
                # print(urltype)
                cprice = re.sub(",", "", cprice1.text[1:])
                print("商品價格:", cprice)
            # II
                table["商品價格"].append(cprice)

        print("=" * 20)
# 存csv檔
fn = base + "/" + str(local_time) + ".csv"
df = pd.DataFrame(table)
df.to_csv(fn, encoding = "utf-8", index = False)
