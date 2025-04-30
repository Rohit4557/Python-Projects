# Rock paper scissor game

import random

options=("r","p","s")
emoji={"r":"🪨", "p": "📜", "s": "✂️" }

while True:
    user_choice=input("Rock,paper or scissor (r/p/s): ").lower()
    if user_choice not in options:
            print("invalid choice!")
            continue

    computer_choice=random.choice(options)

    print(f'you chose {emoji.get(user_choice)}')
    print(f'Computer chose {emoji.get(computer_choice)}')
    if user_choice==computer_choice:
        print("Match draw!") 
    elif (
        (user_choice=='p' and computer_choice=='r') or 
        (user_choice=='s' and computer_choice=='p') or 
        (user_choice=='r' and computer_choice=='s')):
        print('You WIN😍')
    else:
        print("YOU LOSE😐")

    should_continue=input("Continue? (y/n): ").lower()
    if should_continue=='n':
        print("Match ends!")
        break
    else:
         pass
    