from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    SignUp,
    CreateSurvey,
    SurveyList,
    SurveyTitleEdit,
    SurveyPublish,
    SurveyQuestionEdit,
    SurveyQuestionCreate,
    SurveyDetail,
    MyUnpublishedSurvey,
    MyUnpublishedDetailSurvey,
    SurveyResponseView,
)

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("signup/", SignUp.as_view(), name="signup"),
    path("create/", CreateSurvey.as_view(), name="create_survey"),
    path("list/", SurveyList.as_view(), name="survey_list"),
    path("title/edit/<int:pk>/", SurveyTitleEdit.as_view(), name="survey_edit"),
    path("ques/add/<int:survey_id>/", SurveyQuestionCreate.as_view(), name="ques_add"),
    path(
        "<int:survey_id>/q-edit/<int:pk>/", SurveyQuestionEdit.as_view(), name="q_edit"
    ),
    path("publish/<int:pk>/", SurveyPublish.as_view(), name="survey_publish"),
    path("detail/<int:pk>/", SurveyDetail.as_view(), name="survey_detail"),
    path("unpublished/", MyUnpublishedSurvey.as_view(), name="un_published"),
    path(
        "unpub/detail/<int:pk>/",
        MyUnpublishedDetailSurvey.as_view(),
        name="detail_unpub",
    ),
    path(
        "taking/<int:survey_id>/", SurveyResponseView.as_view(), name="survey_response"
    ),
]
