var cur_mention_idx = 0;

function hideClass(className) {
    var x = document.getElementsByClassName(className);
    var i;
    for (i = 0; i < x.length; ++i) {
        x[i].style.display = "none";
    }
}

function mentionClicked(mention_idx, mention_id) {
//    alert(cur_mention_idx);
    cur_mention_idx = mention_idx;
    if (cur_mention_idx + 1 == $('.span-mention').length) {
        $('#btn-submit').css({'background-color': '#337ab7', 'color': '#fff'});
    }

    $('.div-candidates').css({"display": "none"});
    //hideClass("div-main-label");
    $('.span-mention').css({"background-color": "powderblue"});
    $('.span-mention-labeled').css({"background-color": "lightgreen"});
    span_id = "#mention-span-" + cur_mention_idx.toString();
//    alert(span_id);
    $(span_id).css({"background-color": "#FFFF55"});
    $('#div-mention-' + (cur_mention_idx + 1)).css({"display": "block"});
//    document.getElementById('div-mention-' + mention_idx).style.display='block';
}

function showSearchResult(mention_id, reviewed_biz_city, search_url, csrf_token) {
    postdata = {
        csrfmiddlewaretoken: csrf_token,
        mention_id: mention_id,
//        reviewed_biz_city: reviewed_biz_city,
        query_name: document.getElementById('input-query-name-' + mention_id).value,
        query_city: document.getElementById('input-query-city-' + mention_id).value,
        query_addr: document.getElementById('input-query-addr-' + mention_id).value
    };

    divid = "#search-results-" + mention_id;
    $(divid).empty().load(search_url, postdata);
}

function checkRadio(mention_id, btn_id) {
    link_radio_id = 'radio-link-' + mention_id;
    document.getElementById(link_radio_id).checked = true;
    document.getElementById(btn_id).checked = true;
//    $('#div-link-' + mention_id).css({"opacity": "1"});
}

function linkChecked(mention_id) {
    qstr = 'input[name=link-label-' + mention_id + ']:checked'
    var checkedCandidate = $(qstr);
    if (checkedCandidate.length == 0) {
        checkRadio(mention_id, 'radio-gen-' + mention_id + '-1')
    }
}

function nolinkChecked(mention_id) {
//    $('#div-link-' + mention_id).css({"opacity": "0.9"});
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
    if ($('.span-mention').length == 1) {
        $('#btn-submit').css({'background-color': '#337ab7', 'color': '#fff'});
    }

    $('#div-mention-1').css({"display": "block"});

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
            var btnid = "#btn-search-" + $(this).attr('id').substring(17);
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
