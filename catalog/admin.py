import traceback
from django.contrib import admin
# Register your models here.
# 注册模型
from .models import Author, Genre, Article
# 信息发送
from django.contrib import messages
# Deta-SQL3通信库
import SQlite3_Deta
# Deta数据库文章数据切割函数
import Article_Cloud_Data_Split
# 密钥文件
from .config import DETA_KEY
DETA_KEY = DETA_KEY

# admin.site.register(Author)
# admin.site.register(Genre)
# admin.site.register(Article)


# 创建超级用户

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'GithubURL')
    # 控制哪些字段被显示和布局
    # 这里控制的是作者的详细信息页，列表内的按垂直分布，同一元组内按水平分布
    fields = ['first_name', 'last_name', 'GithubURL']


# 文章


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    # 配置列表视图
    list_display = ('title', 'author', 'display_genre',
                    'due_modify', 'due_release')
    # 可以使用 fieldsets 属性添加“部分”以在详细信息表单中对相关的模型信息进行分组
    fieldsets = (
        (None, {
            'fields': ('title', 'author', 'data_id', 'summary', 'content', 'genre', 'remark', 'Check_Upload')
        }),  # Time是该组标题
    )

    # 新动作：上传指定文章至云数据库

    def UploadToCloudDateBase(self, request, queryset):
        # 从queryset集中依次获取文章
        try:
            for article in queryset:
                # deta数据库的key为data_id，name为title，hometown为其他信息的集合，用|分割
                UploadData = '——deta数据分割线——'.join([article.summary, article.content, str(article.data_id), str(article.author.id), str(article.due_modify), str(article.due_release), article.remark,
                                                   str(article.author.id), article.author.first_name, article.author.last_name, article.author.GithubURL, article.CloudDataBase_genre_name()])
                # 上传
                db = SQlite3_Deta.DetaINOUT(
                    key=DETA_KEY, dbname='MyBlog_Article')
                db.Deta_PUT(key=str(article.data_id),
                            name=article.title,
                            hometown=UploadData
                            )
            # 发送成功的信息
            message = f"{queryset.count()} 篇文章已经完成上传！"
            self.message_user(request, message, level=messages.SUCCESS)
        except:
            # 错误信息
            message = f"上传错误！请检查网络情况"
            self.message_user(request, message, level=messages.ERROR)
            traceback.print_exc()
    UploadToCloudDateBase.short_description = 'Upload selected articles'

    def DownloadFromCloudDateBase(self, request, queryset):
        try:
            # 读取本地数据库信息
            Local_Data = SQlite3_Deta.SQL3INOUT('catalog_article')
            Ori_Local_Data = Local_Data.SQ_GET()
            Local_Article_ID = [i[3]for i in Ori_Local_Data]  # 文章唯一id用于比对

            print('[debug]Local_Article_ID =%s' % Local_Article_ID)
            # 读取全部云数据库信息
            Ori_Cloud_Article = SQlite3_Deta.DetaINOUT(
                key=DETA_KEY, dbname='MyBlog_Article').Deta_GET()

            # 获取云数据库文章id用于比对
            Cloud_Article_ID = [i['key'].replace(
                '-', '') for i in Ori_Cloud_Article]  # 本地数据库的id没有-
            print('[debug]Cloud_Article_ID=%s' % Cloud_Article_ID)

            Download_Article_ID = []  # 需要下载的文章id
            for i in Cloud_Article_ID:
                if i not in Local_Article_ID:
                    Download_Article_ID.append(i)
            print('[debug]Download_Article_ID=%s' % Download_Article_ID)
            # 比对完成后对原始云数据库数据进行筛选，留下需要下载的文章
            Download_Cloud_Article = [i for i in Ori_Cloud_Article if i['key'].replace(
                '-', '') in Download_Article_ID]
            #print('[debug]Download_Cloud_Article=%s' % Download_Cloud_Article)

            for i in Download_Cloud_Article:
                catalog_article_genre_maxid = max(
                    [i[0] for i in SQlite3_Deta.SQL3INOUT('catalog_article_genre').SQ_GET()])
                Split_data = Article_Cloud_Data_Split.Deta_Data_split(title=i['name'],
                                                                      catalog_article_genre_maxid=catalog_article_genre_maxid,
                                                                      data=i['hometown'])
                # 文章
                a = Article.objects.create(title=Split_data['local_article_data'][0],
                                           summary=Split_data['local_article_data'][1],
                                           content=Split_data['local_article_data'][2],
                                           data_id=Split_data['local_article_data'][3],
                                           author_id=Split_data['local_article_data'][4],
                                           due_modify=Split_data['local_article_data'][5],
                                           due_release=Split_data['local_article_data'][6],
                                           remark=Split_data['local_article_data'][7],
                                           Check_Upload=False)

                # 一次性添加多个类型
                genres_to_add = []
                for i in Split_data['local_article_genre_data']:
                    genre, created = Genre.objects.get_or_create(
                        name="%s" % str(i))
                    genres_to_add.append(genre)
                a.genre.add(*genres_to_add)

                # 保存
                a.save()
                # 分配类型

            # 下载信息反馈用的计数器
            message = f"{len(Download_Article_ID)} 个文章类型已下载！"
            self.message_user(request, message, level=messages.SUCCESS)

        except TimeoutError:
            message = f"请求超时！请重试"
            self.message_user(request, message, level=messages.ERROR)
            traceback.print_exc()

        except Exception as e:
            # 错误信息
            message = f"下载错误！请检查网络情况"
            self.message_user(request, message, level=messages.ERROR)
            traceback.print_exc()

    # 不需要输入items就可以执行
    DownloadFromCloudDateBase.allow_empty = True
    DownloadFromCloudDateBase.short_description = 'Download'
    actions = ['UploadToCloudDateBase', 'DownloadFromCloudDateBase']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):

    # 新动作：上传指定类型至云数据库
    def UploadToCloudDateBase(self, request, queryset):
        # 从queryset集中依次获取类型
        try:
            for genre in queryset:
                # 上传
                db = SQlite3_Deta.DetaINOUT(
                    key=DETA_KEY, dbname='MyBlog_Article_Genre')
                db.Deta_PUT(
                    key=str(genre.id),
                    name=genre.name
                )
            # 发送成功的信息
            message = f"{queryset.count()} 个文章类型已经完成上传！"
            self.message_user(request, message, level=messages.SUCCESS)
        except:
            # 错误信息
            message = f"上传错误！请检查网络情况"
            self.message_user(request, message, level=messages.ERROR)
            traceback.print_exc()
    UploadToCloudDateBase.short_description = 'Upload selected genres'
    # 新动作：从云数据库下载本地数据库缺少的类型

    def DownloadFromCloudDateBase(self, request, queryset):
        try:
            # 读取本地数据库信息
            Local_Data = SQlite3_Deta.SQL3INOUT('catalog_genre')
            Local_Genre = Local_Data.SQ_GET()
            print('[debug]Local_Genre=%s' % Local_Genre)
            # 读取云数据库信息
            Ori_Cloud_Genre = SQlite3_Deta.DetaINOUT(
                key=DETA_KEY, dbname='MyBlog_Article_Genre').Deta_GET()
            Cloud_Genre = [(int(i['key']), i['name']) for i in Ori_Cloud_Genre]

            print('[debug]Cloud_Genre=%s' % Cloud_Genre)
            # 下载信息反馈用的计数器
            Download_Genre_Num = 0
            # 以元组为单位进行比对,采用云→本地的比对方案，若本地库缺少云库的数据则进行下载，否则不下载
            for i in Cloud_Genre:
                if i not in Local_Genre:
                    Local_Data.SQ_PUT(form='(id,name)', content=i)
                    Download_Genre_Num += 1

            message = f"{Download_Genre_Num} 个文章类型已下载！"
            self.message_user(request, message, level=messages.SUCCESS)
        except:
            # 错误信息
            message = f"下载错误！请检查网络情况"
            self.message_user(request, message, level=messages.ERROR)
            traceback.print_exc()
    # 不需要输入items就可以执行
    DownloadFromCloudDateBase.allow_empty = True
    DownloadFromCloudDateBase.short_description = 'Download'

    actions = ['UploadToCloudDateBase', 'DownloadFromCloudDateBase']
