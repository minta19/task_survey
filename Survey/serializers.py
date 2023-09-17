from rest_framework import serializers
from .models import CustomUser,Survey,Question,SurveyResponse,Score
from rest_framework.exceptions import ValidationError

class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomUser
        fields=['username','email','password']
        extra_kwargs={'password':{'write_only':True}}

    def create(self, validated_data):
        user=CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],

        )
        return user

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Question
        fields=['question', 'question_type', 'score_of_objective','options','correct_answer']
    

class CreateSurveySerializer(serializers.ModelSerializer):
    questions=QuestionSerializer(many=True)
    
    class Meta:
        model=Survey
        fields=['title','questions']

    def validate_questions(self,questions):
        if not questions:
            raise ValidationError(f"Atleast One question is needed for creating survey")
        
        max_questions=20
        min_questions=1
        max_options=10
        min_options=2

        if len(questions)>max_questions:
            raise ValidationError(f"Maximum allowted number of questions are {max_questions}")
        if len(questions)<min_questions:
            raise ValidationError(f"Minimum allowted number of options are {min_questions}")
        
        for question_data in questions:
            question_type=question_data.get('question_type')
            options=question_data.get('options')

            if question_type=='objective':
                if options:
                    if len(options)>max_options:
                        raise ValidationError(f"Maximum allowted number of options are {max_options}")
                    if len(options)<min_options:
                        raise ValidationError(f"Minimum allowted number of options are {min_options}")
        return questions


    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        survey = Survey.objects.create(**validated_data)
        question_number = 1

        for question_data in questions_data:
            Question.objects.create(survey=survey,question_number=question_number,**question_data)
            question_number += 1
        return survey
    
class SurveyPublishSerializer(serializers.ModelSerializer):
    class Meta:
        model=Survey
        fields=['is_published']

class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomUser
        fields=['username']

class SurveyListSerializer(serializers.ModelSerializer):
    created_by=UserNameSerializer(read_only=True)

    class Meta:
        model=Survey
        fields='__all__'
    
class QuestionforViewSerializer(serializers.ModelSerializer):
    class Meta:
        model=Question
        fields=['id','question_number','question', 'question_type', 'score_of_objective','options']
  

class SurveyDetailSerializer(serializers.ModelSerializer):
    questions = QuestionforViewSerializer(many=True, read_only=True)
    created_by=UserNameSerializer(read_only=True)

    class Meta:
        model = Survey
        fields = ('id', 'title', 'created_time', 'created_by','questions')

class UnpublishedQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Question
        fields=['id','question_number','question', 'question_type', 'score_of_objective','options','correct_answer']


class MyUnpublishedSurveyDetailSerializer(serializers.ModelSerializer):
    questions = UnpublishedQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Survey
        fields = ['id', 'title','questions']

class QuestionEditSerializer(serializers.ModelSerializer):
    class Meta:
        model=Question
        fields=['id','question_number']

class ResponseForSurveySerializer(serializers.ModelSerializer):
    ans_of_question=QuestionEditSerializer(many=True,read_only=True)
    
    class Meta:
        model=SurveyResponse
        fields=['ans_of_question','answer']

class QuesEditSerializer(serializers.ModelSerializer):
    class Meta:
        model=Question
        fields=['id','question', 'question_type', 'score_of_objective','options','correct_answer']
   
class SurveyEditSerializer(serializers.ModelSerializer):
    class Meta:
        model=Survey
        fields=['title']


class QuestionAddSerializer(serializers.ModelSerializer):
    class Meta:
        model=Question
        exclude=['survey']