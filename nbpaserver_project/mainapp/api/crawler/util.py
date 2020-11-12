import os
import csv
from . import naverblogcrawler
from . import multimediacrawler

from ... import models
from datetime import datetime

# 'UTF-8'이 아닌, 'MS949'로 할 경우 엑셀에서 바로 열 수 있지만, 특정 문자(\u2027)가 포함된 경우 오류가 납니다.
CSV_ENCODING_TYPE = 'utf-8'

# 크롤러에서 사용하는 BlogPost 객체를 BlogInfo, BlogInfo배열, Dictionary배열로 분리하여 반환
def blog_post_to_model(blog_post):
    hyperlink_dict = []
    tag_dict = []
    try:
        # BlogInfo 객체 생성하여 DB에 저장
        blog_info = models.BlogInfo()
        blog_info.blog_id = blog_post._blog_id
        blog_info.log_no = blog_post._log_no
        blog_info.url = blog_post._url
        blog_info.title = blog_post._title
        blog_info.body = blog_post._body

        # 하이퍼링크 객체 생성하여 DB에 저장
        for l in blog_post._hyperlinks:
            hyperlink = models.Dictionary()
            hyperlink.blog_info = blog_info
            hyperlink.dictionary_type = models.DictionaryType.objects.filter(name='hyperlink')[0]
            hyperlink.word = l
            hyperlink_dict.append(hyperlink)

        # 태그 객체 생성하여 DB에 저장
        for t in blog_post._tags:
            tag = models.Dictionary()
            tag.blog_info = blog_info
            tag.dictionary_type = models.DictionaryType.objects.filter(name='hashtag')[0]
            tag.word = t
            tag_dict.append(tag)

        return blog_info, hyperlink_dict, tag_dict
    except Exception as e:
        print('[SYSTEM][crawler_util] Failed to convert blog_post to blog_info, dictionarys\n' + blog_info.title + ', ' + blog_info.url, e)
        if 'list index out of range' in e.args[0]:
            print('[CRITICAL_ERROR][DB] Is dictionaryType table empty? Check the type tables.')
        
    return None, None, None

# 검색어, 결과 개수(옵션)를 주면 파싱해서 csv로 저장하는 메소드
def crawl_by_search_word(search_word, max_count=None):
    blog_post_list = naverblogcrawler.naver_blog_crawling(search_word, 100, "sim", max_count)

    if blog_post_list:
        print("텍스트 파일로 저장합니다")
        save_as_csv(search_word, blog_post_list)

# 네이버 블로그 URL을 주면 해당 게시물을 파싱해서 csv로 저장하는 메소드
def crawl_single_post(url):
    blog_post_list = []

    blog_post = naverblogcrawler.pasre_blog_post(url)

    return blog_post

    # if blog_post:
    #     blog_post_list.append(blog_post)
    
    # if blog_post_list:
    #     file_name_header = blog_post._blog_id + ' ' + blog_post._log_no

    #     print("텍스트 파일로 저장합니다")
    #     save_as_csv(file_name_header, blog_post_list)

# 경로를 주면 폴더를 생성하는 메소드
def create_directory(path):
    try:
        if not(os.path.isdir(path)):
            os.makedirs(os.path.join(path))
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Failed to create directory!!!!!")
            raise

# 파일명과 BlogPost 배열을 주면 csv파일로 저장하는 메소드
def save_as_csv(file_name_header, blog_post_list):
    now = datetime.today().strftime("%Y%m%d%H%M%S")
    save_path = os.getcwd() + os.sep + 'crawl' + os.sep
    create_directory(save_path)
    file_name = now + '-' + file_name_header + '.csv'

    try:
        f = open(save_path + file_name, 'w', newline='', encoding=CSV_ENCODING_TYPE)
        wr = csv.writer(f)
        wr.writerow(['blog_id', 'log_no', 'url', 'title', 'body', 'hyperlinks', 'tags'])
        for blog_post in blog_post_list:
            try:
                if blog_post:
                    renew_body = blog_post._body
                    print(renew_body)

                    hyperlink_list = ''
                    if blog_post._hyperlinks:
                        for link in blog_post._hyperlinks:
                            hyperlink_list += link + '\n'

                    tag_list = ''
                    if blog_post._tags:
                        for tag in blog_post._tags:
                            tag_list += tag + '\n'

                    wr.writerow([blog_post._blog_id, blog_post._log_no, blog_post._url, blog_post._title, renew_body, hyperlink_list, tag_list])
                    
                    print(blog_post._url + ' 저장 완료')
            except Exception as ex:
                print(ex)
        print('모든 게시물 저장 성공!')
        f.close
    except Exception as e:
        print("Failed to save text file : ")
        print(e)

    return
