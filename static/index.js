var date_choice = document.getElementById("date_choice");

window.onload = function() {
    date_choice.style.display = "none";
}

function show_date_choice(){
    date_choice.style.display = "block";
}

function close_date_choice(){
    date_choice.style.display = "none";
}
