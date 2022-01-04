    $(document).ready(function () {
        $("#edit-answer-ajax-form").submit(function (e) {
            // preventing from page reload and default actions
            e.preventDefault();
            // serialize the data for sending the form data.
            thisElement = $(this);
            var serializedData = $(this).serialize();
            // make POST ajax call
            $.ajax({
                type: 'POST',
                url: thisElement.attr('action'),
                data: serializedData,
                success: function (response) {
                    // display the newly friend to table.
                    var instance = JSON.parse(response["instance"]);
                    var fields = instance[0]["fields"];
                    $("#my_friends tbody").html(
                        `<h2>SuccessFully Saved</h2>
                        `
                    )
                },
                error: function (response) {
                    // alert the error if any error occured
                    alert(response["responseJSON"]["error"]);
                }
            })
        })

    })

var modal = document.getElementById("myModal");

var btn = document.getElementById("id_actions_2");

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