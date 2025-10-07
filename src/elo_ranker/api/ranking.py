from __future__ import annotations

from typing import Dict, List

import rich
from .constants import ATTRIBUTES_KEY, DEFAULT_INITIAL_ELO, DEFAULT_SPREAD, ENTRIES_KEY, INITIAL_ELO_KEY, SPREAD_KEY, TITLE_KEY
from .ranked_entry import RankedEntry
import pickle
import yaml
import enum

import uuid

class BattleResult(enum.IntEnum):
    DRAW = 0
    ENTRY1_WIN = 1
    ENTRY2_WIN = 2


class EloRanking:
    def __init__(self, entries: List[RankedEntry], 
                 initial_elo: int,
                 spread: int) -> None:
        self.id2elo = dict()
        self.id2entry = dict()
        self.id2num_matches = dict()
        
        self.spread = spread

        for entry in entries:
            unique_id = entry.uid()
            self.id2entry[unique_id] = entry
            self.id2elo[unique_id] = initial_elo
            self.id2num_matches[unique_id] = 0

    def save_ranking(self, filename: str):
        with open(filename, "wb") as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def update_with_results(
            self,
            entry1: RankedEntry, 
            entry2: RankedEntry, 
            result: BattleResult):

        print(result)

        elo1 = self.id2elo[entry1.uid()]
        elo2 = self.id2elo[entry2.uid()]

        expected1 = 1 / (1 + 10 ** ((elo2 - elo1) / self.spread))
        expected2 = 1 - expected1
        
        lr = max(self.get_learning_rate(entry1), self.get_learning_rate(entry2))
        
        entry1_win = -1

        if result == BattleResult.DRAW:
            entry1_win = 0.5
        elif result == BattleResult.ENTRY1_WIN:
            entry1_win = 1
        else:
            entry1_win = 0
        entry2_win = 1 - entry1_win
        
        updated_elo1 = elo1 + lr * (entry1_win - expected1)
        updated_elo2 = elo2 + lr * (entry2_win - expected2)

        self.id2elo[entry1.uid()] = updated_elo1
        self.id2elo[entry2.uid()] = updated_elo2

        self.id2num_matches[entry1.uid()] += 1
        self.id2num_matches[entry2.uid()] += 1


    def get_learning_rate(self, entry: RankedEntry) -> int:
        # FIDE def (according to ChatGPT :))
        unique_id = entry.uid()
        num_matches = self.id2num_matches[unique_id]
        rating = self.id2elo[unique_id]

        if num_matches < 30:
            return 40

        if rating < 2400:
            return 20

        return 10
    
    @staticmethod
    def load_ranking(filename: str) -> EloRanking:
        with open(filename, "rb") as f:
            elo_ranking = pickle.load(f)

        return elo_ranking

    @staticmethod
    def from_config(config_path: str) -> EloRanking:
        with open(config_path, "r") as f:
            config_dict = yaml.safe_load(f)
        
        if ENTRIES_KEY not in config_dict:
            raise ValueError(f"Config dict has no key {ENTRIES_KEY}")
        
        entries = list()
        for entry_dict in config_dict[ENTRIES_KEY]:

            if TITLE_KEY not in entry_dict:
                raise ValueError(f"Missing {TITLE_KEY} in entry {entry_dict}")
             
            entry = RankedEntry(
                    entry_dict[TITLE_KEY], 
                    entry_dict.get(ATTRIBUTES_KEY)
            )

            entries.append(entry)


        return EloRanking(
                entries,
                config_dict.get(INITIAL_ELO_KEY, DEFAULT_INITIAL_ELO),
                config_dict.get(SPREAD_KEY, DEFAULT_SPREAD)
        )


    def pretty_print(self):
        """Pretty prints all elements sorted by elo (from best to worst)."""
        sorted_entries = sorted(self.id2elo.items(), key=lambda x: x[1], reverse=True)

        rich.print("Elo Rankings (from best to worst):")
        for i, (uid, elo) in enumerate(sorted_entries, start=1):
            entry = self.id2entry[uid]
            rich.print(f"{i}. {entry.title} - Elo: {elo}")
