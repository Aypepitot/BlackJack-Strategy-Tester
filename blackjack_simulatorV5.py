import random
import pandas as pd
import sys


class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __repr__(self):
        return f"{self.value}{self.suit}"


class Deck:
    def __init__(self, num_decks=6):
        self.num_decks = num_decks
        self.cards = self._generate_deck()
        random.shuffle(self.cards)

    def _generate_deck(self):
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['H', 'D', 'C', 'S']
        deck = [Card(value, suit) for value in values for suit in suits] * self.num_decks
        return deck

    def draw_card(self):
        return self.cards.pop()


class CardCounter:
    def __init__(self, count_values_file='card_count_values.csv'):
        self.count_values = self._load_count_values(count_values_file)
        self.running_count = 0
        self.true_count = 0

    def _load_count_values(self, filepath):
        df = pd.read_csv(filepath, delimiter=';')
        return dict(zip(df['Card'], df['Value']))

    def update_counts(self, card, num_decks_remaining):
        self.running_count += self.count_values[card.value]
        self.true_count = self.running_count / num_decks_remaining


class Player:
    def __init__(self, initial_money=1000):
        self.money = initial_money
        self.hands = [[]]
        self.bets = [0]

    def place_bet(self, amount):
        self.bets[0] = amount
        self.money -= amount

    def double_bet(self, hand_index):
        self.money -= self.bets[hand_index]
        self.bets[hand_index] *= 2

    def receive_card(self, card, hand_index=0):
        self.hands[hand_index].append(card)

    def reset_hands(self):
        self.hands = [[]]
        self.bets = [0]

    def split_hand(self, hand_index):
        self.money -= self.bets[hand_index]
        second_card = self.hands[hand_index].pop()
        self.hands.append([second_card])
        self.bets.append(self.bets[hand_index])

    def hand_value(self, hand_index=0):
        value, aces = 0, 0
        for card in self.hands[hand_index]:
            if card.value in ['J', 'Q', 'K']:
                value += 10
            elif card.value == 'A':
                value += 11
                aces += 1
            else:
                value += int(card.value)
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def has_blackjack(self, hand_index=0):
        return self.hand_value(hand_index) == 21 and len(self.hands[hand_index]) == 2

    def display_hand(self, hand_index=0):
        return [card.value for card in self.hands[hand_index]]


class Dealer(Player):
    def __init__(self):
        super().__init__()

    def should_hit(self):
        return self.hand_value() < 17

    def reset_hands(self):
        self.hands = [[]]


class StrategyManager:
    def __init__(self, pair_strategy_file='strategy_Pair.csv', ace_strategy_file='strategy_Ace.csv',
                 hard_strategy_file='strategy_Hard.csv'):
        self.pair_strategy = self._load_strategy(pair_strategy_file)
        self.ace_strategy = self._load_strategy(ace_strategy_file)
        self.hard_strategy = self._load_strategy(hard_strategy_file)

    def _load_strategy(self, filepath):
        return pd.read_csv(filepath, delimiter=';', index_col=0)

    def get_action(self, player_hand, dealer_upcard):
        dealer_value = dealer_upcard.value
        dealer_value_map = {
            '2': 'Two', '3': 'Three', '4': 'Four', '5': 'Five', '6': 'Six', '7': 'Seven',
            '8': 'Eight', '9': 'Nine', '10': 'Ten', 'J': 'Jack', 'Q': 'Queen', 'K': 'King', 'A': 'Ace'
        }
        dealer_value = dealer_value_map[dealer_value]

        try:
            if len(player_hand) == 2 and player_hand[0].value == player_hand[1].value:
                pair_value = player_hand[0].value
                if pair_value in ['J', 'Q', 'K']:
                    pair_value = '10'
                return self.pair_strategy.loc[pair_value, dealer_value]
            elif 'A' in [card.value for card in player_hand]:
                ace_value = 'A' + (player_hand[1].value if player_hand[0].value == 'A' else player_hand[0].value)
                if ace_value in self.ace_strategy.index:
                    return self.ace_strategy.loc[ace_value, dealer_value]
                else:
                    print(f"Debug: Key {ace_value} not found in ace_strategy")
                    player_total = self._hard_value(player_hand)
                    return self.hard_strategy.loc[player_total, dealer_value]
            else:
                player_total = self._hard_value(player_hand)
                return self.hard_strategy.loc[player_total, dealer_value]
        except KeyError as e:
            print(f"Debug: KeyError {e} in strategy lookup")
            return 'S'  # Default to Stand if there's an error

    def _hard_value(self, hand):
        value = sum([10 if card.value in ['J', 'Q', 'K'] else int(card.value) for card in hand if card.value != 'A'])
        return value + 1 if 'A' in [card.value for card in hand] and value <= 10 else value


class BettingSystem:
    def __init__(self, betting_file='betting_system.csv'):
        self.betting_strategy = self._load_betting_strategy(betting_file)

    def _load_betting_strategy(self, filepath):
        df = pd.read_csv(filepath, delimiter=';')
        return dict(zip(df['TrueCount'], df['Bet']))

    def get_bet(self, true_count):
        return self.betting_strategy.get(int(true_count), 10)


class BlackjackSimulator:
    def __init__(self, count_values_file, betting_file, ace_strategy_file, pair_strategy_file, hard_strategy_file,
                 num_decks=6, penetration=0.6, base_bet=10, initial_money=1000, num_games=100):
        self.num_decks = num_decks
        self.penetration = penetration
        self.base_bet = base_bet
        self.num_games = num_games
        self.deck = Deck(self.num_decks)
        self.card_counter = CardCounter(count_values_file)
        self.player = Player(initial_money)
        self.dealer = Dealer()
        self.strategy_manager = StrategyManager(pair_strategy_file, ace_strategy_file, hard_strategy_file)
        self.betting_system = BettingSystem(betting_file)
        self.results = []

    def simulate(self):
        for _ in range(self.num_games):
            self.play_game()
            if len(self.deck.cards) < self.num_decks * 52 * self.penetration:
                self.deck = Deck(self.num_decks)

        self.display_stats()

    def play_game(self):
        self.player.reset_hands()
        self.dealer.reset_hands()
        self.player.place_bet(self.betting_system.get_bet(self.card_counter.true_count))

        self.player.receive_card(self.deck.draw_card())
        self.dealer.receive_card(self.deck.draw_card())
        self.player.receive_card(self.deck.draw_card())
        self.dealer.receive_card(self.deck.draw_card())

        if self.player.has_blackjack():
            self.player.money += self.player.bets[0] * 2.5
            result = 'Player'
            self.log_result(result, [], [], 0)
        else:
            hand_indices = list(range(len(self.player.hands)))
            player_actions = [[] for _ in hand_indices]

            for hand_index in hand_indices:
                actions = self.player_turn(hand_index, player_actions)
                player_actions[hand_index].extend(actions)

            dealer_actions = self.dealer_turn()

            for hand_index in range(len(self.player.hands)):
                result = self.determine_winner(hand_index)
                self.update_money(result, hand_index)
                self.log_result(result, player_actions[hand_index], dealer_actions, hand_index)

    def player_turn(self, hand_index, player_actions):
        actions = []
        surrender_allowed = True
        double_allowed = True
        while True:
            action = self.strategy_manager.get_action(self.player.hands[hand_index],
                                                      self.dealer.hands[0][0])  # Access the dealer's upcard correctly
            if isinstance(action, pd.Series):
                action = action.values[0]
            if action == 'Sr' and not surrender_allowed:
                action = 'S'
            if action == 'D' and not double_allowed:
                action = 'H'
            actions.append(action)
            if action == 'H':
                self.player.receive_card(self.deck.draw_card(), hand_index)
                surrender_allowed = False
                double_allowed = False
            elif action == 'S':
                break
            elif action == 'D':
                self.player.double_bet(hand_index)
                self.player.receive_card(self.deck.draw_card(), hand_index)
                break
            elif action == 'P':
                self.log_result('Split', actions, [], hand_index)
                self.player.split_hand(hand_index)
                player_actions.append([])  # Ensure player_actions list is updated for the new hand
                for new_hand_index in [hand_index, len(self.player.hands) - 1]:
                    self.player.receive_card(self.deck.draw_card(), new_hand_index)
                    split_actions = self.player_turn(new_hand_index, player_actions)
                    player_actions[new_hand_index].extend(split_actions)
                return actions
            elif action == 'Sr':
                self.player.money += self.player.bets[hand_index] // 2
                self.player.bets[hand_index] = 0
                break

            if self.player.hand_value(hand_index) > 21:
                break
        return actions

    def dealer_turn(self):
        actions = []
        while self.dealer.should_hit():
            actions.append('H')
            self.dealer.receive_card(self.deck.draw_card())
        actions.append('S')
        return actions

    def determine_winner(self, hand_index):
        player_value = self.player.hand_value(hand_index)
        dealer_value = self.dealer.hand_value()

        if player_value > 21:
            return 'Dealer'
        if dealer_value > 21 or player_value > dealer_value:
            return 'Player'
        if player_value < dealer_value:
            return 'Dealer'
        return 'Push'

    def update_money(self, result, hand_index):
        if result == 'Player':
            self.player.money += self.player.bets[hand_index] * 2
        elif result == 'Push':
            self.player.money += self.player.bets[hand_index]

    def log_result(self, result, player_actions, dealer_actions, hand_index):
        log = {
            'Bet': self.player.bets[hand_index],
            'Player Hand': self.player.display_hand(hand_index),
            'Player Total': self.player.hand_value(hand_index),
            'Dealer Hand': self.dealer.display_hand(),
            'Dealer Total': self.dealer.hand_value(),
            'Result': result,
            'Player Money': self.player.money,
            'Running Count': self.card_counter.running_count,
            'True Count': self.card_counter.true_count,
            'Player Actions': player_actions
        }
        self.results.append(log)
        print(log)

    def display_stats(self):
        wins = len([result for result in self.results if result['Result'] == 'Player'])
        losses = len([result for result in self.results if result['Result'] == 'Dealer'])
        pushes = len([result for result in self.results if result['Result'] == 'Push'])
        total_games = len(self.results)
        highest_money = max(result['Player Money'] for result in self.results)
        lowest_money = min(result['Player Money'] for result in self.results)

        print(f"Simulation finished. Total games: {total_games}")
        print(f"Player wins: {wins} ({wins / total_games * 100:.2f}%)")
        print(f"Dealer wins: {losses} ({losses / total_games * 100:.2f}%)")
        print(f"Pushes: {pushes} ({pushes / total_games * 100:.2f}%)")
        print(f"Player's final money: {self.player.money}")
        print(f"Highest money: {highest_money}")
        print(f"Lowest money: {lowest_money}")


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print(
            "Usage: python blackjack_simulatorV5.py card_count_values.csv betting_system.csv strategy_Ace.csv strategy_Pair.csv strategy_Hard.csv")
        sys.exit(1)
    card_count_values_file = sys.argv[1]
    betting_system_file = sys.argv[2]
    strategy_ace_file = sys.argv[3]
    strategy_pair_file = sys.argv[4]
    strategy_hard_file = sys.argv[5]

    simulator = BlackjackSimulator(card_count_values_file, betting_system_file, strategy_ace_file, strategy_pair_file,
                                   strategy_hard_file, num_games=1000)
    simulator.simulate()