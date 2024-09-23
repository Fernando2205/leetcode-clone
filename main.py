"""
main.py

This file contains a Flask web application that allows users to solve programming problems and submit their solutions for evaluation. The application includes the following functionalities:

- Display a list of available problems.
- Display details of a specific problem.
- Validate and evaluate solutions submitted by users.

Functions:
- validate_forbidden_words(solution_code, forbidden_words): 
- check_recursion(solution_code, function_name): 
- is_string(value): 
- index(): 
- show_problems(): 
- problem_detail(problem_name): Displays the details of a specific problem.
- submit_solution(): 
- evaluate_python_code(solution_code, test_cases): 
- evaluate_java_code(solution_code, test_cases): 
Variables:
- app: Instance of the Flask application.
- problems: List of available programming problems.
"""
import re
from flask import Flask, render_template, request

app = Flask(__name__)

problems = [{
    'name': 'FizzBuzz',
    'description':
    'Crear una función que reciba un número entero y retorne Fizz si es multiplo de 3, Buzz si es multiplo de 5, FizzBuzz si es multiplo de ambos o su representación en cadena en cualquier otro caso',
    'languages': ['Python', 'Java'],
    'forbidden_words': ['if'],
    'recursive': True,
    'input_params': [{
        'name': 'n',
        'type': 'int'
    }],
    'output_type': 'str',
    'examples': {
        'correct': {
            'input': '15',
            'output': '"FizzBuzz"'
        },
        'incorrect': {
            'input': '7',
            'output': '"7"'
        }
    },
    'test_cases': [
        {"input": [1176711096], "expected_output": "Fizz"},
        {"input": [5], "expected_output": "Buzz"},
        {"input": [589958805], "expected_output": "FizzBuzz"},
        {"input": [1], "expected_output": "1"},
        {"input": [998160272], "expected_output": "998160272"}
    ]
}, {
    'name':
    'Binary Search',
    'description':
    'Dada una lista ordenada de enteros positivos y un objetivo, implementar busqueda binaria para obtener el indice del objetivo dentro de la lista, en caso de no existir retornar -1',
    'languages': ['Python', 'Java'],
    'forbidden_words': [],
    'recursive':
    True,
    'input_params': [{
        'name': 'arr',
        'type': 'List[int]'
    }, {
        'name': 'target',
        'type': 'int'
    }],
    'output_type':
    'int',
    'examples': {
        'correct': {
            'input': '[1, 2, 3, 4, 5], 3',
            'output': '2'
        },
        'incorrect': {
            'input': '[1, 2, 3, 4, 5], 6',
            'output': '-1'
        }
    },
    'test_cases': [
        {"input": [[1, 2, 3, 4, 5], 3],
            "expected_output": 2},
        {"input": [[1, 2, 3, 4, 5], 6], "expected_output": -1},
        {"input": [[], 1], "expected_output": -1},
    ]


}, {
    'name': 'Factorial',
    'description':
    'Escribe una función que permita calcular el factorial de un numero entero positivo, si la entrada es negativa retornar -1',
    'languages': ['Python', 'Java'],
    'forbidden_words': [],
    'recursive': False,
    'input_params': [{
        'name': 'n',
        'type': 'int'
    }],
    'output_type': 'int',
    'examples': {
        'correct': {
            'input': '5',
            'output': '120'
        },
        'incorrect': {
            'input': '-6',
            'output': '-1'
        }
    },
    'test_cases': [
        {"input": [5], "expected_output": 120},
        {"input": [0], "expected_output": 1},
        {"input": [-6], "expected_output": -1},
    ]


}]


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
    return f"{function_name}(" in solution_code


def is_string(value):
    """
    Checks if the value is a string.
    """
    return isinstance(value, str)


@app.route('/')
def index():
    """
    Endpoint for login.
    """
    return 'Endpoint para el login'


@app.route('/problems')
def show_problems():
    """
    Displays the list of available problems.
    """
    return render_template('problems.html', problems_arr=problems)


@app.route('/problem/<problem_name>')
def problem_detail(problem_name):

    problem = None
    for p in problems:
        if p['name'] == problem_name:
            problem = p
            break

    if not problem:
        return "Problema no encontrado", 404

    return render_template('problem_detail.html', problem=problem)


@app.route('/submit_solution', methods=['POST'])
def submit_solution():
    """
    Processes and evaluates the solution submitted by the user.
    """
    problem_name = request.form.get('problem_name')
    solution_code = request.form.get('solution_code')
    language = request.form.get('language')

    problem = next((p for p in problems if p['name'] == problem_name), None)
    if not problem:
        return "Problema no encontrado", 404

    for forbidden_word in problem['forbidden_words']:
        if solution_code and re.search(r'\b' + re.escape(forbidden_word) + r'\b', solution_code):
            return render_template('evaluation_result.html', result=f"Error: Uso de palabra prohibida '{forbidden_word}'", problem=problem, is_string=is_string)

    # Use problem test_cases
    test_cases = problem['test_cases']

    result = None
    if language == '':
        return render_template('evaluation_result.html', result="Error: No se ha especificado el lenguaje", problem=problem, is_string=is_string)
    if language == 'Python':
        result = evaluate_python_code(solution_code, test_cases)
        return render_template('evaluation_result.html', result=result, problem=problem, is_string=is_string)
    if language == 'Java':
        return render_template('evaluation_result.html', result="Error: El lenguaje aú no está soportado :)", problem=problem, is_string=is_string)


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


# def evaluate_java_code(solution_code, test_cases):
#     """
#     Evaluates the solution code in Java (to be implemented).

#     """


if __name__ == '__main__':
    app.run(debug=True)
