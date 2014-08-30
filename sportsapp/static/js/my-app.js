// Initialize your app
var myApp = new Framework7();

// Export selectors engine
var $$ = Framework7.$;

// Add views
var viewHome = myApp.addView('#viewHome', {
    dynamicNavbar: true
});
var viewForm = myApp.addView('#viewForm', {
    dynamicNavbar: true
});
var viewMore = myApp.addView('#viewMore', {
    dynamicNavbar: true
});

$$('.signin-btn').on('click', function() {
    var formData = myApp.formToJSON('.signin-form');
    $$.post("api/accounts/signin", formData, function(data) {
        var response = JSON.parse(data);
        if (response.status == 0) {
            createCookie('sportsapp', response.sessionid, 30);
            myApp.closeModal('.login-screen');
        } else {
            myApp.addNotification({
                title: 'Signin fail',
                message: response.message
            });
        }

    }, 300);
});


myApp.onPageInit('note-detail', function(page) {
    $$('.toolbar').addClass('hidden-toolbar');
});

myApp.onPageBeforeRemove('note-detail', function(page) {
    $$('.toolbar').removeClass('hidden-toolbar');
});

myApp.onPageInit('*', function(page) {
    signinCheckCookie();
});

var getByApi = function(url, callback) {
    $$.get(url, function(data) {
        if (response.status == 0) {
            callback(response.content);
        } else {
            myApp.addNotification({
                title: response.title,
                message: response.message
            });
        }

    }, 300);
}

var postByApi = function(url, params, callback) {

    var response

    $$.post(url, JSON.stringify(params), function(data) {
        if (response.status == 0) {
            callback(response.content);
        } else {
            myApp.addNotification({
                title: response.title,
                message: response.message
            });
        }

    }, 300);
}

var songs = ['Yellow Submarine', 'Don\'t Stop Me Now', 'Billie Jean', 'Californication'];
var authors = ['Beatles', 'Queen', 'Michael Jackson', 'Red Hot Chili Peppers'];

var ptrContent = $$('.pull-to-refresh-content');

// Add 'refresh' listener on it
ptrContent.on('refresh', function(e) {
    // Emulate 2s loading
    setTimeout(function() {


        // getByApi('api/items', refreshHomePage);

        var itemHTML = '<li class="item-content">' +
            '<div class="item-media"><img src="' + picURL + '" width="44"/></div>' +
            '<div class="item-inner">' +
            '<div class="item-title-row">' +
            '<div class="item-title">' + song + '</div>' +
            '</div>' +
            '<div class="item-subtitle">' + author + '</div>' +
            '</div>' +
            '</li>';
        // Prepend new list element
        ptrContent.find('ul').prepend(itemHTML);
        // When loading done, we need to reset it
        myApp.pullToRefreshDone();
    }, 300);
});


var homeLoadCallback = myApp.onPageInit('homepage', function(page) {
    // getByApi('api/items', refreshHomePage);
});

homeLoadCallback.trigger();

var signinCheckCookie = function() {
    myApp.session_token = readCookie('session-token');
    if (!myApp.session_token) {
        myApp.loginScreen();
    }
};

$(document).ready(function() {
    signinCheckCookie();
});
