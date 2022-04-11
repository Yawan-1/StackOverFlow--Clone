from django.shortcuts import render, redirect, get_object_or_404
from .forms import AnswerReviewForm, QuestionReviewForm, LateAnswerReviewForm, ReviewCloseForm, LowQualityReviewForm
from .forms import CloseForm_Q, VoteToReOpenForm, ReviewReOpenForm, SuggesstedEditForm, FlagPostForm, ReviewFlagCommentForm
from django.http import JsonResponse
from django.contrib import messages
import datetime
from django.utils import timezone
from datetime import timedelta
from qa.forms import EditAnswerForm, UpdateQuestion
from django.core import serializers
from django.db.models import Avg, Count, Min, Sum
from django.db.models import Q
from .models import ReviewCloseVotes, CloseQuestionVotes, Question, Answer, ReOpenQuestionVotes, ReviewQuestionReOpenVotes, FirstQuestionReview, LateAnswerReview, FirstAnswerReview
# from config import QUESTION_OLDER_THAN
from .models import CloseQuestionVotes, ReOpenQuestionVotes, ReviewQuestionReOpenVotes, LowQualityPostsCheck, ReviewFlagComment
from .models import ReviewCloseVotes, QuestionEditVotes, ReviewQuestionEdit, ReviewLowQualityPosts, FlagPost, ReviewFlagPost, FlagComment
from .decorators import required_3000_RepToReview, required_2000_RepToReview, required_500_RepToReview
from qa.models import Reputation, CommentQ
from qa.decorators import highModRequired
from notification.models import PrivRepNotification
from tagbadge.models import TagBadge
from django.contrib.auth.decorators import login_required

# Close Question History -DONE
# Question Edit History - DONE
# Flag Question History - DONE
# ReOpen Question History - DONE

"""
The HttpRequest.is_ajax() method is removed in DJANGO 4, 
so i used is_ajax function to check if the request is
ajax or Not by identifying 'XMLHttpRequest'
Also replaced is_ajax method with this is_ajax function.
"""
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def reOpen_Question_History(request, reviewquestionreopenvotes_id):
    getReviewItem = get_object_or_404(
        ReviewQuestionReOpenVotes,
        pk=reviewquestionreopenvotes_id)
    data = get_object_or_404(Question, reviewquestionreopenvotes=getReviewItem)
    getHistory = ReOpenQuestionVotes.objects.filter(question_to_opening=data)

    context = {'getHistory': getHistory, 'getReviewItem': getReviewItem}
    return render(request, 'review/reOpen_Question_History.html', context)


def flag_Posts_History(request, reviewflagpost_id):
    getReviewItem = get_object_or_404(ReviewFlagPost, pk=reviewflagpost_id)
    if getReviewItem.flag_question_to_view:
        data = get_object_or_404(Question, reviewflagpost=getReviewItem)
        ItIsQuestion = True
        getAllReviewingItems = FlagPost.objects.filter(question_forFlag=data)
    else:
        print("Answer's else statement is Excecuting")
        data = get_object_or_404(Answer, reviewflagpost=getReviewItem)
        ItIsQuestion = False
        getAllReviewingItems = FlagPost.objects.filter(answer_forFlag=data)

    context = {
        'getAllReviewingItems': getAllReviewingItems,
        'getReviewItem': getReviewItem,
    }
    return render(request, 'review/Flag_Post_History.html', context)


def questionCloseHistory(request, reviewclosevotes_id):
    getReviewItem = get_object_or_404(ReviewCloseVotes, pk=reviewclosevotes_id)
    # getQuestion = get_object_or_404(Question, question_to_closed=getReviewItem)
    data = Question.objects.get(reviewclosevotes=getReviewItem)
    getHistory = CloseQuestionVotes.objects.filter(question_to_closing=data)

    context = {'getHistory': getHistory, 'getReviewItem': getReviewItem, }
    return render(request, 'review/Close_Q_History.html', context)


def suggesstedEditHistory_Question(request, reviewquestionedit_id):
    getReviewItem = get_object_or_404(
        ReviewQuestionEdit, pk=reviewquestionedit_id)
    if getReviewItem.question_to_view:
        data = Question.objects.get(reviewquestionedit=getReviewItem)
        ItIsQuestion = True
        getQuestionHistory = data.his.first()
        getAnswerHitory = ''
        getAllReviewingItems = QuestionEditVotes.objects.filter(
            edited_question=data).exclude(rev_Action=None)
    else:
        ItIsQuestion = False
        data = Answer.objects.get(reviewquestionedit=getReviewItem)
        getAnswerHitory = data.anshis.first()
        getQuestionHistory = ''
        getAllReviewingItems = QuestionEditVotes.objects.filter(
            edited_answer=data).exclude(rev_Action=None)

    context = {
        'getAllReviewingItems': getAllReviewingItems,
        'getReviewItem': getReviewItem,
    }
    return render(request, 'review/Suggessted_Edit_History.html', context)


@highModRequired
def reviewFlagComments(request, reviewflagcomment_id):
    commentToReview = get_object_or_404(
        ReviewFlagComment, id=reviewflagcomment_id)
    data = CommentQ.objects.get(reviewflagcomment=commentToReview)

    counting = ReviewFlagComment.objects.filter(
        c_is_reviewed=False).exclude(
        c_flag_reviewed_by=request.user).count()

    getFlagHistory = FlagComment.objects.filter(comment_of=data, ended=False)

    getFlaggerUserProfile = FlagComment.objects.filter(
        comment_of=data, ended=False).first()

    if request.method == 'POST':
        # if counting >= 1:
        form = ReviewFlagCommentForm(
            instance=data,
            data=request.POST,
            files=request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            formData = form.cleaned_data['c_flagReviewActions']
            if formData == "DELETE_IT":
                create_a_NewInstance = FlagComment.objects.create(
                    comment_flagged_by=request.user, comment_of=data, why_flagging="DeleteIt")
                commentToReview.c_flag_reviewed_by = request.user
                commentToReview.c_is_reviewed = True
                commentToReview.c_flagReviewActions = formData
                commentToReview.save()
                getFlaggerUserProfile.comment_flagged_by.profile.helpful_flags_counter += 1
                getFlaggerUserProfile.comment_flagged_by.profile.save()
                for s in getFlagHistory:
                    s.ended = True
                    s.save()
                # data.delete()
                # return redirect('')
            else:
                # create_a_NewInstance = FlagComment.objects.create(comment_flagged_by=request.user, comment_of=getComment, why_flagging="DeleteIt")
                commentToReview.c_flag_reviewed_by = request.user
                commentToReview.c_flagReviewActions = formData

                # commentToReview.c_is_reviewed = True
                commentToReview.save()
                # getFlagHistory.ended = True
                # getFlagHistory.save()
                # return redirect('')
            next_flag = ReviewFlagComment.objects.filter(
                c_is_reviewed=False).exclude(
                c_flag_reviewed_by=request.user).order_by('id').first()
            counting_2 = ReviewFlagComment.objects.filter(
                c_is_reviewed=False).exclude(
                c_flag_reviewed_by=request.user).count()
            if counting_2 >= 1:
                return redirect(
                    'review:reviewFlagComments',
                    reviewflagcomment_id=next_flag.id)
            else:
                messages.error(request, 'No More Comment Flags To Review')
                return redirect('profile:home')

        # else:
            # messages.error(request, "No More Flags to Review")

    else:
        form = ReviewFlagCommentForm(request.POST or None,
                                     request.FILES or None, instance=data)

    getThisItemFromReview = ReviewFlagComment.objects.filter(
        flag_of=data).first()

    if getThisItemFromReview:
        actionWas = ''
        if getThisItemFromReview.c_flagReviewActions == "DELETE_IT":
            actionWas = "Delete_It"
        elif getThisItemFromReview.c_flagReviewActions == "STAY_AS_IT_IS":
            actionWas = "No_Action_Required"
        elif getThisItemFromReview.c_flagReviewActions == "SKIP":
            actionWas = "Skipped"
    else:
        actionWas = ''
    if getThisItemFromReview.c_flag_reviewed_by == request.user:
        is_reviewed = True
    else:
        is_reviewed = False
    # print(actionWas)

    context = {'is_reviewed': is_reviewed, 'form': form, 'data': data, }
    return render(request, 'review/Flag_Comment_Review.html', context)

# @required_2000_RepToReview


def reviewLowQualityPosts(request, reviewlowqualityposts_id):
    getReviewItem = get_object_or_404(
        ReviewLowQualityPosts,
        pk=reviewlowqualityposts_id)

    if getReviewItem.is_question:
        print("Question to Review")
    else:
        print("Answer to Review")

    if request.method == 'POST':
        form = LowQualityReviewForm(
            instance=getReviewItem,
            data=request.POST,
            files=request.FILES)
        if form.is_valid():
            formData = form.cleaned_data['reviewActions']
            if getReviewItem.is_question:
                getQuestion = Question.objects.get(
                    reviewlowqualityposts=getReviewItem)
                getLowQualityItem = LowQualityPostsCheck.objects.filter(
                    low_is=getQuestion, is_completed=False).first()
                getAllVotes_ForSetToReviewed = LowQualityPostsCheck.objects.filter(
                    low_is=getQuestion, is_completed=False)

                if formData == "Looks_OK":
                    create_NegligibleInstance = LowQualityPostsCheck.objects.create(
                        suggested_by=request.user,
                        suggested_through="User-Reviewed",
                        low_is=getQuestion,
                        why_low_quality="Reviewed")
                    getReviewItem.reviewers.add(request.user)
                    getLowQualityItem.how_many_votes_on_OK += 1
                    getLowQualityItem.save()
                    if getLowQualityItem.how_many_votes_on_OK >= 3:
                        getLowQualityItem.is_completed = True
                        getReviewItem.is_reviewed = True
                        getReviewItem.save()
                        getLowQualityItem.save()
                        for s in getAllVotes_ForSetToReviewed:
                            s.is_completed = True
                            s.save()
                            print("All the Votes are Reviewed and set to True \n")
                        print("Question is Good and Will Stay Open \n")

                    # getReviewItem.reviewActions = None
                    getReviewItem.save()

                    getAllLowQualityTask = ReviewLowQualityPosts.objects.filter(
                        reviewers=request.user).count()

                    if not ReviewLowQualityPosts.objects.filter(
                            reviewers=request.user).exists():
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Custodian",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Custodian",
                            description="Complete at least one review task. This badge is awarded once per review type"
                        )

                    if getAllLowQualityTask == 250:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="SILVER",
                            tag_name="Reviewer",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Reviewer",
                            description="Complete at least 250 review tasks. This badge is awarded once per review type"
                        )

                    if getAllLowQualityTask == 1000:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="GOLD",
                            tag_name="Steward",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Steward",
                            description="Complete at least 1000 review tasks. This badge is awarded once per review type"
                        )

                elif formData == "Edit":
                    create_NegligibleInstance = LowQualityPostsCheck.objects.create(
                        suggested_by=request.user,
                        suggested_through="User-Reviewed",
                        low_is=getQuestion,
                        why_low_quality="Reviewed-Edited")
                    getReviewItem.reviewers.add(request.user)
                    getLowQualityItem.how_many_votes_on_OK += 1
                    getLowQualityItem.save()
                    if getLowQualityItem.how_many_votes_on_OK >= 3:
                        getLowQualityItem.is_completed = True
                        getReviewItem.is_reviewed = True
                        getReviewItem.save()
                        getLowQualityItem.save()
                        for s in getAllVotes_ForSetToReviewed:
                            s.is_completed = True
                            s.save()
                            print("All the Votes are Reviewed and set to True \n")
                        print("Question is Good and Will Stay Open \n")

                    # getReviewItem.reviewActions = None
                    getReviewItem.save()

                    getAllLowQualityTask = ReviewLowQualityPosts.objects.filter(
                        reviewers=request.user).count()

                    if not ReviewLowQualityPosts.objects.filter(
                            reviewers=request.user).exists():
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Custodian",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Custodian",
                            description="Complete at least one review task. This badge is awarded once per review type"
                        )

                    if getAllLowQualityTask == 250:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="SILVER",
                            tag_name="Reviewer",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Reviewer",
                            description="Complete at least 250 review tasks. This badge is awarded once per review type"
                        )

                    if getAllLowQualityTask == 1000:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="GOLD",
                            tag_name="Steward",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Steward",
                            description="Complete at least 1000 review tasks. This badge is awarded once per review type"
                        )

                elif formData == "Recommend_Delete":
                    create_NegligibleInstance = LowQualityPostsCheck.objects.create(
                        suggested_by=request.user,
                        suggested_through="User-Reviewed",
                        low_is=getQuestion,
                        why_low_quality="Reviewed-Edited")
                    getReviewItem.reviewers.add(request.user)
                    getLowQualityItem.how_many_votes_on_deleteIt += 1
                    getLowQualityItem.save()
                    if getLowQualityItem.how_many_votes_on_deleteIt >= 3:
                        getLowQualityItem.is_completed = True
                        getReviewItem.is_reviewed = True
                        getReviewItem.save()
                        getLowQualityItem.save()
                        getQuestion.is_deleted = True
                        getQuestion.save()
                        for s in getAllVotes_ForSetToReviewed:
                            s.is_completed = True
                            s.save()
                            print("All the Votes are Reviewed and set to True \n")
                        print("Question is Good and Will Stay Open \n")

                    # getReviewItem.reviewActions = None
                    getReviewItem.save()
                    getAllLowQualityTask = ReviewLowQualityPosts.objects.filter(
                        reviewers=request.user).count()

                    if not ReviewLowQualityPosts.objects.filter(
                            reviewers=request.user).exists():
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Custodian",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Custodian",
                            description="Complete at least one review task. This badge is awarded once per review type"
                        )

                    if getAllLowQualityTask == 250:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="SILVER",
                            tag_name="Reviewer",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Reviewer",
                            description="Complete at least 250 review tasks. This badge is awarded once per review type"
                        )

                    if getAllLowQualityTask == 1000:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="GOLD",
                            tag_name="Steward",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Steward",
                            description="Complete at least 1000 review tasks. This badge is awarded once per review type"
                        )

                elif formData == "Recommend_Close":
                    create_NegligibleInstance = LowQualityPostsCheck.objects.create(
                        suggested_by=request.user,
                        suggested_through="User-Reviewed",
                        low_is=getQuestion,
                        why_low_quality="Reviewed-Edited")
                    getReviewItem.reviewers.add(request.user)
                    getLowQualityItem.how_many_votes_on_deleteIt += 1
                    getLowQualityItem.save()
                    if getLowQualityItem.how_many_votes_on_deleteIt >= 3:
                        getLowQualityItem.is_completed = True
                        getReviewItem.is_reviewed = True
                        getReviewItem.save()
                        getLowQualityItem.save()
                        getQuestion.is_closed = True
                        getQuestion.closed_at = timezone.now()
                        getQuestion.save()
                        for s in getAllVotes_ForSetToReviewed:
                            s.is_completed = True
                            s.save()
                            print("All the Votes are Reviewed and set to True \n")
                        print("Question is Good and Will Stay Open \n")

                    # getReviewItem.reviewActions = None
                    getReviewItem.save()
                    getAllLowQualityTask = ReviewLowQualityPosts.objects.filter(
                        reviewers=request.user).count()

                    if not ReviewLowQualityPosts.objects.filter(
                            reviewers=request.user).exists():
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Custodian",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Custodian",
                            description="Complete at least one review task. This badge is awarded once per review type"
                        )

                    if getAllLowQualityTask == 250:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="SILVER",
                            tag_name="Reviewer",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Reviewer",
                            description="Complete at least 250 review tasks. This badge is awarded once per review type"
                        )

                    if getAllLowQualityTask == 1000:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="GOLD",
                            tag_name="Steward",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Steward",
                            description="Complete at least 1000 review tasks. This badge is awarded once per review type"
                        )

                elif formData == "Skip":
                    getReviewItem.reviewers.add(request.user)
                next_LowQuality_Post = ReviewLowQualityPosts.objects.filter(
                    is_reviewed=False).exclude(reviewers=request.user).order_by('id').first()
                counting_2 = ReviewLowQualityPosts.objects.filter(
                    is_reviewed=False).exclude(
                    reviewers=request.user).count()

                if counting_2 >= 1:
                    return redirect(
                        'review:reviewLowQualityPosts',
                        reviewlowqualityposts_id=next_LowQuality_Post.id)
                else:
                    messages.error(
                        request, 'No More Posts to Review Low Quality Posts')
                    return redirect('profile:home')

            else:
                getAnswer = Answer.objects.get(
                    reviewlowqualityposts=getReviewItem)
                getLowQualityItem = LowQualityPostsCheck.objects.filter(
                    low_ans_is=getAnswer, is_completed=False).first()
                getAllVotes_ForSetToReviewed = LowQualityPostsCheck.objects.filter(
                    low_ans_is=getAnswer, is_completed=False)

                if formData == "Looks_OK":
                    create_NegligibleInstance = LowQualityPostsCheck.objects.create(
                        suggested_by=request.user,
                        suggested_through="User-Reviewed",
                        low_ans_is=getAnswer,
                        why_low_quality="Reviewed")
                    getReviewItem.reviewers.add(request.user)
                    getLowQualityItem.how_many_votes_on_OK += 1
                    getLowQualityItem.save()
                    if getLowQualityItem.how_many_votes_on_OK >= 3:
                        getLowQualityItem.is_completed = True
                        getReviewItem.is_reviewed = True
                        getReviewItem.save()
                        getLowQualityItem.save()
                        for s in getAllVotes_ForSetToReviewed:
                            s.is_completed = True
                            s.save()
                            print("All the Votes are Reviewed and set to True \n")
                        print("Question is Good and Will Stay Open \n")

                    # getReviewItem.reviewActions = None
                    getReviewItem.save()
                    getAllLowQualityTask = ReviewLowQualityPosts.objects.filter(
                        reviewers=request.user).count()

                    if not ReviewLowQualityPosts.objects.filter(
                            reviewers=request.user).exists():
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Custodian",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Custodian",
                            description="Complete at least one review task. This badge is awarded once per review type"
                        )

                    if getAllLowQualityTask == 250:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="SILVER",
                            tag_name="Reviewer",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Reviewer",
                            description="Complete at least 250 review tasks. This badge is awarded once per review type"
                        )

                    if getAllLowQualityTask == 1000:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="GOLD",
                            tag_name="Steward",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Steward",
                            description="Complete at least 1000 review tasks. This badge is awarded once per review type"
                        )

                elif formData == "Edit":
                    create_NegligibleInstance = LowQualityPostsCheck.objects.create(
                        suggested_by=request.user,
                        suggested_through="User-Reviewed",
                        low_ans_is=getAnswer,
                        why_low_quality="Reviewed-Edited")
                    getReviewItem.reviewers.add(request.user)
                    getLowQualityItem.how_many_votes_on_OK += 1
                    getLowQualityItem.save()
                    if getLowQualityItem.how_many_votes_on_OK >= 3:
                        getLowQualityItem.is_completed = True
                        getReviewItem.is_reviewed = True
                        getReviewItem.save()
                        getLowQualityItem.save()
                        for s in getAllVotes_ForSetToReviewed:
                            s.is_completed = True
                            s.save()
                            print("All the Votes are Reviewed and set to True \n")
                        print("Question is Good and Will Stay Open \n")

                    # getReviewItem.reviewActions = None
                    getReviewItem.save()
                    getAllLowQualityTask = ReviewLowQualityPosts.objects.filter(
                        reviewers=request.user).count()

                    if not ReviewLowQualityPosts.objects.filter(
                            reviewers=request.user).exists():
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Custodian",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Custodian",
                            description="Complete at least one review task. This badge is awarded once per review type"
                        )

                    if getAllLowQualityTask == 250:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="SILVER",
                            tag_name="Reviewer",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Reviewer",
                            description="Complete at least 250 review tasks. This badge is awarded once per review type"
                        )

                    if getAllLowQualityTask == 1000:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="GOLD",
                            tag_name="Steward",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Steward",
                            description="Complete at least 1000 review tasks. This badge is awarded once per review type"
                        )

                elif formData == "Recommend_Delete":
                    create_NegligibleInstance = LowQualityPostsCheck.objects.create(
                        suggested_by=request.user,
                        suggested_through="User-Reviewed",
                        low_ans_is=getAnswer,
                        why_low_quality="Reviewed-Edited")
                    getReviewItem.reviewers.add(request.user)
                    getLowQualityItem.how_many_votes_on_deleteIt += 1
                    getLowQualityItem.save()
                    if getLowQualityItem.how_many_votes_on_deleteIt >= 3:
                        getLowQualityItem.is_completed = True
                        getReviewItem.is_reviewed = True
                        getReviewItem.save()
                        getLowQualityItem.save()
                        getAnswer.is_deleted = True
                        getAnswer.save()
                        for s in getAllVotes_ForSetToReviewed:
                            s.is_completed = True
                            s.save()
                            print("All the Votes are Reviewed and set to True \n")
                        print("Question is Good and Will Stay Open \n")

                    # getReviewItem.reviewActions = None
                    getReviewItem.save()
                    getAllLowQualityTask = ReviewLowQualityPosts.objects.filter(
                        reviewers=request.user).count()

                    if not ReviewLowQualityPosts.objects.filter(
                            reviewers=request.user).exists():
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Custodian",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Custodian",
                            description="Complete at least one review task. This badge is awarded once per review type"
                        )

                    if getAllLowQualityTask == 250:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="SILVER",
                            tag_name="Reviewer",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Reviewer",
                            description="Complete at least 250 review tasks. This badge is awarded once per review type"
                        )

                    if getAllLowQualityTask == 1000:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="GOLD",
                            tag_name="Steward",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Steward",
                            description="Complete at least 1000 review tasks. This badge is awarded once per review type"
                        )
                elif formData == "Skip":
                    getReviewItem.reviewers.add(request.user)

                next_LowQuality_Post = ReviewLowQualityPosts.objects.filter(
                    is_reviewed=False).exclude(reviewers=request.user).order_by('id').first()
                counting_2 = ReviewLowQualityPosts.objects.filter(
                    is_reviewed=False).exclude(
                    reviewers=request.user).count()

                if counting_2 >= 1:
                    return redirect(
                        'review:reviewLowQualityPosts',
                        reviewlowqualityposts_id=next_LowQuality_Post.id)
                else:
                    messages.error(
                        request, 'No More Posts to Review Low Quality Posts')
                    return redirect('profile:home')

    else:
        form = LowQualityReviewForm(
            instance=getReviewItem,
            data=request.POST,
            files=request.FILES)

    # data = get_object_or_404(Question, reviewlowqualityposts=getReviewItem)

    if getReviewItem.is_question:
        print("Question to Review In FrontEnd")
        is_question = True
        is_answer = False
        # data = Question.objects.filter(reviewflagpost=getReviewItem).first()
        data = get_object_or_404(Question, reviewlowqualityposts=getReviewItem)
        getThisItemFromReview = ReviewLowQualityPosts.objects.filter(
            is_question=data).first()
        getReviewersByVote = LowQualityPostsCheck.objects.filter(
            low_is=data).first()
        lastVoteWas = ReviewLowQualityPosts.objects.filter(
            is_question=data, is_reviewed=True).last()
        reviewers = getReviewItem.reviewers.all()

    # Question UpVote and DownVote
        likepost = data.qupvote_set.filter(upvote_by_q=request.user).first()
        likeDownpost = data.qdownvote_set.filter(
            downvote_by_q=request.user).first()
        upvotesCount = data.qupvote_set.all().count()
        downvotesCount = data.qdownvote_set.all().count()
        allToShowVotes = upvotesCount - downvotesCount
        getPostComments = data.commentq_set.all().exclude(deleted=True)

    elif getReviewItem.is_answer:
        print("Answer to Review In FrontEnd")
        is_question = False
        is_answer = True
        # data = Answer.objects.filter(reviewflagpost=getReviewItem).first()
        data = get_object_or_404(Answer, reviewlowqualityposts=getReviewItem)
        getThisItemFromReview = ReviewLowQualityPosts.objects.filter(
            is_answer=data).first()
        getReviewersByVote = LowQualityPostsCheck.objects.filter(
            low_ans_is=data).first()
        lastVoteWas = ReviewLowQualityPosts.objects.filter(
            is_answer=data, is_reviewed=True).last()
        getQuestionFromAnswer = Question.objects.get(answer=data)
        # reviewers = ReviewLowQualityPosts.objects.filter(pk=getReviewItem)
        reviewers = getReviewItem.reviewers.all()
        getPostComments = data.commentq_set.all().exclude(deleted=True)

    # Answer UpVote and DownVote
        likepost = data.questionans.qupvote_set.filter(
            upvote_by_q=request.user).first()
        likeDownpost = data.questionans.qdownvote_set.filter(
            downvote_by_q=request.user).first()
        upvotesCount = getQuestionFromAnswer.qupvote_set.all().count()
        downvotesCount = getQuestionFromAnswer.qdownvote_set.all().count()
        allToShowVotes = upvotesCount - downvotesCount

    is_reviewed = ''
    if getThisItemFromReview:
        if request.user in getThisItemFromReview.reviewers.all():
            is_reviewed = True
        else:
            is_reviewed = False

    context = {
        'getPostComments': getPostComments,
        'reviewers': reviewers,
        'getReviewersByVote': getReviewersByVote,
        'is_reviewed': is_reviewed,
        'likepost': likepost,
        'likeDownpost': likeDownpost,
        'data': data,
        'is_question': is_question,
        'lastVoteWas': lastVoteWas,
        'is_answer': is_answer,
        'allToShowVotes': allToShowVotes,
        'form': form,
        'getReviewItem': getReviewItem,
    }
    return render(request, 'review/Low_Quality_Post_Review.html', context)


@required_2000_RepToReview
def reviewClosedQuestions(request, reviewclosevotes_id):
    questionClose = get_object_or_404(ReviewCloseVotes, id=reviewclosevotes_id)
    data = Question.objects.get(reviewclosevotes=questionClose)
    getCloseHistorys = CloseQuestionVotes.objects.filter(
        question_to_closing=data).exclude(ended=True).first()

    # getClose_only_Leave_Open = CloseQuestionVotes.objects.filter(question_to_closing=data).filter(why_closing="Leave_open").first()
    getAllTheVotes = CloseQuestionVotes.objects.filter(
        question_to_closing=data).exclude(ended=True)

    # getClose_only_Leave_Open = CloseQuestionVotes.objects.filter(
    #                         question_to_closing=data).filter(Q(
    #                                 why_closing="Leave_open")).first()

    # getLast_completed_reason_of_review = ReviewCloseVotes.objects.filter(id=reviewclosevotes_id)

    # getLast_completed_reason_of_review = Question.objects.filter(reviewclosevotes__question_to_closed=data).first()

    getLast_completed_reason_of_review = data.reviewclosevotes_set.filter(
        is_completed=True).first()

    counting = ReviewCloseVotes.objects.filter(
        is_completed=False).exclude(
        reviewed_by=request.user).count()

    # if getLast_completed_reason_of_review == None:
    #     print("None sa")

    # print(getCloseHistorys)
    # print(data)

    if request.method == 'POST':
        if counting >= 1:
            form = ReviewCloseForm(
                instance=questionClose,
                data=request.POST,
                files=request.FILES)
            if form.is_valid():
                new_post = form.save(commit=False)
                formData = form.cleaned_data['reviewActions']
# COMMENTED OUT WORKING - START
                if formData == "Close":
                    getAllLowQualityTask = ReviewCloseVotes.objects.filter(
                        reviewed_by=request.user).count()

                    if not ReviewCloseVotes.objects.filter(
                            reviewed_by=request.user).exists():
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Custodian",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Custodian",
                            description="Complete at least one review task. This badge is awarded once per review type"
                        )

                    if getAllLowQualityTask == 250:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="SILVER",
                            tag_name="Reviewer",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Reviewer",
                            description="Complete at least 250 review tasks. This badge is awarded once per review type"
                        )

                    if getAllLowQualityTask == 1000:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="GOLD",
                            tag_name="Steward",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Steward",
                            description="Complete at least 1000 review tasks. This badge is awarded once per review type"
                        )

                    create_a_NewInstance = CloseQuestionVotes.objects.create(
                        user=request.user, question_to_closing=data, why_closing="Close")
                    questionClose.reviewed_by.add(request.user)
                    getCloseHistorys.how_many_votes_on_Close += 1
                    getCloseHistorys.save()
                    if getLast_completed_reason_of_review:
                        if getLast_completed_reason_of_review.how_Ended == "THROUGH_LEAVE_OPEN":
                            print("First Statement is Excecuting")
                            if getCloseHistorys.how_many_votes_on_Close >= getCloseHistorys.how_many_votes_on_Leave_open + 3:
                                questionClose.is_completed = True
                                print(
                                    "Added 1 to parent review user profile's helpful_close_votes \n")
                                # print(getCloseHistorys.user.profile)
                                getCloseHistorys.user.profile.helpful_close_votes += 1
                                getCloseHistorys.user.profile.save()
                                if getCloseHistorys.flagged_by.profile.helpful_flags_counter >= 80:
                                    TagBadge.objects.get_or_create(
                                        awarded_to_user=getCloseHistorys.user,
                                        badge_type="SILVER",
                                        tag_name="Deputy",
                                        bade_position="BADGE")
                                    PrivRepNotification.objects.get_or_create(
                                        for_user=getCloseHistorys.user, type_of_PrivNotify="BADGE_EARNED")
                                    PrivRepNotification.objects.get_or_create(
                                        for_user=getCloseHistorys.user,
                                        type_of_PrivNotify="BADGE_EARNED",
                                        url="#",
                                        for_if="Deputy",
                                        description="Raise 80 helpful flags"
                                    )
                                if getCloseHistorys.flagged_by.profile.helpful_flags_counter >= 500:
                                    TagBadge.objects.get_or_create(
                                        awarded_to_user=getCloseHistorys.user,
                                        badge_type="GOLD",
                                        tag_name="Marshal",
                                        bade_position="BADGE")
                                    PrivRepNotification.objects.get_or_create(
                                        for_user=getCloseHistorys.user,
                                        type_of_PrivNotify="BADGE_EARNED",
                                        url="#",
                                        for_if="Marshal",
                                        description="Raise 500 helpful flags"
                                    )

                                data.is_closed = True
                                data.closed_at = timezone.now()
                                data.save()
                                questionClose.finalResult = questionClose.review_of.why_closing
                                for s in getAllTheVotes:
                                    s.ended = True
                                    s.save()
                                questionClose.reviewed_by.add(request.user)
                                questionClose.how_Ended = "THROUGH_CLOSE"
                                questionClose.reviewActions = None
                                questionClose.save()
                                print("Second Statement is Excecuting")
                                print("Now Closed Successfully")
                        else:
                            # print("First Time Close")
                            if getCloseHistorys.how_many_votes_on_Close >= 3 and getCloseHistorys.how_many_votes_on_Close > getCloseHistorys.how_many_votes_on_Leave_open + 2:
                                questionClose.is_completed = True
                                getCloseHistorys.user.profile.helpful_close_votes += 1
                                getCloseHistorys.user.profile.save()
                                if getCloseHistorys.flagged_by.profile.helpful_flags_counter >= 80:
                                    # createMainTag = Tag.objects.get_or_create(name="Deputy")
                                    TagBadge.objects.get_or_create(
                                        awarded_to_user=getCloseHistorys.user,
                                        badge_type="SILVER",
                                        tag_name="Deputy",
                                        bade_position="BADGE")
                                    PrivRepNotification.objects.get_or_create(
                                        for_user=getCloseHistorys.user,
                                        type_of_PrivNotify="BADGE_EARNED",
                                        url="#",
                                        for_if="Deputy",
                                        description="Raise 80 helpful flags"
                                    )
                                if getCloseHistorys.flagged_by.profile.helpful_flags_counter >= 500:
                                    # createMainTag = Tag.objects.get_or_create(name="Deputy")
                                    TagBadge.objects.get_or_create(
                                        awarded_to_user=getCloseHistorys.user,
                                        badge_type="GOLD",
                                        tag_name="Marshal",
                                        bade_position="BADGE")
                                    PrivRepNotification.objects.get_or_create(
                                        for_user=getCloseHistorys.user,
                                        type_of_PrivNotify="BADGE_EARNED",
                                        url="#",
                                        for_if="Marshal",
                                        description="Raise 500 helpful flags"
                                    )

                                print(
                                    "Added 1 to parent review user profile's helpful_close_votes \n")
                                # print(getCloseHistorys.user.profile)
                                questionClose.reviewed_by.add(request.user)
                                questionClose.how_Ended = "THROUGH_CLOSE"
                                questionClose.finalResult = questionClose.review_of.why_closing
                                data.is_closed = True
                                data.closed_at = timezone.now()
                                data.save()
                                for s in getAllTheVotes:
                                    s.ended = True
                                    s.save()
                                print("Third Statement is Excecuting in Closing")
                                questionClose.reviewActions = None
                                questionClose.save()

                    else:
                        # CHANGE GREATER THAN 3 INTO
                        # "getCloseHistorys.how_many_votes_on_Close >
                        # getCloseHistorys.how_many_votes_on_Leave_open + 2"
                        if getCloseHistorys.how_many_votes_on_Close >= 3 and getCloseHistorys.how_many_votes_on_Close > getCloseHistorys.how_many_votes_on_Leave_open:
                            questionClose.is_completed = True
                            questionClose.reviewed_by.add(request.user)
                            print(
                                "Added 1 to parent review user profile's helpful_close_votes \n")
                            # print(getCloseHistorys.user.profile)
                            getCloseHistorys.user.profile.helpful_close_votes += 1
                            getCloseHistorys.user.profile.save()
                            if getCloseHistorys.user.profile.helpful_flags_counter >= 80:
                                # createMainTag = Tag.objects.get_or_create(name="Deputy")
                                TagBadge.objects.get_or_create(
                                    awarded_to_user=getCloseHistorys.user,
                                    badge_type="SILVER",
                                    tag_name="Deputy",
                                    bade_position="BADGE")
                                PrivRepNotification.objects.get_or_create(
                                    for_user=getCloseHistorys.user,
                                    type_of_PrivNotify="BADGE_EARNED",
                                    url="#",
                                    for_if="Deputy",
                                    description="Raise 80 helpful flags"
                                )
                            if getCloseHistorys.user.profile.helpful_flags_counter >= 500:
                                # createMainTag = Tag.objects.get_or_create(name="Deputy")
                                TagBadge.objects.get_or_create(
                                    awarded_to_user=getCloseHistorys.user,
                                    badge_type="GOLD",
                                    tag_name="Marshal",
                                    bade_position="BADGE")
                                PrivRepNotification.objects.get_or_create(
                                    for_user=getCloseHistorys.user,
                                    type_of_PrivNotify="BADGE_EARNED",
                                    url="#",
                                    for_if="Marshal",
                                    description="Raise 500 helpful flags"
                                )

                            questionClose.how_Ended = "THROUGH_CLOSE"
                            # questionClose.finalResult = questionClose.review_of.why_closing
                            questionClose.reviewActions = None
                            data.is_closed = True
                            data.closed_at = timezone.now()
                            for s in getAllTheVotes:
                                s.ended = True
                                s.save()
                            data.save()
                            print("Fourth Statement is Excecuting")
                            questionClose.save()
                    getAllLowQualityTask = ReviewCloseVotes.objects.filter(
                        reviewed_by=request.user).count()

                    if not ReviewCloseVotes.objects.filter(
                            reviewed_by=request.user).exists():
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Custodian",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Custodian",
                            description="Complete at least one review task. This badge is awarded once per review type"
                        )

                    if getAllLowQualityTask == 250:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="SILVER",
                            tag_name="Reviewer",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Reviewer",
                            description="Complete at least 250 review tasks. This badge is awarded once per review type"
                        )

                    if getAllLowQualityTask == 1000:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="GOLD",
                            tag_name="Steward",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Steward",
                            description="Complete at least 1000 review tasks. This badge is awarded once per review type"
                        )

                    next_blog = ReviewCloseVotes.objects.filter(
                        is_completed=False).exclude(
                        reviewed_by=request.user).order_by('id').first()
                    counting_2 = ReviewCloseVotes.objects.filter(
                        is_completed=False).exclude(
                        reviewed_by=request.user).count()

                    if counting_2 >= 1:
                        return redirect(
                            'review:reviewClosedQuestions',
                            reviewclosevotes_id=next_blog.id)
                    else:
                        messages.error(
                            request, 'No More Posts to Review Close Question Votes')
                        return redirect('profile:home')
# COMMENTED OUT WORKING - END


# COMMENTED OUT NOT-WORKING - START
                elif formData == "Leave_open":
                    create_a_NewInstance = CloseQuestionVotes.objects.create(
                        user=request.user, question_to_closing=data, why_closing="Leave_open")
                    getCloseHistorys.how_many_votes_on_Leave_open += 1
                    questionClose.reviewed_by.add(request.user)
                    getCloseHistorys.save()
                    if getLast_completed_reason_of_review:
                        if getLast_completed_reason_of_review.how_Ended == "THROUGH_CLOSE":
                            if getCloseHistorys.how_many_votes_on_Leave_open >= 3 and getCloseHistorys.how_many_votes_on_Leave_open > getCloseHistorys.how_many_votes_on_Close:
                                questionClose.how_Ended = "THROUGH_LEAVE_OPEN"
                                questionClose.reviewed_by.add(request.user)
                                questionClose.is_completed = True
                                questionClose.reviewActions = None
                                for s in getAllTheVotes:
                                    s.ended = True
                                    s.save()
                                questionClose.save()

                        else:
                            if getCloseHistorys.how_many_votes_on_Leave_open >= 3 and getCloseHistorys.how_many_votes_on_Leave_open > getCloseHistorys.how_many_votes_on_Close:
                                questionClose.is_completed = True
                                questionClose.how_Ended = "THROUGH_LEAVE_OPEN"
                                questionClose.reviewed_by.add(request.user)
                                for s in getAllTheVotes:
                                    s.ended = True
                                    s.save()
                                questionClose.reviewActions = None
                                questionClose.save()
                    else:
                        # print("First Time Leave Open")
                        if getCloseHistorys.how_many_votes_on_Leave_open >= 3 and getCloseHistorys.how_many_votes_on_Leave_open > getCloseHistorys.how_many_votes_on_Close:
                            questionClose.is_completed = True
                            for s in getAllTheVotes:
                                s.ended = True
                                s.save()
                            print("Leave Open Third Statement is Excecuting")
                            questionClose.how_Ended = "THROUGH_LEAVE_OPEN"
                            questionClose.reviewed_by.add(request.user)
                            questionClose.reviewActions = None
                            questionClose.save()
                    next_blog = ReviewCloseVotes.objects.filter(
                        is_completed=False).exclude(
                        reviewed_by=request.user).order_by('id').first()
                    counting_2 = ReviewCloseVotes.objects.filter(
                        is_completed=False).exclude(
                        reviewed_by=request.user).count()
                    getAllLowQualityTask = ReviewCloseVotes.objects.filter(
                        reviewed_by=request.user).count()

                    if not ReviewCloseVotes.objects.filter(
                            reviewed_by=request.user).exists():
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Custodian",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Custodian",
                            description="Complete at least one review task. This badge is awarded once per review type"
                        )

                    if getAllLowQualityTask == 250:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="SILVER",
                            tag_name="Reviewer",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Reviewer",
                            description="Complete at least 250 review tasks. This badge is awarded once per review type"
                        )

                    if getAllLowQualityTask == 1000:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="GOLD",
                            tag_name="Steward",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Steward",
                            description="Complete at least 1000 review tasks. This badge is awarded once per review type"
                        )

                    if counting_2 >= 1:
                        return redirect(
                            'review:reviewClosedQuestions',
                            reviewclosevotes_id=next_blog.id)
                    else:
                        messages.error(
                            request, 'No More Posts to Review Close Question Votes')
                        return redirect('profile:home')
# COMMENTED OUT NOT-WORKING - END

                elif formData == "Edit":
                    create_a_NewInstance = CloseQuestionVotes.objects.create(
                        user=request.user, question_to_closing=data, why_closing="Leave_open")
                    getCloseHistorys.how_many_votes_on_Leave_open += 1
                    questionClose.reviewed_by.add(request.user)
                    getCloseHistorys.save()
                    if getLast_completed_reason_of_review:
                        if getLast_completed_reason_of_review.how_Ended == "THROUGH_CLOSE":
                            if getCloseHistorys.how_many_votes_on_Leave_open >= 3 and getCloseHistorys.how_many_votes_on_Leave_open > getCloseHistorys.how_many_votes_on_Close:
                                questionClose.how_Ended = "THROUGH_LEAVE_OPEN"
                                print("Leave Open First Statement is Excecuting")
                                questionClose.reviewed_by.add(request.user)
                                questionClose.is_completed = True
                                questionClose.reviewActions = None
                                for s in getAllTheVotes:
                                    s.ended = True
                                    s.save()
                                questionClose.save()

                        else:
                            if getCloseHistorys.how_many_votes_on_Leave_open >= 3 and getCloseHistorys.how_many_votes_on_Leave_open > getCloseHistorys.how_many_votes_on_Close:
                                questionClose.is_completed = True
                                print("Leave Open Second Statement is Excecuting")
                                questionClose.how_Ended = "THROUGH_LEAVE_OPEN"
                                questionClose.reviewed_by.add(request.user)
                                for s in getAllTheVotes:
                                    s.ended = True
                                    s.save()
                                questionClose.reviewActions = None
                                questionClose.save()
                    else:
                        # print("First Time Leave Open")
                        if getCloseHistorys.how_many_votes_on_Leave_open >= 3 and getCloseHistorys.how_many_votes_on_Leave_open > getCloseHistorys.how_many_votes_on_Close:
                            questionClose.is_completed = True
                            for s in getAllTheVotes:
                                s.ended = True
                                s.save()
                            print("Leave Open Third Statement is Excecuting")
                            questionClose.how_Ended = "THROUGH_LEAVE_OPEN"
                            questionClose.reviewed_by.add(request.user)
                            questionClose.reviewActions = None
                            questionClose.save()
                    getAllLowQualityTask = ReviewCloseVotes.objects.filter(
                        reviewed_by=request.user).count()

                    if not ReviewCloseVotes.objects.filter(
                            reviewed_by=request.user).exists():
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Custodian",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Custodian",
                            description="Complete at least one review task. This badge is awarded once per review type"
                        )

                    if getAllLowQualityTask == 250:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="SILVER",
                            tag_name="Reviewer",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Reviewer",
                            description="Complete at least 250 review tasks. This badge is awarded once per review type"
                        )

                    if getAllLowQualityTask == 1000:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="GOLD",
                            tag_name="Steward",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Steward",
                            description="Complete at least 1000 review tasks. This badge is awarded once per review type"
                        )

                    next_blog = ReviewCloseVotes.objects.filter(
                        is_completed=False).exclude(
                        reviewed_by=request.user).order_by('id').first()
                    counting_2 = ReviewCloseVotes.objects.filter(
                        is_completed=False).exclude(
                        reviewed_by=request.user).count()

                    if counting_2 >= 1:
                        return redirect(
                            'review:reviewClosedQuestions',
                            reviewclosevotes_id=next_blog.id)
                    else:
                        messages.error(
                            request, 'No More Posts to Review Close Question Votes')
                        return redirect('profile:home')

                elif formData == "Skip":
                    questionClose.reviewed_by.add(request.user)
                    next_blog = ReviewCloseVotes.objects.filter(
                        is_completed=False).exclude(
                        reviewed_by=request.user).order_by('id').first()
                    counting_2 = ReviewCloseVotes.objects.filter(
                        is_completed=False).exclude(
                        reviewed_by=request.user).count()

        else:
            messages.error(
                request, 'No More Posts to Review Close Question Votes')
            return redirect('profile:home')

    else:
        form = ReviewCloseForm(request.POST or None,
                               request.FILES or None, instance=questionClose)

    getAll_Votes_required_in_close_and_completed = CloseQuestionVotes.objects.filter(
        question_to_closing=data).filter(
        Q(
            why_closing="NEED_TO_MORE_FOCUSED") | Q(
                why_closing="DUPLICATE") | Q(
                    why_closing="NEED_ADDITIONAL_DETAILS") | Q(
                        why_closing="OPINION_BASED") | Q(
                            why_closing="Close") | Q(
                                why_closing="Leave_open")).exclude(
                                    ended=True)

    if request.method == 'POST':
        editQ = UpdateQuestion(
            instance=data,
            data=request.POST,
            files=request.FILES)

        if editQ.is_valid():
            editQ.save()
            # next_blog = Question.objects.filter(reviewclosevotes__reviewActions__isnull=True).order_by('id').first()
            # return
            # redirect('review:reviewClosedQuestions',question_id=next_blog.id)

    else:
        editQ = UpdateQuestion(
            request.POST or None,
            request.FILES or None,
            instance=data)

    upvotesCount = data.qupvote_set.all().count()
    downvotesCount = data.qdownvote_set.all().count()
    allToShowVotes = upvotesCount - downvotesCount

    getThisItemFromReview = ReviewCloseVotes.objects.filter(
        question_to_closed=data).first()

    is_reviewed = ''
    if getThisItemFromReview:
        if request.user in getThisItemFromReview.reviewed_by.all():
            is_reviewed = True
        else:
            is_reviewed = False
    # print(actionWas)

    # getReviewers = getThisItemFromReview.reviewed_by.all()

    getReviewersByVote = CloseQuestionVotes.objects.filter(
        question_to_closing=data)

    # for rev in getReviewersByVote:
    # print(getReviewersByVote)

    if getThisItemFromReview:
        endedThrough = ''
        if getThisItemFromReview.how_Ended == "THROUGH_CLOSE":
            endedThrough = "voted_For_Close"
        elif getThisItemFromReview.how_Ended == "THROUGH_LEAVE_OPEN":
            endedThrough = "voted_For_Leave_Open"
        elif getThisItemFromReview.how_Ended == "THROUGH_LEAVE_OPEN":
            endedThrough = "Edited_and_Leave_Open"
    else:
        endedThrough = ''
    print(endedThrough)

    context = {
        'getReviewersByVote': getReviewersByVote,
        'getThisItemFromReview': getThisItemFromReview,
        'endedThrough': endedThrough,
        'is_reviewed': is_reviewed,
        'editQ': editQ,
        'data': data,
        'questionClose': questionClose,
        'form': form,
        'getAll_Votes_required_in_close_and_completed': getAll_Votes_required_in_close_and_completed,
    }
    return render(request, 'review/Close_Q_Review.html', context)


# Uncomment it without testing
# @highModRequired
def reviewFlagPosts(request, reviewflagpost_id):
    getReviewItem = get_object_or_404(ReviewFlagPost, pk=reviewflagpost_id)
    # getQuestion = Question.objects.get(reviewflagpost=getReviewItem)

    if getReviewItem.flag_question_to_view:
        print("Question Flag to Review")
    else:
        print("Answer Flag to Review")

    if request.method == 'POST':
        form = FlagPostForm(
            instance=getReviewItem,
            data=request.POST,
            files=request.FILES)
        if form.is_valid():
            formData = form.cleaned_data['flagReviewActions']

            if getReviewItem.flag_question_to_view:
                getQuestion = Question.objects.get(
                    reviewflagpost=getReviewItem)
                getFlagVoteItem = FlagPost.objects.filter(
                    question_forFlag=getQuestion, ended=False).first()

                if formData == "DELETE_IT":
                    getQuestion.is_deleted = True
                    getReviewItem.flag_reviewed_by = request.user
                    getFlagVoteItem.ended = True
                    getReviewItem.flag_is_reviewed = True
                    getQuestion.save()
                    getReviewItem.save()
                    getFlagVoteItem.save()
                    getFlagVoteItem.flagged_by.profile.helpful_flags_counter += 1
                    getFlagVoteItem.flagged_by.profile.save()
                    if getFlagVoteItem.flagged_by.profile.helpful_flags_counter >= 80:
                        TagBadge.objects.get_or_create(
                            awarded_to_user=getFlagVoteItem.flagged_by,
                            badge_type="SILVER",
                            tag_name="Deputy",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=getCloseHistorys.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Deputy",
                            description="Raise 80 helpful flags"
                        )
                    if getFlagVoteItem.flagged_by.profile.helpful_flags_counter >= 500:
                        TagBadge.objects.get_or_create(
                            awarded_to_user=getFlagVoteItem.flagged_by,
                            badge_type="GOLD",
                            tag_name="Marshal",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=getCloseHistorys.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Marshal",
                            description="Raise 500 helpful flags"
                        )

                elif formData == "CLOSE_IT":
                    # getQuestion.is_closed = True
                    # getQuestion.closed_at = timezone.now()
                    getReviewItem.flag_reviewed_by = request.user
                    getFlagVoteItem.ended = True
                    getReviewItem.flag_is_reviewed = True
                    getQuestion.is_closed = True
                    data.closed_at = timezone.now()
                    getQuestion.save()
                    getReviewItem.save()
                    getFlagVoteItem.save()
                    getFlagVoteItem.flagged_by.profile.helpful_flags_counter += 1
                    getFlagVoteItem.flagged_by.profile.save()
                    if getFlagVoteItem.flagged_by.profile.helpful_flags_counter >= 80:
                        # createMainTag = Tag.objects.get_or_create(name="Deputy")
                        TagBadge.objects.get_or_create(
                            awarded_to_user=getFlagVoteItem.flagged_by,
                            badge_type="SILVER",
                            tag_name="Deputy",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=getCloseHistorys.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Deputy",
                            description="Raise 80 helpful flags"
                        )
                    if getFlagVoteItem.flagged_by.profile.helpful_flags_counter >= 500:
                        # createMainTag = Tag.objects.get_or_create(name="Deputy")
                        TagBadge.objects.get_or_create(
                            awarded_to_user=getFlagVoteItem.flagged_by,
                            badge_type="GOLD",
                            tag_name="Marshal",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=getCloseHistorys.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Marshal",
                            description="Raise 500 helpful flags"
                        )

                elif formData == "STAY_AS_IT_IS":
                    getReviewItem.flag_is_reviewed = True
                    getFlagVoteItem.ended = True
                    getReviewItem.flag_reviewed_by = request.user
                    getQuestion.save()
                    getReviewItem.save()
                    getFlagVoteItem.save()

                else:
                    # messages.error(request, "Skip is Typed")
                    getReviewItem.flag_reviewed_by = request.user
                    getReviewItem.save()

                next_flag_post = ReviewFlagPost.objects.filter(
                    flag_is_reviewed=False).exclude(
                    flag_reviewed_by=request.user).order_by('id').first()
                counting = ReviewFlagPost.objects.filter(
                    flag_is_reviewed=False).exclude(
                    flag_reviewed_by=request.user).count()

                if counting >= 1:
                    return redirect(
                        'review:reviewFlagPosts',
                        reviewflagpost_id=next_flag_post.id)
                else:
                    messages.error(request, 'No More Post Flags To Review')
                    return redirect('profile:home')
            else:
                getAnswer = Answer.objects.get(reviewflagpost=getReviewItem)
                getFlagVoteItem = FlagPost.objects.filter(
                    answer_forFlag=getAnswer, ended=False).first()

                if formData == "DELETE_IT":
                    getAnswer.is_deleted = True
                    getReviewItem.flag_reviewed_by = request.user
                    getFlagVoteItem.ended = True
                    getReviewItem.flag_is_reviewed = True
                    getAnswer.save()
                    getReviewItem.save()
                    getFlagVoteItem.save()
                    getFlagVoteItem.flagged_by.profile.helpful_flags_counter += 1
                    getFlagVoteItem.flagged_by.profile.save()
                    if getFlagVoteItem.flagged_by.profile.helpful_flags_counter >= 80:
                        # createMainTag = Tag.objects.get_or_create(name="Deputy")
                        TagBadge.objects.get_or_create(
                            awarded_to_user=getFlagVoteItem.flagged_by,
                            badge_type="SILVER",
                            tag_name="Deputy",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=getCloseHistorys.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Deputy",
                            description="Raise 80 helpful flags"
                        )
                    if getFlagVoteItem.flagged_by.profile.helpful_flags_counter >= 500:
                        # createMainTag = Tag.objects.get_or_create(name="Deputy")
                        TagBadge.objects.get_or_create(
                            awarded_to_user=getFlagVoteItem.flagged_by,
                            badge_type="GOLD",
                            tag_name="Marshal",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=getCloseHistorys.user,
                            type_of_PrivNotify="BADGE_EARNED",
                            url="#",
                            for_if="Marshal",
                            description="Raise 500 helpful flags"
                        )
            # Answer cannot be closed
                # elif formData == "CLOSE_IT":
                #     getAnswer.is_closed = True
                #     getReviewItem.flag_reviewed_by.add(request.user)
                #     getFlagVoteItem.ended = True
                #     getReviewItem.flag_is_reviewed = True
                #     getAnswer.save()
                #     getReviewItem.save()
                #     getFlagVoteItem.save()

                elif formData == "STAY_AS_IT_IS":
                    getReviewItem.flag_is_reviewed = True
                    getFlagVoteItem.ended = True
                    getReviewItem.flag_reviewed_by = request.user
                    getAnswer.save()
                    getReviewItem.save()
                    getFlagVoteItem.save()

                else:
                    # messages.error(request, "Skip is Typed")
                    getReviewItem.flag_reviewed_by = request.user
                    getReviewItem.save()

                next_flag_post = ReviewFlagPost.objects.filter(
                    flag_is_reviewed=False).exclude(
                    flag_reviewed_by=request.user).order_by('id').first()
                counting = ReviewFlagPost.objects.filter(
                    flag_is_reviewed=False).exclude(
                    flag_reviewed_by=request.user).count()

                if counting >= 1:
                    return redirect(
                        'review:reviewFlagPosts',
                        reviewflagpost_id=next_flag_post.id)
                else:
                    messages.error(request, 'No More Post Flags To Review')
                    return redirect('profile:home')

    else:
        form = FlagPostForm(
            instance=getReviewItem,
            data=request.POST,
            files=request.FILES)

    if getReviewItem.flag_question_to_view:
        print("Question to Review")
        is_question = True
        is_answer = False
        data = Question.objects.filter(reviewflagpost=getReviewItem).first()
        # Try to implement this in models
        likepost = data.qupvote_set.filter(upvote_by_q=request.user).first()
        likeDownpost = data.qdownvote_set.filter(
            downvote_by_q=request.user).first()
        getThisItemFromReview = ReviewFlagPost.objects.filter(
            flag_question_to_view=data).first()
        getReviewersByVote = FlagPost.objects.filter(
            question_forFlag=data).first()
        lastVoteWas = ReviewFlagPost.objects.filter(
            flag_question_to_view=data, flag_is_reviewed=True).last()
        upvotesCount = data.qupvote_set.all().count()
        downvotesCount = data.qdownvote_set.all().count()
        allToShowVotes = upvotesCount - downvotesCount
    elif getReviewItem.flag_answer_to_view_if:
        print("Answer to Review")
        is_question = False
        is_answer = True
        data = Answer.objects.filter(reviewflagpost=getReviewItem).first()
        getThisItemFromReview = ReviewFlagPost.objects.filter(
            flag_answer_to_view_if=data).first()
        getReviewersByVote = FlagPost.objects.filter(
            answer_forFlag=data).first()
        lastVoteWas = ReviewFlagPost.objects.filter(
            flag_answer_to_view_if=data, flag_is_reviewed=True).last()
        getQuestionFromAnswer = Question.objects.get(answer=data)
        # Try to implement this in models
        likepost = data.questionans.qupvote_set.filter(
            upvote_by_q=request.user).first()
        likeDownpost = data.questionans.qdownvote_set.filter(
            downvote_by_q=request.user).first()
        upvotesCount = getQuestionFromAnswer.qupvote_set.all().count()
        downvotesCount = getQuestionFromAnswer.qdownvote_set.all().count()
        allToShowVotes = upvotesCount - downvotesCount

    is_reviewed = ''
    if getThisItemFromReview:
        if getThisItemFromReview.flag_is_reviewed:
            is_reviewed = True
        else:
            is_reviewed = False

    context = {
        'getReviewItem': getReviewItem,
        'getReviewersByVote': getReviewersByVote,
        'likeDownpost': likeDownpost,
        'likepost': likepost,
        'allToShowVotes': allToShowVotes,
        'lastVoteWas': lastVoteWas,
        'getThisItemFromReview': getThisItemFromReview,
        'getReviewersByVote': getReviewersByVote,
        'is_reviewed': is_reviewed,
        'data': data,
        'is_question': is_question,
        'is_answer': is_answer,
        'form': form}
    return render(request, 'review/Flag_Post_Review.html', context)


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

    if totalReputation >= 10:
        # Create Wiki Posts - DONE
        which_user.profile.create_wiki_posts = True
        # Answer Protect Questions - DONE
        which_user.profile.remove_new_user_restrictions = True
        which_user.profile.save()
        PrivRepNotification.objects.get_or_create(
            for_user=which_user,
            privilegeURL="#",
            type_of_PrivNotify="Privilege_Earned")
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

    if totalReputation >= 15:
        # Vote Up Priv - DONE
        which_user.profile.voteUpPriv = True
        # FlagPost - DONE But Not, Need to Save Flag Request through Ajax
        which_user.profile.flag_posts = True
        PrivRepNotification.objects.get_or_create(
            for_user=which_user,
            privilegeURL="#",
            for_if="Up Vote",
            type_of_PrivNotify="Privilege_Earned")
        which_user.profile.save()
    else:
        # Vote Up Priv - DONE
        which_user.profile.voteUpPriv = False
        # FlagPost - DONE But Not, Need to Save Flag Request through Ajax
        which_user.profile.flag_posts = False
        which_user.profile.save()

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


@required_2000_RepToReview
def reviewSuggesstedEdit(request, reviewquestionedit_id):
    getReviewItem = get_object_or_404(
        ReviewQuestionEdit, pk=reviewquestionedit_id)
    # getVoteItem = QuestionEditVotes.objects.filter(reviewquestionedit=getReviewItem).first()
    # if getReviewItem.question_to_view:
    #     getQuestion = Question.objects.get(reviewquestionedit=getReviewItem)
    #     getQuestion = QuestionEditVotes.objects.filter(edited_question=getQuestion).first()
    # else:
    #     getAnswer = Answer.objects.get(reviewquestionedit=getReviewItem)

    if getReviewItem.question_to_view:
        data = Question.objects.get(reviewquestionedit=getReviewItem)
        ItIsQuestion = True
        getQuestionHistory = data.his.first()
        getAnswerHitory = ''
    else:
        ItIsQuestion = False
        data = Answer.objects.get(reviewquestionedit=getReviewItem)
        getAnswerHitory = data.anshis.first()
        getQuestionHistory = ''

    if getReviewItem.question_to_view:
        getQuestion = Question.objects.get(reviewquestionedit=getReviewItem)
        if request.method == 'POST':
            edit_Q_Form = UpdateQuestion(
                instance=getQuestion,
                data=request.POST,
                files=request.FILES)
            if edit_Q_Form.is_valid():
                edit_Q_Form.save()
                # next_question = Question.objects.filter(firstquestionreview__QuestionReviewBy__isnull=True).order_by('id').first()
                return redirect(
                    'review:review_FirstQns',
                    question_id=next_question.id)

        else:
            edit_Q_Form = UpdateQuestion(request.POST or None,
                                         request.FILES or None,
                                         instance=getQuestion)
    else:
        edit_Q_Form = ''

    if getReviewItem.answer_to_view_if:
        getAnswer = Answer.objects.get(reviewquestionedit=getReviewItem)
        if request.method == 'POST':
            editAnswerForm = EditAnswerForm(instance=getAnswer,
                                            data=request.POST,
                                            files=request.FILES)
            if editAnswerForm.is_valid():
                editAnswerForm.save()
                # next_blog = Answer.objects.filter(firstanswerreview__actions__isnull=True).order_by('id').first()
                return redirect(
                    'review:review_FirstAns',
                    answer_id=next_blog.id)

            else:
                messages.error(request, 'Something went Wrong !')

        else:
            editAnswerForm = EditAnswerForm(request.POST or None,
                                            request.FILES or None,
                                            instance=getAnswer)
    else:
        editAnswerForm = ''

    if getReviewItem.question_to_view:
        print("Question to Review")
    else:
        print("Answer to Review")

    # getQuestion = Question.objects.get(reviewquestionedit=getReviewItem)
    # getQuestion = get_object_or_404(Question, reviewquestionedit=getReviewItem)
    # getQuestion = ''
    # getVoteItem = getQuestion.reviewquestionedit_set.filter(is_reviewed=True).first()

    if request.method != 'POST':
        form = SuggesstedEditForm(
            instance=getReviewItem,
            data=request.POST,
            files=request.FILES)

    else:
        form = SuggesstedEditForm(
            instance=getReviewItem,
            data=request.POST,
            files=request.FILES)
        if form.is_valid():
            formData = form.cleaned_data['reviewActions']

        if getReviewItem.question_to_view:
            getQuestion = Question.objects.get(
                reviewquestionedit=getReviewItem)
            # getQuestion = QuestionEditVotes.objects.filter(edited_question=getQuestion).first()
            getVoteItem = QuestionEditVotes.objects.filter(
                edited_question=getQuestion, is_completed=False, rev_Action=None).first()

# If last vote is not reviewed yet then alert the popup

            if getQuestion.post_owner == request.user:
                if formData == "Approve":
                    print("Reviewed by Owner")
                    create_a_NewInstance = QuestionEditVotes.objects.create(
                        edit_suggested_by=request.user, edited_question=getQuestion, rev_Action="Approve")
                    getReviewItem.edit_reviewed_by.add(request.user)
                    getVoteItem.how_many_votes_on_approve += 1
                    # getReviewItem.reviewActions = None
                    getVoteItem.is_completed = True
                    getReviewItem.is_reviewed = True
                    getVoteItem.edit_suggested_by.profile.suggested_Edit_counter += 1
                    getVoteItem.edit_suggested_by.profile.save()
                    getReviewItem.save()
                    getVoteItem.save()
                    question_URL = request.build_absolute_uri(
                        getQuestion.get_absolute_url())
                    createARep_Notification = PrivRepNotification.objects.get_or_create(
                        for_user=data.post_owner,
                        url=question_URL,
                        type_of_PrivNotify="EDIT_GOT_APPROVED",
                        missingReputation=2)
                    getAllEditVotes = QuestionEditVotes.objects.filter(
                        edited_question=getQuestion)
                    for _metaReview in getAllEditVotes:
                        # print("Printing the Error on Line 865")
                        _metaReview.is_completed = True
                        _metaReview.save()
                    return redirect('profile:home')

                if formData == "Reject":
                    print("Reviewed by Owner")
                    create_a_NewInstance = QuestionEditVotes.objects.create(
                        edit_suggested_by=request.user, edited_question=getQuestion, rev_Action="Reject")
                    getReviewItem.edit_reviewed_by.add(request.user)
                    getVoteItem.how_many_votes_on_approve += 1
                    # getReviewItem.reviewActions = None
                    getVoteItem.is_completed = True
                    getReviewItem.is_reviewed = True
                    getVoteItem.edit_suggested_by.profile.suggested_Edit_counter += 1
                    getVoteItem.edit_suggested_by.profile.save()
                    getReviewItem.save()
                    getVoteItem.save()
                    getDat = getQuestion.history.first()
                    getNextRecord = getQuestion.history.earliest().delete()

                    getQuestion.body = getDat.prev_record.body
                    getQuestion.title = getDat.prev_record.title
                    getQuestion.save()
                    getDat = getQuestion.history.first()
                    deletePrev = getDat.prev_record.delete()
                    print("Deleting and Editing Previous Record is Done")
                    getAllLowQualityTask = ReviewQuestionEdit.objects.filter(
                        edit_reviewed_by=request.user).count()

                    if not ReviewQuestionEdit.objects.filter(
                            edit_reviewed_by=request.user).exists():
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Custodian",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if getAllLowQualityTask == 250:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="SILVER",
                            tag_name="Reviewer",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if getAllLowQualityTask == 1000:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="GOLD",
                            tag_name="Steward",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    getAllEditVotes = QuestionEditVotes.objects.filter(
                        edited_question=getQuestion)
                    for _metaReview in getAllEditVotes:
                        # print("Printing the Error on Line 865")
                        _metaReview.is_completed = True
                        _metaReview.save()
                    return redirect('profile:home')
            else:
                if formData == "Approve":
                    create_a_NewInstance = QuestionEditVotes.objects.create(
                        edit_suggested_by=request.user, edited_question=getQuestion, rev_Action="Approve")
                    getReviewItem.edit_reviewed_by.add(request.user)
                    getVoteItem.how_many_votes_on_approve += 1
                    getVoteItem.save()
                    # getReviewItem.reviewActions = None
                    getReviewItem.save()
                    if getVoteItem.how_many_votes_on_approve > getVoteItem.how_many_votes_on_reject and getVoteItem.how_many_votes_on_approve > 2:
                        awardUser = Reputation.objects.create(
                            awarded_to=getVoteItem.edit_suggested_by,
                            question_O=getQuestion,
                            question_rep_C=2,
                            reputation_on_what="EDIT")
                        rewardPrivielege(
                            request, getVoteItem.edit_suggested_by)
                        getVoteItem.is_completed = True
                        question_URL = request.build_absolute_uri(
                            getQuestion.get_absolute_url())
                        createARep_Notification = PrivRepNotification.objects.get_or_create(
                            for_user=data.post_owner,
                            url=question_URL,
                            type_of_PrivNotify="EDIT_GOT_APPROVED",
                            missingReputation=2)

                        getReviewItem.is_reviewed = True
                        getReviewItem.save()
                        getVoteItem.save()
                        getAllEditVotes = QuestionEditVotes.objects.filter(
                            edited_question=getQuestion)
                        for _metaReview in getAllEditVotes:
                            # print("Printing the Error on Line 865")
                            _metaReview.is_completed = True
                            _metaReview.save()
                    request.user.profile.suggested_Edit_counter += 1
                    request.user.profile.save()
                    if request.user.profile.suggested_Edit_counter == 100:
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Proofreader",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")
                    next_blog = ReviewQuestionEdit.objects.filter(
                        is_reviewed=False).exclude(
                        edit_reviewed_by=request.user).order_by('id').first()
                    counting_2 = ReviewQuestionEdit.objects.filter(
                        is_reviewed=False).exclude(
                        edit_reviewed_by=request.user).count()
                    getAllLowQualityTask = ReviewQuestionEdit.objects.filter(
                        edit_reviewed_by=request.user).count()

                    if not ReviewQuestionEdit.objects.filter(
                            edit_reviewed_by=request.user).exists():
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Custodian",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if getAllLowQualityTask == 250:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="SILVER",
                            tag_name="Reviewer",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if getAllLowQualityTask == 1000:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="GOLD",
                            tag_name="Steward",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if counting_2 >= 1:
                        return redirect(
                            'review:reviewSuggesstedEdit',
                            reviewquestionedit_id=next_blog.id)
                    else:
                        messages.error(
                            request, 'No More Suggessted Edits to Review')
                        return redirect('profile:home')

                elif formData == "Reject":
                    print("User is Rejecting")
                    create_a_NewInstance = QuestionEditVotes.objects.create(
                        edit_suggested_by=request.user, edited_question=getQuestion, rev_Action="Reject")
                    getReviewItem.edit_reviewed_by.add(request.user)
                    getVoteItem.how_many_votes_on_reject += 1
                    getVoteItem.save()
                    # getReviewItem.reviewActions = None
                    getReviewItem.save()
                    if getVoteItem.how_many_votes_on_reject > getVoteItem.how_many_votes_on_approve and getVoteItem.how_many_votes_on_reject > 2:
                        # getDat = getQuestion.history.first()
                        # getNextRecord = getDat.prev_record.delete()
                        getVoteItem.is_completed = True
                        getReviewItem.is_reviewed = True
                        getReviewItem.save()
                        getVoteItem.save()
                    # request.user.profile.suggested_Edit_counter += 1
                    # request.user.profile.save()
                        getDat = getQuestion.history.first()
                        getNextRecord = getQuestion.history.earliest().delete()

                        getQuestion.body = getDat.prev_record.body
                        getQuestion.title = getDat.prev_record.title
                        getQuestion.save()
                        getDat = getQuestion.history.first()
                        deletePrev = getDat.prev_record.delete()

                        getAllEditVotes = QuestionEditVotes.objects.filter(
                            edited_question=getQuestion)
                        for _metaReview in getAllEditVotes:
                            # print("Printing the Error on Line 865")
                            _metaReview.is_completed = True
                            _metaReview.save()
                    if request.user.profile.suggested_Edit_counter == 100:
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Proofreader",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")
                    getAllLowQualityTask = ReviewQuestionEdit.objects.filter(
                        edit_reviewed_by=request.user).count()

                    if not ReviewQuestionEdit.objects.filter(
                            edit_reviewed_by=request.user).exists():
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Custodian",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if getAllLowQualityTask == 250:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="SILVER",
                            tag_name="Reviewer",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if getAllLowQualityTask == 1000:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="GOLD",
                            tag_name="Steward",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    next_blog = ReviewQuestionEdit.objects.filter(
                        is_reviewed=False).exclude(
                        edit_reviewed_by=request.user).order_by('id').first()
                    counting_2 = ReviewQuestionEdit.objects.filter(
                        is_reviewed=False).exclude(
                        edit_reviewed_by=request.user).count()

                    if counting_2 >= 1:
                        return redirect(
                            'review:reviewSuggesstedEdit',
                            reviewquestionedit_id=next_blog.id)
                    else:
                        messages.error(
                            request, 'No More Suggessted Edits to Review')
                        return redirect('profile:home')

                elif formData == "Edit":
                    create_a_NewInstance = QuestionEditVotes.objects.create(
                        edit_suggested_by=request.user,
                        edited_question=getQuestion,
                        rev_Action="Approve_Through_Edit")
                    getReviewItem.edit_reviewed_by.add(request.user)
                    # getVoteItem.how_many_votes_on_reject += 1
                    # getVoteItem.save()
                    # getReviewItem.reviewActions = None
                    getReviewItem.save()
                    # if getVoteItem.how_many_votes_on_reject >
                    # getVoteItem.how_many_votes_on_approve and
                    # getVoteItem.how_many_votes_on_reject > 2:
                    awardUser = Reputation.objects.create(
                        awarded_to=getVoteItem.edit_suggested_by,
                        question_O=getQuestion,
                        question_rep_C=2,
                        reputation_on_what="EDIT")
                    rewardPrivielege(request, getVoteItem.edit_suggested_by)
                    getVoteItem.is_completed = True
                    getReviewItem.is_reviewed = True
                    create_a_NewInstance.is_completed = True
                    create_a_NewInstance.save()
                    getReviewItem.save()
                    getVoteItem.save()
                    next_blog = ReviewQuestionEdit.objects.filter(
                        is_reviewed=False).exclude(
                        edit_reviewed_by=request.user).order_by('id').first()
                    counting_2 = ReviewQuestionEdit.objects.filter(
                        is_reviewed=False).exclude(
                        edit_reviewed_by=request.user).count()
                    getAllLowQualityTask = ReviewQuestionEdit.objects.filter(
                        edit_reviewed_by=request.user).count()

                    if not ReviewQuestionEdit.objects.filter(
                            edit_reviewed_by=request.user).exists():
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Custodian",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if getAllLowQualityTask == 250:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="SILVER",
                            tag_name="Reviewer",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if getAllLowQualityTask == 1000:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="GOLD",
                            tag_name="Steward",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if counting_2 >= 1:
                        return redirect(
                            'review:reviewSuggesstedEdit',
                            reviewquestionedit_id=next_blog.id)
                    else:
                        messages.error(
                            request, 'No More Suggessted Edits to Review')
                        return redirect('profile:home')

# FULLY COMMENTED - START
                elif formData == "Improve_Edit":
                    create_a_NewInstance = QuestionEditVotes.objects.create(
                        edit_suggested_by=request.user,
                        is_completed=True,
                        edited_question=getQuestion,
                        rev_Action="Approve_Through_Edit")
                    getReviewItem.edit_reviewed_by.add(request.user)
                    # getVoteItem.how_many_votes_on_reject += 1
                    # getVoteItem.save()
                    # getReviewItem.reviewActions = None
                    getReviewItem.save()
                    # if getVoteItem.how_many_votes_on_reject >
                    # getVoteItem.how_many_votes_on_approve and
                    # getVoteItem.how_many_votes_on_reject > 2:
                    awardUser = Reputation.objects.create(
                        awarded_to=getVoteItem.edit_suggested_by,
                        question_O=getQuestion,
                        question_rep_C=2,
                        reputation_on_what="EDIT")
                    rewardPrivielege(request, getVoteItem.edit_suggested_by)

                    rewardPrivielege(request, getVoteItem.edit_suggested_by)
                    print("Rewarding is not causing any errors")

                    # getVoteItem.is_completed = True
                    getReviewItem.is_reviewed = True
                    getReviewItem.save()
                    getVoteItem.save()
                    create_a_NewInstance.is_completed = True
                    create_a_NewInstance.save()
                    # getAllEditVotes = QuestionEditVotes.objects.filter(edited_question=getQuestion)
                    # for _metaReviewQuestion in getAllEditVotes:
                    # print("Printing the Error on Line 865")
                    # _metaReviewQuestion.is_completed = True
                    # _metaReviewQuestion.save()
                    next_blog = ReviewQuestionEdit.objects.filter(
                        is_reviewed=False).exclude(
                        edit_reviewed_by=request.user).order_by('id').first()
                    counting_2 = ReviewQuestionEdit.objects.filter(
                        is_reviewed=False).exclude(
                        edit_reviewed_by=request.user).count()
                    getAllLowQualityTask = ReviewQuestionEdit.objects.filter(
                        edit_reviewed_by=request.user).count()

                    if not ReviewQuestionEdit.objects.filter(
                            edit_reviewed_by=request.user).exists():
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Custodian",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if getAllLowQualityTask == 250:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="SILVER",
                            tag_name="Reviewer",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if getAllLowQualityTask == 1000:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="GOLD",
                            tag_name="Steward",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if counting_2 >= 1:
                        return redirect(
                            'review:reviewSuggesstedEdit',
                            reviewquestionedit_id=next_blog.id)
                    else:
                        messages.error(
                            request, 'No More Suggessted Edits to Review')
                        return redirect('profile:home')
# FULLY COMMENTED - END

                elif formData == "Reject_and_Edit":

                    if request.method == 'POST':
                        edit_Q_Form = UpdateQuestion(
                            instance=data, data=request.POST, files=request.FILES)
                        if edit_Q_Form.is_valid():
                            edit_Q_Form.save()
                            next_question = Question.objects.filter(
                                firstquestionreview__QuestionReviewBy__isnull=True).order_by('id').first()
                            return redirect(
                                'review:review_FirstQns',
                                question_id=next_question.id)

                        else:
                            messages.error(request, 'Something went wrong !')

                    else:
                        edit_Q_Form = UpdateQuestion(request.POST or None,
                                                     request.FILES or None,
                                                     instance=data)

                    create_a_NewInstance = QuestionEditVotes.objects.create(
                        edit_suggested_by=request.user, edited_question=getQuestion, rev_Action="Reject")
                    getReviewItem.edit_reviewed_by.add(request.user)
                    getVoteItem.how_many_votes_on_reject += 1
                    getVoteItem.save()
                    # getReviewItem.reviewActions = None
                    getReviewItem.save()
                    if getVoteItem.how_many_votes_on_reject > getVoteItem.how_many_votes_on_approve and getVoteItem.how_many_votes_on_reject > 2:
                        # getDat = getQuestion.history.first()
                        # getNextRecord = getDat.prev_record.delete()
                        getVoteItem.is_completed = True
                        getReviewItem.is_reviewed = True
                        getReviewItem.save()
                        getVoteItem.save()
                        getDat = getQuestion.history.first()
                        getNextRecord = getQuestion.history.earliest().delete()

                        getQuestion.body = getDat.prev_record.body
                        getQuestion.title = getDat.prev_record.title
                        getQuestion.save()
                        getDat = getQuestion.history.first()
                        deletePrev = getDat.prev_record.delete()

                        getAllEditVotes = QuestionEditVotes.objects.filter(
                            edited_question=getQuestion)
                        for _metaReview in getAllEditVotes:
                            # print("Printing the Error on Line 865")
                            _metaReview.is_completed = True
                            _metaReview.save()
                    request.user.profile.suggested_Edit_counter += 1
                    request.user.profile.save()
                    if request.user.profile.suggested_Edit_counter == 100:
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Proofreader",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    next_blog = ReviewQuestionEdit.objects.filter(
                        is_reviewed=False).exclude(
                        edit_reviewed_by=request.user).order_by('id').first()
                    counting_2 = ReviewQuestionEdit.objects.filter(
                        is_reviewed=False).exclude(
                        edit_reviewed_by=request.user).count()
                    getAllLowQualityTask = ReviewQuestionEdit.objects.filter(
                        edit_reviewed_by=request.user).count()

                    if not ReviewQuestionEdit.objects.filter(
                            edit_reviewed_by=request.user).exists():
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Custodian",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if getAllLowQualityTask == 250:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="SILVER",
                            tag_name="Reviewer",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if getAllLowQualityTask == 1000:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="GOLD",
                            tag_name="Steward",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if counting_2 >= 1:
                        return redirect(
                            'review:reviewSuggesstedEdit',
                            reviewquestionedit_id=next_blog.id)
                    else:
                        messages.error(
                            request, 'No More Suggessted Edits to Review')
                        return redirect('profile:home')

                elif formData == "Skip":
                    getReviewItem.edit_reviewed_by.add(request.user)
                    next_blog = ReviewQuestionEdit.objects.filter(
                        is_reviewed=False).exclude(
                        edit_reviewed_by=request.user).order_by('id').first()
                    counting_2 = ReviewQuestionEdit.objects.filter(
                        is_reviewed=False).exclude(
                        edit_reviewed_by=request.user).count()

                    if counting_2 >= 1:
                        return redirect(
                            'review:reviewSuggesstedEdit',
                            reviewquestionedit_id=next_blog.id)
                    else:
                        messages.error(
                            request, 'No More Suggessted Edits to Review')
                        return redirect('profile:home')

# ANSWER REVIEW

        else:
            getAnswer = Answer.objects.get(reviewquestionedit=getReviewItem)
            getVoteItem = QuestionEditVotes.objects.filter(
                edited_answer=getAnswer, rev_Action=None, is_completed=False).first()
            if getAnswer.answer_owner == request.user:
                if formData == "Approve":
                    print("Reviewed by Owner")
                    create_a_NewInstance = QuestionEditVotes.objects.create(
                        edit_suggested_by=request.user, edited_answer=getAnswer, rev_Action="Approve")
                    getReviewItem.edit_reviewed_by.add(request.user)
                    getVoteItem.how_many_votes_on_approve += 1
                    # getReviewItem.reviewActions = None
                    getVoteItem.is_completed = True
                    getReviewItem.is_reviewed = True
                    getAnswer.why_editing_answer = None
                    getAnswer.save()
                    getVoteItem.edit_suggested_by.profile.suggested_Edit_counter += 1
                    getVoteItem.edit_suggested_by.profile.save()
                    getReviewItem.save()
                    getVoteItem.save()
                    question_URL = request.build_absolute_uri(
                        getAnswer.questionans.get_absolute_url())
                    createARep_Notification = PrivRepNotification.objects.get_or_create(
                        for_user=getAnswer.answer_owner,
                        url=question_URL,
                        type_of_PrivNotify="EDIT_GOT_APPROVED",
                        missingReputation=2)
                    return redirect(
                        'qa:questionDetailView',
                        pk=getAnswer.questionans.id)
                    # messages.info(request, "Reviewed by Owner")
                    return redirect('profile:home')
                elif formData == "Reject":
                    print("Reviewed by Owner")
                    create_a_NewInstance = QuestionEditVotes.objects.create(
                        edit_suggested_by=request.user, edited_answer=getAnswer, rev_Action="Reject")
                    getReviewItem.edit_reviewed_by.add(request.user)
                    getVoteItem.how_many_votes_on_approve += 1
                    # getReviewItem.reviewActions = None
                    getVoteItem.is_completed = True
                    getReviewItem.is_reviewed = True
                    getAnswer.why_editing_answer = None
                    getVoteItem.edit_suggested_by.profile.suggested_Edit_counter += 1
                    getVoteItem.edit_suggested_by.profile.save()
                    getReviewItem.save()
                    getVoteItem.save()
                    getDat = getAnswer.history.first()
                    getNextRecord = getAnswer.history.earliest().delete()

                    getAnswer.body = getDat.prev_record.body
                    getQuestion.title = getDat.prev_record.title
                    getAnswer.save()
                    getDat = getAnswer.history.first()
                    deletePrev = getDat.prev_record.delete()
                    # messages.info(request, "Reviewed by Owner")
                    return redirect('profile:home')
            else:
                if formData == "Approve":
                    print("Line 849 statement is Excecuting")
                    create_a_NewInstance = QuestionEditVotes.objects.create(
                        edit_suggested_by=request.user, edited_answer=getAnswer, rev_Action="Approve")
                    getReviewItem.edit_reviewed_by.add(request.user)
                    getVoteItem.how_many_votes_on_approve += 1
                    getVoteItem.save()
                    # getReviewItem.reviewActions = None
                    getReviewItem.save()
                    # if getVoteItem.how_many_votes_on_approve >
                    # getVoteItem.how_many_votes_on_reject and
                    # getVoteItem.how_many_votes_on_approve >= 3:
                    if getVoteItem.how_many_votes_on_approve >= 3:
                        print("Line 858 statement is Excecuting")
                        awardUser = Reputation.objects.create(
                            awarded_to=getVoteItem.edit_suggested_by,
                            answer_O=getAnswer,
                            question_rep_C=2,
                            reputation_on_what="EDIT")
                        rewardPrivielege(
                            request, getVoteItem.edit_suggested_by)
                        getVoteItem.is_completed = True
                        getReviewItem.is_reviewed = True
                        getReviewItem.save()
                        getVoteItem.save()
                        getAnswer.why_editing_answer = None
                        getAnswer.save()
                        getAllEditVotes = QuestionEditVotes.objects.filter(
                            edited_answer=getAnswer)
                        question_URL = request.build_absolute_uri(
                            getAnswer.questionans.get_absolute_url())
                        createARep_Notification = PrivRepNotification.objects.get_or_create(
                            for_user=getAnswer.answer_owner,
                            url=question_URL,
                            type_of_PrivNotify="EDIT_GOT_APPROVED",
                            missingReputation=2)

                        for _metaReview in getAllEditVotes:
                            # print("Printing the Error on Line 865")
                            _metaReview.is_completed = True
                            _metaReview.save()
                    next_blog = ReviewQuestionEdit.objects.filter(
                        is_reviewed=False).exclude(
                        edit_reviewed_by=request.user).order_by('id').first()
                    counting_2 = ReviewQuestionEdit.objects.filter(
                        is_reviewed=False).exclude(
                        edit_reviewed_by=request.user).count()
                    getAllLowQualityTask = ReviewQuestionEdit.objects.filter(
                        edit_reviewed_by=request.user).count()

                    if not ReviewQuestionEdit.objects.filter(
                            edit_reviewed_by=request.user).exists():
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Custodian",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if getAllLowQualityTask == 250:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="SILVER",
                            tag_name="Reviewer",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if getAllLowQualityTask == 1000:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="GOLD",
                            tag_name="Steward",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if counting_2 >= 1:
                        return redirect(
                            'review:reviewSuggesstedEdit',
                            reviewquestionedit_id=next_blog.id)
                    else:
                        messages.error(
                            request, 'No More Suggessted Edits to Review')
                        return redirect('profile:home')

                elif formData == "Reject":
                    create_a_NewInstance = QuestionEditVotes.objects.create(
                        edit_suggested_by=request.user, edited_answer=getAnswer, rev_Action="Reject")
                    getReviewItem.edit_reviewed_by.add(request.user)
                    getVoteItem.how_many_votes_on_reject += 1
                    getVoteItem.save()
                    # getReviewItem.reviewActions = None
                    getReviewItem.save()
                    if getVoteItem.how_many_votes_on_reject > getVoteItem.how_many_votes_on_approve and getVoteItem.how_many_votes_on_reject > 2:
                        getVoteItem.is_completed = True
                        getReviewItem.is_reviewed = True
                        getReviewItem.save()
                        getVoteItem.save()
                        getDat = getAnswer.history.first()
                        getNextRecord = getAnswer.history.earliest().delete()
                        getAnswer.why_editing_answer = None
                        getQuestion.title = getDat.prev_record.title
                        getAnswer.body = getDat.prev_record.body
                        getAnswer.save()
                        getDat = getAnswer.history.first()
                        deletePrev = getDat.prev_record.delete()

                    next_blog = ReviewQuestionEdit.objects.filter(
                        is_reviewed=False).exclude(
                        edit_reviewed_by=request.user).order_by('id').first()
                    counting_2 = ReviewQuestionEdit.objects.filter(
                        is_reviewed=False).exclude(
                        edit_reviewed_by=request.user).count()
                    getAllLowQualityTask = ReviewQuestionEdit.objects.filter(
                        edit_reviewed_by=request.user).count()

                    if not ReviewQuestionEdit.objects.filter(
                            edit_reviewed_by=request.user).exists():
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Custodian",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if getAllLowQualityTask == 250:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="SILVER",
                            tag_name="Reviewer",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if getAllLowQualityTask == 1000:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="GOLD",
                            tag_name="Steward",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if counting_2 >= 1:
                        return redirect(
                            'review:reviewSuggesstedEdit',
                            reviewquestionedit_id=next_blog.id)
                    else:
                        messages.error(
                            request, 'No More Suggessted Edits to Review')
                        return redirect('profile:home')

                elif formData == "Edit":
                    create_a_NewInstance = QuestionEditVotes.objects.create(
                        edit_suggested_by=request.user,
                        edited_answer=getAnswer,
                        rev_Action="Approve_Through_Edit")
                    getReviewItem.edit_reviewed_by.add(request.user)
                    getVoteItem.how_many_votes_on_reject += 1
                    getVoteItem.save()
                    # getReviewItem.reviewActions = None
                    # getReviewItem.save()
                    awardUser = Reputation.objects.create(
                        awarded_to=getVoteItem.edit_suggested_by,
                        answer_O=getAnswer,
                        question_rep_C=2,
                        reputation_on_what="EDIT")
                    rewardPrivielege(request, getVoteItem.edit_suggested_by)
                    getAnswer.why_editing_answer = None
                    getAnswer.save()
                    # getVoteItem.is_completed = True
                    getReviewItem.is_reviewed = True
                    create_a_NewInstance.is_completed = True
                    create_a_NewInstance.save()
                    getReviewItem.save()
                    getVoteItem.save()

                    # if getVoteItem.how_many_votes_on_reject > getVoteItem.how_many_votes_on_approve and getVoteItem.how_many_votes_on_reject > 2:
                    #     awardUser = Reputation.objects.create(awarded_to=getVoteItem.edit_suggested_by, answer_O=getAnswer, question_rep_C=2, reputation_on_what="EDIT")
                    #     getVoteItem.is_completed = True
                    #     getReviewItem.is_reviewed = True
                    #     getReviewItem.save()
                    #     getVoteItem.save()
                    next_blog = ReviewQuestionEdit.objects.filter(
                        is_reviewed=False).exclude(
                        edit_reviewed_by=request.user).order_by('id').first()
                    counting_2 = ReviewQuestionEdit.objects.filter(
                        is_reviewed=False).exclude(
                        edit_reviewed_by=request.user).count()
                    getAllLowQualityTask = ReviewQuestionEdit.objects.filter(
                        edit_reviewed_by=request.user).count()

                    if not ReviewQuestionEdit.objects.filter(
                            edit_reviewed_by=request.user).exists():
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Custodian",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if getAllLowQualityTask == 250:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="SILVER",
                            tag_name="Reviewer",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if getAllLowQualityTask == 1000:
                        TagBadge.objects.create(
                            awarded_to_user=request.user,
                            badge_type="GOLD",
                            tag_name="Steward",
                            bade_position="BADGE")
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                    if counting_2 >= 1:
                        return redirect(
                            'review:reviewSuggesstedEdit',
                            reviewquestionedit_id=next_blog.id)
                    else:
                        messages.error(
                            request, 'No More Suggessted Edits to Review')
                        return redirect('profile:home')

                elif formData == "Skip":
                    getReviewItem.edit_reviewed_by.add(request.user)
                    next_blog = ReviewQuestionEdit.objects.filter(
                        is_reviewed=False).exclude(
                        edit_reviewed_by=request.user).order_by('id').first()
                    counting_2 = ReviewQuestionEdit.objects.filter(
                        is_reviewed=False).exclude(
                        edit_reviewed_by=request.user).count()

                    if counting_2 >= 1:
                        return redirect(
                            'review:reviewSuggesstedEdit',
                            reviewquestionedit_id=next_blog.id)
                    else:
                        messages.error(
                            request, 'No More Suggessted Edits to Review')
                        return redirect('profile:home')

    # previousHistory = data.prev_record

    if getReviewItem.question_to_view:
        print("Question to Review In FrontEnd")
        is_question = True
        is_answer = False
        # data = Question.objects.filter(reviewflagpost=getReviewItem).first()
        data = get_object_or_404(Question, reviewquestionedit=getReviewItem)
        getThisItemFromReview = ReviewQuestionEdit.objects.filter(
            question_to_view=data, is_reviewed=False).first()
        # Bug in This
        getReviewersByVote = QuestionEditVotes.objects.filter(
            edited_question=data,
            is_completed=False).exclude(
            rev_Action=None)
        lastVoteWas = ReviewQuestionEdit.objects.filter(
            question_to_view=data, is_reviewed=True).last()
        reviewers = getReviewItem.edit_reviewed_by.all()

    # Question UpVote and DownVote
        likepost = data.qupvote_set.filter(upvote_by_q=request.user).first()
        likeDownpost = data.qdownvote_set.filter(
            downvote_by_q=request.user).first()
        upvotesCount = data.qupvote_set.all().count()
        downvotesCount = data.qdownvote_set.all().count()
        allToShowVotes = upvotesCount - downvotesCount
        comments = data.commentq_set.all().exclude(deleted=True)

        getThisItemFromReview_ForLastVote = ReviewQuestionEdit.objects.filter(
            question_to_view=data).last()
        getReviewersByVote_ForLastVote = QuestionEditVotes.objects.filter(
            edited_question=data).exclude(rev_Action=None)

    # Previous History. - That was edited that's why this review
    # created
        getDat = data.history.first()
        previousHistory = getDat.prev_record.title
        previousHistoryBody = getDat.prev_record.body

    # New History. - With new Edits
        getNewEdit = data.history.earliest()
        getNewEdit_Body = data.body
        getNewEdit_Title = data.title

        answers_of_questions = data.answer_set.all().exclude(deletedHistory="DELETED")
        STORING_THE_ORIGINAL = []

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
                print("Third Statement is Excecuting")

    elif getReviewItem.answer_to_view_if:
        print("Answer to Review In FrontEnd")
        is_question = False
        is_answer = True
        # data = Answer.objects.filter(reviewflagpost=getReviewItem).first()
        data = get_object_or_404(Answer, reviewquestionedit=getReviewItem)
        getThisItemFromReview = ReviewQuestionEdit.objects.filter(
            answer_to_view_if=data, is_reviewed=False).first()
        getReviewersByVote = QuestionEditVotes.objects.filter(
            edited_answer=data, is_completed=True).first()
        lastVoteWas = ReviewQuestionEdit.objects.filter(
            answer_to_view_if=data).last()
        getQuestionFromAnswer = Question.objects.get(answer=data)
        # reviewers = ReviewQuestionEdit.objects.filter(pk=getReviewItem)
        reviewers = getReviewItem.edit_reviewed_by.all()
        comments = data.commentq_set.all().exclude(deleted=True)

        STORING_THE_ORIGINAL = []
        answers_of_questions = ''

    # Answer UpVote and DownVote
        likepost = data.questionans.qupvote_set.filter(
            upvote_by_q=request.user).first()
        likeDownpost = data.questionans.qdownvote_set.filter(
            downvote_by_q=request.user).first()
        upvotesCount = getQuestionFromAnswer.qupvote_set.all().count()
        downvotesCount = getQuestionFromAnswer.qdownvote_set.all().count()
        allToShowVotes = upvotesCount - downvotesCount
        getNewEdit_Title = ''
        previousHistory = ''

    # Previous History. - That was edited that's why this review
    # created
        getDat = data.anshis.first()
        # previousHistory = getDat.prev_record.title
        previousHistoryBody = getDat.prev_record.body

    # New History. - With new Edits
        getNewEdit = data.anshis.earliest()
        getNewEdit_Body = data.body

        getThisItemFromReview_ForLastVote = ReviewQuestionEdit.objects.filter(
            answer_to_view_if=data).last()
        getReviewersByVote_ForLastVote = QuestionEditVotes.objects.filter(
            edited_answer=data).exclude(rev_Action=None)

    is_reviewed = ''
    if getThisItemFromReview_ForLastVote:
        if request.user in getThisItemFromReview_ForLastVote.edit_reviewed_by.all():
            is_reviewed = True
        else:
            is_reviewed = False

    is_stopped = ''
    if getThisItemFromReview_ForLastVote:
        if getThisItemFromReview_ForLastVote.is_reviewed:
            is_stopped = True
        else:
            is_stopped = False

    context = {
        'is_reviewed': is_reviewed,
        'is_question': is_question,
        'is_answer': is_answer,
        'is_stopped': is_stopped,
        'getThisItemFromReview': getThisItemFromReview,
        # 'getReviewItem':getReviewItem,
        'allToShowVotes': allToShowVotes,
        'likepost': likepost,
        'likeDownpost': likeDownpost,
        'getNewEdit_Title': getNewEdit_Title,
        'STORING_THE_ORIGINAL': STORING_THE_ORIGINAL,
        'answers_of_questions': answers_of_questions,
        'comments': comments,

        'getReviewersByVote': getReviewersByVote,
        'previousHistory': previousHistory,
        'previousHistoryBody': previousHistoryBody,
        'getNewEdit': getNewEdit,
        'getNewEdit_Body': getNewEdit_Body,
        'getAnswerHitory': getAnswerHitory,
        'getQuestionHistory': getQuestionHistory,
        'data': data,
        'ItIsQuestion': ItIsQuestion,
        'editAnswerForm': editAnswerForm,
        'edit_Q_Form': edit_Q_Form,
        'getReviewItem': getReviewItem,
        'form': form
    }
    return render(request, 'review/Suggessted_Edit_Review.html', context)


"""
If user's close flag was not the parent and delete only the vote

But if user's flag was parent and voted on how_many_close_votes are 1 (of course it would be self) then delete the CloseQuestionVotes and Reviewing Instance
But if vote is more than 1 then only delete the vote of user on retract.

Because if the flag was made by mistake and that mistake review got 1 more close vote then mistake will not be considered as mistake.
"""
# It is Working But I am thinking about making it with Ajax.


def retract_Close_Flag(request, question_id):
    getQuestion = get_object_or_404(Question, pk=question_id)

    # getCreatedObject = CloseQuestionVotes.objects.filter(question_to_closing=getQuestion).exclude(ended=True).first()

    getCreatedObject_if_Exist = CloseQuestionVotes.objects.filter(
        question_to_closing=getQuestion).exclude(ended=True).exists()

    getCreatedObject_2 = CloseQuestionVotes.objects.filter(
        question_to_closing=getQuestion).exclude(
        ended=True).first()

    getReviewingObject = ReviewCloseVotes.objects.filter(
        review_of=getCreatedObject_2, is_completed=False).first()

    if getCreatedObject_if_Exist:
        if getCreatedObject_2.user == request.user and getCreatedObject_2.how_many_votes_on_Close < 1:
            getCreatedObject_2.delete()
            getReviewingObject.delete()
        else:
            getCreatedObject_2.how_many_votes_on_Close -= 1
            getReviewingObject.reviewed_by.remove(request.user)
            getCreatedObject_2.save()

    return redirect('qa:questionDetailView', pk=question_id)


def retract_Flag_Form(request, question_id):
    getQuestion = get_object_or_404(Question, pk=question_id)

    getCreateObject_If_Exist = FlagPost.objects.filter(
        question_forFlag=getQuestion).exclude(
        ended=True).exists()

    getCreatedObject_2 = FlagPost.objects.filter(
        flagged_by=request.user,
        question_forFlag=getQuestion).exclude(
        ended=True).first()

    getReviewingObject = ReviewFlagPost.objects.filter(
        flag_question_to_view=getQuestion, flag_is_reviewed=True).first()

    if getCreatedObject_if_Exist:
        if getCreatedObject_2.flagged_by == request.user and getCreatedObject_2.how_many_votes_on_spamANDRude < 1 or getCreatedObject_2.how_many_votes_on_notAnAnswer < 1 or getCreatedObject_2.how_many_votes_on_others < 1:
            getCreatedObject_2.delete()
            getReviewingObject.delete()
        else:
            getCreatedObject_2.delete()
            getCreatedObject_2.flag_reviewed_by.remove(request.user)
            getCreatedObject_2.save()

    return redirect('qa:questionDetailView', pk=question_id)


# def retract_ReOpen_Flag(request):
#     getQuestion = get_object_or_404(Question, pk=question_id)

#     getCreatedObject_if_Exist = ReOpenQuestionVotes.objects.filter(question_to_opening=getQuestion).exclude(ended=True).exists()

#     getCreatedObject_2 = ReOpenQuestionVotes.objects.filter(re)


# REVIEW FIRST ANSWER
@required_500_RepToReview
def review_FirstAns(request, answer_id):
    data = get_object_or_404(Answer, pk=answer_id)
    time = timezone.now() - timedelta(seconds=200)
    counting = Answer.objects.filter(
        firstanswerreview__actions__isnull=True).exclude(
        answer_owner=request.user).count()
    post_ids_subquery_2 = Answer.objects.filter(
        date__gt=time
    ).values(
        'answer_owner'
    ).annotate(
        min_id=Min('id')
    ).values('min_id')

    if request.method == 'POST':
        if counting >= 1:
            form = AnswerReviewForm(data=request.POST)
            if form.is_valid():
                # pos = Answer.objects.get(id=answer_id)
                new_post = form.save(commit=False)
                new_post.AnswerReviewedBy = request.user
                new_post.answerReview = data
                new_post.save()

                # if new_post.actions == 'EDIT':
                # return redirect('review:editFromReview', answer_id=data.id)

                next_blog = Answer.objects.filter(
                    firstanswerreview__actions__isnull=True).filter(
                    id__in=post_ids_subquery_2).order_by('id').first()
                counting = Answer.objects.filter(
                    firstanswerreview__actions__isnull=True).exclude(
                    answer_owner=request.user).filter(
                    id__in=post_ids_subquery_2).count()

                getAllLowQualityTask = FirstAnswerReview.objects.filter(
                    AnswerReviewedBy=request.user).count()
                if not FirstAnswerReview.objects.filter(
                        AnswerReviewedBy=request.user).exists():
                    TagBadge.objects.create(
                        awarded_to_user=request.user,
                        badge_type="BRONZE",
                        tag_name="Custodian",
                        bade_position="BADGE")
                    PrivRepNotification.objects.get_or_create(
                        for_user=request.user, type_of_PrivNotify="BADGE_EARNED")
                if getAllLowQualityTask == 250:
                    TagBadge.objects.create(
                        awarded_to_user=request.user,
                        badge_type="SILVER",
                        tag_name="Reviewer",
                        bade_position="BADGE")
                    PrivRepNotification.objects.get_or_create(
                        for_user=request.user, type_of_PrivNotify="BADGE_EARNED")
                if getAllLowQualityTask == 1000:
                    TagBadge.objects.create(
                        awarded_to_user=request.user,
                        badge_type="GOLD",
                        tag_name="Steward",
                        bade_position="BADGE")
                    PrivRepNotification.objects.get_or_create(
                        for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                if counting >= 1:
                    return redirect(
                        'review:review_FirstAns',
                        answer_id=next_blog.id)
                else:
                    messages.error(request, 'No More First Answers to Review')
                    return redirect('profile:home')
        else:
            messages.error(request, 'No More First Answers to Review')
            return redirect('profile:home')

    else:
        form = AnswerReviewForm()

    # post = Answer.objects.get(id=answer_id)
    # post_owner = post.answer_owner

    if request.method == 'POST':
        editForm = EditAnswerForm(instance=data,
                                  data=request.POST,
                                  files=request.FILES)
        if editForm.is_valid():
            editForm.save()
            next_blog = Answer.objects.filter(
                firstanswerreview__actions__isnull=True).order_by('id').first()
            return redirect('review:review_FirstAns', answer_id=next_blog.id)

    else:
        editForm = EditAnswerForm(request.POST or None,
                                  request.FILES or None,
                                  instance=data)

    getThisItemFromReview = FirstAnswerReview.objects.filter(
        answerReview=data).first()

    if getThisItemFromReview:
        actionWas = ''
        if getThisItemFromReview.actions == "LOOKS_OK":
            actionWas = "Approved"
        elif getThisItemFromReview.actions == "EDIT":
            actionWas = "Edit_and_Approve"
        elif getThisItemFromReview.actions == "SKIPPED":
            actionWas = "Skipped"
    else:
        actionWas = ''
    if getThisItemFromReview is not None:
        is_reviewed = True
    else:
        is_reviewed = False
    # print(actionWas)

    context = {
        'getThisItemFromReview': getThisItemFromReview,
        'is_reviewed': is_reviewed,
        'actionWas': actionWas,
        'form': form,
        'data': data,
        'editForm': editForm}
    return render(request, 'review/First_Answer_Review.html', context)

# REVIEW LATE ANSWER


@required_500_RepToReview
def review_LateAnswers(request, answer_id):
    data = get_object_or_404(Answer, pk=answer_id)
    likepost = data.questionans.qupvote_set.filter(
        upvote_by_q=request.user).first()
    likeDownpost = data.questionans.qdownvote_set.filter(
        downvote_by_q=request.user).first()
    # time = timezone.now() - timedelta(minutes=20)
    isOlderThanFiveHours = timezone.now() - timedelta(minutes=10)
    counting = Answer.objects.filter(
        questionans__date__gt=timezone.now() - timedelta(hours=100)).filter(
        date__gt=isOlderThanFiveHours).count()
    # lateAnswers = Answer.objects.filter(questionans__date__gt=timezone.now() - timedelta(hours=100)).filter(date__gt=isOlderThanFiveHours)

    if request.method == 'POST':
        if counting >= 1:
            form = LateAnswerReviewForm(data=request.POST)
            if form.is_valid():
                new_post = form.save(commit=False)
                new_post.L_AnswerReviewdBy = request.user
                new_post.L_answerReview = data
                new_post.save()

                next_blog = Answer.objects.filter(
                    lateanswerreview__L_AnswerActions__isnull=True).filter(
                    questionans__date__gt=timezone.now() -
                    timedelta(
                        hours=100)).filter(
                    date__gt=isOlderThanFiveHours).order_by('id').first()

                counting = Answer.objects.filter(
                    lateanswerreview__L_AnswerActions__isnull=True).filter(
                    questionans__date__gt=timezone.now() -
                    timedelta(
                        hours=100)).filter(
                    date__gt=isOlderThanFiveHours).count()
                getAllLowQualityTask = LateAnswerReview.objects.filter(
                    L_AnswerReviewdBy=request.user).count()
                if not LateAnswerReview.objects.filter(
                        L_AnswerReviewdBy=request.user).exists():
                    TagBadge.objects.create(
                        awarded_to_user=request.user,
                        badge_type="BRONZE",
                        tag_name="Custodian",
                        bade_position="BADGE")
                    PrivRepNotification.objects.get_or_create(
                        for_user=request.user, type_of_PrivNotify="BADGE_EARNED")
                if getAllLowQualityTask == 250:
                    TagBadge.objects.create(
                        awarded_to_user=request.user,
                        badge_type="SILVER",
                        tag_name="Reviewer",
                        bade_position="BADGE")
                    PrivRepNotification.objects.get_or_create(
                        for_user=request.user, type_of_PrivNotify="BADGE_EARNED")
                if getAllLowQualityTask == 1000:
                    TagBadge.objects.create(
                        awarded_to_user=request.user,
                        badge_type="GOLD",
                        tag_name="Steward",
                        bade_position="BADGE")
                    PrivRepNotification.objects.get_or_create(
                        for_user=request.user, type_of_PrivNotify="BADGE_EARNED")

                if counting >= 1:
                    return redirect(
                        'review:review_LateAnswers',
                        answer_id=next_blog.id)
                else:
                    messages.error(request, 'No More Late Answers to Review')
                    return redirect('profile:home')
        else:
            messages.error(request, 'No More Late Answers to Review')
            return redirect('profile:home')

    else:
        form = LateAnswerReviewForm()

    if request.method == 'POST':
        editForm = EditAnswerForm(instance=data,
                                  data=request.POST,
                                  files=request.FILES)
        if editForm.is_valid():
            editForm.save()
            next_blog = Answer.objects.filter(
                firstanswerreview__actions__isnull=True).order_by('id').first()
            return redirect('review:review_FirstAns', answer_id=next_blog.id)

    else:
        editForm = EditAnswerForm(request.POST or None,
                                  request.FILES or None,
                                  instance=data)

    upvotesCount = data.questionans.qupvote_set.all().count()
    downvotesCount = data.questionans.qdownvote_set.all().count()
    allToShowVotes = upvotesCount - downvotesCount

    getThisItemFromReview = LateAnswerReview.objects.filter(
        L_answerReview=data).first()

    if getThisItemFromReview:
        actionWas = ''
        if getThisItemFromReview.L_AnswerActions == "LOOKS_OK":
            actionWas = "Approved"
        elif getThisItemFromReview.L_AnswerActions == "EDIT":
            actionWas = "Edit_and_Approve"
        elif getThisItemFromReview.L_AnswerActions == "RECOMMEND_DELETION":
            actionWas = "Recommend_Delete"
        elif getThisItemFromReview.L_AnswerActions == "SKIPPED":
            actionWas = "Skipped"
    else:
        actionWas = ''
    if getThisItemFromReview is not None:
        is_reviewed = True
    else:
        is_reviewed = False

    context = {
        'getThisItemFromReview': getThisItemFromReview,
        'actionWas': actionWas,
        'is_reviewed': is_reviewed,
        'form': form,
        'data': data,
        'editForm': editForm,
        'likepost': likepost,
        'likeDownpost': likeDownpost,
        'allToShowVotes': allToShowVotes,
    }
    return render(request, 'review/Late_Answer_Review.html', context)

# REVIEW FIRST QUESTION


@required_500_RepToReview
def review_FirstQns(request, question_id):
    data = get_object_or_404(Question, pk=question_id)
    likepost = data.qupvote_set.filter(upvote_by_q=request.user).first()
    likeDownpost = data.qdownvote_set.filter(
        downvote_by_q=request.user).first()
    time = timezone.now() - timedelta(minutes=20)
    counting = Question.objects.filter(
        firstquestionreview__QuestionReviewBy__isnull=True).count()
    post_ids_subquery = Question.objects.filter(
        date__gt=time
    ).values(
        'post_owner'
    ).annotate(
        min_id=Min('id')
    ).values('min_id')

    if request.method == 'POST':
        if counting >= 1:
            form = QuestionReviewForm(data=request.POST)
            if form.is_valid():
                new_post = form.save(commit=False)
                new_post.QuestionReviewBy = request.user
                new_post.questionReview = data
                new_post.save()

                next_question = Question.objects.filter(
                    firstquestionreview__QuestionReviewBy__isnull=True).filter(
                    id__in=post_ids_subquery).order_by('id').first()
                counting = Question.objects.filter(
                    firstquestionreview__QuestionReviewBy__isnull=True).filter(
                    id__in=post_ids_subquery).count()
                getAllLowQualityTask = FirstQuestionReview.objects.filter(
                    QuestionReviewBy=request.user).count()
                if not FirstQuestionReview.objects.filter(
                        QuestionReviewBy=request.user).exists():
                    TagBadge.objects.create(
                        awarded_to_user=request.user,
                        badge_type="BRONZE",
                        tag_name="Custodian",
                        bade_position="BADGE")
                    PrivRepNotification.objects.get_or_create(
                        for_user=request.user, type_of_PrivNotify="BADGE_EARNED")
                if getAllLowQualityTask == 250:
                    PrivRepNotification.objects.get_or_create(
                        for_user=request.user, type_of_PrivNotify="BADGE_EARNED")
                    TagBadge.objects.create(
                        awarded_to_user=request.user,
                        badge_type="SILVER",
                        tag_name="Reviewer",
                        bade_position="BADGE")
                if getAllLowQualityTask == 1000:
                    PrivRepNotification.objects.get_or_create(
                        for_user=request.user, type_of_PrivNotify="BADGE_EARNED")
                    TagBadge.objects.create(
                        awarded_to_user=request.user,
                        badge_type="GOLD",
                        tag_name="Steward",
                        bade_position="BADGE")

                if counting >= 1:
                    return redirect(
                        'review:review_FirstQns',
                        question_id=next_question.id)
                else:
                    messages.error(
                        request, 'No More FirsT Questions to Review')
                    return redirect('profile:home')

        else:
            messages.error(request, 'No More FirsT Questions to Review')
            return redirect('profile:home')

    else:
        form = QuestionReviewForm()

    if request.method == 'POST':
        edit_Q_Form = UpdateQuestion(
            instance=data,
            data=request.POST,
            files=request.FILES)
        if edit_Q_Form.is_valid():
            edit_Q_Form.save()
            next_question = Question.objects.filter(
                firstquestionreview__QuestionReviewBy__isnull=True).order_by('id').first()
            return redirect(
                'review:review_FirstQns',
                question_id=next_question.id)

    else:
        edit_Q_Form = UpdateQuestion(request.POST or None,
                                     request.FILES or None,
                                     instance=data)

    upvotesCount = data.qupvote_set.all().count()
    downvotesCount = data.qdownvote_set.all().count()
    allToShowVotes = upvotesCount - downvotesCount

    getThisItemFromReview = FirstQuestionReview.objects.filter(
        questionReview=data).first()

    if getThisItemFromReview:
        actionWas = ''
        if getThisItemFromReview.questionActions == "LOOKS_OK":
            actionWas = "Approved"
        elif getThisItemFromReview.questionActions == "EDIT":
            actionWas = "Edit_and_Approve"
        elif getThisItemFromReview.questionActions == "SKIPPED":
            actionWas = "Skipped"
    else:
        actionWas = ''
    if getThisItemFromReview is not None:
        is_reviewed = True
    else:
        is_reviewed = False
    # print(actionWas)

    context = {
        'likeDownpost': likeDownpost,
        'actionWas': actionWas,
        'is_reviewed': is_reviewed,
        'form': form,
        'data': data,
        'edit_Q_Form': edit_Q_Form,
        'likepost': likepost,
        'allToShowVotes': allToShowVotes,
        'getThisItemFromReview': getThisItemFromReview,
    }
    return render(request, 'review/First_Question_Review.html', context)

# EDIT FIRST QUESTION (THROUGH AJAX)


def EditQuestionAjax(request, question_id):
    data = get_object_or_404(Question, pk=question_id)
    # request should be ajax and method should be POST.
    if is_ajax(request) and request.method == "POST":
        # get the form data
        edit_Q_Form = UpdateQuestion(instance=data,
                                     data=request.POST,
                                     files=request.FILES)
        # save the data and after fetch the object in instance
        if edit_Q_Form.is_valid():
            instance = edit_Q_Form.save()
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


def Edit_Q_In_SuggesstedEdits(request, question_id):
    data = get_object_or_404(Question, pk=question_id)
    # request should be ajax and method should be POST.
    if is_ajax(request) and request.method == "POST":
        # get the form data
        edit_Q_Form = UpdateQuestion(instance=data,
                                     data=request.POST,
                                     files=request.FILES)
        # save the data and after fetch the object in instance
        if edit_Q_Form.is_valid():
            instance = edit_Q_Form.save()
            # serialize in new friend object in json
            ser_instance = serializers.serialize('json', [
                instance,
            ])
            # send to client side.
            return JsonResponse({"instance": ser_instance}, status=200)
        else:
            # some form errors occured.
            return JsonResponse({"error": form.errors}, status=400)

    # some error occured
    return JsonResponse({"error": ""}, status=400)


def Edit_Answer_In_SuggesstedEdits(request, answer_id):
    data = get_object_or_404(Answer, pk=answer_id)
    # request should be ajax and method should be POST.
    if is_ajax(request) and request.method == "POST":
        # get the form data
        edit_Q_Form = EditAnswerForm(instance=data,
                                     data=request.POST,
                                     files=request.FILES)
        # save the data and after fetch the object in instance
        if edit_Q_Form.is_valid():
            instance = edit_Q_Form.save()
            # serialize in new friend object in json
            ser_instance = serializers.serialize('json', [
                instance,
            ])
            # send to client side.
            return JsonResponse({"instance": ser_instance}, status=200)
        else:
            # some form errors occured.
            return JsonResponse({"error": form.errors}, status=400)

    # some error occured
    return JsonResponse({"error": ""}, status=400)

# EDIT FIRST ANSWER (THROUGH AJAX)


def EditAllowanceAjaxForm(request, answer_id):
    data = get_object_or_404(Answer, pk=answer_id)
    # request should be ajax and method should be POST.
    if is_ajax(request) and request.method == "POST":
        # get the form data
        editForm = EditAnswerForm(instance=data,
                                  data=request.POST,
                                  files=request.FILES)
        # save the data and after fetch the object in instance
        if editForm.is_valid():
            instance = editForm.save()
            # serialize in new friend object in json
            ser_instance = serializers.serialize('json', [
                instance,
            ])
            # send to client side.
            return JsonResponse({"instance": ser_instance}, status=200)
        else:
            # some form errors occured.
            return JsonResponse({"error": form.errors}, status=400)

    # some error occured
    return JsonResponse({"error": ""}, status=400)


def edit_in_Closing_Ajax(request, question_id):
    data = get_object_or_404(Question, pk=question_id)
    if is_ajax(request) and request.method == "POST":
        editForm = UpdateQuestion(
            instance=data,
            data=request.POST,
            files=request.FILES)

        if editForm.is_valid():
            instance = editForm.save()
            ser_instance = serializers.serialize('json', [instance, ])

            return JsonResponse({'instance': ser_instance}, status=200)
        else:
            return JsonResponse({'error': editForm.errors}, status=400)

    return JsonResponse({'error': ""}, status=400)

# CAN COMMENT - IN


def editFromReview(request, answer_id):
    post = Answer.objects.get(id=answer_id)
    # post_owner = post.answer_owner

    if request.method == 'POST':
        form = EditAnswerForm(instance=post,
                              data=request.POST,
                              files=request.FILES)
        if form.is_valid():
            form.save()
            next_blog = Answer.objects.filter(
                firstanswerreview__actions__isnull=True).order_by('id').first()
            return redirect('review:review_FirstAns', answer_id=next_blog.id)

        else:
            messages.error(request, 'Something went Wrong!')

    else:
        form = EditAnswerForm(request.POST or None,
                              request.FILES or None,
                              instance=post)

    context = {'form': form}
    return render(request, 'review/editFromReview.html', context)

# ReviewCloseVotes.objects.filter(is_completed=False).exclude(reviewed_by=request.user).order_by('id').first()

# CAN COMMENT - IN


def review_answer_page(request):
    next_blogs = Answer.objects.filter(
        firstanswerreview__actions__isnull=True).order_by('id').first()
    counting = Answer.objects.filter(
        firstanswerreview__actions__isnull=True).count()

    if counting >= 1:
        can_show = True
    else:
        can_show = False
    context = {'next_blogs': next_blogs, 'can_show': can_show}
    return render(request, 'review/review_answer_page.html', context)


@required_2000_RepToReview
def reOpen_Question_Review(request, reviewquestionreopenvotes_id):
    questionUNClose = get_object_or_404(
        ReviewQuestionReOpenVotes,
        id=reviewquestionreopenvotes_id)
    data = Question.objects.get(reviewquestionreopenvotes=questionUNClose)
    getUNCloseHistorys = ReOpenQuestionVotes.objects.filter(
        question_to_opening=data).filter(
        Q(
            why_opening="IT_IS_BETTER_NOW") | Q(
                why_opening="CLOSED_BY_MISTAKE") | Q(
                    why_opening="OTHER") | Q(
                        why_opening="Open")).exclude(
                            ended=True).first()

    toTurnEnded = ReOpenQuestionVotes.objects.filter(
        question_to_opening=data).filter(
        Q(
            why_opening="IT_IS_BETTER_NOW") | Q(
                why_opening="CLOSED_BY_MISTAKE") | Q(
                    why_opening="OTHER") | Q(
                        why_opening="Open")).exclude(
                            ended=True)

    getLast_completed_reason_of_review = data.reviewquestionreopenvotes_set.filter(
        is_completed=True).last()

# THROUGH_OPENED
# THROUGH_LEAVE_CLOSED

    if request.method != 'POST':
        form = ReviewReOpenForm(
            instance=questionUNClose,
            data=request.POST,
            files=request.FILES)

    else:
        form = ReviewReOpenForm(
            instance=questionUNClose,
            data=request.POST,
            files=request.FILES)
        if form.is_valid():
            formData = form.cleaned_data['reviewActions']

            if formData == "OPEN":
                create_a_NewInstance = ReOpenQuestionVotes.objects.create(
                    user=request.user, question_to_opening=data, why_opening="Open")
                questionUNClose.reopen_reviewed_by.add(request.user)
                getUNCloseHistorys.how_many_votes_on_Open += 1
                getUNCloseHistorys.save()
                if getLast_completed_reason_of_review:
                    # print("Something is There")
                    if getLast_completed_reason_of_review.what_happend == "Ended_Through_Leave_Closed":
                        if getUNCloseHistorys.how_many_votes_on_Open > getUNCloseHistorys.how_many_votes_on_Leave_close + 2:
                            decRep = Reputation.objects.get_or_create(
                                awarded_to=getUNCloseHistorys.user.post_owner,
                                question_O=post,
                                question_rep_C=+2,
                                reputation_on_what='question_reopen_voted')
                            rewardPrivielege(
                                request, getUNCloseHistorys.user.post_owner)
                            questionUNClose.is_completed = True
                            questionUNClose.what_happend = "Ended_Through_Open"
                            # REOPEN THE QUESTION - HERE -
                            for s in toTurnEnded:
                                s.ended = True
                                s.save()
                            # questionUNClose.reviewActions = None
                            data.is_closed = False
                            data.save()
                            questionUNClose.save()
                            print(
                                "THROUGH SECOND TIME Leave Open SuccessFully Saved and Completed is Saved in")

                    elif getUNCloseHistorys.how_many_votes_on_Open >= 3 and getUNCloseHistorys.how_many_votes_on_Open > getUNCloseHistorys.how_many_votes_on_Leave_close:
                        questionUNClose.is_completed = True
                        questionUNClose.what_happend = "Ended_Through_Open"
                        # REOPEN THE QUESTION - HERE -
                        data.is_closed = False
                        for s in toTurnEnded:
                            s.ended = True
                            s.save()
                        data.save()
                        # questionUNClose.reviewActions = None
                        questionUNClose.save()
                        print(
                            "There was a Previous Record But not with 'Ended Through Leave Closed' So saved in new")

                elif getUNCloseHistorys.how_many_votes_on_Open >= 3 and getUNCloseHistorys.how_many_votes_on_Open > getUNCloseHistorys.how_many_votes_on_Leave_close:
                    questionUNClose.is_completed = True
                    questionUNClose.what_happend = "Ended_Through_Open"
                    questionUNClose.reviewActions = None
                    data.is_closed = False
                    for s in toTurnEnded:
                        s.ended = True
                        s.save()
                    data.save()
                    questionUNClose.save()
                    print("No Previous Record is Saved, So I saved existed instance")

                next_blog = ReviewQuestionReOpenVotes.objects.filter(
                    is_completed=False).exclude(
                    reopen_reviewed_by=request.user).order_by('id').first()
                counting_2 = ReviewQuestionReOpenVotes.objects.filter(
                    is_completed=False).exclude(
                    reopen_reviewed_by=request.user).count()

                if counting_2 >= 1:
                    return redirect(
                        'review:reOpen_Question_Review',
                        reviewquestionreopenvotes_id=next_blog.id)
                else:
                    messages.error(
                        request, 'No More ReOpen Post Votes to Review')
                    return redirect('profile:home')

            elif formData == "LEAVE_CLOSED":
                create_a_NewInstance = ReOpenQuestionVotes.objects.create(
                    user=request.user, question_to_opening=data, why_opening="Leave_closed")
                questionUNClose.reopen_reviewed_by.add(request.user)
                getUNCloseHistorys.how_many_votes_on_Leave_close += 1
                getUNCloseHistorys.save()
                if getLast_completed_reason_of_review:
                    if getLast_completed_reason_of_review.what_happend == "Ended_Through_Open":
                        if getUNCloseHistorys.how_many_votes_on_Leave_close > getUNCloseHistorys.how_many_votes_on_Open + 2:
                            getUNCloseHistorys.is_completed = True
                            questionUNClose.what_happend = "Ended_Through_Leave_Closed"
                            # questionUNClose.reviewActions = None
                            for s in toTurnEnded:
                                s.ended = True
                                s.save()
                            questionUNClose.save()
                            print(
                                "THROUGH SECOND TIME Close SuccessFully Saved and Completed is Saved")

                    elif getUNCloseHistorys.how_many_votes_on_Leave_close >= 3 and getUNCloseHistorys.how_many_votes_on_Leave_close > getUNCloseHistorys.how_many_votes_on_Open:
                        questionUNClose.is_completed = True
                        questionUNClose.what_happend = "Ended_Through_Leave_Closed"
                        # questionUNClose.reviewActions = None
                        for s in toTurnEnded:
                            s.ended = True
                            s.save()
                        questionUNClose.save()
                        print(
                            "There was Previous Record But not with 'Ended Through Open' So saved in new")

                elif getUNCloseHistorys.how_many_votes_on_Leave_close >= 3 and getUNCloseHistorys.how_many_votes_on_Leave_close > getUNCloseHistorys.how_many_votes_on_Open:
                    questionUNClose.is_completed = True
                    questionUNClose.what_happend = "Ended_Through_Leave_Closed"
                    # questionUNClose.reviewActions = None
                    for s in toTurnEnded:
                        s.ended = True
                        s.save()
                    questionUNClose.save()
                    print("Close Successfully Saved and Completed is Saved")

                next_blog = ReviewQuestionReOpenVotes.objects.filter(
                    is_completed=False).exclude(
                    reopen_reviewed_by=request.user).order_by('id').first()
                counting_2 = ReviewQuestionReOpenVotes.objects.filter(
                    is_completed=False).exclude(
                    reopen_reviewed_by=request.user).count()

                if counting_2 >= 1:
                    return redirect(
                        'review:reOpen_Question_Review',
                        reviewquestionreopenvotes_id=next_blog.id)
                else:
                    messages.error(
                        request, 'No More ReOpen Post Votes to Review')
                    return redirect('profile:home')

            else:
                messages.error(request, 'Something went wrong')

    getReviewersByVote = ReOpenQuestionVotes.objects.filter(
        question_to_opening=data)

    likepost = data.qupvote_set.filter(upvote_by_q=request.user).first()
    likeDownpost = data.qdownvote_set.filter(
        downvote_by_q=request.user).first()

    upvotesCount = data.qupvote_set.all().count()
    downvotesCount = data.qdownvote_set.all().count()
    allToShowVotes = upvotesCount - downvotesCount

    getThisItemFromReview = ReviewQuestionReOpenVotes.objects.filter(
        question_opened=data).first()
    print(getThisItemFromReview.reviewActions)
    if getThisItemFromReview:
        endedThrough = ''
        if getThisItemFromReview.reviewActions == "OPEN":
            endedThrough = "Open"
        elif getThisItemFromReview.reviewActions == "LEAVE_CLOSED":
            endedThrough = "Leave_Close"
        elif getThisItemFromReview.reviewActions == "EDIT":
            endedThrough = "Edited"
    else:
        endedThrough = ''

    is_reviewed = ''
    if getThisItemFromReview:
        if request.user in getThisItemFromReview.reopen_reviewed_by.all():
            is_reviewed = True
        else:
            is_reviewed = False

    context = {
        'questionUNClose': questionUNClose,
        'endedThrough': endedThrough,
        'likepost': likepost,
        'likeDownpost': likeDownpost,
        'allToShowVotes': allToShowVotes,
        'is_reviewed': is_reviewed,
        'getReviewersByVote': getReviewersByVote,
        'data': data,
        'form': form,
        'getUNCloseHistorys': getUNCloseHistorys}
    return render(request, 'review/ReOpenQuestionReview.html', context)
