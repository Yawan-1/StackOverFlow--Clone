from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile,Position
import datetime
from django.utils import timezone
from datetime import timedelta
from qa.models import Answer,ProtectQuestion
from .forms import EditProfileForm,EmailForm,EditJobPrefrences,EditEmailForm
from django.contrib import messages
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from qa.models import Question,Bounty,BookmarkQuestion,CommentQ,Reputation,QUpvote,QDownvote
from itertools import chain
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from review.models import CloseQuestionVotes,ReOpenQuestionVotes,FlagComment,FlagPost
from tagbadge.models import TagBadge
from django.contrib.auth.models import User
from taggit.models import Tag
from .decorators import unBanRequired,profileOwnerRequired_For_Edit
from .forms import PositionCreateForm,PositionCreateForm
from django.core import serializers
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.db.models import Count,BooleanField, ExpressionWrapper, Q,Exists, OuterRef,Avg, Min,Max, Sum,F, IntegerField, FloatField,Case, Value, When
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from notification.models import Notification
from .decorators import profileOwnerRequired_For_Edit
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
import re
from review.models import ReviewCloseVotes,ReviewQuestionReOpenVotes
from django.db.models import F
import online_users.models
from notification.models import PrivRepNotification

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

"""
The HttpRequest.is_ajax() method is removed in DJANGO 4, 
so i used is_ajax function to check if the request is
ajax or Not by identifying 'XMLHttpRequest'
Also replaced is_ajax method with this is_ajax function.
"""
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def Ajax_searchTag(request):
    q = request.GET.get('w')
    results = Tag.objects.filter(name__icontains=q).distinct()
    serialized_results = []
    for result in results:
        serialized_results.append({
            'id': result.id,
            'tag_name': result.name,
            # 'results':result,
            })

    return JsonResponse({'results': serialized_results})

def tagsPage(request):
    All_tags = Question.tags.most_common()

    context = {'All_tags':All_tags,}
    return render(request, 'profile/tagsPage.html', context)

def usersPage(request):
    users = User.objects.all()

    context = {'users': users}
    return render(request, 'profile/usersPage.html', context)

def Ajax_searchUser(request):
    q = request.GET.get('w')
    results = User.objects.filter(username__icontains=q).distinct()
    serialized_results = []
    for result in results:
        if result.profile.profile_photo:
            photo = result.profile.profile_photo.url
        else:
            photo = ''
        serialized_results.append({
            'id': result.id,
            'photo': photo,
            'user_name': result.username,
            # 'user_location': result.profile.location,
            })
    print(serialized_results)

    return JsonResponse({'results': serialized_results})

# def tags(request):
#     allTags = Question.tags.most_common()

#     context = {'allTags':allTags}
#     return render(request, 'qa/tags.html', context)


def searchTagFromQuery(request):

    query = request.GET.get('tagQuery')
    filters = request.GET.getlist('filters')
    sort = request.GET.getlist('sort')
    print(query)
    print(filters)
    print(sort)
    # getTag = Tag.objects.filter(name__icontains=query)
    getQuestions = ''
    if query:
        tags = query.split(',')
        getQuestions = Question.objects.filter(tags__name__in=tags)
    # tags = ''
    if "NoAnswers" in filters:
        bool_1 = True
    else:
        bool_1 = False

    if "NoAcceptedAnswer" in filters:
        bool_2 = True
    else:
        bool_2 = False

    if "Bounty" in filters:
        bool_3 = True
    else:
        bool_3 = False



    if bool_1 and bool_2 == False and bool_3 == False:
        print("Only First is True")



    if bool_2 and bool_1 == False and bool_3 == False:
        print("Only Second is True")



    if bool_2 and bool_1 == True and bool_3 == False:
        print("First and Second is True")


    if bool_1 and bool_3 == True and bool_2 == False:
        print("First and Third is True")


    if bool_2 and bool_3 == True and bool_2 == False:
        print("Second and Third is True")




# qsts_pks = QueryStringTag.objects.filter(tag__pk__in=['12', '14', '15']).values_list('id', flat=True)



# queries = QueryString.objects.filter(qsquerystring__pk__in=qsts_pks)



    context = {'filters':filters,'query':query,'getQuestions':getQuestions,}
    return render(request, 'qa/searchTagFromQuery.html', context)

"""
- Summary (It will be Default) - DONE
- Answers - DONE
- Questions - DONE
- Tags - DONE
- Badges - DONE
- Bookmarks - DONE
- Bounties - DONW 
- Reputation
- All Actions - DONE
"""

# def getQuestionFrom_tag(request, tag_id):

#     context = {}

# @cache_page(60 * 15)
def activitAnswers(request, user_id, username):
    profileData = get_object_or_404(Profile, pk=user_id)

    countAnswers = Answer.objects.filter(answer_owner=profileData.user).exclude(is_deleted=True).count()

    # Most Votes Answer - Tab One
    most_vote_answers = Answer.objects.filter(answer_owner=user_id).annotate(countThem=Count('a_vote_ups')).order_by('-countThem')
    page = request.GET.get('page', 1)
    paginator = Paginator(most_vote_answers, 35)
    try:
        mostVotes_answers = paginator.page(page)
    except PageNotAnInteger:
        mostVotes_answers = paginator.page(1)
    except EmptyPage:
        mostVotes_answers = paginator.page(paginator.num_pages)


    # Most Votes Answer - Tab One
    recent_edited_answers = Answer.objects.filter(answer_owner=user_id).order_by('-a_edited_time')
    recentAnswerPage = request.GET.get('page', 1)
    recentAnswerPaginator = Paginator(recent_edited_answers, 35)
    try:
        recentEdited_answers = recentAnswerPaginator.page(recentAnswerPage)
    except PageNotAnInteger:
        recentEdited_answers = recentAnswerPaginator.page(1)
    except EmptyPage:
        recentEdited_answers = recentAnswerPaginator.page(recentAnswerPaginator.num_pages)


    # Most Votes Answer - Tab One
    new_answers = Answer.objects.filter(answer_owner=user_id).order_by('-date')

    newest_answer_page = request.GET.get('page', 1)
    newest_answer_paginator = Paginator(new_answers, 35)
    try:
        newest_answers = newest_answer_paginator.page(newest_answer_page)
    except PageNotAnInteger:
        newest_answers = newest_answer_paginator.page(1)
    except EmptyPage:
        newest_answers = newest_answer_paginator.page(newest_answer_paginator.num_pages)



    USER_ONLINE_TIMEOUT = timedelta(seconds=5)
    min_time = timezone.now() - (USER_ONLINE_TIMEOUT)
    queryset = online_users.models.OnlineUserActivity.objects.filter(
        user_id=user_id).annotate(is_online=Case(
            When(last_activity__gte=min_time, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ))

    online_user_activity = get_object_or_404(queryset)


    countVotedPosts_Q = QUpvote.objects.filter(upvote_by_q=user_id).count()
    countDownVotedPosts_Q = QDownvote.objects.filter(downvote_by_q=user_id).count()

    countVotedPosts_A = Answer.objects.filter(a_vote_ups=user_id).count()
    countDownVotedPosts_A = Answer.objects.filter(a_vote_downs=user_id).count()

    getVotesCast_Final = countVotedPosts_Q + countDownVotedPosts_Q + countVotedPosts_A + countDownVotedPosts_A

    # People Reached
    getAllTheViewsOfAllTheQuestion = Question.objects.filter(post_owner=profileData.user).annotate(total_views=Count('viewers')).aggregate(Sum('total_views'))

    reputation_graph = Reputation.objects.filter(awarded_to=user_id)[:15]


    # ----------Next Badge---------- START----------
    countComments = CommentQ.objects.filter(commented_by=profileData.user).count()



    if profileData.about_me == '':
        completed = True
    else:
        completed = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Benefactor").exists():
        benefactor_earned = True
    else:
        benefactor_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Citizen Patrol",bade_position="BADGE").exists():
        ctzn_ptrl_earned = True
    else:
        ctzn_ptrl_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Civic Duty",bade_position="BADGE").exists():
        civc_duty = True
    else:
        civc_duty = False
    getVotedOnQ = Question.objects.filter(qupvote__upvote_by_q=profileData.user).count()
    getVotedOnQ_Down = Question.objects.filter(qdownvote__downvote_by_q=profileData.user).count()
    getVotedOn = Answer.objects.filter(a_vote_ups=profileData.user).count()
    getVotedOn_Down = Answer.objects.filter(a_vote_downs=profileData.user).count()

    countVotes = getVotedOnQ+getVotedOnQ_Down+getVotedOn+getVotedOn_Down



    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Critic", bade_position="BADGE").exists():
        critic_earned = True
    else:
        critic_earned = False



    if profileData.helpful_flags_counter:
        deputy_earned = True
    else:
        deputy_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Disciplined",bade_position="BADGE").exists():
        disclpned_earned = True
    else:
        disclpned_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Excavator",bade_position="BADGE").exists():
        excvter_earned = True
    else:
        excvter_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Investor", bade_position="BADGE").exists():
        investor_earned = True
    else:
        investor_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="GOLD", tag_name="Marshal", bade_position="BADGE").exists():
        marshal_earned = True
    else:
        marshal_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Necromancer",bade_position="BADGE").exists():
        necromancer_earned = True
    else:
        necromancer_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Peer Pressure",bade_position="BADGE").exists():
        pr_pressre_earned = True
    else:
        pr_pressre_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Promoter", bade_position="BADGE").exists():
        promoter_earned = True
    else:
        promoter_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Proofreader",bade_position="BADGE").exists():
        proffreader_earned = True
    else:
        proffreader_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Refiner",bade_position="BADGE").exists():
        refiner_earned = True
    else:
        refiner_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="Bronze", tag_name="Revival",bade_position="BADGE").exists():
        reviv_earned = True
    else:
        reviv_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Self-Learner",bade_position="BADGE").exists():
        slf_lrnr_earned = True
    else:
        slf_lrnr_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Strunk & White",bade_position="BADGE").exists():
        stnk_whte_earned = True
    else:
        stnk_whte_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Suffrage",bade_position="BADGE").exists():
        suffrage_earned = True
    else:
        suffrage_earned = False

    last_24_hours = timezone.now() - timedelta(hours=24)
    getQ_Votes_in_24_Hours = QUpvote.objects.filter(date__gt=last_24_hours).count()
    getQ_DownVotes_in_24_Hours = QDownvote.objects.filter(downvote_by_q=profileData.user, date__gt=last_24_hours).count()
    getA_Votes_in_24_Hours = Answer.objects.filter(a_vote_ups=profileData.user, date__gt=last_24_hours).count()
    getA_DownVotes_in_24_Hours = Answer.objects.filter(a_vote_downs=profileData.user, date__gt=last_24_hours).count()
    totalVotes = getQ_Votes_in_24_Hours + getQ_DownVotes_in_24_Hours + getA_Votes_in_24_Hours + getA_DownVotes_in_24_Hours

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Vox Populi",bade_position="BADGE").exists():
        vx_pop_earned = True
    else:
        vx_pop_earned = False  



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Teacher",bade_position="BADGE").exists():
        teacher_earned = True
    else:
        teacher_earned = False

    newestBadge = TagBadge.objects.filter(awarded_to_user=profileData.user).last()

    # ----------Next Badge---------- END----------


    context = {
        'newestBadge':newestBadge,
        'countVotes':countVotes,
        'teacher_earned':teacher_earned,
        'totalVotes':totalVotes,
        'vx_pop_earned':vx_pop_earned,
        'suffrage_earned':suffrage_earned,
        'stnk_whte_earned':stnk_whte_earned,
        'slf_lrnr_earned':slf_lrnr_earned,
        'reviv_earned':reviv_earned,
        'refiner_earned':refiner_earned,
        'proffreader_earned':proffreader_earned,
        'promoter_earned':promoter_earned,
        'necromancer_earned':necromancer_earned,
        'marshal_earned':marshal_earned,
        'investor_earned':investor_earned,
        'pr_pressre_earned':pr_pressre_earned,
        'excvter_earned':excvter_earned,
        'deputy_earned':deputy_earned,
        'disclpned_earned':disclpned_earned,
        'civc_duty':civc_duty,
        'critic_earned':critic_earned,
        'ctzn_ptrl_earned':ctzn_ptrl_earned,
        'benefactor_earned':benefactor_earned,
        'completed':completed,
        'countComments':countComments,
        'countAnswers':countAnswers,'reputation_graph':reputation_graph,'getAllTheViewsOfAllTheQuestion':getAllTheViewsOfAllTheQuestion,'recentEdited_answers':recentEdited_answers,'newest_answers':newest_answers,'mostVotes_answers':mostVotes_answers,'profileData':profileData,'online_user_activity':online_user_activity,'getVotesCast_Final':getVotesCast_Final,}
    return render(request, 'profile/activitAnswers.html', context)

# IMPLEMENTED THE LOGIC
    # It will contain answers with "templatetags"
    # Most Votes | Last Edited | Most Recent | Most Views
    # with pagination
def questionsActivity(request, user_id, username):
    profileData = get_object_or_404(Profile, pk=user_id)

    countQuestions = Question.objects.filter(post_owner=profileData.user).exclude(is_deleted=True).count()

    question_most_votes = Question.objects.filter(post_owner=user_id).exclude(is_deleted=True).annotate(countThem=Count('qupvote')).order_by('-countThem')

    question_recent_activity = Question.objects.filter(post_owner=user_id).exclude(is_deleted=True).order_by('-active_date')

    question_newest = Question.objects.filter(post_owner=user_id).exclude(is_deleted=True).order_by('-date')

    question_most_views = Question.objects.filter(post_owner=user_id).exclude(is_deleted=True).annotate(countTheViews=Count('viewers')).order_by('-viewers')

    # page = request.GET.get('page', 1)
    # paginator = Paginator(most_vote_answers, 35)
    # try:
    #     mostVotes_answers = paginator.page(page)
    # except PageNotAnInteger:
    #     mostVotes_answers = paginator.page(1)
    # except EmptyPage:
    #     mostVotes_answers = paginator.page(paginator.num_pages)





    USER_ONLINE_TIMEOUT = timedelta(seconds=5)
    min_time = timezone.now() - (USER_ONLINE_TIMEOUT)
    queryset = online_users.models.OnlineUserActivity.objects.filter(
        user_id=user_id).annotate(is_online=Case(
            When(last_activity__gte=min_time, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ))

    online_user_activity = get_object_or_404(queryset)



    countVotedPosts_Q = QUpvote.objects.filter(upvote_by_q=user_id).count()
    countDownVotedPosts_Q = QDownvote.objects.filter(downvote_by_q=user_id).count()

    countVotedPosts_A = Answer.objects.filter(a_vote_ups=user_id).count()
    countDownVotedPosts_A = Answer.objects.filter(a_vote_downs=user_id).count()

    getVotesCast_Final = countVotedPosts_Q + countDownVotedPosts_Q + countVotedPosts_A + countDownVotedPosts_A


    # People Reached
    getAllTheViewsOfAllTheQuestion = Question.objects.filter(post_owner=profileData.user).annotate(total_views=Count('viewers')).aggregate(Sum('total_views'))

    reputation_graph = Reputation.objects.filter(awarded_to=user_id)[:15]



    # ----------Next Badge---------- START----------
    countComments = CommentQ.objects.filter(commented_by=profileData.user).count()



    if profileData.about_me != '':
        completed = True
    else:
        completed = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Benefactor").exists():
        benefactor_earned = True
    else:
        benefactor_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Citizen Patrol",bade_position="BADGE").exists():
        ctzn_ptrl_earned = True
    else:
        ctzn_ptrl_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Civic Duty",bade_position="BADGE").exists():
        civc_duty = True
    else:
        civc_duty = False
    getVotedOnQ = Question.objects.filter(qupvote__upvote_by_q=profileData.user).count()
    getVotedOnQ_Down = Question.objects.filter(qdownvote__downvote_by_q=profileData.user).count()
    getVotedOn = Answer.objects.filter(a_vote_ups=profileData.user).count()
    getVotedOn_Down = Answer.objects.filter(a_vote_downs=profileData.user).count()

    countVotes = getVotedOnQ+getVotedOnQ_Down+getVotedOn+getVotedOn_Down



    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Critic", bade_position="BADGE").exists():
        critic_earned = True
    else:
        critic_earned = False



    if profileData.helpful_flags_counter:
        deputy_earned = True
    else:
        deputy_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Disciplined",bade_position="BADGE").exists():
        disclpned_earned = True
    else:
        disclpned_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Excavator",bade_position="BADGE").exists():
        excvter_earned = True
    else:
        excvter_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Investor", bade_position="BADGE").exists():
        investor_earned = True
    else:
        investor_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="GOLD", tag_name="Marshal", bade_position="BADGE").exists():
        marshal_earned = True
    else:
        marshal_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Necromancer",bade_position="BADGE").exists():
        necromancer_earned = True
    else:
        necromancer_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Peer Pressure",bade_position="BADGE").exists():
        pr_pressre_earned = True
    else:
        pr_pressre_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Promoter", bade_position="BADGE").exists():
        promoter_earned = True
    else:
        promoter_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Proofreader",bade_position="BADGE").exists():
        proffreader_earned = True
    else:
        proffreader_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Refiner",bade_position="BADGE").exists():
        refiner_earned = True
    else:
        refiner_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="Bronze", tag_name="Revival",bade_position="BADGE").exists():
        reviv_earned = True
    else:
        reviv_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Self-Learner",bade_position="BADGE").exists():
        slf_lrnr_earned = True
    else:
        slf_lrnr_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Strunk & White",bade_position="BADGE").exists():
        stnk_whte_earned = True
    else:
        stnk_whte_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Suffrage",bade_position="BADGE").exists():
        suffrage_earned = True
    else:
        suffrage_earned = False

    last_24_hours = timezone.now() - timedelta(hours=24)
    getQ_Votes_in_24_Hours = QUpvote.objects.filter(date__gt=last_24_hours).count()
    getQ_DownVotes_in_24_Hours = QDownvote.objects.filter(downvote_by_q=profileData.user, date__gt=last_24_hours).count()
    getA_Votes_in_24_Hours = Answer.objects.filter(a_vote_ups=profileData.user, date__gt=last_24_hours).count()
    getA_DownVotes_in_24_Hours = Answer.objects.filter(a_vote_downs=profileData.user, date__gt=last_24_hours).count()
    totalVotes = getQ_Votes_in_24_Hours + getQ_DownVotes_in_24_Hours + getA_Votes_in_24_Hours + getA_DownVotes_in_24_Hours

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Vox Populi",bade_position="BADGE").exists():
        vx_pop_earned = True
    else:
        vx_pop_earned = False  



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Teacher",bade_position="BADGE").exists():
        teacher_earned = True
    else:
        teacher_earned = False

    newestBadge = TagBadge.objects.filter(awarded_to_user=profileData.user).last()

    # ----------Next Badge---------- END----------

    context = {
        'newestBadge':newestBadge,
        'countVotes':countVotes,
        'teacher_earned':teacher_earned,
        'totalVotes':totalVotes,
        'vx_pop_earned':vx_pop_earned,
        'suffrage_earned':suffrage_earned,
        'stnk_whte_earned':stnk_whte_earned,
        'slf_lrnr_earned':slf_lrnr_earned,
        'reviv_earned':reviv_earned,
        'refiner_earned':refiner_earned,
        'proffreader_earned':proffreader_earned,
        'promoter_earned':promoter_earned,
        'necromancer_earned':necromancer_earned,
        'marshal_earned':marshal_earned,
        'investor_earned':investor_earned,
        'pr_pressre_earned':pr_pressre_earned,
        'excvter_earned':excvter_earned,
        'deputy_earned':deputy_earned,
        'disclpned_earned':disclpned_earned,
        'civc_duty':civc_duty,
        'critic_earned':critic_earned,
        'ctzn_ptrl_earned':ctzn_ptrl_earned,
        'benefactor_earned':benefactor_earned,
        'completed':completed,
        'countComments':countComments,

        'reputation_graph':reputation_graph,
        'online_user_activity':online_user_activity,
        'getVotesCast_Final':getVotesCast_Final,
        'question_most_votes':question_most_votes,
        'profileData':profileData,
        'question_recent_activity':question_recent_activity,
        'question_newest':question_newest,
        'question_most_views':question_most_views,
        'getAllTheViewsOfAllTheQuestion':getAllTheViewsOfAllTheQuestion,
        'countQuestions':countQuestions,
    }
    return render(request, 'profile/questionsActivity.html', context)

# IMPLEMENTED THE LOGIC
    # It will contain all the tags user answered on.
def tagsActivity(request, user_id, username):
    profileData = get_object_or_404(Profile, pk=user_id)
    tags = Tag.objects.filter(question__answer__answer_owner=user_id).annotate(answeredOn=Count('taggit_taggeditem_items'))



    totalBookmarks = BookmarkQuestion.objects.filter(bookmarked_by=user_id).count()

# Last seen
# To Show Last Seen in Profile. You'll see as "Last seen"
# Transfer this Variable into config.py
    USER_ONLINE_TIMEOUT = timedelta(seconds=5)
    min_time = timezone.now() - (USER_ONLINE_TIMEOUT)
    queryset = online_users.models.OnlineUserActivity.objects.filter(
        user_id=user_id).annotate(is_online=Case(
            When(last_activity__gte=min_time, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ))

    online_user_activity = get_object_or_404(queryset)



    # Total Votes Cast
    countVotedPosts_Q = QUpvote.objects.filter(upvote_by_q=user_id).count()
    countDownVotedPosts_Q = QDownvote.objects.filter(downvote_by_q=user_id).count()

    countVotedPosts_A = Answer.objects.filter(a_vote_ups=user_id).count()
    countDownVotedPosts_A = Answer.objects.filter(a_vote_downs=user_id).count()

    getVotesCast_Final = countVotedPosts_Q + countDownVotedPosts_Q + countVotedPosts_A + countDownVotedPosts_A



    # People Reached
    getAllTheViewsOfAllTheQuestion = Question.objects.filter(post_owner=profileData.user).annotate(total_views=Count('viewers')).aggregate(Sum('total_views'))


    reputation_graph = Reputation.objects.filter(awarded_to=user_id)[:15]




    # ----------Next Badge---------- START----------
    countComments = CommentQ.objects.filter(commented_by=profileData.user).count()



    if profileData.about_me != '':
        completed = True
    else:
        completed = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Benefactor").exists():
        benefactor_earned = True
    else:
        benefactor_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Citizen Patrol",bade_position="BADGE").exists():
        ctzn_ptrl_earned = True
    else:
        ctzn_ptrl_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Civic Duty",bade_position="BADGE").exists():
        civc_duty = True
    else:
        civc_duty = False
    getVotedOnQ = Question.objects.filter(qupvote__upvote_by_q=profileData.user).count()
    getVotedOnQ_Down = Question.objects.filter(qdownvote__downvote_by_q=profileData.user).count()
    getVotedOn = Answer.objects.filter(a_vote_ups=profileData.user).count()
    getVotedOn_Down = Answer.objects.filter(a_vote_downs=profileData.user).count()

    countVotes = getVotedOnQ+getVotedOnQ_Down+getVotedOn+getVotedOn_Down



    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Critic", bade_position="BADGE").exists():
        critic_earned = True
    else:
        critic_earned = False



    if profileData.helpful_flags_counter:
        deputy_earned = True
    else:
        deputy_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Disciplined",bade_position="BADGE").exists():
        disclpned_earned = True
    else:
        disclpned_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Excavator",bade_position="BADGE").exists():
        excvter_earned = True
    else:
        excvter_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Investor", bade_position="BADGE").exists():
        investor_earned = True
    else:
        investor_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="GOLD", tag_name="Marshal", bade_position="BADGE").exists():
        marshal_earned = True
    else:
        marshal_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Necromancer",bade_position="BADGE").exists():
        necromancer_earned = True
    else:
        necromancer_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Peer Pressure",bade_position="BADGE").exists():
        pr_pressre_earned = True
    else:
        pr_pressre_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Promoter", bade_position="BADGE").exists():
        promoter_earned = True
    else:
        promoter_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Proofreader",bade_position="BADGE").exists():
        proffreader_earned = True
    else:
        proffreader_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Refiner",bade_position="BADGE").exists():
        refiner_earned = True
    else:
        refiner_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="Bronze", tag_name="Revival",bade_position="BADGE").exists():
        reviv_earned = True
    else:
        reviv_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Self-Learner",bade_position="BADGE").exists():
        slf_lrnr_earned = True
    else:
        slf_lrnr_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Strunk & White",bade_position="BADGE").exists():
        stnk_whte_earned = True
    else:
        stnk_whte_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Suffrage",bade_position="BADGE").exists():
        suffrage_earned = True
    else:
        suffrage_earned = False

    last_24_hours = timezone.now() - timedelta(hours=24)
    getQ_Votes_in_24_Hours = QUpvote.objects.filter(date__gt=last_24_hours).count()
    getQ_DownVotes_in_24_Hours = QDownvote.objects.filter(downvote_by_q=profileData.user, date__gt=last_24_hours).count()
    getA_Votes_in_24_Hours = Answer.objects.filter(a_vote_ups=profileData.user, date__gt=last_24_hours).count()
    getA_DownVotes_in_24_Hours = Answer.objects.filter(a_vote_downs=profileData.user, date__gt=last_24_hours).count()
    totalVotes = getQ_Votes_in_24_Hours + getQ_DownVotes_in_24_Hours + getA_Votes_in_24_Hours + getA_DownVotes_in_24_Hours

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Vox Populi",bade_position="BADGE").exists():
        vx_pop_earned = True
    else:
        vx_pop_earned = False  



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Teacher",bade_position="BADGE").exists():
        teacher_earned = True
    else:
        teacher_earned = False

    newestBadge = TagBadge.objects.filter(awarded_to_user=profileData.user).last()

    # ----------Next Badge---------- END----------



    context = {
        'newestBadge':newestBadge,
        'countVotes':countVotes,
        'teacher_earned':teacher_earned,
        'totalVotes':totalVotes,
        'vx_pop_earned':vx_pop_earned,
        'suffrage_earned':suffrage_earned,
        'stnk_whte_earned':stnk_whte_earned,
        'slf_lrnr_earned':slf_lrnr_earned,
        'reviv_earned':reviv_earned,
        'refiner_earned':refiner_earned,
        'proffreader_earned':proffreader_earned,
        'promoter_earned':promoter_earned,
        'necromancer_earned':necromancer_earned,
        'marshal_earned':marshal_earned,
        'investor_earned':investor_earned,
        'pr_pressre_earned':pr_pressre_earned,
        'excvter_earned':excvter_earned,
        'deputy_earned':deputy_earned,
        'disclpned_earned':disclpned_earned,
        'civc_duty':civc_duty,
        'critic_earned':critic_earned,
        'ctzn_ptrl_earned':ctzn_ptrl_earned,
        'benefactor_earned':benefactor_earned,
        'completed':completed,
        'countComments':countComments,
        'reputation_graph':reputation_graph,'totalBookmarks':totalBookmarks,'getAllTheViewsOfAllTheQuestion':getAllTheViewsOfAllTheQuestion,'getVotesCast_Final':getVotesCast_Final,'online_user_activity':online_user_activity,'tags':tags,'profileData':profileData}
    return render(request, 'profile/tagsActivity.html', context)


# IMPLEMENTED THE LOGIC
    # It will display all the badges and tag badges.
    # Recent Earned | Only TagBadge 
def badgesActivity(request, user_id, username):
    profileData = get_object_or_404(Profile, pk=user_id)
    badges = TagBadge.objects.filter(awarded_to_user=user_id)

    totalBadges = badges.count()

    totalBookmarks = BookmarkQuestion.objects.filter(bookmarked_by=user_id).count()



# Last seen
# To Show Last Seen in Profile. You'll see as "Last seen"
# Transfer this Variable into config.py
    USER_ONLINE_TIMEOUT = timedelta(seconds=5)
    min_time = timezone.now() - (USER_ONLINE_TIMEOUT)
    queryset = online_users.models.OnlineUserActivity.objects.filter(
        user_id=user_id).annotate(is_online=Case(
            When(last_activity__gte=min_time, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ))

    online_user_activity = get_object_or_404(queryset)



    # Total Votes Cast
    countVotedPosts_Q = QUpvote.objects.filter(upvote_by_q=user_id).count()
    countDownVotedPosts_Q = QDownvote.objects.filter(downvote_by_q=user_id).count()

    countVotedPosts_A = Answer.objects.filter(a_vote_ups=user_id).count()
    countDownVotedPosts_A = Answer.objects.filter(a_vote_downs=user_id).count()

    getVotesCast_Final = countVotedPosts_Q + countDownVotedPosts_Q + countVotedPosts_A + countDownVotedPosts_A


    # People Reached
    getAllTheViewsOfAllTheQuestion = Question.objects.filter(post_owner=profileData.user).annotate(total_views=Count('viewers')).aggregate(Sum('total_views'))



    reputation_graph = Reputation.objects.filter(awarded_to=user_id)[:15]


    # ----------Next Badge---------- START----------
    countComments = CommentQ.objects.filter(commented_by=profileData.user).count()



    if profileData.about_me != '':
        completed = True
    else:
        completed = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Benefactor").exists():
        benefactor_earned = True
    else:
        benefactor_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Citizen Patrol",bade_position="BADGE").exists():
        ctzn_ptrl_earned = True
    else:
        ctzn_ptrl_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Civic Duty",bade_position="BADGE").exists():
        civc_duty = True
    else:
        civc_duty = False
    getVotedOnQ = Question.objects.filter(qupvote__upvote_by_q=profileData.user).count()
    getVotedOnQ_Down = Question.objects.filter(qdownvote__downvote_by_q=profileData.user).count()
    getVotedOn = Answer.objects.filter(a_vote_ups=profileData.user).count()
    getVotedOn_Down = Answer.objects.filter(a_vote_downs=profileData.user).count()

    countVotes = getVotedOnQ+getVotedOnQ_Down+getVotedOn+getVotedOn_Down



    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Critic", bade_position="BADGE").exists():
        critic_earned = True
    else:
        critic_earned = False



    if profileData.helpful_flags_counter:
        deputy_earned = True
    else:
        deputy_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Disciplined",bade_position="BADGE").exists():
        disclpned_earned = True
    else:
        disclpned_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Excavator",bade_position="BADGE").exists():
        excvter_earned = True
    else:
        excvter_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Investor", bade_position="BADGE").exists():
        investor_earned = True
    else:
        investor_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="GOLD", tag_name="Marshal", bade_position="BADGE").exists():
        marshal_earned = True
    else:
        marshal_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Necromancer",bade_position="BADGE").exists():
        necromancer_earned = True
    else:
        necromancer_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Peer Pressure",bade_position="BADGE").exists():
        pr_pressre_earned = True
    else:
        pr_pressre_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Promoter", bade_position="BADGE").exists():
        promoter_earned = True
    else:
        promoter_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Proofreader",bade_position="BADGE").exists():
        proffreader_earned = True
    else:
        proffreader_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Refiner",bade_position="BADGE").exists():
        refiner_earned = True
    else:
        refiner_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="Bronze", tag_name="Revival",bade_position="BADGE").exists():
        reviv_earned = True
    else:
        reviv_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Self-Learner",bade_position="BADGE").exists():
        slf_lrnr_earned = True
    else:
        slf_lrnr_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Strunk & White",bade_position="BADGE").exists():
        stnk_whte_earned = True
    else:
        stnk_whte_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Suffrage",bade_position="BADGE").exists():
        suffrage_earned = True
    else:
        suffrage_earned = False

    last_24_hours = timezone.now() - timedelta(hours=24)
    getQ_Votes_in_24_Hours = QUpvote.objects.filter(date__gt=last_24_hours).count()
    getQ_DownVotes_in_24_Hours = QDownvote.objects.filter(downvote_by_q=profileData.user, date__gt=last_24_hours).count()
    getA_Votes_in_24_Hours = Answer.objects.filter(a_vote_ups=profileData.user, date__gt=last_24_hours).count()
    getA_DownVotes_in_24_Hours = Answer.objects.filter(a_vote_downs=profileData.user, date__gt=last_24_hours).count()
    totalVotes = getQ_Votes_in_24_Hours + getQ_DownVotes_in_24_Hours + getA_Votes_in_24_Hours + getA_DownVotes_in_24_Hours

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Vox Populi",bade_position="BADGE").exists():
        vx_pop_earned = True
    else:
        vx_pop_earned = False  



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Teacher",bade_position="BADGE").exists():
        teacher_earned = True
    else:
        teacher_earned = False

    newestBadge = TagBadge.objects.filter(awarded_to_user=profileData.user).last()

    # ----------Next Badge---------- END----------


    context = {
        'newestBadge':newestBadge,
        'countVotes':countVotes,
        'teacher_earned':teacher_earned,
        'totalVotes':totalVotes,
        'vx_pop_earned':vx_pop_earned,
        'suffrage_earned':suffrage_earned,
        'stnk_whte_earned':stnk_whte_earned,
        'slf_lrnr_earned':slf_lrnr_earned,
        'reviv_earned':reviv_earned,
        'refiner_earned':refiner_earned,
        'proffreader_earned':proffreader_earned,
        'promoter_earned':promoter_earned,
        'necromancer_earned':necromancer_earned,
        'marshal_earned':marshal_earned,
        'investor_earned':investor_earned,
        'pr_pressre_earned':pr_pressre_earned,
        'excvter_earned':excvter_earned,
        'deputy_earned':deputy_earned,
        'disclpned_earned':disclpned_earned,
        'civc_duty':civc_duty,
        'critic_earned':critic_earned,
        'ctzn_ptrl_earned':ctzn_ptrl_earned,
        'benefactor_earned':benefactor_earned,
        'completed':completed,
        'countComments':countComments,'reputation_graph':reputation_graph,'totalBadges':totalBadges,'totalBookmarks':totalBookmarks,'online_user_activity':online_user_activity,'getAllTheViewsOfAllTheQuestion':getAllTheViewsOfAllTheQuestion,'getVotesCast_Final':getVotesCast_Final,'badges':badges,'profileData':profileData}
    return render(request, 'profile/badgesActivity.html', context)


"""
[COMPLETED]-[IMPLEMENTED] = Will do this later, Because i have to make another Model because i made
a M2M Field in which i can't get most recents records (bookmakrds by user_id)
"""
# IMPLEMENTED THE LOGIC
    # It will show all the questions bookmarked by user_id.
    # Most Votes | Last Edited | Most Recent | Most Views
# def bookmarksActivity(request, user_id, username):
#     profileData = get_object_or_404(Profile, pk=user_id)
#     bookmarks = BookmarkQuestion.objects.filter(bookmarked_by=user_id)

#     context = {'bookmarks':bookmarks,'profileData':profileData}
#     return render(request, 'profile/bookmarksActivity.html', context)



def bountiesActivity(request, user_id, username):
    profileData = get_object_or_404(Profile, pk=user_id)
    # It will show all the bounties that are declared by user_id

    countBounties = Bounty.objects.filter(by_user=profileData.user).count()

    LAST_SEVEN_DAYS = timezone.now() - timedelta(days=7)

    # Earned | Active | Offered by user_id
    active_bounties = Bounty.objects.filter(by_user=user_id, date__gt=LAST_SEVEN_DAYS)

    earned_bounties = Bounty.objects.filter(bounty_awarded_to=user_id)


    USER_ONLINE_TIMEOUT = timedelta(seconds=5)
    min_time = timezone.now() - (USER_ONLINE_TIMEOUT)
    queryset = online_users.models.OnlineUserActivity.objects.filter(
        user_id=user_id).annotate(is_online=Case(
            When(last_activity__gte=min_time, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ))

    online_user_activity = get_object_or_404(queryset)


    # Total Votes Cast
    countVotedPosts_Q = QUpvote.objects.filter(upvote_by_q=user_id).count()
    countDownVotedPosts_Q = QDownvote.objects.filter(downvote_by_q=user_id).count()

    countVotedPosts_A = Answer.objects.filter(a_vote_ups=user_id).count()
    countDownVotedPosts_A = Answer.objects.filter(a_vote_downs=user_id).count()

    getVotesCast_Final = countVotedPosts_Q + countDownVotedPosts_Q + countVotedPosts_A + countDownVotedPosts_A


    # People Reached
    getAllTheViewsOfAllTheQuestion = Question.objects.filter(post_owner=profileData.user).annotate(total_views=Count('viewers')).aggregate(Sum('total_views'))


    reputation_graph = Reputation.objects.filter(awarded_to=user_id)[:15]


    # ----------Next Badge---------- START----------
    countComments = CommentQ.objects.filter(commented_by=profileData.user).count()



    if profileData.about_me != '':
        completed = True
    else:
        completed = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Benefactor").exists():
        benefactor_earned = True
    else:
        benefactor_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Citizen Patrol",bade_position="BADGE").exists():
        ctzn_ptrl_earned = True
    else:
        ctzn_ptrl_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Civic Duty",bade_position="BADGE").exists():
        civc_duty = True
    else:
        civc_duty = False
    getVotedOnQ = Question.objects.filter(qupvote__upvote_by_q=profileData.user).count()
    getVotedOnQ_Down = Question.objects.filter(qdownvote__downvote_by_q=profileData.user).count()
    getVotedOn = Answer.objects.filter(a_vote_ups=profileData.user).count()
    getVotedOn_Down = Answer.objects.filter(a_vote_downs=profileData.user).count()

    countVotes = getVotedOnQ+getVotedOnQ_Down+getVotedOn+getVotedOn_Down



    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Critic", bade_position="BADGE").exists():
        critic_earned = True
    else:
        critic_earned = False



    if profileData.helpful_flags_counter:
        deputy_earned = True
    else:
        deputy_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Disciplined",bade_position="BADGE").exists():
        disclpned_earned = True
    else:
        disclpned_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Excavator",bade_position="BADGE").exists():
        excvter_earned = True
    else:
        excvter_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Investor", bade_position="BADGE").exists():
        investor_earned = True
    else:
        investor_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="GOLD", tag_name="Marshal", bade_position="BADGE").exists():
        marshal_earned = True
    else:
        marshal_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Necromancer",bade_position="BADGE").exists():
        necromancer_earned = True
    else:
        necromancer_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Peer Pressure",bade_position="BADGE").exists():
        pr_pressre_earned = True
    else:
        pr_pressre_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Promoter", bade_position="BADGE").exists():
        promoter_earned = True
    else:
        promoter_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Proofreader",bade_position="BADGE").exists():
        proffreader_earned = True
    else:
        proffreader_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Refiner",bade_position="BADGE").exists():
        refiner_earned = True
    else:
        refiner_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="Bronze", tag_name="Revival",bade_position="BADGE").exists():
        reviv_earned = True
    else:
        reviv_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Self-Learner",bade_position="BADGE").exists():
        slf_lrnr_earned = True
    else:
        slf_lrnr_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Strunk & White",bade_position="BADGE").exists():
        stnk_whte_earned = True
    else:
        stnk_whte_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Suffrage",bade_position="BADGE").exists():
        suffrage_earned = True
    else:
        suffrage_earned = False

    last_24_hours = timezone.now() - timedelta(hours=24)
    getQ_Votes_in_24_Hours = QUpvote.objects.filter(date__gt=last_24_hours).count()
    getQ_DownVotes_in_24_Hours = QDownvote.objects.filter(downvote_by_q=profileData.user, date__gt=last_24_hours).count()
    getA_Votes_in_24_Hours = Answer.objects.filter(a_vote_ups=profileData.user, date__gt=last_24_hours).count()
    getA_DownVotes_in_24_Hours = Answer.objects.filter(a_vote_downs=profileData.user, date__gt=last_24_hours).count()
    totalVotes = getQ_Votes_in_24_Hours + getQ_DownVotes_in_24_Hours + getA_Votes_in_24_Hours + getA_DownVotes_in_24_Hours

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Vox Populi",bade_position="BADGE").exists():
        vx_pop_earned = True
    else:
        vx_pop_earned = False  



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Teacher",bade_position="BADGE").exists():
        teacher_earned = True
    else:
        teacher_earned = False

    newestBadge = TagBadge.objects.filter(awarded_to_user=profileData.user).last()

    # ----------Next Badge---------- END----------



    context = {
        'newestBadge':newestBadge,
        'countVotes':countVotes,
        'teacher_earned':teacher_earned,
        'totalVotes':totalVotes,
        'vx_pop_earned':vx_pop_earned,
        'suffrage_earned':suffrage_earned,
        'stnk_whte_earned':stnk_whte_earned,
        'slf_lrnr_earned':slf_lrnr_earned,
        'reviv_earned':reviv_earned,
        'refiner_earned':refiner_earned,
        'proffreader_earned':proffreader_earned,
        'promoter_earned':promoter_earned,
        'necromancer_earned':necromancer_earned,
        'marshal_earned':marshal_earned,
        'investor_earned':investor_earned,
        'pr_pressre_earned':pr_pressre_earned,
        'excvter_earned':excvter_earned,
        'deputy_earned':deputy_earned,
        'disclpned_earned':disclpned_earned,
        'civc_duty':civc_duty,
        'critic_earned':critic_earned,
        'ctzn_ptrl_earned':ctzn_ptrl_earned,
        'benefactor_earned':benefactor_earned,
        'completed':completed,
        'countComments':countComments,'countBounties':countBounties,'online_user_activity':online_user_activity,'getAllTheViewsOfAllTheQuestion':getAllTheViewsOfAllTheQuestion,'getVotesCast_Final':getVotesCast_Final,'earned_bounties':earned_bounties,'reputation_graph':reputation_graph,'active_bounties':active_bounties,'profileData':profileData}
    return render(request, 'profile/bountiesActivity.html', context)



def reputationActivity(request, user_id, username):
    profileData = get_object_or_404(Profile, pk=user_id)
    # It will show all the earned and decreased reputation order_by('date')
    # Date | Graph

    USER_ONLINE_TIMEOUT = timedelta(seconds=5)
    min_time = timezone.now() - (USER_ONLINE_TIMEOUT)
    queryset = online_users.models.OnlineUserActivity.objects.filter(
        user_id=user_id).annotate(is_online=Case(
            When(last_activity__gte=min_time, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ))

    online_user_activity = get_object_or_404(queryset)


    # Total Votes Cast
    countVotedPosts_Q = QUpvote.objects.filter(upvote_by_q=user_id).count()
    countDownVotedPosts_Q = QDownvote.objects.filter(downvote_by_q=user_id).count()

    countVotedPosts_A = Answer.objects.filter(a_vote_ups=user_id).count()
    countDownVotedPosts_A = Answer.objects.filter(a_vote_downs=user_id).count()

    getVotesCast_Final = countVotedPosts_Q + countDownVotedPosts_Q + countVotedPosts_A + countDownVotedPosts_A


    # People Reached
    getAllTheViewsOfAllTheQuestion = Question.objects.filter(post_owner=profileData.user).annotate(total_views=Count('viewers')).aggregate(Sum('total_views'))



    reputation_graph = Reputation.objects.filter(awarded_to=user_id)[:15]

    get_rep_data = Reputation.objects.filter(awarded_to=user_id).order_by('-date_earned')



    # ----------Next Badge---------- START----------
    countComments = CommentQ.objects.filter(commented_by=profileData.user).count()



    if profileData.about_me != '':
        completed = True
    else:
        completed = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Benefactor").exists():
        benefactor_earned = True
    else:
        benefactor_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Citizen Patrol",bade_position="BADGE").exists():
        ctzn_ptrl_earned = True
    else:
        ctzn_ptrl_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Civic Duty",bade_position="BADGE").exists():
        civc_duty = True
    else:
        civc_duty = False
    getVotedOnQ = Question.objects.filter(qupvote__upvote_by_q=profileData.user).count()
    getVotedOnQ_Down = Question.objects.filter(qdownvote__downvote_by_q=profileData.user).count()
    getVotedOn = Answer.objects.filter(a_vote_ups=profileData.user).count()
    getVotedOn_Down = Answer.objects.filter(a_vote_downs=profileData.user).count()

    countVotes = getVotedOnQ+getVotedOnQ_Down+getVotedOn+getVotedOn_Down



    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Critic", bade_position="BADGE").exists():
        critic_earned = True
    else:
        critic_earned = False



    if profileData.helpful_flags_counter:
        deputy_earned = True
    else:
        deputy_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Disciplined",bade_position="BADGE").exists():
        disclpned_earned = True
    else:
        disclpned_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Excavator",bade_position="BADGE").exists():
        excvter_earned = True
    else:
        excvter_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Investor", bade_position="BADGE").exists():
        investor_earned = True
    else:
        investor_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="GOLD", tag_name="Marshal", bade_position="BADGE").exists():
        marshal_earned = True
    else:
        marshal_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Necromancer",bade_position="BADGE").exists():
        necromancer_earned = True
    else:
        necromancer_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Peer Pressure",bade_position="BADGE").exists():
        pr_pressre_earned = True
    else:
        pr_pressre_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Promoter", bade_position="BADGE").exists():
        promoter_earned = True
    else:
        promoter_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Proofreader",bade_position="BADGE").exists():
        proffreader_earned = True
    else:
        proffreader_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Refiner",bade_position="BADGE").exists():
        refiner_earned = True
    else:
        refiner_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="Bronze", tag_name="Revival",bade_position="BADGE").exists():
        reviv_earned = True
    else:
        reviv_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Self-Learner",bade_position="BADGE").exists():
        slf_lrnr_earned = True
    else:
        slf_lrnr_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Strunk & White",bade_position="BADGE").exists():
        stnk_whte_earned = True
    else:
        stnk_whte_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Suffrage",bade_position="BADGE").exists():
        suffrage_earned = True
    else:
        suffrage_earned = False

    last_24_hours = timezone.now() - timedelta(hours=24)
    getQ_Votes_in_24_Hours = QUpvote.objects.filter(date__gt=last_24_hours).count()
    getQ_DownVotes_in_24_Hours = QDownvote.objects.filter(downvote_by_q=profileData.user, date__gt=last_24_hours).count()
    getA_Votes_in_24_Hours = Answer.objects.filter(a_vote_ups=profileData.user, date__gt=last_24_hours).count()
    getA_DownVotes_in_24_Hours = Answer.objects.filter(a_vote_downs=profileData.user, date__gt=last_24_hours).count()
    totalVotes = getQ_Votes_in_24_Hours + getQ_DownVotes_in_24_Hours + getA_Votes_in_24_Hours + getA_DownVotes_in_24_Hours

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Vox Populi",bade_position="BADGE").exists():
        vx_pop_earned = True
    else:
        vx_pop_earned = False  



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Teacher",bade_position="BADGE").exists():
        teacher_earned = True
    else:
        teacher_earned = False

    newestBadge = TagBadge.objects.filter(awarded_to_user=profileData.user).last()

    # ----------Next Badge---------- END----------




    context = {
        'newestBadge':newestBadge,
        'countVotes':countVotes,
        'teacher_earned':teacher_earned,
        'totalVotes':totalVotes,
        'vx_pop_earned':vx_pop_earned,
        'suffrage_earned':suffrage_earned,
        'stnk_whte_earned':stnk_whte_earned,
        'slf_lrnr_earned':slf_lrnr_earned,
        'reviv_earned':reviv_earned,
        'refiner_earned':refiner_earned,
        'proffreader_earned':proffreader_earned,
        'promoter_earned':promoter_earned,
        'necromancer_earned':necromancer_earned,
        'marshal_earned':marshal_earned,
        'investor_earned':investor_earned,
        'pr_pressre_earned':pr_pressre_earned,
        'excvter_earned':excvter_earned,
        'deputy_earned':deputy_earned,
        'disclpned_earned':disclpned_earned,
        'civc_duty':civc_duty,
        'critic_earned':critic_earned,
        'ctzn_ptrl_earned':ctzn_ptrl_earned,
        'benefactor_earned':benefactor_earned,
        'completed':completed,
        'countComments':countComments,'get_rep_data':get_rep_data,'online_user_activity':online_user_activity,'getVotesCast_Final':getVotesCast_Final,'getAllTheViewsOfAllTheQuestion':getAllTheViewsOfAllTheQuestion,'reputation_graph':reputation_graph,'profileData':profileData,}
    return render(request, 'profile/reputationActivity.html', context)

def loadQuestion_div(request, question_id):
    getQuestion = get_object_or_404(Question, id=question_id)

    serialized_results = []

    serialized_results.append({
        'id': getQuestion.id,
        'title': getQuestion.title,
        'date': getQuestion.date
        })

    return JsonResponse({'results': serialized_results})


# def getUserName_From_Comment(request):

#     getUserIdByUsername = User.objects.get(username=getUserName)

#     return JsonResponse




def loadAnswer_div(request, answer_id):
    getAnswer = get_object_or_404(Answer, id=answer_id)

    answer_serialized_results = []

    answer_serialized_results.append({
        'id': getAnswer.id,
        'body': getAnswer.body,
        'date': getAnswer.date
        })

    return JsonResponse({'answer_results': answer_serialized_results})


def flag_summary(request, user_id, username):
    profileData = get_object_or_404(Profile, pk=user_id)

    voted_flags = list(FlagPost.objects.filter(flagged_by=user_id))
    voted_comment_flags = list(FlagComment.objects.filter(comment_flagged_by=user_id))

    def ordering(obj):
        try:
            return obj.flagged_at
        except AttributeError:
            return obj.date

    results = sorted(chain(voted_flags,voted_comment_flags), key=ordering, reverse=True)

    context = {'profileData':profileData,'results':results,}
    return render(request, 'profile/flag_summary.html', context)



# IMPLEMENTED THE LOGIC
    # It will show all the activities, Almost already built
    # All | Accepted Answers | Asked Answers | Badges Earned | Comments
    # Reviews Done |
    """
    Didn't implement every filter because i had to make every query differently, which will be slow.
    """
# @cache_page(60 * 15)
def allActionsActivity(request, user_id, username):
    profileData = get_object_or_404(Profile, pk=user_id)
    query_1 = list(Question.objects.filter(post_owner=user_id).order_by('date'))
    query_2 = list(Answer.objects.filter(answer_owner=user_id).order_by('date'))
    query_3 = list(CloseQuestionVotes.objects.filter(user=user_id).order_by('date'))
    query_4 = list(Bounty.objects.filter(by_user=user_id).select_related('question_bounty').order_by('date'))
    query_5_comment = list(CommentQ.objects.filter(commented_by=user_id).order_by('date'))
    query_6_tag = list(TagBadge.objects.filter(awarded_to_user=user_id).order_by('date'))
    query_7_reviewing = list(ReviewCloseVotes.objects.filter(reviewed_by=user_id).order_by('date'))

    def order(obj):
        try:
            return obj.date
        except AttributeError:
            return obj.date


    results = sorted(chain(query_1, query_2, query_3, query_4, query_5_comment, query_6_tag),key=order , reverse=True)
    page = request.GET.get('page', 1)

    paginator = Paginator(results, 10)
    try:
        paginatedResults = paginator.page(page)
    except PageNotAnInteger:
        paginatedResults = paginator.page(1)
    except EmptyPage:
        paginatedResults = paginator.page(paginator.num_pages)

    getAnsweredAnswers = Answer.objects.filter(answer_owner=user_id).order_by('date')

    countActions = len(results)

# Last seen
# To Show Last Seen in Profile. You'll see as "Last seen"
# Transfer this Variable into config.py
    USER_ONLINE_TIMEOUT = timedelta(seconds=5)
    min_time = timezone.now() - (USER_ONLINE_TIMEOUT)
    queryset = online_users.models.OnlineUserActivity.objects.filter(
        user_id=user_id).annotate(is_online=Case(
            When(last_activity__gte=min_time, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ))

    online_user_activity = get_object_or_404(queryset)



    # Total Votes Cast
    countVotedPosts_Q = QUpvote.objects.filter(upvote_by_q=user_id).count()
    countDownVotedPosts_Q = QDownvote.objects.filter(downvote_by_q=user_id).count()

    countVotedPosts_A = Answer.objects.filter(a_vote_ups=user_id).count()
    countDownVotedPosts_A = Answer.objects.filter(a_vote_downs=user_id).count()

    getVotesCast_Final = countVotedPosts_Q + countDownVotedPosts_Q + countVotedPosts_A + countDownVotedPosts_A


    # People Reached
    getAllTheViewsOfAllTheQuestion = Question.objects.filter(post_owner=profileData.user).annotate(total_views=Count('viewers')).aggregate(Sum('total_views'))

    reputation_graph = Reputation.objects.filter(awarded_to=user_id)[:15]


    # ----------Next Badge---------- START----------
    countComments = CommentQ.objects.filter(commented_by=profileData.user).count()



    if profileData.about_me != '':
        completed = True
    else:
        completed = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Benefactor").exists():
        benefactor_earned = True
    else:
        benefactor_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Citizen Patrol",bade_position="BADGE").exists():
        ctzn_ptrl_earned = True
    else:
        ctzn_ptrl_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Civic Duty",bade_position="BADGE").exists():
        civc_duty = True
    else:
        civc_duty = False
    getVotedOnQ = Question.objects.filter(qupvote__upvote_by_q=profileData.user).count()
    getVotedOnQ_Down = Question.objects.filter(qdownvote__downvote_by_q=profileData.user).count()
    getVotedOn = Answer.objects.filter(a_vote_ups=profileData.user).count()
    getVotedOn_Down = Answer.objects.filter(a_vote_downs=profileData.user).count()

    countVotes = getVotedOnQ+getVotedOnQ_Down+getVotedOn+getVotedOn_Down



    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Critic", bade_position="BADGE").exists():
        critic_earned = True
    else:
        critic_earned = False



    if profileData.helpful_flags_counter:
        deputy_earned = True
    else:
        deputy_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Disciplined",bade_position="BADGE").exists():
        disclpned_earned = True
    else:
        disclpned_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Excavator",bade_position="BADGE").exists():
        excvter_earned = True
    else:
        excvter_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Investor", bade_position="BADGE").exists():
        investor_earned = True
    else:
        investor_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="GOLD", tag_name="Marshal", bade_position="BADGE").exists():
        marshal_earned = True
    else:
        marshal_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Necromancer",bade_position="BADGE").exists():
        necromancer_earned = True
    else:
        necromancer_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Peer Pressure",bade_position="BADGE").exists():
        pr_pressre_earned = True
    else:
        pr_pressre_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Promoter", bade_position="BADGE").exists():
        promoter_earned = True
    else:
        promoter_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Proofreader",bade_position="BADGE").exists():
        proffreader_earned = True
    else:
        proffreader_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Refiner",bade_position="BADGE").exists():
        refiner_earned = True
    else:
        refiner_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="Bronze", tag_name="Revival",bade_position="BADGE").exists():
        reviv_earned = True
    else:
        reviv_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Self-Learner",bade_position="BADGE").exists():
        slf_lrnr_earned = True
    else:
        slf_lrnr_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Strunk & White",bade_position="BADGE").exists():
        stnk_whte_earned = True
    else:
        stnk_whte_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Suffrage",bade_position="BADGE").exists():
        suffrage_earned = True
    else:
        suffrage_earned = False

    last_24_hours = timezone.now() - timedelta(hours=24)
    getQ_Votes_in_24_Hours = QUpvote.objects.filter(date__gt=last_24_hours).count()
    getQ_DownVotes_in_24_Hours = QDownvote.objects.filter(downvote_by_q=profileData.user, date__gt=last_24_hours).count()
    getA_Votes_in_24_Hours = Answer.objects.filter(a_vote_ups=profileData.user, date__gt=last_24_hours).count()
    getA_DownVotes_in_24_Hours = Answer.objects.filter(a_vote_downs=profileData.user, date__gt=last_24_hours).count()
    totalVotes = getQ_Votes_in_24_Hours + getQ_DownVotes_in_24_Hours + getA_Votes_in_24_Hours + getA_DownVotes_in_24_Hours

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Vox Populi",bade_position="BADGE").exists():
        vx_pop_earned = True
    else:
        vx_pop_earned = False  



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Teacher",bade_position="BADGE").exists():
        teacher_earned = True
    else:
        teacher_earned = False

    newestBadge = TagBadge.objects.filter(awarded_to_user=profileData.user).last()

    # ----------Next Badge---------- END----------



    context = {
        'newestBadge':newestBadge,
        'countVotes':countVotes,
        'teacher_earned':teacher_earned,
        'totalVotes':totalVotes,
        'vx_pop_earned':vx_pop_earned,
        'suffrage_earned':suffrage_earned,
        'stnk_whte_earned':stnk_whte_earned,
        'slf_lrnr_earned':slf_lrnr_earned,
        'reviv_earned':reviv_earned,
        'refiner_earned':refiner_earned,
        'proffreader_earned':proffreader_earned,
        'promoter_earned':promoter_earned,
        'necromancer_earned':necromancer_earned,
        'marshal_earned':marshal_earned,
        'investor_earned':investor_earned,
        'pr_pressre_earned':pr_pressre_earned,
        'excvter_earned':excvter_earned,
        'deputy_earned':deputy_earned,
        'disclpned_earned':disclpned_earned,
        'civc_duty':civc_duty,
        'critic_earned':critic_earned,
        'ctzn_ptrl_earned':ctzn_ptrl_earned,
        'benefactor_earned':benefactor_earned,
        'completed':completed,
        'countComments':countComments,'countActions':countActions,'reputation_graph':reputation_graph,'getAllTheViewsOfAllTheQuestion':getAllTheViewsOfAllTheQuestion,'getVotesCast_Final':getVotesCast_Final,'online_user_activity':online_user_activity,'paginatedResults':paginatedResults,'results':results,'profileData':profileData}
    return render(request, 'profile/allActionsActivity.html', context)

def listTOString(word):
    emptyString = ""
    return (emptyString.join(word))

# def ResponsesActivity(request, user_id, username):
#     query_1 = list(CommentQ.objects.filter(question_comment__post_owner=user_id).order_by('date'))
#     query_2 = list(Answer.objects.filter(questionans__post_owner=user_id).order_by('date'))

#     def order(obj):
#         try:
#             return obj.date
#         except AttributeError:
#             return obj.date

#     allPosts = sorted(chain(query_1, query_2), key=order, reverse=True)

#     getAllTheComments_profileData_mentioned_on = CommentQ.objects.all()



#     getUser_Username = User.objects.get(id=user_id)

#     # Get all comments in which user_id_username is mentioned.


#     getNow =



#     COMMENTS = []

#     for comment in getAllTheComments_profileData_mentioned_on:
#         getCommentBody = comment.comment
        
#         user = getCommentBody[getCommentBody.find("@")+1:].split()[0]
#         splitIt = re.split(",(?=(?:[^']*\'[^']*\')*[^']*$)",user)
#         splitFromList = listTOString(splitIt)

#         if "@" in getCommentBody:
#             getUser = User.objects.get(id=user_id)
#             if splitFromList == getUser.username:
#                 try: 
#                     getUser = User.objects.get(id=user_id)
#                     getCommentsNow = CommentQ.objects.filter(commented_by=getUser)
#                     print(getCommentsNow)
#                     for com in getCommentsNow:
#                         COMMENTS.append(com)
#                     # print(getCommentsNow)

#                 except User.DoesNotExist:
#                     print("Something Went Wrong")

#     # for printLoop in COMMENTS:
#     # print(COMMENTS)


#     context = {'COMMENTS':COMMENTS,'allPosts':allPosts}
#     return render(request, 'profile/ResponsesActivity.html', context)

def checkNotifications(request):
    checkIf = Notification.objects.filter(is_read=False)

    return HttpResponse(status=202)

def Votes_castActivity(request, user_id, username):
    profileData = get_object_or_404(Profile, pk=user_id)
    query_1 = list(QUpvote.objects.filter(upvote_by_q=profileData.user))
    query_2 = list(QDownvote.objects.filter(downvote_by_q=profileData.user))
    query_3 = list(CloseQuestionVotes.objects.filter(user=profileData.user))
    query_4 = list(ReOpenQuestionVotes.objects.filter(user=profileData.user))
    query_5 = list(Answer.objects.filter(a_vote_ups=profileData.user))

    def order(obj):
        try:
            return obj.date
        except AttributeError:
            return obj.date_opening


    allPosts = sorted(chain(query_1, query_2, query_3, query_4,query_5), key=order, reverse=True)
    countallVotes = len(allPosts)
# Last seen
# To Show Last Seen in Profile. You'll see as "Last seen"
# Transfer this Variable into config.py
    USER_ONLINE_TIMEOUT = timedelta(seconds=5)
    min_time = timezone.now() - (USER_ONLINE_TIMEOUT)
    queryset = online_users.models.OnlineUserActivity.objects.filter(
        user_id=user_id).annotate(is_online=Case(
            When(last_activity__gte=min_time, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ))

    online_user_activity = get_object_or_404(queryset)



    # Total Votes Cast
    countVotedPosts_Q = QUpvote.objects.filter(upvote_by_q=user_id).count()
    countDownVotedPosts_Q = QDownvote.objects.filter(downvote_by_q=user_id).count()

    countVotedPosts_A = Answer.objects.filter(a_vote_ups=user_id).count()
    countDownVotedPosts_A = Answer.objects.filter(a_vote_downs=user_id).count()

    getVotesCast_Final = countVotedPosts_Q + countDownVotedPosts_Q + countVotedPosts_A + countDownVotedPosts_A


    # People Reached
    getAllTheViewsOfAllTheQuestion = Question.objects.filter(post_owner=profileData.user).annotate(total_views=Count('viewers')).aggregate(Sum('total_views'))



    # ----------Next Badge---------- START----------
    countComments = CommentQ.objects.filter(commented_by=profileData.user).count()



    if profileData.about_me != '':
        completed = True
    else:
        completed = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Benefactor").exists():
        benefactor_earned = True
    else:
        benefactor_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Citizen Patrol",bade_position="BADGE").exists():
        ctzn_ptrl_earned = True
    else:
        ctzn_ptrl_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Civic Duty",bade_position="BADGE").exists():
        civc_duty = True
    else:
        civc_duty = False
    getVotedOnQ = Question.objects.filter(qupvote__upvote_by_q=profileData.user).count()
    getVotedOnQ_Down = Question.objects.filter(qdownvote__downvote_by_q=profileData.user).count()
    getVotedOn = Answer.objects.filter(a_vote_ups=profileData.user).count()
    getVotedOn_Down = Answer.objects.filter(a_vote_downs=profileData.user).count()

    countVotes = getVotedOnQ+getVotedOnQ_Down+getVotedOn+getVotedOn_Down



    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Critic", bade_position="BADGE").exists():
        critic_earned = True
    else:
        critic_earned = False



    if profileData.helpful_flags_counter:
        deputy_earned = True
    else:
        deputy_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Disciplined",bade_position="BADGE").exists():
        disclpned_earned = True
    else:
        disclpned_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Excavator",bade_position="BADGE").exists():
        excvter_earned = True
    else:
        excvter_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Investor", bade_position="BADGE").exists():
        investor_earned = True
    else:
        investor_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="GOLD", tag_name="Marshal", bade_position="BADGE").exists():
        marshal_earned = True
    else:
        marshal_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Necromancer",bade_position="BADGE").exists():
        necromancer_earned = True
    else:
        necromancer_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Peer Pressure",bade_position="BADGE").exists():
        pr_pressre_earned = True
    else:
        pr_pressre_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Promoter", bade_position="BADGE").exists():
        promoter_earned = True
    else:
        promoter_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Proofreader",bade_position="BADGE").exists():
        proffreader_earned = True
    else:
        proffreader_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Refiner",bade_position="BADGE").exists():
        refiner_earned = True
    else:
        refiner_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="Bronze", tag_name="Revival",bade_position="BADGE").exists():
        reviv_earned = True
    else:
        reviv_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Self-Learner",bade_position="BADGE").exists():
        slf_lrnr_earned = True
    else:
        slf_lrnr_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Strunk & White",bade_position="BADGE").exists():
        stnk_whte_earned = True
    else:
        stnk_whte_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Suffrage",bade_position="BADGE").exists():
        suffrage_earned = True
    else:
        suffrage_earned = False

    last_24_hours = timezone.now() - timedelta(hours=24)
    getQ_Votes_in_24_Hours = QUpvote.objects.filter(date__gt=last_24_hours).count()
    getQ_DownVotes_in_24_Hours = QDownvote.objects.filter(downvote_by_q=profileData.user, date__gt=last_24_hours).count()
    getA_Votes_in_24_Hours = Answer.objects.filter(a_vote_ups=profileData.user, date__gt=last_24_hours).count()
    getA_DownVotes_in_24_Hours = Answer.objects.filter(a_vote_downs=profileData.user, date__gt=last_24_hours).count()
    totalVotes = getQ_Votes_in_24_Hours + getQ_DownVotes_in_24_Hours + getA_Votes_in_24_Hours + getA_DownVotes_in_24_Hours

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Vox Populi",bade_position="BADGE").exists():
        vx_pop_earned = True
    else:
        vx_pop_earned = False  



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Teacher",bade_position="BADGE").exists():
        teacher_earned = True
    else:
        teacher_earned = False

    newestBadge = TagBadge.objects.filter(awarded_to_user=profileData.user).last()

    # ----------Next Badge---------- END----------

    reputation_graph = Reputation.objects.filter(awarded_to=user_id)[:15]




    context = {
        'newestBadge':newestBadge,
        'reputation_graph':reputation_graph,
        'countVotes':countVotes,
        'teacher_earned':teacher_earned,
        'totalVotes':totalVotes,
        'vx_pop_earned':vx_pop_earned,
        'suffrage_earned':suffrage_earned,
        'stnk_whte_earned':stnk_whte_earned,
        'slf_lrnr_earned':slf_lrnr_earned,
        'reviv_earned':reviv_earned,
        'refiner_earned':refiner_earned,
        'proffreader_earned':proffreader_earned,
        'promoter_earned':promoter_earned,
        'necromancer_earned':necromancer_earned,
        'marshal_earned':marshal_earned,
        'investor_earned':investor_earned,
        'pr_pressre_earned':pr_pressre_earned,
        'excvter_earned':excvter_earned,
        'deputy_earned':deputy_earned,
        'disclpned_earned':disclpned_earned,
        'civc_duty':civc_duty,
        'critic_earned':critic_earned,
        'ctzn_ptrl_earned':ctzn_ptrl_earned,
        'benefactor_earned':benefactor_earned,
        'completed':completed,
        'countComments':countComments,'countallVotes':countallVotes,'getAllTheViewsOfAllTheQuestion':getAllTheViewsOfAllTheQuestion,'getVotesCast_Final':getVotesCast_Final,'online_user_activity':online_user_activity,'allPosts':allPosts,'profileData':profileData}
    return render(request, 'profile/Votes_castActivity.html', context)

# Users with 20k rep
    # User can vote for deletion (if Q is -3 or lower) if the close is older than 48 hours
    # User can vote for deletion to As (if Q is -1 or lower)

# @login_required
def home(request):

    context = {}
    return render(request, 'profile/home.html', context)

def bountied_home(request):
    questions = Question.objects.filter(
                    is_bountied=True)[:50]

    context = {'questions':questions,}
    return render(request, 'home/bountied_home.html', context)

def hot_q_day_home(request):
    last_3_days = timezone.now() - timedelta(days=3)
    questions = Question.objects.filter(
                    viewers__gte=2
                    ).annotate(countComment=Count('commentq')
                    ).filter(qupvote__date__gt=last_3_days
                    ).order_by('qupvote'
                    ).order_by('-countComment'
                    ).distinct()[:50]

    context = {'questions':questions,}
    return render(request, 'home/hot_q_home.html', context)

def hot_q_week_home(request):
    last_7_days = timezone.now() - timedelta(days=7)
    questions = Question.objects.filter(
                    viewers__gte=2
                    ).annotate(countComment=Count('commentq')
                    ).filter(qupvote__date__gt=last_7_days
                    ).order_by('qupvote'
                    ).order_by('-countComment'
                    ).distinct()[:50]

    context = {'questions':questions,}
    return render(request, 'home/hot_q_week_home.html', context)

def hot_q_month_home(request):
    last_28_days = timezone.now() - timedelta(days=28)
    questions = Question.objects.filter(
                    viewers__gte=2
                    ).annotate(countComment=Count('commentq')
                    ).filter(qupvote__date__gt=last_28_days
                    ).order_by('qupvote'
                    ).order_by('-countComment'
                    ).distinct()[:50]

    context = {'questions':questions,}
    return render(request, 'home/hot_q_month_home.html', context)


def activityPageTabProfile(request,user_id,username):
    profileData = get_object_or_404(Profile, pk=user_id)
    UserAnswers = Answer.objects.filter(answer_owner=profileData.user)
    goldBadges = TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="GOLD")[:3]
    silverBadges = TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER")[:3]
    bronzeBadges = TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE")[:3]

    if request.user.is_authenticated:
        topTags = Tag.objects.filter(question__post_owner=request.user).annotate(countTheVotes=Count('question__qupvote')).filter(countTheVotes__gte=2)
    else:
        topTags = ''

    questions = Question.objects.filter(post_owner=profileData.user).exclude(is_deleted=True)
    answers = Answer.objects.filter(answer_owner=profileData.user).exclude(is_deleted=True)

    getMixTopVotes_Q = list(Question.objects.filter(post_owner=profileData.user).exclude(is_deleted=True).annotate(getMostVotes=Count('qupvote')).order_by('getMostVotes'))
    getMisTopVotes_A = list(Answer.objects.filter(answer_owner=profileData.user).exclude(is_deleted=True).annotate(getMostVotes=Count('a_vote_ups')).order_by('getMostVotes'))

    def order_by(obj):
        try:
            return obj.getMostVotes
        except AttributeError:
            return obj.getMostVotes

    results = sorted(chain(getMixTopVotes_Q, getMisTopVotes_A),key=order_by , reverse=True)

    USER_ONLINE_TIMEOUT = timedelta(seconds=5)
    min_time = timezone.now() - (USER_ONLINE_TIMEOUT)
    queryset = online_users.models.OnlineUserActivity.objects.filter(
        user_id=profileData.user).annotate(is_online=Case(
            When(last_activity__gte=min_time, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ))

    online_user_activity = get_object_or_404(queryset)

    # Peoples Reached
    getAllTheViewsOfAllTheQuestion = Question.objects.filter(post_owner=profileData.user).annotate(total_views=Count('viewers')).aggregate(Sum('total_views'))


    context = {
        'online_user_activity':online_user_activity,
        'results':results,
        'getAllTheViewsOfAllTheQuestion':getAllTheViewsOfAllTheQuestion,
        'topTags':topTags,
        'profileData':profileData,
        'user_id':user_id,
        'goldBadges':goldBadges,
        'silverBadges':silverBadges,
        'bronzeBadges':bronzeBadges,
        'questions':questions,
        'answers':answers,
    }
    return render(request, 'profile/UserProfile_Profile_ActivityTab.html', context)


def developerStoryTab(request, user_id):
    profileStory = get_object_or_404(Profile, user=profileData.user)

    context = {'profileStory':profileStory}
    return render(request, 'profile/developerStoryTab.html', context)


def uploadPosition(request, user_id):
    positions = Position.objects.filter(user=request.user)

    profiles = request.user.profile

    if request.method == 'POST':
        form = PositionCreateForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            new_post.save()
            return redirect('profile:home')

    else:
        form = PositionCreateForm()

    context = {'positions':positions,'profiles': profiles, 'form': form}
    return render(request, 'profile/uploadPosition.html', context)


def addPositionAjax(request,user_id):
    # data = get_object_or_404(Question, pk=question_id)
    # request should be ajax and method should be POST.
    if is_ajax(request) and request.method == "POST":
        # get the form data
        edit_Q_Form = PositionCreateForm(request.POST, request.FILES)
        # save the data and after fetch the object in instance
        if edit_Q_Form.is_valid():
            instance = edit_Q_Form.save(commit=False)
            instance.user = request.user
            instance = edit_Q_Form.save()
            # serialize in new friend object in json
            new_instance = serializers.serialize('json', [
                instance,
            ])
            # send to client side.
            return JsonResponse({"instance": new_instance}, status=200)
        else:
            # some form errors occured.
            return JsonResponse({"error": form.errors}, status=400)

    # some error occured
    return JsonResponse({"error": ""}, status=400)


# IMPLEMENTED THE LOGIC
    # It will show all the questions bookmarked by user_id.
    # Most Votes | Last Edited | Most Recent | Most Views
def bookmarksActivity(request, user_id, username):
    profileData = get_object_or_404(Profile, pk=user_id)

    mostVotes_bookmarks = BookmarkQuestion.objects.filter(bookmarked_by=user_id).annotate(countVotes=Count('bookmarked_question__qupvote')).order_by('-countVotes')


    activity_bookmarks= BookmarkQuestion.objects.filter(bookmarked_by=user_id).order_by('-bookmarked_question__q_edited_time')


    newest_bookmarks = BookmarkQuestion.objects.filter(bookmarked_by=user_id).order_by('-date')


    views_bookmarks = BookmarkQuestion.objects.filter(bookmarked_by=user_id).annotate(countViews=Count('bookmarked_question__viewers')).order_by('-countViews')


    totalBookmarks = mostVotes_bookmarks.count()



# Last seen
# To Show Last Seen in Profile. You'll see as "Last seen"
# Transfer this Variable into config.py
    USER_ONLINE_TIMEOUT = timedelta(seconds=5)
    min_time = timezone.now() - (USER_ONLINE_TIMEOUT)
    queryset = online_users.models.OnlineUserActivity.objects.filter(
        user_id=user_id).annotate(is_online=Case(
            When(last_activity__gte=min_time, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ))

    online_user_activity = get_object_or_404(queryset)



    # Total Votes Cast
    countVotedPosts_Q = QUpvote.objects.filter(upvote_by_q=user_id).count()
    countDownVotedPosts_Q = QDownvote.objects.filter(downvote_by_q=user_id).count()

    countVotedPosts_A = Answer.objects.filter(a_vote_ups=user_id).count()
    countDownVotedPosts_A = Answer.objects.filter(a_vote_downs=user_id).count()

    getVotesCast_Final = countVotedPosts_Q + countDownVotedPosts_Q + countVotedPosts_A + countDownVotedPosts_A


    # People Reached
    getAllTheViewsOfAllTheQuestion = Question.objects.filter(post_owner=profileData.user).annotate(total_views=Count('viewers')).aggregate(Sum('total_views'))

    reputation_graph = Reputation.objects.filter(awarded_to=user_id)[:15]



    # ----------Next Badge---------- START----------
    countComments = CommentQ.objects.filter(commented_by=profileData.user).count()



    if profileData.about_me != '':
        completed = True
    else:
        completed = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Benefactor").exists():
        benefactor_earned = True
    else:
        benefactor_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Citizen Patrol",bade_position="BADGE").exists():
        ctzn_ptrl_earned = True
    else:
        ctzn_ptrl_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Civic Duty",bade_position="BADGE").exists():
        civc_duty = True
    else:
        civc_duty = False
    getVotedOnQ = Question.objects.filter(qupvote__upvote_by_q=profileData.user).count()
    getVotedOnQ_Down = Question.objects.filter(qdownvote__downvote_by_q=profileData.user).count()
    getVotedOn = Answer.objects.filter(a_vote_ups=profileData.user).count()
    getVotedOn_Down = Answer.objects.filter(a_vote_downs=profileData.user).count()

    countVotes = getVotedOnQ+getVotedOnQ_Down+getVotedOn+getVotedOn_Down



    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Critic", bade_position="BADGE").exists():
        critic_earned = True
    else:
        critic_earned = False



    if profileData.helpful_flags_counter:
        deputy_earned = True
    else:
        deputy_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Disciplined",bade_position="BADGE").exists():
        disclpned_earned = True
    else:
        disclpned_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Excavator",bade_position="BADGE").exists():
        excvter_earned = True
    else:
        excvter_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Investor", bade_position="BADGE").exists():
        investor_earned = True
    else:
        investor_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="GOLD", tag_name="Marshal", bade_position="BADGE").exists():
        marshal_earned = True
    else:
        marshal_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Necromancer",bade_position="BADGE").exists():
        necromancer_earned = True
    else:
        necromancer_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Peer Pressure",bade_position="BADGE").exists():
        pr_pressre_earned = True
    else:
        pr_pressre_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Promoter", bade_position="BADGE").exists():
        promoter_earned = True
    else:
        promoter_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Proofreader",bade_position="BADGE").exists():
        proffreader_earned = True
    else:
        proffreader_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Refiner",bade_position="BADGE").exists():
        refiner_earned = True
    else:
        refiner_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="Bronze", tag_name="Revival",bade_position="BADGE").exists():
        reviv_earned = True
    else:
        reviv_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Self-Learner",bade_position="BADGE").exists():
        slf_lrnr_earned = True
    else:
        slf_lrnr_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Strunk & White",bade_position="BADGE").exists():
        stnk_whte_earned = True
    else:
        stnk_whte_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Suffrage",bade_position="BADGE").exists():
        suffrage_earned = True
    else:
        suffrage_earned = False

    last_24_hours = timezone.now() - timedelta(hours=24)
    getQ_Votes_in_24_Hours = QUpvote.objects.filter(date__gt=last_24_hours).count()
    getQ_DownVotes_in_24_Hours = QDownvote.objects.filter(downvote_by_q=profileData.user, date__gt=last_24_hours).count()
    getA_Votes_in_24_Hours = Answer.objects.filter(a_vote_ups=profileData.user, date__gt=last_24_hours).count()
    getA_DownVotes_in_24_Hours = Answer.objects.filter(a_vote_downs=profileData.user, date__gt=last_24_hours).count()
    totalVotes = getQ_Votes_in_24_Hours + getQ_DownVotes_in_24_Hours + getA_Votes_in_24_Hours + getA_DownVotes_in_24_Hours

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Vox Populi",bade_position="BADGE").exists():
        vx_pop_earned = True
    else:
        vx_pop_earned = False  



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Teacher",bade_position="BADGE").exists():
        teacher_earned = True
    else:
        teacher_earned = False

    newestBadge = TagBadge.objects.filter(awarded_to_user=profileData.user).last()

    # ----------Next Badge---------- END----------


    context = {
        'newestBadge':newestBadge,
        'countVotes':countVotes,
        'teacher_earned':teacher_earned,
        'totalVotes':totalVotes,
        'vx_pop_earned':vx_pop_earned,
        'suffrage_earned':suffrage_earned,
        'stnk_whte_earned':stnk_whte_earned,
        'slf_lrnr_earned':slf_lrnr_earned,
        'reviv_earned':reviv_earned,
        'refiner_earned':refiner_earned,
        'proffreader_earned':proffreader_earned,
        'promoter_earned':promoter_earned,
        'necromancer_earned':necromancer_earned,
        'marshal_earned':marshal_earned,
        'investor_earned':investor_earned,
        'pr_pressre_earned':pr_pressre_earned,
        'excvter_earned':excvter_earned,
        'deputy_earned':deputy_earned,
        'disclpned_earned':disclpned_earned,
        'civc_duty':civc_duty,
        'critic_earned':critic_earned,
        'ctzn_ptrl_earned':ctzn_ptrl_earned,
        'benefactor_earned':benefactor_earned,
        'completed':completed,
        'countComments':countComments,'reputation_graph':reputation_graph,'getAllTheViewsOfAllTheQuestion':getAllTheViewsOfAllTheQuestion,'totalBookmarks':totalBookmarks,'views_bookmarks':views_bookmarks,'activity_bookmarks':activity_bookmarks,'newest_bookmarks':newest_bookmarks,'getVotesCast_Final':getVotesCast_Final,'mostVotes_bookmarks':mostVotes_bookmarks,'profileData':profileData,'online_user_activity':online_user_activity,}
    return render(request, 'profile/bookmarksActivity.html', context)



# @login_required
# @cache_page(DEFAULT_TIMEOUT)
def ActivityTabSummary(request, user_id, username):
    profileData = get_object_or_404(Profile, pk=user_id)



# Question DIVs - START
    questionsCount = Question.objects.filter(post_owner=profileData.user).exclude(is_deleted=True).count()
    question_most_votes = Question.objects.filter(post_owner=profileData.user).annotate(countThem=Count('qupvote')).order_by('-countThem')[:5]
    question_recent_activity = Question.objects.filter(post_owner=profileData.user).order_by('-active_date')[:5]
    question_newest = Question.objects.filter(post_owner=profileData.user).order_by('-date')[:5]
    question_most_views = Question.objects.filter(post_owner=profileData.user).annotate(countTheViews=Count('viewers')).order_by('-viewers')[:5]
# Question DIVs - END



# Answer DIVs - START
    answersMostVotes = Answer.objects.filter(answer_owner=profileData.user).annotate(
                            countLikes=Count(
                                'a_vote_ups')).order_by('-countLikes')
    answersCount = Answer.objects.filter(answer_owner=profileData.user).count()
    answersThr_Activity = Answer.objects.filter(answer_owner=profileData.user).order_by('-active_time')[:5]
    answersNewest = Answer.objects.filter(answer_owner=profileData.user).order_by('-date')[:5]
# Answer DIVs - END



# Bookmark DIVs - START
    bookmarks_newest = BookmarkQuestion.objects.filter(bookmarked_by=profileData.user).order_by('date')
    bookmarks_votes = BookmarkQuestion.objects.filter(bookmarked_by=profileData.user).annotate(countVotes=Count('bookmarked_question__qupvote')).order_by('-countVotes')
    bookmarks_activity = BookmarkQuestion.objects.filter(bookmarked_by=profileData.user).order_by('-bookmarked_question__active_date')
    bookmarks_views = BookmarkQuestion.objects.filter(bookmarked_by=profileData.user).annotate(countVotes=Count('bookmarked_question__viewers')).order_by('-countVotes')
    countBookmarks = bookmarks_newest.count()
# Bookmark DIVs - END




    reputations = Reputation.objects.filter(awarded_to=profileData.user).annotate(
                        highestTimeRep=F('answer_rep_C')+ F('question_rep_C')).order_by(
                            '-highestTimeRep')[:5]

    tags = Tag.objects.filter(question__answer__answer_owner=profileData.user).annotate(answeredOn=Count('taggit_taggeditem_items'))[:5]



    badges = TagBadge.objects.filter(awarded_to_user=profileData.user).order_by('date')[:5]

    bounties = Bounty.objects.filter(by_user=profileData.user).order_by('date').distinct()


# Votes cast - START
    Up_votesCast_Q = QUpvote.objects.filter(upvote_by_q=profileData.user).count()
    Down_votesCast_Q = QDownvote.objects.filter(downvote_by_q=profileData.user).count()

    Up_votesCast_A = Answer.objects.filter(a_vote_ups=profileData.user).count()
    Down_votesCast_A = Answer.objects.filter(a_vote_downs=profileData.user).count()

    totalUpvotes = Up_votesCast_Q + Up_votesCast_A
    totalDownVotes = Down_votesCast_Q + Down_votesCast_A

    questionVotes = Up_votesCast_Q + Down_votesCast_Q
    answerVotes = Up_votesCast_A + Down_votesCast_A
# Votes cast - END



    # mixed_vote_count = totalUpvotes + totalDownVotes


    # getting = Profile.objects.filter(is_high_moderator=False)



    getAlltheReputation = Reputation.objects.filter(awarded_to=profileData.user).aggregate(Sum('answer_rep_C'),Sum('question_rep_C'))
    d = getAlltheReputation['question_rep_C__sum']
    total_Question_Rep = getAlltheReputation['question_rep_C__sum'] if d else 0
    s = getAlltheReputation['answer_rep_C__sum']
    total_answer_Rep = getAlltheReputation['answer_rep_C__sum'] if s else 0

    finalReputation = total_answer_Rep + total_Question_Rep


# To Show Last Seen in Profile. You'll see as "Last seen"
# Transfer this Variable into config.py
    USER_ONLINE_TIMEOUT = timedelta(seconds=5)
    min_time = timezone.now() - (USER_ONLINE_TIMEOUT)
    queryset = online_users.models.OnlineUserActivity.objects.filter(
        user_id=profileData.user).annotate(is_online=Case(
            When(last_activity__gte=min_time, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ))

    online_user_activity = get_object_or_404(queryset)



    # People Reached
    getAllTheViewsOfAllTheQuestion = Question.objects.filter(post_owner=profileData.user).annotate(total_views=Count('viewers')).aggregate(Sum('total_views'))


    # Total Votes Cast
    countVotedPosts_Q = QUpvote.objects.filter(upvote_by_q=profileData.user).count()
    countDownVotedPosts_Q = QDownvote.objects.filter(downvote_by_q=profileData.user).count()

    countVotedPosts_A = Answer.objects.filter(a_vote_ups=profileData.user).count()
    countDownVotedPosts_A = Answer.objects.filter(a_vote_downs=profileData.user).count()

    getVotesCast_Final = countVotedPosts_Q + countDownVotedPosts_Q + countVotedPosts_A + countDownVotedPosts_A
    reputation_graph = Reputation.objects.filter(awarded_to=profileData.user)[:15]

    # ----------Next Badge---------- START----------
    countComments = CommentQ.objects.filter(commented_by=profileData.user).count()



    if profileData.about_me != '':
        completed = True
    else:
        completed = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Benefactor").exists():
        benefactor_earned = True
    else:
        benefactor_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Citizen Patrol",bade_position="BADGE").exists():
        ctzn_ptrl_earned = True
    else:
        ctzn_ptrl_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Civic Duty",bade_position="BADGE").exists():
        civc_duty = True
    else:
        civc_duty = False
    getVotedOnQ = Question.objects.filter(qupvote__upvote_by_q=profileData.user).count()
    getVotedOnQ_Down = Question.objects.filter(qdownvote__downvote_by_q=profileData.user).count()
    getVotedOn = Answer.objects.filter(a_vote_ups=profileData.user).count()
    getVotedOn_Down = Answer.objects.filter(a_vote_downs=profileData.user).count()

    countVotes = getVotedOnQ+getVotedOnQ_Down+getVotedOn+getVotedOn_Down



    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Critic", bade_position="BADGE").exists():
        critic_earned = True
    else:
        critic_earned = False



    if profileData.helpful_flags_counter:
        deputy_earned = True
    else:
        deputy_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Disciplined",bade_position="BADGE").exists():
        disclpned_earned = True
    else:
        disclpned_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Excavator",bade_position="BADGE").exists():
        excvter_earned = True
    else:
        excvter_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Investor", bade_position="BADGE").exists():
        investor_earned = True
    else:
        investor_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="GOLD", tag_name="Marshal", bade_position="BADGE").exists():
        marshal_earned = True
    else:
        marshal_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Necromancer",bade_position="BADGE").exists():
        necromancer_earned = True
    else:
        necromancer_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Peer Pressure",bade_position="BADGE").exists():
        pr_pressre_earned = True
    else:
        pr_pressre_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user, badge_type="BRONZE", tag_name="Promoter", bade_position="BADGE").exists():
        promoter_earned = True
    else:
        promoter_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Proofreader",bade_position="BADGE").exists():
        proffreader_earned = True
    else:
        proffreader_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Refiner",bade_position="BADGE").exists():
        refiner_earned = True
    else:
        refiner_earned = False


    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="Bronze", tag_name="Revival",bade_position="BADGE").exists():
        reviv_earned = True
    else:
        reviv_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Self-Learner",bade_position="BADGE").exists():
        slf_lrnr_earned = True
    else:
        slf_lrnr_earned = False

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Strunk & White",bade_position="BADGE").exists():
        stnk_whte_earned = True
    else:
        stnk_whte_earned = False



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Suffrage",bade_position="BADGE").exists():
        suffrage_earned = True
    else:
        suffrage_earned = False

    last_24_hours = timezone.now() - timedelta(hours=24)
    getQ_Votes_in_24_Hours = QUpvote.objects.filter(date__gt=last_24_hours).count()
    getQ_DownVotes_in_24_Hours = QDownvote.objects.filter(downvote_by_q=profileData.user, date__gt=last_24_hours).count()
    getA_Votes_in_24_Hours = Answer.objects.filter(a_vote_ups=profileData.user, date__gt=last_24_hours).count()
    getA_DownVotes_in_24_Hours = Answer.objects.filter(a_vote_downs=profileData.user, date__gt=last_24_hours).count()
    totalVotes = getQ_Votes_in_24_Hours + getQ_DownVotes_in_24_Hours + getA_Votes_in_24_Hours + getA_DownVotes_in_24_Hours

    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="BRONZE", tag_name="Vox Populi",bade_position="BADGE").exists():
        vx_pop_earned = True
    else:
        vx_pop_earned = False  



    if TagBadge.objects.filter(awarded_to_user=profileData.user,badge_type="SILVER", tag_name="Teacher",bade_position="BADGE").exists():
        teacher_earned = True
    else:
        teacher_earned = False

    newestBadge = TagBadge.objects.filter(awarded_to_user=profileData.user).last()

    # ----------Next Badge---------- END----------



    context = {
        'newestBadge':newestBadge,
        'countVotes':countVotes,
        'teacher_earned':teacher_earned,
        'totalVotes':totalVotes,
        'vx_pop_earned':vx_pop_earned,
        'suffrage_earned':suffrage_earned,
        'stnk_whte_earned':stnk_whte_earned,
        'slf_lrnr_earned':slf_lrnr_earned,
        'reviv_earned':reviv_earned,
        'refiner_earned':refiner_earned,
        'proffreader_earned':proffreader_earned,
        'promoter_earned':promoter_earned,
        'necromancer_earned':necromancer_earned,
        'marshal_earned':marshal_earned,
        'investor_earned':investor_earned,
        'pr_pressre_earned':pr_pressre_earned,
        'excvter_earned':excvter_earned,
        'deputy_earned':deputy_earned,
        'disclpned_earned':disclpned_earned,
        'civc_duty':civc_duty,
        'critic_earned':critic_earned,
        'ctzn_ptrl_earned':ctzn_ptrl_earned,
        'benefactor_earned':benefactor_earned,
        'completed':completed,
        'countComments':countComments,

        'countBookmarks':countBookmarks,
        'reputation_graph':reputation_graph,
        'online_user_activity':online_user_activity,
        'getVotesCast_Final':getVotesCast_Final,
        'finalReputation':finalReputation,
        'Up_votesCast_Q':Up_votesCast_Q,
        'totalUpvotes':totalUpvotes,
        'totalDownVotes':totalDownVotes,
        'profileData': profileData,
        'answersNewest':answersNewest,
        'answersMostVotes':answersMostVotes,
        'answersThr_Activity':answersThr_Activity,
        'user_id':user_id,
        'questionVotes':questionVotes,
        'answerVotes':answerVotes,
        'answersCount':answersCount,
        # 'obj':obj,
        # 'getting':getting,
        'question_most_votes': question_most_votes,
        'question_recent_activity': question_recent_activity,
        'question_newest': question_newest,
        'question_most_views': question_most_views,
        'reputations':reputations,
        'questionsCount':questionsCount,
        'tags':tags,
        'getAllTheViewsOfAllTheQuestion':getAllTheViewsOfAllTheQuestion,

        'bookmarks_newest':bookmarks_newest,
        'bookmarks_votes':bookmarks_votes,
        'bookmarks_activity':bookmarks_activity,
        'bookmarks_views':bookmarks_views,
        'badges':badges,
        'bounties':bounties,
        # 'mixed_vote_count':mixed_vote_count,
    }

    return render(request, 'profile/UserProfile.html', context)


def tagPage(request, user_id, tagbadge_id):
    user = get_object_or_404(User, pk=user_id)
    tag = get_object_or_404(TagBadge, pk=tagbadge_id)
    allTags = Tag.objects.all().values_list('name', flat=True)
    allTagsGold = TagBadge.objects.filter(awarded_to_user=user).values_list('tag_name', flat=True)
    tagName = tag.tag_name
    if tag.tag_name in allTags and tag.tag_name in allTagsGold:
        it_it_earned_by = "Earned"
        print("Earned")
    else:
        it_it_earned_by = "Didn't Earned"
        print("Didn't Earned")
    print(tag.tag_name)



    otherWithSame_Badge = TagBadge.objects.filter(tag_name=tag.tag_name).order_by('-date').exclude(awarded_to_user__isnull=True)

    context = {'tagName':tagName,'tag':tag,'it_it_earned_by':it_it_earned_by,'user_1':user,'allTags':allTags,'otherWithSame_Badge':otherWithSame_Badge,}
    return render(request, 'tagbadge/user_profile_tags.html', context)


def otherWithSame_Badge(request, tag):
    # print(tag.tag_name)
    objQ = TagBadge.objects.filter(tag_name=tag).order_by('-date').exclude(awarded_to_user__isnull=True)

    context = {'objQ':objQ,'tag':tag}
    return render(request, 'tagbadge/otherWithSame_Badge.html', context)


@unBanRequired
@profileOwnerRequired_For_Edit
def userProfileEdit_Settings(request, user_id):
    profileData = get_object_or_404(Profile, id=user_id)

    if request.method == 'POST':
        Edit_profile_form = EditProfileForm(data=request.POST,
                                 files=request.FILES,
                                 instance=request.user.profile)

        if Edit_profile_form.is_valid():
            custom_form = Edit_profile_form.save(commit=False)
            custom_form.save()
            if request.user.profile.about_me != '':
                print("Not Blank")
                awardBadge = TagBadge.objects.get_or_create(awarded_to_user=request.user,badge_type="Bronze", tag_name="Autobiographer",bade_position="BADGE")
                sendNotification = PrivRepNotification.objects.get_or_create(for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

            messages.success(request, "Profile Saved")
            return redirect('profile:home')

    else:
        Edit_profile_form = EditProfileForm(instance=request.user.profile)

# To Show Last Seen in Profile. You'll see as "Last seen"
# Transfer this Variable into config.py
    USER_ONLINE_TIMEOUT = timedelta(seconds=5)
    min_time = timezone.now() - (USER_ONLINE_TIMEOUT)
    queryset = online_users.models.OnlineUserActivity.objects.filter(
        user_id=user_id).annotate(is_online=Case(
            When(last_activity__gte=min_time, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ))

    online_user_activity = get_object_or_404(queryset)


    context = {'Edit_profile_form': Edit_profile_form,'profileData':profileData,'online_user_activity':online_user_activity,}
    return render(request, 'profile/EditProfile.html', context)
from django.core.files.storage import FileSystemStorage


def EditProfileAjaxForm(request, user_id):
    # data = get_object_or_404(Answer, pk=answer_id)
    # request should be ajax and method should be POST.
    if is_ajax(request) and request.method == "POST":



        request.user.profile.full_name = request.POST.get("full_name")
        request.user.profile.location = request.POST.get("location")
        request.user.profile.title = request.POST.get("title")
        request.user.profile.about_me = request.POST.get("about_me")
        request.user.profile.website_link = request.POST.get("website_link")
        request.user.profile.twitter_link = request.POST.get("twitter_link")
        request.user.profile.github_link = request.POST.get("github_link")
        request.user.profile.not_to_Display_Full_name = request.POST.get("not_to_Display_Full_name")

        
        if request.FILES != {}:
            request.user.profile.profile_photo = request.FILES["image"]

        request.user.profile.save()


        if request.user.profile.about_me != '':
            awardBadge = TagBadge.objects.get_or_create(awarded_to_user=request.user,badge_type="Bronze", tag_name="Autobiographer",bade_position="BADGE")
            sendNotification = PrivRepNotification.objects.get_or_create(for_user=request.user, url="#", type_of_PrivNotify="BADGE_EARNED", for_if="Autobiographer")


        return JsonResponse({"instance": "SUCCESS"}, status=200)


    # some error occured
    return JsonResponse({"error": ""}, status=400)



@unBanRequired
@profileOwnerRequired_For_Edit
def userProfileJonPrefrences_Settings(request, user_id):
    profileData = get_object_or_404(Profile, pk=user_id)

    if request.method == 'POST':
        editProfile_Job = EditJobPrefrences(request.POST,
                                 request.FILES,
                                 instance=request.user.profile)

        if editProfile_Job.is_valid():
            # custom_form = editProfile_Job.save(commit=False)
            custom_form.save()

            # messages.success(request, "Profile Saved")
            # return redirect('profile:home')

    else:
        editProfile_Job = EditJobPrefrences(instance=request.user.profile)

    USER_ONLINE_TIMEOUT = timedelta(seconds=5)
    min_time = timezone.now() - (USER_ONLINE_TIMEOUT)
    queryset = online_users.models.OnlineUserActivity.objects.filter(
        user_id=profileData.user).annotate(is_online=Case(
            When(last_activity__gte=min_time, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ))

    online_user_activity = get_object_or_404(queryset)


    context = {'online_user_activity':online_user_activity,'profileData':profileData,'editProfile_Job': editProfile_Job}
    return render(request, 'profile/EditProfileJobPrefrences.html', context)


def editProfile_JobPreAjax_Form(request, user_id):
    if is_ajax(request) and request.method == "POST":
        # get the form data
        editProfile = EditJobPrefrences(instance=request.user.profile,
                          data=request.POST,
                          files=request.FILES)
        # save the data and after fetch the object in instance
        if editProfile.is_valid():
            instance = editProfile.save()
            # serialize in new friend object in json
            new_instance = serializers.serialize('json', [
                instance,
            ])
            # send to client side.
            return JsonResponse({"instance": new_instance}, status=200)
        else:
            # some form errors occured.
            print(editProfile.errors)
            return JsonResponse({"error": editProfile.errors}, status=400)

    # some error occured
    return JsonResponse({"error": ""}, status=400)


@unBanRequired
@profileOwnerRequired_For_Edit
def userProfileEdit_Email_Settings(request, user_id):
    profileData = get_object_or_404(Profile, pk=user_id)
    if request.method == 'POST':
        editEmail = EditEmailForm(request.POST,
                                 request.FILES,
                                 instance=request.user.profile)
    else:
        editEmail = EditEmailForm(instance=request.user.profile)

    context = {'profileData':profileData,'editEmail': editEmail}
    return render(request, 'profile/Edit_Email_Settings.html', context)

def editProfile_EditEmail_AjaxForm(request, user_id):
    # data = get_object_or_404(Answer, pk=answer_id)
    # request should be ajax and method should be POST.
    if is_ajax(request) and request.method == "POST":
        # get the form data
        editEmail = EditEmailForm(instance=request.user.profile,
                          data=request.POST,
                          files=request.FILES)
        # save the data and after fetch the object in instance
        if editEmail.is_valid():
            instance = editEmail.save()
            # serialize in new friend object in json
            new_instance = serializers.serialize('json', [
                instance,
            ])
            # send to client side.
            return JsonResponse({"instance": new_instance}, status=200)
        else:
            # some form errors occured.
            return JsonResponse({"error": editEmail.errors}, status=400)

    # some error occured
    return JsonResponse({"error": ""}, status=400)


def email_html(request):
    profile = request.user.profile

    # receivers = []

    # for users in Profile.objects.all():
    #     receivers.append(users.email)

    subject = 'Subject'
    html_message = render_to_string('profile/pdf2.html', {'context': profile})
    plain_message = strip_tags(html_message)
    from_email = 'From yawanspace@gmail.com'
    to = 'myspaceissecret@gmail.com'
    mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)


# def email_html(request):
#     sent = False

#     if request.method == 'POST':
#         form = EmailForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             subject = f"{cd['name']} recommends you read"

#             message = f"{cd['review']} "
#             send_mail(subject,message,'yawanspace@gmail.com',
#                 [request.user.profile.email])
#             sent = True

#     else:
#         form = EmailForm()

#     context = {'sent':sent,'form':form}
#     return render(request, 'profile/pdf2.html', context)


def select_BadgeTarget(request, user_id):
    toTargetPlace = Profile.objects.get(user=user_id)

    if request.GET.get('submit') == 'commenter':
        toTargetPlace.targeted_tag = "Commenter"
        toTargetPlace.save()
        return JsonResponse({'action': 'commenter'})

    elif request.GET.get('submit') == 'altruist':
        toTargetPlace.targeted_tag = "Altruist"
        toTargetPlace.save()
        return JsonResponse({'action':'altruist'})

    elif request.GET.get('submit') == "archaeologist":
        toTargetPlace.targeted_tag = "Archaeologist"
        toTargetPlace.save()
        return JsonResponse({'action': 'archaeologist'})

    elif request.GET.get('submit') == 'autobiographer':
        toTargetPlace.targeted_tag = "Autobiographer"
        toTargetPlace.save()
        return JsonResponse({'action': 'autobiographer'})

    elif request.GET.get('submit') == 'civic_duty':
        toTargetPlace.targeted_tag = "Civic Duty"
        toTargetPlace.save()
        return JsonResponse({'action': 'civic_duty'})

    elif request.GET.get('submit') == 'benefactor':
        toTargetPlace.targeted_tag = "Benefactor"
        toTargetPlace.save()
        return JsonResponse({'action': 'benefactor'})

    elif request.GET.get('submit') == 'citizen_duty':
        toTargetPlace.targeted_tag = "Citizen Duty"
        toTargetPlace.save()
        return JsonResponse({'action': 'citizen_duty'})

    elif request.GET.get('submit') == 'citizen_post':
        toTargetPlace.targeted_tag = "Citizen Post"
        toTargetPlace.save()
        return JsonResponse({'action':'citizen_post'})

    elif request.GET.get('submit') == 'copy_editor':
        toTargetPlace.targeted_tag = "Copy Editor"
        toTargetPlace.save()
        return JsonResponse({'action': 'copy_editor'})

    elif request.GET.get('submit') == 'critic':
        toTargetPlace.targeted_tag = "Critic"
        toTargetPlace.save()
        return JsonResponse({'action': 'critic'})

    elif request.GET.get('submit') == 'custodian':
        toTargetPlace.targeted_tag = "Custodian"
        toTargetPlace.save()
        return JsonResponse({'action': 'custodian'})

    elif request.GET.get('submit') == 'deputy':
        toTargetPlace.targeted_tag = "Deputy"
        toTargetPlace.save()
        return JsonResponse({'action':'deputy'})

    elif request.GET.get('submit') == 'disciplned':
        toTargetPlace.targeted_tag = "Discliplned"
        toTargetPlace.save()
        return JsonResponse({'action': 'discliplned'})

    elif request.GET.get('submit') == 'electorate':
        toTargetPlace.targeted_tag = "Electorate"
        toTargetPlace.save()
        return JsonResponse({'action': 'electorate'})

    elif request.GET.get('submit') == 'excavator':
        toTargetPlace.targeted_tag = "Excavator"
        toTargetPlace.save()
        return JsonResponse({'action':'excavator'})

    elif request.GET.get('submit') == 'explainer':
        toTargetPlace.targeted_tag = "Explainer"
        toTargetPlace.save()
        return JsonResponse({'action': 'explainer'})

    elif request.GET.get('submit') == 'illuminator':
        toTargetPlace.targeted_tag = "Illuminator"
        toTargetPlace.save()
        return JsonResponse({'action': 'illuminator'})

    elif request.GET.get('submit') == 'investor':
        toTargetPlace.targeted_tag = "Investor"
        toTargetPlace.save()
        return JsonResponse({'action':'investor'})

    elif request.GET.get('submit') == 'marshal':
        toTargetPlace.targeted_tag = "Marshal"
        toTargetPlace.save()
        return JsonResponse({'action': 'marshal'})

    elif request.GET.get('submit') == 'mortarboard':
        toTargetPlace.targeted_tag = "Mortarboard"
        toTargetPlace.save()
        return JsonResponse({'action': 'mortarboard'})

    elif request.GET.get('submit') == 'necromancer':
        toTargetPlace.targeted_tag = "Necromancer"
        toTargetPlace.save()
        return JsonResponse({'action':'necromancer'})

    elif request.GET.get('submit') == 'peer_pressure':
        toTargetPlace.targeted_tag = "Peer Pressure"
        toTargetPlace.save()
        return JsonResponse({'action':'peer_pressure'})

    elif request.GET.get('submit') == 'promoter':
        toTargetPlace.targeted_tag = "Promoter"
        toTargetPlace.save()
        return JsonResponse({'action':'promoter'})

    elif request.GET.get('submit') == 'proofreader':
        toTargetPlace.targeted_tag = "Proofreader"
        toTargetPlace.save()
        return JsonResponse({'action':'proofreader'})

    elif request.GET.get('submit') == 'refiner':
        toTargetPlace.targeted_tag = "Refiner"
        toTargetPlace.save()
        return JsonResponse({'action':'refiner'})

    elif request.GET.get('submit') == 'revival':
        toTargetPlace.targeted_tag = "Revival"
        toTargetPlace.save()
        return JsonResponse({'action':'revival'})

    elif request.GET.get('submit') == 'self_learner':
        toTargetPlace.targeted_tag = "Self-learner"
        toTargetPlace.save()
        return JsonResponse({'action':'self_learner'})

    elif request.GET.get('submit') == 'sportsmanship':
        toTargetPlace.targeted_tag = "Sportsmanship"
        toTargetPlace.save()
        return JsonResponse({'action':'sportsmanship'})

    elif request.GET.get('submit') == 'strunk_white':
        toTargetPlace.targeted_tag = "Strunk-White"
        toTargetPlace.save()
        return JsonResponse({'action':'strunk_white'})

    elif request.GET.get('submit') == 'suffrage':
        toTargetPlace.targeted_tag = "Suffrage"
        toTargetPlace.save()
        return JsonResponse({'action':'suffrage'})

    elif request.GET.get('submit') == 'teacher':
        toTargetPlace.targeted_tag = "Teacher"
        toTargetPlace.save()
        return JsonResponse({'action':'teacher'})

    elif request.GET.get('submit') == 'vox_populi':
        toTargetPlace.targeted_tag = "Vox-Populi"
        toTargetPlace.save()
        return JsonResponse({'action':'vox_populi'})

    else:
        messages.error(request, 'Something went wrong!')
        return redirect('profile:home')
