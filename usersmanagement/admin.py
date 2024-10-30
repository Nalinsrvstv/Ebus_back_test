from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from .models import CustomUser
from .utils import send_welcome_email
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email','username')  # Include only the 'email' field in the form

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm  # Use the custom form for user creation
    list_display = ('email', 'first_name', 'last_name', 'is_staff')

    # Remove the 'confirm password' field from the add user form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email','username', 'password1', 'password2'),
        }),
    )

    def save_model(self, request, obj, form, change):
        print("!!!!!!!!!!change"+str(change))
        # Call the parent class's save_model method to perform the actual user creation
        super().save_model(request, obj, form, change)
        # send mail only on first registration time 
        if(change==False):
            # Send a welcome email to the newly created user
            send_welcome_email(email=obj.email,password=form.cleaned_data["password1"],username=obj.username)
       

# Register your CustomUser model with the custom admin class
admin.site.register(CustomUser, CustomUserAdmin)
