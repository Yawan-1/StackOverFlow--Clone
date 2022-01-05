// Question - Upvote - DownVote
       document.addEventListener('DOMContentLoaded', function() {
        window.addEventListener('load', function() {
            // Like
            $('.likeForm').submit(function(e) {
                    e.preventDefault();
                    let thisElement = $(this)
                    $.ajax({
                        url: thisElement.attr('action'),
                        data: {
                            'submit': 'like',
                        },
                        dataType: 'json',
                        method: 'get',
                        async: false,
                        success: function(response) {
                            let likes = $(`#id_likes${thisElement.attr('data-pk')}`).find('.showVoteCount').html()
                            if (response.action == 'undislike_and_like') {
                                likes ++
                                likes ++
                                $(`#id_dislikes${thisElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="like"><i class="fas voteDownInActive fa-sort-down fa-4x"></i><button>`)
                                $(`#id_likes${thisElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="like"><i  class="fas active fa-sort-up fa-4x"></i></button><div class="flex--item d-flex fd-column ai-center color-black fs-title"><div class="showVoteCount">${likes}</div></div>`)

                            } else if (response.action == 'unlike') {
                                likes -= 1
                                $(`#id_likes${thisElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="like"><i  class="fas inactive fa-sort-up fa-4x"></i></button><div class="flex--item d-flex fd-column ai-center color-black fs-title"><div class="showVoteCount">${likes}</div></div>`)

                            } else if (response.action == 'voteError') {
                                $('.toast-container').html(
                                    `<div data-delay="5000" class="s-toast js-toast fade" aria-hidden="false" style="top: 60px;">
    <aside class="s-notice s-notice__info">
        <div class="d-flex gs16 gsx ai-center jc-space-between">
            <div class="flex--item">
                <div class="m0 js-toast-body" id="js-notice-toast-message" role="status" tabindex="0">
                    <strong>Alert ! </strong>Your vote is now locked, and will - unless the Question Edit.
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
                            } else if (response.action == 'lackOfPrivelege') {
                                $('.toast-container').html(
                                    `<div data-delay="5000" class="s-toast js-toast fade" id="closeId" aria-hidden="false" style="top: 60px;">
    <aside class="s-notice s-notice__info">
        <div class="d-flex gs16 gsx ai-center jc-space-between">
            <div class="flex--item">
                <div class="m0 js-toast-body" id="js-notice-toast-message" role="status" tabindex="0">
                    You need atleast 15 Reputation to Up upvote
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
                            } else if (response.action == 'cannotLikeOwnPost') {
                                $('.toast-container').html(
                                    `<div data-delay="5000" class="s-toast js-toast fade" aria-hidden="false" style="top: 60px;">
    <aside class="s-notice s-notice__info">
        <div class="d-flex gs16 gsx ai-center jc-space-between">
            <div class="flex--item">
                <div class="m0 js-toast-body" id="js-notice-toast-message" role="status" tabindex="0">
                    You cannot vote for your Own Post
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
                            } else {
                                likes++
                                $(`#id_likes${thisElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="like"><i  class="fas active fa-sort-up fa-4x"></i></button><div class="flex--item d-flex fd-column ai-center color-black fs-title"><div class="showVoteCount">${likes}</div></div>`)
                            }
                        }
                    })
                })
                // Dislike
            $('.dislikeForm').submit(function(e) {
                e.preventDefault();
                let thisElement = $(this)
                $.ajax({
                    url: thisElement.attr('action'),
                    data: {
                        'submit': 'downVote',
                    },
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        let likes = $(`#id_likes${thisElement.attr('data-pk')}`).find('.showVoteCount').html()
                        if (response.action == 'unlike_and_dislike') {
                            likes -= 2
                            $(`#id_dislikes${thisElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="dislike"><i class="fas voteDownActive fa-sort-down fa-4x"></i></button>`)
                            $(`#id_likes${thisElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="dislike"><i  class="fas inactive fa-sort-up fa-4x"></i></button><div class="flex--item d-flex fd-column ai-center color-black fs-title"><div class="showVoteCount">${likes}</div></div>`)

                        } else if (response.action === 'undislike') {
                            likes ++
                            $(`#id_dislikes${thisElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="dislike"><i class="fas voteDownInActive fa-sort-down fa-4x"></i></button>`)
                            $(`#id_likes${thisElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="like"><i  class="fas inactive fa-sort-up fa-4x"></i></button><div class="flex--item d-flex fd-column ai-center color-black fs-title"><div class="showVoteCount">${likes}</div></div>`)
                        } else if (response.action == 'voteError') {
                            $('.toast-container').html(
                                `<div data-delay="5000" class="s-toast js-toast fade" aria-hidden="false" style="top: 60px;">
    <aside class="s-notice s-notice__info">
        <div class="d-flex gs16 gsx ai-center jc-space-between">
            <div class="flex--item">
                <div class="m0 js-toast-body" id="js-notice-toast-message" role="status" tabindex="0">
                    <strong>Alert ! </strong>Your vote is now locked, and will - unless the Question Edit.
                </div>
            </div>
            <div class="flex--item mr0 js-notice-actions">
                <div class="d-flex">
                    <button class="p8 s-btn d-flex flex__center fc-dark js-dismiss" onclick="clickToClose();" tabindex="0" role="button" aria-label="Dismiss">
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
                        } else if (response.action == 'lackOfPrivelege') {
                            $('.toast-container').html(
                                `<div data-delay="5000" class="s-toast js-toast fade" aria-hidden="false" style="top: 60px;">
    <aside class="s-notice s-notice__info">
        <div class="d-flex gs16 gsx ai-center jc-space-between">
            <div class="flex--item">
                <div class="m0 js-toast-body" id="js-notice-toast-message" role="status" tabindex="0">
                    <strong>Alert ! </strong>You need alteast 125 Reputation to Down Vote
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
                        } else if (response.action == 'cannotLikeOwnPost') {
                                $('.toast-container').html(
                                    `<div data-delay="5000" class="s-toast js-toast fade" aria-hidden="false" style="top: 60px;">
    <aside class="s-notice s-notice__info">
        <div class="d-flex gs16 gsx ai-center jc-space-between">
            <div class="flex--item">
                <div class="m0 js-toast-body" id="js-notice-toast-message" role="status" tabindex="0">
                    <strong>Alert ! </strong>You cannot vote for your own post.
                </div>
            </div>
            <div class="flex--item mr0 js-notice-actions">
                <div class="d-flex">
                    <button class="p8 s-btn d-flex flex__center fc-dark js-dismiss" onclick="clickToClose();" tabindex="0" role="button" aria-label="Dismiss">
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
                        } else {
                            likes -= 1
                            $(`#id_dislikes${thisElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="dislike"><i class="fas voteDownActive fa-sort-down fa-4x"></i></button>`)
                            $(`#id_likes${thisElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="like"><i  class="fas inactive fa-sort-up fa-4x"></i></button><div class="flex--item d-flex fd-column ai-center color-black fs-title"><div class="showVoteCount">${likes}</div></div>`)
                        }
                    }
                })
            })
        })
    })

    


// Answer - Upvote - Downvote
    document.addEventListener('DOMContentLoaded', function() {
        window.addEventListener('load', function() {
            // Like
            $('.ansLikeForm').submit(function(e) {
                    e.preventDefault();
                    let thatElement = $(this)
                    $.ajax({
                        url: thatElement.attr('action'),
                        data: {
                            'submit': 'like',
                        },
                        dataType: 'json',
                        method: 'get',
                        async: false,
                        success: function(response) {
                            // let a_vote_ups = $(`#id_Ans_UpVote${thatElement.attr('data-pk')}`).find('p').html()
                            // let a_vote_downs = $(`#id_Ans_DownVote${thatElement.attr('data-pk')}`).find('p').html()
                            let ansLikes = $(`#id_Ans_UpVote${thatElement.attr('data-pk')}`).find('.showVoteCount-answer').html()
                            // alert(ansLikes)
                            if (response.action == 'unDownVoteAndLike') {
                                ansLikes ++
                                ansLikes ++
                                $(`#id_Ans_DownVote${thatElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="like"><i class="fas voteDownInActive fa-sort-down fa-4x"></i><button>`)
                                $(`#id_Ans_UpVote${thatElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="like"><i  class="fas active fa-sort-up fa-4x"></i></button><div class="flex--item d-flex fd-column ai-center color-black fs-title"><div class="showVoteCount-answer">${ansLikes}</div></div>`)

                            } else if (response.action == 'unlikeAnswer') {
                                ansLikes -= 1
                                $(`#id_Ans_UpVote${thatElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="voteAns"><i class="fas inactive fa-sort-up fa-4x"></i></button><div class="flex--item d-flex fd-column ai-center color-black fs-title"><div class="showVoteCount-answer">${ansLikes}</div></div>`)

                            } else if (response.action == 'lackOfPrivelege') {
                                $('.toast-container').html(
                                    `<div data-delay="5000" class="s-toast js-toast fade" aria-hidden="false" style="top: 60px;">
    <aside class="s-notice s-notice__info">
        <div class="d-flex gs16 gsx ai-center jc-space-between">
            <div class="flex--item">
                <div class="m0 js-toast-body" id="js-notice-toast-message" role="status" tabindex="0">
                    <strong>Alert ! </strong>You need alteast 15 Reputation to Up Vote
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
                            } else if (response.action == 'cannotLikeOwnPost') {
                                $('.toast-container').html(
                                    `<div data-delay="5000" class="s-toast js-toast fade" aria-hidden="false" style="top: 60px;">
    <aside class="s-notice s-notice__info">
        <div class="d-flex gs16 gsx ai-center jc-space-between">
            <div class="flex--item">
                <div class="m0 js-toast-body" id="js-notice-toast-message" role="status" tabindex="0">
                    <strong>Alert ! </strong>You cannot vote for your Own Post
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
                            } else {
                                ansLikes ++
                                $(`#id_Ans_UpVote${thatElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="voteAns"><i  class="fas active fa-sort-up fa-4x"></i></button><div class="flex--item d-flex fd-column ai-center color-black fs-title"><div class="showVoteCount-answer">${ansLikes}</div></div>`)
                            }
                        }
                    })
                })
                // Dislike
            $('.ansDislikeForm').submit(function(e) {
                e.preventDefault();
                let thatElement = $(this)
                $.ajax({
                    url: thatElement.attr('action'),
                    data: {
                        'submit': 'ansDownVote',
                    },
                    dataType: 'json',
                    method: 'get',
                    async: false,
                    success: function(response) {
                        let ansLikes = $(`#id_Ans_UpVote${thatElement.attr('data-pk')}`).find('.showVoteCount-answer').html()
                        // alert(ansLikes)
                        if (response.action == 'unUpvoteAndDownVote') {
                            ansLikes -= 2
                            $(`#id_Ans_DownVote${thatElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="downVoteAns"><i class="fas voteDownActive fa-sort-down fa-4x"></i></button>`)
                            $(`#id_Ans_UpVote${thatElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="downVoteAns"><i  class="fas inactive fa-sort-up fa-4x"></i></button><div class="flex--item d-flex fd-column ai-center color-black fs-title"><div class="showVoteCount-answer">${ansLikes}</div></div>`)

                        } else if (response.action === 'undislike') {
                            ansLikes ++
                            $(`#id_Ans_UpVote${thatElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="voteAns"><i class="fas inactive fa-sort-up fa-4x"></i></button><div class="flex--item d-flex fd-column ai-center color-black fs-title"><div class="showVoteCount-answer">${ansLikes}</div></div>`)
                            $(`#id_Ans_DownVote${thatElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="downVoteAns"><i class="fas voteDownInActive fa-sort-down fa-4x"></i></button>`)

                        } else if (response.action == 'lackOfPrivelege') {
                            $('.toast-container').html(
                                `<div data-delay="5000" class="s-toast js-toast fade" aria-hidden="false" style="top: 60px;">
    <aside class="s-notice s-notice__info">
        <div class="d-flex gs16 gsx ai-center jc-space-between">
            <div class="flex--item">
                <div class="m0 js-toast-body" id="js-notice-toast-message" role="status" tabindex="0">
                    <strong>Alert ! </strong>You need alteast 125 Reputation to Down Vote
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
                        } else if (response.action == 'cannotLikeOwnPost') {
                                $('.toast-container').html(
                                    `<div data-delay="5000" class="s-toast js-toast fade" aria-hidden="false" style="top: 60px;">
    <aside class="s-notice s-notice__info">
        <div class="d-flex gs16 gsx ai-center jc-space-between">
            <div class="flex--item">
                <div class="m0 js-toast-body" id="js-notice-toast-message" role="status" tabindex="0">
                    <strong>Alert ! </strong>You cannot vote for your Own Post
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
                        } else {
                            ansLikes -= 1
                            $(`#id_Ans_UpVote${thatElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="voteAns"><i class="fas inactive fa-sort-up fa-4x"></i></button><div class="flex--item d-flex fd-column ai-center color-black fs-title"><div class="showVoteCount-answer">${ansLikes}</div></div>`)
                            $(`#id_Ans_DownVote${thatElement.attr('data-pk')}`).html(`<button name='submit' type='submit' value="downVoteAns"><i class="fas voteDownActive fa-sort-down fa-4x"></i></button>`)
                        }
                    }
                })
            })
        })
    })
