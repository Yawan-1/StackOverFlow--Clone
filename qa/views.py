from django.shortcuts import render, redirect, get_object_or_404
from .models import Question, Answer, Bounty, Reputation, ProtectQuestion
from .forms import QuestionForm, AnswerForm, UpdateQuestion
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q, Sum, F
from profile.models import Profile
from django.contrib import messages
from notification.models import Notification, PrivRepNotification
from django.core.mail import send_mail
from .forms import BountyForm, BanUser_Form, InlineTagEditForm
from taggit.models import Tag
import datetime
from django.utils import timezone
from datetime import timedelta
from .decorators import loggedOutFromAllDevices, superuser_only, highModRequired
from review.decorators import awardReputation
from .forms import ProtectForm, EditAnswerForm
from .models import CommentQ, QUpvote, QDownvote
from django.contrib.auth.models import User
from tagbadge.models import TagBadge
from simple_history.utils import update_change_reason
from itertools import chain
from .models import BannedUser, BookmarkQuestion
import threading
import time
from time import sleep
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from review.models import CloseQuestionVotes, ReviewCloseVotes, ReOpenQuestionVotes
from review.models import ReviewQuestionReOpenVotes, QuestionEditVotes, ReviewQuestionEdit
from review.models import LowQualityPostsCheck, ReviewLowQualityPosts, FlagPost, FlagComment
from review.models import ReviewFlagComment, ReviewFlagPost
from review.forms import CloseForm_Q, VoteToReOpenForm, FlagQuestionForm, CommentFlagForm, AnswerFlagForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import F
from django.urls import reverse
from django.core import serializers
from django.forms.models import model_to_dict
from itertools import compress
import re
from django.contrib.auth.decorators import login_required

"""
Refrence of build_absolute_uri -
    https://docs.djangoproject.com/en/4.0/ref/request-response/#django.http.HttpRequest.build_absolute_uri
    https://stackoverflow.com/questions/2345708/how-can-i-get-the-full-absolute-url-with-domain-in-django
"""

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

"""
A simple function to convert listed strings
into seperate strings.
"""


def listTOString(word):
    emptyString = ""
    return emptyString.join(word)


def UnBanUser(id):
    """
    I used threading for automatic removal of the User's Ban Suspension, But
    the only problem in "threading" is that if server goes down for any reason
    than all the threads will stop and lost, all the background tasks will stop.
    """

    saveToFalse = BannedUser.objects.get(pk=id)
    if saveToFalse.ban_till == "3_DAYS":
        seconds = 10
        time.sleep(seconds)
    elif saveToFalse.ban_till == "7_DAYS":
        seconds_2 = 604800
        time.sleep(seconds_2)
    elif saveToFalse.ban_till == "15_DAYS":
        seconds_2 = 1296000
        time.sleep(seconds_2)
    elif saveToFalse.ban_till == "30_DAYS":
        seconds_2 = 2592000
        time.sleep(seconds_2)
    elif saveToFalse.ban_till == "2_MONTHS":
        seconds_2 = 5184000
        time.sleep(seconds_2)
    elif saveToFalse.ban_till == "6_MONTHS":
        seconds_2 = 15552000
        time.sleep(seconds_2)
    elif saveToFalse.ban_till == "1_YEAR":
        seconds_2 = 31104000
        time.sleep(seconds_2)
    elif saveToFalse.ban_till == "4_YEARS":
        seconds_2 = 62208000
        time.sleep(seconds_2)

    saveToFalse.is_banned = True
    saveToFalse.save()

    print("Banned Suspension is Successfully Removed")


"""
Ajax form of inline tag editing.

Where to find it :-: In question detail Page.
"""


def InlineTagEditingForm(request, question_id):
    """
    This is view or function for handling ajax's form
    of inline tag editing in Question-Detail-View
    """
    data = get_object_or_404(Question, pk=question_id)

    if request.is_ajax and request.method == 'POST':
        form = InlineTagEditForm(
            instance=data, data=request.POST, files=request.FILES)
        if form.is_valid():
            if request.user.profile.accessTo_moderatorTools:
                instance = form.save(commit=False)
                # instance.user = request.user
                instance = form.save()
                form.save_m2m()
                ser_instance = serializers.serialize('json', [
                    instance,
                ])
                # send to client side.
                return JsonResponse({"instance": "saved"}, status=200)
            else:
                return JsonResponse({'action': 'lackOfPrivelege'})
        else:
            return JsonResponse({"error": form.errors}, status=400)
    return JsonResponse({"error": ""}, status=400)


# @highModRequired
def banUser(request, user_id):
    """
    Ordinary form for Ban the user, When user submits form
    then it will start and save a thread with unique id,
    to keep track of Ban time and with choosen ban days limit
    thread will remove the ban suspension.
    """
    user = get_object_or_404(User, id=user_id)
    userBanHistory = BannedUser.objects.filter(user=user_id)

    if request.method == 'POST':
        ban_form = BanUser_Form(data=request.POST)
        if ban_form.is_valid():
            post = ban_form.save(commit=False)
            post.user = user
            post.banned_by = request.user
            post.save()

            # Begin Thread and send to "UnBanUser" view to track the time.
            t = threading.Thread(target=UnBanUser, args=[post.id])
            t.setDaemon(True)
            t.start()

            return redirect('profile:home')

    else:
        ban_form = BanUser_Form()

    context = {'ban_form': ban_form, 'userBanHistory': userBanHistory}
    return render(request, 'qa/banUser.html', context)
    # return redirect('profile:home')


# TRANSFER
def allActiveThreads(request):
    """
    It will show all the threads currently running.
    Made this to check the active threads.
    """

    allThreads = threading.enumerate()

    context = {'allThreads': allThreads}
    return render(request, 'qa/allActiveThreads.html', context)

# Decorator of post_owner or moderator or gold tag badge earned user required


def deleteQuestion(request, question_id):
    """
    view to delete question and award badges if user is eligible
    """
    question = get_object_or_404(Question, pk=question_id)
    question.deleted_time = timezone.now()
    question.save()
    if question.qupvote_set.all().count() >= 3:
        TagBadge.objects.get_or_create(
            awarded_to_user=question.post_owner,
            badge_type="BRONZE",
            tag_name="Disciplined",
            bade_position="BADGE",
            questionIf_TagOf_Q=question
        )
        PrivRepNotification.objects.get_or_create(
            for_user=request.user,
            url="#",
            type_of_PrivNotify="BADGE_EARNED",
            for_if="Disciplined",
            description="Delete own post with score of 3 or higher"
        )

    getUpvotes = question.qupvote_set.all().count()
    getDownVotes = question.qupvote_set.all().count()

    if question.calculate_UpVote_DownVote >= -3:
        TagBadge.objects.get_or_create(awarded_to_user=question.post_owner,
                                       badge_type="BRONZE",
                                       tag_name="Peer Pressure",
                                       bade_position="BADGE",
                                       questionIf_TagOf_Q=question
                                       )
        PrivRepNotification.objects.get_or_create(
            for_user=request.user,
            url="#",
            type_of_PrivNotify="BADGE_EARNED",
            for_if="Peer Pressure",
            description="Delete own post with score of -3 or lower"
        )

    if request.user == question.post_owner:
        question.is_deleted = True
        question.save()
        return redirect('qa:questionDetailView', pk=question_id)
    else:
        messages.error(request, 'You are not the Post Owner')
        # return JsonResponse({'action':'notPostOwner'})
        return redirect('qa:questionDetailView', pk=question_id)


def undeleteQuestion(request, question_id):
    """
    view to undelete Question
    """
    question = get_object_or_404(Question, pk=question_id)
    if request.user == question.post_owner:
        question.is_deleted = False
        question.save()
        return redirect('qa:questionDetailView', pk=question_id)
    else:
        messages.error(request, 'You are not post owner')
        return redirect('qa:questionDetailView', pk=question_id)


def delete_answer(request, answer_id):
    """
    view to delete Answer
    """
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user == answer.answer_owner:
        answer.is_deleted = True
        answer.deleted_time = timezone.now()
        answer.save()
        return redirect('qa:questionDetailView', pk=answer.questionans.id)
    else:
        messages.error(request, 'You are not post owner')
        return redirect('qa:questionDetailView', pk=answer.questionans.id)


def undelete_answer(request, answer_id):
    """
    view to undelete Answer
    """
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user == answer.answer_owner:
        answer.is_deleted = False
        answer.save()
        return redirect('qa:questionDetailView', pk=answer.questionans.id)
    else:
        messages.error(request, 'You are not post owner')
        return redirect('qa:questionDetailView', pk=answer.questionans.id)


def rewardPrivielege(request, which_user):
    """
    This view will reward privilege to user when called
    within a view with "user" argument to award
    """
    getAlltheReputation = Reputation.objects.filter(
        awarded_to=which_user).aggregate(
        Sum('answer_rep_C'), Sum('question_rep_C'))
    Q_rep = getAlltheReputation['question_rep_C__sum']
    final_Q_Rep = getAlltheReputation['question_rep_C__sum'] if Q_rep else 0
    A_rep = getAlltheReputation['answer_rep_C__sum']
    final_A_Rep = getAlltheReputation['answer_rep_C__sum'] if A_rep else 0
    totalReputation = final_Q_Rep + final_A_Rep

    # If user's reputation is more than 10 then Award Create Wiki Posts privilege.
    if totalReputation >= 10:
        # Create Wiki Posts - DONE
        which_user.profile.create_wiki_posts = True
        # Answer Protect Questions - DONE
        which_user.profile.remove_new_user_restrictions = True
        which_user.profile.save()
        PrivRepNotification.objects.get_or_create(
            for_user=which_user,
            privilegeURL="#",
            for_if="Create Wiki Posts",
            type_of_PrivNotify="Privilege_Earned")
    else:
        # Create Wiki Posts - DONE
        which_user.profile.create_wiki_posts = False
        # Answer Protect Questions - DONE
        which_user.profile.remove_new_user_restrictions = False
        which_user.profile.save()

    # If user's reputation is more than 15 then Award Vote Up privilege.
    if totalReputation >= 15:
        which_user.profile.voteUpPriv = True
        which_user.profile.flag_posts = True
        PrivRepNotification.objects.get_or_create(
            for_user=which_user,
            privilegeURL="#",
            for_if="Up Vote",
            type_of_PrivNotify="Privilege_Earned"
        )
        which_user.profile.save()
    else:
        which_user.profile.voteUpPriv = False
        which_user.profile.flag_posts = False
        which_user.profile.save()

    # If user's reputation is more than 15 then Award Comment Everywhere privilege.
    if totalReputation >= 50:
        # Comment EveryWhere - DONE
        which_user.profile.comment_everywhere_Priv = True
        PrivRepNotification.objects.get_or_create(
            for_user=which_user,
            privilegeURL="#",
            for_if="Comment Everywhere",
            type_of_PrivNotify="Privilege_Earned"
        )
        which_user.profile.save()
    else:
        # Comment EveryWhere - DONE
        which_user.profile.comment_everywhere_Priv = False
        which_user.profile.save()

    if totalReputation >= 75:
        # Set Bounties - DONE
        which_user.profile.set_bounties = True
        PrivRepNotification.objects.get_or_create(
            for_user=which_user,
            privilegeURL="#",
            for_if="Set Bounties",
            type_of_PrivNotify="Privilege_Earned"
        )
        which_user.profile.save()
    else:
        # Set Bounties - DONE
        which_user.profile.set_bounties = False
        which_user.profile.save()

    if totalReputation >= 125:
        # Vote Down - DONE
        which_user.profile.voteDownPriv = True
        PrivRepNotification.objects.get_or_create(
            for_user=which_user,
            privilegeURL="#",
            for_if="Vote Down",
            type_of_PrivNotify="Privilege_Earned"
        )
        which_user.profile.save()
    else:
        # Vote Down - DONE
        which_user.profile.voteDownPriv = False
        which_user.profile.save()

    if totalReputation >= 250:
        which_user.profile.view_close_votes_Priv = True
        PrivRepNotification.objects.get_or_create(
            for_user=which_user,
            privilegeURL="#",
            for_if="View Close Votes",
            type_of_PrivNotify="Privilege_Earned"
        )
        which_user.profile.save()
    else:
        which_user.profile.view_close_votes_Priv = False
        which_user.profile.save()

    if totalReputation >= 500:
        which_user.profile.access_review_queues = True
        PrivRepNotification.objects.get_or_create(
            for_user=which_user,
            privilegeURL="#",
            for_if="Access Review Queues",
            type_of_PrivNotify="Privilege_Earned"
        )
        which_user.profile.save()
    else:
        which_user.profile.access_review_queues = False
        which_user.profile.save()

    if totalReputation >= 1000:
        which_user.profile.established_user_Priv = True
        PrivRepNotification.objects.get_or_create(
            for_user=which_user,
            privilegeURL="#",
            for_if="Established User",
            type_of_PrivNotify="Privilege_Earned"
        )
        which_user.profile.save()
    else:
        which_user.profile.established_user_Priv = False
        which_user.profile.save()

    if totalReputation >= 1500:
        which_user.profile.create_tags = True
        PrivRepNotification.objects.get_or_create(
            for_user=which_user,
            privilegeURL="#",
            for_if="Create Tags",
            type_of_PrivNotify="Privilege_Earned"
        )
        which_user.profile.save()
    else:
        which_user.profile.create_tags = False
        which_user.profile.save()

    if totalReputation >= 2000:
        which_user.profile.edit_questions_answers = True
        PrivRepNotification.objects.get_or_create(
            for_user=which_user,
            privilegeURL="#",
            for_if="Edit Question and Answers",
            type_of_PrivNotify="Privilege_Earned"
        )
        which_user.profile.save()
    else:
        which_user.profile.edit_questions_answers = False
        which_user.profile.save()

    if totalReputation >= 10000:
        which_user.profile.accessTo_moderatorTools = True
        PrivRepNotification.objects.get_or_create(
            for_user=which_user,
            privilegeURL="#",
            for_if="Access to Moderator Tools",
            type_of_PrivNotify="Privilege_Earned"
        )
        which_user.profile.save()
    else:
        which_user.profile.accessTo_moderatorTools = False
        which_user.profile.save()

    if totalReputation >= 15000:
        which_user.profile.protect_questions = True
        PrivRepNotification.objects.get_or_create(
            for_user=which_user,
            privilegeURL="#",
            for_if="Protect Questions",
            type_of_PrivNotify="Privilege_Earned"
        )
        which_user.profile.save()
    else:
        which_user.profile.protect_questions = False
        which_user.profile.save()

    if totalReputation >= 20000:
        which_user.profile.trusted_user_Priv = True
        PrivRepNotification.objects.get_or_create(
            for_user=which_user,
            privilegeURL="#",
            for_if="Trusted User",
            type_of_PrivNotify="Privilege_Earned"
        )
        which_user.profile.save()
    else:
        which_user.profile.trusted_user_Priv = False
        which_user.profile.save()

    return HttpResponse(status=202)


def save_comment(request, question_id):
    """
    For save the comment on question through Ajax
    and award user if eligible
    """
    if request.method == 'POST':
        if request.user.profile.comment_everywhere_Priv:
            comment = request.POST['comment']
            que = Question.objects.get(pk=question_id)
            question_URL = request.build_absolute_uri(que.get_absolute_url())
            commented_by = request.user
            getComments = CommentQ.objects.filter(
                commented_by=request.user).count()
            if getComments >= 10:
                # createTag = Tag.objects.get_or_create(name="Commentator")
                TagBadge.objects.get_or_create(
                    awarded_to_user=commented_by,
                    badge_type="SILVER",
                    tag_name="Commentator",
                    bade_position="BADGE")
                PrivRepNotification.objects.get_or_create(
                    for_user=commented_by,
                    url=question_URL,
                    type_of_PrivNotify="BADGE_EARNED",
                    for_if="Commentator",
                    description="Leave 10 comments"
                )

            if comment != "":
                createdComment = CommentQ.objects.create(
                    question_comment=que, comment=comment, commented_by=commented_by)
                if request.user != que.post_owner:
                    Notification.objects.create(
                        noti_receiver=que.post_owner,
                        type_of_noti="question_comment",
                        url=question_URL,
                        question_noti=que)

                # It is getting comment's body then it is finding "@" in the comment-
                # body and splitting all the other spaces, commas, brackets, etc.
                # Then after it successfully got the name after @ like @xyz,
                # then it will look if user with that username is exists or not
                # and if exists then it will notify the user and if not it will
                # print error of User.DoesNotExist.

                getCommentBody = createdComment.comment

                # Reference link of .find - https://docs.python.org/3/library/stdtypes.html#str.find
                # Refrence link of split() -
                # https://python-reference.readthedocs.io/en/latest/docs/str/split.html#example-1
                user = getCommentBody[getCommentBody.find("@") + 1:].split()[0]

                # Refrence link of re.split -
                # https://docs.python.org/3/library/re.html#re.split
                splitIt = re.split(",(?=(?:[^']*\'[^']*\')*[^']*$)", user)
                newWord = listTOString(splitIt)

                # Reference link of ObjectDoesNotExist -
                # https://docs.djangoproject.com/en/4.0/ref/exceptions/#objectdoesnotexist
                if "@" in getCommentBody:
                    try:
                        User.objects.get(username=newWord)
                        getUserIdByUsername = User.objects.get(
                            username=newWord)
                        question_URL = request.build_absolute_uri(
                            que.get_absolute_url())
                        send_BLANK_notification = Notification.objects.create(
                            noti_receiver=getUserIdByUsername,
                            type_of_noti="BLANK_NOTIFICATION",
                            url=question_URL,
                            question_noti=que)
                        print(getUserIdByUsername)

                    except User.DoesNotExist:
                        print(
                            "No User Found with mentioned username " +
                            newWord +
                            " in comment " +
                            createdComment.comment)

                return JsonResponse({'bool': True})
            else:
                return JsonResponse({'bool': False})
        else:
            return JsonResponse(
                {'action': "Need atleast 50 Reputation to Comment"})


def load_question_upvotes_downvotes(request, question_id):
    getQuestion = get_object_or_404(Question, pk=question_id)

    serialized_votes = []
    serialized_votes.append({
            'upvotes': getQuestion.qupvote_set.all().count(),
            'downvotes': getQuestion.qdownvote_set.all().count(),
        })

    return JsonResponse({'results':serialized_votes})


def load_answer_upvotes_downvotes(request, answer_id):
    getAnswer = get_object_or_404(Answer, pk=answer_id)

    serialized_votes = []
    serialized_votes.append({
            'upvotes': getAnswer.a_vote_ups.all().count(),
            'downvotes': getAnswer.a_vote_downs.all().count(),
        })

    return JsonResponse({'results': serialized_votes})

def Ajax_searchUser_Moderators(request):
    q = request.GET.get('q')
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

    return JsonResponse({'results': serialized_results})


def questionTimeline(request, question_id):
    """
    view for get the question's answer, comment, upvote, downvote and edit history
    exactly like timeline.
    """
    data = get_object_or_404(Question, id=question_id)
    answers_of_questions = data.answer_set.all()

    get_comments = list(CommentQ.objects.filter(question_comment=data))

    get_answers = list(Answer.objects.filter(questionans=data))

    get_bounty = list(Bounty.objects.filter(question_bounty=data))

    get_upvote = list(QUpvote.objects.filter(upvote_question_of=data))

    get_downvote = list(QDownvote.objects.filter(downvote_question_of=data))

    edit_history = list(QuestionEditVotes.objects.filter(edited_question=data))

    def ordering(obj):
        try:
            return obj.date
        except AttributeError:
            return obj.edited_suggested_at

    results = sorted(
        chain(
            get_comments,
            get_answers,
            get_bounty,
            get_upvote,
            get_downvote,
            edit_history),
        key=ordering,
        reverse=True)

    page = request.GET.get('page', 1)

    paginator = Paginator(results, 20)
    try:
        paginated_timeline = paginator.page(page)
    except PageNotAnInteger:
        paginated_timeline = paginator.page(1)
    except EmptyPage:
        paginated_timeline = paginator.page(paginator.num_pages)

    countEvents = len(paginated_timeline)

    context = {
        'data': data,
        'paginated_timeline': paginated_timeline,
        'results': results,
        'countEvents': countEvents,
    }
    return render(request, 'qa/TimeLineQuestion.html', context)


def answerTimeline(request, answer_id):
    """
    view for get the answer's history
    exactly like timeline.
    """
    post_answer = Answer.objects.filter(anshis=answer_id)
    data = get_object_or_404(Answer, id=answer_id)

    for dat in post_answer:
        for s in dat.anshis.all():
            print(s.next_record)

# Comment

    get_comments = list(CommentQ.objects.filter(answer_comment=data))
    edit_history = list(QuestionEditVotes.objects.filter(edited_answer=data))

# AnswerEdit

    def ordering(obj):
        try:
            return obj.date
        except AttributeError:
            return obj.edited_suggested_at

    results = sorted(
        chain(
            get_comments,
            edit_history),
        key=ordering,
        reverse=True)

    page = request.GET.get('page', 1)

    paginator = Paginator(results, 20)
    try:
        paginated_timeline = paginator.page(page)
    except PageNotAnInteger:
        paginated_timeline = paginator.page(1)
    except EmptyPage:
        paginated_timeline = paginator.page(paginator.num_pages)

    countEvents = len(paginated_timeline)

    context = {
        'data': data,
        'post_answer': post_answer,
        'paginated_timeline': paginated_timeline,
        'countEvents': countEvents,
    }
    return render(request, 'qa/TimeLineAnswer.html', context)


def end_bounty_thread(id):
    time.sleep(10000)
    createInstance = Bounty.objects.get(pk=id)
    createInstance.question_bounty.is_bountied = False
    # createInstance.save()
    createInstance.question_bounty.save()
    print(createInstance.question_bounty.is_bountied)
    print("Task Successfully Completed " +
          " Bounty of a Question is Successfully Removed")


def AjaxFlagForm(request, question_id):
    """
    Ajax form to submit Question's Flag
    """
    data = get_object_or_404(Question, pk=question_id)

    getCreateFlag_object = FlagPost.objects.filter(
        question_forFlag=data).exclude(
        ended=True).first()

    if request.method == 'POST':
        Flag_Form = FlagQuestionForm(data=request.POST)
        if Flag_Form.is_valid():
            new_post = Flag_Form.save(commit=False)
            formData = Flag_Form.cleaned_data['actions_Flag_Q']

            if request.user.profile.flag_posts:
                if formData == "SPAM" or formData == "RUDE_OR_ABUSIVE":
                    getCreateFlag_object = FlagPost.objects.filter(question_forFlag=data).filter(
                        Q(actions_Flag_Q="SPAM") | Q(actions_Flag_Q="RUDE_OR_ABUSIVE")).exclude(ended=True).first()
                    if getCreateFlag_object:
                        print("First Statement is Excecuting")
                        new_post.flagged_by = request.user
                        new_post.question_forFlag = data
                        new_post.save()
                        getCreateFlag_object.how_many_votes_on_spamANDRude += 1
                        getCreateFlag_object.save()
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Citizen Patrol",
                            bade_position="BADGE",
                            questionIf_TagOf_Q=data)
                        # return redirect('qa:questionDetailView', pk=data.id)
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            url="#",
                            type_of_PrivNotify="BADGE_EARNED",
                            for_if="Citizen Patrol",
                            description="First flagged post"
                        )

                    else:
                        print("Second Statement is Excecuting")
                        new_post.flagged_by = request.user
                        new_post.question_forFlag = data
                        new_post.how_many_votes_on_spamANDRude += 1
                        new_post.save()
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Citizen Patrol",
                            bade_position="BADGE")
                        # createReviewInstance,created = ReviewFlagPost.objects.get_or_create(flag_question_to_view=data)
                        # createReviewInstance.flag_reviewed_by.add(request.user)
                        # return redirect('qa:questionDetailView', pk=data.id)
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            url="#",
                            type_of_PrivNotify="BADGE_EARNED",
                            for_if="Citizen Patrol",
                            description="First flagged post"
                        )

                elif formData == "VERY_LOW_QUALITY":
                    getCreateFlag_object = FlagPost.objects.filter(
                        question_forFlag=data,
                        actions_Flag_Q="VERY_LOW_QUALITY").exclude(
                        ended=True).first()
                    if getCreateFlag_object:
                        print("Third Statement is Excecuting")
                        new_post.flagged_by = request.user
                        new_post.question_forFlag = data
                        new_post.save()
                        # getCreateFlag_object.how_many_votes_on_notAnAnswer += 1
                        getCreateFlag_object.save()
                        # createReviewInstance,created = ReviewFlagPost.objects.get_or_create(flag_question_to_view=data, flag_of=new_post)
                        # createReviewInstance.flag_reviewed_by.add(request.user)
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Citizen Patrol",
                            bade_position="BADGE")
                        create_Low_Quality_Post_Instance, cre = LowQualityPostsCheck.objects.get_or_create(
                            suggested_by=request.user, low_is=data, why_low_quality="Very Low Quality", suggested_through="User")
                        createLowQualityReviewInstance = ReviewLowQualityPosts.objects.get_or_create(
                            review_of=create_Low_Quality_Post_Instance, is_question=data)
                        # return redirect('qa:questionDetailView', pk=data.id)
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            url="#",
                            type_of_PrivNotify="BADGE_EARNED",
                            for_if="Citizen Patrol",
                            description="First flagged post"
                        )

                    else:
                        print("Fourth Statement is Excecuting")
                        new_post.flagged_by = request.user
                        new_post.question_forFlag = data
                        # new_post.how_many_votes_on_notAnAnswer += 1
                        new_post.save()
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Citizen Patrol",
                            bade_position="BADGE")
                        create_Low_Quality_Post_Instance, cre = LowQualityPostsCheck.objects.get_or_create(
                            suggested_by=request.user, low_is=data, why_low_quality="Very Low Quality", suggested_through="User")
                        ReviewLowQualityPosts.objects.get_or_create(
                            review_of=create_Low_Quality_Post_Instance, is_question=data)
                        # createReviewInstance,created = ReviewFlagPost.objects.get_or_create(flag_question_to_view=data, flag_of=new_post)
                        # createReviewInstance.flag_reviewed_by.add(request.user)
                        # return redirect('qa:questionDetailView', pk=data.id)

                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            url="#",
                            type_of_PrivNotify="BADGE_EARNED",
                            for_if="Citizen Patrol",
                            description="First flagged post"
                        )

                elif formData == "IN_NEED_OF_MODERATOR_INTERVATION" or formData == "ABOUT_PROFESSIONAL":
                    getCreateFlag_object = FlagPost.objects.filter(
                        question_forFlag=data).filter(
                        Q(
                            actions_Flag_Q="IN_NEED_OF_MODERATOR_INTERVATION") | Q(
                            actions_Flag_Q="ABOUT_PROFESSIONAL")).exclude(
                        ended=True).first()
                    if getCreateFlag_object:
                        messages.error(
                            request, 'Previous Flag is Waiting for Review')
                    else:
                        new_post.flagged_by = request.user
                        new_post.question_forFlag = data
                        new_post.save()
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Citizen Patrol",
                            bade_position="BADGE")
                        createReviewInstance, created = ReviewFlagPost.objects.get_or_create(
                            flag_question_to_view=data, flag_of=new_post)
                        createReviewInstance.flag_reviewed_by = request.user
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            url="#",
                            type_of_PrivNotify="BADGE_EARNED",
                            for_if="Citizen Patrol",
                            description="First flagged post"
                        )

                # elif formData == "DUPLICATE" or formData == "OPINION_BASED"
                # or formData == "NEED_MORE_FOCUS" or formData ==
                # "NEED_ADDITIONAL_DETAILS" or formData == "NEED_DEBUGGING" or
                # formData == "NOT_REPRODUCIBLE" or formData ==
                # "BLANTANLTY_OR_CLARITY" or formData ==
                # "SEEKING_RECCOMENDATIONS" or:
                else:
                    # print("This Statement is Excecuting")
                    getCreateFlag_object = FlagPost.objects.filter(
                        question_forFlag=data).filter(
                        Q(
                            actions_Flag_Q="DUPLICATE") | Q(
                            actions_Flag_Q="OPINION_BASED") | Q(
                            actions_Flag_Q="NEED_MORE_FOCUS") | Q(
                            actions_Flag_Q="NEED_ADDITIONAL_DETAILS") | Q(
                            actions_Flag_Q="NEED_DEBUGGING") | Q(
                                actions_Flag_Q="NOT_REPRODUCIBLE") | Q(
                                    actions_Flag_Q="BLANTANLTY_OR_CLARITY") | Q(
                                        actions_Flag_Q="ABOUT_GENERAL_COMPUTING_HAR")).exclude(
                                            ended=True).first()
                    if getCreateFlag_object:
                        print("Last Second Statement is Excecuting")
                        new_post.flagged_by = request.user
                        new_post.question_forFlag = data

                        createLowInstance, cre = CloseQuestionVotes.objects.get_or_create(
                            user=request.user, question_to_closing=data, why_closing="Duplicate", ended=False)
                        # getInstanceNow = CloseQuestionVotes.objects.filter(id=createLowInstance)
                        print(createLowInstance.id)
                        createInstance, created = ReviewCloseVotes.objects.get_or_create(
                            question_to_closed=data)
                        createInstance.review_of = createLowInstance
                        createInstance.save()

                        new_post.save()
                        getCreateFlag_object.how_many_votes_on_others += 1
                        getCreateFlag_object.save()
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Citizen Patrol",
                            bade_position="BADGE")
                        createReviewInstance, created = ReviewFlagPost.objects.get_or_create(
                            flag_question_to_view=data)
                        createReviewInstance.flag_reviewed_by = request.user
                        # createInstance.review_of = createLowInstance
                        # return redirect('qa:questionDetailView', pk=data.id)
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            url="#",
                            type_of_PrivNotify="BADGE_EARNED",
                            for_if="Citizen Patrol",
                            description="First flagged post"
                        )

                    else:
                        print("Last Statement is Excecuting")
                        new_post.flagged_by = request.user
                        new_post.question_forFlag = data
                        new_post.how_many_votes_on_others += 1
                        new_post.save()
                        createReviewInstance, created = ReviewFlagPost.objects.get_or_create(
                            flag_question_to_view=data)
                        createReviewInstance.flag_reviewed_by = request.user

                        create_Low_Quality_Post_Instance, cre = CloseQuestionVotes.objects.get_or_create(
                            user=request.user, question_to_closing=data, why_closing="Duplicate", ended=False)
                        createInstance, created = ReviewCloseVotes.objects.get_or_create(
                            question_to_closed=data)
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Citizen Patrol",
                            bade_position="BADGE")
                        createInstance.review_of = create_Low_Quality_Post_Instance
                        createInstance.save()
                        # return redirect('qa:questionDetailView', pk=data.id)
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            url="#",
                            type_of_PrivNotify="BADGE_EARNED",
                            for_if="Citizen Patrol",
                            description="First flagged post"
                        )

                # elif formData == "ABOUT_GENERAL_COMPUTING_HAR" or formData == "ABOUT_PROFESSIONAL":
                #         new_post.flagged_by = request.user
                #         new_post.question_forFlag = data
                #         new_post.save()

                # else:
                    # messages.error(request, "Response is Out Of Network")

                # new_post.user = request.user
                # new_post.question_forFlag = data
                # new_post.save()
                # return redirect('qa:questionDetailView', pk=data.id,)  #
                # slug=slug)
                ser_instance = serializers.serialize('json', [
                    new_post,
                ])
                # send to client side.
                return JsonResponse({"action": "saved"}, status=200)
            else:
                return JsonResponse({'action': "lackOfPrivelege"})
            # else:
                # return JsonResponse({"action": "cannotCreate"}, status=200)
        else:
            # some form errors occured.
            return JsonResponse({"error": Flag_Form.errors}, status=400)

    # errors occured (if occured)
    return JsonResponse({"error": ""}, status=400)


def flag_answer_ajax(request, answer_id):
    """
    Ajax form to submit Answer's Flag
    """
    getAnswer = get_object_or_404(Answer, pk=answer_id)

    if request.is_ajax and request.method == 'POST':
        Flag_Form = AnswerFlagForm(data=request.POST)
        if Flag_Form.is_valid():
            new_post = Flag_Form.save(commit=False)
            formData = Flag_Form.cleaned_data['actions_Flag_Q']

            if request.user.profile.flag_posts:
                if formData == "SPAM" or formData == "RUDE_OR_ABUSIVE":
                    getCreateFlag_object = FlagPost.objects.filter(answer_forFlag=getAnswer).filter(
                        Q(actions_Flag_Q="SPAM") | Q(actions_Flag_Q="RUDE_OR_ABUSIVE")).exclude(ended=True).first()
                    if getCreateFlag_object:
                        print("First Statement is Excecuting")
                        new_post.flagged_by = request.user
                        new_post.answer_forFlag = getAnswer
                        new_post.save()
                        getCreateFlag_object.how_many_votes_on_spamANDRude += 1
                        getCreateFlag_object.save()
                        getAllReviews = FlagPost.objects.filter(answer_forFlag=getAnswer).filter(
                            Q(actions_Flag_Q="SPAM") | Q(actions_Flag_Q="RUDE_OR_ABUSIVE")).exclude(ended=True)
                        if getCreateFlag_object.how_many_votes_on_spamANDRude >= 2:
                            for rev in getAllReviews:
                                rev.ended = True
                                rev.save()
                        # return redirect('profile:home')
                        # return redirect('qa:questionDetailView', pk=data.id)

                    else:
                        print("Second Statement is Excecuting")
                        new_post.flagged_by = request.user
                        new_post.answer_forFlag = getAnswer
                        new_post.how_many_votes_on_spamANDRude += 1
                        new_post.save()
                        getAllReviews = FlagPost.objects.filter(answer_forFlag=getAnswer).filter(
                            Q(actions_Flag_Q="SPAM") | Q(actions_Flag_Q="RUDE_OR_ABUSIVE")).exclude(ended=True)
                        if getCreateFlag_object.how_many_votes_on_spamANDRude >= 2:
                            for rev in getAllReviews:
                                rev.ended = True
                                rev.save()
                        # return redirect('profile:home')
                        # return redirect('qa:questionDetailView', pk=data.id)

                elif formData == "NOT_AN_ANSWER":
                    getCreateFlag_object = FlagPost.objects.filter(
                        answer_forFlag=getAnswer,
                        actions_Flag_Q="NOT_AN_ANSWER").exclude(
                        ended=True).first()
                    if getCreateFlag_object:
                        print("Third Statement is Excecuting")
                        new_post.flagged_by = request.user
                        new_post.answer_forFlag = getAnswer
                        new_post.save()
                        getCreateFlag_object.how_many_votes_on_notAnAnswer += 1
                        getCreateFlag_object.save()
                        create_Low_Quality_Post_Instance = LowQualityPostsCheck.objects.get_or_create(
                            suggested_by=request.user,
                            low_ans_is=getAnswer,
                            why_low_quality="Not an Answer",
                            suggested_through="User")
                        # return redirect('profile:home')
                        # return redirect('qa:questionDetailView', pk=data.id)

                        getAllReviews = FlagPost.objects.filter(
                            answer_forFlag=getAnswer,
                            actions_Flag_Q="NOT_AN_ANSWER").exclude(
                            ended=True)
                        if getCreateFlag_object.how_many_votes_on_spamANDRude >= 2:
                            for rev in getAllReviews:
                                rev.ended = True
                                rev.save()
                    else:
                        print("Fourth Statement is Excecuting")
                        new_post.flagged_by = request.user
                        new_post.answer_forFlag = getAnswer
                        new_post.how_many_votes_on_notAnAnswer += 1
                        new_post.save()
                        # return redirect('profile:home')
                        # return redirect('qa:questionDetailView', pk=data.id)
                        getAllReviews = FlagPost.objects.filter(
                            answer_forFlag=getAnswer,
                            actions_Flag_Q="NOT_AN_ANSWER").exclude(
                            ended=True)
                        if getCreateFlag_object.how_many_votes_on_spamANDRude >= 2:
                            for rev in getAllReviews:
                                rev.ended = True
                                rev.save()
                else:
                    getCreateFlag_object = FlagPost.objects.filter(
                        answer_forFlag=getAnswer).filter(
                        Q(
                            actions_Flag_Q="IN_NEED_OF_MODERATOR_INTERVATION") | Q(
                            actions_Flag_Q="ABOUT_PROFESSIONAL")).exclude(
                        ended=True).first()
                    if getCreateFlag_object:
                        messages.error(
                            request, 'Previous Flag is Waiting for Review')
                    else:
                        new_post.flagged_by = request.user
                        new_post.answer_forFlag = getAnswer
                        new_post.save()
                        createReviewInstance, created = ReviewFlagPost.objects.get_or_create(
                            flag_answer_to_view_if=getAnswer, flag_of=new_post)
                        createReviewInstance.flag_reviewed_by = request.user
                        createReviewInstance.save()
                        getAllReviews = FlagPost.objects.filter(
                            answer_forFlag=getAnswer).filter(
                            Q(
                                actions_Flag_Q="IN_NEED_OF_MODERATOR_INTERVATION") | Q(
                                actions_Flag_Q="ABOUT_PROFESSIONAL")).exclude(
                            ended=True)
                        if getCreateFlag_object.how_many_votes_on_spamANDRude >= 2:
                            for rev in getAllReviews:
                                rev.ended = True
                                rev.save()
                ser_instance = serializers.serialize('json', [
                    new_post,
                ])
                # send to client side.
                return JsonResponse({"action": "saved"}, status=200)
            else:
                return JsonResponse({'action': "lackOfPrivelege"})
            # else:
                # return JsonResponse({"action": "cannotCreate"}, status=200)
        else:
            # some form errors occured.
            return JsonResponse({"error": Flag_Form.errors}, status=400)

    # some error occured
    return JsonResponse({"error": ""}, status=400)


def AjaxBountyForm(request, question_id):
    """
    Ajax form to save Bounty of question.
    """
    data = get_object_or_404(Question, pk=question_id)

    if request.is_ajax and request.method == 'POST':
        bounty_form = BountyForm(data=request.POST)
        if bounty_form.is_valid():
            if request.user.profile.set_bounties:
                formCleanedData = bounty_form.cleaned_data['bounty_value']
                print(formCleanedData)
                # created = False
                new_post = bounty_form.save(commit=False)
                new_post.by_user = request.user
                new_post.question_bounty = data
                data.limit_exced = True
                data.is_bountied = True
                data.bounty_date_announced = timezone.now()
    # ! Invenstor Badge - First Bounty i manually Declare on another person's Q
                if data.post_owner != request.user:
                    # request.user.profile.investor_B = True
                    # request.user.profile.save()
                    TagBadge.objects.get_or_create(
                        awarded_to_user=request.user,
                        badge_type="BRONZE",
                        tag_name="Investor",
                        bade_position="BADGE",
                        questionIf_TagOf_Q=data)

                    if formCleanedData == "50":
                        Reputation.objects.create(
                            question_O=data,
                            question_rep_C=-50,
                            awarded_to=request.user,
                            reputation_on_what='Applied_Bounty')
                    elif formCleanedData == "100":
                        Reputation.objects.create(
                            question_O=data,
                            question_rep_C=-100,
                            awarded_to=request.user,
                            reputation_on_what='Applied_Bounty')
                    elif formCleanedData == "150":
                        Reputation.objects.create(
                            question_O=data,
                            question_rep_C=-150,
                            awarded_to=request.user,
                            reputation_on_what='Applied_Bounty')
                    elif formCleanedData == "200":
                        Reputation.objects.create(
                            question_O=data,
                            question_rep_C=-200,
                            awarded_to=request.user,
                            reputation_on_what='Applied_Bounty')
                    elif formCleanedData == "250":
                        Reputation.objects.create(
                            question_O=data,
                            question_rep_C=-250,
                            awarded_to=request.user,
                            reputation_on_what='Applied_Bounty')
                    elif formCleanedData == "300":
                        Reputation.objects.create(
                            question_O=data,
                            question_rep_C=-300,
                            awarded_to=request.user,
                            reputation_on_what='Applied_Bounty')
                    elif formCleanedData == "350":
                        Reputation.objects.create(
                            question_O=data,
                            question_rep_C=-350,
                            awarded_to=request.user,
                            reputation_on_what='Applied_Bounty')
                    elif formCleanedData == "400":
                        Reputation.objects.create(
                            question_O=data,
                            question_rep_C=-400,
                            awarded_to=request.user,
                            reputation_on_what='Applied_Bounty')
                    elif formCleanedData == "450":
                        Reputation.objects.create(
                            question_O=data,
                            question_rep_C=-450,
                            awarded_to=request.user,
                            reputation_on_what='Applied_Bounty')
                    elif formCleanedData == "500":
                        Reputation.objects.create(
                            question_O=data,
                            question_rep_C=-500,
                            awarded_to=request.user,
                            reputation_on_what='Applied_Bounty')

                    # UNCOMMENT IT. IT WORKED - ONLY ONE LINE
                    # Bronze_TagBadge.objects.get_or_create(awarded_to=request.user, badge_type="Bronze", tag_name="investor-badge")
    # ! Promoter Badge - First Bounty i manually Declare on my Q

                else:
                    # UNCOMMENT IT. IT WORKED - ONLY ONE LINE
                    # Bronze_TagBadge.objects.get_or_create(awarded_to=request.user, badge_type="Bronze", tag_name="promoter-badge")
                    # createTag = Tag.objects.get_or_create(name="Promoter Badge")
                    TagBadge.objects.get_or_create(
                        awarded_to_user=request.user,
                        badge_type="BRONZE",
                        tag_name="Promoter",
                        bade_position="BADGE",
                        questionIf_TagOf_Q=data)
                    # request.user.profile.save()

                    if formCleanedData == "50":
                        Reputation.objects.create(
                            question_O=data,
                            question_rep_C=-50,
                            awarded_to=request.user,
                            reputation_on_what='Applied_Bounty')
                    elif formCleanedData == "100":
                        Reputation.objects.create(
                            question_O=data,
                            question_rep_C=-100,
                            awarded_to=request.user,
                            reputation_on_what='Applied_Bounty')
                    elif formCleanedData == "150":
                        Reputation.objects.create(
                            question_O=data,
                            question_rep_C=-150,
                            awarded_to=request.user,
                            reputation_on_what='Applied_Bounty')
                    elif formCleanedData == "200":
                        Reputation.objects.create(
                            question_O=data,
                            question_rep_C=-200,
                            awarded_to=request.user,
                            reputation_on_what='Applied_Bounty')
                    elif formCleanedData == "250":
                        Reputation.objects.create(
                            question_O=data,
                            question_rep_C=-250,
                            awarded_to=request.user,
                            reputation_on_what='Applied_Bounty')
                    elif formCleanedData == "300":
                        Reputation.objects.create(
                            question_O=data,
                            question_rep_C=-300,
                            awarded_to=request.user,
                            reputation_on_what='Applied_Bounty')
                    elif formCleanedData == "350":
                        Reputation.objects.create(
                            question_O=data,
                            question_rep_C=-350,
                            awarded_to=request.user,
                            reputation_on_what='Applied_Bounty')
                    elif formCleanedData == "400":
                        Reputation.objects.create(
                            question_O=data,
                            question_rep_C=-400,
                            awarded_to=request.user,
                            reputation_on_what='Applied_Bounty')
                    elif formCleanedData == "450":
                        Reputation.objects.create(
                            question_O=data,
                            question_rep_C=-450,
                            awarded_to=request.user,
                            reputation_on_what='Applied_Bounty')
                    elif formCleanedData == "500":
                        Reputation.objects.create(
                            question_O=data,
                            question_rep_C=-500,
                            awarded_to=request.user,
                            reputation_on_what='Applied_Bounty')

                # Save the thread with its ID.
                new_post.save()
                data.save()
                t = threading.Thread(
                    target=end_bounty_thread, args=[
                        new_post.id])
                t.setDaemon(True)
                t.start()

                # messages.success(request, "Successfully Applied Bounty")
                # return redirect('qa:questionDetailView', pk=data.id,)  #
                # slug=slug)

                ser_instance = serializers.serialize('json', [
                    new_post,
                ])
                # send to client side.
                return JsonResponse({"action": "saved"}, status=200)
            else:
                return JsonResponse({'action': "lackOfPrivelege"})
        else:
            return JsonResponse({"error": bounty_form.errors}, status=400)

    return JsonResponse({"error": ""}, status=400)

# Under Construction - Need Improvement


def getCommunityWikiAnswerDetails(request, answer_id):
    """
    Edit history of answer, if answer is part of Community Wiki
    """
    post = get_object_or_404(Answer, pk=answer_id)

    historyDate = post.anshis

    # getAllHistoryUsers = post.anshis.history_user

    for s in historyDate.all():
        print(s.history_user)

    countAllTheEditors = post.anshis.aggregate(countAll=Count('history_user'))
    print(countAllTheEditors)
    # for s in countAllTheEditors:
    #     k = s['history_user']
    #     print(k)

    context = {'post': post, 'historyDate': historyDate,
               'countAllTheEditors': countAllTheEditors, }
    return render(request, 'qa/communityWikiPostDtls.html', context)


def ProtectQuestionAjax(request, question_id):
    """
    Form to Protect Question using Ajax.
    """
    data = get_object_or_404(Question, pk=question_id)

    if request.is_ajax and request.method == 'POST':
        protectForm = ProtectForm(data=request.POST)
        if protectForm.is_valid():
            if request.user.profile.protect_questions:
                new_post = protectForm.save(commit=False)
                new_post.protected_by = request.user
                new_post.protectionRemovedBy = request.user
                new_post.protecting_question = data
                new_post.stillProtected = True
                data.is_protected = True
                data.save()
                new_post.save()

                ser_instance = serializers.serialize('json', [
                    new_post,
                ])
                # send to client side.
                return JsonResponse({"action": "formSaved"}, status=200)
            else:
                return JsonResponse({'action': "lackOfPrivelege"})
            # else:
                # return JsonResponse({"action": "cannotCreate"}, status=200)
        else:
            return JsonResponse({"error": protectForm.errors}, status=400)

    return JsonResponse({"error": ""}, status=400)


def ReOpenVotesAjax(request, question_id):
    """
    Form to save ReOpen Closed Question votes using Ajax
    """
    data = get_object_or_404(Question, pk=question_id)

# QUESTION RE-OPEN FORM - START

    getCreatedObject = ReOpenQuestionVotes.objects.filter(
        question_to_opening=data).exclude(ended=True).first()
    get_LIVE_Reviwing_object = ReviewQuestionReOpenVotes.objects.filter(
        question_opened=data).exclude(is_completed=True).first()

# TAGGING - START
    winned_gold_tags = TagBadge.objects.filter(
        awarded_to_user=request.user, badge_type="GOLD")
# TAGGING - END

    if request.is_ajax and request.method == 'POST':
        re_open_form = VoteToReOpenForm(data=request.POST)
        if re_open_form.is_valid():
            new_post = re_open_form.save(commit=False)
            formData = re_open_form.cleaned_data['why_opening']
            print(formData)

            if request.user.profile.cast_close_AND_Reopen_votes:

                # USER WITH GOLDEN BADGE IS TRYING TO REOPEN A QUESTION THEN NO
                # REVIEW WILL BE REQUIRED
                if winned_gold_tags:
                    for s in winned_gold_tags:
                        if s.tag_name in data.tags.all().values_list('name', flat=True):
                            new_post.user = request.user
                            new_post.question_to_opening = data
                            # print("First First Statement is Excecuting in ReOpen")
                            # print("Golden Badge's User is ReOpening")
                            # createInstance, created = ReviewQuestionReOpenVotes.objects.get_or_create(question_opened=data, is_completed=False)
                            # createInstance.reopen_reviewed_by.add(request.user)
                            # get_LIVE_Reviwing_object.reopen_reviewed_by.add(request.user)
                            # getCreatedObject.how_many_votes_on_Open += 1
                            # getCreatedObject.save()
                            new_post.question_to_opening.is_closed = False
                            data.save()
                            new_post.save()

                        elif getCreatedObject:
                            if formData == getCreatedObject.why_opening:
                                new_post.user = request.user
                                new_post.question_to_opening = data
                                # print("First Statement is Excecuting in ReOpen")
                                # createInstance, created = ReviewQuestionReOpenVotes.objects.get_or_create(question_opened=data, is_completed=False)
                                # new_post.how_many_votes_on_Open += 1
                                getCreatedObject.how_many_votes_on_Open += 1
                                getCreatedObject.save()
                                new_post.save()
                                if get_LIVE_Reviwing_object:
                                    get_LIVE_Reviwing_object.reopen_reviewed_by.add(
                                        request.user)
                            else:
                                print("This")
                                new_post.user = request.user
                                new_post.question_to_opening = data
                                # print("Second Statement is Excecuting in ReOpen")
                                createInstance, created = ReviewQuestionReOpenVotes.objects.get_or_create(
                                    question_opened=data, is_completed=False)
                                createInstance.reopen_reviewed_by.add(
                                    request.user)
                                # get_LIVE_Reviwing_object.reopen_reviewed_by.add(request.user)
                                getCreatedObject.how_many_votes_on_Open += 1
                                getCreatedObject.save()
                                new_post.save()
                                createInstance.review_of = new_post
                                createInstance.save()
                        else:
                            new_post.user = request.user
                            new_post.question_to_opening = data
                            # print("Third Statement is Excecuting in ReOpen")
                            createInstance, created = ReviewQuestionReOpenVotes.objects.get_or_create(
                                question_opened=data, is_completed=False)
                            createInstance.reopen_reviewed_by.add(request.user)
                            new_post.how_many_votes_on_Open += 1
                            # print("Instance Created")
                            new_post.save()
                            createInstance.review_of = new_post
                            createInstance.save()
                        ser_instance = serializers.serialize('json', [
                            new_post,
                        ])
                        # send to client side.
                        return JsonResponse({"action": "saved"}, status=200)
                        # return redirect('qa:questionDetailView', pk=data.id)
                else:
                    if getCreatedObject:
                        if formData == getCreatedObject.why_opening:
                            new_post.user = request.user
                            new_post.question_to_opening = data
                            # print("First Statement is Excecuting in ReOpen")
                            # createInstance, created = ReviewQuestionReOpenVotes.objects.get_or_create(question_opened=data, is_completed=False)
                            # new_post.how_many_votes_on_Open += 1
                            getCreatedObject.how_many_votes_on_Open += 1
                            getCreatedObject.save()
                            new_post.save()
                            if get_LIVE_Reviwing_object:
                                get_LIVE_Reviwing_object.reopen_reviewed_by.add(
                                    request.user)
                        else:
                            print("This")
                            new_post.user = request.user
                            new_post.question_to_opening = data
                            # print("Second Statement is Excecuting in ReOpen")
                            createInstance, created = ReviewQuestionReOpenVotes.objects.get_or_create(
                                question_opened=data, is_completed=False)
                            createInstance.reopen_reviewed_by.add(request.user)
                            # get_LIVE_Reviwing_object.reopen_reviewed_by.add(request.user)
                            getCreatedObject.how_many_votes_on_Open += 1
                            getCreatedObject.save()
                            new_post.save()
                            createInstance.review_of = new_post
                            createInstance.save()
                    else:
                        new_post.user = request.user
                        new_post.question_to_opening = data
                        # print("Third Statement is Excecuting in ReOpen")
                        createInstance, created = ReviewQuestionReOpenVotes.objects.get_or_create(
                            question_opened=data, is_completed=False)
                        createInstance.reopen_reviewed_by.add(request.user)
                        new_post.how_many_votes_on_Open += 1
                        # print("Instance Created")
                        new_post.save()
                        createInstance.review_of = new_post
                        createInstance.save()
                    # return redirect('qa:questionDetailView', pk=data.id)

                    ser_instance = serializers.serialize('json', [
                        new_post,
                    ])
                    # send to client side.
                    return JsonResponse({"action": "saved"}, status=200)

            else:
                return JsonResponse({'action': "lackOfPrivelege"})

        else:
            # some form errors occured.
            return JsonResponse({"error": re_open_form.errors}, status=400)

    return JsonResponse({"error": ""}, status=400)

# @cache_page(60 * 15)
def questionDetailView(request, pk,):  # slug):
    data = get_object_or_404(Question, pk=pk)
    answers_of_questions = data.answer_set.all().exclude(is_deleted=True)

    STORING_THE_ORIGINAL = []

    # If the last Answer's Edit is Approved then show the new edited answer but
    # if last answer's edit is rejected then show previous one
    for anss in answers_of_questions:
        getAnsHistory = anss.history.first()
        getLastEditVotes = QuestionEditVotes.objects.filter(
            edited_answer=anss).last()
        if getLastEditVotes:
            if getLastEditVotes.rev_Action == "Approve" and getLastEditVotes.is_completed or getLastEditVotes.rev_Action == "Approve_Through_Edit" and getLastEditVotes.is_completed:
                getTheOriginal = anss
                print("First Statement in Storing is Excecuting")
                STORING_THE_ORIGINAL.append(getTheOriginal)
            else:
                print("Second Statement in Storing is Excecuting")
                getTheOriginal = getAnsHistory.prev_record
                STORING_THE_ORIGINAL.append(getTheOriginal)
        else:
            getTheOriginal = anss
            STORING_THE_ORIGINAL.append(getTheOriginal)

    # Answer - Pagination - START
    page = request.GET.get('page', 1)

    paginator = Paginator(STORING_THE_ORIGINAL, 10)
    try:
        answers = paginator.page(page)
    except PageNotAnInteger:
        answers = paginator.page(1)
    except EmptyPage:
        answers = paginator.page(paginator.num_pages)
    # Answer - Pagination - END


# # Need to Review - START
#     if data.date < timezone.now() - timedelta(days=7) and data.viewers.count(
#     ) < 5 and data.commentq_set.all().count() < 1 and data.answer_set.all().count() < 1:
#         TagBadge.objects.get_or_create(
#             awarded_to_user=data.post_owner,
#             badge_type="GOLD",
#             tag_name="Great Answer",
#             bade_position="BADGE")
#         print("Answer is older")
# # Need to Review - END

    # answers_of_questions = Answer.objects.filter(questionans=data)
    # QUESTION BOOKMARKED BY WHOM
    bookmarks = Profile.objects.filter(bookmark_questions=data).count()
    # voted_time = data.date

    is_it_first = data.answer_set.first()
    if is_it_first:
        if is_it_first.a_vote_ups.all().count() >= 1 and is_it_first.accepted:
            TagBadge.objects.get_or_create(
                awarded_to_user=is_it_first.answer_owner,
                badge_type="SILVER",
                tag_name="Enlightened",
                bade_position="BADGE",
                answerIf_TagOf_A=is_it_first)

    countingActiveBounties = Question.objects.filter(limit_exced=True,
                                                     is_bountied=True).count()

# BOUNTY LIMIT SETTER - START
# (If bounty of the -data- Q is more than or equal to 3 then the Bounty-
# button will hide and it will show a message instead)
    # haveActiveBounties = Question.objects.filter(post_owner=request.user, is_bountied=True)
    if countingActiveBounties >= 3:
        cannot_create = True
    else:
        cannot_create = False
# BOUNTY LIMIT SETTER - END

    if_ans = Answer.objects.filter(questionans=data, accepted=True).count()
    if if_ans >= 1:
        is_it_acc = True
    else:
        is_it_acc = False

    # Answer Form - START
    if request.method == 'POST':
        form = AnswerForm(data=request.POST)
        if form.is_valid():
            gettingBody = form.cleaned_data['body']
            gettingWiki = form.cleaned_data['is_wiki_answer']

            if data.is_protected:
                if request.user.profile.remove_new_user_restrictions:
                    new_post = form.save(commit=False)
                    new_post.answer_owner = request.user
                    new_post.questionans = data
                    data.active_date = timezone.now()

                    data.save()
                    question_URL = request.build_absolute_uri(
                        data.get_absolute_url())

                    # if request.user != new_post.answer_owner:
                    Notification.objects.create(
                            noti_receiver=data.post_owner,
                            type_of_noti="NEW_ANSWER",
                            url=question_URL,
                            answer_noti=new_post)

                    if len(gettingBody) <= 200:
                        # print("Second Last Statement")
                        create_Low_Quality_Post_Instance, cre = LowQualityPostsCheck.objects.get_or_create(
                            suggested_through="Automatic", low_ans_is=new_post, why_low_quality="Answer_Less_Than_200", is_completed=False)
                        ReviewLowQualityPosts.objects.get_or_create(
                            review_of=create_Low_Quality_Post_Instance, is_answer=new_post, is_reviewed=False)
                    return redirect(
                        'qa:questionDetailView',
                        pk=data.id,
                    )  # slug=slug)
                else:
                    messages.error(
                        request,
                        'This Question is Protected and You need atleast 10 reputation to Answer it')
            else:
                new_post = form.save(commit=False)
                new_post.answer_owner = request.user
                new_post.questionans = data
                data.active_date = timezone.now()
                data.save()

                if data.qdownvote_set.all().count() >= 2:
                    new_post.monitor_it = True
                    new_post.save()
                    question_URL = request.build_absolute_uri(
                        data.get_absolute_url())
                    # if request.user != new_post.answer_owner:
                    Notification.objects.create(
                            noti_receiver=data.post_owner,
                            type_of_noti="NEW_ANSWER",
                            url=question_URL,
                            answer_noti=new_post)
                else:
                    print("Not Working")

                # WORKED
                # Revival Tag - START
                is_olderThan_nintyMinutes = timezone.now() - timedelta(days=30)
                # Can make a view to count all the Answers in Model
                # getAnswering = data.answer_set.all().count()
                if data.date <= is_olderThan_nintyMinutes:  # and getAnswering <= 0:
                    # print("Revival")
                    new_post.revival_stage_one = True
                    new_post.save()
                    question_URL = request.build_absolute_uri(
                        data.get_absolute_url())
                    # if request.user != new_post.answer_owner:
                    Notification.objects.create(
                            noti_receiver=data.post_owner,
                            type_of_noti="NEW_ANSWER",
                            url=question_URL,
                            answer_noti=new_post)
                # Revival Tag - START

                # WORKED
                is_older_sixty_days = timezone.now() - timedelta(days=60)
                if data.date <= is_older_sixty_days:
                    new_post.necromancer_check = True
                    new_post.save()
                    question_URL = request.build_absolute_uri(
                        data.get_absolute_url())
                    # if request.user != new_post.answer_owner:
                    Notification.objects.create(
                            noti_receiver=data.post_owner,
                            type_of_noti="NEW_ANSWER",
                            url=question_URL,
                            answer_noti=new_post)
                if gettingWiki and request.user.profile.create_wiki_posts == False:
                    new_post.is_wiki_answer = False
                    new_post.save()
                    question_URL = request.build_absolute_uri(
                        data.get_absolute_url())
                    # if request.user != new_post.answer_owner:
                    Notification.objects.create(
                            noti_receiver=data.post_owner,
                            type_of_noti="NEW_ANSWER",
                            url=question_URL,
                            answer_noti=new_post)
                    messages.error(
                        request, 'You need atleast 10 Reputation to this Answer into Wiki Posts')
                else:
                    # print("Main saving answer Statement is Excecuting")
                    new_post.save()
                    question_URL = request.build_absolute_uri(
                        data.get_absolute_url())
                    # if request.user != new_post.answer_owner:
                    Notification.objects.create(
                            noti_receiver=data.post_owner,
                            type_of_noti="NEW_ANSWER",
                            url=question_URL,
                            answer_noti=new_post)

                getEditingTime = request.user.profile.editPostTimeOfUser
                getRecentAnswer = Answer.objects.filter(
                    answer_owner=request.user).last()
                if getRecentAnswer and request.user.profile.editPostTimeOfUser:
                    if getEditingTime >= timezone.now() - \
                            timedelta(minutes=5) and getRecentAnswer.date >= timezone.now() - timedelta(minutes=5):
                        request.user.profile.Refiner_Illuminator_TagPostCounter += 1
                        request.user.profile.save()
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Explainer",
                            bade_position="BADGE",
                            questionIf_TagOf_Q=data)
                        print("Explainer Awarded")
                        if request.user.profile.Refiner_Illuminator_TagPostCounter >= 50:
                            TagBadge.objects.get_or_create(
                                awarded_to_user=request.user,
                                badge_type="SILVER",
                                tag_name="Refiner",
                                bade_position="BADGE",
                                questionIf_TagOf_Q=data)

                        if request.user.profile.Refiner_Illuminator_TagPostCounter >= 500:
                            TagBadge.objects.get_or_create(
                                awarded_to_user=request.user,
                                badge_type="GOLD",
                                tag_name="Illuminator",
                                bade_position="BADGE",
                                questionIf_TagOf_Q=data)

                if len(gettingBody) <= 200:
                    create_Low_Quality_Post_Instance, cre = LowQualityPostsCheck.objects.get_or_create(
                        suggested_through="Automatic", low_ans_is=new_post, why_low_quality="Answer_Less_Than_200", is_completed=False)
                    ReviewLowQualityPosts.objects.get_or_create(
                        review_of=create_Low_Quality_Post_Instance, is_answer=new_post, is_reviewed=False)
                return redirect(
                    'qa:questionDetailView',
                    pk=data.id,
                )  # slug=slug)
    else:
        form = AnswerForm()
    # Answer Form - END


# BOUNTY FORM - START
    if request.method == 'POST':
        bounty_form = BountyForm(data=request.POST)
    else:
        # new_post = new_post.id
        bounty_form = BountyForm()
# BOUNTY FORM - END


# Question Views
    queryset = Question.objects.annotate(
        num_views=Count('viewers')).order_by('-num_views')
    datas = get_object_or_404(queryset, pk=pk)
    if request.user.is_authenticated:
        created = Question.viewers.through.objects.get_or_create(
            question=datas, user=request.user)

        if created:
            datas.num_views += 0
# BADGE - POPULAR QUESTION - MORE THAN 1000 VIEWS.
        if datas.viewers.count() >= 1000:
            TagBadge.objects.get_or_create(
                awarded_to_user=data.post_owner,
                badge_type="BRONZE",
                tag_name="Popular Question",
                bade_position="BADGE")

# BADGE - POPULAR QUESTION - MORE THAN 2500 VIEWS.
        if datas.viewers.count() >= 2500:
            TagBadge.objects.get_or_create(
                awarded_to_user=data.post_owner,
                badge_type="SILVER",
                tag_name="Notable Question",
                bade_position="BADGE")

# BADGE - POPULAR QUESTION - MORE THAN 10000 VIEWS.
        if datas.viewers.count() >= 10000:
            TagBadge.objects.get_or_create(
                awarded_to_user=data.post_owner,
                badge_type="GOLD",
                tag_name="Famous Question",
                bade_position="BADGE")

# -------------


# CLOSING THE QUESTION - START
    getCreateClose_object = CloseQuestionVotes.objects.filter(
        question_to_closing=data).exclude(ended=True).first()
    getAll_Votes_required_in_close_and_completed = CloseQuestionVotes.objects.filter(
        question_to_closing=data).filter(Q(
            why_closing="NEED_TO_MORE_FOCUSED") | Q(
            why_closing="DUPLICATE") | Q(
            why_closing="NEED_ADDITIONAL_DETAILS") | Q(
            why_closing="OPINION_BASED") | Q(why_closing="Close"))

    getReviewingObject = ReviewCloseVotes.objects.filter(
        question_to_closed=data, is_completed=False)

    if getCreateClose_object and getCreateClose_object.how_many_votes_on_Close >= 3:
        for s in getAll_Votes_required_in_close_and_completed:
            s.ended = True
            s.save()
        data.is_closed = True
        data.save()
# CLOSING THE QUESTION - END


# Close Question Form - START
    if request.method == 'POST':
        close_form = CloseForm_Q(data=request.POST)
    else:
        close_form = CloseForm_Q()
# Close Question Form - END


# Flag Comment Form - START
    if request.method == 'POST':
        FlagCommentForm = CommentFlagForm(data=request.POST)
        if FlagCommentForm.is_valid():
            flagForm = FlagCommentForm.save(commit=False)
            # flagForm.comment_of = s
            flagForm.comment_flagged_by = request.user
            flagForm.save()
            return redirect('profile:questionDetailView', pk=data.id)
    else:
        FlagCommentForm = CommentFlagForm()
# Flag Comment Form - START


# Protect Question Form - START
    if request.method == 'POST':
        protectForm = ProtectForm(data=request.POST)
    else:
        protectForm = ProtectForm()
# Protect Question Form - END

    protectedQuestion = ProtectQuestion.objects.filter(
        protecting_question__is_protected=True, stillProtected=True)

    if request.user.is_authenticated:
        likepost = data.qupvote_set.filter(upvote_by_q=request.user).first()

        likeDownpost = data.qdownvote_set.filter(
            downvote_by_q=request.user).first()
    else:
        likepost = ''
        likeDownpost = ''

# -------------TAG- LifeJacket---------------------- START - WORKING -----

    getAnswers = data.answer_set.filter(monitor_it=True)
    for ans in getAnswers:
        if ans.a_vote_ups.count() >= 1 and data.qupvote_set.all().count() >= 2:
            # awardTheTag
            TagBadge.objects.get_or_create(
                awarded_to_user=data.post_owner,
                badge_type="SILVER",
                tag_name="Lifejacket",
                bade_position="BADGE",
                answerIf_TagOf_A=ans)

        if ans.a_vote_ups.count() >= 20 and data.qupvote_set.all().count() >= 3:
            TagBadge.objects.get_or_create(
                awarded_to_user=data.post_owner,
                badge_type="GOLD",
                tag_name="Lifeboat",
                bade_position="BADGE",
                answerIf_TagOf_A=ans)

# -------------TAG- LifeJacket---------------------- END - WORKING -------


# -------------TAG- Populist---------------------- START - WORKING --------------------- Needs Improvement

    getAcceptedAnswer = data.answer_set.filter(accepted=True).first()

    if getAcceptedAnswer is not None:
        getAcceptedAnswerCorrected = getAcceptedAnswer.a_vote_ups.count()
    else:
        getAcceptedAnswerCorrected = ''

    if getAcceptedAnswer is not None:
        multiplied = getAcceptedAnswerCorrected * 2 + 1
        print(multiplied)
        getAllTheAnswers_ofQuestion = data.answer_set.filter(
            a_vote_ups__gt=multiplied).exclude(accepted=True)
    else:
        getAllTheAnswers_ofQuestion = ''

    for s in getAllTheAnswers_ofQuestion:
        print(s.answer_owner)

# -------------TAG- Populist---------------------- END - WORKING --------------------- Needs Improvement

    # getHow_many_vote_on_close = CloseQuestionVotes.objects.filter(question_to_closing=data).annotate(num_count=Count('how_many_votes_on_Close'))

    getHow_many_vote_on_close = CloseQuestionVotes.objects.filter(
        question_to_closing=data).exclude(ended=True).count()

    if getHow_many_vote_on_close >= 1:
        showClose_Votes = True
    else:
        showClose_Votes = False


# if total close votes are 2 and third is having close then close the question AND if total leave_open question are 2 and third is leave_open
# then delete the review queue BUT closing will not delete
# if next review queue is close then close votes are 2 then close the question.


# DELETING THE LAST CLOSE VOTE IF VIEWS ARE LESS THAN 20 AND LAST VOTE IS
# OLDER THAN 5 DAYS - START
    getClose_votes_on_this_question = CloseQuestionVotes.objects.filter(
        question_to_closing=data).last()
    # # QUESTION - ALGORITHM
    if getClose_votes_on_this_question:
        if datas.viewers.all().count(
        ) >= 20 and getClose_votes_on_this_question.date <= timezone.now() - timedelta(days=5):
            print("Delete the Last Close Vote")
            CloseQuestionVotes.objects.filter(
                question_to_closing=data).last().delete()
    # elif datas.viewers.all().count() < 100 and get_last_close_votes is older_than_14_days:
    #     print("Delete the last Close Vote")
# DELETING THE LAST CLOSE VOTE IF VIEWS ARE LESS THAN _________ AND LAST
# VOTE IS OLDER THAN _________ DAYS - END

    get_Ended_With_2 = ReviewCloseVotes.objects.filter(
        question_to_closed=data).last()
    if get_Ended_With_2:
        get_Ended_With = get_Ended_With_2.finalResult
    else:
        get_Ended_With = ''

    if request.user.is_authenticated:
        getClose_votes = CloseQuestionVotes.objects.filter(
            user=request.user, question_to_closing=data)

        getVotes_casted_by_user = CloseQuestionVotes.objects.filter(
            user=request.user, question_to_closing=data).first()
    else:
        getClose_votes = ''
        getVotes_casted_by_user = ''

    if getClose_votes:
        # print("User is Voted for Close")
        can_user_vote_for_close = False
    else:
        can_user_vote_for_close = True
        # print("request.user haven't voted to Close")


# QUESTION RE-OPEN FORM - START

    getCreatedObject = ReOpenQuestionVotes.objects.filter(
        question_to_opening=data).exclude(ended=True).first()
    get_LIVE_Reviwing_object = ReviewQuestionReOpenVotes.objects.filter(
        question_opened=data).exclude(is_completed=True).first()

# TAGGING - START
    if request.user.is_authenticated:
        winned_gold_tags = TagBadge.objects.filter(
            awarded_to_user=request.user, badge_type="GOLD")
    else:
        winned_gold_tags = ''
# TAGGING - END

    if request.method == 'POST':
        re_open_form = VoteToReOpenForm(data=request.POST)
    else:
        re_open_form = VoteToReOpenForm()


# IF THE NEW REQEST IS SAME TO THE LAST THEN GET THE OBJECT AND INCREASE
# THE CLOSE VOTES

# QUESTION RE-OPEN FORM - END


# IMPLEMENTED BUT NEED A POPUP TO INFORM USER THAT PREVIOUS EDIT IS IN
# QUEUE - START
    trueIfLastEdit_is_approved = ReviewQuestionEdit.objects.filter(
        question_to_view=data).last()
    if trueIfLastEdit_is_approved:
        if trueIfLastEdit_is_approved.is_reviewed or request.user == data.post_owner:
            print("Can Make another Edit")
            canMakeAnotherEdit = True
        else:
            print("Cannot Make another Edit")
            canMakeAnotherEdit = False
    else:
        canMakeAnotherEdit = True
# IMPLEMENTED BUT NEED A POPUP TO INFORM USER THAT PREVIOUS EDIT IS IN
# QUEUE - END

    if request.user.is_authenticated:
        # bookmarked_by_user = BookmarkQuestion.objects.filter(bookmarked_by=request.user, bookmarked_question=data).first()
        bookmarked_by_user = data.bookmarkquestion_set.filter(
            bookmarked_by=request.user).first()
    else:
        bookmarked_by_user = ''

    getCreateFlag_object = FlagPost.objects.filter(
        question_forFlag=data).exclude(
        ended=True).first()

    if request.method == 'POST':
        Flag_Form = FlagQuestionForm(data=request.POST)
    else:
        Flag_Form = FlagQuestionForm()

    getAllTheComments = data.commentq_set.all().exclude(deleted=True)

    if request.method == 'POST':
        answerFlagForm = AnswerFlagForm(data=request.POST)
        if answerFlagForm.is_valid():
            new_post = answerFlagForm.save(commit=False)
            formData = answerFlagForm.cleaned_data['actions_Flag_Q']

            if request.user.profile.flag_posts:
                if formData == "SPAM" or formData == "RUDE_OR_ABUSIVE":
                    getCreateFlag_object = FlagPost.objects.filter(answer_forFlag=data).filter(
                        Q(actions_Flag_Q="SPAM") | Q(actions_Flag_Q="RUDE_OR_ABUSIVE")).exclude(ended=True).first()
                    if getCreateFlag_object:
                        new_post.flagged_by = request.user
                        new_post.answer_forFlag = data
                        new_post.save()
                        getCreateFlag_object.how_many_votes_on_spamANDRude += 1
                        getCreateFlag_object.save()
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Citizen Patrol",
                            bade_position="BADGE")
                        # return redirect('qa:questionDetailView', pk=data.id)
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            url="#",
                            type_of_PrivNotify="BADGE_EARNED",
                            for_if="Citizen Patrol",
                            description="First flagged post"
                        )

                    else:
                        new_post.flagged_by = request.user
                        new_post.answer_forFlag = data
                        new_post.how_many_votes_on_spamANDRude += 1
                        new_post.save()
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Citizen Patrol",
                            bade_position="BADGE")
                        # return redirect('qa:questionDetailView', pk=data.id)
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            url="#",
                            type_of_PrivNotify="BADGE_EARNED",
                            for_if="Citizen Patrol",
                            description="First flagged post"
                        )

                elif formData == "NOT_AN_ANSWER":
                    getCreateFlag_object = FlagPost.objects.filter(
                        answer_forFlag=data,
                        actions_Flag_Q="NOT_AN_ANSWER").exclude(
                        ended=True).first()
                    if getCreateFlag_object:
                        new_post.flagged_by = request.user
                        new_post.answer_forFlag = data
                        new_post.save()
                        getCreateFlag_object.how_many_votes_on_notAnAnswer += 1
                        getCreateFlag_object.save()
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Citizen Patrol",
                            bade_position="BADGE")
                        LowQualityPostsCheck.objects.get_or_create(
                            suggested_by=request.user,
                            low_is=data,
                            why_low_quality="Not an Answer",
                            suggested_through="User")
                        # return redirect('qa:questionDetailView', pk=data.id)
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            url="#",
                            type_of_PrivNotify="BADGE_EARNED",
                            for_if="Citizen Patrol",
                            description="First flagged post"
                        )

                    else:
                        new_post.flagged_by = request.user
                        new_post.answer_forFlag = data
                        new_post.how_many_votes_on_notAnAnswer += 1
                        new_post.save()
                        # return redirect('qa:questionDetailView', pk=data.id)

                else:
                    getCreateFlag_object = FlagPost.objects.filter(
                        answer_forFlag=data).filter(
                        Q(
                            actions_Flag_Q="IN_NEED_OF_MODERATOR_INTERVATION") | Q(
                            actions_Flag_Q="ABOUT_PROFESSIONAL")).exclude(
                        ended=True).first()
                    if getCreateFlag_object:
                        messages.error(
                            request, 'Previous Flag is Waiting for Review')
                    else:
                        new_post.flagged_by = request.user
                        new_post.answer_forFlag = data
                        new_post.save()
                        createReviewInstance, created = ReviewFlagPost.objects.get_or_create(
                            flag_question_to_view=data, flag_of=new_post)
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Citizen Patrol",
                            bade_position="BADGE")
                        createReviewInstance.flag_reviewed_by.add(request.user)
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            url="#",
                            type_of_PrivNotify="BADGE_EARNED",
                            for_if="Citizen Patrol",
                            description="First flagged post"
                        )

                return redirect(
                    'qa:questionDetailView',
                    pk=data.id,
                )  # slug=slug)

            else:
                messages.error(
                    request, 'You need atleast 15 Reputation to Flag this Post')

    else:
        answerFlagForm = AnswerFlagForm()

    getLastEditVotes = QuestionEditVotes.objects.filter(
        edited_question=data).last()
    print("Printing the Last Edit Vote Status \n")
    # getFirstRecordOfQuestion = getDat.prev_record
    # print(getLastEditVotes)

    if getLastEditVotes:
        if getLastEditVotes.rev_Action == "Approve" and getLastEditVotes.is_completed or getLastEditVotes.rev_Action == "Approve_Through_Edit" and getLastEditVotes.is_completed or getLastEditVotes.rev_Action == "Approve_Through_Edit" and getLastEditVotes.is_completed:
            getFirstRecordOfQuestion = data
        else:
            # getNextRecord = data.history.earliest().delete()
            getDat = data.history.first()
            getFirstRecordOfQuestion = getDat.prev_record
    else:
        getFirstRecordOfQuestion = data

    getDat = data.history.first()
    getLastRecord = getDat.prev_record

# Show New Contributor Message - START
    joined_date = data.post_owner.date_joined
    is_olderThan_Ten_Days = timezone.now() - timedelta(days=10)

    if joined_date <= is_olderThan_Ten_Days:
        show_new_contributer_message = False
    else:
        show_new_contributer_message = True
# Show New Contributer Message - END

    if request.user.is_authenticated:
        if request.user.profile.accessTo_moderatorTools:
            if request.method != 'POST':
                tagInlineEditForm = InlineTagEditForm(
                    request.POST or None, request.FILES or None, instance=data)
            else:
                tagInlineEditForm = InlineTagEditForm(
                    instance=data, data=request.POST, files=request.FILES)
        else:
            tagInlineEditForm = ''
    else:
        tagInlineEditForm = ''

    is_bountied = Bounty.objects.filter(question_bounty=data).first()
    if request.user.is_authenticated:
        is_flagged = FlagPost.objects.filter(
            question_forFlag=data, flagged_by=request.user).first()
    else:
        is_flagged = ''

    context = {
        'is_flagged': is_flagged,
        'tagInlineEditForm': tagInlineEditForm,
        'is_bountied': is_bountied,
        'show_new_contributer_message': show_new_contributer_message,
        'STORING_THE_ORIGINAL': STORING_THE_ORIGINAL,
        'getLastRecord': getLastRecord,
        'getFirstRecordOfQuestion': getFirstRecordOfQuestion,
        'getAllTheComments': getAllTheComments,
        'answerFlagForm': answerFlagForm,
        'bookmarked_by_user': bookmarked_by_user,
        'FlagCommentForm': FlagCommentForm,
        'canMakeAnotherEdit': canMakeAnotherEdit,
        'getVotes_casted_by_user': getVotes_casted_by_user,
        'getCreatedObject': getCreatedObject,
        'can_user_vote_for_close': can_user_vote_for_close,
        'getReviewingObject': getReviewingObject,
        'get_Ended_With': get_Ended_With,
        'getCreateClose_object': getCreateClose_object,
        'getHow_many_vote_on_close': getHow_many_vote_on_close,
        'showClose_Votes': showClose_Votes,
        'getClose_votes_on_this_question': getClose_votes_on_this_question,
        'answers_of_questions': answers_of_questions,
        'data': data,
        'form': form,
        'datas': datas,
        'bounty_form': bounty_form,
        'is_it_acc': is_it_acc,
        'cannot_create': cannot_create,
        'Flag_Form': Flag_Form,
        'close_form': close_form,
        'protectForm': protectForm,
        'protectedQuestion': protectedQuestion,
        'likepost': likepost,
        'likeDownpost': likeDownpost,
        'getAnswers': getAnswers,
        'getAcceptedAnswer': getAcceptedAnswer,
        'getAcceptedAnswerCorrected': getAcceptedAnswerCorrected,
        're_open_form': re_open_form,
        'answers': answers,
    }

    return render(request, 'qa/questionDetailView.html', context)


def AjaxCloseForm(request, question_id):
    data = get_object_or_404(Question, pk=question_id)
    getCreateClose_object = CloseQuestionVotes.objects.filter(
        question_to_closing=data).exclude(ended=True).first()

    # request should be ajax and method should be POST.
    if request.is_ajax and request.method == 'POST':
        close_form = CloseForm_Q(data=request.POST)
        if close_form.is_valid():
            if request.user.profile.cast_close_AND_Reopen_votes:
                new_post = close_form.save(commit=False)
                formData = close_form.cleaned_data['why_closing']
                formData_duplicate_of = close_form.cleaned_data['duplicate_of']

                if formData != "DUPLICATE":
                    if getCreateClose_object:
                        if formData == getCreateClose_object.why_closing:
                            new_post.user = request.user
                            new_post.question_to_closing = data
                            # createInstance,created = ReviewCloseVotes.objects.get_or_create(question_to_closed=data)
                            # createInstance.reviewed_by.add(request.user)
                            # print("Instance Created")
                            new_post.save()
                            # SAVE THE INSTANCE FIRST
                            # https://stackoverflow.com/questions/33838433/save-prohibited-to-prevent-data-loss-due-to-unsaved-related-object
                            # createInstance.review_of = new_post
                            # createInstance.save()
                            getCreateClose_object.how_many_votes_on_Close += 1
                            getCreateClose_object.save()
                            # createInstance.review_of = new_post
                            # createInstance.save()
                        else:
                            # print("Save the New Request")

                            new_post.user = request.user
                            new_post.question_to_closing = data
                            createInstance, created = ReviewCloseVotes.objects.get_or_create(
                                question_to_closed=data)
                            # createInstance.reviewed_by.add(request.user)
                            # createInstance.reviewed_by.add(request.user)
                            # createInstance.save()
                            getCreateClose_object.how_many_votes_on_Close += 1
                            getCreateClose_object.save()
                            # print("Instance Created")
                            createInstance.reviewed_by.add(request.user)
                            new_post.save()
                            # SAVE THE INSTANCE FIRST
                            # https://stackoverflow.com/questions/33838433/save-prohibited-to-prevent-data-loss-due-to-unsaved-related-object
                            # createInstance.review_of = new_post
                            # createInstance.save()
                            createInstance.review_of = new_post
                            createInstance.save()
                    else:

                        new_post.user = request.user
                        new_post.question_to_closing = data
                        createInstance, created = ReviewCloseVotes.objects.get_or_create(
                            question_to_closed=data)
                        createInstance.reviewed_by.add(request.user)
                        # createInstance.reviewed_by.add(request.user)
                        # createInstance.save()
                        new_post.how_many_votes_on_Close += 1
                        new_post.save()
                        # SAVE THE INSTANCE FIRST
                        # https://stackoverflow.com/questions/33838433/save-prohibited-to-prevent-data-loss-due-to-unsaved-related-object
                        # createInstance.review_of = new_post
                        # createInstance.save()
                        createInstance.review_of = new_post
                        createInstance.save()

                elif formData == "DUPLICATE" and formData_duplicate_of is None:
                    print("Please Write the Another Question's URL")
                    return JsonResponse({'action': 'duplicate_error'})
                    # messages.error(request, "Please Write the Another Question's URL")
                    # print("Please Write the Another Question's URL")

                else:
                    if getCreateClose_object:
                        if formData == getCreateClose_object.why_closing:

                            new_post.user = request.user
                            new_post.question_to_closing = data
                            createInstance, created = ReviewCloseVotes.objects.get_or_create(
                                question_to_closed=data)
                            createInstance.reviewed_by.add(request.user)
                            # print("Instance Created")
                            new_post.save()
                            # SAVE THE INSTANCE FIRST
                            # https://stackoverflow.com/questions/33838433/save-prohibited-to-prevent-data-loss-due-to-unsaved-related-object

                            getCreateClose_object.how_many_votes_on_Close += 1
                            getCreateClose_object.save()
                            createInstance.review_of = new_post
                            createInstance.save()
                        else:

                            new_post.user = request.user
                            new_post.question_to_closing = data
                            createInstance, created = ReviewCloseVotes.objects.get_or_create(
                                question_to_closed=data)
                            createInstance.reviewed_by.add(request.user)
                            # createInstance.reviewed_by.add(request.user)
                            # createInstance.save()
                            getCreateClose_object.how_many_votes_on_Close += 1
                            getCreateClose_object.save()
                            # print("Instance Created")
                            createInstance.review_of = new_post
                            new_post.save()
                            # SAVE THE INSTANCE FIRST
                            # https://stackoverflow.com/questions/33838433/save-prohibited-to-prevent-data-loss-due-to-unsaved-related-object
                            createInstance.review_of = new_post
                            createInstance.save()

                    else:
                        new_post.user = request.user
                        new_post.question_to_closing = data
                        createInstance, created = ReviewCloseVotes.objects.get_or_create(
                            question_to_closed=data)
                        createInstance.reviewed_by.add(request.user)
                        # createInstance.reviewed_by.add(request.user)
                        # createInstance.save()
                        new_post.how_many_votes_on_Close += 1
                        # print("Instance Created")
                        new_post.save()
                        # SAVE THE INSTANCE FIRST
                        # https://stackoverflow.com/questions/33838433/save-prohibited-to-prevent-data-loss-due-to-unsaved-related-object
                        createInstance.review_of = new_post
                        createInstance.save()            # serialize in new friend object in json
                ser_instance = serializers.serialize('json', [
                    new_post,
                ])
                # send to client side.
                return JsonResponse({"action": "saved"}, status=200)
            else:
                return JsonResponse({'action': "lackOfPrivelege"})
        else:
            # some form errors occured.
            return JsonResponse({"error": close_form.errors}, status=400)

    # some error occured
    return JsonResponse({"error": ""}, status=400)


'''
"Unkind" and No "Longer" Needed Votes will not be reviewed,
comment will automatically delete after 3 votes on these two options
Three votes on "Unkind" and "no longer needed" will delete the comment and end the counting.

If user voted on "Harrassment" and "Something else" then it will save review instance
'''


def flagComment(request, commentq_id):
    commentID = get_object_or_404(CommentQ, pk=commentq_id)
    createTrackRecord = FlagComment.objects.filter(
        comment_of=commentID).exclude(
        ended=True).first()

    if request.method == 'POST':
        FlagCommentForm = CommentFlagForm(data=request.POST)
        if FlagCommentForm.is_valid():
            new_post = FlagCommentForm.save(commit=False)
            formData_unkind = FlagCommentForm.cleaned_data['why_flagging']

            if formData_unkind == "UNKIND" or formData_unkind == "NOT_NEEDED":
                # Create CommentFlag instance to keep track how many votes are to Flag.
                # print("User has selected UnKIND or No needed")
                if createTrackRecord:
                    # print("First Statement is Excecuting")
                    new_post.comment_flagged_by = request.user
                    new_post.comment_of = commentID
                    new_post.save()
                    createTrackRecord.how_many_votes_on_notNeeded_unkind += 1
                    createTrackRecord.save()
                    if createTrackRecord.how_many_votes_on_notNeeded_unkind >= 3:
                        commentID.deleted = True
                        commentID.save()
                    return redirect('profile:home')

                else:
                    # print("Second Statement is Excecuting")
                    new_post.comment_flagged_by = request.user
                    new_post.comment_of = commentID
                    new_post.how_many_votes_on_notNeeded_unkind += 1
                    new_post.save()
                    if createTrackRecord.how_many_votes_on_notNeeded_unkind >= 3:
                        commentID.deleted = True
                        commentID.save()
                    return redirect('profile:home')

            else:
                if createTrackRecord:
                    # print("Third Statement is Excecuting")
                    new_post.comment_flagged_by = request.user
                    new_post.comment_of = commentID
                    new_post.save()
                    createTrackRecord.how_many_votes_on_notNeeded_unkind += 1
                    createTrackRecord.save()
                    createReviewingFlagCommentInstance, created = ReviewFlagComment.objects.get_or_create(
                        flag_of=commentID)
                    createReviewingFlagCommentInstance.c_flag_reviewed_by = request.user
                    createReviewingFlagCommentInstance.save()
                    if createTrackRecord.how_many_votes_on_notNeeded_unkind >= 3:
                        commentID.delete()
                    return redirect('profile:home')
                else:
                    # print("Third Statement is Excecuting")
                    new_post.comment_flagged_by = request.user
                    new_post.comment_of = commentID
                    new_post.how_many_votes_on_notNeeded_unkind += 1
                    new_post.save()
                    createReviewingFlagCommentInstance, created = ReviewFlagComment.objects.get_or_create(
                        flag_of=commentID)
                    createReviewingFlagCommentInstance.c_flag_reviewed_by = request.user
                    createReviewingFlagCommentInstance.save()
                    # if createTrackRecord.how_many_votes_on_notNeeded_unkind >= 3:
                    # commentID.delete()
                    return redirect('profile:home')
        else:
            messages.error(request, "Something went wrong!")
            return redirect('profile:home')

    else:
        FlagCommentForm = CommentFlagForm()

    context = {'FlagCommentForms': FlagCommentForm}
    return render(request, 'profile/flagComment.html', context)


def save_comment_answer(request, answer_id):
    if request.method == 'POST':
        if request.user.profile.comment_everywhere_Priv:
            comment = request.POST['comment']
            answeringID = request.POST['request']
            print(answeringID)
            ans = Answer.objects.get(pk=answeringID)
            question_URL = request.build_absolute_uri(
                ans.questionans.get_absolute_url())
            if comment != "":
                create = CommentQ.objects.create(answer_comment=ans,
                                                 comment=comment,
                                                 commented_by=request.user
                                                 )
                if request.user != ans.answer_owner:
                    Notification.objects.create(
                        noti_receiver=ans.answer_owner,
                        type_of_noti="comment_answer",
                        url=question_URL,
                        answer_noti=ans)

                getComments = CommentQ.objects.filter(
                    commented_by=request.user).count()
                if getComments >= 10:
                    TagBadge.objects.get_or_create(
                        awarded_to_user=create.commented_by,
                        badge_type="SILVER",
                        tag_name="Commentator",
                        bade_position="BADGE")
                    PrivRepNotification.objects.get_or_create(
                        for_user=request.user,
                        url=question_URL,
                        type_of_PrivNotify="BADGE_EARNED",
                        for_if="Commentator",
                        description="Leave 10 comments"
                    )

                return JsonResponse({'bool': True})
            else:
                return JsonResponse({'bool': False})
        else:
            return JsonResponse(
                {'action': "Need atleast 50 Reputation to Comment"})


def FlagCommentAjax(request, commentq_id):
    commentID = get_object_or_404(CommentQ, pk=commentq_id)
    # request should be ajax and method should be POST.
    if request.is_ajax and request.method == "POST":
        # get the form data
        edit_Q_Form = CommentFlagForm(data=request.POST)
        # save the data and after fetch the object in instance
        if edit_Q_Form.is_valid():
            instance = edit_Q_Form.save(commit=False)
            instance.comment_flagged_by = request.user
            instance.comment_of = commentID
            instance.how_many_votes_on_notNeeded_unkind += 1
            instance.save()
            # serialize in new friend object in json
            ser_instance = serializers.serialize('json', [
                instance,
            ])
            # send to client side.
            return JsonResponse({"instance": ser_instance}, status=200)
        else:
            # some form errors occured.
            return JsonResponse({"error": edit_Q_Form.errors}, status=400)

    # some error occured
    return JsonResponse({"error": ""}, status=400)


def removeProtection(request, question_id):
    que = get_object_or_404(Question, pk=question_id)
    procQue = ProtectQuestion.objects.filter(protecting_question=que)
    if que.is_protected:
        que.is_protected = False
        for s in procQue:
            s.stillProtected = False
            s.protectionRemovedBy = request.user
            s.date_Removed = timezone.now()
            s.save()
        que.save()
        return JsonResponse({'action': 'lackOfPrivelege'})

    else:
        messages.error(request, "Something went wrong")
        return redirect('profile:home')


@login_required
def new_question(request):
    AllTags = Tag.objects.all().values_list('name', flat=True)
    last_posted_q = Question.objects.filter(post_owner=request.user).last()
    is_olderThan_nintyMinutes = timezone.now() - timedelta(minutes=90)

    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            if last_posted_q is None:
                formTags = form.cleaned_data['tags']
                gettingBody = form.cleaned_data['body']
                gettingTitle = form.cleaned_data['title']
                new_post = form.save(commit=False)
                new_post.post_owner = request.user

                for typedTags in formTags:

                    check_if_everything_is_fine = all(
                        typedTags in AllTags for typedTags in formTags)

                    if request.user.profile.create_tags:
                        if len(gettingBody) >= 0 and len(gettingBody) <= 29:
                            messages.error(
                                request, "Body Text should atleast 30 words. You entered " + str(len(gettingBody)))
                        elif len(gettingTitle) >= 0 and len(gettingTitle) <= 14:
                            messages.error(
                                request, "Title must be at least 15 characters.")
                        else:
                            print(form.errors)
                            form.save()
                            form.save_m2m()
                            if len(gettingBody) <= 200:
                                create_Low_Quality_Post_Instance, cre = LowQualityPostsCheck.objects.get_or_create(
                                    suggested_through="Automatic", low_is=new_post, why_low_quality="Question_Less_Than_200", is_completed=False)
                                createReview_item = ReviewLowQualityPosts.objects.get_or_create(
                                    review_of=create_Low_Quality_Post_Instance, is_question=new_post, is_reviewed=False)
                            return redirect('qa:questions')
                    elif check_if_everything_is_fine:
                        if len(gettingBody) >= 0 and len(gettingBody) <= 29:
                            messages.error(
                                request, "Body Text should atleast 30 words. You entered " + str(len(gettingBody)))
                        elif len(gettingTitle) >= 0 and len(gettingTitle) <= 14:
                            messages.error(
                                request, "Title must be at least 15 characters.")
                        else:
                            form.save()
                            print(form.errors)
                            form.save_m2m()
                            if len(gettingBody) <= 200:
                                create_Low_Quality_Post_Instance, cre = LowQualityPostsCheck.objects.get_or_create(
                                    suggested_through="Automatic", low_is=new_post, why_low_quality="Question_Less_Than_200", is_completed=False)
                                createReview_item = ReviewLowQualityPosts.objects.get_or_create(
                                    review_of=create_Low_Quality_Post_Instance, is_question=new_post, is_reviewed=False)
                            return redirect('qa:questions')

                    else:
                        print("Problem 2")
                        messages.error(
                            request, f'You need atleast 1500 Reputation to create a New Tag - {formTags}')

            else:
                if not request.user.profile.remove_new_user_restrictions:
                    if last_posted_q.date >= is_olderThan_nintyMinutes:
                        messages.error(
                            request, 'Question Asking Limit Exceed, You will be able to ask in 90 minutes')
                    else:
                        formTags = form.cleaned_data['tags']
                        gettingBody = form.cleaned_data['body']
                        gettingTitle = form.cleaned_data['title']
                        new_post = form.save(commit=False)
                        new_post.post_owner = request.user

                        for typedTags in formTags:

                            check_if_everything_is_fine = all(
                                typedTags in AllTags for typedTags in formTags)

                            if request.user.profile.create_tags:
                                if len(gettingBody) >= 0 and len(
                                        gettingBody) <= 29:
                                    messages.error(
                                        request, "Body Text should atleast 30 words. You entered " + str(len(gettingBody)))
                                elif len(gettingTitle) >= 0 and len(gettingTitle) <= 14:
                                    messages.error(
                                        request, "Title must be at least 15 characters.")
                                else:
                                    form.save()
                                    print(form.errors)
                                    form.save_m2m()
                                    if len(gettingBody) <= 200:
                                        create_Low_Quality_Post_Instance, cre = LowQualityPostsCheck.objects.get_or_create(
                                            suggested_through="Automatic", low_is=new_post, why_low_quality="Question_Less_Than_200", is_completed=False)
                                        createReview_item = ReviewLowQualityPosts.objects.get_or_create(
                                            review_of=create_Low_Quality_Post_Instance, is_question=new_post, is_reviewed=False)
                                    return redirect('qa:questions')

                            elif check_if_everything_is_fine:
                                if len(gettingBody) >= 0 and len(
                                        gettingBody) <= 29:
                                    messages.error(
                                        request, "Body Text should atleast 30 words. You entered " + str(len(gettingBody)))
                                elif len(gettingTitle) >= 0 and len(gettingTitle) <= 14:
                                    messages.error(
                                        request, "Title must be at least 15 characters.")
                                else:
                                    form.save()
                                    print(form.errors)
                                    form.save_m2m()
                                    if len(gettingBody) <= 200:
                                        create_Low_Quality_Post_Instance, cre = LowQualityPostsCheck.objects.get_or_create(
                                            suggested_through="Automatic", low_is=new_post, why_low_quality="Question_Less_Than_200", is_completed=False)
                                        createReview_item = ReviewLowQualityPosts.objects.get_or_create(
                                            review_of=create_Low_Quality_Post_Instance, is_question=new_post, is_reviewed=False)
                                    return redirect('qa:questions')
                            else:
                                messages.error(
                                    request, f'You need atleast 1500 Reputation to create a New Tag - {typedTags}')
                else:
                    formTags = form.cleaned_data['tags']
                    gettingBody = form.cleaned_data['body']
                    gettingTitle = form.cleaned_data['title']

                    new_post = form.save(commit=False)
                    new_post.post_owner = request.user
                    for typedTags in formTags:

                        check_if_everything_is_fine = all(
                            typedTags in AllTags for typedTags in formTags)

                        if request.user.profile.create_tags:
                            print(len(gettingTitle))
                            if len(gettingBody) >= 0 and len(
                                    gettingBody) <= 29:
                                messages.error(
                                    request, "Body Text should atleast 30 words. You entered " + str(len(gettingBody)))
                            elif len(gettingTitle) >= 0 and len(gettingTitle) <= 14:
                                messages.error(
                                    request, "Title must be at least 15 characters.")
                            else:
                                form.save()
                                print(form.errors)
                                form.save_m2m()
                                if len(gettingBody) <= 200:
                                    create_Low_Quality_Post_Instance, cre = LowQualityPostsCheck.objects.get_or_create(
                                        suggested_through="Automatic", low_is=new_post, why_low_quality="Question_Less_Than_200", is_completed=False)
                                    createReview_item = ReviewLowQualityPosts.objects.get_or_create(
                                        review_of=create_Low_Quality_Post_Instance, is_question=new_post, is_reviewed=False)
                                return redirect('qa:questions')
                        elif check_if_everything_is_fine:
                            print(len(gettingBody))
                            if len(gettingBody) >= 0 and len(
                                    gettingBody) <= 29:
                                messages.error(
                                    request, "Body Text should atleast 30 words. You entered " + str(len(gettingBody)))
                            elif len(gettingTitle) >= 0 and len(gettingTitle) <= 14:
                                messages.error(
                                    request, "Title must be at least 15 characters.")
                            else:
                                # counting >= 0 and counting <= 29
                                print(form.errors)
                                form.save()
                                form.save_m2m()
                                if len(gettingBody) <= 200:
                                    create_Low_Quality_Post_Instance, cre = LowQualityPostsCheck.objects.get_or_create(
                                        suggested_through="Automatic", low_is=new_post, why_low_quality="Question_Less_Than_200", is_completed=False)
                                    createReview_item = ReviewLowQualityPosts.objects.get_or_create(
                                        review_of=create_Low_Quality_Post_Instance, is_question=new_post, is_reviewed=False)
                                return redirect('qa:questions')
                        else:
                            messages.error(
                                request, f'You need atleast 1500 Reputation to create a New Tag - {typedTags}')
    else:
        form = QuestionForm()

    context = {'form': form}
    return render(request, 'qa/new_question.html', context)


def validateQuestionTitle(request):
    post_title = request.GET.get('title', None)
    data = {
        'titleAlreadyExisted': Question.objects.filter(
            title__iexact=post_title).exists()}
    if data['titleAlreadyExisted']:
        data['error_message'] = f'Already Existed'
        print("Taken")
    else:
        data['success_message'] = f'Good to Go'
        print("Can Use")
    return JsonResponse(data)


def reviewQuestion(request):
    AllTags = Tag.objects.all().values_list('name', flat=True)
    post_title = request.GET.get('title', None)
    post_body = request.GET.get('body', None)
    formTags = request.GET.get('tags', None)
    taken = Question.objects.filter(title__iexact=post_title).exists()
    formTags = formTags.split(",")
    print(formTags)
    for typedTags in formTags:
        check_if_everything_is_fine = all(
            typedTags in AllTags for typedTags in formTags)
        define = ''
        showNewTagError = False
        if request.user.profile.create_tags:
            print("No Restrictions")
        else:
            if not check_if_everything_is_fine:
                showNewTagError = True
            else:
                showNewTagError = False
                define = True
    # print(check_if_everything_is_fine)

    counting = len(post_body)
    if counting >= 0 and counting <= 29:
        postBody = True
        print("Body Text should atleast 30 words. You entered " + str(counting))
        # USED "str(counting)" BECAUSE WITHOUT ADDING str, It would show 'TypeError' :-:
        # print("Body Text should atleast 30 words. You entered " + int(counting))
        # TypeError: can only concatenate str (not "int") to str
    else:
        postBody = False
        print("Body Text is FulFilled")

    # using list comprehension to
    # perform removal
    new = [i for i in formTags if i]

    # spliting = formTags.split(",")
    # print(len(spliting))
    # lengthing = len(spliting)
    # print(lengthing)
    # for words in spliting:
    #     print(count(words))

    if len(new) < 1:
        print("Fine")
        showError = True
    else:
        print("Raise the Error")
        showError = False

    if len(post_title) <= 5:
        print("Add atleast 2 more Words")
        showLessTitleError = True
    else:
        showLessTitleError = False
    # print(showLessTitleError)
    # if taken == True:
    #     is_it_true = True
    # else:
    #     is_it_true = False

    if taken == False and showError == False and showNewTagError == False and showLessTitleError == False and postBody == False:
        allClear = True
        print("Everything Clear")
    else:
        allClear = False
        print("Something is Missing")

    data = {
        'taken': taken,
        # 'postBody':postBody,
        'showError': showError,
        'allClear': allClear,
        'showNewTagError': showNewTagError,
        'define': define,
    }

    if taken:
        data['error_message_of_title'] = f'Already Existed'
    elif postBody:
        data['error_message_of_body_text'] = f'Words are less than 15'
    elif data['showError']:
        data['error_message_of_tag'] = f'Add atleast One Tag'
    elif data['showNewTagError']:
        data['error_message_of_new_tag'] = f'Cannot create a New Tag'
    return JsonResponse(data)


def bookmarkIt(request, question_id):
    post = get_object_or_404(Question, pk=question_id)
    question_URL = request.build_absolute_uri(post.get_absolute_url())

    bookmarks = Profile.objects.filter(bookmark_questions=post).count()
    print(bookmarks)
    if request.GET.get('submit') == 'bookIt':
        if request.user.profile in post.bookmark_questions.all():
            # UNCOMMENT FOR SET TO FALSE IF BOOKMARKS IS LESS THAN _____
            # if bookmarks >= 1:
            # post.post_owner.profile.favorite_question = False
            # post.post_owner.profile.save()
            post.bookmark_questions.remove(request.user.profile)
            return JsonResponse({'action': 'removeBookmark'})
        else:
            post.bookmark_questions.add(request.user.profile)
# BADGE - FVOURITE QUESTION - BOOKMARKED BY 25 USERS
            if bookmarks >= 25:
                # print(bookmarks)
                TagBadge.objects.get_or_create(
                    awarded_to_user=post.post_owner,
                    badge_type="SILVER",
                    tag_name="Favorite-Question",
                    bade_position="class")
                PrivRepNotification.objects.get_or_create(
                    for_user=post.post_owner,
                    type_of_PrivNotify="BADGE_EARNED",
                    url=question_URL,
                    for_if="Favorite-Question",
                    description="Question bookmarked by 25 users"
                )

                # post.post_owner.profile.favorite_question_S = True
# BADGE - STELLAR QUESTION - BOOKMARKED BY 100 USERS
            if bookmarks >= 100:

                TagBadge.objects.get_or_create(
                    awarded_to_user=post.post_owner,
                    badge_type="SILVER",
                    tag_name="Stellar-Question",
                    bade_position="class")
                PrivRepNotification.objects.get_or_create(
                    for_user=post.post_owner,
                    type_of_PrivNotify="BADGE_EARNED",
                    url=question_URL,
                    for_if="Favorite-Question",
                    description="Question bookmarked by 25 users"
                )
            # if bookmarks >= 2:
                # post.post_owner.profile.stellar_question_F = True
            # post.post_owner.profile.save()
            # notification = Notification(type_of_noti='comment_answer', user=request.user,)
            # notification.save()
            return JsonResponse({'action': 'bookmark_only'})
    else:
        messages.error(request, 'Something went wrong')
        return redirect('profile:home')


def awardBounty(request, question_id, answer_id):
    que = get_object_or_404(Question, pk=question_id)
    post = get_object_or_404(Answer, pk=answer_id)
    prev_awarded_bounty = Answer.objects.filter(
        questionans=question_id, is_bountied_awarded=True)
    question_URL = request.build_absolute_uri(que.get_absolute_url())

    if request.GET.get('submit') == 'award':
        if post.is_bountied_awarded:
            return JsonResponse({'action': 'bountyUnacceptError'})

        else:
            if que.is_bountied:
                if prev_awarded_bounty:
                    # IF PREVIOUS ANSWER IS ACCEPTED THAN- IT WILL PREVENT USER-
                    # FROM ACCEPTING ANOTHER ANSWER AND SHOW bountyError ERROR.
                    return JsonResponse({'action': 'bountyError'})
                else:
                    for bv in que.bounty_set.all():
                        if bv.bounty_value == '50':
                            Reputation.objects.create(
                                answer_O=post,
                                answer_rep_C=50,
                                awarded_to=post.answer_owner,
                                reputation_on_what='Bounty_Awarded')
                            PrivRepNotification.objects.get_or_create(
                                for_user=post.answer_owner,
                                type_of_PrivNotify="BOUNTY_AWARDED_REP_P",
                                url=question_URL,
                                answer_priv_noti=post,
                            )
                        elif bv.bounty_value == '100':
                            Reputation.objects.create(
                                answer_O=post,
                                answer_rep_C=100,
                                awarded_to=post.answer_owner,
                                reputation_on_what='Bounty_Awarded')
                            PrivRepNotification.objects.get_or_create(
                                for_user=post.answer_owner,
                                type_of_PrivNotify="BOUNTY_AWARDED_REP_P",
                                url=question_URL,
                                answer_priv_noti=post,
                            )
                        elif bv.bounty_value == '150':
                            Reputation.objects.create(
                                answer_O=post,
                                answer_rep_C=150,
                                awarded_to=post.answer_owner,
                                reputation_on_what='Bounty_Awarded')
                            PrivRepNotification.objects.get_or_create(
                                for_user=post.answer_owner,
                                type_of_PrivNotify="BOUNTY_AWARDED_REP_P",
                                url=question_URL,
                                answer_priv_noti=post,
                            )
                        elif bv.bounty_value == '200':
                            Reputation.objects.create(
                                answer_O=post,
                                answer_rep_C=200,
                                awarded_to=post.answer_owner,
                                reputation_on_what='Bounty_Awarded')
                            PrivRepNotification.objects.create(
                                for_user=post.answer_owner,
                                type_of_PrivNotify="BOUNTY_AWARDED_REP_P",
                                url=question_URL,
                                answer_priv_noti=post,
                            )
                        elif bv.bounty_value == '250':
                            Reputation.objects.create(
                                answer_O=post,
                                answer_rep_C=250,
                                awarded_to=post.answer_owner,
                                reputation_on_what='Bounty_Awarded')
                            PrivRepNotification.objects.get_or_create(
                                for_user=post.answer_owner,
                                type_of_PrivNotify="BOUNTY_AWARDED_REP_P",
                                url=question_URL,
                                answer_priv_noti=post,
                            )
                        elif bv.bounty_value == '300':
                            Reputation.objects.create(
                                answer_O=post,
                                answer_rep_C=300,
                                awarded_to=post.answer_owner,
                                reputation_on_what='Bounty_Awarded')
                            PrivRepNotification.objects.get_or_create(
                                for_user=post.answer_owner,
                                type_of_PrivNotify="BOUNTY_AWARDED_REP_P",
                                url=question_URL,
                                answer_priv_noti=post,
                            )
                        elif bv.bounty_value == '350':
                            Reputation.objects.create(
                                answer_O=post,
                                answer_rep_C=350,
                                awarded_to=post.answer_owner,
                                reputation_on_what='Bounty_Awarded')
                            PrivRepNotification.objects.get_or_create(
                                for_user=post.answer_owner,
                                type_of_PrivNotify="BOUNTY_AWARDED_REP_P",
                                url=question_URL,
                                answer_priv_noti=post,
                            )
                        elif bv.bounty_value == '400':
                            Reputation.objects.create(
                                answer_O=post,
                                answer_rep_C=400,
                                awarded_to=post.answer_owner,
                                reputation_on_what='Bounty_Awarded')
                            PrivRepNotification.objects.get_or_create(
                                for_user=post.answer_owner,
                                type_of_PrivNotify="BOUNTY_AWARDED_REP_P",
                                url=question_URL,
                                answer_priv_noti=post,
                            )
                        elif bv.bounty_value == '450':
                            Reputation.objects.create(
                                answer_O=post,
                                answer_rep_C=450,
                                awarded_to=post.answer_owner,
                                reputation_on_what='Bounty_Awarded')
                            PrivRepNotification.objects.get_or_create(
                                for_user=post.answer_owner,
                                type_of_PrivNotify="BOUNTY_AWARDED_REP_P",
                                url=question_URL,
                                answer_priv_noti=post,
                            )
                        elif bv.bounty_value == '500':
                            Reputation.objects.create(
                                answer_O=post,
                                answer_rep_C=500,
                                awarded_to=post.answer_owner,
                                reputation_on_what='Bounty_Awarded')
                            PrivRepNotification.objects.get_or_create(
                                for_user=post.answer_owner,
                                type_of_PrivNotify="BOUNTY_AWARDED_REP_P",
                                url=question_URL,
                                answer_priv_noti=post,
                            )
                        post.is_bountied_awarded = True
                        bv.is_awarded = True
# ! Altruist Badge - First bounty i award on another person's Q

                        if que.post_owner != request.user:
                            awardTag = TagBadge.objects.get_or_create(
                                awarded_to_user=request.user,
                                badge_type="BRONZE",
                                tag_name="Altruist",
                                bade_position="BADGE",
                                questionIf_TagOf_Q=que)
                            PrivRepNotification.objects.get_or_create(
                                for_user=request.user,
                                type_of_PrivNotify="BADGE_EARNED",
                                url=question_URL,
                                for_if="Altruist",
                                description="First bounty you manually award on another person's question"
                            )
                            # Bronze_TagBadge.objects.get_or_create(awarded_to=request.user, badge_type="Bronze", tag_name="Altruist")
                            # request.user.profile.altruist_B = True
                            # request.user.profile.save()
                        else:
                            print("Error is Here")
                            # ! Benefactor Badge - First bounty i award on my Q
                            awardTag = TagBadge.objects.get_or_create(
                                awarded_to_user=request.user,
                                badge_type="BRONZE",
                                tag_name="Benefactor",
                                bade_position="BADGE",
                                questionIf_TagOf_Q=que)
                            PrivRepNotification.objects.get_or_create(
                                for_user=request.user,
                                type_of_PrivNotify="BADGE_EARNED",
                                url=question_URL,
                                for_if="Benefactor",
                                description="First bounty you manually award on your own question"
                            )
                            # request.user.profile.benefactor_B = True
                            # request.user.profile.save()
                        bv.save()
                    que.limit_exced = False
                    que.save()
                    post.save()
                return JsonResponse({'action': 'awardBountyToIt'})

            else:
                # THIS ERROR IS NOT DEFINED IN HTML
                return JsonResponse({'action': 'questionWithoutBounty'})
    else:
        messages.error(request, 'Something went wrong')
        return redirect('qa:questions')


def mark_accepted(request, answer_id, question_id):
    que = get_object_or_404(Question, id=question_id)
    post = get_object_or_404(Answer, pk=answer_id)
    question_URL = request.build_absolute_uri(que.get_absolute_url())

    prev_accepted_ans = Answer.objects.filter(questionans=que, accepted=True)

    if request.GET.get('submit') == 'mark':
        if post.accepted:
            post.accepted = False
            post.save()
            if Reputation.objects.filter(
                    answer_O=post,
                    question_rep_C=15,
                    awarded_to=post.answer_owner,
                    reputation_on_what='ANSWER_ACCEPT').exists():
                Reputation.objects.filter(
                    answer_O=post,
                    question_rep_C=15,
                    awarded_to=post.answer_owner,
                    reputation_on_what='ANSWER_ACCEPT').delete()
            if PrivRepNotification.objects.filter(
                    for_user=post.answer_owner,
                    is_read=False,
                    url=question_URL,
                    type_of_PrivNotify="ANSWER_ACCEPT_REP_P",
                    missingReputation=15).exists():
                PrivRepNotification.objects.filter(
                    for_user=post.answer_owner,
                    is_read=True,
                    answer_priv_noti=post,
                    url=question_URL,
                    type_of_PrivNotify="ANSWER_ACCEPT_REP_P",
                    missingReputation=15).delete()
            que.is_answer_accepted = False
            que.save()
            return JsonResponse({'action': 'unaccept'})
        else:
            # if post.answer_owner == request.user and post.date < timezone.now() - timedelta(days=2):
            #     prev_accepted_ans.update(accepted=False)
            #     post.accepted = True
            #     post.save()
            #     awardReputation = Reputation.objects.get_or_create(answer_O=post, question_rep_C=15, awarded_to=post.answer_owner,reputation_on_what='ANSWER_ACCEPT')
            #     # -----------------------------------------------------------
            #     createARep_Notification = PrivRepNotification.objects.get_or_create(for_user=post.answer_owner, url=question_URL, type_of_PrivNotify="ANSWER_ACCEPT_REP_P", missingReputation=15)
            #     # -----------------------------------------------------------
            #     TagBadge.objects.get_or_create(awarded_to_user=post.answer_owner,badge_type="BADGE", tag_name="Scholar",bade_position="BADGE")
            #     # print("Scholar Tag Awarded")
            #     return JsonResponse({'action': 'accept'})
            # else:
            #     return JsonResponse({'action': 'acceptIn_10Days'})
            if post.date <= timezone.now() - timedelta(minutes=5):
                que.is_answer_accepted = True
                que.save()
                # if post.answer_owner != request.user:
                prev_accepted_ans.update(accepted=False)
                post.accepted = True
                post.save()
                if request.user != post.answer_owner:
                    awardReputation = Reputation.objects.get_or_create(
                        answer_O=post,
                        question_rep_C=15,
                        awarded_to=post.answer_owner,
                        reputation_on_what='ANSWER_ACCEPT')
                # -----------------------------------------------------------
                createARep_Notification = PrivRepNotification.objects.get_or_create(
                    for_user=post.answer_owner,
                    question_priv_noti=post.questionans,
                    url=question_URL,
                    type_of_PrivNotify="ANSWER_ACCEPT_REP_P",
                    missingReputation=15)
                # -----------------------------------------------------------
                TagBadge.objects.get_or_create(
                    awarded_to_user=post.answer_owner,
                    badge_type="BADGE",
                    tag_name="Scholar",
                    bade_position="BADGE",
                    questionIf_TagOf_Q=post.questionans)
                PrivRepNotification.objects.get_or_create(
                    for_user=post.answer_owner,
                    type_of_PrivNotify="BADGE_EARNED",
                    url=question_URL,
                    for_if="Scholar",
                    description="Ask a question and accept an answer"
                )
                # print("Scholar Tag Awarded")
                return JsonResponse({'action': 'accept'})

            elif que.post_owner == request.user and post.date <= timezone.now() - timedelta(days=2):
                que.is_answer_accepted = True
                que.save()
                # if post.answer_owner != request.user:
                prev_accepted_ans.update(accepted=False)
                post.accepted = True
                post.save()
                if request.user != post.answer_owner:
                    Reputation.objects.get_or_create(
                        answer_O=post,
                        question_rep_C=15,
                        awarded_to=post.answer_owner,
                        reputation_on_what='ANSWER_ACCEPT')
                    # -----------------------------------------------------------
                    PrivRepNotification.objects.get_or_create(
                        for_user=post.answer_owner,
                        url=question_URL,
                        question_priv_noti=post,
                        type_of_PrivNotify="ANSWER_ACCEPT_REP_P",
                        missingReputation=15)
                    # -----------------------------------------------------------
                    TagBadge.objects.get_or_create(
                        awarded_to_user=post.answer_owner,
                        badge_type="BADGE",
                        tag_name="Scholar",
                        bade_position="BADGE",
                        questionIf_TagOf_Q=post.questionans)
                    PrivRepNotification.objects.get_or_create(
                        for_user=post.answer_owner,
                        type_of_PrivNotify="BADGE_EARNED",
                        url=question_URL,
                        for_if="Scholar",
                        description="Ask a question and accept an answer"
                    )
                # print("Scholar Tag Awarded")
                return JsonResponse({'action': 'accept'})

            else:
                return JsonResponse({'action': 'acceptIn_10_Minutes'})
    else:
        messages.error(request, 'Something went wrong')
        return redirect('profile:posts')


def bookmarkQuestion(request, question_id):
    post = get_object_or_404(Question, pk=question_id)

    if request.GET.get('submit') == 'bookmarking':
        if BookmarkQuestion.objects.filter(
                bookmarked_by=request.user,
                bookmarked_question=post).exists():
            BookmarkQuestion.objects.filter(
                bookmarked_by=request.user,
                bookmarked_question=post).delete()
            return JsonResponse({'action': 'bookmarked'})

        else:
            BookmarkQuestion.objects.get_or_create(
                bookmarked_by=request.user, bookmarked_question=post)
            question_URL = request.build_absolute_uri(post.get_absolute_url())

            if post.bookmarkquestion_set.all().count() >= 25:
                createTag = TagBadge.objects.get_or_create(
                    awarded_to_user=post.post_owner,
                    badge_type="SILVER",
                    tag_name="Favorite Question",
                    bade_position="BADGE",
                    questionIf_TagOf_Q=post)
                PrivRepNotification.objects.get_or_create(
                    for_user=post.post_owner,
                    type_of_PrivNotify="BADGE_EARNED",
                    url=question_URL,
                    for_if="Favorite-Question",
                    description="Question bookmarked by 25 users"
                )

            if post.bookmarkquestion_set.all().count() >= 100:
                createTag = TagBadge.objects.get_or_create(
                    awarded_to_user=post.post_owner,
                    badge_type="GOLD",
                    tag_name="Stellar Question",
                    bade_position="BADGE",
                    questionIf_TagOf_Q=post)
                PrivRepNotification.objects.get_or_create(
                    for_user=post.post_owner,
                    type_of_PrivNotify="BADGE_EARNED",
                    url=question_URL,
                    for_if="Favorite-Question",
                    description="Question bookmarked by 25 users"
                )

            return JsonResponse({'action': 'second'})

    messages.error(request, "Something went wrong")
    return redirect('profile:home')


def tourPage(request):

    return render(request, 'profile/tourPage.html')


def award_InformedBadge_OnScroll(request):
    TagBadge.objects.get_or_create(
        awarded_to_user=request.user,
        badge_type="GOLD",
        tag_name="Informed",
        bade_position="BADGE")
    PrivRepNotification.objects.get_or_create(
        for_user=request.user,
        type_of_PrivNotify="BADGE_EARNED",
        url="#",
        for_if="Informed",
        description="Read the entire tour page"
    )

    return JsonResponse({'action': 'awarded'})


# @awardReputation
def question_upvote_downvote(request, question_id):
    post = get_object_or_404(Question, pk=question_id)
    likepost = post.qupvote_set.filter(upvote_by_q=request.user).first()
    downVotedPost = post.qdownvote_set.filter(
        downvote_by_q=request.user).first()
    question_URL = request.build_absolute_uri(post.get_absolute_url())

    upvote_time_limit = timezone.now() - timedelta(minutes=5)
    q_reputation = post.reputation_set.all()

    edited_time = post.q_edited_time

    # minused = edited_time - voted_time

    if post.post_owner == request.user and post.qupvote_set.all().count() >= 1:
        question_URL = request.build_absolute_uri(post.get_absolute_url())
        # createTag = Tag.objects.get_or_create(name="Student")
        TagBadge.objects.get_or_create(
            awarded_to_user=post.post_owner,
            badge_type="BRONZE",
            tag_name="Student",
            bade_position="BADGE",
            questionIf_TagOf_Q=post)
        PrivRepNotification.objects.get_or_create(
            for_user=post.post_owner,
            type_of_PrivNotify="BADGE_EARNED",
            url=question_URL,
            for_if="Student",
            description="First question with score of 1 or more"
        )

    last_24_hours = timezone.now() - timedelta(hours=24)
    getQ_Votes_in_24_Hours = QUpvote.objects.filter(
        date__gt=last_24_hours).count()
    getQ_DownVotes_in_24_Hours = QDownvote.objects.filter(
        downvote_by_q=request.user, date__gt=last_24_hours).count()
    getA_Votes_in_24_Hours = Answer.objects.filter(
        a_vote_ups=request.user, date__gt=last_24_hours).count()
    getA_DownVotes_in_24_Hours = Answer.objects.filter(
        a_vote_downs=request.user, date__gt=last_24_hours).count()
    totalIs = getQ_Votes_in_24_Hours + getQ_DownVotes_in_24_Hours + \
        getA_Votes_in_24_Hours + getA_DownVotes_in_24_Hours

    if totalIs >= 30:
        TagBadge.objects.get_or_create(
            awarded_to_user=request.user,
            badge_type="BRONZE",
            tag_name="Suffrage",
            bade_position="BADGE")
        PrivRepNotification.objects.get_or_create(
            for_user=request.user,
            privilegeURL=question_URL,
            type_of_PrivNotify="BADGE_EARNED")
        PrivRepNotification.objects.get_or_create(
            for_user=request.user,
            type_of_PrivNotify="BADGE_EARNED",
            url=question_URL,
            for_if="Suffrage",
            description="Use 30 votes in a day"
        )

    if totalIs >= 40:
        TagBadge.objects.get_or_create(
            awarded_to_user=request.user,
            badge_type="BRONZE",
            tag_name="Vox Populi",
            bade_position="BADGE")
        PrivRepNotification.objects.get_or_create(
            for_user=request.user,
            type_of_PrivNotify="BADGE_EARNED",
            url=question_URL,
            for_if="Vox Populi",
            description="Use the maximum 40 votes in a day"
        )

    user_url = request.build_absolute_uri(post.get_absolute_url())
    sent = False
    # Upvote
    if request.GET.get('submit') == 'like':
        if QDownvote.objects.filter(
                downvote_by_q=request.user,
                downvote_question_of=post).exists():

            if downVotedPost.date > upvote_time_limit or edited_time > downVotedPost.date:
                QDownvote.objects.filter(
                    downvote_by_q=request.user,
                    downvote_question_of=post).delete()
                m = QUpvote(upvote_by_q=request.user, upvote_question_of=post)
                m.save()
                if Reputation.objects.filter(
                        awarded_to=post.post_owner,
                        question_O=post,
                        question_rep_C=-2,
                        reputation_on_what='QUESTION_DOWNVOTE').exists():
                    Reputation.objects.filter(
                        awarded_to=post.post_owner,
                        question_O=post,
                        question_rep_C=-2,
                        reputation_on_what='QUESTION_DOWNVOTE').delete()
                    Reputation.objects.get_or_create(
                        awarded_to=post.post_owner,
                        question_O=post,
                        question_rep_C=10,
                        reputation_on_what='MY_QUESTION_UPVOTE_REP_P')
                    PrivRepNotification.objects.get_or_create(
                        for_user=post.post_owner,
                        type_of_PrivNotify="MY_QUESTION_UPVOTE_REP_P",
                        url=question_URL,
                        for_if="",
                        description="",
                        question_priv_noti=post,
                    )

                rewardPrivielege(request, post.post_owner)
                return JsonResponse({'action': 'undislike_and_like'})
            else:
                return JsonResponse({'action': 'voteError'})

        elif QUpvote.objects.filter(upvote_by_q=request.user, upvote_question_of=post).exists():
            if likepost.date > upvote_time_limit or edited_time > likepost.date:
                QUpvote.objects.filter(
                    upvote_by_q=request.user,
                    upvote_question_of=post).delete()
                # deleteReputation = Reputation.objects.filter(awarded_to=post.post_owner,question_O=post, question_rep_C=10, reputation_on_what='QUESTION').first()
                # deleteReputation.delete()
                if post.qdownvote_set.all().count() >= 5:
                    post.reversal_monitor = True
                    post.save()

                if PrivRepNotification.objects.filter(
                    for_user=post.post_owner,
                    type_of_PrivNotify="MY_QUESTION_UPVOTE_REP_P",
                    url=question_URL,
                    for_if="",
                    description="",
                    question_priv_noti=post,
                ):
                    PrivRepNotification.objects.filter(
                        for_user=post.post_owner,
                        type_of_PrivNotify="MY_QUESTION_UPVOTE_REP_P",
                        url=question_URL,
                        for_if="",
                        description="",
                        question_priv_noti=post,
                    ).delete()

                if Reputation.objects.filter(
                        awarded_to=post.post_owner,
                        question_O=post,
                        question_rep_C=10,
                        reputation_on_what='MY_QUESTION_UPVOTE_REP_P').exists():
                    Reputation.objects.filter(
                        awarded_to=post.post_owner,
                        question_O=post,
                        question_rep_C=10,
                        reputation_on_what='MY_QUESTION_UPVOTE_REP_P').delete()
                rewardPrivielege(request, post.post_owner)
                return JsonResponse({'action': 'unlike'})
            else:
                return JsonResponse({'action': 'voteError'})

        else:
            if request.user == post.post_owner:
                return JsonResponse({'action': 'cannotLikeOwnPost'})
            else:
                if request.user.profile.voteUpPriv:
                    post.q_reputation += 10
                    post.save()
                    created = QUpvote(
                        upvote_by_q=request.user,
                        upvote_question_of=post)
                    # notify = Notification(noti_receiver=post.post_owner,noti_sender=request.user,url=user_url,type_of_noti="vote_up_question")
                    # notify.save()
                    created.save()
                    Reputation.objects.get_or_create(
                        awarded_to=post.post_owner,
                        question_O=post,
                        question_rep_C=10,
                        reputation_on_what='MY_QUESTION_UPVOTE_REP_P')
                    PrivRepNotification.objects.get_or_create(
                        for_user=post.post_owner,
                        type_of_PrivNotify="MY_QUESTION_UPVOTE_REP_P",
                        url=question_URL,
                        for_if="",
                        description="",
                        question_priv_noti=post,
                    )
                    getReputationEarnedInLast_24Hours = Reputation.objects.filter(
                        awarded_to=post.post_owner).aggregate(
                        Sum('answer_rep_C'), Sum('question_rep_C'))
                    # if getReputationEarnedInLast_24Hours
                    d1 = getReputationEarnedInLast_24Hours['question_rep_C__sum']
                    total_question_rep = getReputationEarnedInLast_24Hours[
                        'question_rep_C__sum'] if d1 else 0
                    s2 = getReputationEarnedInLast_24Hours['answer_rep_C__sum']
                    total_answer_rep = getReputationEarnedInLast_24Hours[
                        'answer_rep_C__sum'] if s2 else 0

                    finalReputation = total_question_rep + total_answer_rep

                    # if finalReputation >= 10:
                    #     print("Awarded the Create Wiki Posts")
                    #     post.post_owner.profile.create_wiki_posts = True
                    #     post.post_owner.profile.save()

                    if created == QUpvote.objects.filter(
                            upvote_by_q=request.user).first():
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Supporter",
                            bade_position="BADGE",
                            questionIf_TagOf_Q=post)
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url=question_URL,
                            for_if="Supporter",
                            description="First up vote"
                        )

    # UNCOMMENT FOR SEND MAIL TO USER - START
                # if request.user.profile.send_email_notifications == True:
                #     subject = f" is reporting a PROFILE"

                #     message = f" \n Why Reporting PROFILE :- {user_url}  \n"\
                #               f" \n Reporting PROFILE Url :- \n"\
                #               f" \n Reported by :-  \n"\

                #     send_mail(subject, message, 'yawanspace@gmail.com',
                #               [request.user.profile.email])
                #     sent = True
    # UNCOMMENT FOR SEND MAIL TO USER - END

                    if post.qupvote_set.all().count() >= 10:
                        TagBadge.objects.get_or_create(
                            awarded_to_user=post.post_owner,
                            badge_type="BRONZE",
                            tag_name="Nice Question",
                            bade_position="BADGE",
                            questionIf_TagOf_Q=post)
                        PrivRepNotification.objects.get_or_create(
                            for_user=post.post_owner,
                            type_of_PrivNotify="BADGE_EARNED",
                            url=question_URL,
                            for_if="Nice Question",
                            description="Question score of 10 or more"
                        )

                    if post.qupvote_set.all().count() >= 25:
                        TagBadge.objects.get_or_create(
                            awarded_to_user=post.post_owner,
                            badge_type="SILVER",
                            tag_name="Good Question",
                            bade_position="BADGE",
                            questionIf_TagOf_Q=post)
                        PrivRepNotification.objects.get_or_create(
                            for_user=post.post_owner,
                            type_of_PrivNotify="BADGE_EARNED",
                            url=question_URL,
                            for_if="Good Question",
                            description="Question score of 25 or more"
                        )

                    if post.qupvote_set.all().count() >= 100:
                        TagBadge.objects.get_or_create(
                            awarded_to_user=post.post_owner,
                            badge_type="GOLD",
                            tag_name="Great Question",
                            bade_position="BADGE",
                            questionIf_TagOf_Q=post)
                        PrivRepNotification.objects.get_or_create(
                            for_user=post.post_owner,
                            type_of_PrivNotify="BADGE_EARNED",
                            url=question_URL,
                            for_if="Great Question",
                            description="Question score of 100 or more"
                        )
                    rewardPrivielege(request, post.post_owner)

                    return JsonResponse({'action': 'like_only'})
                else:
                    return JsonResponse({'action': 'lackOfPrivelege'})
    # DownVote
    elif request.GET.get('submit') == 'downVote':
        if QUpvote.objects.filter(
                upvote_by_q=request.user,
                upvote_question_of=post).exists():
            if likepost.date > upvote_time_limit or edited_time > likepost.date:
                m = QDownvote(
                    downvote_by_q=request.user,
                    downvote_question_of=post)
                m.save()
                QUpvote.objects.filter(
                    upvote_by_q=request.user,
                    upvote_question_of=post).delete()
                # if Reputation.objects.filter()
                getAlltheReputation = Reputation.objects.filter(
                    awarded_to=request.user).aggregate(
                    Sum('answer_rep_C'), Sum('question_rep_C'))
                d = getAlltheReputation['question_rep_C__sum']
                total_question_rep = getAlltheReputation['question_rep_C__sum'] if d else 0
                s = getAlltheReputation['answer_rep_C__sum']
                total_answer_rep = getAlltheReputation['answer_rep_C__sum'] if s else 0
                totalReputation = total_question_rep + total_answer_rep
                if post.qdownvote_set.all().count() >= 5:
                    post.reversal_monitor = True
                    post.save()
                if totalReputation > 2:
                    if Reputation.objects.filter(
                            awarded_to=post.post_owner,
                            question_O=post,
                            question_rep_C=10,
                            reputation_on_what='MY_QUESTION_UPVOTE_REP_P').exists():
                        Reputation.objects.filter(
                            awarded_to=post.post_owner,
                            question_O=post,
                            question_rep_C=10,
                            reputation_on_what='MY_QUESTION_UPVOTE_REP_P').delete()
                        Reputation.objects.get_or_create(
                            awarded_to=post.post_owner,
                            question_O=post,
                            question_rep_C=-2,
                            reputation_on_what='QUESTION_DOWNVOTE')
                else:
                    if Reputation.objects.filter(
                            awarded_to=post.post_owner,
                            question_O=post,
                            question_rep_C=10,
                            reputation_on_what='MY_QUESTION_UPVOTE_REP_P').exists():
                        Reputation.objects.filter(
                            awarded_to=post.post_owner,
                            question_O=post,
                            question_rep_C=10,
                            reputation_on_what='MY_QUESTION_UPVOTE_REP_P').delete()
                rewardPrivielege(request, post.post_owner)
                return JsonResponse({'action': 'unlike_and_dislike'})
            else:
                return JsonResponse({'action': 'voteError'})
        # if request.user in post.q_vote_ups.all():

        #     if voted_time > upvote_time_limit or edited_time > voted_time:
        #         post.q_vote_ups.remove(request.user)
        #         post.q_vote_downs.add(request.user)
        #         return JsonResponse({'action': 'unlike_and_dislike'})
        #     else:
            # return JsonResponse({'action': 'voteError'})

        elif QDownvote.objects.filter(downvote_by_q=request.user, downvote_question_of=post).exists():
            if downVotedPost.date > upvote_time_limit or edited_time > downVotedPost.date:
                QDownvote.objects.filter(
                    downvote_by_q=request.user,
                    downvote_question_of=post).delete()
                if Reputation.objects.filter(
                        awarded_to=post.post_owner,
                        question_O=post,
                        question_rep_C=-2,
                        reputation_on_what='QUESTION_DOWNVOTE').exists():
                    Reputation.objects.filter(
                        awarded_to=post.post_owner,
                        question_O=post,
                        question_rep_C=-2,
                        reputation_on_what='QUESTION_DOWNVOTE').delete()
                rewardPrivielege(request, post.post_owner)
                return JsonResponse({'action': 'undislike'})
            else:
                return JsonResponse({'action': 'voteError'})

        else:
            if request.user == post.post_owner:
                return JsonResponse({'action': 'cannotLikeOwnPost'})
            else:

                if request.user.profile.voteDownPriv:
                    # QUESTION REPUTATION
                    created = QDownvote(
                        downvote_by_q=request.user,
                        downvote_question_of=post)
                    created.save()

                    if created == QDownvote.objects.filter(
                            downvote_by_q=request.user).first():
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Critic",
                            bade_position="BADGE",
                            questionIf_TagOf_Q=post)
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url=question_URL,
                            for_if="Critic",
                            description="First down vote"
                        )

                    getAlltheReputation = Reputation.objects.filter(
                        awarded_to=request.user).aggregate(
                        Sum('answer_rep_C'), Sum('question_rep_C'))
                    d = getAlltheReputation['question_rep_C__sum']
                    total_question_rep = getAlltheReputation['question_rep_C__sum'] if d else 0
                    s = getAlltheReputation['answer_rep_C__sum']
                    total_answer_rep = getAlltheReputation['answer_rep_C__sum'] if s else 0
                    totalReputation = total_question_rep + total_answer_rep
                    if totalReputation > 2:
                        decRep = Reputation.objects.get_or_create(
                            awarded_to=post.post_owner,
                            question_O=post,
                            question_rep_C=-2,
                            reputation_on_what='QUESTION_DOWNVOTE')
                    rewardPrivielege(request, post.post_owner)
                    return JsonResponse({'action': 'dislike_only'})
                else:
                    return JsonResponse({'action': 'lackOfPrivelege'})

    else:
        messages.error(request, 'Something went wrong')
        return redirect('profile:posts')


"""
Removed the decorator because have to design a new decorator with
answer_id, the previous one was for question_id
"""
# @awardReputation


def answer_upvote_downvote(request, answer_id):
    # que = get_object_or_404(Question, pk=question_id)
    post = get_object_or_404(Answer, pk=answer_id)
    question_URL = request.build_absolute_uri(
        post.questionans.get_absolute_url())

    getQuestion = Question.objects.get(answer=post)

    getVotedOnQ = Question.objects.filter(
        qupvote__upvote_by_q=request.user).count()
    getVotedOnQ_Down = Question.objects.filter(
        qdownvote__downvote_by_q=request.user).count()
    getVotedOn = Answer.objects.filter(a_vote_ups=request.user).count()
    getVotedOn_Down = Answer.objects.filter(a_vote_downs=request.user).count()
    if getVotedOn >= 300 or getVotedOn_Down >= 300 or getVotedOnQ >= 300 or getVotedOnQ_Down >= 300:
        TagBadge.objects.get_or_create(
            awarded_to_user=post.answer_owner,
            badge_type="SILVER",
            tag_name="Civic Duty",
            bade_position="BADGE")
        PrivRepNotification.objects.get_or_create(
            for_user=post.answer_owner,
            type_of_PrivNotify="BADGE_EARNED",
            url=question_URL,
            for_if="Civic Duty",
            description="Vote 300 or more times"
        )
    getEditingTime = request.user.profile.editPostTimeOfUser
    getRecentAnswer = Answer.objects.filter(answer_owner=request.user).last()

    if getRecentAnswer and getEditingTime:
        if getEditingTime >= timezone.now() - \
                timedelta(minutes=5) and getRecentAnswer.date >= timezone.now() - timedelta(minutes=5):
            request.user.profile.Refiner_Illuminator_TagPostCounter += 1
            request.user.profile.save()
            TagBadge.objects.get_or_create(
                awarded_to_user=request.user,
                badge_type="BRONZE",
                tag_name="Explainer",
                bade_position="BADGE")
            PrivRepNotification.objects.get_or_create(
                for_user=request.user,
                type_of_PrivNotify="BADGE_EARNED",
                url=question_URL,
                for_if="Explainer",
                description="Edit and answer 1 question (both actions within 12 hours, answer score > 0)"
            )
            if request.user.profile.Refiner_Illuminator_TagPostCounter >= 50:
                TagBadge.objects.get_or_create(
                    awarded_to_user=request.user,
                    badge_type="SILVER",
                    tag_name="Refiner",
                    bade_position="BADGE")
                PrivRepNotification.objects.get_or_create(
                    for_user=request.user,
                    type_of_PrivNotify="BADGE_EARNED",
                    url=question_URL,
                    for_if="Refiner",
                    description="Edit and answer 50 questions (both actions within 12 hours, answer score > 0)"
                )
            if request.user.profile.Refiner_Illuminator_TagPostCounter >= 500:
                TagBadge.objects.get_or_create(
                    awarded_to_user=request.user,
                    badge_type="GOLD",
                    tag_name="Illuminator",
                    bade_position="BADGE")
                PrivRepNotification.objects.get_or_create(
                    for_user=request.user,
                    type_of_PrivNotify="BADGE_EARNED",
                    url=question_URL,
                    for_if="Illuminator",
                    description="Edit and answer 500 questions (both actions within 12 hours, answer score > 0)"
                )

    if post.revival_stage_one and post.a_vote_ups.all().count() >= 2:
        TagBadge.objects.get_or_create(
            awarded_to_user=post.answer_owner,
            badge_type="Bronze",
            tag_name="Revival",
            bade_position="BADGE",
            answerIf_TagOf_A=post)
        PrivRepNotification.objects.get_or_create(
            for_user=post.answer_owner,
            type_of_PrivNotify="BADGE_EARNED",
            url=question_URL,
            for_if="Revival",
            description="Answer more than 30 days after a question was asked as first answer scoring 2 or more"
        )

    if post.necromancer_check and post.a_vote_ups.all().count() >= 5:
        TagBadge.objects.get_or_create(
            awarded_to_user=post.answer_owner,
            badge_type="SILVER",
            tag_name="Necromancer",
            bade_position="BADGE",
            answerIf_TagOf_A=post)
        PrivRepNotification.objects.get_or_create(
            for_user=post.answer_owner,
            type_of_PrivNotify="BADGE_EARNED",
            url=question_URL,
            for_if="Necromancer",
            description="Answer a question more than 60 days later with score of 5 or more"
        )

    last_24_hours = timezone.now() - timedelta(hours=24)
    getQ_Votes_in_24_Hours = QUpvote.objects.filter(
        date__gt=last_24_hours).count()
    getQ_DownVotes_in_24_Hours = QDownvote.objects.filter(
        downvote_by_q=request.user, date__gt=last_24_hours).count()
    getA_Votes_in_24_Hours = Answer.objects.filter(
        a_vote_ups=request.user, date__gt=last_24_hours).count()
    getA_DownVotes_in_24_Hours = Answer.objects.filter(
        a_vote_downs=request.user, date__gt=last_24_hours).count()
    totalIs = getQ_Votes_in_24_Hours + getQ_DownVotes_in_24_Hours + \
        getA_Votes_in_24_Hours + getA_DownVotes_in_24_Hours

    if totalIs >= 30:
        TagBadge.objects.get_or_create(
            awarded_to_user=post.answer_owner,
            badge_type="BRONZE",
            tag_name="Suffrage",
            bade_position="BADGE")
        PrivRepNotification.objects.get_or_create(
            for_user=post.answer_owner,
            type_of_PrivNotify="BADGE_EARNED",
            url=question_URL,
            for_if="Suffrage",
            description="Use 30 votes in a day"
        )

    if post.answer_owner == post.questionans.post_owner and post.a_vote_ups.count() >= 3:
        TagBadge.objects.get_or_create(
            awarded_to_user=post.answer_owner,
            badge_type="SILVER",
            tag_name="Self-Learner",
            bade_position="BADGE",
            answerIf_TagOf_A=post)
        PrivRepNotification.objects.get_or_create(
            for_user=post.answer_owner,
            type_of_PrivNotify="BADGE_EARNED",
            url=question_URL,
            for_if="Self-Learner",
            description="Answer your own question with score of 3 or more"
        )

    if post.a_vote_ups.count() >= 1:
        TagBadge.objects.get_or_create(
            awarded_to_user=post.answer_owner,
            badge_type="SILVER",
            tag_name="Teacher",
            bade_position="BADGE",
            answerIf_TagOf_A=post)
        PrivRepNotification.objects.get_or_create(
            for_user=post.answer_owner,
            type_of_PrivNotify="BADGE_EARNED",
            url=question_URL,
            for_if="Teacher",
            description="Answer a question with score of 1 or more"
        )

    if post.accepted and post.a_vote_ups.count() >= 40:
        TagBadge.objects.get_or_create(
            awarded_to_user=post.answer_owner,
            badge_type="SILVER",
            tag_name="Guru",
            bade_position="BADGE",
            answerIf_TagOf_A=post)
        PrivRepNotification.objects.get_or_create(
            for_user=post.answer_owner,
            type_of_PrivNotify="BADGE_EARNED",
            url=question_URL,
            for_if="Guru",
            description="Accepted answer and score of 40 or more"
        )

    # subquery = ''
    # for s in data.answer_set.all():
    subquery = Tag.objects.filter(
        question__answer__answer_owner=post.answer_owner).annotate(
        num_name=Count('name'))

    for s in subquery:
        gettingAnswers = Answer.objects.filter(questionans__tags__name=s)
        # print(gettingAnswers)
        # print(s)
        for s5 in gettingAnswers:
            # print(s5)
            # print(s5.a_reputation)
            if s.num_name >= 2 and s5.a_reputation >= 15:
                # createTag = Tag.objects.get_or_create(name=s)
                # print("\nTag Awarding Worked\n")
                TagBadge.objects.get_or_create(
                    awarded_to_user=post.answer_owner, badge_type="GOLD", tag_name=s)
                PrivRepNotification.objects.get_or_create(
                    for_user=post.answer_owner,
                    type_of_PrivNotify="BADGE_EARNED",
                    url=question_URL,
                    for_if=s,
                    description="N/A"
                )
            # if s.num_name >= 2 and s2.a_reputation >= 50:
            #     print("Worked")
            #     GoldBadge.objects.get_or_create(awarded_to=request.user,badge_type="Gold",tag_name=s)

    if request.GET.get('submit') == 'like':
        if request.user in post.a_vote_downs.all():
            # REMOVE DOWOVOTE AND UPVOTE
            post.a_vote_downs.remove(request.user)
            print("First Statement is Excecuting")
            post.a_vote_ups.add(request.user)

            # Check if user downvoted the post if then delete that downvote
            # reputation (-2) and add new (+10) reputation
            if Reputation.objects.filter(
                    awarded_to=post.answer_owner,
                    answer_O=post,
                    answer_rep_C=-2,
                    reputation_on_what="DOWN_VOTE_ANSWER_REP_M").exists():
                Reputation.objects.filter(
                    awarded_to=post.answer_owner,
                    answer_O=post,
                    answer_rep_C=-2,
                    reputation_on_what="DOWN_VOTE_ANSWER_REP_M").delete()
                Reputation.objects.get_or_create(
                    awarded_to=post.answer_owner,
                    answer_O=post,
                    answer_rep_C=10,
                    reputation_on_what="MY_ANSWER_UPVOTE_REP_P")
                PrivRepNotification.objects.get_or_create(
                    for_user=post.answer_owner,
                    type_of_PrivNotify="MY_ANSWER_UPVOTE_REP_P",
                    url=question_URL,
                    for_if="",
                    description="",
                    answer_priv_noti=post,
                )
            rewardPrivielege(request, post.answer_owner)
            return JsonResponse({'action': 'unDownVoteAndLike'})

        elif request.user in post.a_vote_ups.all():
            # REMOVE UPVOTE
            post.a_reputation -= 10
            print("Second Statement is Excecuting")
            post.save()
            post.a_vote_ups.remove(request.user)
            if Reputation.objects.filter(
                    awarded_to=post.answer_owner,
                    answer_O=post,
                    answer_rep_C=10,
                    reputation_on_what="MY_ANSWER_UPVOTE_REP_P").exists():
                Reputation.objects.filter(
                    awarded_to=post.answer_owner,
                    answer_O=post,
                    answer_rep_C=10,
                    reputation_on_what="MY_ANSWER_UPVOTE_REP_P").delete()

            if PrivRepNotification.objects.filter(
                    for_user=post.answer_owner,
                    is_read=False,
                    url=question_URL,
                    type_of_PrivNotify="ANSWER_ACCEPT_REP_P",
                    missingReputation=10).exists():
                PrivRepNotification.objects.update(
                    for_user=post.answer_owner,
                    is_read=True,
                    url=question_URL,
                    type_of_PrivNotify="ANSWER_ACCEPT_REP_P",
                    missingReputation=10)
            rewardPrivielege(request, post.answer_owner)
            return JsonResponse({'action': 'unlikeAnswer'})
        elif request.user == post.answer_owner:
            return JsonResponse({'action': 'cannotLikeOwnPost'})
        else:
            # UPVOTE
            if request.user.profile.voteUpPriv:
                post.a_reputation += 10
                # post.date = timezone.now()
                post.save()
                post.a_vote_ups.add(request.user)
                if getQuestion.reversal_monitor and post.a_vote_ups.all().count() >= 20:
                    TagBadge.objects.get_or_create(
                        awarded_to_user=post.answer_owner,
                        badge_type="GOLD",
                        tag_name="Reversal",
                        bade_position="BADGE",
                        answerIf_TagOf_A=post)
                    PrivRepNotification.objects.get_or_create(
                        for_user=post.answer_owner,
                        type_of_PrivNotify="BADGE_EARNED",
                        url=question_URL,
                        for_if="Reversal",
                        description="Provide an answer of +20 score to a question of -5 score")
                PrivRepNotification.objects.get_or_create(
                    for_user=post.answer_owner,
                    is_read=False,
                    url=question_URL,
                    type_of_PrivNotify="ANSWER_ACCEPT_REP_P",
                    missingReputation=10)

                Reputation.objects.get_or_create(
                    awarded_to=post.answer_owner,
                    answer_O=post,
                    answer_rep_C=10,
                    reputation_on_what="MY_ANSWER_UPVOTE_REP_P")
                PrivRepNotification.objects.get_or_create(
                    for_user=post.answer_owner,
                    type_of_PrivNotify="MY_ANSWER_UPVOTE_REP_P",
                    url=question_URL,
                    for_if="",
                    description="",
                    # question_priv_noti=post,
                    answer_priv_noti=post,
                )

                if post.a_vote_ups.all().count() >= 10:
                    TagBadge.objects.get_or_create(
                        awarded_to_user=post.answer_owner,
                        badge_type="BRONZE",
                        tag_name="Nice Answer",
                        bade_position="BADGE",
                        answerIf_TagOf_A=post)
                    PrivRepNotification.objects.get_or_create(
                        for_user=post.answer_owner,
                        type_of_PrivNotify="BADGE_EARNED",
                        url=question_URL,
                        for_if="Nice Answer",
                        description="Answer score of 10 or more"
                    )
                if post.a_vote_ups.all().count() >= 25:
                    TagBadge.objects.get_or_create(
                        awarded_to_user=post.answer_owner,
                        badge_type="SILVER",
                        tag_name="Good Answer",
                        bade_position="BADGE",
                        answerIf_TagOf_A=post)
                    PrivRepNotification.objects.get_or_create(
                        for_user=post.answer_owner,
                        type_of_PrivNotify="BADGE_EARNED",
                        url=question_URL,
                        for_if="Good Answer",
                        description="Answer score of 25 or more"
                    )
                if post.a_vote_ups.all().count() >= 100:
                    TagBadge.objects.get_or_create(
                        awarded_to_user=post.answer_owner,
                        badge_type="GOLD",
                        tag_name="Great Answer",
                        bade_position="BADGE",
                        answerIf_TagOf_A=post)
                    PrivRepNotification.objects.get_or_create(
                        for_user=post.answer_owner,
                        type_of_PrivNotify="BADGE_EARNED",
                        url=question_URL,
                        for_if="Great Answer",
                        description="Answer score of 100 or more"
                    )

                if post == Answer.objects.filter(
                        a_vote_ups=request.user).first():
                    TagBadge.objects.get_or_create(
                        awarded_to_user=request.user,
                        badge_type="BRONZE",
                        tag_name="Supporter",
                        bade_position="BADGE")
                    PrivRepNotification.objects.get_or_create(
                        for_user=request.user,
                        type_of_PrivNotify="BADGE_EARNED",
                        url=question_URL,
                        for_if="Supporter",
                        description="First up vote"
                    )

                rewardPrivielege(request, post.answer_owner)
                return JsonResponse({'action': 'upv'})
            else:
                return JsonResponse({'action': 'lackOfPrivelege'})

    elif request.GET.get('submit') == 'ansDownVote':
        # Remove Upvote and Downvote
        if request.user in post.a_vote_ups.all():
            post.a_vote_ups.remove(request.user)
            post.a_vote_downs.add(request.user)
            if Reputation.objects.filter(
                    awarded_to=post.answer_owner,
                    answer_O=post,
                    answer_rep_C=10,
                    reputation_on_what="MY_ANSWER_UPVOTE_REP_P").exists():
                Reputation.objects.filter(
                    awarded_to=post.answer_owner,
                    answer_O=post,
                    answer_rep_C=10,
                    reputation_on_what="MY_ANSWER_UPVOTE_REP_P").delete()
                Reputation.objects.get_or_create(
                    awarded_to=post.answer_owner,
                    answer_O=post,
                    answer_rep_C=-2,
                    reputation_on_what="DOWN_VOTE_ANSWER_REP_M")
            rewardPrivielege(request, post.answer_owner)
            return JsonResponse({'action': 'unUpvoteAndDownVote'})

        elif request.user in post.a_vote_downs.all():
            # Remove DownVote
            post.a_vote_downs.remove(request.user)
            if Reputation.objects.filter(
                    awarded_to=post.answer_owner,
                    answer_O=post,
                    answer_rep_C=-2,
                    reputation_on_what="DOWN_VOTE_ANSWER_REP_M").exists():
                Reputation.objects.filter(
                    awarded_to=post.answer_owner,
                    answer_O=post,
                    answer_rep_C=-2,
                    reputation_on_what="DOWN_VOTE_ANSWER_REP_M").delete()
            rewardPrivielege(request, post.answer_owner)
            return JsonResponse({'action': 'undislike'})
        elif request.user == post.answer_owner:
            return JsonResponse({'action': 'cannotLikeOwnPost'})
        else:
            # Down Vote
            if request.user.profile.voteDownPriv:
                print("Sixth Statement is Excecuting")
                post.a_vote_downs.add(request.user)
                # post.date = timezone.now()
                post.save()
                Reputation.objects.get_or_create(
                    awarded_to=post.answer_owner,
                    answer_O=post,
                    answer_rep_C=-2,
                    reputation_on_what="DOWN_VOTE_ANSWER_REP_M")
                rewardPrivielege(request, post.answer_owner)
                return JsonResponse({'action': 'downVoteOnly'})
            else:
                return JsonResponse({'action': 'lackOfPrivelege'})
    else:
        messages.error(request, 'Something went wrong')
        return redirect('profile:posts')


def upvote_comment(request, commentq_id):
    com = get_object_or_404(CommentQ, pk=commentq_id)

    if request.GET.get('submit') == 'upVoteCommentIt':
        if request.user in com.com_upvote.all():
            com.com_upvote.remove(request.user)
            return JsonResponse({'action': 'unVoteUp'})
        else:
            com.com_upvote.add(request.user)

            getCommentsUVotes_MoreThan_5 = CommentQ.objects.filter(
                commented_by=request.user).annotate(
                num_comment_upvote=Count('com_upvote')).filter(
                num_comment_upvote__gte=5)

            if getCommentsUVotes_MoreThan_5.count() >= 10:
                TagBadge.objects.get_or_create(
                    awarded_to_user=request.user,
                    badge_type="SILVER",
                    tag_name="Pundit",
                    bade_position="BADGE")
                PrivRepNotification.objects.get_or_create(
                    for_user=request.user,
                    type_of_PrivNotify="BADGE_EARNED",
                    url="#",
                    for_if="Pundit",
                    description="Leave 10 comments with score of 5 or more"
                )

            return JsonResponse({'action': 'voteUp'})

    else:
        messages.error(request, 'Something went wrong')
        return redirect('qa:questions')


@login_required
def edit_answer(request, answer_id):
    post = Answer.objects.get(id=answer_id)
    post_owner = post.answer_owner

    data = get_object_or_404(Answer, id=answer_id)
    active_time = data.active_time
    edited_time = data.a_edited_time

# NEED TO CHECK THE EDITING 6_MON ALGORITHM IS WORKING in Answering Also.

    if request.method == 'POST':
        form = EditAnswerForm(instance=post,
                              data=request.POST,
                              files=request.FILES)

        if form.is_valid():
            formWhyEditing = form.cleaned_data['why_editing_answer']
            form.save(commit=False)
            post.a_edited_time = timezone.now()
            post.active_time = timezone.now()
            post.a_edited_by = request.user
            request.user.profile.editPostTimeOfUser = timezone.now()
            request.user.profile.save()
# ! ARCHAEOLOGIST BADGE - EDIT 100 POST WHICH ARE INACTIVE FOR 6-MONTHS
# Question Old Algorithm - START
            was_inactive_for_six_months = timezone.now() - timedelta(seconds=20)

            if active_time < was_inactive_for_six_months:
                is_in = True
            else:
                is_in = False
# I CAN ALSO DO THIS WITH :-: if active_time < was_inactive_for_six_months
# and data.date < edited_time: BUT HAVEN'T TRIED YET.
            if is_in and data.date < edited_time:
                is_boolean_true = True
                if is_boolean_true:
                    request.user.profile.post_edit_inactive_for_six_month += 1
                    request.user.profile.save()
                    if request.user.profile.post_edit_inactive_for_six_month == 5:
                        request.user.profile.archaeologist_S = True
                        request.user.profile.save()
            else:
                is_boolean_true = False
            data_url = request.build_absolute_uri(
                post.questionans.get_absolute_url())

            if not request.user.profile.edit_questions_answers:
                sendForReview = QuestionEditVotes.objects.create(
                    edit_suggested_by=request.user, edited_answer=post)
                reviewInstance = ReviewQuestionEdit.objects.create(
                    queue_of=sendForReview, answer_to_view_if=post, is_reviewed=False)
                reviewInstance.edit_reviewed_by.add(request.user)
                request.user.profile.posts_edited_counter += 1
                request.user.profile.save()
                getReviewingInstance = ReviewQuestionEdit.objects.filter(
                    queue_of=sendForReview, answer_to_view_if=post, is_reviewed=False).first()
                # data_url = request.build_absolute_uri(getReviewingInstance.get_absolute_url())
                data_url = request.build_absolute_uri(
                    reverse(
                        'review:reviewSuggesstedEdit', args=(
                            getReviewingInstance.pk, )))
                Notification.objects.create(
                    noti_receiver=post_owner,
                    type_of_noti="answer_edit",
                    url=data_url,
                    answer_noti=post)
            elif request.user == post.answer_owner:
                QuestionEditVotes.objects.create(
                    edit_suggested_by=request.user,
                    edited_answer=post,
                    rev_Action="Approve")
            else:
                request.user.profile.posts_edited_counter += 1
                request.user.profile.save()
                data_url = request.build_absolute_uri(
                    post.questionans.get_absolute_url())
                Notification.objects.create(
                    noti_receiver=post_owner,
                    type_of_noti="answer_edit",
                    url=data_url,
                    answer_noti=post)
                QuestionEditVotes.objects.create(
                    edit_suggested_by=request.user,
                    edited_answer=post,
                    rev_Action="Approve")
            if request.user.profile.posts_edited_counter <= 1:
                TagBadge.objects.get_or_create(
                    awarded_to_user=request.user,
                    badge_type="BRONZE",
                    tag_name="Editor",
                    bade_position="BADGE")
                PrivRepNotification.objects.get_or_create(
                    for_user=request.user,
                    type_of_PrivNotify="BADGE_EARNED",
                    url="#",
                    for_if="Editor",
                    description="First Edit"
                )

            if request.user.profile.posts_edited_counter == 80:
                TagBadge.objects.get_or_create(
                    awarded_to_user=request.user,
                    badge_type="SILVER",
                    tag_name="Strunk & White",
                    bade_position="BADGE")
                PrivRepNotification.objects.get_or_create(
                    for_user=request.user,
                    type_of_PrivNotify="BADGE_EARNED",
                    url=data_url,
                    for_if="Strunk & White",
                    description="Edit 80 posts"
                )

            if request.user.profile.posts_edited_counter == 500:
                TagBadge.objects.get_or_create(
                    awarded_to_user=request.user,
                    badge_type="GOLD",
                    tag_name="Copy Editor",
                    bade_position="BADGE")
                PrivRepNotification.objects.get_or_create(
                    for_user=request.user,
                    type_of_PrivNotify="BADGE_EARNED",
                    url=data_url,
                    for_if="Copy Editor",
                    description="Edit 500 posts (excluding own or deleted posts and tag edits)")

            # getEditingTime = request.user.profile.editPostTimeOfUser
            # getRecentAnswer = Answer.objects.filter(answer_owner=request.user).last()

            # if getEditingTime >= timezone.now() - timedelta(minutes=5) and getRecentAnswer.date >= timezone.now() - timedelta(minutes=5) and getRecentAnswer.a_vote_ups.all().count() >= 1:
            #     request.user.profile.Refiner_Illuminator_TagPostCounter += 1
            #     request.user.profile.save()
            #     TagBadge.objects.get_or_create(awarded_to_user=request.user,badge_type="BRONZE", tag_name="Explainer",bade_position="BADGE")
            #     print("Explainer Awarded")
            #     if request.user.profile.Refiner_Illuminator_TagPostCounter >= 50:
            #         TagBadge.objects.get_or_create(awarded_to_user=request.user,badge_type="SILVER", tag_name="Refiner",bade_position="BADGE")
            #     if request.user.profile.Refiner_Illuminator_TagPostCounter >= 500:
            #         TagBadge.objects.get_or_create(awarded_to_user=request.user,badge_type="GOLD", tag_name="Illuminator",bade_position="BADGE")

            getEditingTime = request.user.profile.editPostTimeOfUser
            getRecentAnswer = Answer.objects.filter(
                answer_owner=request.user).last()
            if getRecentAnswer:
                if getEditingTime >= timezone.now() - \
                        timedelta(minutes=5) and getRecentAnswer.date >= timezone.now() - timedelta(minutes=5):
                    request.user.profile.Refiner_Illuminator_TagPostCounter += 1
                    request.user.profile.save()
            form.save()

            update_change_reason(post, formWhyEditing)
            # sendForReview = QuestionEditVotes.objects.create(edit_suggested_by=request.user, edited_answer=post)
            # reviewInstance = ReviewQuestionEdit.objects.create(queue_of=sendForReview,answer_to_view_if=post, is_reviewed=False)
            # data_url = request.build_absolute_uri(reverse('review:reviewSuggesstedEdit', args=(reviewInstance.pk, )))
            # Notification.objects.create(noti_receiver=post_owner, type_of_noti="answer_comment", url=data_url)
            return redirect('profile:home')

        else:
            messages.error(request, 'Form is Not Valid for some reason')

    else:
        form = EditAnswerForm(request.POST or None,
                              request.FILES or None,
                              instance=post)

    context = {'post': post, 'form': form, 'post_owner': post_owner}
    return render(request, 'qa/edit_answer.html', context)


@login_required
def edit_question(request, question_id):
    post = Question.objects.get(id=question_id)
    allComments = post.commentq_set.all()
    post_owner = post.post_owner

    data = get_object_or_404(Question, id=question_id)
    active_time = data.active_date
    edited_time = data.q_edited_time

    if request.method != 'POST':
        form = UpdateQuestion(request.POST or None,
                              request.FILES or None, instance=post)
    else:
        form = UpdateQuestion(
            instance=post, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save(commit=False)
            formWhyEditing = form.cleaned_data['why_editing_question']
            post.q_edited_time = timezone.now()
            post.active_date = timezone.now()
            post.q_edited_by = request.user
            request.user.profile.editPostTimeOfUser = timezone.now()
            request.user.profile.save()
# ! ARCHAEOLOGIST BADGE - EDIT 100 POST WHICH ARE INACTIVE FOR 6-MONTHS
# Question Old Algorithm - START
            # Check if post is inactive for six months and also check
            was_inactive_for_six_months = timezone.now() - timedelta(days=168)

            if active_time < was_inactive_for_six_months:
                is_in = True
            else:
                is_in = False
# I CAN ALSO DO THIS WITH :-: if active_time < was_inactive_for_six_months
# and data.date < edited_time: BUT HAVEN'T TRIED YET.
            if is_in and data.date < edited_time:
                is_boolean_true = True
                if is_boolean_true:
                    request.user.profile.post_edit_inactive_for_six_month += 1
                    request.user.profile.save()
                    if request.user.profile.post_edit_inactive_for_six_month == 1:
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Excavator",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Excavator",
                            description="Edit first post that was inactive for 6 months"
                        )

                    if request.user.profile.post_edit_inactive_for_six_month == 100:
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="SILVER",
                            tag_name="Archaologist",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Archaologist",
                            description="Edit 100 posts that were inactive for 6 months"
                        )

            else:
                is_boolean_true = False
# Question Old Algorithm - END
            form.save()

            # getEditingTime = request.user.profile.editPostTimeOfUser
            # getRecentAnswer = Answer.objects.filter(answer_owner=request.user).last()

            # if getRecentAnswer:
            #     if getEditingTime >= timezone.now() - timedelta(minutes=5) and getRecentAnswer.date >= timezone.now() - timedelta(minutes=5) :
            #         request.user.profile.Refiner_Illuminator_TagPostCounter += 1
            #         TagBadge.objects.get_or_create(awarded_to_user=request.user,badge_type="BRONZE", tag_name="Explainer",bade_position="BADGE")
            #         print("Explainer Awarded")
            #         if request.user.profile.Refiner_Illuminator_TagPostCounter >= 50:
            #             TagBadge.objects.get_or_create(awarded_to_user=request.user,badge_type="SILVER", tag_name="Refiner",bade_position="BADGE")

            #         if request.user.profile.Refiner_Illuminator_TagPostCounter >= 500:
            #             TagBadge.objects.get_or_create(awarded_to_user=request.user,badge_type="GOLD", tag_name="Illuminator",bade_position="BADGE")

            # sendForReview = QuestionEdit.objects.create(edited_question=post,edited_by=request.user)
            if not request.user.profile.edit_questions_answers:
                sendForReview = QuestionEditVotes.objects.create(
                    edit_suggested_by=request.user, edited_question=post)
                reviewInstance = ReviewQuestionEdit.objects.create(
                    queue_of=sendForReview, question_to_view=post, is_reviewed=False)
                reviewInstance.edit_reviewed_by.add(request.user)
                request.user.profile.posts_edited_counter += 1
                request.user.profile.save()
                getReviewingInstance = ReviewQuestionEdit.objects.filter(
                    queue_of=sendForReview, question_to_view=post, is_reviewed=False).first()
                # data_url = request.build_absolute_uri(getReviewingInstance.get_absolute_url())
                data_url = request.build_absolute_uri(
                    reverse(
                        'review:reviewSuggesstedEdit', args=(
                            getReviewingInstance.pk, )))
                Notification.objects.create(
                    noti_receiver=post_owner,
                    type_of_noti="question_edit",
                    url=data_url,
                    question_noti=post)
            elif request.user == post.post_owner:
                QuestionEditVotes.objects.create(
                    edit_suggested_by=request.user,
                    edited_question=post,
                    rev_Action="Approve",
                    is_completed=True)
            else:
                request.user.profile.posts_edited_counter += 1
                request.user.profile.save()
                data_url = request.build_absolute_uri(post.get_absolute_url())
                Notification.objects.create(
                    noti_receiver=post_owner,
                    type_of_noti="question_edit",
                    url=data_url,
                    question_noti=post)
                QuestionEditVotes.objects.create(
                    edit_suggested_by=request.user,
                    edited_question=post,
                    rev_Action="Approve",
                    is_completed=True)

            if request.user.profile.posts_edited_counter <= 1:
                TagBadge.objects.get_or_create(
                    awarded_to_user=request.user,
                    badge_type="BRONZE",
                    tag_name="Editor",
                    bade_position="BADGE")
                PrivRepNotification.objects.get_or_create(
                    for_user=request.user,
                    type_of_PrivNotify="BADGE_EARNED",
                    url=data_url,
                    for_if="Editor",
                    description="Edit first Post"
                )
            if request.user.profile.posts_edited_counter == 80:
                TagBadge.objects.get_or_create(
                    awarded_to_user=request.user,
                    badge_type="SILVER",
                    tag_name="Strunk & White",
                    bade_position="BADGE")
                PrivRepNotification.objects.get_or_create(
                    for_user=request.user,
                    type_of_PrivNotify="BADGE_EARNED",
                    url=data_url,
                    for_if="Strunk & White",
                    description="Edit 80 posts"
                )
            if request.user.profile.posts_edited_counter == 500:
                TagBadge.objects.get_or_create(
                    awarded_to_user=request.user,
                    badge_type="GOLD",
                    tag_name="Copy Editor",
                    bade_position="BADGE")
                PrivRepNotification.objects.get_or_create(
                    for_user=request.user,
                    type_of_PrivNotify="BADGE_EARNED",
                    url=data_url,
                    for_if="Copy Editor",
                    description="Edit 500 posts (excluding own or deleted posts and tag edits)")
            update_change_reason(post, formWhyEditing)
            print(form.errors)

            return redirect('profile:home')

        else:
            print(form.errors)
            messages.error(request,
                           'Something went wrong!')

    context = {
        'allComments': allComments,
        'post': post,
        'form': form,
        'post_owner': post_owner}
    return render(request, 'qa/edit_question.html', context)


def getQuestionEditHistory(request, question_id):
    getQuestion = get_object_or_404(Question, pk=question_id)

    editHistory = getQuestion.history.all()  # .exclude(body=None)

    # for his in editHistory:

    #     if his.prev_record is not None and his.next_record is not None:
    #         print("Worked")
    #         print(len(his.next_record.body) - len(his.prev_record.body))

    context = {'getQuestion': getQuestion, 'editHistory': editHistory}
    return render(request, 'qa/getQuestionEditHistory.html', context)


def answer_edit_history(request, answer_id):
    getAnswer = get_object_or_404(Answer, pk=answer_id)

    editHistory = getAnswer.anshis.all()  # .exclude(body=None)

    context = {'getAnswer': getAnswer, 'editHistory': editHistory, }
    return render(request, 'qa/answer_edit_history.html', context)


def BountiedQuestions(request, query=None):
    days_7 = timezone.now() - timedelta(days=7)
    if query == 'None':
        questions = Question.objects.filter(
            bounty_date_announced__gte=days_7,
            is_bountied=True,
            is_deleted=False
        )
    else:
        questions = Question.objects.filter(
            tags__name__icontains=query,
            bounty_date_announced__gte=days_7,
            is_bountied=True,
            is_deleted=False
        )

    context = {
        'questions': questions,
        'query': query,
        'questionsCount': questions.count()}
    return render(request, 'qa/BountiedQuestions.html', context)


def unansweredQuestions(request, query=None):
    if query == 'None':
        questions = Question.objects.filter(
            answer__answer_owner=None,
            is_deleted=False,
            is_bountied=False)
    else:
        questions = Question.objects.filter(
            tags__name__icontains=query,
            is_deleted=False,
            is_bountied=False).filter(
            Q(answer__answer_owner=None)
        ).distinct()

    context = {
        'questions': questions,
        'query': query,
        'questionsCount': questions.count()}
    return render(request, 'qa/unansweredQuestions.html', context)


def activeQuestions(request, query=None):
    if query == 'None':
        questions = Question.objects.filter(
            is_deleted=False, is_bountied=False).order_by('active_date')
    else:
        questions = Question.objects.filter(
            tags__name__icontains=query,
            is_deleted=False,
            is_bountied=False).order_by('active_date').distinct()

    context = {'questions': questions, 'query': query}
    return render(request, 'qa/activeQuestions.html', context)


# @loggedOutFromAllDevices
def questions(request):
    questions = Question.objects.all().exclude(
        is_bountied=True, is_deleted=True).order_by('-date')

# Damn so use lot of logics But I don't care, I will build this UP !

    if request.method == "POST":
        this = request.POST.getlist('sortId')
        getCheckBoxes = request.POST.getlist('filterId')
        print(getCheckBoxes)

        query = request.POST.get('tagQuery')

        if "RecentActivity" in this:
            selected = "RecentActivity"
            if query:
                relatedTags = Tag.objects.filter(name__icontains=query)
                if "NoAnswers" in getCheckBoxes:
                    bool_1 = True
                else:
                    bool_1 = False
                if "NoAcceptedAnswer" in getCheckBoxes:
                    bool_2 = True
                else:
                    bool_2 = False
                if "Bounty" in getCheckBoxes:
                    bool_3 = True
                else:
                    bool_3 = False

                # No Answers
                if bool_1 and bool_2 == False and bool_3 == False:
                    print("Only First is True")
                    questions = Question.objects.filter(
                        tags__name__icontains=query).annotate(
                        answers=Count('answer')).filter(
                        answers=0,
                        is_deleted=False).order_by('-active_date')

                # No Accepted Answer
                if bool_2 and bool_1 == False and bool_3 == False:
                    print("Only Second is True")
                    questions = Question.objects.filter(
                        tags__name__icontains=query).filter(
                        answer__accepted=False,
                        is_deleted=False).distinct().order_by('-active_date')

                # Has Bounty
                if bool_3 and bool_1 == False and bool_2 == False:
                    questions = Question.objects.filter(
                        tags__name__icontains=query,
                        is_bountied=True,
                        is_deleted=False).order_by('-active_date')
                    print("Only Third is True")

                # No Answers and No Accepted Answer
                if bool_1 and bool_2 and bool_3 == False:
                    questions = Question.objects.filter(
                        tags__name__icontains=query,
                        answer__accepted=False,
                        is_deleted=False).annotate(
                        answers=Count('answer')).filter(
                        answers=0).order_by('-active_date')
                    print("First and Second is True")

                # No Answers and Bounty
                if bool_1 and bool_3 and bool_2 == False:
                    questions = Question.objects.filter(
                        tags__name__icontains=query,
                        is_bountied=True,
                        is_deleted=False).annotate(
                        answers=Count('answer')).filter(
                        answers=0).order_by('-active_date')
                    print("First and Third is True")

                # No Accepted Answers and Bounty
                if bool_2 and bool_3 and bool_1 == False:
                    questions = Question.objects.filter(
                        tags__name__icontains=query,
                        is_bountied=True,
                        answer__accepted=False,
                        is_deleted=False).order_by('-active_date')
                    print("Second and Third is True")

                # ALl Filters are True
                if bool_1 and bool_2 and bool_3:
                    questions = Question.objects.filter(
                        tags__name__icontains=query,
                        is_bountied=True,
                        answer__accepted=False,
                        is_deleted=False).annotate(
                        answers=Count('answer')).filter(
                        answer=0).order_by('-active_date')
                    print("All Are True")

                # Clear Filters
                if bool_1 == False and bool_2 == False and bool_3 == False:
                    questions = Question.objects.filter(
                        tags__name__icontains=query, is_deleted=False).order_by('-active_date')

            else:
                if "NoAnswers" in getCheckBoxes:
                    bool_1 = True
                else:
                    bool_1 = False
                if "NoAcceptedAnswer" in getCheckBoxes:
                    bool_2 = True
                else:
                    bool_2 = False
                if "Bounty" in getCheckBoxes:
                    bool_3 = True
                else:
                    bool_3 = False

                # No Answers
                if bool_1 and bool_2 == False and bool_3 == False:
                    print("Only First is True, Without Query")
                    questions = Question.objects.all().annotate(
                        answers=Count('answer')).filter(
                        answers=0, is_deleted=False).order_by('-active_date')

                # No Accepted Answer
                if bool_2 and bool_1 == False and bool_3 == False:
                    print("Only Second is True")
                    questions = Question.objects.all().filter(
                        answer__accepted=False, is_deleted=False).distinct().order_by('-active_date')

                # Has Bounty
                if bool_3 and bool_1 == False and bool_2 == False:
                    questions = Question.objects.all().exclude(
                        is_bountied=False, is_deleted=True).order_by('-active_date')
                    print("Only Third is True")

                # No Answers and No Accepted Answer
                if bool_1 and bool_2 and bool_3 == False:
                    questions = Question.objects.all().exclude(
                        answer__accepted=True,
                        is_deleted=True).annotate(
                        answers=Count('answer')).filter(
                        answers=0).order_by('-active_date')
                    print("First and Second is True")

                # No Answers and Bounty
                if bool_1 and bool_3 and bool_2 == False:
                    questions = Question.objects.all().exclude(
                        is_bountied=False,
                        is_deleted=True).annotate(
                        answers=Count('answer')).filter(
                        answers=0).order_by('-active_date')
                    print("First and Third is True")

                # No Accepted Answers and Bounty
                if bool_2 and bool_3 and bool_1 == False:
                    questions = Question.objects.all().exclude(
                        is_bountied=False,
                        answer__accepted=True,
                        is_deleted=True).order_by('-active_date')
                    print("Second and Third is True")

                # ALl Filters are True
                if bool_1 and bool_2 and bool_3:
                    questions = Question.objects.all().exclude(
                        is_bountied=False,
                        answer__accepted=True).annotate(
                        answers=Count('answer')).filter(
                        answer=0,
                        is_deleted=False).order_by('-active_date')
                    print("All Are True")

                # Clear Filters
                if bool_1 == False and bool_2 == False and bool_3 == False:
                    questions = Question.objects.all().exclude(
                        is_bountied=True, is_deleted=True).order_by('-active_date')

        elif "Newest" in this:
            selected = "Newest"
            if query:
                relatedTags = Tag.objects.filter(name__icontains=query)
                if "NoAnswers" in getCheckBoxes:
                    bool_1 = True
                else:
                    bool_1 = False
                if "NoAcceptedAnswer" in getCheckBoxes:
                    bool_2 = True
                else:
                    bool_2 = False
                if "Bounty" in getCheckBoxes:
                    bool_3 = True
                else:
                    bool_3 = False

                # No Answers
                if bool_1 and bool_2 == False and bool_3 == False:
                    print("Only First is True")
                    questions = Question.objects.filter(
                        tags__name__icontains=query,
                        is_deleted=False).annotate(
                        answers=Count('answer')).filter(
                        answers=0).order_by('-date')

                # No Accepted Answer
                if bool_2 and bool_1 == False and bool_3 == False:
                    print("Only Second is True")
                    questions = Question.objects.filter(
                        tags__name__icontains=query, is_deleted=False).filter(
                        answer__accepted=False).distinct().order_by('-date')

                # Has Bounty
                if bool_3 and bool_1 == False and bool_2 == False:
                    questions = Question.objects.filter(
                        tags__name__icontains=query,
                        is_deleted=False,
                        is_bountied=True).order_by('-date')
                    print("Only Third is True")

                # No Answers and No Accepted Answer
                if bool_1 and bool_2 and bool_3 == False:
                    questions = Question.objects.filter(
                        tags__name__icontains=query,
                        answer__accepted=False,
                        is_deleted=False).annotate(
                        answers=Count('answer')).filter(
                        answers=0).order_by('-date')
                    print("First and Second is True")

                # No Answers and Bounty
                if bool_1 and bool_3 and bool_2 == False:
                    questions = Question.objects.filter(
                        tags__name__icontains=query,
                        is_bountied=True,
                        is_deleted=False).annotate(
                        answers=Count('answer')).filter(
                        answers=0).order_by('-date')
                    print("First and Third is True")

                # No Accepted Answers and Bounty
                if bool_2 and bool_3 and bool_1 == False:
                    questions = Question.objects.filter(
                        tags__name__icontains=query,
                        is_bountied=True,
                        is_deleted=False,
                        answer__accepted=False).order_by('-date')
                    print("Second and Third is True")

                # ALl Filters are True
                if bool_1 and bool_2 and bool_3:
                    questions = Question.objects.filter(
                        tags__name__icontains=query,
                        is_bountied=True,
                        is_deleted=False,
                        answer__accepted=False).annotate(
                        answers=Count('answer')).filter(
                        answer=0).order_by('-date')
                    print("All Are True")

                # Clear Filters
                if bool_1 == False and bool_2 == False and bool_3 == False:
                    questions = Question.objects.filter(
                        tags__name__icontains=query, is_deleted=False).order_by('-date')

            else:
                if "NoAnswers" in getCheckBoxes:
                    bool_1 = True
                else:
                    bool_1 = False
                if "NoAcceptedAnswer" in getCheckBoxes:
                    bool_2 = True
                else:
                    bool_2 = False
                if "Bounty" in getCheckBoxes:
                    bool_3 = True
                else:
                    bool_3 = False

                # No Answers
                if bool_1 and bool_2 == False and bool_3 == False:
                    print("Only First is True, Without Query")
                    questions = Question.objects.all().annotate(
                        answers=Count('answer')).filter(
                        answers=0, is_deleted=False).order_by('-date')

                # No Accepted Answer
                if bool_2 and bool_1 == False and bool_3 == False:
                    print("Only Second is True")
                    questions = Question.objects.all().filter(
                        answer__accepted=False, is_deleted=False).distinct().order_by('-date')

                # Has Bounty
                if bool_3 and bool_1 == False and bool_2 == False:
                    questions = Question.objects.all().exclude(
                        is_bountied=False, is_deleted=True).order_by('-date')
                    print("Only Third is True")

                # No Answers and No Accepted Answer
                if bool_1 and bool_2 and bool_3 == False:
                    questions = Question.objects.all().exclude(
                        answer__accepted=True).annotate(
                        answers=Count('answer')).filter(
                        answers=0,
                        is_deleted=True).order_by('-date')
                    print("First and Second is True")

                # No Answers and Bounty
                if bool_1 and bool_3 and bool_2 == False:
                    questions = Question.objects.all().exclude(
                        is_bountied=False).annotate(
                        answers=Count('answer')).filter(
                        answers=0,
                        is_deleted=True).order_by('-date')
                    print("First and Third is True")

                # No Accepted Answers and Bounty
                if bool_2 and bool_3 and bool_1 == False:
                    questions = Question.objects.all().exclude(
                        is_bountied=False, answer__accepted=True, is_deleted=True).order_by('-date')
                    print("Second and Third is True")

                # ALl Filters are True
                if bool_1 and bool_2 and bool_3:
                    questions = Question.objects.all().exclude(
                        is_bountied=False,
                        answer__accepted=True,
                        is_deleted=True).annotate(
                        answers=Count('answer')).filter(
                        answer=0).order_by('-date')
                    print("All Are True")

                # Clear Filters
                if bool_1 == False and bool_2 == False and bool_3 == False:
                    questions = Question.objects.all().exclude(
                        is_bountied=True, is_deleted=True).order_by('-date')

        elif "MostVotes" in this:
            selected = "MostVotes"

            if query:
                relatedTags = Tag.objects.filter(name__icontains=query)
                if "NoAnswers" in getCheckBoxes:
                    bool_1 = True
                else:
                    bool_1 = False
                if "NoAcceptedAnswer" in getCheckBoxes:
                    bool_2 = True
                else:
                    bool_2 = False
                if "Bounty" in getCheckBoxes:
                    bool_3 = True
                else:
                    bool_3 = False

                # No Answers
                if bool_1 and bool_2 == False and bool_3 == False:
                    print("Only First is True")
                    questions = Question.objects.filter(
                        tags__name__icontains=query).annotate(
                        answers=Count('answer')).filter(
                        answers=0,
                        is_deleted=False).annotate(
                        mostVotes=Count('qupvote')).order_by('-mostVotes')

                # No Accepted Answer
                if bool_2 and bool_1 == False and bool_3 == False:
                    print("Only Second is True")
                    questions = Question.objects.filter(
                        tags__name__icontains=query).filter(
                        answer__accepted=False,
                        is_deleted=False).distinct().annotate(
                        mostVotes=Count('qupvote')).order_by('-mostVotes')

                # Has Bounty
                if bool_3 and bool_1 == False and bool_2 == False:
                    questions = Question.objects.filter(
                        tags__name__icontains=query, is_bountied=True, is_deleted=False).annotate(
                        mostVotes=Count('qupvote')).order_by('-mostVotes')
                    print("Only Third is True")

                # No Answers and No Accepted Answer
                if bool_1 and bool_2 and bool_3 == False:
                    questions = Question.objects.filter(
                        tags__name__icontains=query,
                        answer__accepted=False,
                        is_deleted=False).annotate(
                        answers=Count('answer')).filter(
                        answers=0).annotate(
                        mostVotes=Count('qupvote')).order_by('-mostVotes')
                    print("First and Second is True")

                # No Answers and Bounty
                if bool_1 and bool_3 and bool_2 == False:
                    questions = Question.objects.filter(
                        tags__name__icontains=query,
                        is_bountied=True,
                        is_deleted=False).annotate(
                        answers=Count('answer')).filter(
                        answers=0).annotate(
                        mostVotes=Count('qupvote')).order_by('-mostVotes')
                    print("First and Third is True")

                # No Accepted Answers and Bounty
                if bool_2 and bool_3 and bool_1 == False:
                    questions = Question.objects.filter(
                        tags__name__icontains=query,
                        is_bountied=True,
                        answer__accepted=False,
                        is_deleted=False).annotate(
                        mostVotes=Count('qupvote')).order_by('-mostVotes')
                    print("Second and Third is True")

                # ALl Filters are True
                if bool_1 and bool_2 and bool_3:
                    questions = Question.objects.filter(
                        tags__name__icontains=query,
                        is_bountied=True,
                        answer__accepted=False,
                        is_deleted=False).annotate(
                        answers=Count('answer')).filter(
                        answer=0).annotate(
                        mostVotes=Count('qupvote')).order_by('-mostVotes')
                    print("All Are True")

                # Clear Filters
                if bool_1 == False and bool_2 == False and bool_3 == False:
                    questions = Question.objects.filter(
                        tags__name__icontains=query, is_deleted=False).annotate(
                        mostVotes=Count('qupvote')).order_by('-mostVotes')

            else:
                if "NoAnswers" in getCheckBoxes:
                    bool_1 = True
                else:
                    bool_1 = False
                if "NoAcceptedAnswer" in getCheckBoxes:
                    bool_2 = True
                else:
                    bool_2 = False
                if "Bounty" in getCheckBoxes:
                    bool_3 = True
                else:
                    bool_3 = False

                # No Answers
                if bool_1 and bool_2 == False and bool_3 == False:
                    print("Only First is True, Without Query")
                    questions = Question.objects.all().annotate(
                        answers=Count('answer')).filter(
                        answers=0, is_deleted=False).annotate(
                        mostVotes=Count('qupvote')).order_by('-mostVotes')

                # No Accepted Answer
                if bool_2 and bool_1 == False and bool_3 == False:
                    print("Only Second is True")
                    questions = Question.objects.all().exclude(
                        answer__accepted=True, is_deleted=True).annotate(
                        mostVotes=Count('qupvote')).order_by('-mostVotes').distinct()

                # Has Bounty
                if bool_3 and bool_1 == False and bool_2 == False:
                    questions = Question.objects.all().exclude(
                        is_bountied=False, is_deleted=True).annotate(
                        mostVotes=Count('qupvote')).order_by('-mostVotes')
                    print("Only Third is True")

                # No Answers and No Accepted Answer
                if bool_1 and bool_2 and bool_3 == False:
                    questions = Question.objects.all().exclude(
                        answer__accepted=True).annotate(
                        answers=Count('answer')).filter(
                        answers=0,
                        is_deleted=False).annotate(
                        mostVotes=Count('qupvote')).order_by('-mostVotes')
                    print("First and Second is True")

                # No Answers and Bounty
                if bool_1 and bool_3 and bool_2 == False:
                    questions = Question.objects.all().exclude(
                        is_bountied=False,
                        is_deleted=True).annotate(
                        answers=Count('answer')).filter(
                        answers=0).annotate(
                        mostVotes=Count('qupvote')).order_by('-mostVotes')
                    print("First and Third is True")

                # No Accepted Answers and Bounty
                if bool_2 and bool_3 and bool_1 == False:
                    questions = Question.objects.all().exclude(
                        is_bountied=False, is_deleted=True, answer__accepted=True).annotate(
                        mostVotes=Count('qupvote')).order_by('-mostVotes')
                    print("Second and Third is True")

                # ALl Filters are True
                if bool_1 and bool_2 and bool_3:
                    questions = Question.objects.all().exclude(
                        is_bountied=False,
                        answer__accepted=True,
                        is_deleted=True).annotate(
                        answers=Count('answer')).filter(
                        answer=0).annotate(
                        mostVotes=Count('qupvote')).order_by('-mostVotes')
                    print("All Are True")

                # Clear Filters
                if bool_1 == False and bool_2 == False and bool_3 == False:
                    questions = Question.objects.all().exclude(
                        is_bountied=True, is_deleted=True).annotate(
                        mostVotes=Count('qupvote')).order_by('-mostVotes')

        # elif "MostFrequent" in this:
            # selected = "MostFrequent"
        else:
            selected = "BountyEndingSoon"
            if query:
                relatedTags = Tag.objects.filter(name__icontains=query)
                if "NoAnswers" in getCheckBoxes:
                    bool_1 = True
                else:
                    bool_1 = False
                if "NoAcceptedAnswer" in getCheckBoxes:
                    bool_2 = True
                else:
                    bool_2 = False
                if "Bounty" in getCheckBoxes:
                    bool_3 = True
                else:
                    bool_3 = False

                minutes_10 = timezone.now() - timedelta(hours=23)
                # questions = Question.objects.filter(bounty_date_announced__lt=minutes_10, is_bountied=True)

                # No Answers
                if bool_1 and bool_2 == False and bool_3 == False:
                    print("Only First is True")
                    questions = Question.objects.filter(
                        tags__name__icontains=query).annotate(
                        answers=Count('answer')).filter(
                        answers=0).filter(
                        bounty_date_announced__lt=minutes_10, is_bountied=True, is_deleted=False)

                # No Accepted Answer
                if bool_2 and bool_1 == False and bool_3 == False:
                    print("Only Second is True, In Bounty Ending Soon")
                    questions = Question.objects.filter(
                        tags__name__icontains=query).filter(
                        answer__accepted=False).filter(
                        bounty_date_announced__lt=minutes_10,
                        is_bountied=True,
                        is_deleted=False).distinct()

                # Has Bounty
                if bool_3 and bool_1 == False and bool_2 == False:
                    questions = Question.objects.filter(
                        tags__name__icontains=query, is_bountied=True, is_deleted=False).filter(
                        bounty_date_announced__lt=minutes_10)
                    print("Only Third is True")

                # No Answers and No Accepted Answer
                if bool_1 and bool_2 and bool_3 == False:
                    questions = Question.objects.filter(
                        tags__name__icontains=query, answer__accepted=False).annotate(
                        answers=Count('answer')).filter(answers=0).filter(
                        bounty_date_announced__lt=minutes_10, is_bountied=True, is_deleted=False)
                    print("First and Second is True")

                # No Answers and Bounty
                if bool_1 and bool_3 and bool_2 == False:
                    questions = Question.objects.filter(
                        tags__name__icontains=query,
                        is_bountied=True).annotate(
                        answers=Count('answer')).filter(
                        answers=0).filter(
                        bounty_date_announced__lt=minutes_10,
                        is_bountied=True,
                        is_deleted=False)
                    print("First and Third is True")

                # No Accepted Answers and Bounty
                if bool_2 and bool_3 and bool_1 == False:
                    questions = Question.objects.filter(
                        tags__name__icontains=query, is_bountied=True, answer__accepted=False).filter(
                        bounty_date_announced__lt=minutes_10, is_bountied=True, is_deleted=False)
                    print("Second and Third is True")

                # ALl Filters are True
                if bool_1 and bool_2 and bool_3:
                    questions = Question.objects.filter(
                        tags__name__icontains=query,
                        is_bountied=True,
                        answer__accepted=False).annotate(
                        answers=Count('answer')).filter(
                        answer=0,
                        is_deleted=False).annotate(
                        mostVotes=Count('qupvote')).order_by('-mostVotes')
                    print("All Are True")

                # Clear Filters
                if bool_1 == False and bool_2 == False and bool_3 == False:
                    questions = Question.objects.filter(tags__name__icontains=query).filter(
                        bounty_date_announced__lt=minutes_10, is_deleted=False, is_bountied=True)

            else:
                if "NoAnswers" in getCheckBoxes:
                    bool_1 = True
                else:
                    bool_1 = False
                if "NoAcceptedAnswer" in getCheckBoxes:
                    bool_2 = True
                else:
                    bool_2 = False
                if "Bounty" in getCheckBoxes:
                    bool_3 = True
                else:
                    bool_3 = False
                minutes_10 = timezone.now() - timedelta(hours=23)

                # No Answers
                if bool_1 and bool_2 == False and bool_3 == False:
                    print("Only First is True, Without Query")
                    questions = Question.objects.filter(
                        bounty_date_announced__lt=minutes_10,
                        is_bountied=True,
                        is_deleted=False).annotate(
                        answers=Count('answer')).filter(
                        answers=0)

                # No Accepted Answer
                if bool_2 and bool_1 == False and bool_3 == False:
                    print("Only Second is True")
                    questions = Question.objects.filter(
                        bounty_date_announced__lt=minutes_10,
                        is_bountied=True,
                        is_deleted=False).exclude(
                        answer__accepted=True).distinct()

                # Has Bounty
                if bool_3 and bool_1 == False and bool_2 == False:
                    questions = Question.objects.filter(
                        bounty_date_announced__lt=minutes_10, is_bountied=True, is_deleted=False)
                    print("Only Third is True")

                # No Answers and No Accepted Answer
                if bool_1 and bool_2 and bool_3 == False:
                    questions = Question.objects.filter(
                        bounty_date_announced__lt=minutes_10,
                        is_bountied=True).exclude(
                        answer__accepted=True).annotate(
                        answers=Count('answer')).filter(
                        answers=0,
                        is_deleted=False)
                    print("First and Second is True")

                # No Answers and Bounty
                if bool_1 and bool_3 and bool_2 == False:
                    questions = Question.objects.filter(
                        bounty_date_announced__lt=minutes_10,
                        is_bountied=True,
                        is_deleted=False).annotate(
                        answers=Count('answer')).filter(
                        answers=0).annotate(
                        mostVotes=Count('qupvote')).order_by('-mostVotes')
                    print("First and Third is True")

                # No Accepted Answers and Bounty
                if bool_2 and bool_3 and bool_1 == False:
                    questions = Question.objects.filter(
                        bounty_date_announced__lt=minutes_10,
                        is_bountied=True,
                        is_deleted=False).exclude(
                        answer__accepted=True)
                    print("Second and Third is True")

                # ALl Filters are True
                if bool_1 and bool_2 and bool_3:
                    questions = Question.objects.filter(
                        bounty_date_announced__lt=minutes_10,
                        is_bountied=True).exclude(
                        answer__accepted=True).annotate(
                        answers=Count('answer')).filter(
                        answer=0,
                        is_deleted=False)
                    print("All Are True")

                # Clear Filters
                if bool_1 == False and bool_2 == False and bool_3 == False:
                    questions = Question.objects.filter(
                        bounty_date_announced__lt=minutes_10, is_bountied=True, is_deleted=False)

    else:
        selected = False
        questions = Question.objects.filter(
            is_deleted=False, is_bountied=False).order_by('-date')
        query = ''
        bool_1 = ''
        bool_2 = ''
        bool_3 = ''
        relatedTags = ''

    # EXCLUDED QUESTIONS WHICH HAVE BOUNTY
    objs = Question.objects.all()  # .exclude(is_bountied=True)
    if request.user.is_authenticated:
        notifics = Notification.objects.filter(
            noti_receiver=request.user).order_by('-date_created')
    else:
        notifics = ''
    minutes_10 = timezone.now() - timedelta(hours=23)
# POSTS BEFORE 4 HOURS
    bount_older = Question.objects.filter(
        bounty_date_announced__lt=minutes_10, is_bountied=True)

    bountied = ''
    object_list = ''

    page = request.GET.get('page', 1)

    paginator = Paginator(questions, 9)
    try:
        questions = paginator.page(page)
    except PageNotAnInteger:
        questions = paginator.page(1)
    except EmptyPage:
        questions = paginator.page(paginator.num_pages)

    countQuestions = Question.objects.count()
    # print("Printing Query")
    # print(query)
    context = {
        'bool_1': bool_1,
        'countQuestions': countQuestions,
        'bool_2': bool_2,
        'bool_3': bool_3,
        'bountied': bountied,
        'query': query,
        'object_list': object_list,
        'questions': questions,
        'selected': selected,
        'notifics': notifics,
        'objs': objs,
        'bount_older': bount_older,
        'relatedTags': relatedTags,
    }

    return render(request, 'qa/Questions_List.html', context)
