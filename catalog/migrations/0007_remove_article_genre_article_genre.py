# Generated by Django 4.1.7 on 2023-04-03 13:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_alter_article_due_release'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='genre',
        ),
        migrations.AddField(
            model_name='article',
            name='genre',
            field=models.OneToOneField(default=None, help_text='选择本文章的类型', on_delete=django.db.models.deletion.SET_DEFAULT, to='catalog.genre'),
        ),
    ]
