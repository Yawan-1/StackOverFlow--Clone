from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from django.urls import reverse_lazy
from .models import Question

class LatestQuestionFeed(Feed):
	title = "My Question"
	link = reverse_lazy('qa:questions')
	description = 'New Post of Question'

	def items(self):
		return Question.objects.all()[:5]

	def item_title(self, item):
		return item.title

	def item_description(self, item):
		return truncatewords(item.body, 30)