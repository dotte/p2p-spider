#! /usr/bin/evn python
# encoding=utf-8

import csv
import urllib2
from bs4 import BeautifulSoup
from openpyxl import Workbook
import re
import sys

reload(sys)
sys.setdefaultencoding('gb2312')

headers = {
    'Accept': 'text/html, application/xhtml+xml, */*',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Host': 'www.haodf.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Cookie': 'td_cookie=18446744070643200088; g=86592_1467175369007; CNZZDATA1914877=cnzz_eid%3D1778255894-1467173708-%26ntime%3D1480584567; CNZZDATA1256706712=1928080324-1467173603-%7C1480580188; CNZZDATA2724401=cnzz_eid%3D1364901054-1480558564-http%253A%252F%252Fwww.haodf.com%252F%26ntime%3D1480580173; td_cookie=18446744070638478304; Hm_lpvt_dfa5478034171cc641b1639b2a5b717d=1480585006; Hm_lvt_dfa5478034171cc641b1639b2a5b717d=1480561641; _ga=GA1.2.539083788.1467175385; g=HDF.95.577355c1e89d9; sdmsg=1; _gat=1'
}
base_url = 'http://www.haodf.com'
hospital_base_url = 'http://www.haodf.com/jibing/xiaoerganmao_yiyuan_beijing_all_all_all_%s.htm'
doctor_base_url = 'http://www.haodf.com/jibing/%s/daifu_%d_beijing_all_all_all.htm'

record_lists = []

#抓取科室数据
def ks_spider():
    url = u"http://www.haodf.com/jibing/list.htm"
    try:
        req = urllib2.Request(url, headers=headers)
        source_code = urllib2.urlopen(req, timeout=10).read()
        plain_text = unicode(source_code)  # ,errors='ignore')
        soup = BeautifulSoup(plain_text, 'lxml')
    except Exception, e:
        print e
        return
    content = soup.find('div', {'class': 'jeshi_tree'})
    kstl_lists = content.findAll('div',{'class': 'kstl'})
    #jb_lists = []
    #ks_lists.append([u'疾病分类', u'链接'])
    for ks in kstl_lists:
        ks_name = ks.find('a').get_text()
        ks_url = ks.find('a').attrs['href'].strip()
        ks_url =base_url + ks_url
        get_jibing_info(ks_url, ks_name)
        print(ks_name)
    save_to_xlsx(record_lists)


#获取疾病信息
def get_jibing_info(url, ks_name):
    print('start %s:' % url)
    try:
        req = urllib2.Request(url, headers=headers)
        source_code = urllib2.urlopen(req, timeout=10).read()
        plain_text = unicode(source_code)  # ,errors='ignore')
        soup = BeautifulSoup(plain_text, 'lxml')
    except Exception, e:
        print e
        return

    content = soup.find('div', {'id': 'el_result_content'})
    jb_lists = content.findAll('li')
    for jb in jb_lists:
        a = jb.find('a')
        if a:
            jb_name = a.text.strip()
            jb_url_name = re.compile(r'^\/.+\/(.+)\.htm$').findall(a.attrs['href'].strip())[0]
            doctor_url = doctor_base_url % (jb_url_name, 1)
            get_doctor_info(doctor_url, ks_name, jb_name, jb_url_name)

#获取医生总页数
def get_doctor_info(doctor_url,ks_name, jb_name,jb_url_name):
    print('start %s:' % doctor_url)
    try:
        req = urllib2.Request(doctor_url, headers=headers)
        source_code = urllib2.urlopen(req, timeout=10).read()
        plain_text = unicode(source_code)  # ,errors='ignore')
        soup = BeautifulSoup(plain_text, 'lxml')
    except Exception, e:
        print e
        return
    content = soup.find('div', {'class': 'page_turn'})
    if content is None:
        return
    total_page = int(content.find('font', {'class': 'black pl5 pr5'}).text.strip())
    for i in range(total_page):
        doctor_page_url = doctor_base_url % (jb_url_name, i+1)
        get_doctor_info_by_page(doctor_page_url, ks_name, jb_name)

#按页抓取该疾病所有医生信息
def get_doctor_info_by_page(doctor_page_url, ks_name, jb_name):
    print('start %s:' % doctor_page_url)
    try:
        req = urllib2.Request(doctor_page_url, headers=headers)
        source_code = urllib2.urlopen(req, timeout=10).read()
        plain_text = unicode(source_code)  # ,errors='ignore')
        soup = BeautifulSoup(plain_text, 'lxml')
    except Exception, e:
        print e
        return
    content = soup.find('ul', {'class': 'fs hp_doc clearfix'})
    li_lists = content.findAll('li')
    for li in li_lists:
        jb_info = []
        jb_info.append(ks_name) #科室名
        jb_info.append(jb_name) #疾病名
        jb_info.append(li.find('a', {'class': 'blue_a3'}).text.strip()) #医生姓名
        jb_info.append(li.find('span', {'class': 'ml15'}).text.strip()) #医生级别
        jb_info.append(li.find('span', {'class': 'ml10'}).text.strip()) #所属医院
        patient_recommend = li.find('span', {'class': 'patient_recommend'}) #患者推荐热度
        if patient_recommend:
            jb_info.append(patient_recommend.find('i', {'class': 'blue'}).text.strip())
        else:
            jb_info.append('')
        patient_recommend_ora = li.find('span', {'class': 'patient_recommend_ora'}) #近两周回复
        if patient_recommend_ora:
            jb_info.append(patient_recommend_ora.text.strip())
        else:
            jb_info.append('')
        shanchang = li.find('p', text=re.compile(u'擅长')) #擅长
        if shanchang:
            jb_info.append(shanchang.text.strip())
        else:
            jb_info.append('')
        record_lists.append(jb_info)


#保存到Excel文件
def save_to_xlsx(pt_lists):
    wb = Workbook()
    ws1 = wb.active
    ws1.title = 'ks'
    for row in pt_lists:
        ws1.append(row)
    wb.save('kslb.xlsx')

#保存到csv文件
def save_to_csv(pt_lists):
    myfile = open('kslb.csv', 'wb')
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(pt_lists)

if __name__ == '__main__':
    ks_spider()

