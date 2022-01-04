from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'review'

urlpatterns = [

	path('review_FirstAns/<int:answer_id>/', views.review_FirstAns, name='review_FirstAns'),

	path('review_answer_page/', views.review_answer_page, name='review_answer_page'),

	path('editFromReview/<int:answer_id>/', views.editFromReview, name='editFromReview'),

    path('post/ajax/EditAllowanceAjaxForm/<int:answer_id>/', views.EditAllowanceAjaxForm, name = "EditAllowanceAjaxForm"),

    path('post/ajax/EditQuestionAjax/<int:question_id>/', views.EditQuestionAjax, name = "EditQuestionAjax"),

    path('review_FirstQns/<int:question_id>/', views.review_FirstQns, name='review_FirstQns'),

    path('review_LateAnswers/<int:answer_id>/', views.review_LateAnswers, name='review_LateAnswers'),

    # path('reviewEdited_questions/<int:questionedit_id>/', views.reviewEdited_questions, name='reviewEdited_questions'),

    path('reviewClosedQuestions/<int:reviewclosevotes_id>/', views.reviewClosedQuestions, name='reviewClosedQuestions'),

    path('reOpen_Question_Review/<int:reviewquestionreopenvotes_id>/', views.reOpen_Question_Review, name='reOpen_Question_Review'),

    # path('edit_in_Closing/<int:question_id>/', views.edit_in_Closing, name='edit_in_Closing'),

    path('edit_in_Closing_Ajax/<int:question_id>/', views.edit_in_Closing_Ajax, name='edit_in_Closing_Ajax'),

    # path('reviewCloseInThis/<int:reviewclosevotes_id>/', views.reviewCloseInThis, name='reviewCloseInThis'),

    # path('reOpenReview/<int:reviewquestionreopenvotes_id>/', views.reOpenReview, name='reOpenReview'),

    path('retract_Close_Flag/<int:question_id>/', views.retract_Close_Flag, name='retract_Close_Flag'),

    path('reviewSuggesstedEdit/<int:reviewquestionedit_id>/', views.reviewSuggesstedEdit, name='reviewSuggesstedEdit'),

    path('reviewFlagPosts/<int:reviewflagpost_id>/', views.reviewFlagPosts, name='reviewFlagPosts'),

    path('reviewLowQualityPosts/<int:reviewlowqualityposts_id>/', views.reviewLowQualityPosts, name='reviewLowQualityPosts'),

    path('reviewFlagComments/<int:reviewflagcomment_id>/', views.reviewFlagComments, name='reviewFlagComments'),

    path('Edit_Q_In_SuggesstedEdits/<int:question_id>/', views.Edit_Q_In_SuggesstedEdits, name='Edit_Q_In_SuggesstedEdits'),

    path('Edit_Answer_In_SuggesstedEdits/<int:answer_id>/', views.Edit_Answer_In_SuggesstedEdits, name='Edit_Answer_In_SuggesstedEdits'),

    path('retract_Flag_Form/<int:question_id>/', views.retract_Flag_Form, name='retract_Flag_Form'),

    path('suggesstedEditHistory_Question/<int:reviewquestionedit_id>/', views.suggesstedEditHistory_Question, name='suggesstedEditHistory_Question'),

    path('questionCloseHistory/<int:reviewclosevotes_id>/', views.questionCloseHistory, name='questionCloseHistory'),

    path('flag_Posts_History/<int:reviewflagpost_id>/', views.flag_Posts_History, name='flag_Posts_History'),

    path('reOpen_Question_History/<int:reviewquestionreopenvotes_id>/', views.reOpen_Question_History, name='reOpen_Question_History'),

]