from django.urls import path
from django.conf import settings
from django.conf.urls.static import static 
from . import views
from django.views.decorators.cache import cache_page

app_name = 'profile'

urlpatterns = [

	path('', views.home, name='home'),

	path('activityPageTabProfile/<int:user_id>/<str:username>/', views.activityPageTabProfile, name='activityPageTabProfile'),

	path('ActivityTabSummary/<int:user_id>/<str:username>/', views.ActivityTabSummary, name='ActivityTabSummary'),

	path('usersPage/', views.usersPage, name='usersPage'),

	path('Ajax_searchTag/', views.Ajax_searchTag, name='Ajax_searchTag'),

	path('tagsPage/', views.tagsPage, name='tagsPage'),

	path('Ajax_searchUser/', views.Ajax_searchUser, name='Ajax_searchUser'),

	path('checkNotifications/', views.checkNotifications, name='checkNotifications'),

	path('userProfileEdit_Settings/<int:user_id>/', views.userProfileEdit_Settings, name='userProfileEdit_Settings'),

	path('email_html/',views.email_html,name='email_html'),

	path('tagPage/<int:user_id>/<int:tagbadge_id>/', views.tagPage, name='tagPage'),

	path('otherWithSame_Badge/<tag>/', views.otherWithSame_Badge, name='otherWithSame_Badge'),

	path('developerStoryTab/<int:user_id>/', views.developerStoryTab, name='developerStoryTab'),

	path('uploadPosition/<int:user_id>/', views.uploadPosition, name='uploadPosition'),

	path('addPositionAjax/<int:user_id>/', views.addPositionAjax, name='addPositionAjax'),

	path('select_BadgeTarget/<int:user_id>/', views.select_BadgeTarget, name='select_BadgeTarget'),

	path('activitAnswers/<int:user_id>/<str:username>/', views.activitAnswers, name='activitAnswers'),

	path('questionsActivity/<int:user_id>/<str:username>/', views.questionsActivity, name='questionsActivity'),

	path('tagsActivity/<int:user_id>/<str:username>/', views.tagsActivity, name='tagsActivity'),

	path('badgesActivity/<int:user_id>/<str:username>/', views.badgesActivity, name='badgesActivity'),

	path('bountiesActivity/<int:user_id>/<str:username>/', views.bountiesActivity, name='bountiesActivity'),

	path('bookmarksActivity/<int:user_id>/<str:username>/', views.bookmarksActivity, name='bookmarksActivity'),

	path('allActionsActivity/<int:user_id>/<str:username>/', views.allActionsActivity, name='allActionsActivity'),

	path('flag_summary/<int:user_id>/<str:username>/', views.flag_summary, name='flag_summary'),

	path('reputationActivity/<int:user_id>/<str:username>/', views.reputationActivity, name='reputationActivity'),

	path('Votes_castActivity/<int:user_id>/<str:username>/', views.Votes_castActivity, name='Votes_castActivity'),

	path('EditProfileAjaxForm/<int:user_id>/', views.EditProfileAjaxForm, name='EditProfileAjaxForm'),

	path('editProfile_JobPreAjax_Form/<int:user_id>/', views.editProfile_JobPreAjax_Form, name='editProfile_JobPreAjax_Form'),

	path('userProfileJonPrefrences_Settings/<int:user_id>/', views.userProfileJonPrefrences_Settings, name='userProfileJonPrefrences_Settings'),

	path('userProfileEdit_Email_Settings/<int:user_id>/', views.userProfileEdit_Email_Settings, name='userProfileEdit_Email_Settings'),

	path('editProfile_EditEmail_AjaxForm/<int:user_id>/', views.editProfile_EditEmail_AjaxForm, name='editProfile_EditEmail_AjaxForm'),

	path('loadQuestion_div/<int:question_id>/', views.loadQuestion_div, name='loadQuestion_div'),

	path('loadAnswer_div/<int:answer_id>/', views.loadAnswer_div, name='loadAnswer_div'),

	path('searchTagFromQuery/', views.searchTagFromQuery, name='searchTagFromQuery'),

	path('bountied_home/', views.bountied_home, name='bountied_home'),

	path('hot_q_day_home/', views.hot_q_day_home, name='hot_q_day_home'),

	path('hot_q_week_home/', views.hot_q_week_home, name='hot_q_week_home'),

	path('hot_q_month_home/', views.hot_q_month_home, name='hot_q_month_home'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
