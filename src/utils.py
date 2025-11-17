import os
import sys
import dill
import pickle

import numpy as np
import pandas as pd
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from src.exception import CustomException
from src.logger import logging

def save_object(file_path, obj):
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, 'wb') as file_obj:
            dill.dump(obj, file_obj)
    except Exception as e:
        raise CustomException(e, sys)
    
def evaluate_models(X_train, y_train, X_test, y_test, models, params):
    try:
        

        report = {}
        best_estimators = {}

        # reduce n_iter to keep runs reasonable; adjust as needed
        for model_name, model in models.items():
            try:
                param = params.get(model_name, {})

                gs = RandomizedSearchCV(model, param, cv=5, n_iter=5, n_jobs=1, verbose=0)
                gs.fit(X_train, y_train)

                best_model = gs.best_estimator_
                # ensure the selected estimator is fitted
                best_model.fit(X_train, y_train)

                y_test_pred = best_model.predict(X_test)

                accuracy = accuracy_score(y_test, y_test_pred)
                precision = precision_score(y_test, y_test_pred, average='weighted')
                recall = recall_score(y_test, y_test_pred, average='weighted')
                f1 = f1_score(y_test, y_test_pred, average='weighted')

                report[model_name] = {
                    "accuracy": accuracy,
                    "precision": precision,
                    "recall": recall,
                    "f1": f1
                }

                best_estimators[model_name] = best_model
            except Exception as e:
                # log/record model failure and continue with other models
                logging.info(f"Model {model_name} failed during evaluation: {e}")
                report[model_name] = {
                    "accuracy": 0.0,
                    "precision": 0.0,
                    "recall": 0.0,
                    "f1": 0.0
                }

        return report, best_estimators
    except Exception as e:
        raise CustomException(e, sys)
    
def load_object(file_path):
    try:
        # saved objects use dill in save_object; use dill to load as well
        with open(file_path, "rb") as file_obj:
            return dill.load(file_obj)

    except Exception as e:
        raise CustomException(e, sys)