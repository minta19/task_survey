from django.contrib import admin

from .models import CustomUser,Survey,Question,SurveyResponse,Score

admin.site.register(CustomUser)
admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(SurveyResponse)
admin.site.register(Score)