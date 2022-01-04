from django.urls import path
from django.conf import settings
from django.conf.urls.static import static 
from . import views
from django.views.decorators.cache import cache_page

app_name = 'tools'

urlpatterns = [

	path('moderator_tools/', views.moderator_tools, name='moderator_tools'),

	path('deletePosts_Mod_Tools/', views.deletePosts_Mod_Tools, name='deletePosts_Mod_Tools'),

	path('question_with_extreme_votes_Mod_Tools/', views.question_with_extreme_votes_Mod_Tools, name='question_with_extreme_votes_Mod_Tools'),

	path('extreme_vote_on_answers/', views.answer_with_extreme_votes_Mod_Tools, name='extreme_ans_votes'),

	path('most_cmts_vws_edts/', views.questions_withmost_commts_vws_edts_Mod_Tools, name='most_cmts_vws_edts'),

	path('recentlyPrtcdQns_Mod_Tools/', views.recentlyPrtcdQns_Mod_Tools, name='recentlyPrtcdQns_Mod_Tools'),

	path('recentlyClsd_Mod_Tools/', views.recentlyClsd_Mod_Tools, name='recentlyClsd_Mod_Tools'),

	path('recently_reopnd_Mod_Tools/', views.recently_reopnd_Mod_Tools, name='recently_reopnd_Mod_Tools'),

	path('pending_Close_Vts_Mod_Tools/', views.pending_Close_Vts_Mod_Tools, name='pending_Close_Vts_Mod_Tools'),

	path('pending_reopen_Vts_Mod_Tools/', views.pending_reopen_Vts_Mod_Tools, name='pending_reopen_Vts_Mod_Tools'),

	path('newAns_To_oldQns_Mod_Tools/', views.newAns_To_oldQns_Mod_Tools, name='newAns_To_oldQns_Mod_Tools'),

]