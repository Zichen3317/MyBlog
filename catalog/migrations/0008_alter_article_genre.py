# Generated by Django 4.1.7 on 2023-04-03 13:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0007_remove_article_genre_article_genre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='genre',
            field=models.OneToOneField(help_text='选择本文章的类型', null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.genre'),
        ),
    ]
