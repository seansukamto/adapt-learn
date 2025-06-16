
from typing import Dict, Any, List

class AdaptiveEngine:
    def __init__(self):
        self.min_level = 1
        self.max_level = 5
        self.threshold = 3

    def adjust_difficulty(self, level:int, is_correct:bool, total:int, correct:int)->int:
        if total < self.threshold:
            return level
        acc = correct/total
        if acc >= 0.8 and level < self.max_level:
            return level+1
        if acc <= 0.4 and level > self.min_level:
            return level-1
        return level
