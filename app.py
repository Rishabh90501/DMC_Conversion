from flask import Flask, request, render_template
import traceback

from src.pipeline.predict_pipeline import PredictPipeline, CustomData
from src.logger import logging

application = Flask(__name__)

app = application

def _safe_cast(value, dtype, field_name):
    if value is None or value == "":
        raise ValueError(f"Missing value for '{field_name}'")
    try:
        return dtype(value)
    except Exception:
        raise ValueError(f"Invalid value for '{field_name}': {value}")

## Route for Home Page
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predictdata', methods=['GET', 'POST'])
def predict_datapoint():
    if request.method == 'GET':
        return render_template('home.html')
    else:
        try:
            # validate and parse inputs safely
            data = CustomData(
                Age=_safe_cast(request.form.get('Age'), int, 'Age'),
                Gender=(request.form.get('Gender') or "").strip(),
                Income=_safe_cast(request.form.get('Income'), int, 'Income'),
                CampaignChannel=(request.form.get('CampaignChannel') or "").strip(),
                CampaignType=(request.form.get('CampaignType') or "").strip(),
                AdSpend=_safe_cast(request.form.get('AdSpend'), float, 'AdSpend'),
                ClickThroughRate=_safe_cast(request.form.get('ClickThroughRate'), float, 'ClickThroughRate'),
                ConversionRate=_safe_cast(request.form.get('ConversionRate'), float, 'ConversionRate'),
                WebsiteVisits=_safe_cast(request.form.get('WebsiteVisits'), float, 'WebsiteVisits'),
                PagesPerVisit=_safe_cast(request.form.get('PagesPerVisit'), float, 'PagesPerVisit'),
                TimeOnSite=_safe_cast(request.form.get('TimeOnSite'), float, 'TimeOnSite'),
                SocialShares=_safe_cast(request.form.get('SocialShares'), int, 'SocialShares'),
                EmailOpens=_safe_cast(request.form.get('EmailOpens'), int, 'EmailOpens'),
                EmailClicks=_safe_cast(request.form.get('EmailClicks'), int, 'EmailClicks'),
                PreviousPurchases=_safe_cast(request.form.get('PreviousPurchases'), int, 'PreviousPurchases'),
                LoyaltyPoints=_safe_cast(request.form.get('LoyaltyPoints'), int, 'LoyaltyPoints')
            )

            pred_df = data.get_data_as_data_frame()
            logging.info(f"Received input for prediction: {pred_df.to_dict(orient='records')}")

            predict_pipeline = PredictPipeline()
            results = predict_pipeline.predict(pred_df)

            # results is expected to be an array-like; show first item
            return render_template('home.html', results=results[0])

        except Exception as e:
            # log full traceback for debugging and show a friendly error message in UI
            logging.error("Prediction error:\n" + traceback.format_exc())
            error_message = str(e)
            return render_template('home.html', results=f"Error: {error_message}")
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)