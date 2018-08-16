#!/usr/bin/env python
import itertools
from enum import Enum
from random import randint
from typing import Any, Collection, List, Optional, Tuple, TypeVar
from abc import ABC, abstractmethod


T = TypeVar('T')
Guess = List[Any]
Result = List[Any]
Clue = Tuple[Guess, Result]


class GuessResult(Enum):
    INCORRECT = 0
    ONLY_COLOR_CORRECT = 1
    ONLY_POSITION_CORRECT = 2
    EXACT_MATCH = 3


class MasterMind:

    def __init__(self, solution: List[T]):
        self._solution = solution

    def validate(self, guess: List[T]) -> List[GuessResult]:
        return validate_solution(self._solution, guess)


class ValidSolutionGenerator(ABC):

    def __init__(self, options: List[Any], length: int=4, duplicates: bool=True):
        self.options = options
        self.length = length
        self.duplicates = duplicates
        self.clues = []

    def add_clue(self, clue: Clue):
        self.clues.append(clue)

    @abstractmethod
    def generate(self):
        pass

    def stat_msg(self):
        return ''


class InMemoryPruner(ValidSolutionGenerator):

    def __init__(self, options: List[Any], length: int=4, duplicates: bool=True):
        super().__init__(options, length, duplicates)
        self.all_valid_choices = sorted(list(all_choices(options, length, duplicates=duplicates)))

    def add_clue(self, clue: Clue):
        super().add_clue(clue)
        guess, result = clue
        # Prune list of possible choices based on newest clue
        self.all_valid_choices = [opt for opt in self.all_valid_choices if valid_possibility(guess, result, opt)]
        if len(self.all_valid_choices) == 0:
            print('Logical inconsistency')
            exit()

    def generate(self):
        return self.all_valid_choices[0]

    def stat_msg(self):
        return 'Choices available: {}'.format(len(self.all_valid_choices))


class RandomGuessValidator(ValidSolutionGenerator):

    def __init__(self, options: List[Any], length: int=4, duplicates: bool=True):
        super().__init__(options, length, duplicates)
        self.last_guess_count = None

    def generate(self):
        rnd_choice, self.last_guess_count = generate_random_valid_guess(
            self.clues, self.options, self.length, self.duplicates, max_tries=None)
        if rnd_choice is None:
            print("Couldn't find valid guess")
            exit()
        return rnd_choice

    def stat_msg(self):
        return 'Guesses needed: {}'.format(self.last_guess_count)


def identify_exact_matches(solution: List[T], guess: List[T]) -> Collection[int]:
    solution_set = {(idx, val) for idx, val in enumerate(solution)}
    guess_set = {(idx, val) for idx, val in enumerate(guess)}
    exact_matches = solution_set.intersection(guess_set)
    match_idxs = [pos for pos, _ in exact_matches]
    return match_idxs


def identify_colour_matches(solution: List[T], guess: List[T]) -> Collection[T]:
    solution_set = {val for val in solution}
    guess_set = {val for val in guess}
    color_matches = solution_set.intersection(guess_set)
    return color_matches


def validate_solution(solution: List[T], guess: List[T]) -> List[GuessResult]:
    if solution == guess:
        return [GuessResult.EXACT_MATCH] * len(guess)

    result = []
    match_idxs = sorted(identify_exact_matches(solution, guess))
    result.extend([GuessResult.EXACT_MATCH] * len(match_idxs))

    # Remove exact matches from consideration
    remaining_solution = list(solution)
    remaining_guess = list(guess)
    for pos in reversed(match_idxs):
        del remaining_solution[pos]
        del remaining_guess[pos]

    # Look for only-colour matches in remaining values
    match_cols = identify_colour_matches(remaining_solution, remaining_guess)
    result.extend([GuessResult.ONLY_COLOR_CORRECT] * len(match_cols))

    return result


def valid_possibility(prev_guess: List[T], prev_result: Collection[GuessResult], next_guess: List[T]) -> bool:
    """
    For the next guess to be a possible solution, the relationship between the next guess and the previous
    guess should be the same as the relationship between the previous guess and the solution.
    """
    cmp_result = validate_solution(prev_guess, next_guess)
    return list(prev_result) == list(cmp_result)


def generate_combination(options: List[Any], length: int=4, duplicates=True):
    if not duplicates and len(options) < length:
        raise Exception("Not enough options provided to generate non-duplicate combinations")

    # Copy options since we might alter it
    options = list(options)
    combination = []
    for i in range(length):
        choice_idx = randint(0, len(options) - 1)
        combination.append(options[choice_idx])
        if not duplicates:
            del options[choice_idx]
    return combination


def all_choices(options: List[Any], length: int=4, duplicates: bool=True):
    all_options = list(options)
    if duplicates:
        all_options = options * length
    # When allowing duplicate options the number of unique permutations and combinations are identical
    # i.e. set(combinations) == set(permutations)
    return set(itertools.permutations(all_options, length))


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


def generate_random_valid_guess(clues: List[Clue],
                                options: List[Any], length: int=4, duplicates=True,
                                max_tries: Optional[int]=1000) -> Tuple[Guess, int]:
    guess = None
    guess_valid = False
    count = 0
    while not guess_valid:
        guess = generate_combination(options, length, duplicates)
        guess_valid = True
        for clue in clues:
            prev_guess, prev_result = clue
            guess_valid = guess_valid and valid_possibility(prev_guess, prev_result, guess)
            if not guess_valid:
                continue
        count += 1
        if max_tries is not None and count > max_tries:
            guess = None
            break

    return guess, count


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


def main():
    OPTIONS = ["black", "gray", "white", "red", "green", "blue", "yellow", "purple"]

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

    solution = generate_combination(OPTIONS)  # ['white', 'yellow', 'white', 'red']
    print("Secret solution:", solution)

    mm = MasterMind(solution)
    iteratively_solve(mm, OPTIONS)  # , log=lambda *x: x)

    solve_counts = []
    for i in range(100):
        solution = generate_combination(OPTIONS)
        mm = MasterMind(solution)
        _, clues = iteratively_solve(mm, OPTIONS, log=lambda *x: x)
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
