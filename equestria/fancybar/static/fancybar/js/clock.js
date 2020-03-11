function update_clock() {
    var dNow = new Date();
    var utc = new Date(dNow.getTime() + dNow.getTimezoneOffset() * 60000);
    var utcdate= utc.getFullYear() + '-' + (utc.getMonth()+1) + '-' + utc.getDate() + ' ' + utc.getHours() + ':' + utc.getMinutes() + ':' + utc.getSeconds();
    $('.clock').text(utcdate);
    // execute every half a second
    setTimeout(update_clock, 1000);
}

$( document ).ready(function() {
    update_clock();
});
