import argparse
import rich
from rich.prompt import Prompt
import warnings

from src.elo_ranker.api.match_maker import MatchMaker
from src.elo_ranker.api.ranking import BattleResult, EloRanking

from rich.console import Console
from rich.rule import Rule

import random

def handle_match():
    entry1, entry2 = MATCH_MAKER.match()
    
    rich.print("Entry 1")
    rich.print(entry1)

    rich.print("=" * 50)

    rich.print("Entry 2")
    rich.print(entry2)

    winner = int(Prompt.ask("Winner (0 for draw)", choices=["0", "1", "2"]))
    result = BattleResult(winner)

    MATCH_MAKER.register_match_result(entry1, entry2, result)

def handle_print():
    ranking = MATCH_MAKER.ranking
    ranking.pretty_print()

def handle_batch_match():
    batch = MATCH_MAKER.batch_match()

    for entry1, entry2 in batch:
        rich.print("Entry 1")
        rich.print(entry1)

        rich.print("=" * 50)

        rich.print("Entry 2")
        rich.print(entry2)

        CONSOLE.print(Rule())

    for entry1, entry2 in batch:
        winner = int(Prompt.ask(f"Winner (0 for draw), 1={entry1.title}, 2={entry2.title}", choices=["0", "1", "2"]))
        result = BattleResult(winner)

        MATCH_MAKER.register_match_result(entry1, entry2, result)



COMMANDS = {
        "match" : handle_match,
        "print" : handle_print,
        "batch" : handle_batch_match
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", "-c", help="Config file path")
    parser.add_argument("--checkpoint", help="Checkpoint ranking")
    parser.add_argument("save", help="Save checkpoint")

    args = parser.parse_args()

    CONSOLE = Console()
    
    if args.checkpoint is not None:
        RANKING = EloRanking.load_ranking(args.checkpoint)
    else:
        RANKING = EloRanking.from_config(args.config)

    MATCH_MAKER = MatchMaker(RANKING)
    
    try:
        while True:
            cmd = Prompt.ask("Command")

            if cmd == "exit":
                ranking = MATCH_MAKER.ranking
                ranking.save_ranking(args.save)
                break
            
            if cmd not in COMMANDS:
                warnings.warn(f"Command {cmd} not in {COMMANDS.keys()}")
                continue

            cmd_fun = COMMANDS[cmd]
            cmd_fun()
    finally:
        ranking = MATCH_MAKER.ranking
        ranking.save_ranking(args.save)
