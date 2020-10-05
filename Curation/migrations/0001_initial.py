# Generated by Django 3.0.1 on 2020-03-11 02:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Project', '0001_initial'),
        ('Database', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Curation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No'), ('', 'Undetermined')], default='', max_length=200, verbose_name='category')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='time')),
                ('curator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='curation', to=settings.AUTH_USER_MODEL)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='curation', to='Database.Dataset')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='curation', to='Project.Project')),
            ],
            options={
                'unique_together': {('curator', 'project', 'dataset')},
            },
        ),
    ]
