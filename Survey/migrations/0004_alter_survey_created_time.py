# Generated by Django 4.2.5 on 2023-09-15 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Survey', '0003_rename_response_surveyresponse_alter_question_survey'),
    ]

    operations = [
        migrations.AlterField(
            model_name='survey',
            name='created_time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
