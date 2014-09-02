// Initialize your app
var myApp = new Framework7({
    pushState: true,
});


// Export selectors engine
var $$ = Dom7;


// add string.format method
String.prototype.format = function(args) {
    var newStr = this;
    for (var key in args) {
        newStr = newStr.replace('{' + key + '}', args[key]);
    }
    return newStr;
};

Date.prototype.formate_date = function() {
    var year = this.getFullYear();
    var date = ("0" + this.getDate()).slice(-2);
    var month = ("0" + (this.getMonth() + 1)).slice(-2);
    return "{year}-{month}-{date}".format({
        year: year,
        month: month,
        date: date
    });
}

function docSting(f) {
    return f.toString().replace(/^[^\/]+\/\*!?\s?/, '').replace(/\*\/[^\/]+$/, '');
}


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


var setNotes = function(content) {
    var itemNoteHTML = docSting(function() {
        /*
    <div class="list-block">
      <ul>
        <li class="item-content">
          <div class="item-inner">
            <div class="item-title">Item title</div>
          </div>
        </li>
      </ul>
    </div>
    */
    });
    var itemContentHtml = docSting(function() {
        /*
        < div class = "content-block-title" >{title}< /div>
        
        */
    });


    $$('.notes-list').html('');
    var previous_date = '';
    for (var item in content.notes) {
        if (previous_date != content.notes[item].create_date) {
            previous_date = content.notes[item].create_date
            $$('.notes-list').append('<div class="content-block-title item-date" style="text-align:center; margin-bottom:0;">{create_date}</div>'.format({
                create_date: previous_date
            }));
        }

        $$('.notes-list').append('<div class="item-kind content-block">{kind}: {quantity}</div>'.format({
            'quantity': content.notes[item].quantity,
            'kind': content.notes[item].kind['name']
        }))
        if (content.notes[item].content) {
            $$('.notes-list').append('<div class="content-block inset item-kind"><div class="content-block-inner">{content}</div></div>'.format({
                content: content.notes[item].content
            }));
        }
    }

    myApp.pullToRefreshDone();
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
        } else if (response.status == -2) {
            eraseCookie('session_token');
        }
        myApp.addNotification({
            title: response.title,
            message: response.message
        });

    }, 300);
});

$('body').delegate('.signup-btn', 'click', function() {
    var formData = myApp.formToJSON('.signup-form');
    $$.post("api/accounts/signup", formData, function(data) {
        var response = JSON.parse(data);
        if (response.status == 0) {
            createCookie('session_token', response.content.token, 30);
            viewHome.loadPage('/');
        } else if (response.status == -2) {
            eraseCookie('session_token');
        }
        myApp.addNotification({
            title: response.title,
            message: response.message
        });
    }, 300);
});


$('body').delegate('.create-kind-btn', 'click', function() {
    var formData = myApp.formToJSON('.kind-form');
    $$.post("api/kind/create", formData, function(data) {
        var response = JSON.parse(data);
        if (response.status == 0) {
            viewForm.goBack();
        } else if (response.status == -2) {
            eraseCookie('session_token');
        }
        myApp.addNotification({
            title: response.title,
            message: response.message
        });
    }, 300);
});


$('body').delegate('.create-note-btn', 'click', function() {
    var formData = myApp.formToJSON('.note-form');
    $$.post("api/note/create", formData, function(data) {
        var response = JSON.parse(data);
        if (response.status == 0) {
            viewForm.goBack();
            myApp.showTab('#viewHome');
        } else if (response.status == -2) {
            eraseCookie('session_token');
        }

        myApp.addNotification({
            title: response.title,
            message: response.message
        });

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

myApp.onPageInit('create-note', function(page) {
    var today = new Date();
    $('.note-date').attr('value', today.formate_date());
});

$$('#viewForm').on('show', function() {
    if (myApp.userData.kinds.length == 0) {
        getByApi(myApp.urlParams.GET_KINDS, setKinds);
    }
});


var getByApi = function(url, callback) {
    $$.get(url, function(data) {
        var response = JSON.parse(data);
        if (response.status == 0) {
            callback(response.content);
        } else if (response.status == -2) {
            eraseCookie('session_token');
        }
        myApp.addNotification({
            title: response.title,
            message: response.message
        });

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

$$('.refresh-kinds').on('refresh', function(e) {
    getByApi(myApp.urlParams.GET_KINDS, setKinds);
});

$$('.refresh-notes').on('refresh', function(e) {
    getByApi(myApp.urlParams.GET_NOTES, setNotes);
});


$(document).ready(function() {
    signinCheckCookie();
});
