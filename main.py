from flask import Flask, render_template

app = Flask(__name__)

problems = [{
    'name': 'FizzBuzz',
    'description':
    'Crear una función que reciba un número entero y retorne Fizz si es multiplo de 5, Buzz es multiplo de 3, FizzBuzz es multiplo de ambos o su representación en cadena en cualquier otro caso',
    'languages': ['Python', 'Java'],
    'forbidden_words': ['if'],
    'recursive': True,
    'input_params': [{
        'name': 'n',
        'type': 'int'
    }],
    'output_type': 'str'
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
    'int'
}, {
    'name': 'Factorial',
    'description':
    'Escribe una función que permita calcular el factorial de un numero entero',
    'languages': ['Python', 'Java'],
    'forbidden_words': [],
    'recursive': False,
    'input_params': [{
        'name': 'n',
        'type': 'int'
    }],
    'output_type': 'int'
}]


@app.route('/')
def index():
    return 'para ver los problemas ir a /problems'


@app.route('/problems')
def show_problems():
    return render_template('problems.html', problems_arr=problems)


@app.route('/getproblems')
def get_problems():
    return (problems)


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


if __name__ == '__main__':
    app.run(debug=True)
