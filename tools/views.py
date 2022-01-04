from django.shortcuts import render
from qa.models import Answer,Question,ProtectQuestion
from review.models import ReviewCloseVotes,ReviewQuestionReOpenVotes
from itertools import chain
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from qa.decorators import access_mod_tools_priv_required

@access_mod_tools_priv_required
def moderator_tools(request):

    context = {}
    return render(request, 'tools/moderatorTools.html')


def deletePosts_Mod_Tools(request):
    questions = list(Question.objects.filter(is_deleted=True))
    answers = list(Answer.objects.filter(is_deleted=True))

    def order_by(obj):
        try:
            return obj.deleted_time
        except AttributeError:
            return obj.deleted_time

    results = sorted(chain(questions, answers),key=order_by , reverse=True)

    context = {'results':results,}
    return render(request, 'tools/deletePosts_Mod_Tools.html', context)


def question_with_extreme_votes_Mod_Tools(request):
    questions = Question.objects.all().order_by('-qupvote')

    context = {'questions':questions,}
    return render(request, 'tools/question_with_extreme_votes_Mod_Tools.html', context)


def answer_with_extreme_votes_Mod_Tools(request):
    answers = Answer.objects.annotate(countVotes=Count('a_vote_ups')).order_by('-countVotes')

    context = {'answers':answers}
    return render(request, 'tools/answer_with_extreme_votes_Mod_Tools.html', context)


def questions_withmost_commts_vws_edts_Mod_Tools(request):
    questions_comnts = Question.objects.all().order_by('-commentq')
    question_vws = Question.objects.all().order_by('-viewers')
    question_edts = Question.objects.all().order_by('-reviewquestionedit').distinct()

    context = {'questions_comnts':questions_comnts,'question_vws':question_vws,'question_edts':question_edts,}
    return render(request, 'tools/postWithMost_Commts_Vws_Edts_Mod_Tools.html', context)


def recentlyPrtcdQns_Mod_Tools(request):
    protected_questions = ProtectQuestion.objects.all().order_by('-protected_date')

    context = {'protected_questions':protected_questions,}
    return render(request, 'tools/recentlyPrtcdQns_Mod_Tools.html', context)


def recentlyClsd_Mod_Tools(request):
    closed_questions = ReviewCloseVotes.objects.filter(is_completed=True, reviewActions="Close").order_by('-date')

    context = {'closed_questions':closed_questions}
    return render(request, 'tools/recentlyClsd_Mod_Tools.html', context)


def recently_reopnd_Mod_Tools(request):
    reopened_questions = ReviewQuestionReOpenVotes.objects.filter(is_completed=True, reviewActions="OPEN").order_by('-date')

    context = {'reopened_questions':reopened_questions}
    return render(request, 'tools/recently_reopnd_Mod_Tools.html', context)


def pending_Close_Vts_Mod_Tools(request):
    pnding_close_votes = ReviewCloseVotes.objects.filter(
                                is_completed=False).exclude(
                                    question_to_closed__is_closed=True)

    context = {'pnding_close_votes':pnding_close_votes,}
    return render(request, 'tools/pending_Close_Vts_Mod_Tools.html', context)


def pending_reopen_Vts_Mod_Tools(request):
    pnding_reopen_votes = ReviewQuestionReOpenVotes.objects.filter(
                                is_completed=False)

    context = {'pnding_reopen_votes':pnding_reopen_votes,}
    return render(request, 'tools/pending_reopen_Vts_Mod_Tools.html', context)


def newAns_To_oldQns_Mod_Tools(request):
    # Of questions which are older than 183 days (6 months)
    new_answers = Answer.objects.filter(
            lateanswerreview__L_AnswerActions__isnull=True).filter(
                questionans__date__lte=timezone.now() - timedelta(days=2)).filter(
                    date__gte=timezone.now() - timedelta(days=10))
                # Show late answers in list of last days 
    context = {'new_answers':new_answers,}
    return render(request, 'tools/newAns_To_oldQns.html', context)


# def suggstd_Edts_Stts_Mod_Tools(request):

#     context = {}
#     return render(request, 'tools/suggstd_Edts_Stts_Mod_Tools.html', context)