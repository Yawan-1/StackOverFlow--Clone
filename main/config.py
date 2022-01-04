# VOTE SHOULD LOCK IN MINUTES.
# In question_upvote_downvote
UPVOTE_TIME_LIMIT = timezone.now() - timedelta(hours=10)

# NEW USER CAN ASK SECOND QUESTION IN MINUTES.
# In new_question
NEW_QUESTION_MINUTE_LIMIT = timezone.now() - timedelta(minutes=90)

