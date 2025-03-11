trying to implement strategy test black jack to see if basic strategy is the best strategy

Command line to play the simulation :
python blackjack_simulatorV5.py card_count_values.csv betting_system.csv strategy_Ace.csv strategy_Pair.csv strategy_Hard.csv

With V5 version. Following basic strategy,with 5000 games my average stat is :
Player : 39%
Dealer 52%
Pushes : 6%
I know it don't equal to 100% but who cares...

With V6 and implementation of SrS (Surrender if possible if not Stand) and SrH (same but hit) and still 5000 games. I also add Nb game (from one simulation) and final money to see impact of double / bettings system for the futur  
My average stats :
Player : 39%
Dealer 51%
Pushes : 7%
Nb game : 5300
Player final money : -2755
Slightly better but now I can make more varaition of basic strategy
I know it don't equal to 100% but who cares...
