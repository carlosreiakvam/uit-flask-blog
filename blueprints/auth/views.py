from urllib.parse import urljoin, urlparse

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from mysql.connector import Error, errorcode

from blueprints.auth.forms import LoginForm, RegisterForm
from models.bruker import Bruker

router = Blueprint('auth', __name__, url_prefix="/auth")


@router.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        bruker = Bruker.get_user(form.brukernavn.data)
        if bruker:
            flash("Brukernavn er allerede tatt", "danger")
            return render_template('register.html', form=form, heading="Registrer ny bruker")
        bruker = Bruker(brukernavn=form.brukernavn.data, epost=form.epost.data, opprettet=None,
                        fornavn=form.fornavn.data, etternavn=form.etternavn.data)
        bruker.hash_password(form.passord.data)

        bruker.insert_user()

        flash("Registreringen var vellykket!")

        return redirect(url_for("auth.login"))

    for fieldName, error_messages in form.errors.items():
        for error_message in error_messages:
            flash(f"{error_message}", "danger")

    return render_template('register.html', form=form, title="Ny bruker", heading="Registrer ny bruker")


@router.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():

        bruker = Bruker.get_user(form.username.data)
        if bruker is None or not bruker.check_password(form.password.data):
            flash('Feil brukernavn og/eller passord', 'danger')
            return render_template('login.html', form=form, heading="Logg inn")

        login_user(bruker)

        flash('Logged in successfully.', 'success')

        next_url = request.args.get('next')
        if not is_safe_url(next_url):
            return abort(400)
        print(next_url)
        return redirect(next_url or url_for("hovedside.index"))
    return render_template('login.html', form=form, title="login", heading="Logg inn")


@router.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("hovedside.index"))


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc
