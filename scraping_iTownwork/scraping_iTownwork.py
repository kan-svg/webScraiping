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
        csv_file_name = "iTownwork" + csv_date + ".csv"
        #カレントディレクトリを変更(CSVファイルのディレクトリ先を指定)
        os.chdir("/Users/kan/Desktop/sample/Webスクレイピング/スクレイピング/iTownwork/")
        #open(ファイル名, mode = 'w'(書き込み), encoding='utf_8'(文字コード), errors='ignore')
        f = open(csv_file_name, "w", encoding="utf_8", errors="ignore")

        #CSVファイルへ書き込みを行う
        writer = csv.writer(f, lineterminator="\n")
        #ヘッダのリストを用意
        csv_header = ["No.","大ジャンル","小ジャンル","掲載名","フリガナ","電話番号","FAX番号","住所","アクセス","駐車場","現金以外の支払い方法","ホームページ","E-mailアドレス","業種","休業日","予約"]
        #CSVファイルに1行を書き込む
        writer.writerow(csv_header)
        
        #オプションを用意
        option = Options()
        #ヘッドレスモードの設定を付与
        option.add_argument('--headless')
        
        # クローリング先一覧
        urlitp = "https://itp.ne.jp/"

        # ヘッダー設定
        headers = {
            "User-Agent": "Mozilla/.... Chrome/.... Safari/...."
        }
        
        # ページ数計算
        soupitp = BeautifulSoup(requests.get(urlitp, headers = headers).content, 'html.parser')
        
        #webページ起動
        driver = webdriver.Chrome("/Users/kan/Desktop/sample/Webスクレイピング/スクレイピング/chromedriver",options=option)
        driver.get(urlitp)
        time.sleep(1)
        
        # csvに出力するための変数iを定義
        i = 1
        
        # 変数初期化
        genreL = "-"
        genreS = "-"
        companyName = "-"
        ruby = "-"
        phoneNumber = "-"
        faxNumber = "-"
        address = "-"
        access = "-"
        parkingLot = "-"
        payment = "-"
        homePage = "-"
        email = "-"
        industries = "-"
        holiday = "-"
        reservation = "-"
        
        # ボタンクリック
        main_link = driver.find_element_by_class_name("o-top-genre-list-button")
        main_link.click()
        time.sleep(1)

        links = driver.find_elements_by_class_name("a-radio-check-pill-button__label")
        links_length = len(links)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #   大ジャンルをクリック
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        for num1 in range(links_length):
            # スクレピング間隔：1秒
            time.sleep(1)

            links = driver.find_elements_by_class_name("a-radio-check-pill-button__label")
            time.sleep(1)
            
            genreL = links[num1].text.strip()
            time.sleep(1)
            
            links[num1].click()
            time.sleep(1)

            nextLinks = driver.find_elements_by_class_name("a-tag-button")
            nextLinks_length = len(nextLinks)
            time.sleep(1)
            
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            #   小ジャンルをクリック
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            for num2 in range(nextLinks_length):
                # スクレピング間隔：1秒
                time.sleep(1)

                nextLinks = driver.find_elements_by_class_name("a-tag-button")
                time.sleep(1)
                
                genreS = nextLinks[num2].text.strip()
                time.sleep(1)
                
                nextLinks[num2].click()
                time.sleep(2)
                
                maxcases = int(driver.find_element_by_class_name("o-result-body__total-hits").text.replace("件",""))
                cases = int(maxcases/20)
                
                for num3 in range(cases):
                    # スクレピング間隔：1秒
                    time.sleep(1)

                    elemsItp = driver.find_elements_by_class_name("o-result-article-list__item")

                    # さらに表示ボタンの存在チェック
                    try:
                        furtherDisplay = driver.find_elements_by_class_name("m-read-more")                
                    except:
                        furtherDisplay = 0

                    if len(furtherDisplay) > 0:
                        furtherDisplay[0].click()
                        time.sleep(1)

                        for num4 in range(20):
                            # スクレピング間隔：1秒
                            time.sleep(1)

                            num5 = num3*20 + num4

                            # 詳細ページURL取得
                            try:
                                detailsUrl = elemsItp[num5].find_element_by_tag_name("a").get_attribute("href")                   
                                detailsUrl = detailsUrl + "shop/"
                            except IndexError:
                                print("url IndexError")                    

                            # HTMLパース
                            soupItp = BeautifulSoup(requests.get(detailsUrl, headers = headers).content, 'html.parser')
                            time.sleep(1)

                            # タウンワークのテンプレか判定
                            try:
                                templateJudgment = soupItp.select(".itp-logo > a")[0].text
                            except:
                                templateJudgment = ""

                            if templateJudgment == "iタウンページ":

                                # 掲載名取得
                                try:
                                    companyName = soupItp.find('dt', text="掲載名").parent
                                    companyName = companyName.select("dd")[0].get_text(strip=True)
                                    if companyName == "":
                                        companyName = "-" 
                                except:
                                    companyName = "-" 

                                # フリガナ取得
                                try:
                                    ruby = soupItp.find('dt', text="フリガナ").parent
                                    ruby = ruby.select("dd")[0].get_text(strip=True)
                                    if ruby == "":
                                        ruby = "-" 
                                except:
                                    ruby = "-"

                                # 電話番号取得
                                try:
                                    phoneNumber = soupItp.select(".tell")[0].get_text(strip=True)
                                    if phoneNumber == "":
                                        phoneNumber = "-" 
                                except:
                                    phoneNumber = "-"

                                # FAX番号取得
                                try:
                                    faxNumber = soupItp.find('dt', text="FAX番号").parent
                                    faxNumber = faxNumber.select("dd")[0].get_text(strip=True)
                                    if faxNumber == "":
                                        faxNumber = "-" 
                                except:
                                    faxNumber = "-" 

                                # 住所取得
                                try:
                                    address = soupItp.find('dt', text="住所").parent
                                    address = address.select("dd > p")[0].get_text(strip=True)
                                    if address == "":
                                        address = "-"
                                except:
                                    address = "-"

                                # アクセス取得
                                try:
                                    access = soupItp.find('dt', text="アクセス").parent
                                    access = access.select("dd")[0].get_text(strip=True)
                                    if access == "":
                                        access = "-"
                                except:
                                    access = "-"

                                # 駐車場取得
                                try:
                                    parkingLot = soupItp.find('dt', text="駐車場").parent
                                    parkingLot = parkingLot.select("dd")[0].get_text(strip=True)
                                    if parkingLot == "":
                                        parkingLot = "-"
                                except:
                                    parkingLot = "-"

                                # 現金以外の支払い方法取得
                                try:
                                    payment = soupItp.find('dt', text="現金以外の支払い方法").parent
                                    payment = payment.select("dd")[0].get_text(strip=True)
                                    if payment == "":
                                        payment = "-"
                                except:
                                    payment = "-"

                                # ホームページ取得
                                try:
                                    homePage = soupItp.find('dt', text="ホームページ").parent
                                    homePage = homePage.select("dd > div >p >a")[0].attrs["href"]
                                    if homePage == "":
                                        homePage = "-"
                                except:
                                    homePage = "-"

                                # E-mailアドレス取得
                                try:
                                    email = soupItp.find('dt', text="E-mailアドレス").parent
                                    email = email.select("dd > div >p >a")[0].attrs["href"].replace("mailto:","")
                                    if email == "":
                                        email = "-"
                                except:
                                    email = "-"

                                # 業種取得
                                try:
                                    industries = soupItp.find('dt', text="業種").parent
                                    industries = industries.select("dd")[0].get_text(strip=True)
                                    if industries == "":
                                        industries = "-"
                                except:
                                    industries = "-"

                                # 営業時間取得
                                try:
                                    businessHours = soupItp.find('dt', text="営業時間").parent
                                    businessHours = businessHours.select("dd > p")[0].get_text(strip=True)
                                    if businessHours == "":
                                        businessHours = "-"
                                except:
                                    businessHours = "-"

                                # 休業日取得
                                try:
                                    holiday = soupItp.find('dt', text="休業日").parent
                                    holiday = holiday.select("dd")[0].get_text(strip=True)
                                    if holiday == "":
                                        holiday = "-"
                                except:
                                    holiday = "-"

                                # 予約取得
                                try:
                                    reservation = soupItp.find('dt', text="予約").parent
                                    reservation = reservation.select("dd")[0].get_text(strip=True)
                                    if reservation == "":
                                        reservation = "-"
                                except:
                                    reservation = "-"

                                csvlist = []
                                time.sleep(1)
                                csvlist.append(i)
                                csvlist.append(genreL)
                                csvlist.append(genreS)
                                csvlist.append(companyName)
                                csvlist.append(ruby)
                                csvlist.append(phoneNumber)
                                csvlist.append(faxNumber)
                                csvlist.append(address)
                                csvlist.append(access)
                                csvlist.append(parkingLot)
                                csvlist.append(payment)
                                csvlist.append(homePage)
                                csvlist.append(email)
                                csvlist.append(industries)
                                csvlist.append(holiday)
                                csvlist.append(reservation)

                                #writerow()に対してcsvlistを渡して、1行の情報をCSVファイルに書き込む
                                writer.writerow(csvlist)

                                i = i+1
                    else:
                        break

                #ブラウザを閉じる
                driver.close()
                time.sleep(1)

                #webページ起動
                driver = webdriver.Chrome("/Users/kan/Desktop/sample/Webスクレイピング/スクレイピング/chromedriver",options=option)
                driver.get(urlitp)
                time.sleep(1)

                # ボタンクリック
                main_link = driver.find_element_by_class_name("o-top-genre-list-button")
                main_link.click()
                time.sleep(1)

                links = driver.find_elements_by_class_name("a-radio-check-pill-button__label")
                links[num1].click() 
                time.sleep(1)
                                            
        #open()で開いたファイルオブジェクトを閉じる
        f.close()
        #ブラウザを閉じる
        driver.close()
