# Generated by Django 3.2.4 on 2021-07-13 13:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Database', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('ID', models.IntegerField(blank=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('public', models.BooleanField(default=True, verbose_name='public')),
                ('approved', models.BooleanField(default=False, verbose_name='approved')),
                ('fields', models.TextField(blank=True, verbose_name='fields')),
                ('keywords', models.TextField(blank=True, verbose_name='keywords')),
                ('keywords_filter', models.BooleanField(default=True, verbose_name='keywords_filter')),
                ('processed_filter', models.BooleanField(default=False, verbose_name='processed_filter')),
                ('vocabulary', models.TextField(blank=True, verbose_name='vocabulary')),
                ('vocabulary_map', models.TextField(blank=True, verbose_name='vocabulary_map')),
            ],
        ),
        migrations.CreateModel(
            name='TaskUpload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('task_file', models.FileField(upload_to='upload/', verbose_name='task_file')),
                ('file_type', models.CharField(choices=[('GEO', 'GEO query download'), ('ArrayExpress', 'ArrayExpress query download'), ('List', 'List of GEO or ArrayExpress IDs')], max_length=200, verbose_name='file_type')),
                ('time_upload', models.DateTimeField(auto_now_add=True, verbose_name='time_upload')),
                ('add', models.BooleanField(default=True, verbose_name='add')),
                ('curator', models.TextField(blank=True, verbose_name='curator')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='file_upload', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='file_upload', to='Project.project')),
            ],
        ),
        migrations.CreateModel(
            name='Association_Project_Dataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='association_project_dataset', to='Database.dataset')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='association_project_dataset', to='Project.project')),
            ],
            options={
                'unique_together': {('project', 'dataset')},
            },
        ),
        migrations.CreateModel(
            name='Association_Project_Curator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner', models.BooleanField(verbose_name='owner')),
                ('active', models.BooleanField(verbose_name='active')),
                ('curator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='association_project_curator', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='association_project_curator', to='Project.project')),
            ],
            options={
                'unique_together': {('project', 'curator')},
            },
        ),
    ]
