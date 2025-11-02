import os
import sys
from dataclasses import dataclass

import pandas as pd 
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.exception import CustomException
from src.logger import logging
from src.utils import save_object

@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path: str = os.path.join('artifacts', 'preprocessor.pkl')

class DataTransformation:
    def __init__(self):
        self.data_transformation_config = DataTransformationConfig()

    def get_data_transformer_object(self):
        '''This function is responsible for data transformation'''

        try:
            logging.info("Data Transformation Initiated")

            numerical_columns = [ 'Age', 'Income', 'AdSpend', 'ClickThroughRate', 
                                 'ConversionRate', 'WebsiteVisits', 'PagesPerVisit', 
                                 'TimeOnSite', 'SocialShares','EmailOpens', 'EmailClicks', 
                                 'PreviousPurchases', 'LoyaltyPoints']
            categorical_columns = ['Gender', 'CampaignChannel', 'CampaignType']

            num_pipeline = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy='median')),  
                ('scaler', StandardScaler())
            ])

            cat_pipeline = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy='most_frequent')),   
                ('one_hot_encoder', OneHotEncoder()),  
                ('scaler', StandardScaler(with_mean=False))       
            ])

            logging.info("Numerical columns: {}".format(numerical_columns))
            logging.info("Numerical Scaling Completed and Pipeline Created")
            
            logging.info("Categorical columns: {}".format(categorical_columns))     
            logging.info("Categorical Encoding Completed and Pipelines Created")

            preprocessor = ColumnTransformer(
                [("num_pipeline",num_pipeline,numerical_columns),
                ("cat_pipelines",cat_pipeline,categorical_columns)]
            )

            return preprocessor

        except Exception as e:
            logging.error("Error in Data Transformation")
            raise CustomException(e, sys)
    
    def initiate_data_transformation(self, train_path, test_path, valid_path):
        try:
            logging.info("Reading training and testing data")
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)
            valid_df = pd.read_csv(valid_path)

            logging.info("Obtaining preprocessing object")
            preprocessing_obj = self.get_data_transformer_object()

            target_column_name = 'Conversion'

            numerical_columns = [ 'Age', 'Income', 'AdSpend', 'ClickThroughRate', 
                                 'ConversionRate', 'WebsiteVisits', 'PagesPerVisit', 
                                 'TimeOnSite', 'SocialShares','EmailOpens', 'EmailClicks', 
                                 'PreviousPurchases', 'LoyaltyPoints']

            input_feature_train_df = train_df.drop(columns=[target_column_name], axis=1)
            target_feature_train_df = train_df[target_column_name]

            input_feature_test_df = test_df.drop(columns=[target_column_name], axis=1)
            target_feature_test_df = test_df[target_column_name]

            input_feature_valid_df = valid_df.drop(columns=[target_column_name], axis=1)
            target_feature_valid_df = valid_df[target_column_name]

            logging.info("Applying preprocessing object on training and testing dataframes")

            input_feature_train_arr = preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr = preprocessing_obj.transform(input_feature_test_df)
            input_feature_valid_arr = preprocessing_obj.transform(input_feature_valid_df)

            train_arr = np.c_[input_feature_train_arr, np.array(target_feature_train_df)]
            test_arr = np.c_[input_feature_test_arr, np.array(target_feature_test_df)]
            valid_arr = np.c_[input_feature_valid_arr, np.array(target_feature_valid_df)]

            logging.info("Saved preprocessing object")

            save_object(
                file_path=self.data_transformation_config.preprocessor_obj_file_path,
                obj=preprocessing_obj
            )

            return (
                train_arr,
                test_arr,
                valid_arr,
                self.data_transformation_config.preprocessor_obj_file_path,
            )

        except Exception as e:
            logging.error("Error occurred in initiate_data_transformation")
            raise CustomException(e, sys)