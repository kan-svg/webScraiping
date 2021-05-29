from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
import requests
import time
import re
import datetime
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class Command(BaseCommand):
    help = 'Scraping'

    def handle(self, *args, **kwargs):
        
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
 
        # 秘密鍵（JSONファイル）のファイル名を入力
        credentials = ServiceAccountCredentials.from_json_keyfile_name('sales-list-313306-b2642fcee6f9.json', scope)
        gc = gspread.authorize(credentials)

        # 「キー」でワークブックを取得
        SPREADSHEET_KEY = '15t87NoXzrI9Ugu07srgQcDaXkSCg2UBe4dfK31o-K6I'
        wb = gc.open_by_key(SPREADSHEET_KEY)
        ws = wb.sheet1  # 一番左の「シート1」を取得
        
        # クローリング先一覧
        urlTabelog = "https://tabelog.com/fukuoka/rstLst/"

        # ヘッダー設定
        headers = {
            "User-Agent": "Mozilla/.... Chrome/.... Safari/...."
        }
        
        # ページ数計算
        soupTabelog = BeautifulSoup(requests.get(urlTabelog, headers = headers).content, 'html.parser')
        maxcases = int(soupTabelog.select('.c-page-count__num > strong')[2].text)
        cases = int(maxcases / 20)
        
        # スプレッドシートに出力するための変数iを定義
        i = 1

        # クローラー（食べログ）
        for num in range(cases):
        
            # クローリングページ遷移
            url = urlTabelog + str(num + 1) +'/'
            # HTMLパース
            soupTabelog = BeautifulSoup(requests.get(url, headers = headers).content, 'html.parser')

            # 全案件リスト取得
            try:
                elemsTabelog = soupTabelog.select(".js-rstlist-info > div.list-rst")
            except IndexError:
                print("IndexError")

            for elemTabelog in elemsTabelog:
                # スクレピング間隔：3秒
                time.sleep(3)

                # 変数初期化
                shopName = "-"
                detailsUrl = "-"
                genre = "-"
                address = "-"
                course = "-"
                dish = "-"
                drink = "-"
                useScene = "-"
                location = "-"
                service = "-"
                officialAccount = "-"
                homePage = "-"
                openingDate = "-"
                phoneNumber = "-"

                # 店名取得
                try:
                    shopName = elemTabelog.select(".list-rst__rst-name-target")[0].text
                except Exception:
                    pass

                # 詳細ページURL取得
                try:
                    detailsUrl = elemTabelog.select('a')[0].attrs["href"]
                except IndexError:
                    print("url IndexError")

                # 各店HTMLパース
                soup = BeautifulSoup(requests.get(detailsUrl, headers = headers).content, 'html.parser')

                # ジャンル取得
                try:
                    genre = soup.find('th', text="ジャンル").parent.select("td > span")[0].text
                except Exception:
                    pass

                # 住所取得
                try:
                    address = soup.select(".rstinfo-table__address")[0].text
                except Exception:
                    pass

                # コース取得
                try:
                    course = soup.find('th', text="コース").parent.select("td > p")[0].text
                except Exception:
                    pass

                # 料理取得
                try:
                    dish = soup.find('th', text="料理").parent.select("td > p")[0].text
                except Exception:
                    pass

                # ドリンク取得
                try:
                    drink = soup.find('th', text="ドリンク").parent.select("td > p")[0].text
                except Exception:
                    pass

                # 利用シーン取得
                try:
                    useScene = soup.find('th', text="利用シーン").parent.select("td > p")[0].text.replace("\n","")
                except Exception:
                    pass

                # ロケーション取得
                try:
                    location = soup.find('th', text="利用シーン").parent.select("td > p")[0].text.replace("\n","")
                except Exception:
                    pass

                # サービス取得
                try:
                    service = soup.find('th', text="サービス").parent.select("td > p")[0].text
                except Exception:
                    pass

                # 公式アカウント取得
                try:
                    officialAccount = soup.find('th', text="公式アカウント").parent.select("td > div > a")[0].attrs["href"]
                except Exception:
                    pass

                # ホームページ取得
                try:
                    homePage = soup.find('th', text="ホームページ").parent.select("td > p > a")[0].attrs["href"]
                except Exception:
                    pass

                # オープン日取得
                try:
                    openingDate = soup.find('th', text="オープン日").parent.select("td > p")[0].text
                except Exception:
                    pass

                # 電話番号取得
                try:
                    phoneNumber = soup.find('th', text="電話番号").parent.select("td > p > strong")[0].text
                except Exception:
                    pass
                
                time.sleep(1)
                
                # B列からN列まで順に出力
                ws.update_cell(i+2, 1, i)
                time.sleep(1)
                ws.update_cell(i+2, 2, shopName)
                time.sleep(1)
                ws.update_cell(i+2, 3, genre)
                time.sleep(1)
                ws.update_cell(i+2, 4, address)
                time.sleep(1)
                ws.update_cell(i+2, 5, course)
                time.sleep(1)
                ws.update_cell(i+2, 6, dish)
                time.sleep(1)
                ws.update_cell(i+2, 7, drink)
                time.sleep(1)
                ws.update_cell(i+2, 8, useScene)
                time.sleep(1)
                ws.update_cell(i+2, 9, location)
                time.sleep(1)
                ws.update_cell(i+2, 10, service)
                time.sleep(1)
                ws.update_cell(i+2, 11, officialAccount)
                time.sleep(1)
                ws.update_cell(i+2, 12, homePage)
                time.sleep(1)
                ws.update_cell(i+2, 13, openingDate)
                time.sleep(1)
                ws.update_cell(i+2, 14, phoneNumber)
                time.sleep(1)

                i = i+1
