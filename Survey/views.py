from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import BasicAuthentication
from .models import Survey, Question, SurveyResponse, Score, CustomUser
from rest_framework.exceptions import ValidationError

from .serializers import (
    SignUpSerializer,
    CreateSurveySerializer,
    SurveyListSerializer,
    SurveyDetailSerializer,
    QuestionAddSerializer,
    MyUnpublishedSurveyDetailSerializer,
    SurveyPublishSerializer,
    ResponseForSurveySerializer,
    SurveyEditSerializer,
    QuesEditSerializer,
)


class SignUp(generics.CreateAPIView):
    serializer_class = SignUpSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"MESSAGE": "USER REGISTERED SUCCESSFULLY"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateSurvey(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = CreateSurveySerializer
    queryset = Survey.objects.all()

    def perform_create(self, serializer):
        print(f"User: {self.request.user}")
        serializer.save(created_by=self.request.user)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response(
            {"Message": "Survey created successfully"}, status=status.HTTP_201_CREATED
        )


class SurveyList(generics.ListAPIView):
    queryset = Survey.objects.filter(is_published=True).select_related("created_by")
    serializer_class = SurveyListSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class SurveyPublish(generics.UpdateAPIView):
    queryset = Survey.objects.filter(is_published=False)
    serializer_class = SurveyPublishSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.created_by != self.request.user:
            return Response(
                {"detail": "You don't have permission to publish this survey."}
            )

        serializer = self.get_serializer(instance, data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response(
            {"detail": "Survey published successfully."}, status=status.HTTP_200_OK
        )


class SurveyDetail(generics.RetrieveAPIView):
    serializer_class = SurveyDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Survey.objects.filter(is_published=True)
            .prefetch_related("questions")
            .select_related("created_by")
        )


class MyUnpublishedSurvey(generics.ListAPIView):
    serializer_class = SurveyListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Survey.objects.filter(
            created_by=user, is_published=False
        ).select_related("created_by")


class MyUnpublishedDetailSurvey(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MyUnpublishedSurveyDetailSerializer

    def get_queryset(self):
        user = self.request.user
        return Survey.objects.filter(
            created_by=user, is_published=False
        ).prefetch_related("questions")


class SurveyTitleEdit(generics.UpdateAPIView):
    queryset = Survey.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SurveyEditSerializer

    def update(self, request, *args, **kwargs):
        survey_to_update = self.get_object()
        user = request.user

        if survey_to_update.created_by != user:
            return Response(
                {"message": "You are not allowed to edit this survey."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if survey_to_update.is_published:
            return Response(
                {"message": "You are not allowed to edit a published survey."},
                status=status.HTTP_403_FORBIDDEN,
            )

        survey_serializer = SurveyEditSerializer(survey_to_update, data=request.data)

        if not survey_serializer.is_valid():
            return Response(
                survey_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        survey_serializer.save()

        return Response(
            {"message": "Survey title updated successfully."}, status=status.HTTP_200_OK
        )


class SurveyQuestionEdit(generics.UpdateAPIView):
    queryset = Question.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = QuesEditSerializer

    def update(self, request, *args, **kwargs):
        question_to_update = self.get_object()
        user = request.user

        if question_to_update.survey.created_by != user:
            return Response(
                {"message": "You are not allowed to edit this question."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(question_to_update, data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response(
            {"message": "Question updated successfully."}, status=status.HTTP_200_OK
        )


# add question to existing survey(unpublished)
class SurveyQuestionCreate(generics.CreateAPIView):
    queryset = Question.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionAddSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        survey_id = kwargs.get("survey_id")

        try:
            survey = Survey.objects.get(
                id=survey_id, created_by=user, is_published=False
            )
        except Survey.DoesNotExist:
            return Response(
                {"message": "Survey not found or it's published."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(survey=survey)
            return Response(
                {"message": "Question created successfully."},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SurveyResponseView(generics.CreateAPIView):
    serializer_class = ResponseForSurveySerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, survey_id, *args, **kwargs):
        user_id = request.user.id
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            survey = Survey.objects.get(id=survey_id)
        except Survey.DoesNotExist:
            return Response(
                {"detail": "Survey not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if SurveyResponse.objects.filter(survey=survey, user=user).exists():
            return Response(
                {"detail": "You have already attempted this survey."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        responses = request.data.get("responses", [])

        total_score = 0
        valid_responses = []

        for response_data in responses:
            question_id = response_data.get("question_id")
            question_number = response_data.get("question_number")
            answer = response_data.get("answer")

            try:
                question = Question.objects.get(id=question_id)
            except Question.DoesNotExist:
                return Response(
                    {"detail": f"Question with ID {question_id} not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if question.survey != survey or question.question_number != question_number:
                return Response(
                    {"detail": "Invalid question ID or number."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if question.question_type == "objective":
                options = question.options
                if answer not in options:
                    raise ValidationError(
                        {"detail": "Invalid answer for the objective question."}
                    )
                if answer == question.correct_answer:
                    total_score += question.score_of_objective

            valid_responses.append(
                {
                    "user": user,
                    "survey": survey,
                    "ans_of_question": question,
                    "answer": answer,
                }
            )

        if len(valid_responses) == len(responses):
            SurveyResponse.objects.bulk_create(
                [SurveyResponse(**data) for data in valid_responses]
            )
        try:
            score = Score.objects.get(user=user, survey=survey)
        except Score.DoesNotExist:
            score = Score.objects.create(
                user=user, survey=survey, total_score=total_score
            )

        score.total_score = total_score
        score.save()
        response_data = {
            "detail": "Survey responses submitted successfully.",
            "total_score_message": f"Total score of answered objective questions: {total_score}",
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


