function hideClass(className) {
    var x = document.getElementsByClassName(className);
    var i;
    for (i = 0; i < x.length; ++i) {
        x[i].style.display = "none";
    }
}

function mentionClicked(mention_id) {
    hideClass("div-candidates");
    //hideClass("div-main-label");
    document.getElementById('m' + mention_id).style.display='block';
//    document.getElementById('div-main-label-' + mention_id).style.display='block';
}