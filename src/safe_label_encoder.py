import numpy as np
from sklearn.preprocessing import LabelEncoder

class SafeLabelEncoder(LabelEncoder):
    def transform(self, X):
        # Convert values not seen during training → "unknown"
        unknown_label = -1
        X = np.array(X)

        seen = set(self.classes_)

        output = []
        for item in X:
            if item in seen:
                output.append(super().transform([item])[0])
            else:
                output.append(unknown_label)

        return np.array(output)

    def fit_transform(self, X, *args, **kwargs):
        # Fit + transform
        result = super().fit_transform(X)
        return result
