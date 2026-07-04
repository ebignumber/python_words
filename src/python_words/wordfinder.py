"""Word finder game module - allows users to play word search puzzles."""

import os
import random
import json
import sys
from pathlib import Path
from python_words.config import get_config_path

# Ensure we're in the right directory
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(MODULE_DIR)


def initialize_paths():
    """Initialize the paths for puzzle data."""
    global puzzle_path
    os.chdir(PROJECT_ROOT)


# Reads series in Puzzles
def start_game():
    global series
    global puzzle_path
    global has_played_a_round
    
    initialize_paths()
    puzzles = os.listdir(puzzle_path)
    for index, i in enumerate(puzzles):
        print(str(index + 1) + ': ' + str(i))
    while True:
        if not has_played_a_round:
            print('Select a series you want to play:\n')
            select_series = input('')
        if select_series.isnumeric() and not "-" in select_series and not select_series == '0':
            try:
                series = puzzles[int(select_series) - 1]
                break
            except:
                print("Number must be one of the options")
        else:
            print('Your input must be a number listed')
    puzzle_path = f'{puzzle_path}{os.path.sep}{series}'


# Select the puzzle
def select_puzzle():
    global puzzle_number
    global has_played_a_round

    # Reads puzzle_number
    if not has_played_a_round: 
        while True: 
            try:
                puzzle_number = input('Enter a puzzle number or type "exit" to exit: ')
                if puzzle_number == 'exit':
                    break
                puzzle_number = int(puzzle_number)
                if puzzle_number < 1 or puzzle_number > len(os.listdir(puzzle_path)):
                    print(f"Level Number must be between 1 and {len(os.listdir(puzzle_path))}")
                else:
                    break
            except:
                print('not a number')
    else:
        puzzle_number += 1
    if puzzle_number == 'exit':
        exit()


# Converts puzzle to a list of lists
def empty_puzzle_list():
    global puzzle_list
    puzzle_list = []
    n = 225
    while n > 0:
        if n % 15 == 0:
            puzzle_list.append([' '])
        puzzle_list[(225 - n) // 15].append(' ')
        n -= 1


# Adds words to the puzzle and collects them in a list to guess
def add_word_to_puzzle(opt, x, y, w, word_found):
    for index, i in enumerate(w):
        if word_found == False:
            if opt == 'r':
                puzzle_list[y][index + x] = '#'
            else:
                puzzle_list[index + y][x] = '#'
        else:
            if opt == 'r':
                puzzle_list[y][index + x] = i
            else:
                puzzle_list[index + y][x] = i


# Gets new puzzle to play
def get_puzzle():
    global puzzle_data, word_list, puzzle_list
    with open(f'{puzzle_path}{os.path.sep}{puzzle_number}.json', 'r') as f:  # Opens path to puzzle
        puzzle_data = json.load(f)
        print(puzzle_data)
    word_list = list(puzzle_data.keys())
    for word in word_list:
        add_word_to_puzzle(puzzle_data[word]['direction'], puzzle_data[word]['x'], puzzle_data[word]['y'], word, False)


# Updates the puzzle to add the puzzle
def update_puzzle(word):
    result = puzzle_data[word]
    add_word_to_puzzle(result['direction'], result['x'], result['y'], word, True)
    found_words.append(word)
    puzzle_data.pop(word)
    word_list.pop(word_list.index(word))


def display_puzzle(puzzle):
    for i in range(15):
        print(''.join(puzzle[i]))


# Adds the letters that are used in the puzzle
def collect_legal_letters(list):
    global letters
    if difficulty == 'normal':
        all_words = list + found_words
    else:
        all_words = list
    letters = []
    all_words_string = ''.join(all_words)
    legal_letters = set(all_words_string)
    for i in legal_letters:
        occurrences = []
        for j in all_words:
            occurrences.append(j.count(i))
        if max(occurrences) == 1:
            letters.append(i)
        elif contracted:
            letters.append(f'{max(occurrences)}{i}')
        else:
            for k in range(max(occurrences)):
                letters.append(i)


def read_command(command):
    global current_puzzle, puzzle_data, difficulty, letters, contracted, message
    match command:
        #case "/":
        #    with open(f"docs{os.path.sep}wordfinder-commands.txt", 'r') as f:
        #        message = f.read()

        case "/COMPACT":
            letter_set = set(letters)
            for i in letter_set:
                if not letters.count(i) == 1:
                    count = letters.count(i)
                    first_occurrence = letters.index(i)
                    for j in range(letters.count(i)):
                        letters.pop(letters.index(i))
                    letters.insert(first_occurrence, f'{count}{i}')

        case "/EASY":
            difficulty = 'easy'

        case "/EXPAND":
            for index, i in enumerate(letters):
                if not i.isalpha():
                    integer = int(i[0:-1])
                    letter = i[-1]
                    letters.pop(index)
                    for j in range(integer):
                        print(letter)
                        letters.insert(index, letter)

        case "/EXIT":
            sys.exit()

        case "/HINT":
            word_to_hint = word_list[random.randint(0, len(word_list) - 1)]
            index_to_hint = random.randint(0, len(word_to_hint) - 1)
            direction = puzzle_data[word_to_hint]['direction']
            word_to_hint_x = puzzle_data[word_to_hint]['x']
            word_to_hint_y = puzzle_data[word_to_hint]['y']
            if direction == 'r':
                x = int(word_to_hint_x) + index_to_hint
                y = int(word_to_hint_y)
            else:
                x = word_to_hint_x 
                y = word_to_hint_y + index_to_hint

            if not puzzle_list[y][x] == '#':
                read_command("/HINT")
            else:
                puzzle_list[y][x] = f"\033[31m{word_to_hint[index_to_hint]}\033[0m"
                message = 'Hint Added!\n'

        case "/NORMAL":
            difficulty = 'normal'

        case "/RESET":
            empty_puzzle_list()
            get_puzzle()
            found_words.clear()
            current_puzzle = puzzle_list

        case "/SHUFFLE":
            current_letters = letters
            letters = []
            while not len(current_letters) == 0:
                random_int = random.randint(0, len(current_letters) - 1)
                letters.append(current_letters[random_int])
                current_letters.pop(random_int)

        case _:
            message = 'Not a command\n'
            return


# Tries to find the guessed word in the list of words  
def guess_word():
    global message
    guess = input('Guess a word or type "/" for a list of commands:\n\n').upper()
    print('\n')
    if guess[0] == '/':
        read_command(guess)
        return

    if guess in found_words:
        message = 'Word Already Guessed\n'
    elif guess in word_list:
        update_puzzle(guess)
        message = 'Word Found\n'
        if difficulty == 'easy':
            collect_legal_letters(word_list)
    else:
        message = 'Word Not Found\n'


# Plays the game
def play_game():
    global letters, current_puzzle, message
    current_puzzle = puzzle_list
    collect_legal_letters(word_list)
    while len(word_list) != 0:
        os.system('cls' if os.name == 'nt' else 'clear')
        display_puzzle(current_puzzle)
        print(f'Letters: {letters}')
        print("\n" + message)
        message = ''
        guess_word()
    os.system('cls' if os.name == 'nt' else 'clear')
    message = ''
    display_puzzle(current_puzzle)
    print(f'You completed puzzle {puzzle_number}!\n')


def main():
    """Main entry point for the wordfinder module."""
    global has_played_a_round, series, puzzle_number
    
    initialize_paths()
    
    # Reset global state for a fresh game
    global has_played_a_round, difficulty, contracted, series, puzzle_path, message
    global puzzle_list, word_list, found_words, current_puzzle, puzzle_data, letters, puzzle_number
    
    has_played_a_round = False
    difficulty = 'normal'
    contracted = False
    series = ''
    puzzle_path = get_config_path() / "Puzzles"
    message = ''
    puzzle_list = []
    word_list = []
    found_words = []
    current_puzzle = []
    puzzle_data = {}
    letters = []
    puzzle_number = None
    
    start_game()
    select_puzzle()
    empty_puzzle_list()
    get_puzzle()

    # The loop calling the other functions
    while True:
        play_game()
        if puzzle_number < len(os.listdir(puzzle_path)):
            yes_or_no = input('Would you like to play the next level? \n\nn: no\ns: start new level\nany other key: start next level\n')
        else:
            yes_or_no = input('Congrats! you finished the series! Would you like to play another series? \n\nn: no\n')
        if yes_or_no == 'n':
            break
        elif puzzle_number >= len(os.listdir(puzzle_path)) or yes_or_no == 's':
            print('\n')
            has_played_a_round = False
            start_game()
            select_puzzle()
            empty_puzzle_list()
            get_puzzle()
            found_words.clear()
        else:
            has_played_a_round = True
            select_puzzle()
            empty_puzzle_list()
            get_puzzle()
            found_words.clear()


if __name__ == "__main__":
    main()
