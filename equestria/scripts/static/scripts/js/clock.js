// pads a number to a specified size by prepending zeros
function pad(num, size) {
    var s = num+"";
    while (s.length < size) s = "0" + s;
    return s;
    
}

function update_clock() {
    var dNow = new Date();
    var utc = new Date(dNow.getTime() + dNow.getTimezoneOffset() * 60000);
    var utcdate = pad(utc.getFullYear(), 4) + '-' + pad(utc.getMonth()+1, 2) + '-' + pad(utc.getDate(),2) + ' ' + pad(utc.getHours(),2) + ':' + pad(utc.getMinutes(),2) + ':' + pad(utc.getSeconds(),2);
    $('.clock').text(utcdate);
    // execute every half a second
    setTimeout(update_clock, 1000);
}

$( document ).ready(function() {
    update_clock();
});
