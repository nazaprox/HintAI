
import uuid
from datetime import datetime


class HelpMeSession:

    def __init__(self):

        self.session_id = str(uuid.uuid4())

        self.created_at = datetime.now().isoformat()

        # Fichiers
        self.exercise_file = None
        self.exercise_type = None

        self.student_work_file = None
        self.student_work_type = None

        self.work_skipped = False

        # Analyses
        self.exercise_analysis = None
        self.work_analysis = None

        # Progression pédagogique
        self.current_hint = 0

        self.hints = []

        self.student_questions = []

        self.tutor_answers = []

        # Résolution
        self.solution = None

        # Correction
        self.correction = None

        # Evaluation
        self.evaluation = None

        self.completed = False

        self.skill = None


    def set_exercise(
        self,
        file_name,
        file_type
    ):

        self.exercise_file = file_name
        self.exercise_type = file_type


    def set_student_work(
        self,
        file_name,
        file_type
    ):

        self.student_work_file = file_name
        self.student_work_type = file_type
        self.work_skipped = False


    def skip_student_work(self):

        self.student_work_file = None
        self.student_work_type = None
        self.work_skipped = True


    def add_hint(self, hint):

        self.hints.append(hint)

        self.current_hint = len(
            self.hints
        )


    def add_question(
        self,
        question,
        answer
    ):

        self.student_questions.append(
            question
        )

        self.tutor_answers.append(
            answer
        )


    def complete(self):

        self.completed = True


    def to_dict(self):

        return {

            "session_id":
            self.session_id,

            "created_at":
            self.created_at,

            "exercise_file":
            self.exercise_file,

            "exercise_type":
            self.exercise_type,

            "student_work_file":
            self.student_work_file,

            "student_work_type":
            self.student_work_type,

            "work_skipped":
            self.work_skipped,

            "exercise_analysis":
            self.exercise_analysis,

            "work_analysis":
            self.work_analysis,

            "current_hint":
            self.current_hint,

            "hints":
            self.hints,

            "student_questions":
            self.student_questions,

            "tutor_answers":
            self.tutor_answers,

            "solution":
            self.solution,

            "correction":
            self.correction,

            "evaluation":
            self.evaluation,

            "skill":
            self.skill,

            "completed":
            self.completed

        }


# ==========================================
# SESSION LEARN A CONCEPT
# ==========================================


class LearningSession:

    def __init__(self):

        self.session_id = str(uuid.uuid4())

        self.created_at = datetime.now().isoformat()

        self.concept = None

        self.class_level = None

        self.example_exercises = []

        self.student_work = None

        self.explanation = None

        self.guided_exercise = None

        self.hints = []

        self.evaluation = None

        self.skill = None

        self.completed = False


    def set_concept(
        self,
        concept
    ):

        self.concept = concept


    def set_class_level(
        self,
        class_level
    ):

        self.class_level = class_level


    def add_example(
        self,
        exercise
    ):

        self.example_exercises.append(
            exercise
        )


    def set_student_work(
        self,
        work
    ):

        self.student_work = work


    def complete(self):

        self.completed = True


    def to_dict(self):

        return {

            "session_id":
            self.session_id,

            "created_at":
            self.created_at,

            "concept":
            self.concept,

            "class_level":
            self.class_level,

            "example_exercises":
            self.example_exercises,

            "student_work":
            self.student_work,

            "explanation":
            self.explanation,

            "guided_exercise":
            self.guided_exercise,

            "hints":
            self.hints,

            "evaluation":
            self.evaluation,

            "skill":
            self.skill,

            "completed":
            self.completed

        }
