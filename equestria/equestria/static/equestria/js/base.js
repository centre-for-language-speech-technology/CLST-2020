
let update_timer = null;
let update_list = [];

function create_element(tag_name, class_list, text) {
    let element = document.createElement(tag_name);
    for (let i = 0; i < class_list.length; i++) {
        element.classList.add(class_list[i]);
    }
    element.appendChild(document.createTextNode(text));
    return element;
}

function create_select(options) {
    let select = create_element('select', [], '');
    for (let i = 0; i < options.length; i++) {
        let option = create_element('option', [], options[i].text);
        option.value = options[i].value;
        select.appendChild(option);
    }
    return select;
}

function set_cookie(name,value,days) {
    let expires = "";
    value = encodeURI(value);
    if (days) {
        let date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}

function get_cookie(name) {
    let nameEQ = name + "=";
    let ca = document.cookie.split(';');
    for(let i=0;i < ca.length;i++) {
        let c = ca[i];
        while (c.charAt(0)===' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) === 0) return decodeURI(c.substring(nameEQ.length,c.length));
    }
    return null;
}

function update_and_replace(data_url, container, data) {
    let csrf_token = get_csrf_token();
    jQuery(function($) {
        data.csrfmiddlewaretoken = csrf_token;
        $.ajax({type: 'POST', url: data_url, data, dataType:'json', asynch: true, success:
            function(data) {
                replace_container(container, data.data)
            }}).fail(function() {
                console.error("Failed to update " + container);
            });
        }
    )
}

function update_and_callback(data_url, data, callback, method = 'POST'/*, args */) {
    let args = Array.prototype.slice.call(arguments, 4);
    let csrf_token = get_csrf_token();
    let headers = {};
    if (method === 'DELETE' || method === "PUT" || method === "PATCH") {
        headers = {"X-CSRFToken": csrf_token};
    }
    jQuery(function($) {
        data.csrfmiddlewaretoken = csrf_token;
        $.ajax({type: method, url: data_url, data, dataType: 'json', contentType: 'application/json', asynch: true, headers: headers}).done(
            function(data) {
                args.unshift(data);
                callback.apply(this, args);
            }).fail(function() {
                console.error("Failed to update");
            });
        }
    )
}

function update_and_callback_no_data(data_url, data, callback, method = 'POST'/*, args */) {
    let args = Array.prototype.slice.call(arguments, 4);
    let csrf_token = get_csrf_token();
    let headers = {};
    if (method === 'DELETE' || method === 'PUT') {
        headers = {"X-CSRFToken": csrf_token};
    }
    jQuery(function($) {
        data.csrfmiddlewaretoken = csrf_token;
        $.ajax({type: method, url: data_url, data, asynch: true, headers: headers}).done(
            function(data) {
                callback.apply(this, args);
            }).fail(function() {
                console.error("Failed to update");
                callback.apply(this, args);
            });
        }
    )
}

function send_update_request(data_url, callback, method = 'POST'/*, args */) {
    let args = Array.prototype.slice.call(arguments, 3);
    let csrf_token = get_csrf_token();
    let headers = {};
    if (method === 'DELETE' || method === 'PUT') {
        headers = {"X-CSRFToken": csrf_token};
    }
    jQuery(function($) {
        let data = {};
        data.csrfmiddlewaretoken = csrf_token;
        $.ajax({type: method, url: data_url, data, asynch: true, headers: headers, success:
            function(data) {
                args.unshift(data);
                callback.apply(this, args);
            }, error: function(xhr, status, error) {
                args.unshift(xhr.responseJSON);
                callback.apply(this, args);
            }});
        }
    )
}

function replace_container(container, data) {
    container.innerHTML = data;
}

function add_update_list(func, args, manual = false) {
    update_list.push({func: func, args: args, manual: manual});
}

function update_update_list(manual = true) {
    clearTimeout(update_timer);
    for (let i = 0; i < update_list.length; i++) {
        if (!update_list[i].manual || manual) {
            update_list[i].func.apply(this, update_list[i].args);
        }
    }
    update_timer = setTimeout(update_update_list, 5000, manual=false);
}

function get_csrf_token() {
    let cookie_csrf = get_cookie("csrftoken");
    if (cookie_csrf === null) {
        if (typeof CSRF_TOKEN !== 'undefined') {
            return CSRF_TOKEN;
        }
        else {
            throw "Unable to retrieve CSRF token";
        }
    }
    else {
        return cookie_csrf;
    }
}

$(document).ready(function() {
    update_update_list();
});