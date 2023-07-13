import requests
from bs4 import BeautifulSoup
import pandas as pd


class MovieCrawler:

    @staticmethod
    def get_this_week_movie():
        url = 'https://movies.yahoo.com.tw/movie_thisweek.html'
        return MovieCrawler.get_movie_content(url)

    @staticmethod
    def get_coming_soon_movie():
        url = 'https://movies.yahoo.com.tw/movie_comingsoon.html'
        return MovieCrawler.get_movie_content(url)

    @staticmethod
    def get_movie_content(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        }
        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        # get movie name
        names = soup.findAll("div", {"class": "release_movie_name"})
        release_movie_name_list = []
        for name in names:
            release_movie_name = name.find("a", {"class": "gabtn"}).text.replace("\n", "").replace(" ", "")
            release_movie_name_list.append(release_movie_name)

        # get movie time
        times = soup.findAll("div", {"class": "release_movie_time"})
        release_movie_time_list = []
        for time in times:
            release_movie_time = time.text.replace("上映日期：", "").replace("\n", "").replace(" ", "")
            release_movie_time_list.append(release_movie_time)

        # get movie brief
        movie_briefs = soup.findAll("div", {"class": "release_text"})
        release_movie_text_list = []
        for brief in movie_briefs:
            release_movie_text = brief.text.replace("\n", "").replace("\r", "").replace(" ", "")
            release_movie_text_list.append(release_movie_text)

        # combine all data to df
        df = pd.DataFrame({
            '電影名稱': release_movie_name_list,
            '上映時間': release_movie_time_list,
            '電影簡介': release_movie_text_list
        })

        return df
