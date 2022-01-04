from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
# from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager
import datetime
from django.utils import timezone
from datetime import timedelta
from model_utils import FieldTracker
from django.db.models.signals import post_save
from django.dispatch import receiver
from martor.models import MartorField
from simple_history.models import HistoricalRecords
from django.db.models import IntegerField, Model
from django.core.validators import MaxValueValidator, MinValueValidator
from slugify import slugify

# Need to use pagination in every tab in profile pages.


ACTIVE_FOR_CHOICES = [

    ('ANSWERED', 'Answered'),
    ('MODIFIED', 'Modified'),
    ('ASKED', 'Asked'),

]


class Question(models.Model):
    post_owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=5000, default='')
    body = MartorField()
    tags = TaggableManager()
    date = models.DateTimeField(auto_now_add=True)
    active_date = models.DateTimeField(auto_now=True)
    viewers = models.ManyToManyField(User, related_name='viewed_posts', blank=True)
    q_reputation = models.IntegerField(default=0)
    q_edited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='q_edited_by', default='', null=True, blank=True)
    q_edited_time = models.DateTimeField(auto_now_add=True)  
    is_bountied = models.BooleanField(default=False)
    bounty_date_announced = models.DateTimeField(auto_now_add=True)
    limit_exced = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    is_protected = models.BooleanField(default=False)
    why_editing_question = models.CharField(max_length=5000, default='')
    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords(related_name='his')
    answeredOnMinusTwo_Downvote = models.DateTimeField(auto_now_add=True)
    is_closed = models.BooleanField(default=False)
    closed_at = models.DateTimeField(auto_now_add=True, blank=True)
    is_answer_accepted = models.BooleanField(default=False)

    reversal_monitor = models.BooleanField(default=False)

    lastActiveFor = models.CharField(choices=ACTIVE_FOR_CHOICES, max_length=5000, default='', blank=True)
    lastActiveFor_by = models.ForeignKey(User, on_delete=models.CASCADE,related_name='lastActiveFor_by', blank=True, null=True)
    slug = models.SlugField(max_length=1000, null=True, blank=True)

    deleted_time = models.DateTimeField(auto_now_add=True, blank=True)



    class Meta:
        ordering = ["-date"]

    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = slugify(
    #             f"{self.title}-{self.id}", max_length=1000, lowercase=True
    #         )

    def __str__(self):
        return f'[USER] - {self.post_owner} = [TITLE] - {self.title} - [Deleted?] - {self.is_deleted} - [Bountied?] - {self.is_bountied}'

    def get_absolute_url(self):
        # 'slug':self.slug})
        return reverse('qa:questionDetailView', kwargs={'pk': self.pk, })

    @property
    def count_answers(self):
        return Answer.objects.filter(questionans=self).exclude(is_deleted=True).count()

    @property
    def calculate_UpVote_DownVote(self):
        get_Upvotes = self.qupvote_set.count()
        get_DownVotes = self.qdownvote_set.count()
        return get_Upvotes - get_DownVotes

    @property
    def calculate_viewers(self):
        return self.viewers.all().count()

    @property
    def count_all_bookmarkers(self):
        return self.bookmarkquestion_set.all().count()

    @property
    def lastEdited_by(self):
        return self.q_edited_by

    @property
    def remainingBountyDate(self):
        if self.is_bountied:
            return self.bounty_date_announced + timedelta(days=7)

    @property
    def get_all_tags(self):
        return self.tags.all()

    @property
    def expireBounty(self):
        if self.is_bountied:
            if self.bounty_date_announced < timezone.now() - timedelta(days=7):
                self.is_bountied = False
                self.save()

    @property
    def is_question_bountied(self):
        if self.is_bountied:
            hideBountyButton = True
        else:
            hideBountyButton = False 
        return hideBountyButton

    # @property
    # def count_questions(self):
    #     return Question.objects.all().count()



class BookmarkQuestion(models.Model):
    bookmarked_by = models.ForeignKey(User, on_delete=models.CASCADE)
    bookmarked_question = models.ForeignKey(Question, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[U] {self.bookmarked_by} = [Q] {self.bookmarked_question.title}"

class QUpvote(models.Model):
    upvote_by_q = models.ForeignKey(User, on_delete=models.CASCADE)
    upvote_question_of = models.ForeignKey(Question, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    hisory = HistoricalRecords(related_name="qupvotehistory")

    def __str__(self):
        return f"{self.upvote_question_of} = [UPVOTED-BY] {self.upvote_by_q}"

class QDownvote(models.Model):
    downvote_by_q = models.ForeignKey(User, on_delete=models.CASCADE)
    downvote_question_of = models.ForeignKey(Question, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    hisory = HistoricalRecords(related_name="qdownvotehistory")

    def __str__(self):
        return f"{self.downvote_question_of} = [DOWNVOTED-BY] {self.downvote_question_of}"

DELETE_HISTORY = [

    ('DELETED','Deleted'),
    ('UNDELETED','UnDeleted'),

]

class Answer(models.Model):
    answer_owner = models.ForeignKey(User, on_delete=models.CASCADE)
    questionans = models.ForeignKey(Question, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    body = MartorField()
    a_vote_ups = models.ManyToManyField(User, related_name='a_vote_up', blank=True)
    a_vote_downs = models.ManyToManyField(User, related_name='a_vote_down', blank=True)
    accepted = models.BooleanField(default=False)
    a_reputation = models.IntegerField(default=0)
    is_bountied_awarded = models.BooleanField(default=False)
    # a_upvote_time = models.DateTimeField(auto_now_add=True)
    # a_downvote_time = models.DateTimeField(auto_now_add=True)
    active_time = models.DateTimeField(auto_now=True)
    a_edited_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='a_edited_time')
    a_edited_time = models.DateTimeField(auto_now=True)
    why_editing = models.CharField(max_length=5000,default='')
    history = HistoricalRecords(related_name='anshis')
    deletedHistory = models.CharField(max_length=5000, choices=DELETE_HISTORY, default='')
    monitor_it = models.BooleanField(default=False)
    why_editing_answer = models.CharField(max_length=5000, default='', blank=True, null=True)

    revival_stage_one = models.BooleanField(default=False, blank=True, null=True)
    # revival_stage_two = models.BooleanField(default=False, blank=True, null=True)
    necromancer_check = models.BooleanField(default=False, blank=True, null=True)
    is_wiki_answer = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_time = models.DateTimeField(auto_now_add=True, blank=True)
    # @property
    # def allVoteCal(self):
    #     return self.a_vote_ups.count.all() + self.a_vote_downs.count.all()

    # @property
    # def countVotes(self):
    #     return 

    def __str__(self):
        return f'[USER] - {self.answer_owner} = [TITLEs] - {self.body}'

    @property
    def countAllTheVotes(self):
        return self.a_vote_ups.all().count() - self.a_vote_downs.all().count()

    @property
    def count_ViewsOf_Q(self):
        return self.questionans.viewers.all().count()

    # @property
    # def get_prev_record_diff(self):   

    #     previous_record = self.get_prev_record()
 
    #     if previous_record is not None:

    #         return self.diff_against(previous_record)

    #     return None



class CommentQ(models.Model):
    question_comment = models.ForeignKey(Question,on_delete=models.CASCADE, blank=True, null=True)
    answer_comment = models.ForeignKey(Answer, on_delete=models.CASCADE, blank=True, null=True)
    commented_by = models.ForeignKey(User,on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    comment = models.CharField(max_length=200, default='')
    date = models.DateTimeField(auto_now_add=True)
    com_upvote = models.ManyToManyField(User, related_name='comm_upvote', blank=True)
    com_upvote_time = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords(related_name='commentHis')

    def __str__(self):
        if self.question_comment:
            return f"{self.comment} - {self.question_comment.title} - [D] {self.deleted}"
        else:
            return f"{self.comment} - {self.answer_comment} - [D] {self.deleted}"

    @property
    def count_upvote(self):
        return self.com_upvote.all().count()



class AnswerComment(models.Model):
    com = models.ForeignKey(Answer, on_delete=models.CASCADE, blank=True, null=True)
    tex = models.CharField(max_length=30, default='')

    def __str__(self):
        return f"{self.tex} - [D] - {self.com}"


BOUNTY_VALUE_CHOICES = [

    ('50', '50'),
    ('100', '100'),
    ('150', '150'),
    ('200', '200'),
    ('250', '250'),
    ('300', '300'),
    ('350', '350'),
    ('400', '400'),
    ('450', '450'),
    ('500', '500'),

]

class Bounty(models.Model):
    by_user = models.ForeignKey(User, on_delete=models.CASCADE)
    question_bounty = models.ForeignKey(Question, on_delete=models.CASCADE)
    bounty_awarded_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bounty_awarded_to', null=True, blank=True)
    bounty_value = models.CharField(max_length=500, choices=BOUNTY_VALUE_CHOICES, default='50')
    why_bounting = models.CharField(max_length=30, default='')
    is_awarded = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    bountyHistory = HistoricalRecords(related_name="bountyhistory")

    def __str__(self):
        return f'{self.question_bounty}'


APPROVAL_CHOICES = [

    ('Close','Close'),
    ('Leave_open', 'Leave open'),
    ('Edit', 'Edit'),
    ('Skip', 'Skip'),

]


class ProtectQuestion(models.Model):
    protected_by = models.ForeignKey(User, on_delete=models.CASCADE)
    protectionRemovedBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name='protectionRemovedBy')
    protecting_question = models.ForeignKey(Question, on_delete=models.CASCADE)
    why_want_toProtect = models.CharField(max_length=30,default='')
    protected_date = models.DateTimeField(auto_now_add=True)
    stillProtected = models.BooleanField(default=False)
    date_Removed = models.DateTimeField(auto_now_add=False,null=True,blank=True)

    def __str__(self):
        return f"{self.protecting_question}"

REPUTATION_CHOICES = [

    ('QUESTION', 'Question'),
    ('ANSWER', 'Answer'),
    ('EDIT', 'Edit'),
    ('ANSWER_ACCEPT', 'Answer Accept'),

]

INC_DEC_CHOICES = [

    ('Increased', 'Increased'),
    ('Decreased', 'Decreased'),

]

class Reputation(models.Model):
    awarded_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True,blank=True)
    question_O = models.ForeignKey(Question, on_delete=models.CASCADE, null=True,blank=True)
    answer_O = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    # user_reputation = models.IntegerField(default=0)
    inc_dec = models.CharField(max_length=30, choices=INC_DEC_CHOICES, default='')
    question_rep_C = models.IntegerField(default=0, blank=True, null=True)
    answer_rep_C = models.IntegerField(default=0, blank=True, null=True) #validators=[MinValueValidator(-1),]
    reputation_on_what = models.CharField(max_length=30, choices=REPUTATION_CHOICES, default='')
    date_earned = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.question_rep_C != 0 and self.answer_rep_C == 0:
            return f'[REPUTATION] - {self.question_rep_C} = {self.question_O.title}'
        elif self.answer_rep_C != 0 and self.question_rep_C == 0:
            return f'[REPUTATION] - {self.answer_rep_C}'  

# Ban User is Under Construction

BANN_REASONS = [

    ('DOING_SOCKPUPPETS' , 'Doing SockPuppets'),
    ('RUDE_TO_MEMBERS', 'Rude to Members'),
    ('TERMS_AND_CONDITIONS_VOILATIONS', 'Terms and Conditions Voilations'),

]

BAN_TILL_CHOICES = [

    ('3_DAYS', "3 Days"),
    ('7_DAYS', "7 Days"),
    ('15_DAYS', "15 DAYS"),
    ('30_DAYS', "30 DAYS"),
    ('2_MONTHS', "2 MONTHS"),
    ('6_MONTHS', "6 MONTHS"),
    ('1_YEAR', "1 YEAR"),
    ('4_YEARS', "4 YEARS"),

]

class BannedUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    banned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="banned_by")
    banned_reasons = models.CharField(max_length=50, choices=BANN_REASONS, default='')
    baned_at = models.DateTimeField(auto_now_add=True)
    is_banned = models.BooleanField(default=False)
    ban_till = models.CharField(max_length=30, choices=BAN_TILL_CHOICES, default='')

    def __str__(self):
        return f"{self.user} - {self.banned_reasons} - {self.ban_till}"
