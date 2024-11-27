"""
main.py

This file contains a Flask web application that allows users
to solve programming problems and submit their solutions for evaluation.

"""
import os
import re
import subprocess
import json
import tempfile
from typing import Any
from flask import Flask, redirect, render_template, request, url_for, flash
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from db import db
from sqlalchemy.orm import joinedload
from urllib.parse import urlparse
from models import Solution, User, Problem
from forms import LoginForm, SignupForm


app = Flask(__name__)

secret_key = os.urandom(24)
app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def loadUser(user_id):
    return User.query.get(int(user_id))


@app.before_request
def create_tables() -> None:
    if not hasattr(app, 'tables_created'):
        db.create_all()
        app.tables_crrated = True


@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('show_problems'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Nombre de usuario o contraseña inválidos')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('show_problems')
        return redirect(next_page)
    return render_template('login.html', title='Ingresar', form=form)


@app.route('/signup/', methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('show_problems'))
    form = SignupForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first() is not None:
            flash('Este nombre de usuario ya existe')
            return redirect(url_for('signup'))
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Felicitaciones, ahora estás registrado!')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Registrarse', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/problems')
@login_required
def show_problems():
    """
    Displays the list of available problems.
    """
    problems = Problem.query.all()
    return render_template('problems.html', problems_arr=problems)


@app.route('/problem/<int:problem_id>')
@login_required
def problem_detail(problem_id):
    """
    Displays the details of a specific problem.
    """
    problem = Problem.query.get_or_404(problem_id)
    problem.languages = json.loads(problem.languages)
    problem.forbidden_words = json.loads(problem.forbidden_words)
    problem.input_params = json.loads(problem.input_params)
    problem.examples = json.loads(problem.examples)
    problem.test_cases = json.loads(problem.test_cases)
    return render_template('problem_detail.html', problem=problem)


@app.route('/submit_solution', methods=['POST'])
@login_required
def submit_solution():
    """
    Processes and evaluates the solution submitted by the user.
    """
    problem_id = request.form.get('problem_id')
    solution_code = request.form.get('solution_code')
    language = request.form.get('language')

    problem = Problem.query.get_or_404(problem_id)
    if not problem:
        return "Problema no encontrado", 404

    forbidden_words = json.loads(problem.forbidden_words)
    for forbidden_word in forbidden_words:
        if solution_code and re.search(r'\b' + re.escape(forbidden_word) + r'\b', solution_code):
            return render_template('evaluation_result.html', result=f"Error: Uso de palabra prohibida '{forbidden_word}'", problem=problem, is_string=is_string)

    if problem.recursive == False and check_recursion(solution_code, 'solution'):
        return render_template('evaluation_result.html', result="Error: No se admite solución recursiva", problem=problem, is_string=is_string)

    test_cases = json.loads(problem.test_cases)
    if language == 'Python':
        result = evaluate_python_code(solution_code, test_cases)
    # elif language == 'Java':
    #     result = evaluate_java_code(solution_code, test_cases, input_params)
    elif language == 'Ruby':
        result = evaluate_ruby_code(solution_code, test_cases)
    else:
        result = "Lenguaje no soportado"

    # Store solution
    solution = Solution(
        user_id=current_user.id,
        problem_id=problem.id,
        code=solution_code,
        result=json.dumps(result))

    db.session.add(solution)
    db.session.commit()

    return render_template('evaluation_result.html', result=result, problem=problem, is_string=is_string)


@app.route('/register', methods=['GET'])
def show_register():
    return render_template('register.html')


@app.route('/history')
@login_required
def history():
    """
    Displays the history of solutions submitted by the user.
    """
    solutions = Solution.query.options(joinedload(
        Solution.problem)).filter_by(user_id=current_user.id).all()
    for solution in solutions:
        solution.result = json.loads(solution.result)
    return render_template('history.html', solutions=solutions)


@app.route('/solution/<int:solution_id>')
@login_required
def view_solution(solution_id):
    """
    Displays the details of a specific solution.
    """
    solution = Solution.query.options(joinedload(
        Solution.problem)).get_or_404(solution_id)
    solution.result = json.loads(solution.result)
    return render_template('view_solution.html', solution=solution,)


def evaluate_python_code(solution_code, test_cases):
    """
    Evaluates the solution code in Python using test cases.
    """
    results = []
    for test_case in test_cases:
        try:
            # We use exec() safely in a controlled environment
            exec_globals = {}
            exec(solution_code, exec_globals)

            # Call the solution() function with the test case parameters
            output = exec_globals['solution'](*test_case["input"])
            results.append({
                "input": test_case["input"],
                "expected_output": test_case["expected_output"],
                "user_output": output,
                "passed": output == test_case["expected_output"]
            })
        except Exception as e:
            results.append({
                "input": test_case["input"],
                "expected_output": test_case["expected_output"],
                "user_output": str(e),
                "passed": False
            })

    return results


def evaluate_ruby_code(solution_code, test_cases):
    """
    Evaluates Ruby code with test cases
    """
    results = []

    with tempfile.TemporaryDirectory() as temp_dir:
        # Write solution code to file
        solution_file_path = os.path.join(temp_dir, 'solution.rb')
        wrapped_code = wrap_ruby_code(solution_code)

        with open(solution_file_path, 'w', encoding='utf-8') as f:
            f.write(wrapped_code)

        # Run tests
        for test_case in test_cases:
            try:
                input_data = [str(arg) for arg in test_case['input']]
                expected_output = test_case['expected_output']

                # Run Ruby code
                process = subprocess.run(
                    ['ruby', solution_file_path] + input_data,
                    capture_output=True,
                    text=True
                )

                if process.returncode != 0:
                    raise Exception(process.stderr)

                # Get output and convert to appropriate type
                user_output = process.stdout.strip()
                converted_output = convert_output(user_output, expected_output)

                results.append({
                    'input': test_case['input'],
                    'expected_output': expected_output,
                    'user_output': converted_output,
                    'passed': converted_output == expected_output
                })

            except Exception as e:
                results.append({
                    'input': test_case['input'],
                    'expected_output': expected_output,
                    'user_output': str(e),
                    'passed': False
                })

    return results


def wrap_ruby_code(solution_code):
    return f"""
{solution_code}

# Ensure first argument is converted to integer
n = ARGV[0].to_i
result = solution(n)
puts result.to_s
"""


def convert_output(user_output: str, expected_type: Any) -> Any:
    """
    Converts the Ruby output string to the expected Python type
    """
    if isinstance(expected_type, bool):
        return user_output.lower() == 'true'
    elif isinstance(expected_type, int):
        return int(user_output)
    elif isinstance(expected_type, float):
        return float(user_output)
    return user_output


def validate_forbidden_words(solution_code, forbidden_words):
    """
    Validates if the solution code contains forbidden words.
    """
    for word in forbidden_words:
        if word in solution_code:
            return False, f"Uso de palabra prohibida: {word}"
    return True, ""


def check_recursion(solution_code, function_name):
    """
    Checks if the solution code uses recursion.
    """
    return solution_code.count(f"{function_name}(") >= 2


def is_string(value):
    """
    Checks if the value is a string.
    """
    return isinstance(value, str)


if __name__ == '__main__':
    app.run(debug=True)
