#!/usr/bin/python
# encoding: utf-8

from mayiutils.file_io.pickle_wrapper import PickleWrapper as pkw
from mayiutils.crawl import requests_wrapper as rw
from mayiutils.crawl import pyquery_wrapper as pw
from mayiutils.db.pymongo_wrapper import PyMongoWrapper
from mayiutils.nlp.re_wrapper import ReWrapper as rew


def getDocRoot(url):
    '''
    获取html DOM树的根
    :param url:
    :return:
    '''
    r1 = rw.RequestsWrapper(url)
    html = r1.getText()
    return pw.PyQueryWrapper(html).root

def parseList(url, selectors, saveTo='mongodb', dbname=None, tablename=None, filepath=None,
              nextTag='下一页', pretag=''):
    '''
    爬取页面的列表[title:url,...]
    :param url:  带爬取页面的url
    :param selectors:  页面中要爬取元素的选择器
    :param saveTo:  爬取的列表的保存位置
        可以是mongodb，可以是pkl
    :return:
    '''
    d = getDocRoot(url)
    #用一个字典保存一条爬取的结果
    if saveTo == 'mongodb':
        pmw = PyMongoWrapper('h1')
        table = pmw.getCollection(dbname, tablename)
        pmw.setUniqueIndex(dbname, tablename, 'title')
        for i in range(len(d(selectors))):
            try:
                d1 = dict()
                d1['title'] = d(selectors).eq(i).text().strip()
                d1['url'] = d(selectors).eq(i).attr.href
                print(d1)
                table.insert_one(d1)
            except Exception as e:
                print(e, d1)
        #获取“下一页”所在的链接地址
        nexturl = d('.bigPage > :contains({})'.format(nextTag)).eq(0).attr.href
        print(nexturl)
        if nexturl:
            nexturl = '{}{}'.format(pretag, d('.bigPage > :contains({})'.format(nextTag)).eq(0).attr.href)
            parseList(nexturl, selectors, saveTo, dbname, tablename, filepath,
                  nextTag, pretag)
    elif saveTo == 'pkl':
        list1 = list()
        for i in range(len(d(selectors))):
            try:
                d1 = dict()
                d1['title'] = d(selectors).eq(i).text().strip()
                d1['url'] = d(selectors).eq(i).attr.href
                print(d1)
                list1.append(d1)
            except Exception as e:
                print(e, d1)
        return list1

def parseDetail(url, selectors):
    """
    爬取页面详情
    :param url: 待爬取页面的url
    :param selectors: dict。爬取元素的选择器
    :return: 解析好的字典
    """
    r1 = rw.RequestsWrapper(url)
    html = r1.getText()
    d = pw.PyQueryWrapper(html).root
    d1 = dict()
    d1['url'] = url
    try:
        for k, v in selectors.items():
            if k.endswith("List"):#如果以List结果，说明要爬取的是一个list
                if k == "mainblockList":#爬取主模块内容
                    for i in range(len(d(v[0]))):
                        tag = d(v[0])(v[1]).eq(i).text().strip()
                        content = d(v[0])(v[2]).eq(i).text().strip()
                        d1[tag] = content
                else:
                    l1 = list()
                    for i in range(len(d(v))):
                        l1.append(d(v).eq(i).text().strip())
                    d1[k] = l1
            else:
                d1[k] = d(v).eq(0).text().strip()

    except Exception as e:
        print(e, k, d1)
    return d1
def crawlBKMY():
    '''
    爬取百科名医的代码
    :return:
    '''
    # pkw.dump2file(list('123'), 'abc.pkl')
    # parseList('https://www.baikemy.com/disease/list/0/0?pageIndex=1&pageCount=82',
    #               'li.ccjb_jbli_li > a:nth-child(1)',
    #               dbname='mybk',
    #               tablename='jbproduct',
    #               pretag='https://www.baikemy.com'
    #               )

    pmw = PyMongoWrapper('h1')
    # table = pmw.getCollection('mybk', 'jbproduct')
    table1 = pmw.getCollection('mybk', 'jbproductdetail')
    # urls = list(pmw.findAll(table,fieldlist=['url']))

    # pkw.dump2file(urls, 'urls.pkl')
    urls = pkw.loadfromfile('urls.pkl')
    count = 8842
    for url in urls[8842:]:
        print('{}--{}'.format(url,count))
        url1 = url['url'][(url['url'].rfind('/')+1) :]
        # print(url, url1)
        # break
        r = parseDetail('https://www.baikemy.com/disease/detail/{}/1'.format(url1),
                        {"title":'.jb-head-left-text',
                         "expertList":'.jbct-ctzz-center > ul:nth-child(1) > li',
                         "mainblockList":['div.lemma-main-content',
                                          'div.headline-1 > span.headline-content',
                                           'div.para']
                             }
                          )
        if '病因' in r or '临床表现' in r:
            r['isdisease']='true'
        else:
            r['isdisease']='false'
            print(r)
        table1.insert_one(r)
        count += 1


if __name__ == '__main__':
    '''
    爬取药源网的药品说明书
    爬取策略
        http://www.yaopinnet.com/tools/sms.asp上分为两部分说明书
            按字母检索中药说明书
            按字母检索化学药说明书
        分两次爬取
        
        #gmp_content > div:nth-child(4)
    '''
    #第一步 获取中药/化药的字母link列表
    # root = getDocRoot('http://www.yaopinnet.com/tools/sms.asp')
    # e1 = root('#gmp_content > div:nth-child(4) >a')
    # letterLinkList = list()
    # for i in range(len(e1)):
    #     letterLinkList.append(e1.eq(i).attr.href)
    # pkw.dump2File(letterLinkList, 'tmp/zyletterLinkList.pkl')
    # e1 = root('#gmp_content > div:nth-child(6) > a')
    # letterLinkList = list()
    # for i in range(len(e1)):
    #     letterLinkList.append(e1.eq(i).attr.href)
    # pkw.dump2File(letterLinkList, 'tmp/hyletterLinkList.pkl')
    #----------------------------------------------------------
    # zyLetterList = pkw.loadFromFile('tmp/zyletterLinkList.pkl')
    # hyLetterList = pkw.loadFromFile('tmp/hyletterLinkList.pkl')
    #
    # #第二步 获取中药/化药的药品说明书链接
    # zyInstructionList = list()
    # hyInstructionList = list()
    prefix = 'http://www.yaopinnet.com'
    # for url in zyLetterList:
    #     urlList = list()
    #     u1 = '{}{}'.format(prefix, url)
    #     urlList.append(u1)
    #     root = getDocRoot(u1)
    #     e1 = root('#sms_page > a')
    #     for i in range(len(e1)):
    #         urlList.append('{}{}'.format(prefix, e1.eq(i).attr.href))
    #         # print(e1.eq(i).attr.href)
    #     for url in urlList:
    #         root = getDocRoot(url)
    #         e1 = root('#c_list1 > ul > li > a')
    #         for i in range(len(e1)):
    #             d1 = dict()
    #             d1['title'] = e1.eq(i).text().strip()
    #             d1['url'] = e1.eq(i).attr.href
    #             print(d1)
    #             zyInstructionList.append(d1)
    #         e1 = root('#c_list2 > ul > li > a')
    #         for i in range(len(e1)):
    #             d1 = dict()
    #             d1['title'] = e1.eq(i).text().strip()
    #             d1['url'] = e1.eq(i).attr.href
    #             print(d1)
    #             zyInstructionList.append(d1)
    #     #     break
    #     # break
    # print('中药爬取完成，数量{}'.format(len(zyInstructionList)))
    # pkw.dump2File(zyInstructionList, 'tmp/zyInstructionList.pkl')
    # for url in hyLetterList:
    #     urlList = list()
    #     u1 = '{}{}'.format(prefix, url)
    #     urlList.append(u1)
    #     root = getDocRoot(u1)
    #     e1 = root('#sms_page > a')
    #     for i in range(len(e1)):
    #         urlList.append('{}{}'.format(prefix, e1.eq(i).attr.href))
    #         # print(e1.eq(i).attr.href)
    #     for url in urlList:
    #         root = getDocRoot(url)
    #         e1 = root('#c_list1 > ul > li > a')
    #         for i in range(len(e1)):
    #             d1 = dict()
    #             d1['title'] = e1.eq(i).text().strip()
    #             d1['url'] = e1.eq(i).attr.href
    #             print(d1)
    #             hyInstructionList.append(d1)
    #         e1 = root('#c_list2 > ul > li > a')
    #         for i in range(len(e1)):
    #             d1 = dict()
    #             d1['title'] = e1.eq(i).text().strip()
    #             d1['url'] = e1.eq(i).attr.href
    #             print(d1)
    #             hyInstructionList.append(d1)
    #     #     break
    #     # break
    # print('化药爬取完成，数量{}'.format(len(hyInstructionList)))
    # pkw.dump2File(hyInstructionList, 'tmp/hyInstructionList.pkl')
    #--------------------------------------------------------------
    # zyInstructionList = pkw.loadFromFile('tmp/zyInstructionList.pkl')
    hyInstructionList = pkw.loadFromFile('tmp/hyInstructionList.pkl')
    # print(len(zyInstructionList), len(hyInstructionList))#6559 6214
    # 第三步爬取说明书详情页
    pattern1 = rew.getPattern(r'【(\w+)】(.+)')
    pattern2 = rew.getPattern(r'(\w+)】(.+)')

    pmw = PyMongoWrapper('h1')
    dbname = 'yyw'
    tablename = 'drugdetail'
    table = pmw.getCollection(dbname, tablename)
    # pmw.setUniqueIndex(dbname, tablename, '通用名称')
    # #爬取中药说明书详情
    # count = 212
    # for d in zyInstructionList[count:]:
    #     u1 = '{}{}'.format(prefix, d['url'])
    #     print(count, u1)
    #     root = getDocRoot(u1)
    #     e1 = root('.smsli')
    #     dd = dict()
    #     dd['url'] = u1
    #     if len(e1) > 0:
    #         for i in range(len(e1)):
    #             s = e1.eq(i).text().strip()
    #             r = rew.findall(pattern1, s)
    #             # print(r)
    #             if r and r[0][0] == '药品名称':
    #                 ss = rew.split(r'\n|：', r[0][1].strip())
    #                 if len(ss) == 4:
    #                     dd[ss[0]] = ss[1]
    #                     dd[ss[2]] = ss[3]
    #             elif r:
    #                 dd[r[0][0]] = r[0][1]
    #     else:
    #         e1 = root('#sms_content')
    #         s = e1.text().strip()
    #         ss = s.split('【')
    #         print(ss)
    #         for t in ss:
    #             r = rew.findall(pattern2, t)
    #             # print(r)
    #             if r:
    #                 if r[0][0] == '药品名称':
    #                     ss = rew.split(r'\n|：', r[0][1].strip())
    #                     if len(ss) == 4:
    #                         dd[ss[0]] = ss[1]
    #                         dd[ss[2]] = ss[3]
    #                 elif r[0][0] == '执行标准':
    #                     dd[r[0][0]] = r[0][1][:r[0][1].index('分享到')]
    #                 else:
    #                     dd[r[0][0]] = r[0][1]
    #     print(dd)
    #     if '通用名称' in dd:
    #         table.insert_one(dd)
    #     else:
    #         print('error:', d)
    #     count += 1
    #爬取化学药说明书详情
    count = 4861
    for d in hyInstructionList[count:]:
        u1 = '{}{}'.format(prefix, d['url'])
        print(count, u1)
        root = getDocRoot(u1)
        e1 = root('.smsli')
        dd = dict()
        dd['url'] = u1
        if len(e1) > 0:
            for i in range(len(e1)):
                s = e1.eq(i).text().strip()
                r = rew.findall(pattern1, s)
                # print(r)
                if r and r[0][0] == '药品名称':
                    ss = rew.split(r'\n|：', r[0][1].strip())
                    temp = len(ss) // 2
                    for ii in range(temp):
                        dd[ss[2*ii]] = ss[2*ii+1]
                elif r:
                    dd[r[0][0]] = r[0][1]
        else:
            e1 = root('#sms_content')
            s = e1.text().strip()
            ss = s.split('【')
            print(ss)
            for t in ss:
                r = rew.findall(pattern2, t)
                # print(r)
                if r:
                    if r[0][0] == '药品名称':
                        ss = rew.split(r'\n|：', r[0][1].strip())
                        if len(ss) == 4:
                            dd[ss[0]] = ss[1]
                            dd[ss[2]] = ss[3]
                    elif r[0][0] == '执行标准':
                        dd[r[0][0]] = r[0][1][:r[0][1].index('分享到')]
                    else:
                        dd[r[0][0]] = r[0][1]
        print(dd)
        if '通用名称' in dd:
            dd['ishuaxueyao'] = 'true'
            table.insert_one(dd)
        else:
            print('error:', d)
        count += 1
    # print(r)
    # parseList('https://www.baikemy.com/disease/list/0/0?pageIndex=1&pageCount=82',
    #               'li.ccjb_jbli_li > a:nth-child(1)',
    #                 saveTo='pkl',
    #               pretag='https://www.baikemy.com'
    #               )




