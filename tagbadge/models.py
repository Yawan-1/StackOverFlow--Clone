from django.db import models
from django.contrib.auth.models import User
# from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from qa.models import Question,Answer


BADGE_POSITION_CHOICES = [
	
	('TAG','Tag'),
	('BADGE','Badge'),

]


BADGE_TYPE_CHOICES = [

	('GOLD', 'Gold'),
	('SILVER', 'Silver'),
	('BRONZE', 'Bronze')

]



class TagBadge(models.Model):
	awarded_to_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='awarded_to_user')
	description = models.CharField(max_length=500, blank=True, null=True)
	badge_type = models.CharField(max_length=30,choices=BADGE_TYPE_CHOICES)
	tag_name = models.CharField(max_length=30, default='')
	preBuild = models.BooleanField(default=False)
	date = models.DateTimeField(auto_now_add=True)
	bade_position = models.CharField(max_length=30,choices=BADGE_POSITION_CHOICES,default='')
	url = models.URLField(blank=True, null=True)
	questionIf_TagOf_Q = models.ForeignKey(Question, on_delete=models.CASCADE, blank=True, null=True)
	answerIf_TagOf_A = models.ForeignKey(Answer, on_delete=models.CASCADE, blank=True, null=True)

	def __str__(self):
		return f"{self.awarded_to_user} - {self.badge_type} - {self.tag_name} - {self.bade_position} - {self.tag_name}"
