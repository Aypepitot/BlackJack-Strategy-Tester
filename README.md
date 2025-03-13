trying to implement strategy test black jack to see if basic strategy is the best strategy

Command line to play the simulation :
python blackjack_simulatorV6.py card_count_values.csv betting_system.csv strategy_Ace.csv strategy_Pair.csv strategy_Hard.csv

Basic strategy ENHC stats : (from 3 simulations of 50000 games)

Player wins: 21612 (42.02%)
Dealer wins: 20611 (40.08%)
Surrenders: 5180 (10.07%)
Pushes: 4027 (7.83%)
Player's final money: 4120.0
Highest money: 4895.0
Lowest money: 590.0

Player wins: 21425 (41.56%)
Dealer wins: 20751 (40.25%)
Surrenders: 5140 (9.97%)
Pushes: 4235 (8.22%)
Player's final money: 1005.0
Highest money: 1640.0
Lowest money: -1875.0

Player wins: 21467 (41.67%)
Dealer wins: 20642 (40.07%)
Surrenders: 5261 (10.21%)
Pushes: 4147 (8.05%)
Player's final money: 1975.0
Highest money: 3555.0
Lowest money: -210.0

Trying to change basic strategy 12 -> 17 players versus 7 to Ace dealer in Full SrS

Player wins: 19182 (37.27%)
Dealer wins: 15495 (30.10%)
Surrenders: 13643 (26.51%)
Pushes: 3153 (6.13%)

Trying to change basic strategy 12 -> 17 players versus 7 to Ace dealer in Full SrH :

Player wins: 19252 (37.46%)
Dealer wins: 15271 (29.71%)
Surrenders: 13621 (26.50%)
Pushes: 3256 (6.33%)
Player's final money: -6320.0
Highest money: 1640.0
Lowest money: -6460.0

Trying to change basic strategy 12 -> 17 players versus 7 to Ace dealer in Full H :

Player wins: 22336 (43.43%)
Dealer wins: 24919 (48.46%)
Surrenders: 199 (0.39%)
Pushes: 3971 (7.72%)
Player's final money: -6400.0
Highest money: 1800.0
Lowest money: -6495.0

Trying to change basic strategy 12 -> 17 players versus 7 to Ace dealer in Full S :

Player wins: 22252 (43.25%)
Dealer wins: 25609 (49.78%)
Surrenders: 189 (0.37%)
Pushes: 3394 (6.60%)
Player's final money: -13545.0
Highest money: 1060.0
Lowest money: -13950.0

Double at 12 againt 7 and more expect Ace

Player wins: 21587 (41.99%)
Dealer wins: 20466 (39.81%)
Surrenders: 5209 (10.13%)
Pushes: 4143 (8.06%)
Player's final money: -2480.0
Highest money: 1490.0
Lowest money: -2490.0

Double at 12 againt 6 and less :

Player wins: 21638 (42.05%)
Dealer wins: 20524 (39.89%)
Surrenders: 5171 (10.05%)
Pushes: 4119 (8.01%)
Player's final money: 3170.0
Highest money: 3230.0
Lowest money: -545.0

Fulle double at 12 exept Ace :

Player wins: 21553 (41.87%)
Dealer wins: 20461 (39.75%)
Surrenders: 5319 (10.33%)
Pushes: 4137 (8.04%)
Player's final money: -5825.0
Highest money: 2030.0
Lowest money: -6525.0

Double all small hand to 12 include agains 6 and less but SrH for 5 to 9 :

Player wins: 21125 (41.09%)
Dealer wins: 20783 (40.43%)
Surrenders: 5493 (10.69%)
Pushes: 4006 (7.79%)
Player's final money: -9705.0
Highest money: 1150.0
Lowest money: -9830.0

Strat le chat 1 plus aggresive :13/03/25:

Player wins: 22167 (43.07%)
Dealer wins: 25247 (49.05%)
Surrenders: 0 (0.00%)
Pushes: 4055 (7.88%)
Player's final money: -13330.0
Highest money: 1060
Lowest money: -13450.0

Strat le chat Variation 2 : Stratégie plus conservatrice :

Player wins: 21258 (41.27%)
Dealer wins: 27506 (53.40%)
Surrenders: 0 (0.00%)
Pushes: 2750 (5.34%)
Player's final money: -43475.0
Highest money: 1050
Lowest money: -43485.0

Variation 3 : Stratégie avec plus de "Surrender"

Player wins: 12804 (24.89%)
Dealer wins: 6569 (12.77%)
Surrenders: 29615 (57.58%)
Pushes: 2445 (4.75%)
Player's final money: -65855.0
Highest money: 1015.0
Lowest money: -65880.0

Variation 4 : Stratégie avec moins de "Double" :

Player wins: 22343 (43.37%)
Dealer wins: 24619 (47.79%)
Surrenders: 0 (0.00%)
Pushes: 4550 (8.83%)
Player's final money: -8750.0
Highest money: 1940.0
Lowest money: -9225.0

Alternative Chat GPT

Player wins: 21426 (41.67%)
Dealer wins: 20647 (40.15%)
Surrenders: 5910 (11.49%)
Pushes: 3439 (6.69%)
Player's final money: -705.0
Highest money: 1785.0
Lowest money: -2120.0

Alternative 2 :

Player wins: 20924 (40.65%)
Dealer wins: 20948 (40.70%)
Surrenders: 5907 (11.48%)
Pushes: 3696 (7.18%)
Player's final money: -8925.0
Highest money: 1190.0
Lowest money: -9195.0





