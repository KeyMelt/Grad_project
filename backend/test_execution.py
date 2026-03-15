import requests
import time

submit_url = "http://127.0.0.1:8000/submit"
payload = {
    "lesson_id": "td_q_learning",
    "code": (
        "def q_learning_update(Q, state, action, reward, next_state, alpha, gamma):\n"
        "    best_next_value = max(Q[next_state])\n"
        "    td_target = reward + gamma * best_next_value\n"
        "    Q[state][action] = Q[state][action] + alpha * (td_target - Q[state][action])\n"
        "    return Q\n"
    ),
    "learning_rate": 0.1,
    "discount_factor": 0.9,
    "exploration_rate": 0.1,
}

try:
    submit_response = requests.post(submit_url, json=payload)
    submit_response.raise_for_status()
    task_id = submit_response.json()["task_id"]

    while True:
        status_response = requests.get(f"http://127.0.0.1:8000/tasks/{task_id}")
        status_response.raise_for_status()
        task = status_response.json()
        print(task)

        if task["status"] in {"succeeded", "failed"}:
            break

        time.sleep(0.5)
except Exception as e:
    print(f"Failed: {e}")
