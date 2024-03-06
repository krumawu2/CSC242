#!/usr/bin/env python
# coding: utf-8

import sys
import argparse
from collections import defaultdict

def parse_input():
    """Parses CNF formula from stdin and returns it as a list of sets."""
    clauses = []
    for line in sys.stdin:
        clause = set(line.strip().split(","))
        clauses.append(clause)
    return clauses

def find_unit_clauses(clauses):
    """Returns a list of unit clauses (clauses with only one literal)."""
    return [list(clause)[0] for clause in clauses if len(clause) == 1]

def find_pure_literals(clauses):
    """Finds pure literals in the set of clauses."""
    literal_occurrence = defaultdict(int)
    for clause in clauses:
        for literal in clause:
            if "~" not in literal:
                literal_occurrence[literal] += 1
            else:
                literal_occurrence[literal[1:]] -= 1
    return [literal for literal, count in literal_occurrence.items() if count != 0]

def assign(clauses, literal, value):
    """Assigns a value to a literal and simplifies the clauses."""
    new_clauses = []
    for clause in clauses:
        if literal in clause and value or f"~{literal}" in clause and not value:
            continue
        new_clause = clause - {literal, f"~{literal}"}
        if new_clause:  # Ensure we don't add empty clauses
            new_clauses.append(new_clause)
    return new_clauses

def dpll(clauses, assignments, use_unit_clause, use_pure_literal):
    """Recursive DPLL algorithm with improved contradiction handling."""
    if not clauses:
        return assignments
    if any(not clause for clause in clauses):
        return False

    if use_unit_clause:
        unit_clauses = find_unit_clauses(clauses)
        unit_literals = set(unit_clauses)  # Use a set for efficient lookup
        # Check for contradictions among unit clauses
        for literal in unit_literals:
            if (literal.startswith("~") and literal[1:] in unit_literals) or \
               ("~" + literal in unit_literals):
                return False  # Contradiction found

        while unit_clauses:
            literal = unit_clauses.pop()
            value = True
            if literal.startswith("~"):
                literal, value = literal[1:], False
            assignments[literal] = value
            clauses = assign(clauses, literal, value)
            unit_clauses = find_unit_clauses(clauses)

    if use_pure_literal:
        pure_literals = find_pure_literals(clauses)
        for literal in pure_literals:
            value = True
            if literal.startswith("~"):
                literal, value = literal[1:], False
            assignments[literal] = value
            clauses = assign(clauses, literal, value)

    if not clauses:
        return assignments
    if any(not clause for clause in clauses):
        return False

    for clause in clauses:
        for literal in clause:
            if literal not in assignments and f"~{literal}" not in assignments:
                for value in [True, False]:
                    next_assignments = assignments.copy()
                    next_assignments[literal] = value
                    next_clauses = assign(clauses, literal, value)
                    result = dpll(next_clauses, next_assignments, use_unit_clause, use_pure_literal)
                    if result is not False:
                        return result
                return False

    return assignments

def main():
    parser = argparse.ArgumentParser(description="Solves satisfiability problems using the DPLL algorithm.")
    parser.add_argument('--nounit', action='store_false', help="Disable the unit clause heuristic.")
    parser.add_argument('--nopure', action='store_false', help="Disable the pure literal heuristic.")
    args = parser.parse_args()

    clauses = parse_input()
    result = dpll(clauses, {}, args.nounit, args.nopure)
    if result is not False:
        all_literals = set(literal for clause in clauses for literal in clause)
        for literal in all_literals:
            if literal.startswith('~'):
                var = literal[1:]
            else:
                var = literal
            if var not in result and f"~{var}" not in result:
                result[var] = False  # Assign false to unassigned variables
        print("satisfiable", " ".join(f"{k}={'T' if v else 'F'}" for k, v in sorted(result.items(), key=lambda x: x[0])))
    else:
        print("unsatisfiable")

if __name__ == "__main__":
    main()

