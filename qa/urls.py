from django.urls import path
from .  import views
from django.conf import settings
from django.conf.urls.static import static 
from .feeds import LatestQuestionFeed

app_name = 'qa'

urlpatterns = [

	path('new_question/', views.new_question, name='new_question'),

	path('questionDetailView/<int:pk>/', views.questionDetailView, name='questionDetailView'),

	path('questions/', views.questions, name='questions'),

	path('edit_question/<int:question_id>/', views.edit_question, name='edit_question'),

	path('question_upvote_downvote/<int:question_id>/', views.question_upvote_downvote, name='question_upvote_downvote'),

	path('mark_accepted/<int:question_id>/<int:answer_id>/', views.mark_accepted, name='mark_accepted'),

	path('bookmarkIt/<int:question_id>/', views.bookmarkIt, name='bookmarkIt'),

	path('BountiedQuestions/<query>', views.BountiedQuestions, name='BountiedQuestions'),

	path('answer_upvote_downvote/<int:answer_id>/', views.answer_upvote_downvote, name='answer_upvote_downvote'),

	path('awardBounty/<int:question_id>/<int:answer_id>/', views.awardBounty, name='awardBounty'),

	path('removeProtection/<int:question_id>/', views.removeProtection, name='removeProtection'),

	path('save_comment/<int:question_id>/', views.save_comment, name='save_comment'),

	path('upvote_comment/<int:commentq_id>/', views.upvote_comment, name='upvote_comment'),

	path('edit_answer/<int:answer_id>/', views.edit_answer, name='edit_answer'),

	path('deleteQuestion/<int:question_id>/', views.deleteQuestion, name='deleteQuestion'),

	path('undeleteQuestion/<int:question_id>/', views.undeleteQuestion, name='undeleteQuestion'),

	path('validateQuestionTitle/', views.validateQuestionTitle, name='validateQuestionTitle'),

	path('reviewQuestion/', views.reviewQuestion, name='reviewQuestion'),

	path('timeline/<int:question_id>/', views.questionTimeline, name='questionTimeline'),

	path('answerTimeline/<int:answer_id>/', views.answerTimeline, name='answerTimeline'),

	path('end_bounty_thread/<int:id>/', views.end_bounty_thread, name='end_bounty_thread'),

	path('banUser/<int:user_id>/', views.banUser, name='banUser'),

	path('allActiveThreads/', views.allActiveThreads, name='allActiveThreads'),

	path('UnBanUser/<int:id>/', views.UnBanUser, name='UnBanUser'),

	path('bookmarkQuestion/<int:question_id>/', views.bookmarkQuestion, name='bookmarkQuestion'),

	path('flagComment/<int:commentq_id>/', views.flagComment, name='flagComment'),

	path('save_comment_answer/<int:answer_id>/', views.save_comment_answer, name='save_comment_answer'),

	path('FlagCommentAjax/<int:commentq_id>/', views.FlagCommentAjax, name='FlagCommentAjax'),

	path('AjaxBountyForm/<int:question_id>/', views.AjaxBountyForm, name='AjaxBountyForm'),

	path('AjaxCloseForm/<int:question_id>/', views.AjaxCloseForm, name='AjaxCloseForm'),

	path('ProtectQuestionAjax/<int:question_id>/', views.ProtectQuestionAjax, name='ProtectQuestionAjax'),

	path('getCommunityWikiAnswerDetails/<int:answer_id>/', views.getCommunityWikiAnswerDetails, name='getCommunityWikiAnswerDetails'),

	path('ReOpenVotesAjax/<int:question_id>/', views.ReOpenVotesAjax, name='ReOpenVotesAjax'),

	path('award_InformedBadge_OnScroll/', views.award_InformedBadge_OnScroll, name='award_InformedBadge_OnScroll'),

	path('tourPage/', views.tourPage, name='tourPage'),

	path('AjaxFlagForm/<int:question_id>/', views.AjaxFlagForm, name='AjaxFlagForm'),

	path('Ajax_searchUser_Moderators/', views.Ajax_searchUser_Moderators, name='Ajax_searchUser_Moderators'),

	# path('inlineTagEditing_Mod_Tools/<int:question_id>/', views.inlineTagEditing_Mod_Tools, name='inlineTagEditing_Mod_Tools'),

	path('InlineTagEditingForm/<int:question_id>/', views.InlineTagEditingForm, name='InlineTagEditingForm'),

	path('feed/', LatestQuestionFeed(), name='post_feed'),

	path('flag_answer_ajax/<int:answer_id>/', views.flag_answer_ajax, name='flag_answer_ajax'),

	path('answer_edit_history/<int:answer_id>/', views.answer_edit_history, name='answer_edit_history'),

	path('getQuestionEditHistory/<int:question_id>/', views.getQuestionEditHistory, name='getQuestionEditHistory'),

	path('delete_answer/<int:answer_id>/', views.delete_answer, name='delete_answer'),

	path('undelete_answer/<int:answer_id>/', views.undelete_answer, name='undelete_answer'),

	path('unansweredQuestions/<query>/', views.unansweredQuestions, name='unansweredQuestions'),

	path('activeQuestions/<query>/', views.activeQuestions, name='activeQuestions'),

	path('load_question_upvotes_downvotes/<int:question_id>/', views.load_question_upvotes_downvotes, name='load_question_upvotes_downvotes'),

	path('load_answer_upvotes_downvotes/<int:answer_id>/', views.load_answer_upvotes_downvotes, name='load_answer_upvotes_downvotes'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


