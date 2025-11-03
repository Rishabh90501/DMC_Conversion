from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from sklearn.linear_model import LogisticRegression
from src.utils import save_object
from src.logger import logging


def main():
    try:
        ingestion = DataIngestion()
        train_path, test_path = ingestion.initiate_data_ingestion()

        dt = DataTransformation()
        train_arr, test_arr, preprocessor_path = dt.initiate_data_transformation(train_path, test_path)

        # quick train: simple logistic regression on transformed arrays
        X_train, y_train = train_arr[:,:-1], train_arr[:,-1]
        X_test, y_test = test_arr[:,:-1], test_arr[:,-1]

        model = LogisticRegression(max_iter=1000)
        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        acc = (preds == y_test).mean()

        logging.info(f"Quick-run LogisticRegression accuracy: {acc}")

        # save quick model
        save_object('artifacts/quick_model.pkl', model)

        print(f"Quick-run accuracy: {acc}")
    except Exception as e:
        logging.exception("Quick run failed")
        raise


if __name__ == '__main__':
    main()
