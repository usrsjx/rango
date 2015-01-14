$(document).ready(function() {

    // JQuery code to be added in here.

    $("p").hover(
        function() {
            $(this).css('color', 'red');
        },
        function() {
                $(this).css('color', 'blue');
        });

    var editable = "{{ editable }}" != "False";

    if (!editable) {
        $('input').prop("disabled", true);
        $('button').prop("disabled", true);
    }

});