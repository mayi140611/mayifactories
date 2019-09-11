# 备份MongoDB数据
cd /Users/luoyonggui/Documents/mongodump &&
mongodump -o /Users/luoyonggui/Documents/mongodump/`date +%Y%m%d` &&
tar -cvf `date +%Y%m%d`.tgz `date +%Y%m%d` &&
rm -rf /Users/luoyonggui/Documents/mongodump/`date +%Y%m%d`