import os
import sys
import pandas as pd

from src.utils import load_object

from src.exception import CustomException
from src.logger import logging


class PredictPipeline:
    def __init__(self):
        pass

    def predict(self,features):
        try:
            model_path=os.path.join("artifacts","model.pkl")
            preprocessor_path=os.path.join('artifacts','preprocessor.pkl')
            print("Before Loading")

            model=load_object(file_path=model_path)
            preprocessor=load_object(file_path=preprocessor_path)
            print("After Loading")

            data_scaled=preprocessor.transform(features)
            preds=model.predict(data_scaled)
            return preds

        except Exception as e:
            logging.info("Exception occurred in prediction")
            raise CustomException(e, sys)
        
class CustomData:
    def __init__(self,
        Age: int,
        Gender: str,
        Income: int,
        CampaignChannel: str,
        CampaignType: str,
        AdSpend: float,
        ClickThroughRate: float,
        ConversionRate: float,
        WebsiteVisits: float,
        PagesPerVisit: float,
        TimeOnSite: float,
        SocialShares: int,
        EmailOpens: int,
        EmailClicks: int,
        PreviousPurchases: int,
        LoyaltyPoints: int):
        
        self.Age = Age
        self.Gender = Gender
        self.Income = Income
        self.CampaignChannel = CampaignChannel
        self.CampaignType = CampaignType
        self.AdSpend = AdSpend
        self.ClickThroughRate = ClickThroughRate
        self.ConversionRate = ConversionRate
        self.WebsiteVisits = WebsiteVisits
        self.PagesPerVisit = PagesPerVisit
        self.TimeOnSite = TimeOnSite
        self.SocialShares = SocialShares
        self.EmailOpens = EmailOpens
        self.EmailClicks = EmailClicks
        self.PreviousPurchases = PreviousPurchases
        self.LoyaltyPoints = LoyaltyPoints
    
    def get_data_as_data_frame(self):
        try:
            custom_data_input_dict = {
                "Age": [self.Age],
                "Gender": [self.Gender],
                "Income": [self.Income],
                "CampaignChannel": [self.CampaignChannel],
                "CampaignType": [self.CampaignType],
                "AdSpend": [self.AdSpend],
                "ClickThroughRate": [self.ClickThroughRate],
                "ConversionRate": [self.ConversionRate],
                "WebsiteVisits": [self.WebsiteVisits],
                "PagesPerVisit": [self.PagesPerVisit],
                "TimeOnSite": [self.TimeOnSite],
                "SocialShares": [self.SocialShares],
                "EmailOpens": [self.EmailOpens],
                "EmailClicks": [self.EmailClicks],
                "PreviousPurchases": [self.PreviousPurchases],
                "LoyaltyPoints": [self.LoyaltyPoints]
            }

            return pd.DataFrame(custom_data_input_dict)
        except Exception as e:
            logging.info("Exception occurred in CustomData class")
            raise CustomException(e, sys)