from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from qa.models import Question
import os
from random import choice
from os.path import join as path_join
from os import listdir
from os.path import isfile
import datetime
from django.utils import timezone
from datetime import timedelta
from datetime import datetime as dt
from django.urls import reverse
from qa.models import CommentQ

def random_img():
    dir_path = 'media/'
    files = [content for content in listdir(
        dir_path) if isfile(path_join(dir_path, content))]
    return path_join(dir_path, choice(files))



JOB_STATUS = [
    ('looking_for_job', 'Actively looking right now'),
    ('open_but_not_looking', 'Open, but not actively looking'),
    ('not_interested_in_jobs', 'Not interested in jobs'),
]


EXPERIENCE_LEVEL = [

    ('Student','Student'),
    ('Junior', 'Junior'),
    ('Mid_Level', 'Mid Level'),
    ('Senior', 'Senior'),
    ('Lead', 'Lead'),
    ('Manager', 'Manager'),

]

JOB_TYPE_CHOICES = [

    ('FULL_TIME', 'Full Time'),
    ('CONTRCT', 'Contract'),
    ('InternShip', 'InternShip'),

]



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=30, default='', blank=True)
    not_to_Display_Full_name = models.CharField(max_length=30, default='', blank=True)
    email = models.EmailField(max_length=30, default='')
    location = models.CharField(max_length=30, default='', blank=True)
    title = models.CharField(max_length=30, default='', blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos', default='media/isle.jpg')
    about_me = models.CharField(max_length=30, default='', blank=True, null=True)
    website_link = models.URLField(blank=True)
    twitter_link = models.URLField(blank=True)
    github_link = models.URLField(blank=True)
    bookmark_questions = models.ManyToManyField(Question, related_name='bookmark_questions', blank=True)
    q_edited_counter = models.IntegerField(default=0)
    time = models.DateTimeField(auto_now_add=True)
    reputation = models.IntegerField(default=1)
    is_banned = models.BooleanField(default=False)
    post_edit_inactive_for_six_month = models.IntegerField(default=0)
    is_moderator = models.BooleanField(default=False)
    is_high_moderator = models.BooleanField(default=False)
    targeted_tag = models.CharField(max_length=30, default='Commenter')
# BADGES
    review_close_votes = models.BooleanField(default=False)
    favorite_question_S = models.BooleanField(default=False)
    lifeJacket = models.BooleanField(default=False)


    altruist = models.BooleanField(default=False)
# PRIVILEGES
    commenter = models.BooleanField(default=False)


# OTHERS


    logout_on_all_devices = models.BooleanField(default=False)
    send_email_notifications = models.BooleanField(default=False)

    voting_flags = models.IntegerField(default=0)
    helpful_close_votes = models.IntegerField(default=0)


# DEVELOPER STORY
    name = models.CharField(max_length=30, default='')
    prefered_technologies = models.CharField(max_length=30, default='')
    min_expierence_level = models.CharField(max_length=30,choices=EXPERIENCE_LEVEL, default='')
    max_expierence_level = models.CharField(max_length=30,choices=EXPERIENCE_LEVEL, default='')
    job_type = models.CharField(max_length=30, choices=JOB_TYPE_CHOICES)
    job_search_status = models.CharField(max_length=30, choices=JOB_STATUS)
    phone_number = models.CharField(max_length=30, blank=True, null=True)


    create_posts = models.BooleanField(default=True) # Done
    create_wiki_posts = models.BooleanField(default=False) # Done
    remove_new_user_restrictions = models.BooleanField(default=False) # Done
    voteUpPriv = models.BooleanField(default=False) # Done
    flag_posts = models.BooleanField(default=False) # Done
    comment_everywhere_Priv = models.BooleanField(default=False) # Done
    set_bounties = models.BooleanField(default=False) # Done
    edit_community_wiki = models.BooleanField(default=False)
    voteDownPriv = models.BooleanField(default=False) # Done
    view_close_votes_Priv = models.BooleanField(default=False)
    access_review_queues = models.BooleanField(default=False)
    established_user_Priv = models.BooleanField(default=False) # Done
    create_tags = models.BooleanField(default=False) # Done
    edit_questions_answers = models.BooleanField(default=False) # Done
    cast_close_AND_Reopen_votes = models.BooleanField(default=False) # Done
    accessTo_moderatorTools = models.BooleanField(default=False)
    protect_questions = models.BooleanField(default=False) # Done
    trusted_user_Priv = models.BooleanField(default=False)

    helpful_flags_counter = models.IntegerField(default=0, blank=True, null=True)
    posts_edited_counter = models.IntegerField(default=0, blank=True, null=True)
    suggested_Edit_counter = models.IntegerField(default=0, blank=True, null=True)
    editPostTimeOfUser = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    Refiner_Illuminator_TagPostCounter = models.IntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return f'{self.user}'

    def get_absolute_url(self):
        return reverse('profile:activityPageTabProfile', kwargs={'user_id': self.user_id,'username': self.user.username})

    @property
    def age(self):
        current_datetime = datetime.datetime.now(timezone.utc)
        return (current_datetime - self.time).days

    # def countComments_done(self):
    #     countComments = CommentQ.objects.filter(commented_by=self)



@receiver(post_save, sender=User)  # add this
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)  # add this
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Position(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=30, default='')
    title = models.CharField(max_length=30, default='')
    company_website = models.CharField(max_length=30, default='')
    technologies = models.CharField(max_length=30, default='')
    responsibilities = models.CharField(max_length=30, default='')
