import requests
import lxml
import xlwt
import sqlite3
import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def save_data_in_sqlite(path, dataList):
    init_db(path)
    conn = sqlite3.connect(path)
    cu = conn.cursor()
    for data in dataList:
        values = []
        for i in range(0, len(data)):
            data[i] = f'"{data[i]}"'
            values.append(data[i])
        sql = '''
        INSERT INTO MOVIE_TOP250 
        (
        link,cname, ename,  pic_link, score, rated, description, info
        ) values (?,?,?,?,?,?,?,?)
        '''
        cu.execute(sql, values)
        conn.commit()
    cu.close()
    conn.close()
    print('保存成功')


def init_db(path):
    conn = sqlite3.connect(path)
    sql = '''
    CREATE TABLE MOVIE_TOP250 
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
        link TEXT,
        cname VARCHAR,
        ename VARCHAR,
        pic_link TEXT,
        score NUMERIC,
        rated NUMERIC,
        description TEXT,
        info TEXT
    );
    '''
    cu = conn.cursor()
    try:
        cu.execute(sql)
        conn.commit()
        print('DB创建成功')
    except sqlite3.OperationalError:
        print('表已存在')
    finally:
        cu.close()
        conn.close()


def save_data_in_excel(path, dataList):
    print('保存')
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('sheet1', cell_overwrite_ok=True)
    col = ('link', 'title', 'enTitle', 'img', 'rating', 'count', 'description', 'info')
    for i in range(0, len(col)):
        worksheet.write(0, i, col[i])
    for i in range(0, len(dataList)):
        print(f'第{i + 1}条')
        data = dataList[i]
        for j in range(0, len(data)):
            worksheet.write(i + 1, j, data[j])

    workbook.save(path)
    print('爬取成功')


def ask_url(baseURL, params):
    headers = {
        'User-Agent': UserAgent().chrome
    }
    params = params
    response = requests.get(baseURL, headers=headers, params=params)
    return response.text


def get_data(baseURL, regDict):
    dataList = []
    for i in range(0, 10):
        params = {
            'start': i * 25
        }
        html = ask_url(baseURL, params)
        soup = BeautifulSoup(html, 'lxml')
        for item in soup.findAll('div', class_='item'):
            item = str(item)
            data = []
            link = re.findall(regDict['link'], item)[0]
            data.append(link)
            title = re.findall(regDict['title'], item)
            ctitle = title[0]
            data.append(ctitle)
            otitle = " "
            if len(title) > 1:
                otitle = title[1].replace('/', '').strip()
            data.append(otitle)
            img = re.findall(regDict['img'], item)[0]
            data.append(img)
            rating = re.findall(regDict['rating'], item)[0]
            data.append(rating)
            rateCount = re.findall(regDict['rateCount'], item)[0]
            data.append(rateCount)
            desc = re.findall(regDict['description'], item)
            if len(desc) > 0:
                desc = desc[0]
            else:
                desc = " "
            data.append(desc)
            info = re.findall(regDict['basicInfo'], item)[0]
            info = re.sub(r'<br(\s+)?/>(\s+)?', " ", info).strip()
            data.append(info)
            dataList.append(data)

    # print(dataList)
    return dataList


def init_regex():
    dict = {
        'link': re.compile(r'<a href="(.*?)">'),
        'img': re.compile(r'<img.*src="(.*?)"', re.S),
        'title': re.compile(r'<span class="title">(.*?)</span>'),
        'rating': re.compile(r'<span class="rating_num" property="v:average">(.*?)</span>'),
        'rateCount': re.compile(r'<span>(\d*)人评价</span>'),
        'description': re.compile(r'<span class="inq">(.*)</span>'),
        'basicInfo': re.compile(r'<p class="">(.*?)</p>', re.S)
    }
    return dict


def main():
    baseURL = 'https://movie.douban.com/top250?'
    regDict = init_regex()
    path = 'test.xls'
    dbpath = 'test.db'
    data = get_data(baseURL, regDict)
    # save_data_in_excel(path, data)
    save_data_in_sqlite(dbpath, data)


if __name__ == '__main__':
    main()
