from typing import List, Set, Tuple
from .ranked_entry import RankedEntry
from .ranking import BattleResult, EloRanking

import random

class MatchMaker:
    def __init__(self, ranking: EloRanking, window_ratio: float = 1.0):
        self.ranking = ranking
        self.window_ratio = window_ratio


    def _match(self, entries: Set[RankedEntry]) -> Tuple[RankedEntry, RankedEntry]:
        window_entries = random.sample(
                list(entries),
                k=int(self.window_ratio * len(entries))
        )
        
        closest_pairs = list()
        smallest_diff = float("inf")

        for entry1 in entries:
            id1 = entry1.uid()
            for entry2 in window_entries:
                id2 = entry2.uid()

                if id2 == id1:
                    continue

                elo1 = self.ranking.id2elo[id1]
                elo2 = self.ranking.id2elo[id2]

                diff = abs(elo1 - elo2)
                # if diff == smallest_diff:
                closest_pairs.append((id1, id2))

                # if diff < smallest_diff:
                #     smallest_diff = diff
                #     closest_pairs = [(id1, id2)]
        
        sampled_pair = random.choice(closest_pairs)
        entry1 = self.ranking.id2entry[sampled_pair[0]]
        entry2 = self.ranking.id2entry[sampled_pair[1]]

        return entry1, entry2

    
    def match(self) -> Tuple[RankedEntry, RankedEntry]:
        return self.batch_match(batch_size=1)[0]

    
    def batch_match(self, batch_size: int = 2) -> List[Tuple[RankedEntry, RankedEntry]]:
        matches = []
        entries = set(self.ranking.id2entry.values())
        for _ in range(batch_size):
            entry1, entry2 = self._match(entries)
            matches.append((entry1, entry2))
            entries.remove(entry1)
            entries.remove(entry2)

        return matches


    def register_match_result(self, entry1: RankedEntry, 
                              entry2: RankedEntry,
                              result: BattleResult):
        self.ranking.update_with_results(
                entry1, entry2, result
        )
    

