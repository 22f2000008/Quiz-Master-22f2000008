from flask import render_template, request, redirect, flash, url_for, session
from flask import current_app as app
from .models import db, Admin, User_Info, Subject, Quiz, Score, Chapter, Question
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')   

import matplotlib.pyplot as plt  
import io
import base64
from flask import Blueprint

 
app.py = Blueprint("stats", __name__)

@app.route("/", methods=["GET", "POST"])
def Home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def signin():
    if request.method == "GET":
        return render_template("login.html")

    elif request.method == "POST":
        usernames = request.form.get("user_name")
        passwords = request.form.get("password")

        user = Admin.query.filter_by(email=usernames, password=passwords).first()
        if user:
            session["user_role"] = "admin"  
            session["user_id"] = user.id  
            return redirect("/adminhome")

        user = User_Info.query.filter_by(email=usernames, password=passwords).first()
        if user:
            session["user_role"] = "user"
            session["user_id"] = user.id  
            return redirect("/userdashboard")

        flash("Invalid username or password", "error")
        return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def signup():
    admin_exists = Admin.query.first() is not None

    if request.method == "GET":
        return render_template("Signup.html", admin_exists=admin_exists)

    elif request.method == "POST":
        uname = request.form.get("user_name")  
        pwd = request.form.get("password")
        full_name = request.form.get("full_name")
        qualification = request.form.get("qualification")
        dob_str = request.form.get("dob")

        if not admin_exists:

            new_admin = Admin(email=uname, password=pwd, name=full_name)
            db.session.add(new_admin)
            db.session.commit()

            session["user_role"] = "admin"
            session["user_id"] = new_admin.id
            flash("Admin registration successful. Please log in.", "success")
            return redirect("/login")
        
        else:
            # if admin exists, only user can register
            user = User_Info.query.filter_by(email=uname).first()
            if user:
                flash("Email already registered. Try logging in.", "warning")
                return redirect("/register")
            
            new_user = User_Info(email=uname, password=pwd, full_name=full_name, qualification=qualification, dob=dob_str)
            db.session.add(new_user)
            db.session.commit()

            session["user_role"] = "user"
            session["user_id"] = new_user.id
            flash("User registration successful. Please log in.", "success")
            return redirect("/login")

@app.route("/userdashboard", methods=["GET", "POST"])
def user_dash():
    print("Session data in user_dash:", session)
    quizzes = Quiz.query.join(Chapter).join(Subject).all()
    quizzes = Quiz.query.all()
    return render_template("userdashboard.html", quizzes=quizzes)

@app.route("/adminhome", methods=["GET", "POST"])
def admin_dash():

    print("Session data in admin_dash:", session)
    search_query = request.args.get("search", "").strip().lower()
    
    subjects = Subject.query.filter(Subject.subject_name.ilike(f"%{search_query}%")).all() if search_query else Subject.query.all()
    quizzes = Quiz.query.filter(Quiz.quiz_name.ilike(f"%{search_query}%")).all() if search_query else Quiz.query.all()
    
    return render_template("Adminhome.html", subjects=subjects, quizzes=quizzes, search_query=search_query)

@app.route("/create_subject", methods=["POST"])
def create_subject():
    sub_name = request.form.get("sub_name")
    if not sub_name:
        flash("Subject name is required!", "error")
        return redirect("/adminhome")

    try:
        new_subject = Subject(subject_name=sub_name)
        db.session.add(new_subject)
        db.session.commit()
        flash("Subject added successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "error")
    return redirect("/adminhome")
@app.route('/delete_subject/<int:subject_id>')
def delete_subject(subject_id):
    try:
        subject = Subject.query.get_or_404(subject_id)
        db.session.delete(subject)
        db.session.commit()
        flash("Subject deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting question: {e}", "error")

    return redirect("/adminhome")

@app.route("/edit_chapter", methods=["POST"])
def edit_chapter():
    chapter_id = request.form.get("chapter_id")
    chapter_name = request.form.get("chapter_name")
    no_of_questions = request.form.get("no_of_questions")

    if not chapter_id or not chapter_name or not no_of_questions:
        flash("All fields are required!", "error")
        return redirect("/adminhome")

    try:
        chapter = Chapter.query.get_or_404(chapter_id)
        chapter.chapter_name = chapter_name
        chapter.no_of_question = int(no_of_questions)
        db.session.commit()
        flash("Chapter updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating chapter: {e}", "error")
    
    return redirect("/adminhome")

@app.route("/add_chapter", methods=["POST"])
def add_chapter():
    subject_id = request.form.get("subject_id")
    cat_name = request.form.get("cat_name")
    cat_question = request.form.get("cat_question")

    if not subject_id or not cat_name or not cat_question:
        flash("All fields are required!", "error")
        return redirect("/adminhome")

    try:
        new_chapter = Chapter(chapter_name=cat_name, no_of_question=int(cat_question), subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        flash("Chapter added successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "error")
    return redirect("/adminhome")


@app.route('/delete_chapter/<int:chapter_id>')
def delete_chapter(chapter_id):
    try:
        chapter = Chapter.query.get_or_404(chapter_id)
        db.session.delete(chapter)
        db.session.commit()
        flash("Chapter deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting question: {e}", "error")

    return redirect("/adminhome")

@app.route("/quizdashboard", methods=["GET"])
def quiz_dashboard():
    search_query = request.args.get("search", "").strip().lower()

    if search_query:
        quizzes = Quiz.query.filter(Quiz.quiz_name.ilike(f"%{search_query}%")).all()
    else:
        quizzes = Quiz.query.all()

    return render_template("quiz.html", quizzes=quizzes, search_query=search_query)


@app.route("/create_quiz", methods=["POST"])
def create_quiz():
    quiz_name = request.form.get("quiz_name")
    chapter_id = request.form.get("chapter_id")
    quiz_date_str = request.form.get("date")
    duration_str = request.form.get("duration")

    try:
        quiz_date = datetime.strptime(quiz_date_str, "%Y-%m-%d").date() if quiz_date_str else None
        duration = datetime.strptime(duration_str, "%H:%M:%S").time() if duration_str else None

        if not all([quiz_name, chapter_id, quiz_date, duration]):
            flash("All fields are required!", "error")
            return redirect("/quizdashboard")

        new_quiz = Quiz(quiz_name=quiz_name, chapter_id=int(chapter_id), quiz_date=quiz_date, duration=duration)
        db.session.add(new_quiz)
        db.session.commit()
        flash("Quiz added successfully!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "error")

    return redirect("/quizdashboard")

@app.route('/edit_quiz/<int:quiz_id>', methods=['POST'])
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    try:
        quiz.quiz_name = request.form.get('quiz_name')
        quiz.chapter_id = int(request.form.get('chapter_id'))
        quiz.quiz_date = datetime.strptime(request.form.get('date'), "%Y-%m-%d").date()
        quiz.duration = datetime.strptime(request.form.get('duration'), "%H:%M:%S").time()

        db.session.commit()
        flash("Quiz updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "error")

    return redirect("/quizdashboard")

@app.route('/delete_quiz/<int:quiz_id>', methods=['GET'])
def delete_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if quiz:
        Score.query.filter_by(quiz_id=quiz_id).delete()
        db.session.delete(quiz)
        db.session.commit()
        return redirect('/quizdashboard')  
    else:
        return "Quiz not found", 404

 
@app.route('/add_question', methods=['POST'])
def add_question():
    quiz_id = request.form.get('quiz_id')
    question_text = request.form.get('question_text')
    option1 = request.form.get('option1')
    option2 = request.form.get('option2')
    option3 = request.form.get('option3')
    option4 = request.form.get('option4')
    correct_option = request.form.get('correct_answer')   

    if not all([quiz_id, question_text, option1, option2, option3, option4, correct_option]):
        flash("All fields are required!", "error")
        return redirect("/quizdashboard")

    new_question = Question(
        text=question_text,
        quiz_id=int(quiz_id),   
        option1=option1,
        option2=option2,
        option3=option3,
        option4=option4,
        correct_option=correct_option
    )

    try:
        db.session.add(new_question)
        db.session.commit()
        flash("Question added successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "error")

    return redirect("/quizdashboard")

@app.route('/edit_question', methods=['POST'])
def edit_question():
    question_id = request.form.get('question_id')
    quiz_id = request.form.get('quiz_id')
    question_text = request.form.get('question_text')
    option1 = request.form.get('option1')
    option2 = request.form.get('option2')
    option3 = request.form.get('option3')
    option4 = request.form.get('option4')
    correct_option = request.form.get('correct_answer')

    question = Question.query.get_or_404(question_id)

    if not all([question_text, option1, option2, option3, option4, correct_option]):
        flash("All fields are required!", "error")
        return redirect("/quizdashboard")

    try:
        question.text = question_text
        question.option1 = option1
        question.option2 = option2
        question.option3 = option3
        question.option4 = option4
        question.correct_option = correct_option

        db.session.commit()
        flash("Question updated successfully!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "error")

    return redirect("/quizdashboard")


@app.route('/delete_question/<int:question_id>')
def delete_question(question_id):
    try:
        question = Question.query.get_or_404(question_id)
        db.session.delete(question)
        db.session.commit()
        flash("Question deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting question: {e}", "error")

    return redirect("/quizdashboard")

@app.route('/start_quiz/<int:quiz_id>')
def start_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        flash("Quiz not found!", "error")
        return redirect(url_for('user_dash'))

    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    questions_data = [
        {
            "id": q.id,
            "text": q.text,
            "quiz_id": q.quiz_id,
            "options": [q.option1, q.option2, q.option3, q.option4],
            "correct_option": q.correct_option
        }
        for q in questions
    ]

    duration_seconds = (quiz.duration.hour * 3600) + (quiz.duration.minute * 60) + quiz.duration.second

    return render_template("start_quiz.html", 
                           quiz=quiz, 
                           questions=questions_data, 
                           duration=duration_seconds)

@app.route('/submit_quiz/<int:quiz_id>', methods=['POST'])
def submit_quiz(quiz_id):
    user_id = session.get("user_id")
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    if not questions:
        flash("No questions found for this quiz.", "error")
        return redirect("/")

    score = sum(1 for question in questions if str(question.correct_option) == request.form.get(f"q{question.id}"))

    new_score = Score(
        user_id=user_id, 
        quiz_id=quiz_id, 
        score=score, 
        num_questions=len(questions)  
    )
    db.session.add(new_score)
    db.session.commit()

    flash(f"Quiz Completed! Your Score: {score}/{len(questions)}", "success")
    return redirect("/score")


@app.route("/score", methods=["GET"])
def score_dash():
    user_id = session.get('user_id')
    user_role = session.get('user_role', 'user')

    #For admin, show all scores grouped by user
    if user_role == 'admin':
        #  all scores for all user
        all_user_scores = (
            Score.query
            .join(User_Info, Score.user_id == User_Info.id)  
            .join(Quiz)  
            .add_columns(User_Info.full_name, Quiz.quiz_name, Score.quiz_id, Score.score, Score.num_questions, Score.date_created)
            .order_by(User_Info.full_name, Score.date_created.desc())  
            .all()
        )

        #  scores by user name for summary report
        summary_by_user = {}
        for score in all_user_scores:
            user_name = score.full_name
            if user_name not in summary_by_user:
                summary_by_user[user_name] = {
                    "total_attempts": 0,
                    "highest_score": 0,
                    "total_score": 0,
                    "latest_attempt": score.date_created,
                }
            summary_by_user[user_name]["total_attempts"] += 1
            summary_by_user[user_name]["highest_score"] = max(summary_by_user[user_name]["highest_score"], score.score)
            summary_by_user[user_name]["total_score"] += score.score
            summary_by_user[user_name]["latest_attempt"] = max(summary_by_user[user_name]["latest_attempt"], score.date_created)

        #  average scores
        for user_name, data in summary_by_user.items():
            data["average_score"] = round(data["total_score"] / data["total_attempts"], 2) if data["total_attempts"] > 0 else 0

        # Sort summary report by latest attempt date  
        summary_by_user = dict(sorted(summary_by_user.items(), key=lambda item: item[1]["latest_attempt"], reverse=True))

        return render_template("admin_score.html", all_user_scores=all_user_scores, summary_by_user=summary_by_user)
    
    # For user, show only their scores
    else:
        user_scores =(
            Score.query
            .filter_by(user_id=user_id)
            .join(Quiz)   
            .add_columns(Quiz.quiz_name, Score.quiz_id, Score.score, Score.num_questions, Score.date_created)
            .order_by(Score.date_created.desc())  
            .all()
        )

        # scores by quiz name for summary report
        summary_report = {}
        for score in user_scores:
            quiz_name = score.quiz_name
            if quiz_name not in summary_report:
                summary_report[quiz_name] = {
                    "total_attempts": 0,
                    "highest_score": 0,
                    "total_score": 0,
                    "latest_attempt": score.date_created,
                }
            summary_report[quiz_name]["total_attempts"] += 1
            summary_report[quiz_name]["highest_score"] = max(summary_report[quiz_name]["highest_score"], score.score)
            summary_report[quiz_name]["total_score"] += score.score
            summary_report[quiz_name]["latest_attempt"] = max(summary_report[quiz_name]["latest_attempt"], score.date_created)

        # average scores
        for quiz_name, data in summary_report.items():
            data["average_score"] = round(data["total_score"] / data["total_attempts"], 2) if data["total_attempts"] > 0 else 0

        # summary report by latest attempt date (newest first)
        summary_report = dict(sorted(summary_report.items(), key=lambda item: item[1]["latest_attempt"], reverse=True))

        return render_template("Scores.html", user_scores=user_scores, summary_report=summary_report)

def generate_plot():
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    encoded_img = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()
    plt.clf()
    return encoded_img

@app.route("/user_stats")
def user_stats():
    user_id = session.get("user_id")
    user_role = session.get("user_role", 'user')

    # For user, show only their own stats
    if user_role == 'user':
        user_scores = (
            db.session.query(Subject.subject_name, db.func.sum(Score.score))
            .select_from(Score)
            .filter(Score.user_id == user_id)   
            .join(Quiz, Score.quiz_id == Quiz.id)  
            .join(Chapter, Quiz.chapter_id == Chapter.id)   
            .join(Subject, Chapter.subject_id == Subject.id)  
            .group_by(Subject.subject_name)
            .all()
        )
    
    # For admin, show all users' stats
    else:
        user_scores = (
            db.session.query(Subject.subject_name, db.func.sum(Score.score))
            .select_from(Score)
            .join(Quiz, Score.quiz_id == Quiz.id)   
            .join(Chapter, Quiz.chapter_id == Chapter.id)   
            .join(Subject, Chapter.subject_id == Subject.id)  
            .group_by(Subject.subject_name)
            .all()
        )
    subjects = [subject for subject, _ in user_scores]
    scores = [score for _, score in user_scores]

    # Bar Chart
    plt.figure(figsize=(6, 4))
    plt.bar(subjects, scores, color='skyblue')
    plt.xlabel("Subjects")
    plt.ylabel("Total Score")
    plt.title("User Scores by Subject")
    bar_chart = generate_plot()

    # Pie Chart
    plt.figure(figsize=(5, 5))
    plt.pie(scores, labels=subjects, autopct='%1.1f%%', colors=['lightblue', 'lightgreen', 'lightcoral', 'gold'])
    plt.title("Score Distribution by Subject")
    pie_chart = generate_plot()

    return render_template("user_summary.html", bar_chart=bar_chart, pie_chart=pie_chart)


@app.route("/admin_stats")
def admin_stats():
    user_rankings = db.session.query(User_Info.full_name, db.func.sum(Score.score)).join(Score).group_by(User_Info.id).order_by(db.func.sum(Score.score).desc()).limit(5).all()
    
    users = [user for user, _ in user_rankings]
    scores = [score for _, score in user_rankings]
    
    # Bar Chart
    plt.figure(figsize=(6, 4))
    plt.bar(users, scores, color='orange')
    plt.xlabel("Users")
    plt.ylabel("Total Score")
    plt.title("Top 5 Users by Score")
    bar_chart = generate_plot()
    
    subject_avg_scores = db.session.query(Subject.subject_name, db.func.avg(Score.score))\
    .join(Chapter, Subject.id == Chapter.subject_id)\
    .join(Quiz, Chapter.id == Quiz.chapter_id)\
    .join(Score, Quiz.id == Score.quiz_id)\
    .group_by(Subject.subject_name).all()

    
    subjects = [subject for subject, _ in subject_avg_scores]
    avg_scores = [score for _, score in subject_avg_scores]
    
    # Pie Chart
    plt.figure(figsize=(5, 5))
    plt.pie(avg_scores, labels=subjects, autopct='%1.1f%%', colors=['lightcoral', 'lightblue', 'lightgreen', 'gold'])
    plt.title("Average Score Distribution by Subject")
    pie_chart = generate_plot()
    
    return render_template("admin_summary.html", bar_chart=bar_chart, pie_chart=pie_chart)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")   



