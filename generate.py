from abc import ABC, abstractmethod
from validate import *


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
    """
    Generates all possibilities in memory and then prunes the possibilities with each additional clue.

    A large possibility space will take long to generate and use up lots of memory.
    """

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
    """
    Takes random guesses which it then validates with the list of clues.

    A large probability space will take longer and longer to generate valid guesses.
    """

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
