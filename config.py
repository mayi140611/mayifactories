import sys
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils/db')
from pymongo_wrapper import PyMongoWrapper
mongo = PyMongoWrapper()

LOG_PATH = '/Users/luoyonggui/Documents/logs'
# 投资组合
portfolio = {'stock': [
                ('东方航空', 15500),
                ('中国核电', 8300),
                ('中信证券', 1500),
                ('兴业银行', 1800),
                ('中国石油', 1700),
            ],
            'fund': [
                ('510300.SH', 7200),
                ('510500.SH', 3200),
                ('159938.SZ', 9500),
                ('159920.SZ', 1000),
                ('518880.SH', 3200),
                ('512580.SH', 15800),
                ('159915.SZ', 4100),
                ('512800.SH', 6000),
                ('512880.SH', 2000),
                ('513050.SH', 5000),
            ],
            'otc_fund': [
                ('建信中证500指数增强A', 13699.71+9028.49),
                ('富国沪深300指数增强', 13704.73),
                ('富国中证红利指数增强', 21081.72+7133.1+11245.7),
                ('兴全可转债混合', 17831.75),
                ('易方达证券公司分级', 14259.70),
                ('富国中证500指数(LOF)', 6957.22),
                ('华夏上证50ETF联接A', 7068.28),
                ('华夏中证500ETF联接A', 37520),
                ('华宝标普油气上游股票', 12656.15+7714.7),
                ('广发医药卫生联接A', 12136.65+7798.49),
                ('广发纯债债券A', 6007.1),
                ('广发中证500ETF联接C', 4151.45),
                ('广发创业板ETF联接A', 3694.24),
                ('广发养老指数A', 31864.15),
                ('广发中证全指金融地产联接A', 11497.64),
                ('广发中证传媒ETF联接A', 23948.61),
                ('广发中证环保ETF联接A', 27267.64+3779.89),
                ('广发中债7-10年国开债指数A', 2500.95),
                ('易方达安心回报债券A', 1928.96+11771.68),
                ('博时信用债纯债债券A', 2802.54),
                ('长信可转债债券A', 2497.79),
                ('华安德国30(DAX)联接', 8411+2787),
            ]
}
INDEX_NAMES=[
    '000001.SH',
    '399001.SZ',  # 深圳成指
    '399006.SZ',  # 创业板指
]
FUND_NAMES = [
    '510300.SH',
    '510500.SH',
    '512800.SH',
    '512880.SH',
    '512660.SH',
    '518880.SH',
    '512580.SH',
    '513050.SH',
    '159938.SZ',
    '159915.SZ',
    '159920.SZ',
]
OTC_FUND_NAMES = [
    '易方达证券公司分级',
    '广发纯债债券A',
    '兴全可转债混合',
    '博时信用债纯债债券A',
    '广发中债7-10年国开债指数A',
    '华夏中证500ETF联接A',
    '富国中证红利指数增强',
    '广发医药卫生联接A',
    '华夏上证50ETF联接A',
    '建信中证500指数增强A',
    '广发养老指数A',
    '华宝标普油气上游股票',
    '广发创业板ETF联接A',
    '长信可转债债券A',
    '易方达安心回报债券A',
    '广发中证500ETF联接C',
    '广发中证全指金融地产联接A',
    '富国中证500指数(LOF)',
    '广发中证环保ETF联接A',
    '富国沪深300指数增强',
    '广发中证传媒ETF联接A',
    '华安德国30(DAX)联接',
]
#黄金
GOLDS = ['中润资源',
         # '湖南黄金',
         # '恒邦股份',
         # '荣华实业',
         # '中金黄金',
         # '山东黄金',
         # '园城黄金',
         # '赤峰黄金',
         # '西部黄金',
         '紫金矿业']

BANKS = ['平安银行',
         # '宁波银行',
         # '江阴银行',
         # '张家港行',
         # '郑州银行',
         # '青岛银行',
         # '青农商行',
         # '苏州银行',
         # '浦发银行',
         # '华夏银行',
         # '民生银行',
         # '招商银行',
         # '无锡银行',
         # '江苏银行',
         # '杭州银行',
         # '西安银行',
         # '南京银行',
         # '常熟银行',
         # '兴业银行',
         # '北京银行',
         # '上海银行',
         # '农业银行',
         # '交通银行',
         # '工商银行',
         # '长沙银行',
         # '光大银行',
         # '成都银行',
         # '紫金银行',
         # '建设银行',
         # '中国银行',
         # '贵阳银行',
         # '中信银行',
         '苏农银行']
BROKERS = ['申万宏源',
 '东北证券',
 '锦龙股份',
 '国元证券',
 '国海证券',
 '广发证券',
 '长江证券',
 '山西证券',
 '国盛金控',
 '西部证券',
 '国信证券',
 '第一创业',
 '华西证券',
 '长城证券',
 '华林证券',
 '东方财富',
 '中信证券',
 '国投资本',
 '国金证券',
 '华创阳安',
 '西南证券',
 '华鑫股份',
 '海通证券',
 '哈投股份',
 '华安证券',
 '东方证券',
 '招商证券',
 '中信建投',
 '太平洋',
 '财通证券',
 '天风证券',
 '东兴证券',
 '国泰君安',
 '红塔证券',
 '中原证券',
 '兴业证券',
 '东吴证券',
 '华泰证券',
 '光大证券',
 '浙商证券',
 '中国银河',
 '方正证券',
 '南京证券']
# 白酒
LIQUORS = ['泸州老窖',
 '古井贡酒',
 '酒鬼酒',
 '五粮液',
 '顺鑫农业',
 '洋河股份',
 '青青稞酒',
 '伊力特',
 '金种子酒',
 '贵州茅台',
 '老白干酒',
 '舍得酒业',
 '水井坊',
 '山西汾酒',
 '迎驾贡酒',
 '今世缘',
 '口子窖',
 '金徽酒']
STOCK_NAMES = [
               '东方航空',
               '南方航空',
               '中国核电',
               '中国平安',
               '北大荒',
               '中国石油',
               '山鹰纸业',
               ] # + BANKS + BROKERS + LIQUORS + GOLDS
table = mongo.getCollection('finance', 'stock_basic')
df = mongo.findAll(table, fieldlist=['name'], returnFmt='df')
STOCK_NAMES = df.name.tolist()[::-1]



