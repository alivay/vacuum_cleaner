# vacuum_cleaner
vacuum cleaner performance measuring environment simulator

This is the solution to ex. 2.5 in the book "Artificial Intelligence - A Modern Approach" (Stuart J. Russell and Peter Norvig).

It focuses on the environment that simulates an agent (robot) for cleaning floors.


pseudo code is based on figure 2.15 - 

function RUN-EVAL-ENVIRONMENT(state, UPDATE-FN, agents, termination, PERFORMANCE-FN) return scores
  local variables: scores, a vector the same size as agents, all 0
  
  repeat
  
    for each agent in agents do
      PERCEPT[agent[ <- GET_PERCEPT(agent, state)
    end
    for each agent in agents do
      ACTION[agent] <- PROGRAM[agent](PERCEPT[agent])
    end
    state <- UPDATE-FN(actions, agents, state)
    scores <- PERFORM-FN(scores, agents, state)
    
  until termination(state)
  return scores
  
