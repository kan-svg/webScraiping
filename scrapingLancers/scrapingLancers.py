from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
from ...models import Project
import requests
import re
import datetime
import time
from selenium import webdriver

class Command(BaseCommand):
    help = 'Scraping'

    def handle(self, *args, **kwargs):
        #webページ起動
        driver = webdriver.Chrome("/Users/kan/Desktop/sample/Webスクレイピング/スクレイピング/chromedriver")
        driver.get('https://www.lancers.jp/')
        time.sleep(3)

        login_button = driver.find_element_by_link_text("ログイン")
        login_button.click()
        time.sleep(3)

        USERNAME = "versatile@magjobs.co.jp"
        PASSWORD = "MagjobS0401lancers"

        time.sleep(1)

        #ユーザ名入力
        username_input = driver.find_element_by_xpath('//input[@id="UserEmail"]')
        username_input.send_keys(USERNAME)
        time.sleep(1)

        #パスワード入力
        password_input = driver.find_element_by_xpath('//input[@id="UserPassword"]')
        password_input.send_keys(PASSWORD)
        time.sleep(1)

        #フォーム内の要素にsubmitメソッドを指定してログイン
        username_input.submit()
        time.sleep(5)
        
        job_search = driver.find_element_by_link_text("仕事を探す")

        time.sleep(3)

        job_search.click()

        time.sleep(5)
        
        driver.implicitly_wait(10)

        sourceLancers = driver.page_source
        # HTMLパース
        soupLancers = BeautifulSoup(sourceLancers,'html.parser')        
        
        # ページ数計算
        cases = int(soupLancers.select(".pager--main > li >a")[-1].text)
        
        # ヘッダー設定
        headers = {
            "User-Agent": "Mozilla/.... Chrome/.... Safari/...."
        }

        # クローラー（ランサーズ）
        for num in range(cases):
            info = num + 1
            
            sourceLancers = driver.page_source
            # HTMLパース
            soupLancers = BeautifulSoup(sourceLancers,'html.parser')
            
            # 全案件リスト取得
            try:
                elemsLancers = soupLancers.select(".c-media-list__item")
            except IndexError:
                print("IndexError")

            for elemLancers in elemsLancers:
                # スクレピング間隔：3秒
                time.sleep(3)
                
                # PR判定
                prJudgment = elemLancers.attrs["class"]
                if 'top' not in prJudgment: 
                    # 変数初期化
                    category = []
                    subCategory = []
                    rewardLower = 0
                    rewardUpper = 0
                    rewardCharacterUnit = 0
                    workStyle = []
                    contents = []
                    contentsName = []
                    contentsItem = []
                    sponsor = "ランサーズ"
                    sponsorUrl = "https://www.lancers.jp/"

                    # 詳細ページURL取得
                    try:
                        url = elemLancers.select('a[href^="/work/detail"]')[0].attrs["href"]
                    except IndexError:
                        print("url IndexError")
                        
                    # 仕事方式取得
                    workStyle = elemLancers.select(".c-badge__text")[0].text

                    # 仕事方式置換
                    if workStyle == "プロジェクト":
                        workStyle = "固定報酬"
                                        
                    # タスク案件除外
                    if workStyle != "":
                        # 報酬内容取得
                        reward = elemLancers.select(".c-media__job-price > .c-media__job-number")
                        # 報酬が数値か判定
                        if reward[0].text.replace(',','').isdigit():   
                            if len(reward) == 3:
                                # 報酬下限取得
                                rewardLower = int(reward[0].text.replace(',',''))
                                # 文字単価取得
                                rewardCharacterUnit = float(reward[2].text.replace(',',''))
                                # 報酬上限取得
                                rewardUpper = int(reward[1].text.replace(',',''))
                            elif len(reward) == 2:
                                # ライティング案件判定
                                writeJudgment = elemLancers.select(".c-media__job-unit")[0].text
                                if writeJudgment == "~":
                                    writeJudgment = elemLancers.select(".c-media__job-unit")[2].text
                                else:
                                    writeJudgment = elemLancers.select(".c-media__job-unit")[1].text
                                
                                time.sleep(1)
                                
                                if writeJudgment == "円 / 文字":
                                    # 報酬下限取得
                                    rewardLower = 0
                                    # 文字単価取得
                                    rewardCharacterUnit = float(reward[1].text.replace(',',''))
                                    # 報酬上限取得
                                    rewardUpper = int(reward[0].text.replace(',',''))
                                else:
                                    # 報酬下限取得
                                    rewardLower = int(reward[0].text.replace(',',''))
                                    # 文字単価取得
                                    rewardCharacterUnit = 0
                                    # 報酬上限取得
                                    rewardUpper = int(reward[1].text.replace(',',''))
                            else:
                                # 報酬下限取得
                                rewardLower = 0
                                # 文字単価取得
                                rewardCharacterUnit = 0
                                # 報酬上限取得
                                rewardUpper = int(reward[0].text.replace(',',''))
                        else:
                            # 報酬下限取得
                            rewardLower = 0
                            # 文字単価取得
                            rewardCharacterUnit = 0
                            # 報酬上限取得
                            rewardUpper = 0

                        # 詳細ページURL
                        detailsUrl = "https://www.lancers.jp" + url
                        
                        driver.get(detailsUrl)
            
                        time.sleep(3)

                        # クローリングページ遷移
                        source = driver.page_source

                        time.sleep(3)

                        # HTMLパース
                        soup = BeautifulSoup(source,'html.parser')

                        time.sleep(3)

                        # 案件名
                        projectName = soup.h1.get_text(strip=True).split('の仕事')[0]
                        
                        # 閲覧制限除外
                        if projectName != '閲覧制限':

                            # カテゴリー取得
                            if soup.select(".c-breadcrumb__item") != []:
                                category = soup.select(".c-breadcrumb__item")[2].get_text(strip=True).replace('の仕事', '')
                                subCategory = soup.select(".c-breadcrumb__item")[3].get_text(strip=True).replace('の仕事', '')
                            
                            # 現在時刻取得
                            date = soup.select(".p-work-detail__sub-heading-item")[0].get_text(strip=True)
                            # DATE型へ変換
                            dateChange = datetime.datetime.strptime(date, '%Y年%m月%d日')
                            publicationDate = datetime.date(dateChange.year, dateChange.month, dateChange.day)                            
                            
                            # コンテンツ内容取得
                            if soup.select(".c-definitionList > .definitionList__description") != []:
                                contentsItem = soup.select(".c-definitionList > .definitionList__description")
                                
                            # コンテンツ項目取得
                            if soup.select(".c-definitionList > .definitionList__term") != []:
                                contentsName = soup.select(".c-definitionList > .definitionList__term")
                                                            
                            #コンテンツ項目と内容を合算
                            for contentName, contentItem in zip(contentsName, contentsItem):
                                contentItem = contentItem.get_text('\n', strip=True)
                                # コンテンツ内容の表示を整理()
                                contentItem = re.sub("【", "\n【", contentItem)
                                contentName = contentName.get_text(strip=True)
                                contents.append("\n【" + contentName + "】\n" + contentItem)

                            # コンテンツリストより抽出
                            contents = '\n\n'.join(contents)
                            contents = contents.lstrip("\n")

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
                                sponsor = sponsor,
                                sponsor_link = sponsorUrl,
                                project_link = detailsUrl,
                                publication_date = publicationDate,
                                ) 
                            product.save()
                                                        
                            driver.back()
                            
                            time.sleep(3)
                                    

            if info != cases:
                #次のページのURLを取得
                next_link = driver.find_elements_by_xpath('//a[@class="pager__item__anchor"]')[-1]

                #次のページのURLでブラウザをオープン
                next_link.click()

                time.sleep(5)  
                
        #ブラウザを閉じる
        driver.close()
