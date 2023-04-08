# Used to generate URLs by reversing the URL patterns
from django.urls import reverse
from django.db import models
import uuid  # Required for unique book instances
# Create your models here.
# Deta-SQL3通信库
import SQlite3_Deta
# 密钥文件
from .config import DETA_KEY
DETA_KEY = DETA_KEY
# 文章部分

# 文章本身


class Genre(models.Model):
    """
    文章类型
    """
    name = models.CharField(
        max_length=200, help_text="输入文章的归类(编程/其它...)")

    def __str__(self):
        """
        用于表示Model对象的字符串 (in Admin site etc.)
        """
        return self.name

    # 重写save函数
    def save(self, *args, **kwargs):
        # your additional code goes here
        super().save(*args, **kwargs)  # call the original save method
        try:
            # 上传
            # key是id,name是name
            db = SQlite3_Deta.DetaINOUT(
                key=DETA_KEY, dbname='MyBlog_Article_Genre')
            db.Deta_PUT(
                key=str(self.id),
                name=self.name
            )
            print('\n---[debug]Upload %s - %s ✓\n---' %
                  (str(self.id), self.name))
        except:
            print('\n---[error]Upload %s - %s ×\n---' %
                  (str(self.id), self.name))


class Article(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    # on_delete=models.SET_NULL — 如果关联的作者记录被删除，它将把作者的值设置为Null
    # 使用外键是因为book只能有一个作者，但是author可以有多个book
    # Author是一个字符串而不是对象，因为它还没有在文件中声明。

    # 概要
    summary = models.TextField(
        max_length=1000, help_text="输入文章的概要")
    # 文章的内容，以markdown形式
    content = models.TextField(
        help_text="输入文章的内容"
    )
    # data_id 应该是deta数据库自带的每条数据的id
    data_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, help_text="文章相对数据库的唯一ID")
    # 类型
    genre = models.ManyToManyField(
        Genre, help_text="选择本文章的类型")
    # 使用ManyToManyField，因为类型可以包含许多书籍。书籍可以涵盖许多体裁。
    # 流派类已经定义，所以我们可以指定上面的对象。

    # 发布时间以及修改时间
    due_release = models.DateTimeField(auto_now_add=True)
    due_modify = models.DateTimeField(auto_now=True)
    # 备注
    remark = models.CharField(max_length=500)
    # 在保存时是否自动上传云数据库
    Check_Upload = models.BooleanField(help_text="是否上传云数据库", default=False)

    def __str__(self):
        """
        用于表示Model对象的字符串。
        """
        return self.title

    def get_absolute_url(self):
        """
        返回访问特定文章实例的url。
        """
        return reverse('article-detail', args=[str(self.id)])

    # 将文章类型合并为一个字符串，并将该字符串命名为Genre以便展示时调用
    def display_genre(self):
        """
        Creates a string for the Genre. This is required to display genre in Admin.
        """
        return ', '.join([genre.name for genre in self.genre.all()[:3]])
    display_genre.short_description = 'Genre'

    def CloudDataBase_genre_name(self):
        '''
        返回文章所属类别的所有id
        '''
        # self.genre.all()[:]不是列表类型
        Genre_lst = [str(genre.name) for genre in self.genre.all()]
        print('[debug]Genre_lst(name)=%s' % Genre_lst)
        if len(Genre_lst) != 0:
            return '丨'.join(Genre_lst)
        else:
            return ''

    # 重写save函数

    def save(self, *args, **kwargs):
        # 检测该函数是否被启用
        print('[debug]models.py - Article.save() Start')
        # your additional code goes here
        super().save(*args, **kwargs)  # call the original save method
        if self.Check_Upload == True:
            print('[debug]models.py - Article.save() - Upload Start')
            try:
                # deta数据库的key为data_id，name为title，hometown为其他信息的集合，用|分割
                UploadData = '——deta数据分割线——'.join([self.summary, self.content, str(self.data_id), str(self.author.id), str(self.due_modify), str(self.due_release), self.remark,
                                                   str(self.author.id), self.author.first_name, self.author.last_name, self.author.GithubURL, self.CloudDataBase_genre_name()])
                # 上传
                db = SQlite3_Deta.DetaINOUT(
                    key=DETA_KEY, dbname='MyBlog_Article')
                db.Deta_PUT(key=str(self.data_id),
                            name=self.title,
                            hometown=UploadData
                            )
                print('\n---[debug]Upload %s - %s ✓\n---' %
                      (self.title, self.author))
            except:
                print('\n---[error]Upload %s - %s ×\n---' %
                      (self.title, self.author))


class Author(models.Model):
    """
    Model representing an author.
    """
    first_name = models.CharField(max_length=100)  # 姓名
    last_name = models.CharField(max_length=100)  # 姓氏
    GithubURL = models.URLField(max_length=200, blank=True)  # Github主页链接，可不填

    def get_absolute_url(self):
        """
        返回访问特定作者实例的url。
        """
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """
        用于表示Model对象的字符串。
        """
        return '%s, %s' % (self.last_name, self.first_name)
