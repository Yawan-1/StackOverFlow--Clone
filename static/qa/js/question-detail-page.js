    document.addEventListener('DOMContentLoaded', function() {
        window.addEventListener('load', function() {
            $('.AcceptForm').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {
                        'submit': 'mark',
                    },
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'unaccept') {
                            $(`#id_accept${thisElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="accept"><i class="wrong far fa-check fa-3x"></i></button><br><img class="unaccept-loading-image" src="{% static 'preloader.gif' %}"></img>`)
                            $('.unaccept-loading-image').show();
                            $('.unaccept-loading-image').fadeOut(1000);
                        }
                        else if (response.action == 'bountyError') {
                            $('.toast-container').html(
                                `<div data-delay="5000" class="s-toast js-toast fade" aria-hidden="false" style="top: 60px;">
    <aside class="s-notice s-notice__info">
        <div class="d-flex gs16 gsx ai-center jc-space-between">
            <div class="flex--item">
                <div class="m0 js-toast-body" id="js-notice-toast-message" role="status" tabindex="0">
                    <strong>Alert ! </strong>You already accepted an Answer
                </div>
            </div>
            <div class="flex--item mr0 js-notice-actions">
                <div class="d-flex">
                    <button class="p8 s-btn d-flex flex__center fc-dark js-dismiss" tabindex="0" role="button" aria-label="Dismiss">
                        <svg class="m0 svg-icon iconClearSm" width="14" height="14" viewBox="0 0 14 14">
                            <path d="M12 3.41 10.59 2 7 5.59 3.41 2 2 3.41 5.59 7 2 10.59 3.41 12 7 8.41 10.59 12 12 10.59 8.41 7 12 3.41Z"></path>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </aside>
</div>`
                            );
                            $(".toast").toast('show', {
                                autohide: true,
                            });
                            $('.js-toast').fadeOut(8000);
                        } else if (response.action == "acceptIn_10_Minutes") {
                            $('.toast-container').html(
                                `<div data-delay="5000" class="s-toast js-toast fade" aria-hidden="false" style="top: 60px;">
    <aside class="s-notice s-notice__info">
        <div class="d-flex gs16 gsx ai-center jc-space-between">
            <div class="flex--item">
                <div class="m0 js-toast-body" id="js-notice-toast-message" role="status" tabindex="0">
                    <strong>Alert ! </strong>Accept after 10 Minutes of Posting Answer
                </div>
            </div>
            <div class="flex--item mr0 js-notice-actions">
                <div class="d-flex">
                    <button class="p8 s-btn d-flex flex__center fc-dark js-dismiss" tabindex="0" role="button" aria-label="Dismiss">
                        <svg class="m0 svg-icon iconClearSm" width="14" height="14" viewBox="0 0 14 14">
                            <path d="M12 3.41 10.59 2 7 5.59 3.41 2 2 3.41 5.59 7 2 10.59 3.41 12 7 8.41 10.59 12 12 10.59 8.41 7 12 3.41Z"></path>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </aside>
</div>`
                            );
                            $(".toast").toast('show', {
                                autohide: true,
                            });
                            $('.js-toast').fadeOut(8000);
                        } else if (response.action == "acceptIn_10Days") {
                            $('.toast-container').html(
                                `<div data-delay="5000" class="s-toast js-toast fade" aria-hidden="false" style="top: 60px;">
    <aside class="s-notice s-notice__info">
        <div class="d-flex gs16 gsx ai-center jc-space-between">
            <div class="flex--item">
                <div class="m0 js-toast-body" id="js-notice-toast-message" role="status" tabindex="0">
                    <strong>Alert ! </strong>You can Accept your Answer in 2 Days
                </div>
            </div>
            <div class="flex--item mr0 js-notice-actions">
                <div class="d-flex">
                    <button class="p8 s-btn d-flex flex__center fc-dark js-dismiss" tabindex="0" role="button" aria-label="Dismiss">
                        <svg class="m0 svg-icon iconClearSm" width="14" height="14" viewBox="0 0 14 14">
                            <path d="M12 3.41 10.59 2 7 5.59 3.41 2 2 3.41 5.59 7 2 10.59 3.41 12 7 8.41 10.59 12 12 10.59 8.41 7 12 3.41Z"></path>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </aside>
</div>`
                            );
                            $(".toast").toast('show', {
                                autohide: true,
                            });
                            $('.js-toast').fadeOut(8000);
                        } else { // Accept Only
                            $(`#id_accept${thisElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="accept"><i  class="correct far fa-check fa-3x"></i></button><br><img class="accept-loading-image" src="{% static 'preloader.gif' %}"></img>`)
                            $('.toast-container').html(
                                `<div data-delay="5000" class="s-toast js-toast fade" aria-hidden="false" style="top: 60px;">
    <aside class="s-notice s-notice__info">
        <div class="d-flex gs16 gsx ai-center jc-space-between">
            <div class="flex--item">
                <div class="m0 js-toast-body" id="js-notice-toast-message" role="status" tabindex="0">
                    Dont' forget to Upvote the Post that Helped You
                </div>
            </div>
            <div class="flex--item mr0 js-notice-actions">
                <div class="d-flex">
                    <button class="p8 s-btn d-flex flex__center fc-dark js-dismiss" tabindex="0" role="button" aria-label="Dismiss">
                        <svg class="m0 svg-icon iconClearSm" width="14" height="14" viewBox="0 0 14 14">
                            <path d="M12 3.41 10.59 2 7 5.59 3.41 2 2 3.41 5.59 7 2 10.59 3.41 12 7 8.41 10.59 12 12 10.59 8.41 7 12 3.41Z"></path>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </aside>
</div>`
                            );
                            $('.accept-loading-image').show();
                            $('.accept-loading-image').fadeOut(1000);
                            $(".toast").toast('show', {
                                autohide: true,
                            });
                            $('.js-toast').fadeOut(8000);
                        }
                    }
                })
            })
        })
    })

document.addEventListener('DOMContentLoaded', function() {
        window.addEventListener('load', function() {
            $('.AwardForm').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {
                        'submit': 'award',
                    },
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'awardBountyToIt') { // Accept Only
                            $(`#id_award${thisElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="Award"><i  class="awarded fad fa-award fa-3x"></i></button><br><img class="accept-loading-image" src="{% static 'preloader.gif' %}"></img>`)
                            $('.toast-container').html(
                                `<div data-delay="5000" class="s-toast js-toast fade" aria-hidden="false" style="top: 60px;">
    <aside class="s-notice s-notice__info">
        <div class="d-flex gs16 gsx ai-center jc-space-between">
            <div class="flex--item">
                <div class="m0 js-toast-body" id="js-notice-toast-message" role="status" tabindex="0">
                    Dont' forget to Upvote the Post that Helped You
                </div>
            </div>
            <div class="flex--item mr0 js-notice-actions">
                <div class="d-flex">
                    <button class="p8 s-btn d-flex flex__center fc-dark js-dismiss" tabindex="0" role="button" aria-label="Dismiss">
                        <svg class="m0 svg-icon iconClearSm" width="14" height="14" viewBox="0 0 14 14">
                            <path d="M12 3.41 10.59 2 7 5.59 3.41 2 2 3.41 5.59 7 2 10.59 3.41 12 7 8.41 10.59 12 12 10.59 8.41 7 12 3.41Z"></path>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </aside>
</div>`
                            );
                            $('.accept-loading-image').show();
                            $('.accept-loading-image').fadeOut(1000);
                            $(".toast").toast('show', {
                                autohide: true,
                            });
                            $('.js-toast').fadeOut(8000);
                        } else if (response.action == 'bountyError') {
                            $('.toast-container').html(
                                `<div data-delay="5000" class="s-toast js-toast fade" aria-hidden="false" style="top: 60px;">
    <aside class="s-notice s-notice__info">
        <div class="d-flex gs16 gsx ai-center jc-space-between">
            <div class="flex--item">
                <div class="m0 js-toast-body" id="js-notice-toast-message" role="status" tabindex="0">
                    <strong>Alert ! </strong>You already awarded Bounty on other Answer, You can award Bounty only on one Answer
                </div>
            </div>
            <div class="flex--item mr0 js-notice-actions">
                <div class="d-flex">
                    <button class="p8 s-btn d-flex flex__center fc-dark js-dismiss" tabindex="0" role="button" aria-label="Dismiss">
                        <svg class="m0 svg-icon iconClearSm" width="14" height="14" viewBox="0 0 14 14">
                            <path d="M12 3.41 10.59 2 7 5.59 3.41 2 2 3.41 5.59 7 2 10.59 3.41 12 7 8.41 10.59 12 12 10.59 8.41 7 12 3.41Z"></path>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </aside>
</div>`
                            );
                            $(".toast").toast('show', {
                                autohide: true,
                            });
                            $('.js-toast').fadeOut(8000);
                        } else if (response.action == 'bountyUnacceptError') {
                            $('.toast-container').html(
                                `<div data-delay="5000" class="s-toast js-toast fade" aria-hidden="false" style="top: 60px;">
    <aside class="s-notice s-notice__info">
        <div class="d-flex gs16 gsx ai-center jc-space-between">
            <div class="flex--item">
                <div class="m0 js-toast-body" id="js-notice-toast-message" role="status" tabindex="0">
                    <strong>Alert ! </strong>You cannot revert Bounty, Once it's accepted
                </div>
            </div>
            <div class="flex--item mr0 js-notice-actions">
                <div class="d-flex">
                    <button class="p8 s-btn d-flex flex__center fc-dark js-dismiss" tabindex="0" role="button" aria-label="Dismiss">
                        <svg class="m0 svg-icon iconClearSm" width="14" height="14" viewBox="0 0 14 14">
                            <path d="M12 3.41 10.59 2 7 5.59 3.41 2 2 3.41 5.59 7 2 10.59 3.41 12 7 8.41 10.59 12 12 10.59 8.41 7 12 3.41Z"></path>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </aside>
</div>`
                            );
                            $(".toast").toast('show', {
                                autohide: true,
                            });
                            $('.js-toast').fadeOut(8000);
                        }
                    }
                })
            })
        })
    })

document.addEventListener('DOMContentLoaded', function() {
        window.addEventListener('load', function() {
            $('.BountyForm').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {
                        'submit': 'award',
                    },
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'awardBountyToIt') { // Accept Only
                            $(`#id_award${thisElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="Award"><i  class="correct far fa-check fa-3x"></i></button><br><img class="accept-loading-image" src="{% static 'preloader.gif' %}"></img>`)
                            $('.toast-container').html(
                                `<div data-delay="5000" class="s-toast js-toast fade" aria-hidden="false" style="top: 60px;">
    <aside class="s-notice s-notice__info">
        <div class="d-flex gs16 gsx ai-center jc-space-between">
            <div class="flex--item">
                <div class="m0 js-toast-body" id="js-notice-toast-message" role="status" tabindex="0">
                    Bounty Successfully Applied
                </div>
            </div>
            <div class="flex--item mr0 js-notice-actions">
                <div class="d-flex">
                    <button class="p8 s-btn d-flex flex__center fc-dark js-dismiss" tabindex="0" role="button" aria-label="Dismiss">
                        <svg class="m0 svg-icon iconClearSm" width="14" height="14" viewBox="0 0 14 14">
                            <path d="M12 3.41 10.59 2 7 5.59 3.41 2 2 3.41 5.59 7 2 10.59 3.41 12 7 8.41 10.59 12 12 10.59 8.41 7 12 3.41Z"></path>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </aside>
</div>`
                            );
                            $('.accept-loading-image').show();
                            $('.accept-loading-image').fadeOut(1000);
                            $(".toast").toast('show', {
                                autohide: true,
                            });
                            $('.js-toast').fadeOut(8000);
                        }
                    }
                })
            })
        })
    })

document.addEventListener("DOMContentLoaded", function () {
    window.addEventListener("load", function () {
        $(".bookmarkQuestionForm").submit(function (t) {
            t.preventDefault();
            let a = $(this);
            $.ajax({
                url: a.attr("action"),
                data: { submit: "bookmarking" },
                dataType: "json",
                method: "get",
                async: !1,
                success: function (t) {
                    "bookmarked" == t.action
                        ? $(`#id_bookMark${a.attr("data-pk")}`).html("<button name='submit' type='submit' value=\"accept\"><i class=\"far fa-bookmark fa-1x\"></i></button>")
                        : $(`#id_bookMark${a.attr("data-pk")}`).html("<button name='submit' type='submit' value=\"accept\"><i  class=\"fas fa-bookmark fa-1x\"></i></button>");
                },
            });
        });
    });
});

    document.addEventListener('DOMContentLoaded', function() {
        window.addEventListener('load', function() {
            $('.unpro').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {
                        'submit': 'award',
                    },
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'lackOfPrivelege') { // Accept Only
                            $(`#unpro${thisElement.attr('data-pk')}`).html(`<br><img class="accept-loading-image" src="{% static 'preloader.gif' %}"></img>`)
                            $('.toast-container').html(
                                `<div data-delay="5000" class="s-toast js-toast fade" aria-hidden="false" style="top: 60px;">
    <aside class="s-notice s-notice__info">
        <div class="d-flex gs16 gsx ai-center jc-space-between">
            <div class="flex--item">
                <div class="m0 js-toast-body" id="js-notice-toast-message" role="status" tabindex="0">
                    <strong>Danger! </strong>Protection has successfully removed.
                </div>
            </div>
            <div class="flex--item mr0 js-notice-actions">
                <div class="d-flex">
                    <button class="p8 s-btn d-flex flex__center fc-dark js-dismiss" tabindex="0" role="button" aria-label="Dismiss">
                        <svg class="m0 svg-icon iconClearSm" width="14" height="14" viewBox="0 0 14 14">
                            <path d="M12 3.41 10.59 2 7 5.59 3.41 2 2 3.41 5.59 7 2 10.59 3.41 12 7 8.41 10.59 12 12 10.59 8.41 7 12 3.41Z"></path>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </aside>
</div>`
                            );
                            $('.accept-loading-image').show();
                            $('.accept-loading-image').fadeOut(1000);
                            $('.container-protect').fadeOut(100);
                            $(".toast").toast('show', {
                                autohide: true,
                            });
                            $('.js-toast').fadeOut(8000);
                        }
                    }
                })
            })
        })
    })

    document.addEventListener('DOMContentLoaded', function() {
        window.addEventListener('load', function() {
            $('.bookForm').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {
                        'submit': 'bookIt',
                    },
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        if (response.action == 'removeBookmark') {
                            $(`#id_bookMark${thisElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="accept"><i class="far fa-bookmark fa-1x"></i></button>`)
                        } else { // Accept Only
                            $(`#id_bookMark${thisElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="accept"><i  class="fas fa-bookmark fa-1x"></i></button>`)
                        }
                    }
                })
            })
        })
    })

    document.addEventListener('DOMContentLoaded', function() {
        window.addEventListener('load', function() {
            $('.commentAnswerVoteForm').submit(function(e) {
                e.preventDefault();
                let thisElementUpvoteComment = $(this);
                $.ajax({
                    url: thisElementUpvoteComment.attr('action'),
                    data: {
                        'submit': 'upVoteCommentIt',
                    },
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        let likes = $(`#id_AnswerCommentVote${thisElementUpvoteComment.attr('data-pk')}`).find('div').html()
                        if (response.action == 'unVoteUp') {
                            likes --
                            $(`#id_AnswerCommentVote${thisElementUpvoteComment.attr('data-pk')}`).html(`<div class="move-to-left">${likes}</div><button name='submit' type='submit' value="accept"><i class="fas upvote-comment-inactive fa-sort-up fa-2x"></i></button>`)
                        } else if (response.action == 'voteUp') {
                            likes ++
                            $(`#id_AnswerCommentVote${thisElementUpvoteComment.attr('data-pk')}`).html(`<div class="move-to-left">${likes}</div><button name='submit' type='submit' value="accept"><i class="fas upvote-comment-active fa-sort-up fa-2x"></i></button>`)
                        }
                    }
                })
            })
        })
    })


    document.addEventListener('DOMContentLoaded', function() {
        window.addEventListener('load', function() {
            $('.commentVoteForm').submit(function(e) {
                e.preventDefault();
                let thisElementUpvoteComment = $(this);
                $.ajax({
                    url: thisElementUpvoteComment.attr('action'),
                    data: {
                        'submit': 'upVoteCommentIt',
                    },
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        let likes = $(`#id_commentVote${thisElementUpvoteComment.attr('data-pk')}`).find('div').html()
                        if (response.action == 'unVoteUp') {
                            likes --
                            $(`#id_commentVote${thisElementUpvoteComment.attr('data-pk')}`).html(`<div class="move-to-left">${likes}</div><button name='submit' type='submit' value="accept"><i class="fas upvote-comment-inactive fa-sort-up fa-2x"></i></button>`)
                        } else if (response.action == 'voteUp') {
                            likes ++
                            $(`#id_commentVote${thisElementUpvoteComment.attr('data-pk')}`).html(`<div class="move-to-left">${likes}</div><button name='submit' type='submit' value="accept"><i class="fas upvote-comment-active fa-sort-up fa-2x"></i></button>`)
                        }
                    }
                })
            })
        })
    })

    var span = document.getElementsByClassName("close")[0];
    var disableStartBountyBtn = document.getElementById('myBtn');
    $(document).ready(function () {
        /*
            On submiting the form, send the POST ajax
            request to server and after successfull submission
            display the object.
        */
        $("#bounty-form").submit(function (e) {
            // preventing from page reload and default actions
            e.preventDefault();
            var bountyURL = $(this);
            // serialize the data for sending the form data.
            var serializedData = $(this).serialize();
            // make POST ajax call
            $.ajax({
                type: 'POST',
                url: bountyURL.attr('action'),
                data: serializedData,
                success: function (response) {
                if (response.action == "saved") {
                modal.style.display = "none";
                // alert("Bounty is Applied Successfully")
                $("#myBtn").prop( "hidden", true );

                } else if (response.action == "lackOfPrivelege") {
                    alert("Cannot Create");
                }

                },
                error: function (response) {
                    // alert the error if any error occured
                    alert(response["responseJSON"]["error"]);
                }
            })
        })
    })


    $(document).ready(function () {
        $("#inlne-tag-edit").submit(function (e) {
            // preventing from page reload and default actions
            e.preventDefault();
            var thisElementURL = $(this);
            // serialize the data for sending the form data.
            var serializedData = $(this).serialize();
            // make POST ajax call
            $.ajax({
                type: 'POST',
                url: thisElementURL.attr('action'),
                data: serializedData,
                success: function (response) {
                    if (response.instance == "saved") {
                        $(`.successMessage-inline-tag-edit`).html("<div class='success-message'>Tag is Successfully Edited</div>")

                    } else if (response.action == "lackOfPrivelege") {
                        alert("You need atleast 10000 Reputation");
                    }
                },
                error: function (response) {
                    // alert the error if any error occured
                    alert(response["responseJSON"]["error"]);
                }
            })
        })
    })

$(document).ready(function () {
    $("#flag-form-ajax").submit(function (e) {
        e.preventDefault();
        var thisUrl = $(this);
        var a = $(this).serialize();
        $.ajax({
            type: "POST",
            url: thisUrl.attr('action'),
            data: a,
            success: function (e) {
                "saved" == e.action ? ((modelFlagQuestion.style.display = "none"), $("#questionFlagButton").prop("hidden", !0)) : "lackOfPrivelege" == e.action && alert("Lack of Privilege");
            },
            error: function (e) {
                alert(e.responseJSON.error);
            },
        });
    });
});