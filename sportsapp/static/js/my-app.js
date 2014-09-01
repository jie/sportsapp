// add string.format method
String.prototype.format = function(args) {
    var newStr = this;
    for (var key in args) {
        newStr = newStr.replace('{' + key + '}', args[key]);
    }
    return newStr;
};

function docSting(f) {
    return f.toString().replace(/^[^\/]+\/\*!?\s?/, '').replace(/\*\/[^\/]+$/, '');
}

// Initialize your app
var myApp = new Framework7({
    pushState: true,
});


// Export selectors engine
var $$ = Framework7.$;

myApp.urlParams = {
    'GET_KINDS': 'api/kinds',
    'GET_NOTES': 'api/notes',
}

myApp.userData = {
    'notes': [],
    'kinds': []
}

var setKinds = function(content) {
    var itemHTML = docSting(function() {
        /*
    <li>
        <a href='{link}' class='item-link item-content'>
            <div class='item-media'><i class='icon icon-f7'></i>
            </div>
            <div class='item-inner'>
                <div class='item-title'>{name}</div>
                <div class='item-after'></div>
            </div>
        </a>
    </li>
    */
    });
    $$('.note-kind').find('ul').html('');
    for (var item in content.kinds) {
        $$('.note-kind').find('ul').prepend(itemHTML.format({
            'link': 'note/create/' + content.kinds[item].pk,
            'name': content.kinds[item].name
        }));
    }
    myApp.pullToRefreshDone();
}


myApp.setNotes = function(content) {
    var itemHTML = docSting(function() {
        /*
    <li>
        <a href='{link}' class='item-link item-content'>
            <div class='item-media'><i class='icon icon-f7'></i>
            </div>
            <div class='item-inner'>
                <div class='item-title'>{name}</div>
                <div class='item-after'></div>
            </div>
        </a>
    </li>
    */
    });
    for (var item in content.notes) {
        $$('.note-kind').find('ul').prepend(itemHTML.format({
            'link': 'note/create/' + item.pk,
            'name': item.name
        }));
    }
}

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
            myApp.closeModal('.login-screen');
            createCookie('session_token', response.content.token, 30);
        } else {
            myApp.addNotification({
                title: response.title,
                message: response.message
            });
        }

    }, 300);
});

$('body').delegate('.signup-btn', 'click', function() {
    var formData = myApp.formToJSON('.signup-form');
    $$.post("api/accounts/signup", formData, function(data) {
        var response = JSON.parse(data);
        if (response.status == 0) {
            createCookie('session_token', response.content.token, 30);
            viewHome.loadPage('/');
        } else {
            myApp.addNotification({
                title: response.title,
                message: response.message
            });
        }

    }, 300);
});


$('body').delegate('.create-kind-btn', 'click', function() {
    var formData = myApp.formToJSON('.kind-form');
    $$.post("api/kind/create", formData, function(data) {
        var response = JSON.parse(data);
        if (response.status == 0) {
            viewForm.goBack();
        } else {
            myApp.addNotification({
                title: response.title,
                message: response.message
            });
        }

    }, 300);
});

myApp.onPageInit('signup', function(page) {
    myApp.closeModal('.login-screen');
    $$('.toolbar').addClass('hidden-toolbar');
});

myApp.onPageInit('note-detail', function(page) {
    $$('.toolbar').addClass('hidden-toolbar');
});

myApp.onPageBeforeRemove('note-detail', function(page) {
    $$('.toolbar').removeClass('hidden-toolbar');
});


$$('#viewForm').on('show', function() {
    if (myApp.userData.kinds.length == 0) {
        getByApi(myApp.urlParams.GET_KINDS, setKinds);
    }
});


// myApp.onPageInit('*', function(page) {
//     signinCheckCookie();
// });


var getByApi = function(url, callback) {
    $$.get(url, function(data) {
        var response = JSON.parse(data);
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


var signinCheckCookie = function() {
    myApp.session_token = readCookie('session_token');
    if (!myApp.session_token) {
        myApp.loginScreen();
    }
};

$('body').delegate('.refresh-kinds', 'refresh', function(e) {
    console.log('asdasdasdasdasd');
    getByApi(myApp.urlParams.GET_KINDS, setKinds);
});

$(document).ready(function() {
    signinCheckCookie();
});
