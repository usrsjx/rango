$(document).ready(function() {
    $('#likes').click(function(){
        var catid = $(this).attr("data-catid");
        $.get('/rango/like_category/', {category_id: catid}, function(data){
                   $('#like_count').html(data);
                   $('#likes').hide();
        });
    });

    $('#suggestion').keyup(function(){
        var typed_suggestion;
        typed_suggestion = $(this).val();
        $.get('/rango/category_suggest/', {suggestion: typed_suggestion}, function(data){
                   $('#cats').html(data);
        });
    });

    $('.rango-add').click(function(){
        var catid = $(this).attr("data-catid");
        var catTitle = $(this).attr("data-title");
        var catUrl = $(this).attr("data-url");
        $.get('/rango/auto_add_page/', {category_id: catid, title: catTitle, url: catUrl}, function(data){
               $('#pages').html(data);
        });
    });
});