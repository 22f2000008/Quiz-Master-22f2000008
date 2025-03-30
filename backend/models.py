from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def get_id(self):
        return self.email


class User_Info(db.Model):
    __tablename__ = "user_info"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    full_name = db.Column(db.String, nullable=False)
    qualification = db.Column(db.String, nullable=False)
    dob = db.Column(db.String, nullable=False)

    # Relationship to Score
    scores = db.relationship("Score", backref="user", cascade="all, delete-orphan")

    def get_id(self):
        return self.email


class Subject(db.Model):
    __tablename__ = "subject"
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String, nullable=False, unique=True)

    # Relationship to Chapters
    chapters = db.relationship("Chapter", backref="subject", cascade="all, delete-orphan")

     


class Chapter(db.Model):
    __tablename__ = "chapter"
    id = db.Column(db.Integer, primary_key=True)
    chapter_name = db.Column(db.String, nullable=False)
    no_of_question = db.Column(db.Integer, nullable=False)

    # Foreign Key linking to Subject
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete="CASCADE"), nullable=False)

    # Relationship to Quizzes
    quizzes = db.relationship("Quiz", backref="chapter", cascade="all, delete-orphan")

    


class Quiz(db.Model):
    __tablename__ = "quiz"
    id = db.Column(db.Integer, primary_key=True)
    quiz_name = db.Column(db.String(100), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id', ondelete="CASCADE"), nullable=False)
    quiz_date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Time, nullable=False)

    # Relationship to Questions
    questions = db.relationship('Question', backref='quiz', cascade="all, delete", lazy="select")

    # Relationship to Score
    scores = db.relationship("Score", backref="quiz", cascade="all, delete-orphan")

     


class Question(db.Model):
    __tablename__ = "question"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"), nullable=False)

    option1 = db.Column(db.String(100), nullable=False)
    option2 = db.Column(db.String(100), nullable=False)
    option3 = db.Column(db.String(100), nullable=False)
    option4 = db.Column(db.String(100), nullable=False)
    correct_option = db.Column(db.String(50), nullable=False)

   


class Score(db.Model):
    __tablename__ = "score"
    id = db.Column(db.Integer, primary_key=True)

     
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id', ondelete="CASCADE"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"), nullable=False)

    score = db.Column(db.Integer, nullable=False)
    num_questions = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())

    
