from django import forms
from .models import Profile,Position
from martor.fields import MartorFormField

class EditProfileForm(forms.ModelForm):

	class Meta:
		model = Profile
		fields = ['profile_photo','full_name','location','title','about_me',
					'website_link','twitter_link','github_link',
							'not_to_Display_Full_name']

class EmailForm(forms.Form):
	name = forms.CharField(max_length=25)
	email = forms.EmailField()
	review = MartorFormField()

class PositionCreateForm(forms.ModelForm):

	class Meta:
		model = Position
		fields = ['company_name','title']

JOB_TYPE_CHOICES = [

    ('FULL_TIME', 'Full Time'),
    ('CONTRCT', 'Contract'),
    ('InternShip', 'InternShip'),

]


class EditJobPrefrences(forms.ModelForm):
	# job_type = forms.MultipleChoiceField(choices=JOB_TYPE_CHOICES, widget=forms.CheckboxSelectMultiple())

	class Meta:
		model = Profile
		fields = ['min_expierence_level',
					'max_expierence_level','job_type',
						'job_search_status','phone_number']
		widgets = {
			'job_search_status': forms.RadioSelect(),
			# 'job_type': forms.CheckboxSelectMultiple(),
		}

			

class EditEmailForm(forms.ModelForm):

	class Meta:
		model = Profile
		fields = ['email']