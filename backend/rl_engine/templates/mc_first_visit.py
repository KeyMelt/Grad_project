# ---------------------------------------------
# Monte Carlo: First-Visit Prediction
# ---------------------------------------------
# Implement First-Visit MC prediction.
# You are provided with a complete `episode` which is a list of (state, action, reward).
# For Blackjack, `state` is the observation tuple returned by the environment.


def mc_first_visit_prediction(episode, V, returns, gamma=0.9):
    # TODO: Implement First-Visit MC updates.
    # For every state in the episode, if it is the first time the state was visited,
    # calculate the return G, append to returns[state], and update V[state].
    pass
