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

function showSearchResult(mention_id, reviewed_biz_city, csrf_token) {
    postdata = {
        csrfmiddlewaretoken: csrf_token,
        mention_id: mention_id,
        reviewed_biz_city: reviewed_biz_city,
        search_text: document.getElementById('input-' + mention_id).value
    };

    divid = "#search-results-" + mention_id;
    $(divid).empty().load('/yelp/search/', postdata);
}

function checkRadio(mention_id, btn_id) {
    link_radio_id = 'radio-link-' + mention_id;
    document.getElementById(link_radio_id).checked = true;
    document.getElementById(btn_id).checked = true;
}

$(document).ready(function(){
    $('#form-main').on('keyup keypress', function(e) {
        var keyCode = e.keyCode || e.which;
        if (keyCode === 13) {
        e.preventDefault();
        return false;
        }
    });
    $('.input-search-biz').on('keyup', function(e) {
        var keyCode = e.keyCode || e.which;
        if (keyCode === 13) {
            var btnid = "#btn-search-" + $(this).attr('id').substring(6);
            $(btnid).trigger('click');
            return false;
        }
    });
});
