from django.contrib import admin

from .models import FirstAnswerReview,FirstQuestionReview
from .models import LateAnswerReview
# from .models import QuestionEdit
from .models import CloseQuestionVotes, ReviewQuestionReOpenVotes
from .models import ReviewCloseVotes,ReOpenQuestionVotes,QuestionEditVotes
from .models import ReviewQuestionEdit,LowQualityPostsCheck,ReviewLowQualityPosts
from .models import ReviewFlagPost,FlagComment,ReviewFlagComment,FlagPost
# admin.site.register(QuestionEdit)

admin.site.register(FirstAnswerReview)

admin.site.register(FirstQuestionReview)

admin.site.register(LateAnswerReview)

admin.site.register(CloseQuestionVotes)

admin.site.register(ReviewCloseVotes)

admin.site.register(ReOpenQuestionVotes)

admin.site.register(ReviewQuestionReOpenVotes)

admin.site.register(QuestionEditVotes)

admin.site.register(ReviewQuestionEdit)

admin.site.register(LowQualityPostsCheck)

admin.site.register(ReviewLowQualityPosts)

admin.site.register(FlagComment)

admin.site.register(ReviewFlagPost)

admin.site.register(ReviewFlagComment)

admin.site.register(FlagPost)