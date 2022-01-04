function openInbox() {
    // getting = document.getElementsByTagName("myDiv2");
    gettingOpen = document.getElementsByTagName("myDiv");
    gettingOpen[0].classList.toggle("active");

    gettingAchieveOpen = document.getElementsByTagName("acvhieveDiv");
    if (gettingAchieveOpen[0].classList.contains("active")) {
        // alert("Achievements Inbox Panel is Open");
        gettingAchieveOpen[0].classList.toggle("active");
    }


    gettingAchieveOpen = document.getElementsByTagName("reviewDiv");
    if (gettingAchieveOpen[0].classList.contains("active")) {
        // alert("Achievements Inbox Panel is Open");
        gettingAchieveOpen[0].classList.toggle("active");
    }



    var $this = $('.achieveSVG');
    var forBackground = $('.achieveSVGOuter');

    if ($this.hasClass('fillTheSVG')) {
        $this.removeClass('fillTheSVG');
        forBackground.removeClass('forBackgroundClass');
    }

    var $this = $('.reviewSVG');
    var forBackground = $('.reviewSVGOuter');

    if ($this.hasClass('fillTheSVG')) {
        $this.removeClass('fillTheSVG');
        forBackground.removeClass('forBackgroundClass');
    }

}


function openAchievementInbox() {
    gettingAchieveOpen = document.getElementsByTagName("acvhieveDiv");
    gettingAchieveOpen[0].classList.toggle("active");

    gettingAchieveOpen = document.getElementsByTagName("myDiv");
    if (gettingAchieveOpen[0].classList.contains("active")) {
        // alert("Achievements Inbox Panel is Open");
        gettingAchieveOpen[0].classList.toggle("active");
    }

    gettingAchieveOpen = document.getElementsByTagName("reviewDiv");
    if (gettingAchieveOpen[0].classList.contains("active")) {
        // alert("Achievements Inbox Panel is Open");
        gettingAchieveOpen[0].classList.toggle("active");
    }


    var $this = $('.myInboxSVG');
    var forBackground = $('.myInboxSVGOuter');

    if ($this.hasClass('fillTheSVG')) {
        $this.removeClass('fillTheSVG');
        forBackground.removeClass('forBackgroundClass');
    }

    var $this = $('.reviewSVG');
    var forBackground = $('.reviewSVGOuter');

    if ($this.hasClass('fillTheSVG')) {
        $this.removeClass('fillTheSVG');
        forBackground.removeClass('forBackgroundClass');
    }


}


function openReviewInbox() {
    gettingReviewOpen = document.getElementsByTagName("reviewDiv");
    gettingReviewOpen[0].classList.toggle("active");


    gettingAchieveOpen = document.getElementsByTagName("acvhieveDiv");
    if (gettingAchieveOpen[0].classList.contains("active")) {
        // alert("Achievements Inbox Panel is Open");
        gettingAchieveOpen[0].classList.toggle("active");
    }

    gettingAchieveOpen = document.getElementsByTagName("myDiv");
    if (gettingAchieveOpen[0].classList.contains("active")) {
        // alert("Achievements Inbox Panel is Open");
        gettingAchieveOpen[0].classList.toggle("active");
    }


    var $this = $('.myInboxSVG');
    var forBackground = $('.myInboxSVGOuter');

    if ($this.hasClass('fillTheSVG')) {
        $this.removeClass('fillTheSVG');
        forBackground.removeClass('forBackgroundClass');
    }

    var $this = $('.achieveSVG');
    var forBackground = $('.achieveSVGOuter');

    if ($this.hasClass('fillTheSVG')) {
        $this.removeClass('fillTheSVG');
        forBackground.removeClass('forBackgroundClass');
    }



}


    $('._important, .myInboxSVGOuter').click(function() {
    var $this = $('.myInboxSVG');
    var forBackground = $('.myInboxSVGOuter');

    if ($this.hasClass('fillTheSVG')) {
        $this.removeClass('fillTheSVG');
        forBackground.removeClass('forBackgroundClass');
    } else {
        $this.addClass('fillTheSVG');
        // alert("Third ")
        forBackground.addClass('forBackgroundClass');
    }
});


    $('._positive, .achieveSVGOuter').click(function() {
    var $this = $('.achieveSVG');
    var forBackground = $('.achieveSVGOuter');

    if ($this.hasClass('fillTheSVG')) {
        $this.removeClass('fillTheSVG');
        forBackground.removeClass('forBackgroundClass');
    } else {
        $this.addClass('fillTheSVG');
        // alert("Third ")
        forBackground.addClass('forBackgroundClass');
    }
});


    $('._review, .reviewSVGOuter').click(function() {
    var $this = $('.reviewSVG');
    var forBackground = $('.reviewSVGOuter');

    if ($this.hasClass('fillTheSVG')) {
        $this.removeClass('fillTheSVG');
        forBackground.removeClass('forBackgroundClass');
    } else {
        $this.addClass('fillTheSVG');
        // alert("Third ")
        forBackground.addClass('forBackgroundClass');
    }
});

