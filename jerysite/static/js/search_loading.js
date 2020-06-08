/*
        On submiting the form, send the POST ajax
        request to server and after successfull submission
        display the object.

$("#form_search").submit(function (e)
와 같은 문법 :
function call_search(){
    // e.preventDefault(); 필요없음.
}*/
function getCookie(c_name)
{
    if (document.cookie.length > 0)
    {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1)
        {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start,c_end));
        }
    }
    return "";
 }

$(document).ready(function () {
    //topic form id
    $("#topic-index-text").keydown(function (key) {
        //키의 코드가 13번일 경우 (13번은 엔터키)
        if (key.keyCode == 13) {
            key.preventDefault();
            var serializedData = $("#form_search").serialize();
            console.log("submit 후 함수 실행중");
            $.ajax({
                type: 'POST',
                url: "",
                dataType : 'json',
                data: serializedData,
                success: function (response) {
                    var temp = JSON.parse(response);
                    var topic = temp.topic;
                    var pk = temp.pk;
                    console.log("response : " + temp);
                    console.log('t : '+ topic);
                    console.log('pk : '+ pk);
                    window.location.href = ("result/"+topic+"/"+pk);
                },
                beforeSend: function() {
                    $('#loading').show();  // 보이도록 변경
                    //$('.class').hide();
                    // $('input').prop('disabled', true);
                },
                beforeSend: function() {
                    $('#loading').show();  // 보이도록 변경
                    $('input').prop('disabled', true);
                },
                error: function (response) {
                    // alert the error if any error occured
                    // TODO: undefined error 수정 - {{error_message}} 내용 바꾸던지..!
                    alert(response["error"]);
                    window.location.reload();   //페이지 새로고침
                }
            });
        }
    });
});
// html에 있는 id  ("") topic-main-text
$("#form_search_result").submit(function (e) {
    // preventing from page reload and default actions
    e.preventDefault();
    url = $(this).attr('action');
    var serializedData = $("#form_search_result").serialize();
    console.log("submit 후 함수 실행중");
    $.ajaxSetup({
        headers: {"X-CSRFToken": getCookie("csrftoken")}
    });
    $.ajax({
        type: 'POST',
        url: "",
        dataType : 'json',
        data: serializedData,
        success: function (response) {
            var temp = JSON.parse(response);
            var topic = temp.topic;
            var pk = temp.pk;
            console.log("response : " + temp);
            console.log('pk : '+ pk);
            window.location.href = ("../"+topic+"/"+pk);
        },
        beforeSend: function() {
            $('#loading').show();  // 보이도록 변경
            $('input').prop('disabled', true);
        },
        beforeSend: function() {
            $('#loading').show();  // 보이도록 변경
            $('input').prop('disabled', true);
        },
        beforeSend: function() {
            $('#loading').show();  // 보이도록 변경
            $('input').prop('disabled', true);
        },
        error: function (response) {
            // alert the error if any error occured
            // TODO: undefined error 수정 - {{error_message}} 내용 바꾸던지..!
            alert(response["error"]);
            window.location.reload();   //페이지 새로고침
        }
    });
});