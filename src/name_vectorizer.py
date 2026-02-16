import numpy as np
import string

class NameVectorizer:
    def __init__(self):
        self.alphabet = string.ascii_lowercase
        self.char_index = {c: i for i, c in enumerate(self.alphabet)}

    def transform_name(self, name):
        """Convert a name into a fixed-length vector based on character frequencies."""
        name = name.lower()
        vec = np.zeros(len(self.alphabet))

        for ch in name:
            if ch in self.char_index:
                vec[self.char_index[ch]] += 1

        return vec

    def transform_batch(self, names):
        return np.array([self.transform_name(n) for n in names])
