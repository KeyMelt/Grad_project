from typing import List, Dict, Any
import json
import os
import numpy as np

class EventLogger:
    """Logs intermediate RL steps in a structured format during simulation."""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.current_episode = []
        self.all_episodes = []
        os.makedirs(self.log_dir, exist_ok=True)
        
    def clear(self):
        """Clears existing logs for a new run."""
        self.current_episode = []
        self.all_episodes = []

    def log_step(self, step_data: Dict[str, Any]):
        """
        Logs a single step.
        Expected format includes: state, action, reward, next_state, updated_values (e.g., Q-estimates)
        """
        self.current_episode.append(step_data)
        
    def end_episode(self):
        """Marks the end of an episode."""
        self.all_episodes.append(list(self.current_episode))
        self.current_episode = []
        
    def save_logs(self, filename="rl_log.json"):
        """Saves all logged data to a file."""
        filepath = os.path.join(self.log_dir, filename)
        with open(filepath, "w") as f:
            json.dump(self.all_episodes, f, indent=4)
        return filepath
    
    def get_logs(self):
        return [list(episode) for episode in self.all_episodes]
        
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)
