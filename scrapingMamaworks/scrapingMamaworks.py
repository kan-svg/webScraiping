from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
import requests
import time
import re
import datetime
import os
from ...models import Project

class Command(BaseCommand):
    help = 'Scraping'

    def handle(self, *args, **kwargs):

        # クローリング先一覧
        urlMamaworks = "https://mamaworks.jp/list?lrj[0]="

        # ヘッダー設定
        headers = {
            "User-Agent": "Mozilla/.... Chrome/.... Safari/...."
        }


        # クローラー（ママワークス）
        for num1 in range(9):
            if num1 + 1 != 7:

                print('num1:' + str(num1))

                # クローリングページ遷移
                url = urlMamaworks + str(num1 + 1) +'&page=1'
                # HTMLパース
                soupMamaworks = BeautifulSoup(requests.get(url, headers = headers).content, 'html.parser')
                # ページ数計算
                cases = int(soupMamaworks.select('ul.pagination > li')[-1].text)

                for num2 in range(cases):

                    print('num2:' + str(num2))

                    # クローリングページ遷移
                    url = urlMamaworks + str(num1 + 1) +'&page=' + str(num2 + 1)
                    # HTMLパース
                    soupMamaworks = BeautifulSoup(requests.get(url, headers = headers).content, 'html.parser')

                    # 全案件リスト取得
                    try:
                        elemsMamaworks = soupMamaworks.select(".p-recruit-index__result-box")
                    except IndexError:
                        print("IndexError")

                    for elemMamaworks in elemsMamaworks:
                        # スクレピング間隔：3秒
                        time.sleep(3)

                        # 変数初期化
                        category = []
                        subCategory = []
                        rewardLower = 0
                        rewardUpper = 0
                        rewardCharacterUnit = 0
                        projectName = ""
                        workStyle = []
                        contents = []
                        contentsName = []
                        contentsItem = []
                        sponsor = "ママワークス"
                        sponsorUrl = "https://mamaworks.jp/"

                        # 詳細ページURL取得
                        try:
                            detailsUrl = elemMamaworks.select('a')[0].attrs["href"]
                        except IndexError:
                            print("url IndexError")

                        # 案件名取得
                        projectName = elemMamaworks.select("h2")[0].text


                        # 報酬取得
                        reward = elemMamaworks.select("section >a > p")[0].text.replace('\u3000','').replace('\u2003','')

                        # 仕事方式取得
                        if '時間単価' in reward:
                            workStyle = '時間報酬'
                        elif '時間報酬' in reward:
                            workStyle = '時間報酬'
                        elif '時給' in reward:
                            workStyle = '時間報酬'
                        else:
                            workStyle = '固定報酬'

                        # カテゴリー取得
                        if num1 + 1 == 1:
                            category = '営業・マーケティング'
                        elif num1 + 1 == 2:
                            category = 'データ入力・タイピング'
                        elif num1 + 1 == 3:
                            category = 'クリエイティブ'
                        elif num1 + 1 == 4:
                            category = '編集・制作'
                        elif num1 + 1 == 5:
                            category = '人事・総務・経理・広報'
                        elif num1 + 1 == 6:
                            category = 'ライティング・翻訳'
                        elif num1 + 1 == 8:
                            category = 'PG・SE・PM'
                        else:
                            category = 'その他'

                        # ライティング案件は文字単価獲得
                        if category == 'ライティング・翻訳':

                            # 報酬取得
                            reward = elemMamaworks.select("section >a > p")[0].text.replace('\u3000','').replace('\u2003','')

                            if '1文字' in reward:

                                begin = '1文字'
                                end = '円'

                                r = re.compile( '(%s.*%s)' % (begin,end), flags=re.DOTALL)
                                m = r.search(reward)
                                ret = ''
                                if m is not None:
                                    ret = m.group(0)

                                    rewardCharacterUnit = re.split('円', ret)
                                    rewardCharacterUnit = rewardCharacterUnit[0].replace('1文字','')
                                    rewardCharacterUnit = rewardCharacterUnit.partition('～')[0]
                                    pattern=r'([0-9]+\.?[0-9]*)'

                                    try:
                                        rewardCharacterUnit = float(re.findall(pattern,rewardCharacterUnit)[0])

                                    except IndexError:
                                        rewardCharacterUnit = float(rewardCharacterUnit)

                                else:
                                    rewardCharacterUnit = 0

                            else:
                                rewardCharacterUnit = 0

                        # 現在時刻取得
                        date = elemMamaworks.select(".p-recruit-index__result-job-application-period")[0].text
                        date = date.partition(' 〜')[0].replace('掲載期間：', '')
                        # DATE型へ変換
                        dateChange = datetime.datetime.strptime(date, '%Y/%m/%d')
                        publicationDate = datetime.date(dateChange.year, dateChange.month, dateChange.day)


                        # 詳細ページURL
                        res = requests.get(detailsUrl, headers = headers)
                        soup = BeautifulSoup(res.text, 'html.parser')

                        # サブカテゴリー取得
                        subCategory = soup.select(".p-recruit-show__detail-box > ul >li >p")[0].text

                        # コンテンツ項目取得
                        if soup.select(".p-recruit-show__contents") != []:
                            contentsName = soup.select("th")

                        # コンテンツ内容取得
                        if soup.select(".p-recruit-show__contents") != []:
                            contentsItem = soup.select("td")

                        #コンテンツ項目と内容を合算
                        for contentName, contentItem in zip(contentsName, contentsItem):
                            contentItem = contentItem.get_text('\n', strip=True)
                            # コンテンツ内容の表示を整理()
                            contentName = contentName.get_text(strip=True)
                            contents.append("\n【" + contentName + "】\n" + contentItem)

                        # コンテンツリストより抽出
                        contents = '\n\n'.join(contents)
                        contents = contents.lstrip("\n\n")

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
