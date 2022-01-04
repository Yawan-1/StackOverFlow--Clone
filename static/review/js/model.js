var modal = document.getElementById("myModal");
var btn = document.getElementById("id_reviewActions_3");
var span = document.getElementsByClassName("close")[0]; 
btn.onclick = function sd() {
  modal.style.display = "block";
}

span.onclick = function closeIt() {
  modal.style.display = "none";
}

window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}

