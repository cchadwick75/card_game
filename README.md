
## Installation

### 1.  Clone Repository Game repository
```git clone https://github.com/cchadwick75/card_game```

### 2.  Activate Virtual Environment
Navigate to card_game directory and run the following command
```source venv/bin/activate```

### 3.  Install requirements.txt while inside (venv)
```pip3 install -r requirements.txt```

### Installation Complete

## Rules
+ ### 1.  Card Rules
+ There are 4 Colors in the Deck, here are the colors and points associated
  * BLUE = 4
  * RED = 3
  * YELLOW = 2
  * GREEN = 1
  
+ Each Card Color has a set of numbers.  Much like a regular deck of cards.  The Range for each color is 2-7.  So your hand could have a Blue 2 and a Blue 4.
+ Each player gets 3 cards randomly drawn from the deck. 
+ Once each player has 3 cards the total scores are calculated.  
+ Each players score is calculated by points associated with card color * the card number.
+ For instance a BLUE 5 would have a total of 20 points according to list above. 
  
+ ### 2.  How To Run/Play
This will show you how to play interactively and display example screenshots of results.
  + ##### A.  Call Program 
  + ``` python card_game_play.py ```
  + ##### B. Type Y when prompted to play game
  + ``` Play Color Cards?  : (y/n) : ```
  + ##### C.  Sort Deck with a Y, or N to not sort deck
  + ``` Sort deck by color specific colors : Y/N```
  + ##### D.  Sort Deck with a Y, or N to not sort deck
  + ##### E.  If sorting the deck, enter a comma seperated group of deck colors.  This will sort by the color and number will be ascending.  see below for example
  + ```Type Colors:  Choices(BLUE GREEN RED YELLOW): separate by comma blue, green```
  + NOTE:  it should be noted that any other entries or misspellings of colors will not sort.  
  + NOTE:  Sorted order will be displayed, below is an example
  + ```here is your sorted deck: [('BLUE', 2), ('BLUE', 3), ('BLUE', 4), ('BLUE', 5), ('BLUE', 6), ('BLUE', 7), ('GREEN', 2), ('GREEN', 3), ('GREEN', 4), ('GREEN', 5), ('GREEN', 6), ('GREEN', 7), ('YELLOW', 3), ('RED', 7), ('YELLOW', 5), ('YELLOW', 6), ('YELLOW', 7), ('YELLOW', 4), ('RED', 3), ('RED', 5), ('RED', 6), ('RED', 2), ('YELLOW', 2), ('RED', 4)]```

  + ##### F.  Enter Name
  + ``` Player 1 Enter Your Name:  ```

  + ##### G.  Enter Number of Players
  + NOTE: Max amount of players is 2.  1 Player will play against the computer
  + ```Select 1 Player or 2 Players : type 1 or 2  ```
  + ##### H.  Draw your card by pressing Y, you will perform this task until all your cards(3 times) are drawn.  
  + ```collin, select a card.  Type Y to Draw from Deck:  y```
  + ```collin's hand:```
  + ```[('GREEN', 4)]```
  + ```Windows 95's hand:```
  + ```[('RED', 2)]```
  
  + ##### I.See totals and game ends
```
collin's hand:
[('GREEN', 4), ('RED', 7), ('YELLOW', 6)]
Windows 95's hand:
[('RED', 2), ('BLUE', 5), ('GREEN', 5)]
Game Is Over
collin: 37


Windows 95: 31


collin Wins

```
+ ### End of Game How To.

+ ### 3.  How To Run pytest
+ From Command Line Enter:
+ ``` pytest test_card_game_play.py```




    
    
    

