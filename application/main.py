from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Define a dictionary for each person's information
# Change your name, role in the group, and put some details in about
# To run, make sure your directory is in application, then type in the terminal "python main.py" (Flask required)
people_info = {
    'Name 1': {'name': 'Name 1', 'role': 'Engineer', 'about': ''},
    'Fadee Ghiragosian': {'name': 'Fadee Ghiragosian', 'role': 'Backend Lead', 'about': ' I am pursuing a degree in Computer Science, my family is from Egypt and Armenia, and I love playing video games. '},
    'Name 3': {'name': 'Name 3', 'role': 'Teacher', 'about': ''},
    'Name 4': {'name': 'Name 4', 'role': 'Doctor', 'about': ''},
    'Name 5': {'name': 'Name 5', 'role': 'Lawyer', 'about': ''},
    'Name 6': {'name': 'Name 6', 'role': 'Writer', 'about': ''},
    'Name 7': {'name': 'Name 7', 'role': 'Entrepreneur', 'about': ''},
}

@app.route('/')
def index():
    names = list(people_info.keys())
    return render_template('index.html', names=names)

@app.route('/about/<name>')
def about(name):
    person = people_info.get(name)
    if person:
        return render_template('about.html', person=person)
    else:
        return "Person not found"

@app.route('/about/<name>/update', methods=['POST'])
def update_about(name):
    if request.method == 'POST':
        about = request.form['about']
        person = people_info.get(name)
        if person:
            person['about'] = about
            return redirect(url_for('about', name=name))
        else:
            return "Person not found"
    else:
        return redirect(url_for('about', name=name))

if __name__ == '__main__':
    app.run(debug=True)
