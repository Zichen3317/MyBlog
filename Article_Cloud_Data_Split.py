# -*- coding:utf-8 -*-
# ==========================================
#       Author: ZiChen
#        📧Mail: 1538185121@qq.com
#         ⌚Time: 2023/04/04 21:04:01
# ==========================================
# 将Deta数据库读取到的文章数据进行切割分类以便写入sqlite3数据库
def Deta_Data_split_ID(data: str):
    '''
    只切出id并返回
    '''
    return data.split('——deta数据分割线——')[2]


def Deta_Data_split(title, catalog_article_genre_maxid, data: str):
    '''
    title 文章开头
    catalog_article_genre_maxid catalog_article_genre表中最新一条数据的id，由于在上传时是无法获取到这个id的
        为了保障写入时不会出现重复写入同一ID导致报错的情况，故需要手动获取数据库中的id

    返回格式均为列表
    '''
    # 前七个数据是catalog_article表的
    data_lst = data.split('——deta数据分割线——')
    article_data = []  # 防止内容中有转义字符
    for i in data_lst[0:7]:
        article_data.append(r"%s" % i)
    # 插入标题
    article_data.insert(0, title)
    #print('[debug]article_data =  %s' % article_data)
    # 第8~11数据是catalog_author表的
    author_data = data_lst[7:11]
    print('[debug]author_data =  %s' % author_data)
    # 文章的唯一id
    article_id = data_lst[2]
    print('[debug]article_id =  %s' % article_id)

    # 2023/04/07 10:19:52 ❗❗❗如果这篇文章没有类型标签，会返回空列表

    # catalog_author_genre
    print('[debug]data_lst[11] =  %s' % data_lst[11])
    article_genre_data = data_lst[11].split('丨')
    print('[debug]article_genre_data =  %s' % article_genre_data)

    Return_data = {'local_article_data': article_data,
                   'local_article_genre_data': article_genre_data,
                   'local_author_data': author_data}
    # print(Return_data)

    return Return_data
