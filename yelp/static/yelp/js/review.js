var cur_mention_idx = 0;

function hideClass(className) {
    var x = document.getElementsByClassName(className);
    var i;
    for (i = 0; i < x.length; ++i) {
        x[i].style.display = "none";
    }
}

function mentionClicked(mention_idx, mention_id) {
    cur_mention_idx = mention_idx;
    $('.div-candidates').css({"display": "none"});
    //hideClass("div-main-label");
    $('.span-mention').css({"background-color": "powderblue"});
    $('.span-mention-labeled').css({"background-color": "lightgreen"});
    span_id = "#mention-span-" + cur_mention_idx.toString();
    $(span_id).css({"background-color": "#FFFF55"});
    document.getElementById('span-mention-' + mention_id).style.display='block';
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

function prevMention() {
    --cur_mention_idx;
    span_id = "#mention-span-" + cur_mention_idx.toString();
    if ($(span_id).length) {
        $(span_id).trigger('click');
    } else {
        ++cur_mention_idx;
    }
}

function nextMention() {
    ++cur_mention_idx;
    span_id = "#mention-span-" + cur_mention_idx.toString();
    if ($(span_id).length) {
        $(span_id).trigger('click');
    } else {
        --cur_mention_idx;
    }
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

    $(document).keyup(function(e) {
        var keyCode = e.keyCode || e.which;

        if (keyCode === 37) {
            prevMention();
        }
        if (keyCode === 39) {
            nextMention();
        }
    });
});
