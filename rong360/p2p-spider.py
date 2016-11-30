#! /usr/bin/evn python
# encoding=utf-8

import csv
import urllib2
from bs4 import BeautifulSoup
from openpyxl import Workbook
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

headers = {
    'Accept': 'text/html, application/xhtml+xml, */*',
    #'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Host': 'www.rong360.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Cookie': 'td_cookie=18446744070526600166; __jsluid=cada8c5400b78114cb717829f18c17ac; RONGID=cb5e017681868551aff148b8eee69c91; abclass=1480468395_6; PHPSESSID=sp71lt2ac7pglfpekcgkj0a7f3; cityDomain=beijing; __utmz=1480469685.utmcsr=(direct)|utmcmd=(direct)'
}
#抓取爬p2p数据
def p2pspider():
    url = u"http://www.rong360.com/licai-p2p/pingtai/rating/"
    try:
        req = urllib2.Request(url,headers=headers)
        source_code = urllib2.urlopen(req, timeout=10).read()
        plain_text = unicode(source_code)  # ,errors='ignore')
        soup = BeautifulSoup(plain_text, 'lxml')
    except Exception, e:
        print e
        return
    content = soup.find('tbody', {'id': 'ui_product_list_tbody'})
    tr_lists = content.findAll('tr')
    pt_lists = []
    pt_lists.append([u'平台', u'评级', u'平均收益', u'人气指数',u'网友评价',u'评价总数',u'链接', \
                     u'注册资金',u'上线时间' ,u'所在地区' ,u'平台网址' ,u'起投金额' ,u'管理费' ,u'取现费' ,u'平台背景',u'风险准备金',\
                     u'资金托管',u'保障方式',u'债权转让',u'自动投标',u'提现到账时间'])
    for pt in tr_lists:
        pt_info = []
        pt_info.append(pt.find('a').get_text())
        pt_info.append(pt.find('td', {'class': 'pingji'}).text.strip())
        pt_info.append(pt.find('td', {'class': 'average'}).text.strip())
        pt_info.append(pt.find('td', {'class': 'risk_index'}).text.strip())
        pt_info.append(pt.find('b', {'class': 'mct-rate'}).text.strip())
        pt_info.append(pt.find('span', {'class': 'rate-num'}).text.strip())
        pt_url = pt.attrs['click-url'].strip()
        pt_info.append(pt_url)
        get_detail_info(pt_url, pt_info)
        print(pt_info)
        pt_lists.append(pt_info)
    save_to_xlsx(pt_lists)
    save_to_csv(pt_lists)


#获取详细信息
def get_detail_info(url, pt_info):
    print('start %s:', url)
    try:
        req = urllib2.Request(url, headers=headers)
        source_code = urllib2.urlopen(req, timeout=10).read()
        plain_text = unicode(source_code)  # ,errors='ignore')
        soup = BeautifulSoup(plain_text, 'lxml')
    except Exception, e:
        print e
        return
    content = soup.find('div', {'class': 'loan-des wrap-clear'})
    p_lists = content.findAll('p', {'class': ['li2', 'li4']})
    for p in p_lists:
        pt_info.append(p.text.strip())

#保存到Excel文件
def save_to_xlsx(pt_lists):
    wb = Workbook()
    ws1 = wb.active
    ws1.title = 'p2p'
    for row in pt_lists:
        ws1.append(row)
    wb.save('p2p.xlsx')

#保存到csv文件
def save_to_csv(pt_lists):
    myfile = open('rong360-p2p', 'wb')
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(pt_lists)

if __name__ == '__main__':
    p2pspider()

