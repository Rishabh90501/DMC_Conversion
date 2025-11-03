from flask import Flask,request, render_template
import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from src.pipeline.predict_pipeline import PredictPipeline, CustomData

application = Flask(__name__)

app = application

## Route for Home Page

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predictdata',methods=['GET','POST'])
def predict_datapoint():
    if request.method == 'GET':
        return render_template('home.html')
    else:
        data=CustomData(
            Age = int(request.form.get('Age')),
            Gender = request.form.get('Gender'),
            Income = int(request.form.get('Income')),
            CampaignChannel = request.form.get('CampaignChannel'),
            CampaignType = request.form.get('CampaignType'),
            AdSpend = float(request.form.get('AdSpend')),
            ClickThroughRate = float(request.form.get('ClickThroughRate')),
            ConversionRate = float(request.form.get('ConversionRate')),
            WebsiteVisits = float(request.form.get('WebsiteVisits')),
            PagesPerVisit = float(request.form.get('PagesPerVisit')),
            TimeOnSite = float(request.form.get('TimeOnSite')),
            SocialShares = int(request.form.get('SocialShares')),
            EmailOpens = int(request.form.get('EmailOpens')),
            EmailClicks = int(request.form.get('EmailClicks')),
            PreviousPurchases = int(request.form.get('PreviousPurchases')),
            LoyaltyPoints = int(request.form.get('LoyaltyPoints'))
        )
        pred_df=data.get_data_as_data_frame()
        print(pred_df)

        predict_pipeline=PredictPipeline()
        results=predict_pipeline.predict(pred_df)

        return render_template('home.html',results=results[0])
    
if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True)