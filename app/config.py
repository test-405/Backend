mysql = {
    'user': 'root',
    'passwd': '790713wh.',
    'host': 'localhost',
    'db': 'paper'
}

mysqlConfig = "mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4" \
    .format(mysql['user'], mysql['passwd'], mysql['host'], mysql['db'])
