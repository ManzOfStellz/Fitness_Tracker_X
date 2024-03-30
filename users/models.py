from django.db import models
from django.contrib.auth.models import User
from PIL import Image

# Extending User Model Using a One-To-One Link
class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE) #one to one relationship with user model
    avatar = models.ImageField(default='default.png', upload_to='profile_images')   #profile picture
    bio = None  #bio set to None as not relevant
    def __str__(self):  #string representation of the user
        return self.user.username   #return the username of the user

    # resizing images
    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.avatar.path)  #assign variable to open the image

        if img.height > 100 and img.width > 100:    #if the image is greater than 100x100

            new_img = (100,100) #set the new image size to 100x100
            img.thumbnail(new_img)  #resize the image
            img.save(self.avatar.path)  #save the image
            
        elif img.height > 100 or img.width > 100:   #if only one dimension is greater than 100x100
            
            new_img = (img.width, 100 ) if img.height > 100 else (100, img.height)  #set that dimension to 100
            img.thumbnail(new_img)  #resize the image
            img.save(self.avatar.path)  #save the image
