"""Puzzle creator module - allows users to create word search puzzles."""

import os
import json
import curses
import re

# Ensure we're in the right directory
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(MODULE_DIR)

PUZZLE_WIDTH = 15


class State:
    def __init__(self, puzzle, message, selected, series):
        self.puzzle = puzzle
        self.message = message
        self.selected = selected
        self.series = series

    def get_puzzle_path(self):
        return f'Puzzles{os.path.sep}{self.series}{os.path.sep}'

    def get_words_from_puzzle(self):
        return list(self.puzzle.keys())

    def get_words_matching_regexp(self, regexp):
        words = list(self.puzzle.keys())
        matches = []
        try:
            for word in words:
                match_uppercase = re.search(regexp, word)
                match_lowercase = re.search(regexp, word.lower())
                if match_uppercase or match_lowercase:
                    matches.append(word)
            return matches
        except re.PatternError:
            return []


# Displays the puzzle and gives details about it
def display_puzzle(puzzle):
    displayed_puzzle = ''

    def print_word_to_puzzle(opt, x, y, w):
        for index, i in enumerate(w):
            if opt == 'r':
                display[y][index + x] = i
            else:
                display[index + y][x] = i

    display = [[' ' for _ in range(PUZZLE_WIDTH)] for _ in range(PUZZLE_WIDTH)]
    words = []
    displayed_puzzle += '_______________'
    for word in list(puzzle.keys()):
        print_word_to_puzzle(puzzle[word]['direction'], puzzle[word]['x'], puzzle[word]['y'], word)
        words.append(word)
    for j in range(PUZZLE_WIDTH):
        displayed_puzzle += f"\n{''.join(display[j])}{j}"
    displayed_puzzle += '\n012345678901234\n'

    # Prints letters used in the puzzle
    letters = []
    mixed_words = ''.join(words)
    legal_letters = set(mixed_words)
    for i in legal_letters:
        occurrences = []
        for j in words:
            occurrences.append(j.count(i))
        if max(occurrences) == 1:
            letters.append(i)
        else:
            letters.append(f'{max(occurrences)}{i}')
    displayed_puzzle += f"\nLetters: {letters}\n"
    return displayed_puzzle


def add_word(word, user_state):
    if word.isalpha():
        user_state.puzzle.__setitem__(word.upper(), {'direction': 'r', 'x': 0, 'y': 0})
        user_state.message = f"word {word.upper()} added to puzzle"
    else:
        user_state.message = "Invalid word"


def remove_word(word, user_state):
    if word.upper() in user_state.selected:
        user_state.selected.remove(word.upper())
    try:
        user_state.puzzle.pop(word.upper())
        return
    except:
        user_state.message = f'Could not find the word {word} to remove'


def remove_words_by_regexp(regexp, user_state):
    words_to_remove = user_state.get_words_matching_regexp(regexp)
    for word in words_to_remove:
        if word in user_state.selected:
            user_state.selected.remove(word)
        if word in user_state.puzzle:
            user_state.puzzle.pop(word)


def select_word(word, user_state):
    if not word.upper() in user_state.puzzle:
        user_state.message = "Word not found in puzzle"
    else:
        user_state.selected = [word.upper()]
        user_state.message = f"word {word.upper()} selected"


def select_words_by_regexp(regexp, user_state):
    user_state.selected = user_state.get_words_matching_regexp(regexp)


def save_puzzle(puzzle_integer, user_state):
    puzzle_path = user_state.get_puzzle_path()
    try:
        os.listdir(puzzle_path)
    except:
        if puzzle_integer == 1:
            os.mkdir(puzzle_path)

    try:
        if len(os.listdir(puzzle_path)) + 1 < int(puzzle_integer):
            user_state.message = "The integer is too big!, try just 'save' instead"
            return
        elif int(puzzle_integer) < 1:
            user_state.message = "The integer is too small!, try just 'save' instead"
            return
    except:
        user_state.message = "the puzzle needs to be saved as an integer"
        return
    try:
        with open(f'{puzzle_path}{puzzle_integer}.json', 'x') as f:
            json.dump(user_state.puzzle, f, indent=4)
            user_state.message = f'Successfully created {puzzle_integer}'
    except:
        with open(f'{puzzle_path}{puzzle_integer}.json', 'w') as f:
            json.dump(user_state.puzzle, f, indent=4)
            user_state.message = f'Puzzle {puzzle_integer} was overwritten'


def load_puzzle(name, user_state):
    puzzle_path = user_state.get_puzzle_path()
    try:
        with open(f'{puzzle_path}{name}.json', 'r') as f:
            user_state.puzzle = json.load(f)
            user_state.message = f"loaded {name}"
            user_state.selected = []
    except:
        user_state.message = f'Puzzle {name} doesn\'t exist'


def move_puzzle(puzzle_number, location, user_state, stdscr):
    puzzle_path = user_state.get_puzzle_path()
    puzzles = os.listdir(puzzle_path)
    try:
        puzzle_number = int(puzzle_number)
        location = int(location)
        if location < 1:
            user_state.message = 'the location integer must be positive'
    except:
        user_state.message = 'the arguments must be integers'

    if location > len(puzzles):
        user_state.message = "can't move puzzle to that location. location out of bounds"
        return

    try:
        os.rename(f'{puzzle_path}{puzzle_number}.json', f'{puzzle_path}moving.json')
    except:
        user_state.message = f"puzzle {puzzle_number} does not exist!"
        return
    # Renames puzzles in front of puzzle
    i = puzzle_number
    while i < len(puzzles):
        try:
            os.rename(f'{puzzle_path}{i + 1}.json', f'{puzzle_path}{i}.json')
        except:
            stdscr.clear()
            stdscr.addstr(f"an error occurred: could not find puzzle {i + 1} in {user_state.series}\nPlease make sure that all the puzzles in the series are integers and that no numbers are missing.\n\n\nPress any key to continue")
            stdscr.getkey()

        i += 1
    # Renames puzzles in front of new puzzle location
    n = len(puzzles) - 1
    while n >= location:
        try:
            os.rename(f'{puzzle_path}{n}.json', f'{puzzle_path}{n + 1}.json')
        except:
            stdscr.clear()
            stdscr.addstr(f"an error occurred: could not find puzzle {n} in {user_state.series}\nPlease make sure that all the puzzles in the series are integers and that no numbers are missing\n\n\nPress any key to continue")
            stdscr.getkey()
        n -= 1
    try:
        os.rename(f'{puzzle_path}moving.json', f'{puzzle_path}{location}.json')
    except:
        stdscr.clear()
        stdscr.addstr("an error occurred changing the name of the moving.json file, you may need to do this manually\n\n\nPress any key to continue")
        stdscr.getkey()


def move_words(words, x, y, user_state):
    if not words:
        user_state.message = "Cannot move word. Word not selected"
        return
    try:
        x = int(x)
        y = int(y)
    except:
        user_state.message = "x and y coordinates must be integers"
        return
    for word in words:
        word_x = user_state.puzzle[word]['x']
        word_y = user_state.puzzle[word]['y']
        word_direction = user_state.puzzle[word]['direction']
        # Move word in x direction
        if (len(word) + x + word_x > PUZZLE_WIDTH and word_direction == 'r') or word_x + x + 1 > PUZZLE_WIDTH:
            user_state.puzzle[word]['x'] = 0
        elif word_x + x < 0 and word_direction == 'r':
            user_state.puzzle[word]['x'] = PUZZLE_WIDTH - len(word)
        elif word_x + x < 0 and word_direction == 'd':
            user_state.puzzle[word]['x'] = PUZZLE_WIDTH - 1
        else:
            user_state.puzzle[word]['x'] = user_state.puzzle[word]['x'] + x

        # Move word in y direction
        if (len(word) + y + word_y > PUZZLE_WIDTH and word_direction == 'd') or word_y + y + 1 > PUZZLE_WIDTH:
            user_state.puzzle[word]['y'] = 0
        elif word_y + y < 0 and word_direction == 'd':
            user_state.puzzle[word]['y'] = PUZZLE_WIDTH - len(word)
        elif word_y + y < 0 and word_direction == 'r':
            user_state.puzzle[word]['y'] = PUZZLE_WIDTH - 1
        else:
            user_state.puzzle[word]['y'] = user_state.puzzle[word]['y'] + y


def rotate_words(words, user_state):
    if not user_state.selected:
        user_state.message = "No words are selected to rotate"
        return
    for word in words:
        word_x = user_state.puzzle[word]['x']
        word_y = user_state.puzzle[word]['y']
        word_direction = user_state.puzzle[word]['direction']

        # Test if word is out of bounds if rotated
        if (len(word) + word_x - 1 > 14 and word_direction == 'd') or (len(word) + word_y - 1 > 14 and word_direction == 'r'):
            user_state.message = f'Could not rotate {word}, it would go out of bounds'
            return
    # Rotates the word
    for word in words:
        if user_state.puzzle[word]['direction'] == 'r':
            user_state.puzzle[word]['direction'] = 'd'
        else:
            user_state.puzzle[word]['direction'] = 'r'
        user_state.message = f"words rotated"


def delete_puzzle(puzzle_number, user_state, stdscr):
    puzzle_path = user_state.get_puzzle_path()
    try:
        puzzle_number = int(puzzle_number)
    except:
        user_state.message = 'the argument must be an integer'
    try:
        os.remove(f'{puzzle_path}{puzzle_number}.json')
    except:
        user_state.message = f"puzzle {puzzle_number} does not exist!"
        return
    puzzles = os.listdir(puzzle_path)
    n = puzzle_number
    while n <= len(puzzles):
        try:
            os.rename(f'{puzzle_path}{n + 1}.json', f'{puzzle_path}{n}.json')
        except:
            stdscr.clear()
            stdscr.addstr(f"an error occurred: could not find puzzle {n + 1} in {user_state.series}\nPlease make sure that all the puzzles in the series are integers and that no numbers are missing\n\n\nPress any key to continue")
            stdscr.getkey()
            return
        n += 1
    user_state.message = f"puzzle {puzzle_number} deleted"
    if len(os.listdir(puzzle_path)) == 0:
        os.rmdir(puzzle_path)


def view_series(series, user_state):
    puzzle_path = user_state.get_puzzle_path()
    try:
        os.listdir(puzzle_path)
    except:
        user_state.message = "This series doesn't have any puzzles in it!"
        return
    number_of_puzzles_in_series = len(os.listdir(puzzle_path))
    report = f'Levels in {series}\n\nNumber of puzzles: {number_of_puzzles_in_series}\n\n'
    for puzzle in range(number_of_puzzles_in_series):
        with open(f'{puzzle_path}{puzzle + 1}.json', 'r') as f:
            report += f"Level {puzzle + 1}\n\n{display_puzzle(json.load(f))}\n"
    os.system(f'echo "{report}" | more' if os.name == 'nt' else f'echo "{report}" | less')


def print_bold_word(word, user_state, stdscr):
    if word != "":
        if user_state.puzzle[word]['direction'] == 'r':
            stdscr.addstr(1 + user_state.puzzle[word]['y'], user_state.puzzle[word]['x'], word, curses.A_BOLD)
        else:
            for i in range(len(word)):
                stdscr.addstr(1 + user_state.puzzle[word]['y'] + i, user_state.puzzle[word]['x'], word[i], curses.A_BOLD)


def input_string(message, behavior, user_state, stdscr):
    if behavior == "words":
        tab_array = user_state.get_words_from_puzzle()
    elif behavior == "series":
        tab_array = os.listdir(f"Puzzles")
    elif behavior == "puzzles":
        tab_array = []
        for i in range(len(os.listdir(user_state.get_puzzle_path()))):
            tab_array.append(str(i + 1))
    else:
        tab_array = []
    input_str = r''
    formated_message = f"{message}: > "
    cursor_location = 0
    times_pressed_tab = -1
    puzzle = user_state.puzzle
    while True:
        stdscr.clear()
        stdscr.addstr(display_puzzle(puzzle))
        stdscr.addstr(f"SERIES: {user_state.series}\n")
        stdscr.addstr(f"{user_state.message}\n\n")
        stdscr.addstr(23, 0, formated_message + input_str)
        stdscr.addstr(23, len(formated_message) + cursor_location, '')
        stdscr.refresh()
        if behavior == 'regexp':
            for i in user_state.get_words_matching_regexp(input_str):
                print_bold_word(i, user_state, stdscr)
            stdscr.addstr(23, len(formated_message) + cursor_location, '')
        elif behavior == 'words':
            if input_str.upper() in user_state.puzzle:
                print_bold_word(input_str.upper(), user_state, stdscr)
            stdscr.addstr(23, len(formated_message) + cursor_location, '')
        key = stdscr.getch()

        if (key == curses.KEY_BACKSPACE or key == 127) and cursor_location > 0:
            input_str = input_str[:cursor_location - 1] + input_str[cursor_location:]
            cursor_location -= 1
        elif key == ord('\n'):
            break
        elif key == ord('\t'):
            if(tab_array):
                times_pressed_tab += 1
                input_str = tab_array[times_pressed_tab % len(tab_array)]
                cursor_location = len(input_str)
                if(behavior == "puzzles"):
                    user_state.message = f"There are {len(tab_array)} puzzles in this series"
                    with open(f'{user_state.get_puzzle_path()}{tab_array[times_pressed_tab % len(tab_array)] }.json', 'r') as f:
                        puzzle = json.load(f)
        elif key == 27:  # 27 is for the escape key
            return ''
        elif key == curses.KEY_LEFT and not cursor_location == 0:
            cursor_location -= 1
        elif key == curses.KEY_RIGHT and cursor_location < len(input_str):
            cursor_location += 1
        elif 0 <= key <= 255:
            input_str = input_str[:cursor_location] + chr(key) + input_str[cursor_location:]
            cursor_location += 1
        user_state.get_words_matching_regexp(input_str)
        stdscr.clear()
        stdscr.addstr(f"{message}:\n")

    stdscr.refresh()
    return input_str


def read_input(user_input, user_state, stdscr):
    try:
        user_input = chr(user_input)
    except ValueError:
        return
    
    global series
    
    match user_input:
        # WORD COMMANDS
        case 'a':
            word = input_string("What word do you want to add? ", 'null', user_state, stdscr)
            if not word:
                return
            if len(word) > PUZZLE_WIDTH:
                user_state.message = f"Word must be less than {PUZZLE_WIDTH + 1} characters long!"
                return
            add_word(word, user_state)
            if not word.upper() in user_state.selected and word.upper() in user_state.get_words_from_puzzle():
                select_word(word, user_state)
        case 'd':
            word = input_string("What word do you want to delete? ", 'words', user_state, stdscr)
            if not word:
                return
            if not word.upper() in user_state.puzzle:
                user_state.message = f"Can't delete {word}. word not in puzzle"
                return
            remove_word(word, user_state)
        case 'D':
            regexp = input_string("Delete words matching a regular expression ", 'regexp', user_state, stdscr)
            remove_words_by_regexp(regexp, user_state)
        case 's':
            word = input_string("Select a word ", 'words', user_state, stdscr)
            if not word:
                return
            if not word.upper() in user_state.puzzle:
                user_state.message = f"Can't select {word}. word not in puzzle"
                return
            select_word(word, user_state)
        case 'S':
            regexp = input_string("Select words in a regular expression ", 'regexp', user_state, stdscr)
            select_words_by_regexp(regexp, user_state)
        # MOVEMENT COMMANDS
        case key if key == 'h' or key == chr(curses.KEY_LEFT):
            move_words(user_state.selected, -1, 0, user_state)
        case key if key == 'j' or key == chr(curses.KEY_DOWN):
            move_words(user_state.selected, 0, 1, user_state)
        case key if key == 'k' or key == chr(curses.KEY_UP):
            move_words(user_state.selected, 0, -1, user_state)
        case key if key == 'l' or key == chr(curses.KEY_RIGHT):
            move_words(user_state.selected, 1, 0, user_state)
        case 'r':
            rotate_words(user_state.selected, user_state)
        # SERIES COMMANDS
        case 'c':
            series_name = input_string("Enter the name of a series you want to create/edit: ", 'series', user_state, stdscr)
            if series_name.isalnum():
                user_state.series = series_name
        case 'o':
            try:
                os.listdir(user_state.get_puzzle_path())
            except:
                user_state.message = "The series you are editing contains no puzzles"
                return
            puzzle_integer = input_string('Enter a puzzle number to load: ', 'puzzles', user_state, stdscr)
            load_puzzle(puzzle_integer, user_state)
        case 'q':
            curses.endwin()
            exit()
        case 'v':
            view_series(user_state.series, user_state)
        case 'w':
            try:
                save_puzzle(len(os.listdir(user_state.get_puzzle_path())) + 1, user_state)
            except:
                save_puzzle(1, user_state)
        case 'W':
            try:
                requested_integer = int(input_string("Enter a puzzle number to overwrite: ", 'puzzles', user_state, stdscr))
            except:
                user_state.message = "Not a number"
                return
            save_puzzle(requested_integer, user_state)
        case 'x':
            try:
                os.listdir(user_state.get_puzzle_path())
            except:
                user_state.message = "The series you are editing contains no puzzles"
                return
            puzzle_integer = input_string("What puzzle do you want to delete?: ", 'puzzles', user_state, stdscr)
            delete_puzzle(puzzle_integer, user_state, stdscr)
        case 'm':
            try:
                os.listdir(user_state.get_puzzle_path())
            except:
                user_state.message = "The series you are editing contains no puzzles"
                return
            try:
                puzzle_integer = int(input_string('Where puzzle do you want to move?: ', 'puzzles', user_state, stdscr))
            except:
                user_state.message = "Not a number"
                return
            try:
                location = int(input_string('Where do you want to move the puzzle? :', 'puzzles', user_state, stdscr))
            except:
                user_state.message = "Not a number"
                return
            move_puzzle(puzzle_integer, location, user_state, stdscr)
        case key if key == '?' or key == chr(curses.KEY_HELP):
            os.system('more ..\\docs\\creating-puzzles.txt' if os.name == 'nt' else 'less ../docs/creating-puzzles.txt')
        case _:
            return


def main():
    """Main entry point for the puzzle creator module."""
    os.chdir(PROJECT_ROOT)
    
    # Allows user to input commands
    user_state = State({}, 'Welcome to Python Words! Type "?" for help', [], 'Custom')
    stdscr = curses.initscr()

    stdscr.keypad(True)
    while True:
        stdscr.clear()
        stdscr.addstr(display_puzzle(user_state.puzzle))
        stdscr.addstr(f"SERIES: {user_state.series}\n")
        stdscr.addstr(f"{user_state.message}\n\n")
        for i in user_state.selected:
            print_bold_word(i, user_state, stdscr)
        stdscr.addstr(23, 0, "")
        try:
            key = stdscr.getch()
            read_input(key, user_state, stdscr)
        except KeyboardInterrupt:
            user_state.message = "Press 'q' to exit the program"


if __name__ == "__main__":
    main()
