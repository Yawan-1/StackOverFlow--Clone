    function toogleQuestion(id) {
        let collapseModel = document.getElementById(`collapse-model-question-${id}`);
        let currentActive = document.querySelector('.collapsable-bar-content.active');

    if(currentActive){
      currentActive.classList.remove('active');
    }

    if(currentActive != collapseModel){
      collapseModel.classList.add("active");
    }

}


    function toggleAnswer(id) {
        let collapseModel_Answer = document.getElementById(`collapse-model-answer-${id}`);
        let currentActiveAns = document.querySelector('.collapsable-bar-content-2.active');

    if(currentActiveAns) {
      currentActiveAns.classList.remove('active');
    }

    if(currentActiveAns != collapseModel_Answer) {
      collapseModel_Answer.classList.add("active");
    }

}


    function First_B_Tab() {
    gettingOpen = document.getElementsByClassName("First-B");
    gettingOpen[0].classList.add("active");


    gettingOpen = document.getElementsByClassName("Second-B");
    gettingOpen[0].classList.remove("active");


    gettingOpen = document.getElementsByClassName("Third-B");
    gettingOpen[0].classList.remove("active");




}


function Second_B_Tab() {
    gettingOpen = document.getElementsByClassName("Second-B");
    gettingOpen[0].classList.add("active");


    gettingOpen = document.getElementsByClassName("First-B");
    gettingOpen[0].classList.remove("active");


    gettingOpen = document.getElementsByClassName("Third-B");
    gettingOpen[0].classList.remove("active");




}


function Third_B_Tab() {
    gettingOpen = document.getElementsByClassName("Third-B");
    gettingOpen[0].classList.add("active");


    gettingOpen = document.getElementsByClassName("First-B");
    gettingOpen[0].classList.remove("active");


    gettingOpen = document.getElementsByClassName("Second-B");
    gettingOpen[0].classList.remove("active");




}