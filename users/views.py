### This file contains the views for the app. It contains the views for the register, login, profile, calories, exercise, and home pages. It also contains the logic for the remember me functionality in the login view, and the logic for the calories and exercise pages to calculate the calories consumed and burnt respectively.
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.mail import EmailMessage
import matplotlib.pyplot as plt
import io
import os
import base64
from .forms import RegisterForm, LoginForm, UpdateUserForm, UpdateProfileForm, CalorieForm, ExerciseForm
import sqlite3
from datetime import datetime, date, timedelta



db="db.sqlite3" #variable containing db path

def create_connection(db_file): #function for creating a connection

    conn = None



    try:

        conn = sqlite3.connect(db_file) #try to connect

    except Exception as e:

        print(e)    #debug

    return conn

def generate_line_graph(x_data, y_data, title, x_label, y_label):
    plt.figure(figsize=(8, 6))
    plt.plot(x_data, y_data, marker='o', linestyle='-')
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xticks(rotation=90)
    plt.tight_layout()

    # Convert the plot to an image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Encode the image to base64
    graph_url = base64.b64encode(image_png)
    graph_url = graph_url.decode('utf-8')

    return graph_url

class RegisterView(View):   #register view



    form_class = RegisterForm   #form is registerform
    initial = {'key': 'value'}
    template_name = 'users/register.html' #sign up page



    def dispatch(self, request, *args, **kwargs): # will redirect to the home page if a user tries to access the register page while logged in
        
        if request.user.is_authenticated:

            return redirect(to='/') #redirect to home if authenticated

        # else process runs as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)
    


    def get(self, request, *args, **kwargs):    # handling get requests

        form = self.form_class(initial=self.initial)

        return render(request, self.template_name, {'form': form})
    


    def post(self, request, *args, **kwargs): #post request handler

        form = self.form_class(request.POST)    #attaches each instance of the registerform to variable form

        if form.is_valid(): #if the mandatory fields of the form are filled

            username = form.cleaned_data.get('username')      #assign cleaned version of username
            email = form.cleaned_data.get('email')            #assign cleaned version of email

            if User.objects.filter(email=email).exists():        #check if email already exists in the database

                messages.info(request, 'User with email already exists! Try logging in.')         # return message asking user to login

                return redirect('login') #redirect to login page
                
            messages.success(request, f'Account created for {username}') #returns message saying account has been created

            DB = create_connection(db)  #create connection
            cursor = DB.cursor()        #assign cursor

            form.save()                 #save form


            ##Execute queries to update weight to the value the user provided and goal to 2000 (default value they can customise in profile)

            cursor.execute("UPDATE auth_user SET weight = ? WHERE username = ?", (form.cleaned_data.get('weight'), form.cleaned_data.get('username'))) # Update user weight

            cursor.execute("UPDATE auth_user SET goal = 2000 WHERE username = ?", (form.cleaned_data.get('username'),)) # Update goal to 2000 by default

            DB.commit() #save
            cursor.close()
            DB.close()

            return redirect(to='login')# redirects to login where they can now use their new account

        return render(request, self.template_name, {'form': form})



# Class based view that extends from the django default login view to add the remember me functionality
class CustomLoginView(LoginView):

    form_class = LoginForm
    
    def form_valid(self, form):

        remember_me = form.cleaned_data.get('remember_me') #assigns user preference to (boolean) variable 'remember_me'

        if not remember_me: #if they do not wish to be remembered
            
            self.request.session.set_expiry(0) # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed

            self.request.session.modified = True # Set session as modified to force data updates/cookie to be set to the length specified in settings.py (one month)

        return super(CustomLoginView, self).form_valid(form)



class ResetPasswordView(SuccessMessageMixin, PasswordResetView):    #view for the forgot password page

    template_name = 'users/password_reset.html' #template for the page to request a password reset

    email_template_name = 'users/password_reset_email.html' #email template

    subject_template_name = 'users/password_reset_subject' #email subject (txt file)

    ##Below is the text displayed once the form is successfully submitted
    success_message = "We've emailed you a link for resetting your password, " \
                      "if an account exists with the email you entered you should receive an email within five minutes." \
                      " If you don't receive an email, " \
                      "please double check that the address is correct, and check your spam folder."
    
    success_url = reverse_lazy('users-home') #sends user to home page (will be guest) if the request is successful



class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):  #change password view (not to be confused with forgot password)

    template_name = 'users/change_password.html'    #HTML file

    success_message = "Successfully Changed Your Password" 

    success_url = reverse_lazy('users-home')



@login_required #decorator that requires login to access next method (to access profile)
def profile(request):   #profile request handler

    if request.method == 'POST':    #handling POST

        user_form = UpdateUserForm(request.POST, instance=request.user) #gets the user form
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile) #gets profile form
        oldemail = request.user.email   #assigns the email the user had before submitting the form to variable 

        if user_form.is_valid() and profile_form.is_valid(): #if both forms have their required fields filled out with valid inputs

            email=str(user_form.cleaned_data.get('email')) # assigns the email given in the form to email variable

            if User.objects.filter(email=email).exists() and email != oldemail: # check if email already exists in the database and belongs to another user
                
                    messages.info(request, 'An account is already linked with this email. If this is yours then please log in to that account or contact support through fitnesstrackerx@gmail.com')         # return message asking user to login

                    return redirect('users-profile') #redirect to login page
            
            DB = create_connection(db)  #create connection
            cursor = DB.cursor()        #assign cursor


            ##check if form weight exists
            if user_form.cleaned_data.get('weight') is not None:

                #execute query to update the users weight
                cursor.execute("UPDATE auth_user SET weight = ? WHERE id = ?", (user_form.cleaned_data.get('weight'), request.user.id))

            ##check if form goal exists
            if user_form.cleaned_data.get('goal') is not None:

                #execute query to update the users daily goal
                cursor.execute("UPDATE auth_user SET goal = ? WHERE id = ?", (user_form.cleaned_data.get('goal'), request.user.id))

            DB.commit()     #save changes
            cursor.close()
            DB.close()

            user_form.save()    #save both forms
            profile_form.save() 

            messages.success(request, 'Your profile has been updated.') #returns message that profile has been updated

            return redirect(to='users-profile') #redirects to same page (essentially refreshes so the user can see changes)

    else: 
        ##If it is a GET request

        user_form = UpdateUserForm(instance=request.user)   #create an instance of each form and assign to respective variables
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form}) #returns profile page with the user's instances of the forms

@login_required #decorator that requires login before accessing these requests

def calories(request):  #handling requests from calories

    user = int(request.user.id) #assign variable to user id

    if request.method == "POST":    #If POST

        calorieform = CalorieForm(request.POST, instance=request.user) #gets the calorie form

        #checks if it is a delete request
        if 'entry_id' in request.POST:

            entry_id = request.POST['entry_id']

            DB = create_connection(db)  #create connection
            cursor = DB.cursor()        #assign cursor

            cursor.execute("DELETE FROM food WHERE id = ?", [entry_id]) #executing deletion query

            DB.commit() #committing changes and closing
            cursor.close()
            DB.close()
    
            return redirect('calories') # Redirect to the same page after deletion
        
        if calorieform.is_valid():  #otherwise if it is not a deletion request (i.e, it is a request to update the calories)
            
            DB = create_connection(db)  #create connection
            cursor = DB.cursor()        #assign cursor

            # Insert new entry into food table

            ##Below is a tuple that contains the user id, calorie value from the submitted form, foodname from submitted form, and the date.
            data_tuple = (user, int(calorieform.cleaned_data.get('calorievalue')), str(calorieform.cleaned_data.get('food')), date.today())

            cursor.execute("INSERT INTO food (user_id, calories, foodname, date) VALUES (?, ?, ?, ?)", data_tuple) #Add entry to food

            DB.commit() #committing changes and closing
            cursor.close()
            DB.close()

            # Redirect to avoid form resubmission
            return redirect('calories')

    # Fetch logged calories for GET requests
        
    DB = create_connection(db) #create connection
    cursor = DB.cursor()       #assign cursor

    #Execute query to get the foods and calories logged by the user today
    cursor.execute("SELECT id, foodname, calories FROM food WHERE user_id = ? AND date = ?", (user, date.today(),))

    logged_calories = cursor.fetchall() #fetch all the calories logged by the user today
    total_calories = sum(int(entry[2]) for entry in logged_calories)    #total the calories logged by the user today

    context = {'logged_calories': logged_calories,   #context variables to pass through
               'total_calories': total_calories}
    
    cursor.close()
    DB.close()

    return render(request, 'users/calories.html', {'form': CalorieForm, **context}) #render the calories page with the form and context variables

@login_required #requires login to access the exercise request handler



def exercises(request): #exercise request handler

    user_id = request.user.id   #assign user id to variable



    def calculate_calories(type_value, duration):   #create method for calculating calories

        DB = create_connection(db) #create connection
        cursor = DB.cursor()       #assign cursor

        ##Execute query to get the user's weight
        cursor.execute('SELECT weight FROM auth_user WHERE id = ?', (user_id,))

        result = cursor.fetchone()  #fetch result
        weight = result[0]          #assign result to weight variable

        cursor.close()
        DB.close()

        #IF block to determine the value (to be used when calculating calories) in each exercise
        if type_value == "Running":

            val = 4.1

        elif type_value == "Cycling":

            val = 2.4

        elif type_value == "Walking":

            val = 1.0

        elif type_value == "Jogging":

            val = 3.04

        elif type_value == "Swimming":

            val = 2.3

        return round(((val * duration*((weight)/50))*160/60))   #uses formula I calculated/derived from a few sources to calculate calories burned

    if request.method == "POST":    #If POST request

        exercise_form = ExerciseForm(request.POST)  #get the exercise form

        if 'entry_id' in request.POST:  #if it is a delete request

            entry_id = request.POST['entry_id'] #assign entry id to variable

            DB = create_connection(db)  #create connection
            cursor = DB.cursor()        #assign cursor

            ##Execute query to delete the exercise entry
            cursor.execute("DELETE FROM exercise WHERE id = ? AND user_id = ?", [entry_id, user_id])

            DB.commit() #commit changes and close connections
            cursor.close()
            DB.close()

            return redirect('exercise') #redirect to the exercise page after deletion
        
        if exercise_form.is_valid():    #if it is not a deletion request and the form is valid (i.e, it is a request to update the exercises)

            duration = exercise_form.cleaned_data.get('duration')   #assign duration to variable
            type_value = exercise_form.cleaned_data.get('type')     #assign type to variable

            DB = create_connection(db)  #create connection
            cursor = DB.cursor()        #assign cursor

            ##Execute query to insert the exercise entry into the exercise table with the user id, duration, calories, type, and date
            cursor.execute("INSERT INTO exercise (user_id, duration, calories, type, date) VALUES (?, ?, ?, ?, ?)",
                           (user_id, duration, calculate_calories(type_value, duration), type_value, date.today(),))
            
            DB.commit() #save changes and close
            cursor.close()
            DB.close()

            return redirect('exercise') #redirect to the exercise page after updating the exercises

    # Fetch logged exercises for GET requests
    DB = create_connection(db)  #create connection
    cursor = DB.cursor()        #assign cursor

    ##Execute query to get the exercises logged by the user today
    cursor.execute("SELECT id, duration, calories, type FROM exercise WHERE user_id = ? AND date = ?", (user_id, date.today()))

    logged_exercises = cursor.fetchall()    #fetch all the exercises logged by the user today
    total_burnt = sum(int(entry[2]) for entry in logged_exercises)  #total the calories burnt by the user today

    context = {'logged_exercises': logged_exercises,    #context variables to pass through
               'total_burnt': total_burnt}

    cursor.close()
    DB.close()

    return render(request, 'users/exercise.html', {'form': ExerciseForm(), **context})  #render the exercise page with the form and context variables

def home(request):  #home page request handler
    if request.user.is_authenticated:   #if the user is authenticated

        user_id = request.user.id       #assign user id to variable

        DB = create_connection(db)
        cursor = DB.cursor()
        #Check if goal and weight exist -- they will not exist if this is a first time login from google OAuth2
        cursor.execute("SELECT weight, goal FROM auth_user WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result[0] or not result[1]:  # Check if weight and goal exist

            # Add weight and goal to the user
            cursor.execute("UPDATE auth_user SET weight = ?, goal = ? WHERE id = ?", (60, 2000, user_id))

            DB.commit()

        cursor.close()
        DB.close()

        # Calculate total calories consumed

        DB = create_connection(db)  #create connection
        cursor = DB.cursor()        #assign cursor

        ##Execute query to get the sum of calories consumed by the user today
        cursor.execute("SELECT SUM(calories) FROM food WHERE user_id = ? AND date = ?", (user_id, date.today()))

        total_calories_result = cursor.fetchone()   #fetch the result

        total_calories = total_calories_result[0] if total_calories_result[0] is not None else 0    #assign the total calories to the variable

        cursor.close()
        DB.close()

        # Calculate total calories burnt

        DB = create_connection(db)  #create connection
        cursor = DB.cursor()        #assign cursor

        ##Execute query to get the sum of calories burnt by the user today
        cursor.execute("SELECT SUM(calories) FROM exercise WHERE user_id = ? AND date = ?", (user_id, date.today()))

        total_burnt_result = cursor.fetchone()  #fetch the result

        total_burnt = total_burnt_result[0] if total_burnt_result[0] is not None else 0 #assign the total calories burnt to the variable

        cursor.close()
        DB.close()

        # Fetch user's goal

        DB = create_connection(db)  #create connection
        cursor = DB.cursor()        #assign cursor

        ##Execute query to get the user's goal
        cursor.execute("SELECT goal FROM auth_user WHERE id = ?", (user_id,))

        goal_result = cursor.fetchone() #fetch the result

        goal = goal_result[0] if goal_result else 0 #assign the goal to the variable
        
        cursor.close()
        DB.close()

        # Calculate total remaining calories
        total_remaining_calories = goal - total_calories + total_burnt  #calculate the total remaining calories

        ##render the home page with the total calories, total burnt, and total remaining calories
        return render(request, 'users/home.html', {'total_calories': total_calories, 
                                                    'total_burnt': total_burnt,
                                                    'total_remaining_calories': total_remaining_calories})
    #if the user is not authenticated render home page normally
    else:
        return render(request, 'users/home.html')



@login_required

def calorie_history(request):
    # Connect to the database
    DB = create_connection(db)
    cursor = DB.cursor()
    user_id = request.user.id
    # Calculate the date one month ago
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Query the database to retrieve calorie intake and burnt data for the past month
    cursor.execute("SELECT date, SUM(calories) FROM food WHERE user_id = ? AND date BETWEEN ? AND ? GROUP BY date", (user_id, start_date, end_date))
    intake_data = cursor.fetchall()
    
    cursor.execute("SELECT date, SUM(calories) FROM exercise WHERE user_id = ? AND date BETWEEN ? AND ? GROUP BY date", (user_id, start_date, end_date))
    burnt_data = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    DB.close()

    # Prepare data for plotting
    intake_dates, intake_calories = zip(*intake_data) if intake_data else ([], [])
    burnt_dates, burnt_calories = zip(*burnt_data) if burnt_data else ([], [])

    # Generate the graphs
    intake_graph = generate_line_graph(intake_dates, intake_calories, 'Calorie Intake', 'Date', 'Calories')
    burnt_graph = generate_line_graph(burnt_dates, burnt_calories, 'Calorie Burnt', 'Date', 'Calories')

    # Pass the graphs to the template
    return render(request, 'users/calorie_history.html', {'intake_graph': intake_graph, 'burnt_graph': burnt_graph})



@login_required
def download_data(request):
    user = request.user
    user_id = user.id
    
    # Create a connection to the database
    DB = create_connection(db)
    cursor = DB.cursor()

    # Query to retrieve data from auth_user table
    cursor.execute("SELECT * FROM auth_user WHERE id=?", (user_id,))
    auth_user_data = cursor.fetchall()

    # Query to retrieve data from social_auth_usersocialauth table
    cursor.execute("SELECT * FROM social_auth_usersocialauth WHERE user_id=?", (user_id,))
    social_auth_data = cursor.fetchall()

    # Query to retrieve data from food table
    cursor.execute("SELECT * FROM food WHERE user_id=?", (user_id,))
    food_data = cursor.fetchall()

    # Query to retrieve data from exercise table
    cursor.execute("SELECT * FROM exercise WHERE user_id=?", (user_id,))
    exercise_data = cursor.fetchall()

    # Query to retrieve data from users_profile table
    cursor.execute("SELECT * FROM users_profile WHERE user_id=?", (user_id,))
    profile_data = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    DB.close()

    # Concatenate all data into a single list
    all_data = {
        'auth_user_data': auth_user_data,
        'social_auth_data': social_auth_data,
        'food_data': food_data,
        'exercise_data': exercise_data,
        'profile_data': profile_data,
    }

    # Create a text file to store the data
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current file
    file_name = 'user_data.txt'  # Specify the file name
    file_path = os.path.join(base_dir, file_name)  # Combine the directory and file name to create the full file path
    with open(file_path, 'w') as f:
        for table, data in all_data.items():
            f.write(f"Table: {table}\n")
            for row in data:
                f.write(f"{row}\n")

    # Send an email with the data file attached
    subject = 'Your Data'
    body = f"Hi, {user.username}\n\nYou requested a copy of your data. Attached is a file containing all of the data we have kept since you signed up.\n\nThanks for using Fitness Tracker X.\n\nKind Regards,\nKV"
    from_email = os.getenv('email')  # Replace with your email address
    to_email = [user.email]
    email = EmailMessage(subject, body, from_email, to_email)
    email.attach_file(file_path)
    email.send()

    # Delete the temporary file
    os.remove(file_path)

    return render(request, 'users/download_data.html')