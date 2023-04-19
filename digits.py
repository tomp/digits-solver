#!/usr/bin/env python3
"""
A simple script to solve NYT Digits puzzles.

The problems are simple enough that we can do an exhaustive search of
all possible plays.

Author: Tom POllard
Created: April 18, 2023
"""
from typing import Iterable, Tuple
import sys
from dataclasses import dataclass
from collections import deque
import argparse


PLUS, MINUS, TIMES, DIVIDE = "+", "-", "*", "/"
ACTIONS = (PLUS, MINUS, TIMES, DIVIDE)
COMMUTATIVE = {PLUS: True, MINUS: False, TIMES: True, DIVIDE: False}



@dataclass(frozen=True)
class State:
    """A State instance represents an intermediate step in solving the puzzle."""

    operands: list[int]
    history: list[str]

    def __post_init___(self):
        self.operands.sort()

    def __hash__(self) -> int:
        return hash(tuple(self.operands))

    def moves(self) -> Iterable["State"]:
        n = len(self.operands)
        for action in ACTIONS:
            ordered = COMMUTATIVE[action]
            for i, j in pairs(n, ordered):
                a, b, values = use_values(i, j, self.operands)
                if action == PLUS:
                    result = a + b
                elif action == MINUS:
                    result = a - b
                elif action == TIMES:
                    result = a * b
                elif action == DIVIDE:
                    if a % b:
                        continue
                    result = a // b
                else:
                    raise RuntimeError(f"unrecognized action: '{action}'")

                if result:
                    operation = f"{a}{action}{b}={result}"
                    history = self.history.copy()
                    history.append(operation)
                    yield State(values + [result], history)


def pairs(n: int, ordered: bool = False) -> Iterable[Tuple[int, int]]:
    for i in range(n-1):
        for j in range(i+1, n):
            yield (i, j)
            if not ordered:
                yield (j, i)


def use_values(i: int, j: int, values: list[int]) -> Tuple[int, int, list[int]]:
    i1, j1 = min(i, j), max(i, j)
    return values[i], values[j], values[:i1] + values[i1+1:j1] + values[j1+1:]


def solve(target: int, values: list[int], all_solutions: bool = False) -> list[list[str]]:
    """Solve a digits puzzle, specified by the target value and the list of
    integers that can be used.  This is a simple breadth-first search over the full
    space of possible operations.  
    A list of lists of strings is returned, each describing the sequence of operations
    for one solution.  If all_solutions is False, the list will conain only the shortest
    solution found.
    """
    init = State(values, [])
    queue = deque([init])
    seen = set([hash(init)])

    solutions = []
    while queue:
        curr = queue.popleft()
        if target in curr.operands:
            solutions.append(curr.history)
            if all_solutions:
                continue
            break
        if len(curr.operands) < 2:
            continue
        for succ in curr.moves():
            if hash(succ) in seen:
                continue
            queue.append(succ)
            seen.add(hash(succ))

    return solutions


def targets(values: list[int]) -> list[int]:
    """Return a list of all integers than can be generated from the given set of values,
    and the four operations.
    """
    init = State(values, [])
    queue = deque([init])
    seen = set([hash(init)])

    elements = set()
    while queue:
        curr = queue.popleft()
        elements |= set(curr.operands)
        for succ in curr.moves():
            if hash(succ) in seen:
                continue
            queue.append(succ)
            seen.add(hash(succ))

    result = list(elements)
    result.sort()
    return result


def parse_args():

    parser = argparse.ArgumentParser(description = "Solve a Digits puzzle")
    parser.add_argument("--target", "-t", type=int, help="The target value")
    parser.add_argument("--values", "-v", help="Two or more comma- or space-separated integers")
    parser.add_argument("--all", "-a", action="store_true", help="Find all possible solutions")
    opt = parser.parse_args()

    if "," in opt.values:
        opt.values = list(map(int, opt.values.replace(" ", "").split(",")))
    elif " " in opt.values.strip():
        opt.values = list(map(int, opt.values.strip().split()))
    else:
        raise ValueError(f"unrecognized format for --values: {opt.values}")

    return opt


def main() -> int:
    opt = parse_args()

    if opt.target:
        solutions = solve(opt.target, opt.values, opt.all)
        for soln in solutions:
            print(soln)
        return 0

    elements = targets(opt.values)
    print(f"Found {len(elements)} elements")
    for elem in elements:
        print(elem)
    return 0

if __name__ == '__main__':
    sys.exit(main())
