from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import time
import re
import datetime
import os
from ...models import Project

class Command(BaseCommand):
    help = 'Scraping'

    def handle(self, *args, **kwargs):

        # オプションを用意
        option = Options()
        # ヘッドレスモードの設定を付与
        option.add_argument('--headless')

        # ChromeのWebDriverオブジェクトを作成
        driver = webdriver.Chrome("/Users/kan/Desktop/sample/Webスクレイピング/スクレイピング/chromedriver",options=option)

        # webページ起動
        driver.get('https://app.shufti.jp/')
        time.sleep(3)

        login_button = driver.find_element_by_link_text("ログイン")
        login_button.click()
        time.sleep(3)

        USERNAME = "gkan46003@gmail.com"
        PASSWORD = "gkan46003admin"

        time.sleep(1)

        # ユーザ名入力
        username_input = driver.find_element_by_xpath('//input[@id="username"]')
        username_input.send_keys(USERNAME)
        time.sleep(1)

        # パスワード入力
        password_input = driver.find_element_by_xpath('//input[@id="password"]')
        password_input.send_keys(PASSWORD)
        time.sleep(1)

        # ログイン
        username_input.submit()
        time.sleep(3)

        # 全案件表示
        job_search = driver.find_element_by_link_text("仕事を探す")
        time.sleep(1)
        job_search.click()
        time.sleep(3)

        driver.implicitly_wait(10)

        # HTMLパース
        sourceShufti = driver.page_source
        soupShufti = BeautifulSoup(sourceShufti,'html.parser')
        time.sleep(3)

        # ページ数計算
        cases = int(soupShufti.select(".c-pc-pagination > li")[-2].text)

        for num in range(cases):

            # クローリングページ遷移
            sourceShufti = driver.page_source

            # HTMLパース
            soupShufti = BeautifulSoup(sourceShufti,'html.parser')
            time.sleep(3)

            # 案件一覧取得
            elemsShufti = soupShufti.select(".jobs-lists > section")
            time.sleep(3)

            for elemShufti in elemsShufti:
                # スクレピング間隔：3秒
                time.sleep(3)

                # PR判定
                prJudgment = elemShufti.attrs["class"]
                if prJudgment == ['job-info']:
                    # 変数初期化
                    category = []
                    subCategory = []
                    rewardLower = 0
                    rewardUpper = 0
                    rewardCharacterUnit = 0
                    projectName = ""
                    workStyle = []
                    contents = []
                    sponsor = "シュフティ"
                    sponsorUrl = "https://app.shufti.jp/"    

                    # 案件名取得
                    projectName = elemShufti.select(".job-info-heading > h3")[0].text

                    # 仕事形式取得
                    workStyle = elemShufti.select(".c-pc-label")[0].get_text(strip=True)

                    if workStyle == 'プロジェクト':
                        workStyle = '固定報酬'


                    #報酬下限,上限取得
                    rewardLower = elemShufti.select(".job-info-text-bold")[0].text.replace(',','').replace('円','').replace(' / 件','')
                    rewardUpper = elemShufti.select(".job-info-price-bold")[0].text.replace(',','').replace('円','').replace(' / 件','')
                    time.sleep(1)

                    if '件' in rewardUpper:
                        rewardLower = rewardUpper
                        
                    rewardLower = int(rewardLower)
                    rewardUpper = int(rewardUpper)
                    time.sleep(1)

                    #詳細URL
                    url = elemShufti.select("a")[0].attrs["href"]
                    detailsUrl = "https://app.shufti.jp" + url

                    driver.get(detailsUrl)

                    time.sleep(3)

                    # クローリングページ遷移
                    source = driver.page_source

                    time.sleep(3)

                    # HTMLパース
                    soup = BeautifulSoup(source,'html.parser')

                    time.sleep(3)

                    # 現在時刻取得
                    date = datetime.datetime.now()
                    # 掲載日に現在時刻を格納
                    publicationDate = datetime.date(date.year, date.month, date.day)

                    time.sleep(3)

                    # カテゴリー取得
                    try:
                        category = soup.select(".breadcrumb > li:nth-of-type(3) > a > span")[0].text
                    except IndexError:
                        category = ""

                    time.sleep(3)

                    try:
                        subCategory = soup.select(".breadcrumb > li:nth-of-type(4) > a > span")[0].text
                    except IndexError:
                        subCategory = ""

                    time.sleep(3)

                    # 文字単価（ライティング案件）
                    if category == 'ライティング':
                        rewardUpper = int(soup.select(".jobs-view-summary-reward")[0].text.replace(',', '').replace('円', '').replace(' / 件',''))
                        rewardLower = rewardUpper

                        characterMinimum = int(soup.select(".jobs-view-rule >dl >dd >span")[0].text.replace(',', '').replace('文字', ''))

                        rewardCharacterUnit = float(float(rewardUpper) / float(characterMinimum))
                        # 小数点第二位を四捨五入
                        rewardCharacterUnit = round(rewardCharacterUnit, 1)
                    else:
                        rewardCharacterUnit = 0


                    # コンテンツ内容取得
                    try:
                        elemContents = soup.select(".l-pc-main >div:nth-of-type(3) >section")[0]
                        time.sleep(3)

                        for i in elemContents.select("br"):
                            i.replace_with("\n")
                        time.sleep(3)

                        contents = elemContents.get_text("\n")
                        time.sleep(3)

                        contents = contents.replace('\n\n','\n')
                        time.sleep(3)

                    except IndexError:
                        print("コンテンツ取得エラー")
                    time.sleep(3)


                    # データベースへ保存
                    product = Project(
                        project_name = projectName,
                        reward_lower = rewardLower,
                        reward_upper = rewardUpper,
                        reward_charunit = rewardCharacterUnit,
                        category = category,
                        sub_category = subCategory,
                        work_style = workStyle,
                        contents = contents,
                        publication_date = publicationDate,
                        sponsor = sponsor,
                        sponsor_link = sponsorUrl,
                        project_link = detailsUrl,
                        )   
                    product.save()
                    
                    # 案件一覧画面へ戻る
                    driver.back()
                    time.sleep(3)

            if int(num + 1) != cases:
                # 次のページのURLを取得
                next_link = driver.find_element_by_xpath('//li[@class="right-arrow"]/a')

                # 次のページのURLでブラウザをオープン
                next_link.click()
                time.sleep(3)  


        # ブラウザを閉じる
        driver.close()
