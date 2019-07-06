# Generated by Django 2.2.2 on 2019-07-05 15:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nodes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='source',
            name='individuals',
            field=models.ManyToManyField(blank=True, to='nodes.Individual'),
        ),
        migrations.AddField(
            model_name='source',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sources', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='origin',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='origins', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='node',
            name='auto_related',
            field=models.ManyToManyField(blank=True, related_name='_node_auto_related_+', to='nodes.Node'),
        ),
        migrations.AddField(
            model_name='node',
            name='auto_tags',
            field=models.ManyToManyField(blank=True, related_name='auto_tagged', to='nodes.Tag'),
        ),
        migrations.AddField(
            model_name='node',
            name='collections',
            field=models.ManyToManyField(blank=True, to='nodes.Collection'),
        ),
        migrations.AddField(
            model_name='node',
            name='origin',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='nodes.Origin'),
        ),
        migrations.AddField(
            model_name='node',
            name='related',
            field=models.ManyToManyField(blank=True, related_name='_node_related_+', to='nodes.Node'),
        ),
        migrations.AddField(
            model_name='node',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='nodes.Source'),
        ),
        migrations.AddField(
            model_name='node',
            name='tags',
            field=models.ManyToManyField(blank=True, to='nodes.Tag'),
        ),
        migrations.AddField(
            model_name='node',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nodes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='individual',
            name='aka',
            field=models.ManyToManyField(blank=True, related_name='_individual_aka_+', to='nodes.Individual'),
        ),
        migrations.AddField(
            model_name='individual',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='individuals', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='collection',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collections', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together={('user', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='origin',
            unique_together={('user', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='individual',
            unique_together={('user', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='collection',
            unique_together={('user', 'name')},
        ),
    ]