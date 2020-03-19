function validate(obj, file, counter, arrayExtensions) {
    var ext = file.split(".");
    ext = ext[ext.length-1].toLowerCase();      
    
    if (arrayExtensions.lastIndexOf(ext) == -1) {
	$(obj).val("");
	$(obj).fadeOut(100).fadeIn(100).fadeOut(100).fadeIn(100);
	$("#p" + counter).fadeOut(100).fadeIn(100).fadeOut(100).fadeIn(100);
    }
}
