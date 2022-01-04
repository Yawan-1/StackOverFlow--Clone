from django import forms
from .models import FirstAnswerReview,FirstQuestionReview,LateAnswerReview
# from .models import QuestionEdit
from .models import ReOpenQuestionVotes,ReviewQuestionReOpenVotes,CloseQuestionVotes
from .models import ReviewCloseVotes,ReviewQuestionEdit,ReviewLowQualityPosts
from .models import ReviewFlagPost,FlagPost,FlagComment,ReviewFlagComment

class FlagQuestionForm(forms.ModelForm):
	# like = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)

	class Meta:
		model = FlagPost
		fields = ['actions_Flag_Q']
		widgets = {
			'actions_Flag_Q': forms.RadioSelect()
		}

class AnswerFlagForm(forms.ModelForm):

	class Meta:
		model = FlagPost
		fields = ['actions_Flag_Q']
		widgets = {
			'actions_Flag_Q': forms.RadioSelect()
		} 

class ReviewFlagCommentForm(forms.ModelForm):

	class Meta:
		model = ReviewFlagComment
		fields = ['c_flagReviewActions']
		widgets = {
			'c_flagReviewActions': forms.RadioSelect()
		} 

class CommentFlagForm(forms.ModelForm):

	class Meta:
		model = FlagComment
		fields = ['why_flagging']

class LowQualityReviewForm(forms.ModelForm):

	class Meta:
		model = ReviewLowQualityPosts
		fields = ['reviewActions']
		widgets = {
			'reviewActions': forms.RadioSelect()
		}

class FlagPostForm(forms.ModelForm):

	class Meta:
		model = ReviewFlagPost
		fields = ['flagReviewActions']
		widgets = {
			'flagReviewActions': forms.RadioSelect()
		}

# class ReviewForm(forms.ModelForm):

# 	class Meta:
# 		model = Review
# 		fields = ['actions']
# 		widgets = {
# 			'actions': forms.RadioSelect()
# 		}

class SuggesstedEditForm(forms.ModelForm):

	class Meta:
		model = ReviewQuestionEdit
		fields = ['reviewActions']
		widgets = {
			'reviewActions': forms.RadioSelect()
		} 


class CloseForm_Q(forms.ModelForm):

	class Meta:
		model = CloseQuestionVotes
		fields = ['why_closing','duplicate_of']
		widgets = {
			'why_closing': forms.RadioSelect()
		}


class AnswerReviewForm(forms.ModelForm):

	class Meta:
		model = FirstAnswerReview
		fields = ['actions']
		widgets = {
			'actions': forms.RadioSelect()
		}

class QuestionReviewForm(forms.ModelForm):

	class Meta:
		model = FirstQuestionReview
		fields = ['questionActions']
		widgets = {
			'questionActions': forms.RadioSelect()
		}

class LateAnswerReviewForm(forms.ModelForm):

	class Meta:
		model = LateAnswerReview
		fields = ['L_AnswerActions']
		widgets = {
			'L_AnswerActions': forms.RadioSelect()
		}

# class EditReviewQuestion(forms.ModelForm):

# 	class Meta:
# 		model = QuestionEdit
# 		fields = ['approval_from_user']
# 		widgets = {
# 			'approval_from_user': forms.RadioSelect()
# 		}




class ReviewReOpenForm(forms.ModelForm):

	class Meta:
		model = ReviewQuestionReOpenVotes
		fields = ['reviewActions']
		widgets = {
			'reviewActions': forms.RadioSelect()
		}
class VoteToReOpenForm(forms.ModelForm):

	class Meta:
		model = ReOpenQuestionVotes
		fields = ['why_opening']
		widgets = {
			'why_opening' : forms.RadioSelect()
		} 

class ReviewCloseForm(forms.ModelForm):

	class Meta:
		model = ReviewCloseVotes
		fields = ['reviewActions']
		widgets = {
			'reviewActions' : forms.RadioSelect()
		}
