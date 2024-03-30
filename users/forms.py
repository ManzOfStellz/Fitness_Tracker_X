from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import Profile


class RegisterForm(UserCreationForm): #signup form

    first_name = forms.CharField(max_length=100,            #name
                                 required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'First Name',
                                                               'class': 'form-control',
                                                               }))
    


    weight = forms.IntegerField(min_value=40, #user weight
                                max_value=300,
                                required=True,
                                widget=forms.TextInput(attrs={'placeholder': 'Your Weight',
                                                              'class': 'form-control',
                                                              }))



    username = forms.CharField(max_length=100,              #requested username
                               required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Username',
                                                             'class': 'form-control',
                                                             }))
    


    email = forms.EmailField(required=True,                 #requested email
                             widget=forms.TextInput(attrs={'placeholder': 'Email',
                                                           'class': 'form-control',
                                                           }))
    


    password1 = forms.CharField(max_length=50,              #initial password
                                required=True,
                                widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                  'class': 'form-control',
                                                                  'data-toggle': 'password',
                                                                  'id': 'password',
                                                                  }))
    


    password2 = forms.CharField(max_length=50,              #password confirmation
                                required=True,
                                widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password',
                                                                  'class': 'form-control',
                                                                  'data-toggle': 'password',
                                                                  'id': 'password',
                                                                  }))
    


    class Meta:

        model = User
        fields = ['first_name', 'weight', 'username', 'email', 'password1', 'password2']



class LoginForm(AuthenticationForm): #login form

    username = forms.CharField(max_length=100, #username
                               required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Username',
                                                             'class': 'form-control',
                                                             }))
    


    password = forms.CharField(max_length=50, #password
                               required=True,
                               widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                 'class': 'form-control',
                                                                 'data-toggle': 'password',
                                                                 'id': 'password',
                                                                 'name': 'password',
                                                                 }))
    


    remember_me = forms.BooleanField(required=False) #'remember me' option



    class Meta:

        model = User
        fields = ['username', 'password', 'remember_me']



class UpdateUserForm(forms.ModelForm): #update user

    username = forms.CharField(max_length=100,  #username
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    


    email = forms.EmailField(required=True,     #email
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    

    
    goal = forms.IntegerField(max_value=4000,
                              min_value=1000,
                              required=False)
    


    weight = forms.IntegerField(max_value=500,
                                min_value=50,
                                required=False)
    


    class Meta:

        model = User
        fields = ['username', 'email', 'goal', 'weight']



class UpdateProfileForm(forms.ModelForm):   #update profile

    avatar = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control-file'}))     #profile picture



    class Meta:

        model = Profile
        fields = ['avatar']



class CalorieForm(forms.ModelForm):

    food = forms.CharField(max_length=30,
                           min_length=1,
                           required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'})
                           )



    calorievalue = forms.IntegerField(max_value=1000,
                                      min_value=1,
                                      required=True,
                                      )
    


    class Meta:

        model = User
        fields = ['food', 'calorievalue']



class ExerciseForm(forms.ModelForm):

    EXERCISE_TYPE=[
        ('Walking', 'Walking'),
        ('Cycling', 'Cycling'),
        ('Jogging', 'Jogging'),
        ('Running', 'Running'),
        ('Swimming', 'Swimming')
        ]



    duration = forms.IntegerField(max_value=300,
                           min_value=1,
                           required=True,
                           )
    

    
    type = forms.ChoiceField(
        choices=EXERCISE_TYPE,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}))
    

    
    class Meta:
        
        model = User
        fields = ['duration', 'type']
