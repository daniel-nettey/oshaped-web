import csv
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path
from django.contrib import admin
from .models import *
from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse
import pandas as pd


# Get the file uploaded (csv or excel) and convert to pandas dataframe
def getFile(uploadfile):
    """
    If the file is a CSV, read it as a CSV. If the file is an Excel file, read it as an Excel file

    :param uploadfile: The file that the user uploads
    :return: A tuple of two values. The first value is a boolean value that indicates whether the file
    is a csv or excel file. The second value is the dataframe of the file.
    """
    if uploadfile.name.endswith('.csv'):
        file_data = pd.read_csv(uploadfile)
        print('#### CSV FILE ####')
        return True, file_data

    elif uploadfile.name.endswith('.xls') or uploadfile.name.endswith('xlsx'):
        file_data = pd.read_excel(uploadfile, skiprows=0)
        print('#### EXCEL FILE ####')
        return True, file_data

    return False, None

class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"

class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()


@admin.register(User)
class UserAdmin(admin.ModelAdmin, ExportCsvMixin):
    actions = ["export_as_csv"]

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-user-csv/', self.upload_file),]
        return new_urls + urls

    def upload_file(self, request):

        if request.method == "POST":
            uploadfile = request.FILES["csv_upload"]

            # This is checking if the file is a csv or excel file. If it is, it returns the dataframe
            # of the file. If it is not, it returns a warning message.
            file_temp = getFile(uploadfile)

            if file_temp[0]:
                file_data = file_temp[1]
            else:
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)

            for data in file_data.values:
                print()
                created = User.objects.update_or_create(
                    email=data[0],
                    first_name=data[1],
                    last_name=data[2],
                    date_of_birth=str(str(data[3]).split(' ')[0]),
                    mobile=data[4],
                    gender=data[5],
                    role=data[6],
                    position=data[7],
                    date_of_program=str(data[8]) if str(
                        data[8]) == '' or len(str(data[8])) == 0 else None
                )

            url = reverse('admin:index')
            return HttpResponseRedirect(url)

        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_upload.html", data)

@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin, ExportCsvMixin):
    actions = ["export_as_csv"]

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-scenario-csv/', self.upload_file),]
        return new_urls + urls

    def upload_file(self, request):

        if request.method == "POST":
            uploadfile = request.FILES["csv_upload"]

            # This is checking if the file is a csv or excel file. If it is, it returns the dataframe
            # of the file. If it is not, it returns a warning message.
            file_temp = getFile(uploadfile)

            if file_temp[0]:
                file_data = file_temp[1]
            else:
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)

    
            tempScenario = None
            tempSuperAttribute = None
        
            for data in file_data.values:
                # Add Scenario to database
                if type(data[1]) == str:
                    created = Scenario.objects.update_or_create(
                        id= int(data[0]),
                        content=data[1]
                    )
                    tempScenario = created[0]
                    Test_Scenario.objects.update_or_create(
                        scenario = tempScenario,
                        test = Test.objects.get(id=1)
                    )
                
                #Add Answers to database with respective scenario
                if type(data[2]) == str and type(data[3]) == str:
                    Answer.objects.update_or_create(
                        content=data[2],
                        ranking = data[3],
                        scenario=tempScenario
                    )

                #Add SuperAttribute to database
                if type(data[5]) == str:
                    created = SuperAttribute.objects.update_or_create(
                        name = data[5],

                    )
                    tempSuperAttribute = created[0]

                #Add main attribute and connect to scenario to database
                if type(data[4]) == str:
                    tempAttribute = Attribute.objects.update_or_create(
                        name = data[4],
                        superAttribute = tempSuperAttribute
                    )
                    Scenario_Attribute.objects.update_or_create(
                        attribute = tempAttribute[0],
                        scenario = tempScenario
                    )

                # Add attribute to answer with respective score
                

                
                    

            url = reverse('admin:index')
            return HttpResponseRedirect(url)

        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_upload.html", data)


# Register your models here.
admin.site.register([Announcement, Answer, Attribute, Test,
                    User_Test, Test_Scenario, Response, SuperAttribute, Scenario_Attribute])
