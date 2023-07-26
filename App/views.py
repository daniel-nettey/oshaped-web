import json
import random
from django.http import HttpResponse
from django.shortcuts import redirect, render
from rest_framework import generics
from .models import *
from .serializers import *
from django.core.cache import cache
from django.db.models import Sum,Count,Value,F
from django.db.models.functions import Concat
from django.db import connection


Answer.objects.annotate(
    total_score=Sum('response__score')
).values('scenario', 'total_score').order_by('scenario')



# Create your views here.

def HomeView(request):
    user_found = True
    if request.method == "POST":
        user_email = request.POST.get('email')
        
        user_found = User.objects.filter(email=user_email).count() > 0

        if user_found:
            # store email in cache and take test
            cache.set('user_email', user_email, timeout=None)
            return redirect('/test')

    return render(request, "index.html", {"found": user_found})


class UserDataGet(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class TestDataGet(generics.ListCreateAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer

class ScenarioDataGet(generics.ListCreateAPIView):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer

class AnswerDataGet(generics.ListCreateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

class AttributeDataGet(generics.ListCreateAPIView):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer

class AnnouncementDataGet(generics.ListCreateAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer


def FeedbackView(request):
    # user = User.objects.filter(email="symbolic@mac.com")[0]
    cacheEmail  = cache.get('user_email')
    cacheEmail  = 'dnettey3@gmail.com'

    # Get the user, scenarios and responses 
    userID = User.objects.get(email = cacheEmail)
    temp_Scenarios = Scenario.objects.filter(test_scenario__in=Test_Scenario.objects.filter(test=1))
    responses = Response.objects.filter(user=userID, test=1)


    # Get the scenario Results 
    scenario_results = Response.objects.filter(user=userID, test=1).select_related('scenario_attribute').values(
        'answer__scenario','answer__scenario__content').annotate(total_score=Sum('score')).order_by('answer__scenario')    
    
    # Get the attribute Results
    attribute_results = Response.objects.filter(user=userID, test=1).select_related(
        'answer__scenario__scenario_attribute__attribute').values(
        name = F('answer__scenario__scenario_attribute__attribute__name')).annotate(
        total_score=Sum('score'), percentage = Sum('score') * 100/(Count('answer__scenario') * 5)).order_by(
        '-percentage', 'answer__scenario__scenario_attribute__attribute__id'
        )

    # Get the Super Attribute Results
    superattribute_results = Response.objects.filter(user=userID, test=1).select_related(
        'answer__scenario__scenario_attribute__attribute__superAttribute').values(
        name = F('answer__scenario__scenario_attribute__attribute__superAttribute__name')).annotate(
        total_score=Sum('score')).order_by('-total_score','answer__scenario__scenario_attribute__attribute__superAttribute__id')
    
    print(superattribute_results)


    return render(request, "feedback.html", {
        'scenarios': temp_Scenarios, 'responses':responses,'scenario_results': scenario_results, 
        'attribute_results': attribute_results, 'superattribute_results': superattribute_results  
        })

    

def UserView(request):
    # user = User.objects.filter(email="symbolic@mac.com")[0]
    cacheEmail  = cache.get('user_email')
    cacheEmail  = 'dnettey3@gmail.com'

    userID = User.objects.get(email = cacheEmail)

    temp_Scenarios = Scenario.objects.filter(
            test_scenario__in=Test_Scenario.objects.filter(test=1))
    

    
    responses = Response.objects.filter(user=userID, test=1)


    return render(request, "report.html", {'scenarios': temp_Scenarios, 'responses':responses})


def LoginView(request):

    if request.method == "POST":
        email = request.POST.get('email')

        # store email in cache
        cache.set('user_email', email, timeout=None)

        # Check if email exists already then add user
        if len(User.objects.filter(email = email)) == 0:
            date_of_program = request.POST.get('date_of_program')

            User.objects.create(
                first_name = request.POST.get('first-name'),
                last_name = request.POST.get('last-name'),
                email = email,
                date_of_birth = request.POST.get('date_of_birth'),
                mobile = request.POST.get('phone-number'),
                gender = request.POST.get('gender'),
                role = request.POST.get('role'),
                position = request.POST.get('position'),
                date_of_program = date_of_program if date_of_program != '' else None
            )
            return redirect('/test')
        
        else:
            print("The user already exists")

            return render(request, 'login.html', {'error': True})

    return render(request, 'login.html')


def TestScenarioAnswerView(request):
    try:
        # Get the test details
        total_scenarios,total_scenarios_count,user_response_count, userID, test = getTestDetails();

        # Check if user has not completed the test else direct to report
        if user_response_count < total_scenarios_count:
            # Return scenario and possible answers based on number of questions answered
            scenario = total_scenarios[user_response_count]
            answer = Answer.objects.filter(scenario=scenario)

            if request.method == "POST":
                print('### GET USER ANSWERS ###')

                # list of users values 
                user_answers = eval(request.POST.get('answerList_values'))
                print(user_answers, end='\n\n')
    
                try:
                    # Save responses of all options in database and continue test
                    storeAnswers(user_answers, userID.id, test, False)
                    return redirect('/test/')

                except Exception:
                    raise Exception
            
            answer = shuffle_queryset(answer)
            
            return render(request, "scenario.html", {"scenarios": scenario, "answers": answer, "solved_scenarios": user_response_count, "scenario_number": user_response_count + 1,
                                                     "total_scenarios": total_scenarios_count, "scenarios_range": range(total_scenarios_count )})
    
        # User has completed the test, direct user to report page 
        else:
            return redirect('/feedback/')

    except:
        return redirect('/')
        

# DELETE SOON
def ScenarioAnswerView(request, scenario_number):
    try:
        # Get the test details
        total_scenarios,total_scenarios_count,user_response_count, userID, test = getTestDetails();
    
        # Get specific scenario and the responses in the order they were chosen
        scenario = total_scenarios[scenario_number - 1]
        
        responses = Response.objects.filter(user=userID, test=test, answer__scenario=scenario).select_related(
            'answer').values('answer__id', 'answer__content', 'choice').annotate(id=F('answer__id')).annotate(
            content=F('answer__content')).order_by('choice')
        
        
        # Modify the response of user. 
        if request.method == "POST":
            print('### GET USER ANSWERS ###')

            # list of users values 
            user_answers = eval(request.POST.get('answerList_values'))
            print(user_answers, end='\n\n')

            try:
                # Save responses of all options in database and continue test
                storeAnswers(user_answers, userID.id, test, True)
                return redirect('/test/')

            except Exception:
                raise Exception

        return render(request, "scenario.html", {"scenarios": scenario, "answers": responses, "total_scenarios": total_scenarios_count, 
                                                 "solved_scenarios": user_response_count, "scenario_number": scenario_number })

    except:
        return redirect('/as')

    
   

def ScenarioAnswerTestView(request):
    scenario_all = Scenario.objects.all()
    scenario = scenario_all.first()
    answer = Answer.objects.filter(scenario=scenario.id)

    if request.method == "POST":
        try:

            scenario = scenario_all.exclude(id=scenario.id).first()
            answer = Answer.objects.filter(scenario=scenario.id)

            return render(request, 'scenario.html',  {"scenarios": scenario, "answers": answer})
        except Exception:
            raise Exception

    else:
        return render(request, "scenario.html", {"scenarios": scenario, "answers": answer})











########## HELPER FUNCTIONS ###########


# Get test Details
def getTestDetails():    
    # cacheEmail = cache.get('user_email')
    # print(cacheEmail)
    # REmove 
    cacheEmail = 'dnettey3@gmail.com'

    # Check user has loggedin 
    if cacheEmail:
        userID = User.objects.get(email = cacheEmail)
        test = 1

        # Get all the scenarios that belong to the test
        total_scenarios = Scenario.objects.filter(
            test_scenario__in=Test_Scenario.objects.filter(test=1))
        total_scenarios_count = total_scenarios.count()

        # Check response for the user's progress and return display
        user_response_count = Response.objects.filter(
            user=userID, test=test).count() // 4
        
        return total_scenarios, total_scenarios_count, user_response_count, userID, test

    return None

# Helper Function to Save Answers in ScenarioView 
def storeAnswers(user_answers, userID, testID, updateRecord):
    tempRankVals = [rankValues[x][0] for x,val in enumerate(rankValues)]

    # Compute Correct Scores for choices
    for idx, ans in enumerate(user_answers):
        tempScore = 0
        tempRanking = Answer.objects.get(id = ans).ranking 
        tempUserChoice = tempRankVals[idx]

        # When user gets it right 
        if  tempUserChoice == tempRanking:
            tempScore = 5 

        # When user is semi right eg : likely for somewhat likely | Unlikely for somewhat unlikely
        elif (tempUserChoice in tempRankVals[:2] and tempRanking in tempRankVals[:2]):
            tempScore = 3

        elif(tempUserChoice in tempRankVals[2:] and tempRanking in tempRankVals[2:]):
            tempScore = 3

        print(tempUserChoice, '-',tempRanking, ':',tempScore)

        # Whether created is being created or updated
        if updateRecord:
            ansRecord = Response.objects.get( user_id= userID, answer_id=ans, test_id = testID)
            ansRecord.choice = tempUserChoice
            ansRecord.score = tempScore
            ansRecord.save()

            print(ansRecord)

        else:
             Response.objects.update_or_create(
                user_id= userID, 
                answer_id=ans, 
                test_id = testID, 
                choice = tempUserChoice,
                score = tempScore
            )

# Shuffle Query set 
def shuffle_queryset(queryset):
    # Convert queryset to list to allow shuffling
    shuffled_list = list(queryset)

    # Shuffle the list randomly
    random.shuffle(shuffled_list)

    print('#### SHUFFLING ANSWERS ####')

    # Return shuffled list
    return shuffled_list