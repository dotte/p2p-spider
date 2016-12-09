#-*- coding:utf-8 -*-

#urllib模块提供了读取Web页面数据的接口
import urllib
from bs4 import BeautifulSoup
#re模块主要包含了正则表达式
import re


def download_files(url):
    page = urllib.urlopen(url)  # urllib.urlopen()方法用于打开一个URL地址
    html = page.read()  # read()方法用于读取URL上的数据
    soup = BeautifulSoup(html, 'lxml')
    file_lists = soup.find_all('a', text=u'幻灯片下载')
    re_name = r'<a href="http://bj2016.archsummit.com/presentation/.+?>(.+?)</a>'
    for link in file_lists:
        try:
            soup.find_all(href=re.compile(re_name))
            name = link.find_parent('td').find('a').text.replace(':', '-')
            print('href:%s;name:%s' % (link['href'], name))
            urllib.urlretrieve(link['href'], 'D:\\infoq_pdf\\%s.pdf' % name)
        except IOError as e:
            print(e)
            continue

if __name__ == '__main__':
    download_files("http://bj2016.archsummit.com/schedule")