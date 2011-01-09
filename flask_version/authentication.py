from flask import Flask, url_for, render_template, request, session, redirect, g

from base import app

##################
# Authentication #
##################

@app.route('/login', methods=['POST', 'GET'])
def login():
    from sagenb.misc.misc import SAGE_VERSION
    template_dict = {'accounts': app.notebook.get_accounts(),
                     'default_user': app.notebook.default_user(),
                     'recovery': app.notebook.conf()['email'],
                     'next': request.values.get('next', ''), 
                     'sage_version':SAGE_VERSION}

    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']

        if username == 'COOKIESDISABLED':
            return "Please enable cookies or delete all Sage cookies and localhost cookies in your browser and try again."

        try:
            U = app.notebook.user(username)
        except KeyError:
            #log.msg("Login attempt by unknown user '%s'."%username)
            U = None
            template_dict['username_error'] = True
            
        if U is None:
            pass
        elif U.password_is(password):
            if U.is_suspended():
                #suspended
                return "Your account is currently suspended"
            else:
                #Valid user, everything is okay
                session['username'] = username
                session.modified = True
                return redirect(request.values.get('next', url_for('index')))
        else:
            template_dict['password_error'] = True

    response = app.make_response(render_template('html/login.html', **template_dict))
    response.set_cookie('cookie_test_%s'%app.notebook.port, 'cookie_test')
    return response

@app.route('/logout/')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))
