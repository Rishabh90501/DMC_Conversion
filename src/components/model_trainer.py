import os
import sys
from dataclasses import dataclass

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from catboost import CatBoostClassifier
from xgboost import XGBClassifier


from scipy.stats import uniform, randint

from sklearn.metrics import accuracy_score

from src.exception import CustomException
from src.logger import logging

from src.utils import save_object, evaluate_models

@dataclass
class ModelTrainerConfig:
    trained_model_file_path=os.path.join("artifacts","model.pkl")

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config=ModelTrainerConfig()


    def initiate_model_trainer(self,train_array,test_array):
        try:
            logging.info("Split training and test input data")
            X_train,y_train,X_test,y_test=(
                train_array[:,:-1],
                train_array[:,-1],
                test_array[:,:-1],
                test_array[:,-1]
            )
            
            models = {
                'Logistic Regression': LogisticRegression(),
                'KNN': KNeighborsClassifier(),
                'Naive Bayes': GaussianNB(),
                'SVM': SVC(probability=True),
                'Decision Tree': DecisionTreeClassifier(),
                'Random Forest': RandomForestClassifier(random_state=42),
                'Gradient Boost': GradientBoostingClassifier(random_state=42),
                'ADA Boost': AdaBoostClassifier(random_state=42),
                'CatBoost': CatBoostClassifier(verbose=0, random_state=42),
                'XGBoost': XGBClassifier(random_state=42)
            }

            params = {
                'Logistic Regression': {'C': uniform(loc=0.01, scale=10), 'solver': ['liblinear', 'lbfgs']},
                'KNN': {'n_neighbors': randint(3, 12)},
                'Naive Bayes': {'var_smoothing': uniform(loc=1e-9, scale=1e-7)},
                'SVM': {'C': uniform(loc=0.1, scale=100), 'gamma': uniform(loc=0.001, scale=1)},
                'Decision Tree': {'max_depth': randint(10, 50), 'min_samples_split': randint(2, 25)},
                'Random Forest': {'n_estimators': randint(50, 400), 'max_depth': randint(10, 40)},
                'Gradient Boost': {'n_estimators': randint(50, 400), 'learning_rate': uniform(loc=0.01, scale=1.0)},
                'ADA Boost': {'n_estimators': randint(50, 400), 'learning_rate': uniform(loc=0.01, scale=1.0)},
                'CatBoost': {'iterations': randint(50, 400), 'learning_rate': uniform(loc=0.01, scale=0.5), 'depth': randint(3, 10)},
                'XGBoost': {'n_estimators': randint(50, 400), 'learning_rate': uniform(loc=0.01, scale=0.5), 'max_depth': randint(3, 10)}
            } 

            logging.info("Starting model evaluation")

            model_report, best_estimators = evaluate_models(X_train=X_train,
                                                            y_train=y_train,
                                                            X_test=X_test,
                                                            y_test=y_test,
                                                            models=models,
                                                            params=params)

            logging.info(f"Model Report: {model_report}")

            # get best model by accuracy; prefer models that produced a fitted estimator
            sorted_models = sorted(model_report.items(), key=lambda x: x[1]['accuracy'], reverse=True)

            best_model = None
            best_model_name = None
            best_model_score = 0.0

            for name, metrics in sorted_models:
                if name in best_estimators and metrics.get('accuracy', 0.0) > best_model_score:
                    best_model_name = name
                    best_model = best_estimators[name]
                    best_model_score = metrics.get('accuracy', 0.0)

            if best_model is None:
                # no model produced a fitted estimator
                raise CustomException("No valid fitted model found during evaluation", sys)

            if best_model_score<0.6:
                raise CustomException("No best model found", sys)
            logging.info(f"Best found model on both training and testing dataset")

            # best_model returned from evaluate_models is already fitted

            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=best_model
            )

            predicted=best_model.predict(X_test)

            mean_accuracy=accuracy_score(y_test, predicted)
            return mean_accuracy
            
        except Exception as e:
            raise CustomException(e,sys)