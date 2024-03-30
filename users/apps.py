from django.apps import AppConfig


class UserConfig(AppConfig): 
    
    default_auto_field = 'django.db.models.BigAutoField' #default field set to large
    name = 'users' #just to stop names from clashing

    def ready(self):
        import users.signals  #noqa
