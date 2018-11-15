import requests
import json
import os
import time
from selenium import webdriver
from urllib.parse import urlencode
from multiprocessing.pool import Pool

def download_sln(start_url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(chrome_options=chrome_options)
    browser.get(start_url)
    return browser.page_source

def download(url):
    '''
    下载网页内容
    :param:url:下载网页链接
    :return:返回网页内容
    '''
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
    }
    if url:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                response.encoding = response.apparent_encoding
                return response.text
        except:
            return None

def download_bytes(url):
    '''
    下载二进制文件
    :param url: 最终音乐链接
    :return: 二进制数据
    '''
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
    }
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.content
    except:
        return None

def parse(result):
    '''
    第二层
    :param result: 包含最终所有音乐链接的json字符串
    :return: 每个音乐链接
    '''
    result = json.loads(result)
    data = result['data']
    tracksAudioPlay = data['tracksAudioPlay']
    if tracksAudioPlay:
        albumName = tracksAudioPlay[0]['albumName']
        if not os.path.exists(albumName):
            os.mkdir(albumName)
        for i in tracksAudioPlay:
            # albumName = i['albumName']
            src = i['src']
            trackName = i['trackName']
            fp = '{0}/{1}.{2}'.format(albumName,trackName,'m4a')
            # print(fp)
            # print(src)
            save(fp,src)

def save(fp,src):
    '''
    保存所有音乐
    :param fp: 文件路径
    :param src: 音乐链接
    :return:
    '''
    try:
        if not os.path.exists(fp):
            ctn = download_bytes(src)
            with open(fp,'wb') as f:
                f.write(ctn)
                print(fp,end='  ')
                print('保存成功')
        else:
            print(fp,end='  ')
            print('文件已存在')
    except:
        print(fp,end=' ')
        print('保存失败')

def structure_start_url():
    '''
    第一层
    构造最初页面的urls
    :return: 包含每页的url列表
    '''
    urls = []
    base_url = 'https://www.ximalaya.com/revision/category/queryCategoryPageAlbums?'
    for i in range(1,35):
        date = {
            'category': 'yinyue',
            'sort': 0,
            'page': i,
            'perPage': 30,
        }
        url = base_url + urlencode(date)
        urls.append(url)
    return urls

def parse_start(result):
    '''
    第一层:解析每个音乐的包名和链接
    :param result:包含所有音乐包的页面的json数据
    :return:字典 包名和链接
    '''
    dct = {}
    result = json.loads(result)
    data = result['data']
    alb = data['albums']
    for i in alb:
        title = i['title']
        albumId = i['albumId']
        dct[title] = albumId
    return dct

def structure_url(albumId,pageNum):
    '''
    构造第二层url
    :return: urls:所有链接
    '''
    urls = []
    for i in range(1,9):
        url = 'https://www.ximalaya.com/revision/play/album?'
        data = {
                'albumId':albumId,
                'pageNum':pageNum,
                'pageSize':30,
        }
        urls.append(url + urlencode(data))
    return urls

def main(first_url):
    #从第一层网页获取构造第二层网页的关键字

    # for first_url in first_urls:
    first_result = download(first_url)
    dct = parse_start(first_result)
    #构造的二层网页
    for albumId in dct.values():
        for page in range(1,30):
            second_urls = structure_url(albumId,page)
            #从第二层网页获取最终的音乐
            for second_url in second_urls:
                second_result = download(second_url)
                parse(second_result)



if __name__ == '__main__':
    start = time.time()
    first_urls = structure_start_url()
    pool = Pool()
    pool.map(main,first_urls)
    pool.close()
    pool.join()
    end = time.time()
    print('Total spend time:%d'%(end-start))
