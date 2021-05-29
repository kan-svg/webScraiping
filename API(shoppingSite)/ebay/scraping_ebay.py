# eBayのTrading APIを使ってeBayの未発送の注文情報を取得する方法
from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import datetime
import os
import csv
import time
import re
import pandas as pd
import requests

#CSVファイル名に当日の日付をつける
csv_date = datetime.datetime.today().strftime("%Y%m%d")
#CSVファイル名を保存する変数を作成
csv_file_name = "ebay_order_" + csv_date + ".csv"
#カレントディレクトリを変更(CSVファイルのディレクトリ先を指定)
os.chdir("/Users/kan/Desktop/sample/Webスクレイピング/スクレイピング/ebay")
#open(ファイル名, mode = 'w'(書き込み), encoding='utf_8'(文字コード), errors='ignore')
f = open(csv_file_name, "w", encoding="utf_8", errors="ignore")

#CSVファイルへ書き込みを行う
writer = csv.writer(f, lineterminator="\n")
#ヘッダのリストを用意
#csv_header = ["売上日","Order No.","顧客名","Item No.","Item Name","Condition","Custom Label","受取人","売上金額","送料","受取人住所","Sales record number","amazonのURL","楽天の最安値URL","Yahooの最安値URL"]
csv_header = ["売上日","Order No.","顧客名","Item No.","Item Name","Condition","Custom Label","受取人","売上金額","送料","受取人住所","Sales record number","amazonのURL","楽天の最安URL","Yahooの最安値URL"]
#CSVファイルに1行を書き込む
writer.writerow(csv_header)

time.sleep(1)

#アカウント情報を変数に格納
YOUR_APPID = "Tsuyoshi-ando-PRD-77a9ffde4-0c07d9d6"
YOUR_DEVID = "687a9377-cbe4-4fc7-8c56-021e8708914f"
YOUR_CERTID = "PRD-7a9ffde4b312-7c9b-4655-becc-3b16"
YOUR_AUTH_TOKEN = "AgAAAA**AQAAAA**aAAAAA**NfWuYA**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6ANmYKpC5CHpQSdj6x9nY+seQ**/EUGAA**AAMAAA**ImMyKZgYbdpUdS86NDc0TyCT6iu91cVUMLAB9U/rxeUNh2mXlU+KN70NWGOj3ZFzoI8RNrvyQqGIVAzGxkHpGw4LeH3Dcn5+1CBuwXEY16/8XqEHGuNfsQVm4sSxXTUpO09Cdlz80wr4IWM8hvraIkZiuMCqb6fJIvOSdkWQZpvfrOGQmF61P7s5Y+wUTcOfz6tG6/hUfT4Gzl8tpDFmBv28Wx36zvhIax62qEO+m/tny+4uKcXr7nBLiHkoHk0HnskLJff/Tv6TLde8VOkpKz6BFMHCNC/N5BoyBxUWDHTQ9JadedI+xw/5hmtSKQ25nmukUwplGHG29RFMwIj72GZMfbBMF8kGKo8oSBI3p3llMl7uDW05e4Q7cWk6NhrKoR41EM4HPIMmm6NN9ZuAKkPniW4zusW9EhgzWn/msI/Y079CuOGgPW0gSLZEskrqk12oqZPrGe3VXA+j7+cwwLQdsXtATZLz438bTVy6fNPxXTepBIsTO9KiNxtssLAMMuAbYcVgkwlhOvEmLCk/cBvKHxBLRb5ZS8Xk2D2fwtaUZnmpLLIOYqw8fHzjrPTzrZIqqLF2D6U6HPTeKML4MBuZZ+pzW3j8myPOsAsq86dPKIUneHEPxNa2fRx+wo7nuwfc9kLa3QMvsWWB1ASOhd1F+WOtpwHcXNCwakKmq9b1T+ahyVyCsrjp0g0SblnTSbkgSDcYIfQOSDJNito5U3DuHxBVCambXVIiEW1Ou2nh3XQxIZnGdNf/Va6I6Ge8"

time.sleep(1)

#オプションを用意
option = Options()
#ヘッドレスモードの設定を付与
option.add_argument('--headless')

time.sleep(1)

try:
    # ebayのapiにアクセス
    api = Trading(appid=YOUR_APPID, devid=YOUR_DEVID, certid=YOUR_CERTID, token=YOUR_AUTH_TOKEN)

    #注：現在、フィルターは過去90日間のデータのみを返します。
    # 注文データ取得
    api.execute('GetOrders', {
        #"OrderStatus": "Completed", # 支払い済みの注文のみに絞り込み
        #"OrderRole": "Seller", # セラーの注文のみに絞り込み
        'NumberOfDays': 8,
    })
    time.sleep(1)
    
    # 取得した注文データから各種データを取得
    for order in api.response.reply.OrderArray.Order:
        
        time.sleep(3)
        
        for txn in order.TransactionArray.Transaction:
            # Transaction Type : https://dev.commissionfactory.com/V1/Affiliate/Types/Transaction/
            data = {
                "created_time" : order.CreatedTime, # 売上日
                "order_No": order.OrderID, # Order No.
                "buyer_userName": order.BuyerUserID, #顧客名(名)                
                "item_No" : txn.Item.ItemID, # Item No.
                "item_name": txn.Item.Title, # Item Name
                "item_customLabel": txn.Item.SKU, # Custom Label
                "item_shippingName": order.ShippingAddress.Name, # 受取人
                "order_amountPaid": order.AmountPaid, # 売上金額
                "order_recordNumber": order.ShippingDetails.SellingManagerSalesRecordNumber # Sales record number
                }
            
            time.sleep(1)
            
            created_Time = str(data["created_time"])
            created_Time = datetime.datetime.strptime(created_Time, '%Y-%m-%d %H:%M:%S')
            
            time.sleep(1)
            
            try:
                item_condition = txn.Item.ConditionID #Condition
            except:
                item_condition = 1000 #Condition
            
            time.sleep(1)
                        
            if int(item_condition) == 1000:
                item_condition = "New"
            elif int(item_condition) == 1500:
                item_condition = "New other"
            elif int(item_condition) == 1750:
                item_condition = "New with defects"
            elif int(item_condition) == 2000:
                item_condition = "Certified refurbished"
            elif int(item_condition) == 2500:
                item_condition = "Seller refurbished"
            elif int(item_condition) == 2750:
                item_condition = "Like New"
            elif int(item_condition) == 3000:
                item_condition = "Used"
            elif int(item_condition) == 4000:
                item_condition = "Very Good"
            elif int(item_condition) == 5000:
                item_condition = "Good"            
            elif int(item_condition) == 6000:
                item_condition = "Acceptable"            
            else:
                item_condition = "For parts or not working"            
            
            
            if order.ShippingServiceSelected.ShippingServiceCost != "":
                order_shippingCost = order.ShippingServiceSelected.ShippingServiceCost
            else:
                order_shippingCost = 0
            
            ship_address1 = str(order.ShippingAddress.Street1)
            ship_address2 = str(order.ShippingAddress.Street2)
            ship_city = str(order.ShippingAddress.CityName)
            ship_state = str(order.ShippingAddress.StateOrProvince)
            ship_postal_code = str(order.ShippingAddress.PostalCode)
            ship_country = str(order.ShippingAddress.Country)
            
            order_shippingAddress = ship_address1 + ship_address2 + " " + ship_city + " " + ship_state + " " + ship_postal_code + " " + ship_country
            
            amazon_url = "https://www.amazon.co.jp/s?k=" + data["item_customLabel"] + "&__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&ref=nb_sb_noss"
                        
            # クローリング先
            urlMnsearch = "https://mnsearch.com/item?kwd=" + data["item_customLabel"]
            
            #webページ起動
            driver = webdriver.Chrome("/Users/kan/Desktop/sample/Webスクレイピング/スクレイピング/chromedriver",options=option)
            driver.get(urlMnsearch)
            time.sleep(1)
            
            try:
                rakuten_url = driver.find_element_by_link_text("楽天市場").get_attribute("href")
            except:
                rakuten_url = "None"
                
            try:
                yahoo_url = driver.find_element_by_link_text("Yahooショッピング").get_attribute("href")
            except:
                yahoo_url = "None"
            
            time.sleep(1)
            
            driver.close()
            
            time.sleep(1)
            
            #csvに書き込む
            csvlist = []
            csvlist.append(created_Time)
            csvlist.append(data["order_No"])
            csvlist.append(data["buyer_userName"])
            csvlist.append(data["item_No"])
            csvlist.append(data["item_name"])
            csvlist.append(item_condition)
            csvlist.append(data["item_customLabel"])
            csvlist.append(data["item_shippingName"])
            csvlist.append(data["order_amountPaid"].value)
            csvlist.append(order_shippingCost.value)
            csvlist.append(order_shippingAddress)
            csvlist.append(re.sub(r"\D", "", data["order_recordNumber"]))
            csvlist.append(amazon_url)
            csvlist.append(rakuten_url)
            csvlist.append(yahoo_url)
            
            #writerow()に対してcsvlistを渡して、1行の情報をCSVファイルに書き込む
            writer.writerow(csvlist)
            
            
    #open()で開いたファイルオブジェクトを閉じる
    f.close()  

    #日付並び替え
    data = pd.read_csv(r'/Users/kan/Desktop/sample/Webスクレイピング/スクレイピング/ebay/ebay_order_20210528.csv')
    data['売上日'] = pd.to_datetime(data['売上日'], infer_datetime_format= True)
    data.sort_values(by = '売上日', ascending = False, inplace = True)     
    
except ConnectionError as e:
    print(e)
