from flask import Flask, render_template, request, redirect, url_for, flash
from statistics import mean

app = Flask(__name__)
app.secret_key = 'secret_key'


# Student and PerformanceTracker classes
class Student:
    def __init__(self, name, scores):
        self.name = name
        self.scores = scores

    def calculate_average(self):
        if len(self.scores) == 0:
            return 0
        return mean(self.scores)

    def is_passing(self):
        passing_score = 40
        return all(score >= passing_score for score in self.scores)


import pandas as pd


class PerformanceTracker:
    def __init__(self):
        self.students = {}

    def add_student(self, name, scores):
        if name in self.students:
            return False
        else:
            self.students[name] = Student(name, scores)
            self.save_to_excel()  # Save data to Excel after adding a student
            return True

    def calculate_class_average(self):
        if len(self.students) == 0:
            return 0
        return mean(student.calculate_average() for student in self.students.values())

    def get_student_performance(self):
        performance_data = []
        for student in self.students.values():
            avg_score = student.calculate_average()
            status = "Passing" if student.is_passing() else "Needs Improvement"
            performance_data.append({
                'name': student.name,
                'average_score': f"{avg_score:.2f}",
                'status': status
            })
        return performance_data

    def save_to_excel(self):
        data = {
            'Name': [],
            'Math': [],
            'Science': [],
            'English': [],
            'Average': [],
            'Status': []
        }

        for student in self.students.values():
            avg_score = student.calculate_average()
            status = "Passing" if student.is_passing() else "Needs Improvement"
            data['Name'].append(student.name)
            data['Math'].append(student.scores[0])
            data['Science'].append(student.scores[1])
            data['English'].append(student.scores[2])
            data['Average'].append(f"{avg_score:.2f}")
            data['Status'].append(status)

        df = pd.DataFrame(data)
        df.to_excel('students_performance.xlsx', index=False)


# Initialize tracker
tracker = PerformanceTracker()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form['name']
    try:
        scores = [int(request.form['math']), int(request.form['science']), int(request.form['english'])]
        if tracker.add_student(name, scores):
            flash(f"Student '{name}' added successfully!", 'success')
        else:
            flash(f"Student '{name}' already exists.", 'error')
    except ValueError:
        flash("Please enter valid numeric scores.", 'error')

    return redirect(url_for('index'))


@app.route('/show_performance')
def show_performance():
    performance_data = tracker.get_student_performance()
    class_average = tracker.calculate_class_average()
    return render_template('performance.html', performance_data=performance_data, class_average=class_average)

@app.route('/show_students')
def show_students():
    return render_template('students_table.html', students=tracker.students)

if __name__ == "__main__":
    app.run(debug=True)
