$(document).ready(function () {
    $('body').fadeIn({ duration: 150 });
})

$(document).ready(function () {
    $('.calendar').datepicker({
        showButtonPanel: true,
        changeMonth: true,
        changeYear: true,
        minDate: '+1D'
    });
})