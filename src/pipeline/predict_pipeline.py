import os
import sys
import pandas as pd

from src.utils import load_object

from src.exception import CustomException
from src.logger import logging


class PredictPipeline:
    def __init__(self):
        pass

    def predict(self, features: pd.DataFrame):
        try:
            model_path = os.path.join("artifacts", "model.pkl")
            preprocessor_path = os.path.join("artifacts", "preprocessor.pkl")

            # explicit checks with clear error messages
            if not os.path.exists(preprocessor_path):
                raise FileNotFoundError(f"Preprocessor file not found: {preprocessor_path}")
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")

            logging.info(f"Loading preprocessor from {preprocessor_path} and model from {model_path}")
            model = load_object(file_path=model_path)
            preprocessor = load_object(file_path=preprocessor_path)
            logging.info("Loaded model and preprocessor successfully")

            # ensure features is a DataFrame
            if not isinstance(features, pd.DataFrame):
                raise ValueError("features must be a pandas DataFrame")

            # transform and predict
            data_scaled = preprocessor.transform(features)
            preds = model.predict(data_scaled)
            return preds

        except Exception as e:
            logging.error("Exception occurred during prediction", exc_info=True)
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
            # normalize categorical inputs to match training labels
            def _norm_gender(val: str) -> str:
                v = (val or "").strip().lower()
                if v in ["male", "m"]:
                    return "Male"
                if v in ["female", "f"]:
                    return "Female"
                return val

            def _norm_channel(val: str) -> str:
                v = (val or "").strip().lower()
                mapping = {
                    "email": "Email",
                    "social_media": "Social Media",
                    "social media": "Social Media",
                    "search_engine": "Search Engine",
                    "search engine": "Search Engine",
                    "referral": "Referral",
                    "ppc": "PPC",
                }
                return mapping.get(v, val)

            def _norm_type(val: str) -> str:
                # Title-case common campaign types; fall back to original
                v = (val or "").strip().lower()
                mapping = {
                    "awareness": "Awareness",
                    "consideration": "Consideration",
                    "conversion": "Conversion",
                    "retention": "Retention",
                }
                return mapping.get(v, val)

            custom_data_input_dict = {
                "Age": [self.Age],
                "Gender": [_norm_gender(self.Gender)],
                "Income": [self.Income],
                "CampaignChannel": [_norm_channel(self.CampaignChannel)],
                "CampaignType": [_norm_type(self.CampaignType)],
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
            logging.error("Exception occurred in CustomData.get_data_as_data_frame", exc_info=True)
            raise CustomException(e, sys)