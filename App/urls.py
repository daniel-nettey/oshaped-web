from django.urls import path
from .views import *

urlpatterns = [
    path('', HomeView, name="index"),
    path('login/', LoginView, name="logIn"),
    path('report/', UserView, name="userTest"),
    path('feedback/', FeedbackView, name="userTest"),

    path('test/', TestScenarioAnswerView, name="TestScenario"),
    path('scenario/<int:scenario_id>/', ScenarioAnswerView, name="ScenarioAnswer"),
    path('scenario/', ScenarioAnswerTestView, name="ScenarioAnswer"),

    # Delete 
    path('user_get/', UserDataGet.as_view()),
    path('test_get/', TestDataGet.as_view()),
    path('scenario_get/', ScenarioDataGet.as_view()),
    path('answer_get/', AnswerDataGet.as_view()),
    path('attribute_get/', AttributeDataGet.as_view()),
    path('announcement_get/', AnnouncementDataGet.as_view()),
]