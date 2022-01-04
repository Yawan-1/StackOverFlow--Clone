from django.shortcuts import render

def privileges(request):

	context = {}
	return render(request, 'help/privileges.html', context)



def CreateWikiPosts_Privilege_Info_Page(request):

	return render(request, 'privileges/createWikiPosts.html', context)

def RemoveNewUserRestric_Privilege_Info_Page(request):

	return render(request, 'privileges/RemoveNewUserRestric.html', context)

def VoteUp_Privilege_Info_Page(request):

	return render(request, 'privileges/VoteUp.html', context)

def FlagPost_Privilege_Info_Page(request):

	return render(request, 'privileges/FlagPost.html', context)

def CommentEveryWhere_Privillege_Info_Page(request):

	return render(request, 'privileges/CommentEveryWhere.html', context)

def SetBounty_Privilege_Info_Page(request):

	return render(request, 'privileges/SetBounty.html', context)

def VoteDown_Privilege_Info_Page(request):

	return render(request, 'privileges/VoteDown.html', context)

def ViewCloseVote_Privilege_Info_Page(request):

	return render(request, 'privileges/ViewCloseVote.html', context)

def AccessReviewQueue_Privilege_Info_Page(request):

	return render(request, 'privileges/AccessReviewQueue.html', context)

def EstablishedUser_Privilege_Info_Page(request):

	return render(request, 'privileges/EstablishedUser.html', context)

def CreateTags_Privilege_Info_Page(request):

	return render(request, 'privileges/CreateTags.html', context)

def EditQuestionAnswer__Privilege_Info_Page(request):

	return render(request, 'privileges/EditQuestionAnswer.html', context)

def AccessToModTools_Privilege_Info_Page(request):

	return render(request, 'privileges/AccessToModTools.html', context)

def ProtectQ_Privilege_Info_Page(request):

	return render(request, 'privileges/ProtectQ.html', context)

def TrustedUser_Privilege_Info_Page(request):

	return render(request, 'privileges/TrustedUser.html', context)

