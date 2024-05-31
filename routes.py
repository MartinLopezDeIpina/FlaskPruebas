from flask import render_template, session, redirect, url_for, request

from app import app
from models import Persona


@app.route('/personas')
def personas():
    personas = Persona.query.all()
    return render_template('personas.html', personas=personas)


@app.route('/persona/<int:id>')
def persona(id):
    persona = Persona.query.get_or_404(id)
    return render_template('persona.html', persona=persona)


@app.route('/')
def index():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/home')
def home():
    if session.get('username') is None:
        return redirect(url_for('login'))
    else:
        return render_template('home.html', username=session['username'])


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

