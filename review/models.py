from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import datetime
from django.utils import timezone
from datetime import timedelta
from qa.models import Answer,Question
from simple_history.models import HistoricalRecords
from qa.models import CommentQ

REVIEW_ANSWER_ACTION_CHOICES = [

    ('LOOKS_OK','Looks Ok'),
    ('EDIT', 'Edit'),
    ('SHARE_FEEDBACK','Share Feedback'),
    ('SKIPPED','Skip'),

]

# Need 500 Rep
class FirstAnswerReview(models.Model):
    AnswerReviewedBy = models.ForeignKey(User, on_delete=models.CASCADE)
    answerReview = models.ForeignKey(Answer, on_delete=models.CASCADE)
    actions = models.CharField(max_length=30, choices=REVIEW_ANSWER_ACTION_CHOICES,null=True)
    # testEdit = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'[Answer] - {self.answerReview}'

REVIEW_QUESTION_ACTIONS_CHOICES = [

    ('LOOKS_OK','Looks Ok'),
    ('EDIT', 'Edit'),
    ('SHARE_FEEDBACK','Share Feedback'),
    ('SKIPPED','Skip'),

]

# Need 500 Rep
class FirstQuestionReview(models.Model):
    QuestionReviewBy = models.ForeignKey(User, on_delete=models.CASCADE)
    questionReview = models.ForeignKey(Question, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    questionActions = models.CharField(max_length=30, choices=REVIEW_QUESTION_ACTIONS_CHOICES,null=True)

    def __str__(self):
        return f"[QUESTION] - {self.QuestionReviewBy}"

LATE_ANSWER_ACTIONS_CHOICES = [

    ('LOOKS_OK','Looks Ok'),
    ('EDIT', 'Edit'),
    ('RECOMMEND_DELETION','Recommend Deletion'),
    ('SKIPPED','Skip'),    

]

# Need 500 Rep
class LateAnswerReview(models.Model):
    L_AnswerReviewdBy = models.ForeignKey(User, on_delete=models.CASCADE)
    L_answerReview = models.ForeignKey(Answer, on_delete=models.CASCADE)
    L_AnswerActions = models.CharField(max_length=30, choices=LATE_ANSWER_ACTIONS_CHOICES,null=True, verbose_name='Late Answers Review')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[ANSWER] - {self.L_answerReview}"

APPROVAL_CHOICES = [

    ('None','None'),
    ('Approve', 'Approve'),
    ('Reject', 'Reject'),

]

# QUESTION EDIT REVIEW - START====================================================

# Need 2000 Rep
class QuestionEditVotes(models.Model):
    edit_suggested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    edited_question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    edited_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    edited_suggested_at = models.DateTimeField(auto_now_add=True)
    how_many_votes_on_approve = models.IntegerField(default=0)
    how_many_votes_on_reject = models.IntegerField(default=0)
    rev_Action = models.CharField(max_length=30, blank=True, null=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        if self.edited_question:
            return f"[Question] = {self.edited_question.title} = {self.rev_Action} = {self.is_completed}"
        else:
            return f"[Answer] = {self.rev_Action} = {self.is_completed}"

        # return f"{self.edited_question.title} = {self.rev_Action}"

EDIT_REVIEW_ACTIONS = [

    ('Approve', 'Approve'), # DONE
    ('Improve_Edit' , 'Improve Edit'), # DONE
    ('Reject_and_Edit', 'Reject and Edit'),
    ('Reject', 'Reject'), # DONE
    ('Edit', 'Edit'), # DONE
    ('Skip', 'Skip'), # DONE

]

# Need 2000 Rep
class ReviewQuestionEdit(models.Model):
    question_to_view = models.ForeignKey(Question, on_delete=models.CASCADE, blank=True, null=True)
    answer_to_view_if = models.ForeignKey(Answer, on_delete=models.CASCADE, blank=True, null=True)
    edit_reviewed_by = models.ManyToManyField(User, related_name="edit_reviewed_by")
    queue_of = models.ForeignKey(QuestionEditVotes, on_delete=models.CASCADE, blank=True, null=True)
    date_reviewed = models.DateTimeField(auto_now_add=True)
    reviewActions = models.CharField(max_length=30, choices=EDIT_REVIEW_ACTIONS, blank=True, null=True)
    is_reviewed = models.BooleanField(default=False, blank=True, null=True)

    # def get_absolute_url(self):
    #     # 'slug':self.slug})
    #     return reverse('review:reviewSuggesstedEdit', kwargs={'pk': self.queue_of.edited_question.id, })


    def __str__(self):
        if self.is_reviewed:
            return f"Reviewed"
        else:
            return f"On-Going"

    # def get_absolute_url(self):
        # return reverse('review:reviewSuggesstedEdit', kwargs={'pk': self.ReviewQuestionEdit.id})

# QUESTION EDIT REVIEW - END====================================================



# CLOSE QUESTION VOTES============================================================


CLOSE_ACTIONS_Q = [

    ('DUPLICATE','duplicate'),
    ('OPINION_BASED','Opinion Based'),
    ('OFF_TOPIC','Off Topic'),
    ('NEEDS_DETAILS_OR_CLARITY','Needs details or Clarity'),
    ('NEED_MORE_FOCUS','Need More Focus'),

]

# Need 3000 Rep
class CloseQuestionVotes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question_to_closing = models.ForeignKey(Question,on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    # CHANGE duplicate_of's CharField into URLField
    duplicate_of = models.CharField(max_length=1000, default='', null=True, blank=True)
    why_closing = models.CharField(max_length=30,choices=CLOSE_ACTIONS_Q)
    how_many_votes_on_Close = models.IntegerField(default=0)
    how_many_votes_on_Leave_open = models.IntegerField(default=0)
    ended = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.question_to_closing.title} [WHY] - {self.why_closing}"



CLOSE_REVIEW_ACTION_CHOICES = [

    ('Close', 'Close'),
    ("Leave_open", "Leave_open"),
    ('Edit', 'Edit'),

]

# class ReviewClosed_Question(models.Model):

ENDED_CHOICES = [

    ('THROUGH_CLOSE', 'Through Close'),
    ('THROUGH_LEAVE_OPEN', 'Through Leave Open')

]

# Need 3000 Rep
class ReviewCloseVotes(models.Model):
    question_to_closed = models.ForeignKey(Question, on_delete=models.CASCADE,default='')
    review_of = models.ForeignKey(CloseQuestionVotes, on_delete=models.CASCADE,default='', null=True)
    reviewActions = models.CharField(max_length=30,choices=CLOSE_REVIEW_ACTION_CHOICES, blank=True, null=True)
    reviewed_by = models.ManyToManyField(User, related_name="reviewed_by")
    is_completed = models.BooleanField(default=False)
    how_Ended = models.CharField(max_length=30, choices=ENDED_CHOICES, blank=True, null=True)
    finalResult = models.CharField(max_length=30, default='', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.is_completed:
            return f"{self.how_Ended} - Reviewed"
        else:
            return f"{self.how_Ended} - OnGoing"

    @property
    def get_close_votes(self):
        return self.review_of.how_many_votes_on_Close

    @property
    def get_lveopen_votes(self):
        return self.review_of.how_many_votes_on_Close


# CLOSE QUESTION VOTES============================================================



# REOPEN QUESTION VOTES============================================================

REOPEN_CLOSED_Q_CHOICES = [

    ('IT_IS_BETTER_NOW', 'It is Better Now'),
    ('CLOSED_BY_MISTAKE', 'Closed By Mistake'),
    ('OTHER', 'Other')

]

REOPEN_ENDED_CHOICES = [

    ('THROUGH_OPENED', 'Through Opened'),
    ('THROUGH_LEAVE_CLOSED', 'Through Leave Closed'),

]

# Need 3000 Rep
class ReOpenQuestionVotes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question_to_opening = models.ForeignKey(Question, on_delete=models.CASCADE)
    date_opening = models.DateTimeField(auto_now_add=True)
    why_opening = models.CharField(max_length=30, choices=REOPEN_CLOSED_Q_CHOICES)
    if_other = models.CharField(max_length=30, default='', null=True, blank=True)
    how_many_votes_on_Open = models.IntegerField(default=0)
    how_many_votes_on_Leave_close = models.IntegerField(default=0)
    # how_Ended = models.CharField(max_length=30, choices=REOPEN_ENDED_CHOICES, blank=True, null=True)
    ended = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return f"{self.why_opening} = {self.question_to_opening.title}"

REVIEW_REOPEN_ACTION_CHOICES = [
    
    ('OPEN', 'Open'),
    ('LEAVE_CLOSED', 'Leave Closed'),
    ('EDIT', 'EDIT'),
]

# Need 3000 Rep
class ReviewQuestionReOpenVotes(models.Model):
    question_opened = models.ForeignKey(Question, on_delete=models.CASCADE)
    review_of = models.ForeignKey(ReOpenQuestionVotes, on_delete=models.CASCADE,default='', null=True)
    reviewActions = models.CharField(max_length=30, choices=REVIEW_REOPEN_ACTION_CHOICES, blank=True, null=True)
    reopen_reviewed_by = models.ManyToManyField(User, related_name='reopen_reviewed_by')
    is_completed = models.BooleanField(default=False)
    what_happend = models.CharField(max_length=30, default='',blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.is_completed:
            return f"{self.review_of.question_to_opening.title} - Reviewed"
        else:
            return f"{self.review_of.question_to_opening.title} - On-Going"

    @property
    def count_open_votes(self):
        return self.review_of.how_many_votes_on_Open

    @property
    def count_leaveClose_votes(self):
        return self.review_of.how_many_votes_on_Leave_close

# REOPEN QUESTION VOTES============================================================

LOW_QUALITY_CHOICES = [

    ('Looks_OK', 'Looks Ok'),
    ('Edit', 'Edit'),
    ('Recommend_Delete', 'Recommend Delete'),
    ('Recommend_Close', 'Recommend Close'),
    ('Skip', 'Skip'),

]

WHY_LOW_QUALTY = [

    ('Answer_Less_Than_200', 'Answer is Less than 200 Words'),
    ('Question_Less_Than_200', 'Question is Less than 200 Words'),
    ('Comment_As_Answer', 'Comment as Answer'),

]

SUGGEST_CHOICES = [

    ('User', 'User'),
    ('Automatic', 'Automatic')

]

# Need 2000 Rep
class LowQualityPostsCheck(models.Model):
    suggested_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    suggested_through = models.CharField(max_length=30, choices=SUGGEST_CHOICES)
    low_is = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    low_ans_is = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    why_low_quality = models.CharField(max_length=30, choices=WHY_LOW_QUALTY)
    is_completed = models.BooleanField(default=False)

    how_many_votes_on_OK = models.IntegerField(default=0)
    how_many_votes_on_deleteIt = models.IntegerField(default=0)
    how_many_votes_on_close = models.IntegerField(default=0)

    at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.low_is:
            return f"[Q] {self.why_low_quality} - [Q] - {self.low_is.title}"
        else:
            return f"[A] {self.why_low_quality} - [A] - {self.low_ans_is.body}"



# Need 2000 Rep
class ReviewLowQualityPosts(models.Model):
    reviewers = models.ManyToManyField(User, related_name="reviewers")
    review_of = models.ForeignKey(LowQualityPostsCheck, on_delete=models.CASCADE)
    reviewActions = models.CharField(max_length=30, choices=LOW_QUALITY_CHOICES, blank=True, null=True)
    is_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, blank=True, null=True)
    is_question = models.ForeignKey(Question, on_delete=models.CASCADE, blank=True, null=True)
    is_reviewed = models.BooleanField(default=False)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.is_reviewed:
            return f"Reviewed"
        else:
            return f"Pending"

# ---------------------------------------FLAG Q/A-------START

Q_Flags_Choices = [

    ('SPAM', 'Spam'), # Automatic = POST
    ('RUDE_OR_ABUSIVE', 'Rude or Abusive'), # Automatic = POST
    ('NOT_AN_ANSWER', 'Not an Answer'), # Only For Answer = ANSWER
    ('IN_NEED_OF_MODERATOR_INTERVATION', 'In Need of Moderator Intervation'), # Can only seen by moderators = POST
        # It needs a text field.
    # ('NEED_ADDITIONAL_DETAILS','Needs Additional Details'), # = QUESTION
    # ('NEED_TO_MORE_FOCUSED','Needs to be More Focused'), # Will be = QUESTION

    ('VERY_LOW_QUALITY', 'Very Low Quality'), # Will be pushed to Low Quality Posts = QUESTION


    ('NEEDS_IMPROVEMENT', 'Needs Improvement'),# = QUESTION
            ('DUPLICATE', 'Duplicate'), # ----Close Review----
            ('OPINION_BASED', 'Opinion Based'),# = QUESTION # ----Close Review----
            ('NEED_MORE_FOCUS', 'Need More Focus# = QUESTION'),# = QUESTION # ----Close Review----
            ('NEED_ADDITIONAL_DETAILS','Needs Additional Details'), # = QUESTION # ----Close Review----
        ('A_COMMUNITY_SPECIFIC_REASON', 'A Community specific reason'),# = QUESTION

            ('ABOUT_GENERAL_COMPUTING_HAR', 'About General'),# = QUESTION # ----Close Review----
            ('ABOUT_PROFESSIONAL', 'About Professional'),# = QUESTION # ----Close Review----
            ('SEEKING_RECCOMENDATIONS', 'Seeking Reccomendations'),# = QUESTION # ----Close Review----
            ('NEED_DEBUGGING', 'Need Debugging Details'),# = QUESTION # ----Close Review----
            ('NOT_REPRODUCIBLE', 'Not Reproducible'),# = QUESTION # ----Close Review----
            ('BLANTANLTY_OR_CLARITY', 'Blantanlity or Clarity'),# = QUESTION # ----Close Review----

]

"""

needs improvement
 - a community specific reason
     - about general computing hardware and software
     - about professional server-or networking-related infrastructure administration
     - seeking recommendations for books
     - need deubugging details
     - not reproducible or was caused by type
     - blatanlty off-topic
 - needs details or clarity
 - needs more focus
 - opinion based

"""

"""
Don't Review Spam and Rude, just count them and if post
got 3 of them.

Not an anser and Very low quality and NEED_TO_MORE_FOCUSED and NEED_ADDITIONAL_DETAILS are of Very Low Qualities thing.

IN_NEED_OF_MODERATOR_INTERVATION will only see to moderators.
"""

class FlagPost(models.Model):
    flagged_by = models.ForeignKey(User, on_delete=models.CASCADE)
    question_forFlag = models.ForeignKey(Question, on_delete=models.CASCADE, blank=True, null=True)
    answer_forFlag = models.ForeignKey(Answer, on_delete=models.CASCADE, blank=True, null=True)
    actions_Flag_Q = models.CharField(max_length=300, choices=Q_Flags_Choices)

    how_many_votes_on_spamANDRude = models.IntegerField(default=0)
    how_many_votes_on_notAnAnswer = models.IntegerField(default=0)
    how_many_votes_on_others = models.IntegerField(default=0)

    flagged_at = models.DateTimeField(auto_now_add=True)
    ended = models.BooleanField(default=False)

    def __str__(self):
        return f"[WHY-FLAG] - {self.actions_Flag_Q}"

FLAG_REVIEW_CHOICES = [

    ('DELETE_IT', 'Delete It'),
    ('STAY_AS_IT_IS', 'No Actions Needed, Stay Open'),
    ('CLOSE_IT', 'Close It'),
    ('SKIP', 'Skip')

]

class ReviewFlagPost(models.Model):
    flag_question_to_view = models.ForeignKey(Question, on_delete=models.CASCADE, blank=True, null=True)
    flag_answer_to_view_if = models.ForeignKey(Answer, on_delete=models.CASCADE, blank=True, null=True)
    flag_reviewed_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    flag_of = models.ForeignKey(FlagPost, on_delete=models.CASCADE, blank=True, null=True)
    flagReviewActions = models.CharField(max_length=30, choices=FLAG_REVIEW_CHOICES)
    flag_is_reviewed = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        if self.flag_is_reviewed:
            return f"Reviewed"
        else:
            return f"On-Going"

# ---------------------------------------FLAG Q/A-------END





# ---------------------------------------FLAG COMMENT-------START

COMMENT_FLAG_CHOICES = [

    ('HARRASSMENT', 'Harrassment'),
    ('UNKIND', 'UnKind'),
    ('NOT_NEEDED', 'No longer Needed'),
    ('SOMETHING_ELSE', 'Something Else'),

]

class FlagComment(models.Model):
    comment_of = models.ForeignKey(CommentQ, on_delete=models.CASCADE)
    comment_flagged_by = models.ForeignKey(User, on_delete=models.CASCADE)
    why_flagging = models.CharField(max_length=30, choices=COMMENT_FLAG_CHOICES)
    something_else = models.CharField(max_length=30, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    how_many_votes_on_notNeeded_unkind = models.IntegerField(default=0)
    how_many_votes_on_harr_else = models.IntegerField(default=0)
    ended = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.comment_of}"


C_FLAG_ACTIONS = [

    ('DELETE_IT', 'Delete It'),
    ('STAY_AS_IT_IS', 'No Actions Needed'),
    ('SKIP', 'Skip'),

]

class ReviewFlagComment(models.Model):
    flag_of = models.ForeignKey(CommentQ, on_delete=models.CASCADE)
    review_of = models.ForeignKey(FlagComment, on_delete=models.CASCADE, default='',null=True)
    c_flag_reviewed_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    c_flagReviewActions = models.CharField(max_length=30, choices=C_FLAG_ACTIONS)
    c_is_reviewed = models.BooleanField(default=False)

    def __str__(self):
        if self.c_is_reviewed:
            return f"Reviewed"
        else:
            return f"On-Going"

# ---------------------------------------FLAG COMMENT------END



class MyModel(models.Model):
    this = models.CharField(max_length=30, default='')

# class MyModel_1(models.Model):
#     field_2 = models.CharField(max_length=30, default='')