function rateStar(starCount) {
    var stars = document.getElementsByClassName("fa-star");
    for (var i = 0; i < stars.length; i++) {
        if (i < starCount) {
            stars[i].classList.add("checked");
        } else {
            stars[i].classList.remove("checked");
        }
    }
    document.getElementById("rating").value = starCount;
}

document.getElementById("ratingForm").onsubmit = function (event) {
    var rating = document.getElementById("rating").value;
    if (rating == 0) {
        document.getElementById("ratingError").style.display = "block";
        event.preventDefault();
    } else {
        document.getElementById("ratingError").style.display = "none";
    }
};

