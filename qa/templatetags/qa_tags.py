from django import template
from qa.models import Reputation,Question,BookmarkQuestion,Answer
from django.db.models import Count,BooleanField, ExpressionWrapper, Q,Exists, OuterRef,Avg, Min,Max, Sum,F, IntegerField, FloatField,Case, Value, When
from tagbadge.models import TagBadge
from django.utils import timezone
from datetime import timedelta



register = template.Library()

"""This template tag is now useless, Because i built this for-
ordering items in loop without having multiple queries in rendering view
but it was showing "Duplicate results", so i decided
to build every query in view instead of using this.
Not Working -- Never used in any of app's templates.
"""
@register.filter
def sort_by(queryset, order):
    return queryset.order_by(order)
    # Tried "return queryset.distinct().order_by(order)" But it was still showing duplicate items.

@register.filter
def percentage(value):
    return format(100*value/10)

@register.filter
def advanced_percentage(queryset, from_how_much):
    return format(100*queryset/from_how_much)

@register.filter
def advanced_percentage_without_profile(from_how_much):
    return format(100*from_how_much/300)

@register.filter
def calculate_remaining_time(queryset):
    from_7_days = timezone.now() - timedelta(days=7)
    return queryset - from_7_days

"""
This template tag (calculate_reputation) is for display user's reputation in for (template) loop.
Working -- Fine
"""
@register.filter
def calculate_reputation(user_id):
    if user_id.is_authenticated:
        getAlltheReputation = Reputation.objects.filter(
                                awarded_to=user_id).aggregate(
                                    Sum('answer_rep_C'),Sum('question_rep_C'))
        Q_rep = getAlltheReputation['question_rep_C__sum']
        final_Q_Rep = getAlltheReputation['question_rep_C__sum'] if Q_rep else 0
        A_rep = getAlltheReputation['answer_rep_C__sum']
        final_A_Rep = getAlltheReputation['answer_rep_C__sum'] if A_rep else 0
        return final_Q_Rep + final_A_Rep


# It will count and show all "Gold Badges" on profile right corner.
@register.filter
def calculateGoldBadges(user_id):
    if user_id.is_authenticated:
        getAllTheGoldBadges = TagBadge.objects.filter(awarded_to_user=user_id,badge_type="GOLD").count()
        return getAllTheGoldBadges


# It will count and show all "Bronze Badges" on profile right corner.
@register.filter
def calculateBronzeBadges(user_id):
    if user_id.is_authenticated:
        getAllTheBronzeBadges = TagBadge.objects.filter(awarded_to_user=user_id,badge_type="BRONZE").count()
        return getAllTheBronzeBadges


# It will count and show all "Silver Badges" on profile right corner.
@register.filter
def calculatSilvereBadges(user_id):
    if user_id.is_authenticated:
        getAllTheSilverBadges = TagBadge.objects.filter(awarded_to_user=user_id,badge_type="SILVER").count()
        return getAllTheSilverBadges


@register.filter
def calculateEarned_Badge_Users(tag):
    countBadge = TagBadge.objects.filter(id=tag).annotate(Count('awarded_to_user'))
    return countBadge


@register.filter
def count_questions_by_tag(user_id,tag):
    count_questions = Question.objects.filter(post_owner=user_id,tags=tag).count()
    return count_questions


@register.filter
def count_questions_by_tag_without_user(tag):
    count_questions_by_tagUser = Question.objects.filter(tags=tag).count()
    return count_questions_by_tagUser


@register.filter
def count_all_bookmarkers(user_id):
    countBookmarks = BookmarkQuestion.objects.filter(bookmarked_by=user_id).count()
    return countBookmarks

@register.filter
def count_answers_by_user(user_id):
    countAnswers = Answer.objects.filter(answer_owner=user_id).count()
    return countAnswers

@register.filter
def count_questions_by_user(user_id):
    countQuestions = Question.objects.filter(post_owner=user_id).count()
    return countQuestions