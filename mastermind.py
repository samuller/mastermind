#!/usr/bin/env python
from random import randint
from enum import Enum
from typing import Any, Collection, List, TypeVar
import itertools


class GuessResult(Enum):
    INCORRECT = 0
    ONLY_COLOR_CORRECT = 1
    ONLY_POSITION_CORRECT = 2
    EXACT_MATCH = 3


T = TypeVar('T')

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


def validate_solution(solution, guess: List[T]) -> List[GuessResult]:
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


class MasterMind:

    def __init__(self, solution: List[T]):
        self._solution = solution

    def validate(self, guess: List[T]) -> List[GuessResult]:
        return validate_solution(self._solution, guess)


def valid_possibility(prev_guess: List[T], prev_result: Collection[GuessResult], next_guess: List[T]) -> bool:
    """
    For the next guess to be a possible solution, the relationship between the next guess and the previous
    guess should be the same as the relationship between the previous guess and the solution.
    """
    cmp_result = validate_solution(prev_guess, next_guess)
    return list(prev_result) == list(cmp_result)


def generate_combination(options: List[Any], count: int=4, duplicates=True):
    if not duplicates and len(options) < count:
        raise Exception("Not enough options provided to generate non-duplicate combinations")

    # Copy options since we might alter it
    options = list(options)
    combination = []
    for i in range(count):
        choice_idx = randint(0, len(options) - 1)
        combination.append(options[choice_idx])
        if not duplicates:
            del options[choice_idx]
    return combination


def all_choices(options, count=4, duplicates=True):
    all_options = list(options)
    if duplicates:
        all_options = options * count
    # When allowing duplicate options the number of unique permutations and combinations are identical
    # i.e. set(combinations) == set(permutations)
    return set(itertools.permutations(all_options, count))


def main():
    OPTIONS = ["black", "gray", "white", "red", "green", "blue", "yellow", "purple"]

    solution = generate_combination(OPTIONS)
    print(solution)

    guess = generate_combination(OPTIONS)
    print(guess)

    mm = MasterMind(solution)
    result = mm.validate(guess)
    print([res.name for res in result])

    next_guess = generate_combination(OPTIONS)
    print(next_guess)
    print(valid_possibility(guess, result, next_guess))

    print(len(all_choices(OPTIONS)))
    all_valid_choices = [opt for opt in all_choices(OPTIONS) if valid_possibility(guess, result, opt)]
    print(len(all_valid_choices))

    # solution = ['red', 'white', 'white', 'white']
    # guess = ['purple', 'purple', 'white', 'yellow']
    # print(MasterMind(solution).validate(guess))

    # ['yellow', 'gray', 'blue', 'yellow']
    # ['yellow', 'blue', 'black', 'blue']

    # ['purple', 'purple', 'yellow', 'black']
    # ['yellow', 'black', 'purple', 'purple']


if __name__ == "__main__":
    main()
