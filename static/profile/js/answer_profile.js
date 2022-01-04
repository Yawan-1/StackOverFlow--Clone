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
