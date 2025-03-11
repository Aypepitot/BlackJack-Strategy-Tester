trying to implement strategy test black jack to see if basic strategy is the best strategy

Command line to play the simulation :
python blackjack_simulatorV5.py card_count_values.csv betting_system.csv strategy_Ace.csv strategy_Pair.csv strategy_Hard.csv

With V5 version. Following basic strategy,with 5000 games my average stat is :
Player : 39%
Dealer 52%
Pushes : 6%
I know it don't equal to 100% but who cares...

With V6 and implementation of SrS (Surrender if possible if not Stand) and SrH (same but hit), correction of Ace hands and 50000 games. I also add Nb game (from one simulation) and final money to see impact of double / bettings system for the futur  
My average stats :
Simulation finished. Total games: 52944
Player wins: 22350 (42.21%)
Dealer wins: 24978 (47.18%)
Pushes: 4144 (7.83%)
Player's final money: 3170.0
Highest money: 3985.0
Lowest money: 735.0
Slightly better but now I can make more variation of basic strategy

Variante 1 Instead of double in Ace strategy just hit :
Simulation finished. Total games: 52964
Player wins: 22359 (42.22%)
Dealer wins: 24870 (46.96%)
Pushes: 4253 (8.03%)
Player's final money: 1400.0
Highest money: 4250.0
Lowest money: 640.0
