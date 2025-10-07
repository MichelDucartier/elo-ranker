from typing import Tuple
from elo_ranker.api.ranked_entry import RankedEntry
from elo_ranker.api.ranking import BattleResult, EloRanking

import random

class MatchMaker:
    def __init__(self, ranking: EloRanking):
        self.ranking = ranking


    def match(self) -> Tuple[RankedEntry, RankedEntry]:
        sorted_items = [v for k,v in sorted(self.ranking.id2entry, 
                                            key=lambda item : item[1])]
        
        selected_len = max(2, 0.1 * len(sorted_items))
        selected_items = sorted_items[:selected_len]

        entry1, entry2 = random.sample(selected_items, 2)

        return entry1, entry2


    def register_match_result(self, entry1: RankedEntry, 
                              entry2: RankedEntry,
                              result: BattleResult):
        self.ranking.update_with_results(
                entry1, entry2, result
        )
    

