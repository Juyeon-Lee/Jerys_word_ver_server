/*
        On submiting the form, send the POST ajax
        request to server and after successfull submission
        display the object.

$("#form_search").submit(function (e)
와 같은 문법 :
function call_search(){
    // e.preventDefault(); 필요없음.
}*/
function getCookie(c_name) {
    if (document.cookie.length > 0) {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1) {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start, c_end));
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
            // console.log( $("#topic-index-text").val());
            // console.log("submit 후 함수 실행중");

            var flag = 1;
            if ((new RegExp(/[a-zA-Z]/gi)).test($("#topic-index-text").val())  //영어
                || (new RegExp(/[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\"\'…{}]/gi)).test($("#topic-index-text").val()) //특수문자
                || (new RegExp(/[ㄱ-ㅎ|ㅏ-ㅣ]/gi)).test($("#topic-index-text").val())
                || (new RegExp(/[0-9]/gi)).test($("#topic-index-text").val())
            ) {
                alert("올바르지 않은 글자(영문자, 특수문자, 숫자 등)를 제외하고 입력하세요.");
                flag = 0;
            } 
            // else if ((new RegExp(/[0-9]/gi)).test($("#topic-main-text").val())) { //숫자
    //     var input_splited = $("#topic-main-text").val().split(' ');
    //     for (var i = 0 in input_splited) {    //나눠서 한 문자열씩 검사
    //         console.log(input_splited[i]);
    //         if (new RegExp(/[가-힣]/gi).test(input_splited[i])); //한글있으면 통과
    //         else {  //한글 포함 안된게 하나라도 있으면 break
    //             alert("숫자만 입력된 검색어가 있습니다. 다시 확인해주세요.");
    //             flag = 0;
    //             break;
    //         }
    //     }
    // }
            if (flag === 1) {
                console.log("ajax 실행");
                $.ajax({
                    type: 'POST',
                    url: "",
                    dataType: 'json',
                    data: serializedData,
                    success: function (response) {
                        var temp = JSON.parse(response);
                        var topic = temp.topic;
                        var pk = temp.pk;
                        console.log("response : " + temp);
                        console.log('t : ' + topic);
                        console.log('pk : ' + pk);
                        window.location.href = ("result/" + topic + "/" + pk);
                    },
                    beforeSend: function () {
                        $('#loading').show();  // 보이도록 변경
                        //$('.class').hide();
                        // $('input').prop('disabled', true);
                    },
                    error: function (response) {
                        //console.log(JSON.parse(response.responseJSON).error.topic[0]);
                        alert("올바르지 못한 단어 혹은 학습되지 않은 단어가 있습니다. 확인 후 다시 입력해주세요.");
                        window.location.reload();   //페이지 새로고침
                    }
                });
            }
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
        headers: { "X-CSRFToken": getCookie("csrftoken") }
    });

    var flag = 1;
    if ((new RegExp(/[a-zA-Z]/gi)).test($("#topic-main-text").val())  //영어
        || (new RegExp(/[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\"\'…{}]/gi)).test($("#topic-main-text").val()) //특수문자
        || (new RegExp(/[ㄱ-ㅎ|ㅏ-ㅣ]/gi)).test($("#topic-main-text").val())
        || (new RegExp(/[0-9]/gi)).test($("#topic-main-text").val())
    ) {
        alert("올바르지 않은 글자(영문자, 특수문자 등)를 제외하고 입력하세요.");
        flag = 0;
    } 
    
    if (flag === 1) {
        console.log("ajax 실행");
        $.ajax({
            type: 'POST',
            url: "",
            dataType: 'json',
            data: serializedData,
            success: function (response) {
                var temp = JSON.parse(response);
                var topic = temp.topic;
                var pk = temp.pk;
                console.log("response : " + temp);
                console.log('pk : ' + pk);
                window.location.href = ("../" + topic + "/" + pk);
            },
            beforeSend: function () {
                $('#loading').show();  // 보이도록 변경
                $('input').prop('disabled', true);
            },
            error: function (response) {
                //console.log(JSON.parse(response.responseJSON).error.topic[0]);
                alert("올바르지 못한 입력 혹은 학습되지 않은 단어가 있습니다. 확인 후 다시 입력해주세요.");
                window.location.reload();   //페이지 새로고침
            }
        });
    }
});