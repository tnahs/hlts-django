# Generated by Django 2.2.1 on 2019-05-24 15:20

from django.db import migrations, models
import django.db.models.deletion
import main.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('slug', models.SlugField(max_length=256, unique=True)),
            ],
            options={
                'verbose_name': 'author',
                'verbose_name_plural': 'authors',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Origin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('slug', models.SlugField(max_length=256, unique=True)),
            ],
            options={
                'verbose_name': 'origin',
                'verbose_name_plural': 'origins',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('slug', models.SlugField(max_length=256, unique=True)),
                ('title', models.CharField(blank=True, max_length=256)),
                ('publication', models.CharField(blank=True, max_length=256)),
                ('chapter', models.CharField(blank=True, max_length=256)),
                ('date', models.CharField(blank=True, max_length=256)),
                ('website', models.CharField(blank=True, max_length=256)),
                ('notes', models.TextField(blank=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='main.Author')),
            ],
            options={
                'verbose_name': 'source',
                'verbose_name_plural': 'sources',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Passage',
            fields=[
                ('uuid', models.UUIDField(default=main.models.uuid_, editable=False, primary_key=True, serialize=False)),
                ('body', models.TextField()),
                ('notes', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('in_trash', models.BooleanField(default=False)),
                ('is_starred', models.BooleanField(default=False)),
                ('is_refreshable', models.BooleanField(default=False)),
                ('origin', models.ForeignKey(default=main.models.default_origin, on_delete=django.db.models.deletion.DO_NOTHING, to='main.Origin')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Source')),
            ],
            options={
                'verbose_name': 'passage',
                'verbose_name_plural': 'passages',
                'ordering': ('created',),
            },
        ),
    ]
