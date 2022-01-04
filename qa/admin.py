from django.contrib import admin
from django.contrib.admin import site
import adminactions.actions as actions
from .models import Question,Answer,Bounty,Reputation,QDownvote
from .models import ProtectQuestion,CommentQ,QUpvote,BookmarkQuestion
# from .models import ADownvote,AUpvote
from .models import BannedUser
from simple_history.admin import SimpleHistoryAdmin
actions.add_to_site(site)


admin.site.register(Question,SimpleHistoryAdmin)

admin.site.register(BookmarkQuestion)

admin.site.register(Answer)

admin.site.register(Bounty)

admin.site.register(Reputation)

admin.site.register(ProtectQuestion)

admin.site.register(CommentQ)

admin.site.register(QUpvote)

admin.site.register(QDownvote)

admin.site.register(BannedUser)