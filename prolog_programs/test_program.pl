% Solve predicate - define solution structure and constraints
solve(Solution) :-
    Solution = [alice(Knights), bob(Knaves), charlie(Knights)],
    member(knight, Knights),
    member(knave, Knaves),
    alice_statement(Alice, Bob, Knights, Knaves),
    bob_statement(Bob, Charlie, Knights, Knaves),
    charlie_statement(Charlie, Alice, Bob, Knights, Knaves).

% Helper predicates to evaluate statements based on truth or lies
alice_statement(alice(knave), _, [], []) :- !.
alice_statement(_, _, [knight|_], _) :- !.
alice_statement(_, _, _, [knave|_]).

bob_statement(bob(knave), _, [], []) :- !.
bob_statement(_, charlie(knave), [knight|_], _) :- !.
bob_statement(_, _, _, [knave|_]).

charlie_statement(charlie(knave), _, _, [], []) :- !.
charlie_statement(_, alice(Knights), bob(Knaves), [], []) :-
    member(alice, Knights) =:= member(bob, Knaves).

% Helper to ensure all elements are different
all_different([]).
all_different([H|T]) :- \+ member(H, T), all_different(T).

% Auto-execution
:- initialization(main).
main :-
    solve(Solution),
    writeln('Solution:'),
    write(Solution), nl,
    halt.