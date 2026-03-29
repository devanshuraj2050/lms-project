# ============================================
# NOTE:
# This project was initially using courses.json
# Now fully migrated to SQLite database (lms.db)
# All course-related operations use DB only
# ============================================
import os

import json

import sqlite3

from flask import Flask, render_template,request, redirect, url_for, session

app = Flask(__name__)

app.secret_key = "lms_secret_key"


@app.route("/")
def home():
    return render_template("index.html")

import json
@app.route("/courses")
def courses():

    # ============================================
    # OLD: Data was loaded from courses.json
    # NEW: Fetching all courses from database
    # ============================================

    conn = sqlite3.connect("lms.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()

    conn.close()

    return render_template("courses.html", courses=courses)


# Here I am going to add the routes for the add courses by the admin. 

@app.route("/add_course", methods=["GET","POST"])
def add_course():

    if request.method == "POST":

        # ============================================
        # OLD: Course was saved in JSON file
        # NEW: Insert course into database
        # ============================================

        conn = sqlite3.connect("lms.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO courses (title, age, duration, price, image, description)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            request.form["title"],
            request.form["age"],
            request.form["duration"],
            request.form["price"],
            request.form["image"],
            request.form["description"]
        ))

        conn.commit()
        conn.close()

        return redirect("/courses")

    return render_template("add_course.html")


# Now here I am going to add routes for the course management and deletion by the admin.


@app.route("/manage_courses")
def manage_courses():

    # ============================================
    # OLD: Courses loaded from JSON
    # NEW: Fetch all courses from database
    # ============================================

    conn = sqlite3.connect("lms.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()

    conn.close()

    return render_template("manage_courses.html", courses=courses)


# deletion

@app.route("/delete_course/<int:id>")
def delete_course(id):

    # ============================================
    # OLD: Deleted course using list index (JSON)
    # NEW: Delete course using database ID
    # ============================================

    conn = sqlite3.connect("lms.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM courses WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect(url_for("manage_courses"))



@app.route("/gallery")
def gallery():

    image_folder = "static/images"

    images = os.listdir(image_folder)

    return render_template('gallery.html', images=images, logged_in=('user' in session))



@app.route("/contact")
def contact():
    return render_template("contact.html")


# admin_login    


@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":

            session["user"] = username

            return redirect(url_for("dashboard"))

        else:
            return "Invalid username or password"

    return render_template("login.html")


# student_login
@app.route("/login", methods=["GET","POST"])
def student_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("lms.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM students WHERE email=? AND password=?", (email,password))
        student = cursor.fetchone()

        conn.close()

        if student:
            session["student_email"] = email
            return redirect("/student_dashboard")

        else:
            return "Invalid email or password"

    return render_template("student_login.html")



# STUDENT DASHBOARD
@app.route("/student_dashboard")
def student_dashboard():

    if "student_email" not in session:
        return redirect(url_for("student_login"))

    student_email = session["student_email"]

    conn = sqlite3.connect("lms.db")
    cursor = conn.cursor()

    # ============================================
    # Fetch enrolled course IDs from DB
    # ============================================

    cursor.execute("""
    SELECT course_id FROM enrollments
    WHERE student_email=?
    """, (student_email,))
    
    enrollments = cursor.fetchall()

    # ============================================
    # OLD: Courses fetched from JSON using index
    # NEW: Fetch each course directly from DB
    # ============================================

    my_courses = []

    for enrollment in enrollments:
        course_id = enrollment[0]

        cursor.execute("SELECT * FROM courses WHERE id=?", (course_id,))
        course = cursor.fetchone()

        if course:
            my_courses.append(course)

    conn.close()

    total_courses = len(my_courses)

    return render_template(
        "student_dashboard.html",
        student_email=student_email,
        total_courses=total_courses,
        courses=my_courses
    )

# MY COURSE ROUTES
@app.route("/my_courses")
def my_courses():

    if "student_email" not in session:
        return redirect(url_for("student_login"))

    student_email = session["student_email"]

    conn = sqlite3.connect("lms.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT course_id FROM enrollments
    WHERE student_email=?
    """, (student_email,))

    enrollments = cursor.fetchall()

    # ============================================
    # OLD: Used JSON
    # NEW: Fetch courses from DB
    # ============================================

    my_courses = []

    for enrollment in enrollments:
        course_id = enrollment[0]

        cursor.execute("SELECT * FROM courses WHERE id=?", (course_id,))
        course = cursor.fetchone()

        if course:
            my_courses.append(course)            

    conn.close()

    return render_template(
        "my_courses.html",
        courses=my_courses,
        student_email=student_email
    )
# COURSE STATS ROUTES
@app.route("/admin/course_stats")
def course_stats():

    conn = sqlite3.connect("lms.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT course_id, COUNT(*) 
    FROM enrollments
    GROUP BY course_id
    """)

    stats = cursor.fetchall()

    # ============================================
    # OLD: Titles fetched from JSON
    # NEW: Fetch titles from DB using course_id
    # ============================================

    course_data = []

    for course_id, count in stats:
        cursor.execute("SELECT title FROM courses WHERE id=?", (course_id,))
        result = cursor.fetchone()

        if result:
            course_data.append({
                "title": result[0],
                "count": count
            })

    conn.close()

    return render_template("course_stats.html", course_data=course_data)



    

@app.route("/dashboard")
def dashboard():

    if "user" in session:
        return render_template("dashboard.html")

    return redirect(url_for("admin_login"))

@app.route("/principal")
def principal():
    return render_template("principal.html")


@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect(url_for("home"))


# Now here I am going to add upload routes bro........................


@app.route("/upload", methods=["GET","POST"])
def upload():

    if "user" not in session:
        return redirect(url_for("admin_login"))

    if request.method == "POST":

        file = request.files["image"]

        if file:

            filepath = os.path.join("static/images", file.filename)

            file.save(filepath)

            return "Image uploaded successfully"

    return render_template("upload.html")


    # Now here I am going to add delete button  routes bro........................

    
@app.route('/manage_gallery')
def manage_gallery():
    if 'user' not in session:
        return redirect('/login')

    images = os.listdir('static/images')
    return render_template('manage_gallery.html', images=images)



import os
from flask import redirect, url_for

@app.route('/delete/<filename>')
def delete_image(filename):

    filepath = os.path.join('static/images', filename)

    if os.path.exists(filepath):
        os.remove(filepath)

    return redirect(url_for('manage_gallery'))


# Route to display all registered students (Admin Panel)


@app.route("/admin/students")
def admin_students():
    conn = sqlite3.connect("lms.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()

    return render_template("admin_students.html", students=students)



# Now here I am adding student table for the admin_student.html page bro..............



def create_students_table():
    conn = sqlite3.connect("lms.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

create_students_table()



def create_courses_table():
    conn = sqlite3.connect("lms.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        age TEXT,
        duration TEXT,
        price TEXT,
        description TEXT,
        image TEXT
    )
    """)

    conn.commit()
    conn.close()

create_courses_table()



# Create the Enrollments Table
def create_enrollments_table():
    conn = sqlite3.connect("lms.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_email TEXT,
        course_id INTEGER
    )
    """)

    conn.commit()
    conn.close()

create_enrollments_table()




# Now here I am adding the sign up routes for the students.........
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("lms.db")
        cursor = conn.cursor()

        # ✅ Step 1: Check if email already exists
        cursor.execute("SELECT * FROM students WHERE email=?", (email,))
        existing = cursor.fetchone()

        # if existing:
        #     conn.close()
        #     return "Email already registered! Please login."

        # # ✅ Step 2: Insert new student safely
        try:
            cursor.execute("""
                INSERT INTO students (name, email, password)
                VALUES (?, ?, ?)
            """, (name, email, password))

            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()
            return "Email already exists! Please login."

        conn.close()

        # ✅ Step 3: Auto login after signup
        session["student_email"] = email

        return redirect("/courses")

    return render_template("signup.html")



# Enroll Button
@app.route("/enroll/<int:course_id>")
def enroll(course_id):
    """
    This route handles course enrollment for a student.
    It ensures:
    1. Only logged-in users can enroll
    2. Duplicate enrollments are prevented
    """

    # ✅ Step 1: Check if user is logged in
    if "student_email" not in session:
        return redirect("/login")

    # ✅ Step 2: Get logged-in student's email from session
    student_email = session["student_email"]

    # ✅ Step 3: Connect to database
    conn = sqlite3.connect("lms.db")
    cursor = conn.cursor()

    # ✅ Step 4: Check if the student is already enrolled in this course
    cursor.execute("""
        SELECT * FROM enrollments
        WHERE student_email = ? AND course_id = ?
    """, (student_email, course_id))

    existing = cursor.fetchone()

    # ✅ Step 5: If NOT already enrolled → insert new record
    if not existing:
        cursor.execute("""
            INSERT INTO enrollments (student_email, course_id)
            VALUES (?, ?)
        """, (student_email, course_id))

        # Save changes
        conn.commit()

    # ✅ Step 6: Close database connection
    conn.close()

    # ✅ Step 7: Redirect user to My Courses page
    return redirect("/my_courses")




# ✅ FIX: Add Course Detail Route (MANDATORY)
@app.route("/course/<int:course_id>")
def course_detail(course_id):

    if "student_email" not in session:
        return redirect("/login")

    student_email = session["student_email"]

    conn = sqlite3.connect("lms.db")
    cursor = conn.cursor()

    # Get course
    cursor.execute("SELECT * FROM courses WHERE id=?", (course_id,))
    course = cursor.fetchone()

    # Check if already enrolled
    cursor.execute("""
    SELECT * FROM enrollments
    WHERE student_email=? AND course_id=?
    """, (student_email, course_id))

    enrollment = cursor.fetchone()

    conn.close()

    return render_template(
        "course_detail.html",
        course=course,
        enrolled=enrollment
    )



if __name__ == "__main__":
    app.run(debug=True)