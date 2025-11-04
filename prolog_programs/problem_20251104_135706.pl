% Define solution with explicit finite domains
solve(Solution) :-
    % Step 1: Define structure with variables
    Solution = [person(alice, Cat), person(bob, Dog), person(carol, Bird)],
    
    % Step 2: Define finite domains for each variable
    member(Cat, [cat, dog, bird]),
    member(Dog, [cat, dog, bird]),
    member(Bird, [cat, dog, bird]),
    
    % Step 3: Add constraints early
    Cat \= cat,
    Dog = dog,
    Bird \= bird,
    
    % Step 4: Add problem-specific constraints
    Cat \= Dog,
    Dog \= Bird,
    Cat \= Bird.

% Auto-execution
:- initialization(main).
main :-
    solve(Solution),
    writeln('Solution:'),
    print_solution(Solution),
    halt.

print_solution([]).
print_solution([H|T]) :- writeln(H), print_solution(T).