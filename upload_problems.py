import json
from main import app, db
from models import Problem

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
        'type': 'list[int]'
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
with app.app_context():
    db.create_all()
    for problem_data in problems:
        problem = Problem(
            name=problem_data['name'],
            description=problem_data['description'],
            languages=json.dumps(problem_data['languages']),
            forbidden_words=json.dumps(
                problem_data['forbidden_words']),
            recursive=problem_data['recursive'],
            input_params=json.dumps(
                problem_data['input_params']),
            output_type=problem_data['output_type'],
            examples=json.dumps(problem_data['examples']),
            test_cases=json.dumps(
                problem_data['test_cases'])
        )
        db.session.add(problem)
    db.session.commit()
