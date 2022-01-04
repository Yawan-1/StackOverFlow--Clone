from django import forms
from .models import Question,Answer,Bounty,ProtectQuestion
from .models import BannedUser

class InlineTagEditForm(forms.ModelForm):

	class Meta:
		model = Question
		fields = ['tags']

class SearchForm(forms.Form):
	noAnswers = forms.BooleanField(initial=False)

class BanUser_Form(forms.ModelForm):

	class Meta:
		model = BannedUser
		fields = ['banned_reasons', 'ban_till']

class BountyForm(forms.ModelForm):

	class Meta:
		model = Bounty
		fields = ['bounty_value','why_bounting']

class QuestionForm(forms.ModelForm):

	class Meta:
		model = Question
		fields = ['title','body','tags']

class AnswerForm(forms.ModelForm):

	class Meta:
		model = Answer
		fields = ['body','is_wiki_answer']

class UpdateQuestion(forms.ModelForm):

	class Meta:
		model = Question
		fields = ['title','body','tags','why_editing_question']

class EditAnswerForm(forms.ModelForm):

	class Meta:
		model = Answer
		fields = ['body','why_editing_answer']

# class ReviewAnswer(forms.ModelForm):

# 	class Meta:
# 		model = ReviewFirstAnswer
# 		fields = ['actions']

CHOICES=[('select1','select 1'),
         ('select2','select 2')]


class ProtectForm(forms.ModelForm):

	class Meta:
		model = ProtectQuestion
		fields = ['why_want_toProtect']