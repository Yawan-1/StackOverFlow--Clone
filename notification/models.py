from django.db import models
from django.contrib.auth.models import User
from qa.models import Question,Answer

TYPE_OF_NOTI = [

	('comment_answer','comment_answer'),
	('question_comment','question_comment'),
	('community_message','community_message'),
	('question_edit', 'question_edit'),
	('question_reopen_voted','Question ReOpen Voted'),
	('question_suggested_edit', 'Question Suggested Edit'),
	('NEW_ANSWER', 'New_Answer'),

]

class Notification(models.Model):
	noti_receiver = models.ForeignKey(User,on_delete=models.CASCADE, default='', related_name='noti_receiver')
	type_of_noti = models.CharField(max_length=30,choices=TYPE_OF_NOTI,default='')
	url = models.URLField(null=True,blank=True)
	date_created = models.DateTimeField(auto_now_add=True)
	is_read = models.BooleanField(default=False)
	question_noti = models.ForeignKey(Question, on_delete=models.CASCADE, blank=True, null=True)
	answer_noti = models.ForeignKey(Answer, on_delete=models.CASCADE, blank=True, null=True)

	def __str__(self):
		return f"{self.type_of_noti} - [USER] {self.noti_receiver} - [READED?] - {self.is_read}"

PRIV_NOTIFY_CHOICES = [

	('EDIT_GOT_APPROVED', 'Edit Approved'),
	# ('DOWN_VOTE_ANSWER_REP_M', 'Answer Down Vote Rep Minus'),
	('ANSWER_ACCEPT_REP_P', 'Answer Accept Rep Plus'),
	('BOUNTY_AWARDED_REP_P', 'Bounty Award Rep Plus'),
	('MY_ANSWER_UPVOTE_REP_P', 'Answered Answer Upvote Rep Plus'),
	('QUESTION_DOWNVOTE', 'Question DownVote'),
	('MY_QUESTION_UPVOTE_REP_P', 'Asked Question Upvote Rep Plus'),
	('Privilege_Earned', 'Privilege Earned'),
	('BADGE_EARNED', 'Badge Earned')
]

class PrivRepNotification(models.Model):
	for_user = models.ForeignKey(User, on_delete=models.CASCADE)
	url = models.URLField(null=True, blank=True, default="#")
	for_if = models.CharField(max_length=30,default='')
	date_created_PrivNotify = models.DateTimeField(auto_now_add=True)
	is_read = models.BooleanField(default=False)
	type_of_PrivNotify = models.CharField(max_length=30, choices=PRIV_NOTIFY_CHOICES,default='')
	missingReputation = models.IntegerField(default=0, blank=True, null=True)
	privilegeURL = models.URLField(null=True, blank=True)
	description = models.CharField(max_length=1000, default='')
	question_priv_noti = models.ForeignKey(Question, on_delete=models.CASCADE, blank=True, null=True)
	answer_priv_noti = models.ForeignKey(Answer, on_delete=models.CASCADE, blank=True, null=True)

	def __str__(self):
		return self.type_of_PrivNotify

# PRIV_NOTIFY_CHOICES = [

# 	('QUESTION_EDIT_REP_P', 'Question edit Rep Plus'),
# 	('ANSWER_EDIT_REP_P', 'Answer edit Rep Plus'),
# 	('DOWN_VOTE_ANSWER_REP_M', 'Answer Down Vote Rep Minus'),
# 	('ANSWER_ACCEPT_REP_P', 'Answer Accept Rep Plus'),
# 	('BOUNTY_AWARDED_REP_P', 'Bounty Award Rep Plus'),
# 	('MY_ANSWER_UPVOTE_REP_P', 'Answered Answer Upvote Rep Plus'),
# 	('QUESTION_DOWNVOTE', 'Question DownVote'),
# 	('MY_QUESTION_UPVOTE_REP_P', 'Asked Question Upvote Rep Plus'),
# 	("EDIT_GOT_APPROVED", "Approved Edit"),
# 	('Privilege_Earned', 'Privilege Earned'),
# ]

# class privilegeNotification(models.Model):
# 	for_user = models.ForeignKey(User, on_delete=models.CASCADE)
# 	url = models.URLField(null=True, blank=True)
# 	is_read = models.BooleanField(default=False)
# 	date = models.DateTimeField(auto_now_add=True)
# 	type_of_PrivNotify = models.CharField(max_length=30, choices=PRIV_NOTIFY_CHOICES,default='')



