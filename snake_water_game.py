# Snake water and gun game

print("choices:\n1 = snake\n2 = water\n3 = gun\nexit = to exit the game")

try:
    max_pt = int(input("Enter the maximum points to win: "))
    p1 = 0
    p2 = 0

    while p1 != max_pt and p2 != max_pt:
        c1 = input("Enter choice 1: ")
        c2 = input("Enter choice 2: ")
        chose = {c1, c2}

        if c1 == 'exit' or c2 == 'exit':
            break

        if c1 == c2:
            print("Same choices! No points awarded.")
            continue

        if chose == {'1', '2'}:
            if c1 == '1' and c2 == '2':
                p1 += 1
                p2 -= 1
                print("Snake beats Water: Player 1 wins")
            else:
                p2 += 1
                p1 -= 1
                print("Snake beats Water: Player 2 wins")

        elif chose == {'2', '3'}:
            if c1 == '2' and c2 == '3':
                p1 += 1
                p2 -= 1
                print("Water beats Gun: Player 1 wins")
            else:
                p2 += 1
                p1 -= 1
                print("Water beats Gun: Player 2 wins")

        elif chose == {'1', '3'}:
            if c1 == '3' and c2 == '1':
                p1 += 1
                p2 -= 1
                print("Gun beats Snake: Player 1 wins")
            else:
                p2 += 1
                p1 -= 1
                print("Gun beats Snake: Player 2 wins")

        else:
            print("Invalid choices!")

    print("\nGame finished!")
    print(f"Total points earned by Player 1 and Player 2 respectively: {p1} and {p2}")

    if p1 == p2:
        print("Match Draw!")
    else:
        print("CONGRATS PLAYER 1!! YOU WON THE MATCH") if p1 > p2 else print("CONGRATS PLAYER 2!! YOU WON THE MATCH")

except:
    print("Error! Please improve your input.")

