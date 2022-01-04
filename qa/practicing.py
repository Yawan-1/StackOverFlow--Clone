
    getCreateClose_object = CloseQuestionVotes.objects.filter(question_to_closing=data).exclude(ended=True).first()



    if request.method == 'POST':
        close_form = CloseForm_Q(data=request.POST)
        if close_form.is_valid():
            new_post = close_form.save(commit=False)
            formData = close_form.cleaned_data['why_closing']
            formData_duplicate_of = close_form.cleaned_data['duplicate_of']

            if formData != "DUPLICATE":
                if getCreateClose_object:
                    if formData == getCreateClose_object.why_closing:
                        # print("Same as Before")
                        print("First Statement is Excecuting")
                        new_post.user = request.user
                        new_post.question_to_closing = data
                        # createInstance,created = ReviewCloseVotes.objects.get_or_create(question_to_closed=data)
                        # createInstance.reviewed_by.add(request.user)
                        # print("Instance Created")
                        new_post.save()
                        # SAVE THE INSTANCE FIRST
                        # https://stackoverflow.com/questions/33838433/save-prohibited-to-prevent-data-loss-due-to-unsaved-related-object
                        # createInstance.review_of = new_post
                        # createInstance.save()
                        getCreateClose_object.how_many_votes_on_Close += 1
                        getCreateClose_object.save()
                        # Maybe i can remove these two lines
                        createInstance.review_of = new_post
                        createInstance.save()
                    else:
                        # print("Save the New Request")
                        print("Second Statement is Excecuting")

                        new_post.user = request.user
                        new_post.question_to_closing = data
                        createInstance,created = ReviewCloseVotes.objects.get_or_create(question_to_closed=data)
                        # createInstance.reviewed_by.add(request.user)
                        # createInstance.reviewed_by.add(request.user)
                        # createInstance.save()
                        getCreateClose_object.how_many_votes_on_Close += 1
                        getCreateClose_object.save()
                        # print("Instance Created")

                        new_post.save()
                        # SAVE THE INSTANCE FIRST
                        # https://stackoverflow.com/questions/33838433/save-prohibited-to-prevent-data-loss-due-to-unsaved-related-object
                        # createInstance.review_of = new_post
                        # createInstance.save()
                        
                        # Maybe i can remove these two lines
                        createInstance.review_of = new_post
                        createInstance.save()
                else:

                    new_post.user = request.user
                    new_post.question_to_closing = data
                    createInstance,created = ReviewCloseVotes.objects.get_or_create(question_to_closed=data)
                    createInstance.reviewed_by.add(request.user)
                    # createInstance.reviewed_by.add(request.user)
                    # createInstance.save()
                    new_post.how_many_votes_on_Close += 1
                    print("Third Statement is Excecuting")
                    new_post.save()
                    # SAVE THE INSTANCE FIRST
                    # https://stackoverflow.com/questions/33838433/save-prohibited-to-prevent-data-loss-due-to-unsaved-related-object
                    # createInstance.review_of = new_post
                    # createInstance.save()
                    createInstance.review_of = new_post
                    createInstance.save()

            elif formData == "DUPLICATE" and formData_duplicate_of == None:
                messages.error(request, "Please Write the Another Question's URL")
                print("Please Write the Another Question's URL")

            else:
                if getCreateClose_object:
                    if formData == getCreateClose_object.why_closing:
                        print("Fourth Statement is Excecuting")

                        new_post.user = request.user
                        new_post.question_to_closing = data
                        createInstance,created = ReviewCloseVotes.objects.get_or_create(question_to_closed=data)
                        createInstance.reviewed_by.add(request.user)
                        # print("Instance Created")
                        new_post.save()
                        # SAVE THE INSTANCE FIRST
                        # https://stackoverflow.com/questions/33838433/save-prohibited-to-prevent-data-loss-due-to-unsaved-related-object

                        getCreateClose_object.how_many_votes_on_Close += 1
                        getCreateClose_object.save()
                        createInstance.review_of = new_post
                        createInstance.save()
                    else:
                        print("Fifth Statement is Excecuting")

                        new_post.user = request.user
                        new_post.question_to_closing = data
                        createInstance,created = ReviewCloseVotes.objects.get_or_create(question_to_closed=data)
                        createInstance.reviewed_by.add(request.user)
                        # createInstance.reviewed_by.add(request.user)
                        # createInstance.save()
                        getCreateClose_object.how_many_votes_on_Close += 1
                        getCreateClose_object.save()
                        # print("Instance Created")
                        createInstance.review_of = new_post
                        new_post.save()
                        # SAVE THE INSTANCE FIRST
                        # https://stackoverflow.com/questions/33838433/save-prohibited-to-prevent-data-loss-due-to-unsaved-related-object
                        createInstance.review_of = new_post
                        createInstance.save()

                else:
                    print("Sixth Statement is Excecuting")
                    new_post.user = request.user
                    new_post.question_to_closing = data
                    createInstance,created = ReviewCloseVotes.objects.get_or_create(question_to_closed=data)
                    createInstance.reviewed_by.add(request.user)
                    # createInstance.reviewed_by.add(request.user)
                    # createInstance.save()
                    new_post.how_many_votes_on_Close += 1
                    # print("Instance Created")
                    new_post.save()
                    # SAVE THE INSTANCE FIRST
                    # https://stackoverflow.com/questions/33838433/save-prohibited-to-prevent-data-loss-due-to-unsaved-related-object
                    createInstance.review_of = new_post
                    createInstance.save()
            return redirect('qa:questionDetailView', pk=data.id,)  # slug=slug)

    else:
        close_form = CloseForm_Q()
