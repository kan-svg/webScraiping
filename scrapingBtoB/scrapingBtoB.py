from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
import requests
import time
import re
import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import csv

class Command(BaseCommand):
    help = 'Scraping'

    def handle(self, *args, **kwargs):
        
        #CSVファイル名に当日の日付をつける
        csv_date = datetime.datetime.today().strftime("%Y%m%d")
        #CSVファイル名を保存する変数を作成
        csv_file_name = "BtoB_" + csv_date + ".csv"
        #カレントディレクトリを変更(CSVファイルのディレクトリ先を指定)
        os.chdir("/Users/kan/Desktop/sample/Webスクレイピング/スクレイピング/BtoB/")
        #open(ファイル名, mode = 'w'(書き込み), encoding='utf_8'(文字コード), errors='ignore')
        f = open(csv_file_name, "w", encoding="utf_8", errors="ignore")

        #CSVファイルへ書き込みを行う
        writer = csv.writer(f, lineterminator="\n")
        #ヘッダのリストを用意
        csv_header = ["No.","会社名","郵便番号","住所","事業内容（表の左上）","業界","電話番号","設立年月日","ホームページ","事業内容","代表氏名","法人番号","資本金","上場区分","FAX番号","事業所/店舗数","事業所","従業員"]
        #CSVファイルに1行を書き込む
        writer.writerow(csv_header)
        
        #オプションを用意
        option = Options()
        #ヘッドレスモードの設定を付与
        option.add_argument('--headless')
        
        # クローリング先一覧
        urlBtoB = "https://b2b-ch.infomart.co.jp/company/search/top.page"

        # ヘッダー設定
        headers = {
            "User-Agent": "Mozilla/.... Chrome/.... Safari/...."
        }
        
        # ページ数計算
        soupBtoB = BeautifulSoup(requests.get(urlBtoB, headers = headers).content, 'html.parser')
        maxcases = int(soupBtoB.select('#maxNum')[0].text.replace(",",""))
        cases = int(maxcases / 20)
        
        #webページ起動
        driver = webdriver.Chrome("/Users/kan/Desktop/sample/Webスクレイピング/スクレイピング/chromedriver",options=option)
        driver.get(urlBtoB)
        time.sleep(1)
        
        # スプレッドシートに出力するための変数iを定義
        i = 1

        # クローラー（BtoB）
        for num in range(cases):
            
            # 現在表示しているページのソースコードを取得
            sourceBtoB = driver.page_source
            # HTMLパース
            soupBtoB = BeautifulSoup(sourceBtoB,'html.parser')

            # 全案件リスト取得
            try:
                elemsBtoB = soupBtoB.select(".content_inner > section > div")
            except IndexError:
                print("IndexError")

            for elemBtoB in elemsBtoB:
                # スクレピング間隔：3秒
                time.sleep(3)

                # 変数初期化
                companyName = "-"
                detailsUrl = ""
                postalCode = ""
                address = "-"
                businessContent1 = "-"
                industries = []
                industry = "-"
                phoneNumber = "-"
                establishmentDate = "-"
                homePage = "-"
                businessContent2 = "-"
                representativeName = "-"
                corporateNumber = "-"
                capital = "-"
                listingClassification = "-"
                faxNumber = "-"
                storesNumber = "-"
                office = "-"
                employees = "-"

                # 会社名取得
                try:
                    companyName = elemBtoB.select(".lnkCompanyName")[0].get_text(strip=True)
                except Exception:
                    pass

                # 詳細ページURL取得
                try:
                    detailsUrl = elemBtoB.select(".lnkCompanyName")[0].attrs["href"].replace("..","")
                    detailsUrl = "https://b2b-ch.infomart.co.jp/company" + detailsUrl
                except IndexError:
                    print("url IndexError")                    
                    
                # HTMLパース
                soup = BeautifulSoup(requests.get(detailsUrl, headers = headers).content, 'html.parser')
                
                time.sleep(1)
                
                # 郵便番号取得
                try:
                    postalCode = soup.select('#lblCompanyZip')[0].text
                    if postalCode == "":
                        postalCode = "-"                        
                except Exception:
                    pass
                
                # 住所取得
                try:
                    address = soup.select('#lblCompanyAddress')[0].text
                    if address == "":
                        address = "-" 
                except Exception:
                    pass

                # 事業内容（表の左上）取得
                try:
                    businessContent1 = soup.select('#lblCompanyPr')[0].text
                    if businessContent1 == "":
                        businessContent1 = "-" 
                except Exception:
                    pass
                                
                # 業界取得
                try:
                    industries = soup.select(".co-detail-ind > a")
                    theIndustry  = []
                    for industry in industries:
                        industry = industry.text
                        theIndustry.append(industry)

                    industry = ",".join(theIndustry)
                    if industry == "":
                        industry = "-"
                except Exception:
                    pass                
                
                # 電話番号取得
                try:
                    phoneNumber = soup.select('#lblPhone')[0].text
                    if phoneNumber == "":
                        phoneNumber = "-"
                except Exception:
                    pass

                # 設立年月日取得
                try:
                    establishmentDate = soup.select('#lblFound')[0].text
                    if establishmentDate == "":
                        establishmentDate = "-"
                except Exception:
                    pass
                
                # ホームページ取得
                try:
                    homePage = soup.select('#spnUrl')[0].text
                    if homePage == "":
                        homePage = "-"
                except Exception:
                    pass
                
                # 事業内容取得
                try:
                    businessContent2 = soup.select('#lblCompanyProfile')[0].text
                    if businessContent2 == "":
                        businessContent2 = "-"
                except Exception:
                    pass
                
                # 代表氏名取得
                try:
                    representativeName = soup.select('#lblRepresentName')[0].text
                    if representativeName == "":
                        representativeName = "-"
                except Exception:
                    pass
                
                # 法人番号取得
                try:
                    corporateNumber = soup.select('#lblCorpGenuineId')[0].text
                    if corporateNumber == "":
                        corporateNumber = "-"
                except Exception:
                    pass
                
                # 資本金取得
                try:
                    capital = soup.select('#lblCapital')[0].text
                    if capital == "":
                        capital = "-"
                except Exception:
                    pass
                
                # 上場区分取得
                try:
                    listingClassification = soup.select('#lblListedKBN')[0].text
                    if listingClassification == "":
                        listingClassification = "-"
                except Exception:
                    pass
                
                # FAX番号取得
                try:
                    faxNumber = soup.select('#lblFax')[0].text
                    if faxNumber == "":
                        faxNumber = "-"
                except Exception:
                    pass
                
                # 事業所/店舗数取得
                try:
                    storesNumber = soup.select('#lblNumberStore')[0].text
                    if storesNumber == "":
                        storesNumber = "-"
                except Exception:
                    pass
                
                # 事業所取得
                try:
                    office = soup.select('#lblStoreInfo')[0].text
                    if office == "":
                        office = "-"
                except Exception:
                    pass
                
                # 従業員取得
                try:
                    employees = soup.select('#lblNumberEmp')[0].text
                    if employees == "":
                        employees = "-"
                except Exception:
                    pass
                
                time.sleep(1)
                
                csvlist = []
                time.sleep(1)
                csvlist.append(i)
                csvlist.append(companyName)
                csvlist.append(postalCode)
                csvlist.append(address)
                csvlist.append(businessContent1)
                csvlist.append(industry)
                csvlist.append(phoneNumber)
                csvlist.append(establishmentDate)
                csvlist.append(homePage)
                csvlist.append(businessContent2)
                csvlist.append(representativeName)
                csvlist.append(corporateNumber)
                csvlist.append(capital)
                csvlist.append(listingClassification)
                csvlist.append(faxNumber)
                csvlist.append(storesNumber)
                csvlist.append(office)
                csvlist.append(employees)
                
                #writerow()に対してcsvlistを渡して、1行の情報をCSVファイルに書き込む
                writer.writerow(csvlist)

                i = i+1
                
            #次のページのURLを取得
            next_link = driver.find_element_by_xpath('//div[@class="page-sort only_pc"]/div/div/span[@class="next"]/a')                
            #次のページのURLでブラウザをオープン
            next_link.click()

            time.sleep(3)
            
        #open()で開いたファイルオブジェクトを閉じる
        f.close()
        #ブラウザを閉じる
        driver.close()
