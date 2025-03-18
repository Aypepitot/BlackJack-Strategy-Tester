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

    def draw_card(self, card_counter):
        card = self.cards.pop()
        num_decks_remaining = len(self.cards) / 52
        card_counter.update_counts(card, num_decks_remaining)
        return card


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
    def __init__(self, initial_money=100):
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
                # Trouver la valeur des cartes autres que l'As
                other_cards = [card for card in player_hand if card.value != 'A']
                other_sum = sum(10 if card.value in ['J', 'Q', 'K'] else int(card.value) for card in other_cards)
                if other_sum <= 10:
                    ace_value = 'A' + str(other_sum)
                    if ace_value in self.ace_strategy.index:
                        return self.ace_strategy.loc[ace_value, dealer_value]
                    else:
                        print(f"Debug: Key {ace_value} not found in ace_strategy")

                    # Si la somme dépasse 10 ou si la clé n'est pas trouvée, on traite comme une main dure
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
                 num_decks=6, penetration=0.6, base_bet=10, initial_money=100, num_games=100):
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

        self.player.receive_card(self.deck.draw_card(self.card_counter))
        self.dealer.receive_card(self.deck.draw_card(self.card_counter))
        self.player.receive_card(self.deck.draw_card(self.card_counter))
        self.dealer.receive_card(self.deck.draw_card(self.card_counter))

        if len(self.deck.cards) < self.num_decks * 52 * (1 - self.penetration):
            print(f"🔄 Remélange du deck (Pénétration : {self.penetration * 100:.0f}%)")
            self.deck = Deck(self.num_decks)  # Nouveau deck mélangé
            self.card_counter.running_count = 0  # Réinitialiser le running count

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

            if action == 'SrH' and not surrender_allowed:
                action = 'H'
            if action == 'SrS' and not surrender_allowed:
                action = 'S'
            if action == 'D' and not double_allowed:
                action = 'H'

            actions.append(action)

            if action == 'H':
                self.player.receive_card(self.deck.draw_card(self.card_counter), hand_index)
                surrender_allowed = False
                double_allowed = False
            elif action == 'S':
                break
            elif action == 'D':
                self.player.double_bet(hand_index)
                self.player.receive_card(self.deck.draw_card(self.card_counter), hand_index)
                break
            elif action == 'P':
                self.log_result('Split', actions, [], hand_index)
                self.player.split_hand(hand_index)
                player_actions.append([])  # Ensure player_actions list is updated for the new hand
                for new_hand_index in [hand_index, len(self.player.hands) - 1]:
                    self.player.receive_card(self.deck.draw_card(self.card_counter), new_hand_index)
                    split_actions = self.player_turn(new_hand_index, player_actions)
                    player_actions[new_hand_index].extend(split_actions)
                return actions
            elif action in ['SrH', 'SrS']:
                if surrender_allowed:
                    self.player.money += self.player.bets[hand_index] // 2
                    self.player.bets[hand_index] = 0
                    return actions
                    break

            if self.player.hand_value(hand_index) > 21:
                break
        return actions

    def dealer_turn(self):
        actions = []
        while self.dealer.should_hit():
            actions.append('H')
            self.dealer.receive_card(self.deck.draw_card(self.card_counter))
        actions.append('S')
        return actions

    def determine_winner(self, hand_index):

        if self.player.bets[hand_index] == 0:
            return 'Surrender'
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
        remaining_cards = len(self.deck.cards)
        total_cards = self.num_decks * 52
        percentage_remaining = (remaining_cards / total_cards) * 100
        log = {
            'Bet': self.player.bets[hand_index],
            'Player Hand': self.player.display_hand(hand_index),
            'Player Total': self.player.hand_value(hand_index),
            'Dealer Hand': self.dealer.display_hand(),
            'Dealer Total': self.dealer.hand_value(),
            'Result': result,
            'Player Money': self.player.money,
            'Running Count': self.card_counter.running_count,
            'True Count': f"{self.card_counter.true_count:.2f}",
            'Remaining Cards': remaining_cards,
            'Percentage Remaining': f"{percentage_remaining:.2f}%",
            'Player Actions': player_actions
        }
        self.results.append(log)
        print(log)

    def display_stats(self):
        wins = len([result for result in self.results if result['Result'] == 'Player'])
        losses = len([result for result in self.results if result['Result'] == 'Dealer'])
        surrenders = len([result for result in self.results if result['Result'] == 'Surrender'])
        pushes = len([result for result in self.results if result['Result'] == 'Push'])
        total_games = len(self.results) - len([result for result in self.results if result['Result'] == 'Split'])
        highest_money = max(result['Player Money'] for result in self.results)
        lowest_money = min(result['Player Money'] for result in self.results)
        total_cards = self.num_decks * 52
        remaining_cards = len(self.deck.cards)
        percentage_remaining = (remaining_cards / total_cards) * 100

        print(f"Simulation finished. Total games: {total_games}")
        print(f"Player wins: {wins} ({wins / total_games * 100:.2f}%)")
        print(f"Dealer wins: {losses} ({losses / total_games * 100:.2f}%)")
        print(f"Surrenders: {surrenders} ({surrenders / total_games * 100:.2f}%)")
        print(f"Pushes: {pushes} ({pushes / total_games * 100:.2f}%)")
        print(f"Player's final money: {self.player.money}")
        print(f"Highest money: {highest_money}")
        print(f"Lowest money: {lowest_money}")
        print(f"Remaining cards: {remaining_cards} ({percentage_remaining:.2f}%)")


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
                                   strategy_hard_file, num_games=10)
    simulator.simulate()

import threading
import tkinter as tk
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class BlackjackGUI:
    def __init__(self, root, simulator):
        self.root = root
        self.simulator = simulator
        self.root.title("Blackjack Simulator")
        self.root.state('zoomed')  # Plein écran

        # Champ pour saisir le nombre de parties
        self.num_games_label = tk.Label(root, text="Nombre de parties:")
        self.num_games_label.pack()
        self.num_games_entry = tk.Entry(root)
        self.num_games_entry.insert(0, "200")  # Valeur par défaut
        self.num_games_entry.pack()

        # Champ pour saisir la somme de départ
        self.initial_money_label = tk.Label(root, text="Somme de départ (€):")
        self.initial_money_label.pack()
        self.initial_money_entry = tk.Entry(root)
        self.initial_money_entry.insert(0, "100")  # Valeur par défaut
        self.initial_money_entry.pack()

        # Bouton pour démarrer la simulation
        self.start_button = tk.Button(root, text="Lancer la Simulation", command=self.run_simulation)
        self.start_button.pack(pady=10)

        # Création des graphiques
        self.figure = Figure(figsize=(12, 6), dpi=100)

        # Graphique pour l'évolution de l'argent
        self.ax_money = self.figure.add_subplot(211)
        self.ax_money.set_title("Évolution de l'Argent")
        self.ax_money.set_xlabel("Nombre de parties")
        self.ax_money.set_ylabel("Argent (€)")

        # Axe secondaire pour une autre métrique
        self.ax_secondary = self.ax_money.twinx()
        self.ax_secondary.set_ylabel("True Count")

        # Graphique pour les pourcentages de résultats
        self.ax_percentages = self.figure.add_subplot(212)
        self.ax_percentages.set_title("Pourcentages de Résultats")
        self.ax_percentages.set_xlabel("Nombre de parties")
        self.ax_percentages.set_ylabel("Pourcentage (%)")

        # Intégration des graphes à l'interface Tkinter
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def run_simulation(self):
        """ Lance la simulation dans un thread séparé pour ne pas bloquer l'interface graphique """
        # Mettre à jour les paramètres de la simulation avec les valeurs saisies par l'utilisateur
        self.simulator.num_games = int(self.num_games_entry.get())
        self.simulator.player.money = int(self.initial_money_entry.get())

        # Réinitialiser les graphiques
        self.ax_money.clear()
        self.ax_money.set_title("Évolution de l'Argent", fontsize=14)
        self.ax_money.set_xlabel("Nombre de parties", fontsize=12)
        self.ax_money.set_ylabel("Argent (€)", fontsize=12)
        self.ax_money.grid(True, linestyle='--', alpha=0.6)

        self.ax_secondary.clear()
        self.ax_secondary.set_ylabel("True Count")

        self.ax_percentages.clear()
        self.ax_percentages.set_title("Pourcentages de Résultats", fontsize=14)
        self.ax_percentages.set_xlabel("Nombre de parties", fontsize=12)
        self.ax_percentages.set_ylabel("Pourcentage (%)", fontsize=12)
        self.ax_percentages.grid(True, linestyle='--', alpha=0.6)

        self.canvas.draw()

        # Lancer la simulation dans un thread séparé
        simulation_thread = threading.Thread(target=self.run_simulation_thread, daemon=True)
        simulation_thread.start()

    def run_simulation_thread(self):
        """ Fonction exécutée en arrière-plan pour mettre à jour la simulation en temps réel """
        self.simulator.results = []  # Réinitialiser les résultats
        money_history = []
        true_count_history = []
        results_count = {'Player': 0, 'Dealer': 0, 'Surrender': 0, 'Push': 0}
        percentages_history = {'Player': [], 'Dealer': [], 'Surrender': [], 'Push': []}

        update_interval = max(1, self.simulator.num_games // 10)  # Mettre à jour moins fréquemment pour plus de fluidité

        for i in range(self.simulator.num_games):
            self.simulator.play_game()  # Joue une partie
            money_history.append(self.simulator.player.money)  # Enregistre l'évolution de l'argent
            true_count_history.append(self.simulator.card_counter.true_count)  # Enregistre l'évolution du true count

            # Mettre à jour les comptes de résultats
            result = self.simulator.results[-1]['Result']
            if result in results_count:
                results_count[result] += 1

            # Calculer les pourcentages
            total_games_played = i + 1
            for key in results_count:
                percentages_history[key].append((results_count[key] / total_games_played) * 100)

            # Mise à jour des graphiques à un intervalle défini
            if i % update_interval == 0 or i == self.simulator.num_games - 1:
                self.update_graphs(money_history, true_count_history, percentages_history)

    def update_graphs(self, money_history, true_count_history, percentages_history):
        """ Met à jour les graphiques en appelant Tkinter depuis le thread principal """
        # Mettre à jour le graphique de l'argent
        self.ax_money.clear()
        sns.lineplot(x=range(1, len(money_history) + 1), y=money_history, ax=self.ax_money, color='blue', label='Argent')
        self.ax_money.set_title("Évolution de l'Argent", fontsize=14)
        self.ax_money.set_xlabel("Nombre de parties", fontsize=12)
        self.ax_money.set_ylabel("Argent (€)", fontsize=12)
        self.ax_money.grid(True, linestyle='--', alpha=0.6)

        # Mettre à jour l'axe secondaire avec le true count
        self.ax_secondary.clear()
        sns.lineplot(x=range(1, len(true_count_history) + 1), y=true_count_history, ax=self.ax_secondary, color='orange', label='True Count')
        self.ax_secondary.set_ylabel("True Count")

        # Mettre à jour le graphique des pourcentages
        self.ax_percentages.clear()
        for key, color in zip(percentages_history.keys(), ['green', 'red', 'purple', 'orange']):
            sns.lineplot(x=range(1, len(percentages_history[key]) + 1), y=percentages_history[key], ax=self.ax_percentages, label=key, color=color)
        self.ax_percentages.set_title("Pourcentages de Résultats", fontsize=14)
        self.ax_percentages.set_xlabel("Nombre de parties", fontsize=12)
        self.ax_percentages.set_ylabel("Pourcentage (%)", fontsize=12)
        self.ax_percentages.legend()
        self.ax_percentages.grid(True, linestyle='--', alpha=0.6)

        self.canvas.draw()
        self.root.after(1, self.canvas.draw)  # Forcer le rafraîchissement graphique avec Tkinter

# Lancement de l'interface graphique
if __name__ == "__main__":
    root = tk.Tk()
    simulator = BlackjackSimulator(
        "card_count_values.csv", "betting_system.csv", "strategy_Ace.csv",
        "strategy_Pair.csv", "strategy_Hard.csv", num_decks=6, penetration=0.75,
        num_games=200  # Valeur par défaut, sera remplacée par l'entrée utilisateur
    )
    app = BlackjackGUI(root, simulator)
    root.mainloop()

