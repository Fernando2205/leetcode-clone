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
from urllib.parse import urlparse
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask import Flask, redirect, render_template, request, url_for, flash
from sqlalchemy.orm import joinedload
from models import Solution, User, Problem
from forms import LoginForm, SignupForm
from db import db


app = Flask(__name__)

secret_key = os.urandom(24)
app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    """
    Loads the user with the specified ID.
    """
    return User.query.get(int(user_id))


@app.before_request
def create_tables() -> None:
    """
    Creates the database tables if they do not exist.
    """
    if not hasattr(app, 'tables_created'):
        db.create_all()
        app.tables_created = True


@app.route('/', methods=['GET', 'POST'])
def login():
    """
    Logs in the user.
    """
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
    """
    Registers a new user.
    """
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
    """
    Logs out the current user.
    """
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

    if problem.recursive is False and check_recursion(solution_code, 'solution'):
        return render_template('evaluation_result.html', result="Error: No se admite solución recursiva", problem=problem, is_string=is_string)

    test_cases = json.loads(problem.test_cases)
    input_params = json.loads(problem.input_params)
    if language == 'Python':
        result = evaluate_python_code(solution_code, test_cases)
    elif language == 'Java':
        result = evaluate_java_code(solution_code, test_cases, input_params)
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


@app.route('/history')
@login_required
def history():
    """
    Displays the history of solutions submitted by the user.
    """
    sort_order = request.args.get('sort', 'desc')  # Default to descending

    query = Solution.query.options(joinedload(
        Solution.problem)).filter_by(user_id=current_user.id)

    if sort_order == 'asc':
        solutions = query.order_by(Solution.timestamp.asc()).all()
    else:
        solutions = query.order_by(Solution.timestamp.desc()).all()

    for solution in solutions:
        solution.result = json.loads(solution.result)
    return render_template('history.html', solutions=solutions, current_sort=sort_order)


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
                    text=True,
                    check=False
                )

                if process.returncode != 0:
                    raise Exception(process.stderr)

                # Get output and convert to appropriate type
                user_output = process.stdout.strip()
                converted_output = convert_output(user_output, expected_output)
                passed = False

                if isinstance(expected_output, list):
                    passed = sorted(converted_output) == sorted(
                        expected_output)
                else:
                    passed = converted_output == expected_output

                results.append({
                    'input': test_case['input'],
                    'expected_output': expected_output,
                    'user_output': converted_output,
                    'passed': passed
                })

            except Exception as e:
                results.append({
                    'input': test_case['input'],
                    'expected_output': expected_output,
                    'user_output': str(e),
                    'passed': False
                })

    return results


def evaluate_java_code(solution_code: str, test_cases: list, input_params: list) -> list:
    """Evaluates Java code with test cases"""
    results = []

    with tempfile.TemporaryDirectory() as temp_dir:
        # Write Solution.java
        solution_path = os.path.join(temp_dir, 'Solution.java')
        with open(solution_path, 'w', encoding='utf-8') as f:
            f.write(solution_code)

        # Write Main.java with wrapper
        wrapper_code = wrap_java_code(input_params)
        main_path = os.path.join(temp_dir, 'Main.java')
        with open(main_path, 'w', encoding='utf-8') as f:
            f.write(wrapper_code)

        # Compile Java files
        compile_process = subprocess.run(
            ['javac', solution_path, main_path],
            capture_output=True,
            text=True,
            check=False
        )

        # Check compilation errors
        if compile_process.returncode != 0:
            return [{
                'input': '',
                'expected_output': '',
                'user_output': compile_process.stderr,
                'passed': False
            }]

        # Run tests
        for test_case in test_cases:
            try:
                input_data = [str(arg) for arg in test_case['input']]
                expected_output = test_case['expected_output']

                # Run Java code
                process = subprocess.run(
                    ['java', '-cp', temp_dir, 'Main'] + input_data,
                    capture_output=True,
                    text=True,
                    check=False
                )

                if process.returncode != 0:
                    raise Exception(process.stderr)

                # Convert output and compare
                user_output = process.stdout.strip()
                converted_output = convert_output(user_output, expected_output)
                passed = False

                if isinstance(expected_output, list):
                    passed = sorted(converted_output) == sorted(
                        expected_output)
                else:
                    passed = converted_output == expected_output

                results.append({
                    'input': test_case['input'],
                    'expected_output': expected_output,
                    'user_output': converted_output,
                    'passed': passed
                })

            except Exception as e:
                results.append({
                    'input': test_case['input'],
                    'expected_output': expected_output,
                    'user_output': str(e),
                    'passed': False
                })

    return results


def wrap_ruby_code(solution_code: str) -> str:
    """
    Wraps the Ruby solution code in a script that handles command line arguments.
    """
    normalized_code = solution_code.replace('\r\n', '\n')

    return f"""
{normalized_code}

# Convert command line arguments to appropriate types
args = ARGV.map do |arg|
    case arg
    when /^\\[.*\\]$/  # Array
        begin
            eval(arg)
        rescue
            arg
        end
    when /^-?\\d+$/    # Integer (including negative)
        arg.to_i
    when /^-?\\d*\\.\\d+$/  # Float (including negative)
        arg.to_f
    when 'true', 'false'  # Boolean
        arg == 'true'
    else              # String or other
        arg
    end
end

# Call solution with converted arguments
result = solution(*args)

# Handle array output
if result.is_a?(Array)
    result = result.sort if result.all? do |item|
        item.is_a?(Integer) || item.is_a?(Float)
    end
end

puts result.to_s
"""


def convert_output(user_output: str, expected_type: Any) -> Any:
    """
    Converts the Ruby output string to the expected Python type
    """
    try:
        if isinstance(expected_type, list):
            if user_output.startswith('[') and user_output.endswith(']'):
                items = user_output[1:-1].split(',')
                if items and items[0].strip():
                    if isinstance(expected_type[0], int):
                        return [int(x.strip()) for x in items]
                    if isinstance(expected_type[0], float):
                        return [float(x.strip()) for x in items]

                    return [x.strip() for x in items]
                return []
        elif isinstance(expected_type, bool):
            return user_output.lower() == 'true'
        elif isinstance(expected_type, int):
            return int(user_output)
        elif isinstance(expected_type, float):
            return float(user_output)
    except (ValueError, IndexError):
        return user_output

    return user_output


def wrap_java_code(input_params: list) -> str:
    """
    Wraps the Java solution code in a Main class with a main method.
    """
    param_conversions = []
    solution_params = []

    for i, param in enumerate(input_params):
        param_name = f"parsed_arg_{i}"

        if param['type'] == 'list[int]':
            param_conversions.append(f"""
            String[] arrayStr = args[{i}].substring(1, args[{i}].length()-1).split(",");
            int[] {param_name};
            if (arrayStr.length == 1 && arrayStr[0].trim().isEmpty()) {{
                {param_name} = new int[0];  // Handle empty array case
            }} else {{
                {param_name} = new int[arrayStr.length];
                for (int j = 0; j < arrayStr.length; j++) {{
                    {param_name}[j] = Integer.parseInt(arrayStr[j].trim());
                }}
            }}""")
        else:
            type_conversions = {
                'int': f"int {param_name} = Integer.parseInt(args[{i}]);",
                'str': f"String {param_name} = args[{i}];",
                'bool': f"boolean {param_name} = Boolean.parseBoolean(args[{i}]);",
                'float': f"float {param_name} = Float.parseFloat(args[{i}]);"
            }
            param_conversions.append(type_conversions.get(
                param['type'], f"String {param_name} = args[{i}];"))

        solution_params.append(param_name)

    return f"""
public class Main {{
    public static void main(String[] args) {{
        try {{
            Solution solution = new Solution();
            {chr(10).join(param_conversions)}

            Object result = solution.solution({', '.join(solution_params)});
            System.out.println(result);
        }} catch (Exception e) {{
            System.err.println(e.getMessage());
        }}
    }}
}}"""


def validate_forbidden_words(solution_code: str, forbidden_words: str) -> bool:
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
