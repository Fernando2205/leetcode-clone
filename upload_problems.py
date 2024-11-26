import json
from main import app, db
from models import Problem

problems = [{

    'name': 'FizzBuzz',
    'description':
    'Crear una función que reciba un número entero y retorne Fizz si es multiplo de 3, Buzz si es multiplo de 5, FizzBuzz si es multiplo de ambos o su representación en cadena en cualquier otro caso',
    'languages': ['Python', 'Java', 'Ruby'],
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
    'languages': ['Python', 'Java', 'Ruby'],
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
    'languages': ['Python', 'Java', 'Ruby'],
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


}, {
    'name': 'Integer to Roman',
    'description':
    'Convertir un número entero entre 1 y 3999 a su representación en números romanos.',
    'languages': ['Python', 'Java', 'Ruby'],
    'forbidden_words': [],
    'recursive': False,
    'input_params': [{
        'name': 'num',
        'type': 'int'
    }],
    'output_type': 'str',
    'examples': {
        'correct': {
            'input': '1994',
            'output': '"MCMXCIV"'
        },
        'incorrect': {
            'input': '4000',
            'output': '""'
        }
    },
    'test_cases': [
        {"input": [1994], "expected_output": "MCMXCIV"},
        {"input": [58], "expected_output": "LVIII"},
        {"input": [9], "expected_output": "IX"},
    ]
}, {
    'name': 'Roman to Integer',
    'description':
    'Convertir una cadena de números romanos a su representación en números enteros.',
    'languages': ['Python', 'Java', 'Ruby'],
    'forbidden_words': [],
    'recursive': False,
    'input_params': [{
        'name': 's',
        'type': 'str'
    }],
    'output_type': 'int',
    'examples': {
        'correct': {
            'input': '"MCMXCIV"',
            'output': '1994'
        },
        'incorrect': {
            'input': '"MMMM"',
            'output': '-1'
        }
    },
    'test_cases': [
        {"input": ["MCMXCIV"], "expected_output": 1994},
        {"input": ["LVIII"], "expected_output": 58},
        {"input": ["IX"], "expected_output": 9},
    ]
}, {
    'name': 'Money (USD) to English',
    'description':
    'Convertir una cantidad de dinero en dólares a su representación en palabras en inglés.',
    'languages': ['Python', 'Java', 'Ruby'],
    'forbidden_words': [],
    'recursive': False,
    'input_params': [{
        'name': 'amount',
        'type': 'float'
    }],
    'output_type': 'str',
    'examples': {
        'correct': {
            'input': '1234.56',
            'output': '"one thousand two hundred thirty-four dollars and fifty-six cents"'
        },
        'incorrect': {
            'input': '-1',
            'output': '""'
        }
    },
    'test_cases': [
        {"input": [
            1234.56], "expected_output": "one thousand two hundred thirty-four dollars and fifty-six cents"},
        {"input": [0.99], "expected_output": "ninety-nine cents"},
        {"input": [1000000], "expected_output": "one million dollars"},
    ]
}, {
    'name': 'Palindromo',
    'description':
    'Determinar si una cadena es un palíndromo. Un palindromo es una palabra o frase cuyas letras están dispuestas de tal manera que resulta la misma leída de izquierda a derecha que de derecha a izquierda',
    'languages': ['Python', 'Java', 'Ruby'],
    'forbidden_words': [],
    'recursive': False,
    'input_params': [{
        'name': 's',
        'type': 'str'
    }],
    'output_type': 'bool',
    'examples': {
        'correct': {
            'input': '"racecar"',
            'output': 'true'
        },
        'incorrect': {
            'input': '"hello"',
            'output': 'false'
        }
    },
    'test_cases': [
        {"input": ["racecar"], "expected_output": True},
        {"input": ["hello"], "expected_output": False},
        {"input": ["madam"], "expected_output": True},
    ]
}, {
    'name': 'Sum of Two Numbers',
    'description':
    'Dada una lista de números y un objetivo, encontrar dos números en la lista que sumen el objetivo.',
    'languages': ['Python', 'Java', 'Ruby'],
    'forbidden_words': [],
    'recursive': False,
    'input_params': [{
        'name': 'nums',
        'type': 'list[int]'
    }, {
        'name': 'target',
        'type': 'int'
    }],
    'output_type': 'list[int]',
    'examples': {
        'correct': {
            'input': '[2, 7, 11, 15], 9',
            'output': '[2, 7]'
        },
        'incorrect': {
            'input': '[1, 2, 3], 6',
            'output': '[]'
        }
    },
    'test_cases': [
        {"input": [[2, 7, 11, 15], 9], "expected_output": [2, 7]},
        {"input": [[1, 2, 3], 6], "expected_output": []},
        {"input": [[3, 3], 6], "expected_output": [3, 3]},
    ]
}, {'name': 'Valid Number',
    'description':
    'Dada una cadena retornar true o false si es un número válido teniendo en cuenta que un número es valido unicamente si es un numero entero, decimal o elevado a una potencia usando e como indicador de potencia.',
    'languages': ['Python', 'Java', 'Ruby'],
    'forbidden_words': [],
    'recursive': False,
    'input_params': [{
        'name': 's',
        'type': 'str'
    }],
    'output_type': 'bool',
    'examples': {
        'correct': {
            'input': '"2e10"',
            'output': 'true'
        },
        'incorrect': {
            'input': '"abc"',
            'output': 'false'
        }
    },
    'test_cases': [
        {"input": ["2"], "expected_output": True},
        {"input": ["-0.1"], "expected_output": True},
        {"input": ["-123.456e789"], "expected_output": True},
        {"input": ["abc"], "expected_output": False},
        {"input": ["e3"], "expected_output": False},
        {"input": ["-+3"], "expected_output": False},
    ]
    }, {
    'name': 'Valid Parentheses',
    'description':
    'Determinar si una cadena de paréntesis es válida.',
    'languages': ['Python', 'Java', 'Ruby'],
    'forbidden_words': [],
    'recursive': False,
    'input_params': [{
        'name': 's',
        'type': 'str'
    }],
    'output_type': 'bool',
    'examples': {
        'correct': {
            'input': '"()"',
            'output': 'true'
        },
        'incorrect': {
            'input': '"(]"',
            'output': 'false'
        }
    },
    'test_cases': [
        {"input": ["()"], "expected_output": True},
        {"input": ["(]"], "expected_output": False},
        {"input": ["()[]{}"], "expected_output": True},
    ]
}]

with app.app_context():
    db.create_all()
    for problem_data in problems:
        problem = Problem.query.filter_by(name=problem_data['name']).first()
        if problem:
            problem.description = problem_data['description']
            problem.languages = json.dumps(problem_data['languages'])
            problem.forbidden_words = json.dumps(
                problem_data['forbidden_words'])
            problem.recursive = problem_data['recursive']
            problem.input_params = json.dumps(problem_data['input_params'])
            problem.output_type = problem_data['output_type']
            problem.examples = json.dumps(problem_data['examples'])
            problem.test_cases = json.dumps(problem_data['test_cases'])
        else:
            problem = Problem(
                name=problem_data['name'],
                description=problem_data['description'],
                languages=json.dumps(problem_data['languages']),
                forbidden_words=json.dumps(problem_data['forbidden_words']),
                recursive=problem_data['recursive'],
                input_params=json.dumps(problem_data['input_params']),
                output_type=problem_data['output_type'],
                examples=json.dumps(problem_data['examples']),
                test_cases=json.dumps(problem_data['test_cases'])
            )
            db.session.add(problem)
    db.session.commit()
