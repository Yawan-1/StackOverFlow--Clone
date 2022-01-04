from qa.models import Question,Answer
from django.shortcuts import render, redirect
import datetime
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Count, Min, Sum
# cp = CONTEXT_PROCESSORS
# from .models import QuestionEdit
from django.db.models import Avg, Count, Min, Sum
from django.db.models import Q
from .models import ReviewCloseVotes,ReOpenQuestionVotes,ReviewQuestionReOpenVotes
from .models import QuestionEditVotes,ReviewQuestionEdit,ReviewLowQualityPosts,ReviewFlagPost
from .models import ReviewFlagComment


def reviewAnswer_cp(request):
	time = timezone.now() - timedelta(minutes=200)
	post_ids_subquery_2 = Answer.objects.filter(
							date__gt=time).values('answer_owner').annotate(
							min_id=Min('id')).values('min_id')
	next_blog = ''
	if request.user.is_authenticated:
		next_blog = Answer.objects.filter(
							firstanswerreview__actions__isnull=True).exclude(answer_owner=request.user).filter(
							id__in=post_ids_subquery_2).order_by('id').first()
	return {
		'next_blog':next_blog
	}

def returnTrue(request):
	time = timezone.now() - timedelta(minutes=200)
	post_ids_subquery_2 = Answer.objects.filter(
							date__gt=time).values('answer_owner').annotate(
							min_id=Min('id')).values('min_id')
	counting = 0
	if request.user.is_authenticated:
		counting = Answer.objects.filter(
					firstanswerreview__actions__isnull=True).exclude(answer_owner=request.user).filter(
						id__in=post_ids_subquery_2).count()

	if counting >= 1:
		can_show = True
	else:
		can_show = False

	return {
		'can_show':can_show,
    }

def reviewQuestion_cp(request):
	time = timezone.now() - timedelta(minutes=200)
	post_ids_subquery = ''
	next_question = ''

	if request.user.is_authenticated:
		post_ids_subquery = Question.objects.filter(
	                            date__gt=time
	                        ).values(
	                            'post_owner'
	                        ).annotate(
	                            min_id=Min('id')
	                        ).values('min_id')

		next_question = Question.objects.filter(
						firstquestionreview__QuestionReviewBy__isnull=True).exclude(post_owner=request.user).filter(
							id__in=post_ids_subquery).order_by('id').first()
	return {
		'next_question':next_question
	}


def returnTrue_or_False(request):
	time = timezone.now() - timedelta(minutes=200)
	post_ids_subquery = ''
	counting = 0
	if request.user.is_authenticated:
		post_ids_subquery = Question.objects.filter(
	                            date__gt=time
	                        ).values(
	                            'post_owner'
	                        ).annotate(
	                            min_id=Min('id')
	                        ).values('min_id')

		counting = Question.objects.filter(firstquestionreview__QuestionReviewBy__isnull=True).exclude(post_owner=request.user).filter(id__in=post_ids_subquery).count()

	if counting >= 1:
		can_review = True
	else:
		can_review = False

	return {
		'can_review':can_review
	}

def reviewLateAnswer_cp(request):
	isOlderThanFiveHours = timezone.now() - timedelta(minutes=10)
	questionIDS = Answer.objects.filter(
			lateanswerreview__L_AnswerActions__isnull=True).filter(
				questionans__date__gt=timezone.now() - timedelta(hours=100)).filter(
					date__gt=timezone.now() - timedelta(minutes=100)).order_by('id').first()

	# next_question = Question.objects.filter(firstquestionreview__QuestionReviewBy__isnull=True).filter(id__in=post_ids_subquery).order_by('id').first()
	return {
		'questionIDS':questionIDS
	}

def returnLateReview_True_or_False(request):
	# time = timezone.now() - timedelta(minutes=200)
	isOlderThanFiveHours = timezone.now() - timedelta(minutes=10)
	# lateAnswers = Question.objects.filter(
 #                    date__gt=timezone.now() - timedelta(hours=100)).filter(
 #                        answer__date_added__gt=isOlderThanFiveHours)

	counting = Answer.objects.filter(
				lateanswerreview__L_AnswerActions__isnull=True).filter(
					questionans__date__gt=timezone.now() - timedelta(hours=100)).filter(
						date__gt=timezone.now() - timedelta(minutes=10)).count()

	if counting >= 1:
		cal_LateRev = True
	else:
		cal_LateRev = False

	return {
		'cal_LateRev':cal_LateRev
	}


def reviewClosedQuestions(request):
	reviewCloseQuestionID = ''
	if request.user.is_authenticated:
		# Edit .exclude(question_to_closed__is_closed=True), Exclude those questions why are closed on the spot (In Question Detail) without waiting in review queue.
		reviewCloseQuestionID = ReviewCloseVotes.objects.filter(is_completed=False).exclude(question_to_closed__is_closed=True).exclude(reviewed_by=request.user).order_by('id').first()

	return {
		'reviewCloseQuestionID':reviewCloseQuestionID,
	}

def returnTrue_or_FalseClosedQuestions(request):
	counting = 0
	if request.user.is_authenticated:
		# Edit .exclude(question_to_closed__is_closed=True), Exclude those questions why are closed on the spot (In Question Detail) without waiting in review queue.
		counting = ReviewCloseVotes.objects.filter(is_completed=False).exclude(question_to_closed__is_closed=True).exclude(reviewed_by=request.user).count()

	if counting >= 1:
		areClosedQuestions_Available = True
	else:
		areClosedQuestions_Available = False

	return {
		'areClosedQuestions_Available':areClosedQuestions_Available,
	}


def reviewReOpenQuestion_sVotes(request):
	reviewTo_ReOpenQuestionID = ''
	if request.user.is_authenticated:
		reviewTo_ReOpenQuestionID = ReviewQuestionReOpenVotes.objects.filter(is_completed=False).exclude(reopen_reviewed_by=request.user).order_by('id').first()

	return {
		'reviewTo_ReOpenQuestionID':reviewTo_ReOpenQuestionID,
	}

def returnTrue_or_FalseUnCloseQuestion_s(request):
	counting = 0
	if request.user.is_authenticated:
		counting = ReviewQuestionReOpenVotes.objects.filter(is_completed=False).exclude(reopen_reviewed_by=request.user).count()

	if counting >= 1:
		questionToReOpen_available = True
	else:
		questionToReOpen_available = False

	return {
		'questionToReOpen_available':questionToReOpen_available,
	}

def reviewEditedPosts(request):
	reviewEditedPts = ''
	if request.user.is_authenticated:
		reviewEditedPts = ReviewQuestionEdit.objects.filter(is_reviewed=False).exclude(edit_reviewed_by=request.user).order_by('id').first()

	return {
		'reviewEditedPts':reviewEditedPts,
	}

def returnTrue_or_FalseEditPosts(request):
	counting = 0
	if request.user.is_authenticated:
		counting = ReviewQuestionEdit.objects.filter(is_reviewed=False).exclude(edit_reviewed_by=request.user).count()

	if counting >= 1:
		editQuestions_review_Available = True
	else:
		editQuestions_review_Available = False

	return {
		'editQuestions_review_Available':editQuestions_review_Available,
	}

def reviewLowQualityPosts(request):
	reviewLowPts = ''
	if request.user.is_authenticated:
		reviewLowPts = ReviewLowQualityPosts.objects.filter(is_reviewed=False).exclude(reviewers=request.user).order_by('id').first()

	return {
		'reviewLowPts':reviewLowPts
	}

def returnTrue_or_FalseLowPosts(request):
	counting = 0
	if request.user.is_authenticated:
		counting = ReviewLowQualityPosts.objects.filter(is_reviewed=False).exclude(reviewers=request.user).count()

	if counting >= 1:
		reviewLowPosts = True
	else:
		reviewLowPosts = False

	return {
		'reviewLowPosts':reviewLowPosts,
	}

def reviewFlagPosts(request):
	reviewFlagPts = ''
	if request.user.is_authenticated:
		reviewFlagPts = ReviewFlagPost.objects.filter(flag_is_reviewed=False).exclude(flag_reviewed_by=request.user).order_by('id').first()

	return {
		'reviewFlagPts':reviewFlagPts
	}

def returnTrue_or_FalseFlagPosts(request):
	counting = 0
	if request.user.is_authenticated:
		counting = ReviewFlagPost.objects.filter(flag_is_reviewed=False).exclude(flag_reviewed_by=request.user).count()

	if counting >= 1:
		is_available_FlagPosts = True
	else:
		is_available_FlagPosts = False

	return {
		'is_available_FlagPosts':is_available_FlagPosts
	}

def reviewFlagComments(request):
	reviewFlagCmnts = ''
	if request.user.is_authenticated:
		reviewFlagCmnts = ReviewFlagComment.objects.filter(c_is_reviewed=False).exclude(c_flag_reviewed_by=request.user).order_by('id').first()

	return {
		'reviewFlagCmnts':reviewFlagCmnts
	}

def returnTrue_or_FalseFlagComments(request):
	counting = 0
	if request.user.is_authenticated:
		counting = ReviewFlagComment.objects.filter(c_is_reviewed=False).exclude(c_flag_reviewed_by=request.user).count()

	if counting >= 1:
		is_available_FlagComments = True
	else:
		is_available_FlagComments = False

	return {
		'is_available_FlagComments':is_available_FlagComments
	}