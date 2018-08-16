import itertools
from enum import Enum
from random import randint
from typing import Any, Collection, List, Optional, Tuple, TypeVar


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

