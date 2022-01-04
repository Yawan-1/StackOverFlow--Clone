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


function FirstTab_Q() {
    gettingOpen = document.getElementsByClassName("First-Q")
    gettingOpen[0].classList.add("active");

    gettingOpen = document.getElementsByClassName("Second-Q");
    gettingOpen[0].classList.remove("active");


    gettingOpen = document.getElementsByClassName("Third-Q");
    gettingOpen[0].classList.remove("active");

    gettingOpen = document.getElementsByClassName("Fourth-Q");
    gettingOpen[0].classList.remove("active");


}

function SecondTab_Q() {

    gettingOpen = document.getElementsByClassName("Second-Q");
    gettingOpen[0].classList.add("active");

    gettingOpen = document.getElementsByClassName("First-Q");
    gettingOpen[0].classList.remove("active");

    gettingOpen = document.getElementsByClassName("Third-Q");
    gettingOpen[0].classList.remove("active");

    gettingOpen = document.getElementsByClassName("Fourth-Q");
    gettingOpen[0].classList.remove("active");

}

function ThirdTab_Q() {

    gettingOpen = document.getElementsByClassName("Third-Q");
    gettingOpen[0].classList.add("active");

    gettingOpen = document.getElementsByClassName("First-Q");
    gettingOpen[0].classList.remove("active");

    gettingOpen = document.getElementsByClassName("Second-Q");
    gettingOpen[0].classList.remove("active");

    gettingOpen = document.getElementsByClassName("Fourth-Q");
    gettingOpen[0].classList.remove("active");


}

function FourthTab_Q() {

    gettingOpen = document.getElementsByClassName("Fourth-Q");
    gettingOpen[0].classList.add("active");

    gettingOpen = document.getElementsByClassName("First-Q");
    gettingOpen[0].classList.remove("active");

    gettingOpen = document.getElementsByClassName("Second-Q");
    gettingOpen[0].classList.remove("active");

    gettingOpen = document.getElementsByClassName("Third-Q");
    gettingOpen[0].classList.remove("active");


}


function FirstTab() {
    // getting = document.getElementsByTagName("myDiv2");
    gettingOpen = document.getElementsByClassName("First");
    gettingOpen[0].classList.add("active");

    gettingOpen = document.getElementsByClassName("Second");
    gettingOpen[0].classList.remove("active");


    gettingOpen = document.getElementsByClassName("Third");
    gettingOpen[0].classList.remove("active");

}

function SecondTab() {

    gettingOpen = document.getElementsByClassName("Second");
    gettingOpen[0].classList.add("active");

    gettingOpen = document.getElementsByClassName("First");
    gettingOpen[0].classList.remove("active");

    gettingOpen = document.getElementsByClassName("Third");
    gettingOpen[0].classList.remove("active");

}

function ThirdTab() {
    gettingOpen = document.getElementsByClassName("Third");
    gettingOpen[0].classList.add("active");


    gettingOpen = document.getElementsByClassName("First");
    gettingOpen[0].classList.remove("active");


    gettingOpen = document.getElementsByClassName("Second");
    gettingOpen[0].classList.remove("active");

}








function First_B_Tab() {
    gettingOpen = document.getElementsByClassName("first-B");
    gettingOpen[0].classList.add("active");


    gettingOpen = document.getElementsByClassName("second-B");
    gettingOpen[0].classList.remove("active");


    gettingOpen = document.getElementsByClassName("third-B");
    gettingOpen[0].classList.remove("active");


    gettingOpen = document.getElementsByClassName("fourth-B");
    gettingOpen[0].classList.remove("active");


    gettingOpen = document.getElementsByClassName("fifth-B");
    gettingOpen[0].classList.remove("active");

}


function Second_B_Tab() {
    gettingOpen = document.getElementsByClassName("second-B");
    gettingOpen[0].classList.add("active");


    gettingOpen = document.getElementsByClassName("first-B");
    gettingOpen[0].classList.remove("active");


    gettingOpen = document.getElementsByClassName("third-B");
    gettingOpen[0].classList.remove("active");


    gettingOpen = document.getElementsByClassName("fourth-B");
    gettingOpen[0].classList.remove("active");


    gettingOpen = document.getElementsByClassName("fifth-B");
    gettingOpen[0].classList.remove("active");

}


function Third_B_Tab() {
    gettingOpen = document.getElementsByClassName("third-B");
    gettingOpen[0].classList.add("active");


    gettingOpen = document.getElementsByClassName("first-B");
    gettingOpen[0].classList.remove("active");


    gettingOpen = document.getElementsByClassName("second-B");
    gettingOpen[0].classList.remove("active");


    gettingOpen = document.getElementsByClassName("fourth-B");
    gettingOpen[0].classList.remove("active");


    gettingOpen = document.getElementsByClassName("fifth-B");
    gettingOpen[0].classList.remove("active");

}


function Fourth_B_Tab() {
    gettingOpen = document.getElementsByClassName("fourth-B");
    gettingOpen[0].classList.add("active");


    gettingOpen = document.getElementsByClassName("first-B");
    gettingOpen[0].classList.remove("active");


    gettingOpen = document.getElementsByClassName("second-B");
    gettingOpen[0].classList.remove("active");


    gettingOpen = document.getElementsByClassName("third-B");
    gettingOpen[0].classList.remove("active");


    gettingOpen = document.getElementsByClassName("fifth-B");
    gettingOpen[0].classList.remove("active");
 
}


function Fifth_B_Tab() {
    gettingOpen = document.getElementsByClassName("fifth-B");
    gettingOpen[0].classList.add("active");


    gettingOpen = document.getElementsByClassName("first-B");
    gettingOpen[0].classList.remove("active");


    gettingOpen = document.getElementsByClassName("second-B");
    gettingOpen[0].classList.remove("active");


    gettingOpen = document.getElementsByClassName("third-B");
    gettingOpen[0].classList.remove("active");


    gettingOpen = document.getElementsByClassName("fourth-B");
    gettingOpen[0].classList.remove("active");
 
}