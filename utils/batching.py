from collections import defaultdict
import time

class SessionBatcher:
    def __init__(self, max_batch_size=20, max_wait=30):
        self.batches = defaultdict(list)
        self.timestamps = {}
        self.max_batch_size = max_batch_size
        self.max_wait = max_wait

    def add_message(self, session_id, interlocutor_id, message):
        key = (session_id, interlocutor_id)
        self.batches[key].append(message)
        self.timestamps.setdefault(key, time.time())

    def get_ready_batches(self):
        now = time.time()
        ready_batches = []
        for key, messages in list(self.batches.items()):
            if len(messages) >= self.max_batch_size or (now - self.timestamps[key]) > self.max_wait:
                ready_batches.append((key, messages))
                del self.batches[key]
                del self.timestamps[key]
        return ready_batches
