from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Define a dictionary for each person's information
# Change your name, role in the group, and put some details in about
# To run, make sure your directory is in application, then type in the terminal "python main.py" (Flask required)
people_info = {
    'Johnny Kwon': {'name': 'Johnny Kwon', 'role': 'Team Lead', 'about': 'I am the team leader of this project and a Senior CS Major of SFSU. Always learning and look forward to suffering in this field'},
    'Fadee Ghiragosian': {'name': 'Fadee Ghiragosian', 'role': 'Backend Lead', 'about': ' I am pursuing a degree in Computer Science, my family is from Egypt and Armenia, and I love playing video games. '},
    'Ethan Ho': {'name': 'Ethan Ho', 'role': 'Github Lead', 'about': ' Last semester for CS Degree. I build custom keyboards, play video games, and read in my spare time. '},
    'Abby Lin': {'name': 'Abby Lin', 'role': 'Database', 'about': ' Last Semester CS Major, an international transfer student from Taiwan. I love music, swimming, and playing games.'},
    'Nichan Lama': {'name': 'Nichan lama', 'role': 'Backend', 'about': 'I am a CS major. I love trying out new food and working out.'},
    'Zabiullah Niemati': {'name': 'Zabiullah Niemati', 'role': 'Frontend', 'about': 'My name is Zabiullah Niemati, and hopefully, this will be my last semester at SFSU. I am majoring in computer science. I already hold a bachelor's degree in engineering from overseas, and this will be my second bachelor's degree.'},
    'Zizo Ezzat': {'name': 'Zizo Ezzat', 'role': 'Frontend', 'about': '4th year CS Major, I love working out and listening to music.'},
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
