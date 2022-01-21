from words import __validAnswers, __validGuesses
import numpy as np
import random
import functools
import pandas as pd

from collections import Counter
from itertools import product

__FIRST_GUESS = 'soare'
__WORDLENGTH = len(__FIRST_GUESS)
sequences = (''.join(s) for s in product('012', repeat=__WORDLENGTH))
colors = (''.join(s) for s in product('⬛🟨🟩', repeat=__WORDLENGTH))
colorMap = dict(zip(sequences, colors))

class Lexicon:
    def __init__(self, validAnswers, validGuesses) -> None:
        self.answers = validAnswers
        self.guesses = validGuesses
    
    def filterAnswers(self, guess, response):
        return tuple([answer for answer in self.answers if compare(guess, answer) == response])

    @property
    def bestGuess(self):
        if len(self.answers) == 1 or len(self.answers) == 2:
            return(self.answers[0])
        
        best_guess = ''
        best_entropy = 0

        for guess in self.guesses:
            probs = find_distribution(guess, self.answers)
            entropy = calculate_entropy(probs)
            if entropy > best_entropy:
                best_entropy = entropy
                best_guess = guess
        return best_guess

@functools.cache
def compare(guess, answer):
    answerLetterCounts = Counter(answer)
    wordLength = len(answer)
    response = ['0'] * wordLength

    for i in range(wordLength):
        if answer[i] == guess[i]:
            response[i] = '2'
            answerLetterCounts[guess[i]] -= 1

    for i in range(wordLength):
        if (
            answerLetterCounts[guess[i]] > 0 and 
            answer[i] != guess[i] and 
            guess[i] in answer
        ):
            response[i] = '1'
            answerLetterCounts[guess[i]] -= 1

    return ''.join(response)

def find_distribution(guess, lexicon):
    responseCounts = np.zeros(3**len(guess))
    for word in lexicon:
        response = compare(guess, word)
        responseCounts[int(response, 3)] += 1    
    return responseCounts / len(lexicon)

def calculate_entropy(dist):
    H = -np.sum(dist * np.log2(dist, where=~np.isclose(dist, 0)))
    return H

_cachedSecondGuess = {}
def cachedSecondGuess(firstGuess, firstResponse, lexicon):
    if (firstGuess, firstResponse) not in _cachedSecondGuess:
        _cachedSecondGuess[(firstGuess, firstResponse)] = lexicon.bestGuess
    return _cachedSecondGuess[(firstGuess, firstResponse)]

def autoplay(correctAnswer, validAnswers=__validAnswers, 
             validGuesses=__validGuesses, firstGuess=__FIRST_GUESS):
    if correctAnswer == firstGuess:
        return (firstGuess, '2' * len(firstGuess), 1)
    valid = Lexicon(__validAnswers, __validGuesses)

    response = compare(firstGuess, correctAnswer)
    valid.answers = valid.filterAnswers(firstGuess, response)
    guesses = [(firstGuess, response, len(valid.answers))]
    currentGuess = cachedSecondGuess(firstGuess, response, valid)
    response = compare(currentGuess, correctAnswer)

    while currentGuess != correctAnswer:
        valid.answers = valid.filterAnswers(currentGuess, response)
        guesses.append((currentGuess, response, len(valid.answers)))
        currentGuess = valid.bestGuess
        response = compare(currentGuess, correctAnswer)
    
    guesses.append((currentGuess, response, 1))

    return guesses

def play(correctAnswer, validAnswers=__validAnswers, validGuesses=__validGuesses):
    valid = Lexicon(__validAnswers, __validGuesses)
    guess = input('What is your first guess? ')
    
    response = compare(guess, correctAnswer)
    print(colorMap[response])
    numGuesses = 1

    while guess != correctAnswer:
        valid.answers = valid.filterAnswers(guess, response)
        print(f'The word could be one of: {valid.answers}.')
        print(f'Your next guess should be {valid.bestGuess}.')
        guess = input('What is your guess? ')
        response = compare(guess, correctAnswer)
        print(f'The game responds: {colorMap[response]}')
        numGuesses += 1
    
    print(f'You guessed it!  It took you {numGuesses} tries.')



if __name__ == '__main__':

    mode = input('What would you like to do? Enter analyze, play, autoplay, or solve.\n')

    if mode == 'autoplay':
        correctAnswer = random.choice(__validAnswers)
        print('Autoplay mode selected.  Game initialized.  The computer will now play the game.')
        solutionPath = autoplay(correctAnswer)
        print(f'The correct answer is: {correctAnswer}')
        print(solutionPath)
    
    if mode == 'play':
        correctAnswer = random.choice(__validAnswers)
        print('Play mode selected.  Game initialized.')
        play(correctAnswer)

    if mode == 'analyze':
        print('Analyze mode selected.  Finding solution paths for all valid puzzles.')
        out = {}
        numAnswers = len(__validAnswers)
        for i, answer in enumerate(__validAnswers):
            print(f'Solving {answer} ({i+1} out of {numAnswers})...')
            out[answer] = autoplay(answer)
        out = pd.Series(out).to_frame()
        out.columns = ['path']
        out['n'] = out.path.apply(len)
        csvPath = input('Finished analyzing.  Where would you like to output the tsv file? ')
        out.to_csv(csvPath, sep='\t', index_label='answer')

    if mode == 'solve':
        valid = Lexicon(__validAnswers, __validGuesses)
        print('Solve mode selected.\nThe best first guess is soare.')
        guess = input('Please input your first guess.\n')
        response = input('How did the game respond? 0: Black, 1: Yellow, 2: Green ')

        while response != '22222':
            print(f'Calculating next best answer for {guess}→{colorMap[response]}\n')
            valid.answers = valid.filterAnswers(guess, response)
            print(
                f'There are {len(valid.answers)} valid answers remaining: {valid.answers}.'
                '\n'
                f'The next best guess is {valid.bestGuess}.'
            )
            guess = input('Please input your next guess.\n')
            response = input('How did the game respond? 0: ⬛, 1: 🟨, 2: 🟩\n')
        
        print('Congratulations!')













