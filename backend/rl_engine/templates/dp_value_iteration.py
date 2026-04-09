def value_iteration(V, env, gamma=0.9, theta=1e-8):
    delta = float("inf")
    action_count = env.action_space.n
    while delta > theta:
        delta = 0.0
        for state in range(len(V)):
            old_value = V[state]
            action_values = []
            for action in range(action_count):
                action_value = 0.0
                for transition_prob, next_state, reward, done in env.P[state][action]:
                    future = 0.0 if done else V[next_state]
                    action_value += transition_prob * (reward + gamma * future)
                action_values.append(action_value)
            V[state] = max(action_values)
            delta = max(delta, abs(old_value - V[state]))
    return V
