from django.shortcuts import redirect,render
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied
import time
from qa.models import Question,Answer
from .models import ReviewQuestionEdit
from qa.models import Reputation
import datetime
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count,BooleanField, ExpressionWrapper, Q,Exists, OuterRef,Avg, Min,Max, Sum,F, IntegerField, FloatField,Case, Value, When
# https://stackoverflow.com/questions/31197517/how-to-test-user-ownership-of-object-using-django-decorators

def timeit(method):

   def timed(*args, **kw):
       ts = time.time()
       result = method(*args, **kw)
       te = time.time()
       print('%r (%r, %r) %2.2f sec' % (method.__name__, args, kw, te - ts))
       return result

   return timed

def awardReputation(function):
	def awardIt(request, *args, **kwargs):
		if request.user.is_authenticated:
			print("Printing Decorator Stuff \n")
			pk = kwargs["question_id"]
			getQuestion = Question.objects.get(pk=pk)
			print(getQuestion)
			print(pk)
			user = request.user
			print(user)
			last_24_hours = timezone.now() - timedelta(hours=3)
			getReputationEarnedInLast_24Hours = Reputation.objects.filter(
                            awarded_to=getQuestion.post_owner, date_earned__gte=last_24_hours).aggregate(
                                    Sum('answer_rep_C'),Sum('question_rep_C'))
         # if getReputationEarnedInLast_24Hours
			d1 = getReputationEarnedInLast_24Hours['question_rep_C__sum']
			totling2 = getReputationEarnedInLast_24Hours['question_rep_C__sum'] if d1 else 0
			# print(getAlltheReputation)
			s2 = getReputationEarnedInLast_24Hours['answer_rep_C__sum']
			totlingAnsRep2 = getReputationEarnedInLast_24Hours['answer_rep_C__sum'] if s2 else 0

			print("Printing reputation earned in last 24 Hours :-:")
			print(totling2 + totlingAnsRep2)
			finalReputation = totling2 + totlingAnsRep2

			if finalReputation >= 10:
				request.user.profile.reputation += 500
				request.user.profile.save()
				print("Award the Badge that have to award at 200 reputation earn in 24 Hours")
			print("\n")
			return function(request, *args, **kwargs)
		else:
			return redirect('users:login_request')

	return awardIt


def required_500_RepToReview(function):
	def redirectFunc(request, *args, **kwargs):
		if request.user.is_authenticated:
			if request.user.profile.access_review_queues:
				return function(request, *args, **kwargs)
			else:
				return render(request, 'Denied/requiredRep_500.html')
		else:
			return redirect('users:login_request')

	return redirectFunc

def required_3000_RepToReview(function):
# def required_3000_RepToReview(function, obj):
	def redirectFunc(request, *args, **kwargs):
		if request.user.is_authenticated:
			# if request.user == obj.post_owner or request.user == obj.answer_owner:
			if request.user.profile.cast_close_AND_Reopen_votes:
				return function(request, *args, **kwargs)
			else:
				# DIDN'T CREATE THE TEMPLATE YET.
				return render(request, 'Denied/requiredRep_3000.html')
		else:
			return redirect('users:login_request')

	return redirectFunc

def required_2000_RepToReview(function):
	def redirectFunc(request, *args, **kwargs):
		pk = kwargs['reviewquestionedit_id']
		getReviewing_item = ReviewQuestionEdit.objects.get(id=pk)
		if getReviewing_item.question_to_view:
			getQuestion = Question.objects.get(reviewquestionedit=pk)
		else:
			getAnswer = Answer.objects.get(reviewquestionedit=pk)
		if request.user.is_authenticated:
			if request.user.profile.review_close_votes:
				print("Redirect through First Statement")
				return function(request, *args, **kwargs)
			elif getReviewing_item.question_to_view and request.user == getQuestion.post_owner:
				print("Redirect through Second Statement")
				return function(request, *args, **kwargs)
			elif getReviewing_item.answer_to_view_if and request.user == getAnswer.answer_owner:
				print("Redirect through Third Statement")
				return function(request, *args, **kwargs)
			else:
				return render(request, 'Denied/requiredRep_2000.html')
		else:
			return redirect('users:login_request')

	return redirectFunc


def required_10000_RepToTools(function):
	def redirectFunc(request, *args, **kwargs):
		if request.user.is_authenticated:
			if request.user.profile.accessTo_moderatorTools:
				return function(request, *args, **kwargs)
			else:
				return render(request, 'Denied/requiredRep_10000.html')
		else:
			return redirect('users:login_request')

	return redirectFunc