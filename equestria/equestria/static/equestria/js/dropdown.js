$(document).ready(function(){
    $(".dropdown").hover(            
	dropdown, dropup
    );
    $(".dropdown-toggle").click(function (e) {
	e.preventDefault();
	var href = $(this).attr("href");
	window.open(href);
	return false;
    }

			       );
});

function dropdown() {
    $('.dropdown-menu', this).not('.in .dropdown-menu').stop(true,true).slideDown("400");
    $(this).toggleClass('open');        
}

function dropup() {
    $('.dropdown-menu', this).not('.in .dropdown-menu').stop(true,true).slideUp("400");
    $(this).toggleClass('open');       
}
