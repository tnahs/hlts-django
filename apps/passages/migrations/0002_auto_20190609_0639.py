# Generated by Django 2.2.2 on 2019-06-09 06:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('passages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tag',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='source',
            name='authors',
            field=models.ManyToManyField(to='passages.Author'),
        ),
        migrations.AddField(
            model_name='source',
            name='medium',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='passages.Medium'),
        ),
        migrations.AddField(
            model_name='source',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sources', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='passage',
            name='collections',
            field=models.ManyToManyField(blank=True, to='passages.Collection'),
        ),
        migrations.AddField(
            model_name='passage',
            name='origin',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='passages.Origin'),
        ),
        migrations.AddField(
            model_name='passage',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='passages', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='passage',
            name='related',
            field=models.ManyToManyField(blank=True, related_name='_passage_related_+', to='passages.Passage'),
        ),
        migrations.AddField(
            model_name='passage',
            name='source',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='passages.Source'),
        ),
        migrations.AddField(
            model_name='passage',
            name='tags',
            field=models.ManyToManyField(blank=True, to='passages.Tag'),
        ),
        migrations.AddField(
            model_name='passage',
            name='topics',
            field=models.ManyToManyField(blank=True, to='passages.Topic'),
        ),
        migrations.AddField(
            model_name='origin',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='origins', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='medium',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='collection',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collections', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='author',
            name='aka',
            field=models.ManyToManyField(blank=True, related_name='_author_aka_+', to='passages.Author'),
        ),
        migrations.AddField(
            model_name='author',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authors', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='topic',
            unique_together={('owner', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together={('owner', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='source',
            unique_together={('owner', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='passage',
            unique_together={('owner', 'uuid')},
        ),
        migrations.AlterUniqueTogether(
            name='origin',
            unique_together={('owner', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='medium',
            unique_together={('owner', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='collection',
            unique_together={('owner', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='author',
            unique_together={('owner', 'name')},
        ),
    ]