from django import template
from qa.models import Reputation
from django.db.models import Count,BooleanField, ExpressionWrapper, Q,Exists, OuterRef,Avg, Min,Max, Sum,F, IntegerField, FloatField,Case, Value, When
from tagbadge.models import TagBadge

register = template.Library()

@register.filter
def calculateEarned_Badge_Users(tag):
	counting = TagBadge.objects.filter(id=tag).aggregate(Sum('awarded_to_user'))
	return counting