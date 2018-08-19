#!/usr/bin/env python
from typing import Any, Collection, List, Optional, Tuple, TypeVar
from validate import *
from generate import RandomGuessValidator, generate_combination


def iteratively_solve(mm: MasterMind, options: List[T], length: int=4, log=print) -> Tuple[Guess, List[Clue]]:
    guess = None
    result = None

    guesser = RandomGuessValidator(options, length, duplicates=True)
    log(guesser.stat_msg())
    log("")

    clues = []
    count = 0
    while result != [GuessResult.EXACT_MATCH] * length:
        count += 1

        guess = guesser.generate()
        log("Guess {}: {}".format(count, guess))
        result = mm.validate(guess)
        log("Result:", [res.name for res in result])

        guesser.add_clue((guess, result))
        log(guesser.stat_msg())
        clues.append((guess, result))
        log("")

    return guess, clues


def manual_input(options: List[T], option_chars:List[chr], length: int=4, duplicates=True):
    result_chars = {
        'b': GuessResult.EXACT_MATCH,
        'w': GuessResult.ONLY_COLOR_CORRECT,
        'p': GuessResult.ONLY_POSITION_CORRECT,
        ' ': GuessResult.INCORRECT
    }

    guesser = RandomGuessValidator(options, length, duplicates)

    result = None
    while result != [GuessResult.EXACT_MATCH] * length:
        rnd_choice = guesser.generate()
        print(guesser.stat_msg())
        rnd_choice_inp = ''.join([option_chars[options.index(col)] for col in rnd_choice])
        print('Random valid choice: {} [{}]'.format(', '.join(rnd_choice),rnd_choice_inp))

        guess_inp = input("Guess: ")
        if guess_inp == '':
            guess_inp = rnd_choice_inp
        guess = [options[option_chars.index(col)] for col in guess_inp]
        result_inp = input("Result: ")
        result = [result_chars[res] for res in result_inp]

        guesser.add_clue((guess, result))
        print()

    exit()


OPTIONS = ["black", "gray", "white", "red", "green", "blue", "yellow", "purple"]
LENGTH = 4


def main():

    # Manually solve
    # manual_options = {
    #     # 'p': 'purple',
    #     # 'r': 'red',
    #     'u': 'blue',
    #     'g': 'green',
    #     'y': 'yellow',
    #     'o': 'orange',
    #     'n': 'brown',
    #     'i': 'pink',
    #     # 'e': 'empty'
    # }
    # options_tuple = manual_options.items()
    # manual_input([v for _, v in options_tuple], [k for k, _ in options_tuple], length=4, duplicates=False)

    solution = generate_combination(OPTIONS, length=LENGTH)
    print("Secret solution:", solution)

    mm = MasterMind(solution)
    iteratively_solve(mm, OPTIONS, length=LENGTH)

    # Benchmark methods of generating possibilities. Determine if generating a list of strings slow enough that we
    # should rather represent each possibility by an assigned numeric value which can be interpreted/processed back
    # to a list of string values.
    import timeit
    print(timeit.timeit('generate_combination(OPTIONS, length=LENGTH)', number=10000,
                        globals=globals()))
    print(timeit.timeit('randint(0, max - 1)', number=10000,
                        setup="from math import pow\n" + "max = pow(len(OPTIONS),LENGTH)",
                        globals=globals()))
    print(timeit.timeit('numpy.random.randint(max)', number=10000,
                        setup="import numpy.random\n" + "max = pow(len(OPTIONS),LENGTH)",
                        globals=globals()))
    print(timeit.timeit(
        "validate_solution(['red', 'white', 'white', 'white'], ['purple', 'purple', 'white', 'yellow'])",
        number=10000,  globals=globals()))
    exit()

    solve_counts = []
    for i in range(100):
        solution = generate_combination(OPTIONS, length=LENGTH)
        mm = MasterMind(solution)
        _, clues = iteratively_solve(mm, OPTIONS, length=LENGTH, log=lambda *x: x)
        solve_counts.append(len(clues))
        if len(clues) > 10:
            print(solution)
            print(clues)

    import collections
    print(collections.Counter(solve_counts))

    import numpy as np
    import matplotlib.pyplot as plt
    # hist, bins = np.histogram(solve_counts)
    plt.hist(solve_counts, 0.5 + np.arange(0, 12))
    plt.title("Histogram of guesses needed")
    plt.show()


    # solution = ['red', 'white', 'white', 'white']
    # prev_guess = ['purple', 'purple', 'white', 'yellow']
    # print(MasterMind(solution).validate(prev_guess))

    # ['yellow', 'gray', 'blue', 'yellow']
    # ['yellow', 'blue', 'black', 'blue']

    # ['purple', 'purple', 'yellow', 'black']
    # ['yellow', 'black', 'purple', 'purple']


if __name__ == "__main__":
    main()
