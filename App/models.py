from django.db import models
from django.core.validators import RegexValidator

# Ranking Values 
rankValues = (('Likely','Likely'), ('Somewhat Likely','Somewhat Likely'),('Somewhat Unlikely','Somewhat Unlikely'), ('Unlikely','Unlikely'))

# Create your models here.

# User Table 
class User(models.Model):
    email = models.EmailField()
    first_name = models.CharField(max_length=30, default="")
    last_name = models.CharField(max_length=30, default="")
    date_of_birth = models.DateField()
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message = ("Phone number must be entered in the format: '+999999999'. Up to 15 digits is allowed."))
    mobile = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    gender = models.CharField(max_length=20, choices=(('M','Male'), ('F','Female'),('O','Other')))
    role = models.CharField(max_length=200, default="")
    position = models.CharField(max_length=200, default="")
    date_of_program = models.DateField(default=None, blank=True, null=True)

    def __str__(self):
        return str(self.first_name) + ' ' + str(self.last_name)


# Test Table
class Test(models.Model):
    name = models.CharField(max_length=60, default='SDJ Test')
    description = models.TextField(default=None, blank=True, null=True)

    def __str__(self):
        return str(self.name)


# Scenario Table 
class Scenario(models.Model):
    id = models.CharField(max_length=10,primary_key=True)
    content = models.TextField()
    type = models.CharField(max_length=50, default=None, blank=True, null=True)
    image = models.ImageField(default=None, blank=True, null=True)
    
    def __str__(self):
        return str(self.content)



# Answer Table 
class Answer(models.Model):
    content = models.TextField()
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, default='')
    ranking = models.CharField(max_length=20, choices=rankValues)

    def __str__(self):
        return str(self.content)

# Super Attribute Table 
class SuperAttribute(models.Model):
    name = models.CharField(max_length=40, default="")
    

    def __str__(self):
        return str(self.name)

# Attributes Table 
class Attribute(models.Model):
    name = models.CharField(max_length=40, default="")
    superAttribute = models.ForeignKey(SuperAttribute, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)

# User & Test Table 
class User_Test(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)

    eq = models.IntegerField(default=0)
    influencing = models.IntegerField(default=0)
    communication = models.IntegerField(default=0)
    collaboration = models.IntegerField(default=0)
    problem_solving = models.IntegerField(default=0)
    
    class Meta:
        unique_together = (('test','user',))

    def __str__(self):
        return str(self.user) + " - " + str(self.test)


# Test & Scenario Table 
class Test_Scenario(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('test','scenario',))

    def __str__(self):
        return str(self.test) + " - " + str(self.scenario)


# Scenario & Attributes Table 
class Scenario_Attribute(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)

    score = models.IntegerField(default=0)

    class Meta:
        unique_together = (('scenario','attribute',))

    def __str__(self):
        return str(self.scenario) + " - " + str(self.attribute)


# Main table for all responses 
class Response(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    choice = models.CharField(max_length=20, choices=rankValues)
    score = models.IntegerField(default=0)

    class Meta:
        unique_together = (('user','test','answer'))

    def __str__(self):
        return str(self.user) + " - " + str(self.test) + " - " + str(self.answer) + ": " + str(self.score)

# Announcement Table 
class Announcement(models.Model):
    title = models.CharField(max_length=60)
    image = models.ImageField(default=None, blank=True, null=True)
    description = models.TextField(default=None, blank=True, null=True)

    def __str__(self):
        return str(self.title)
