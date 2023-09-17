from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email=models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    
    def __str__(self) -> str:
        return self.username
    

class Survey(models.Model):
    title=models.CharField(max_length=255,unique=True)
    created_time=models.DateTimeField(auto_now=True)
    created_by=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    is_published=models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return f"{self.title}--{self.created_by}" 
    
class Question(models.Model):
    question_choice=[
        ('objective','objective'),
        ('other','other')
    ]
    survey=models.ForeignKey(Survey,on_delete=models.CASCADE,related_name='questions')
    question_number=models.PositiveIntegerField(null=True)
    question=models.TextField()
    question_type=models.CharField(max_length=30,choices=question_choice,default='other')
    score_of_objective=models.PositiveIntegerField(null=True,blank=True)
    options = models.JSONField(null=True, blank=True)
    correct_answer = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.survey}-{self.question_number}--{self.question}"
    
class SurveyResponse(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    survey=models.ForeignKey(Survey,on_delete=models.CASCADE)
    ans_of_question=models.ForeignKey(Question,on_delete=models.CASCADE)
    answer=models.TextField()

    def __str__(self) -> str:
        return f"{self.survey}--{self.ans_of_question}"

class Score(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    survey=models.ForeignKey(Survey,on_delete=models.CASCADE)
    total_score=models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.user}--{self.survey}--{self.total_score}"



