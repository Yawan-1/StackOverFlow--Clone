from django.shortcuts import render, redirect
import datetime
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Count, Min, Sum, Q
from qa.models import Question
from notification.models import PrivRepNotification,Notification

def top_questions(request):
	questionsHome = Question.objects.filter(
							is_deleted=False, is_bountied=False).order_by(
							'-date')[:50]
	return {
			'questionsHome':questionsHome
		}

def count_all_bounties(request):
	bounties = Question.objects.filter(is_bountied=True)

	return {
		'count_bounty': bounties.count()
	}