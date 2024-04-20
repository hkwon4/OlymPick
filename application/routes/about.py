from flask import Blueprint, request, render_template, redirect, url_for
from data import people_info

about_bp = Blueprint('about', __name__)

@about_bp.route('/About Me')
def team():
    names = list(people_info.keys())
    return render_template('index.html', names=names)

@about_bp.route('/about/<name>')
def about(name):
    person = people_info.get(name)
    if person:
        return render_template('about.html', person=person)
    else:
        return "Person not found"

@about_bp.route('/about/<name>/update', methods=['POST'])
def update_about(name):
    if request.method == 'POST':
        about = request.form['about']
        person = people_info.get(name)
        if person:
            person['about'] = about
            return redirect(url_for('about.about', name=name))
        else:
            return "Person not found"
    else:
        return redirect(url_for('about.about', name=name))