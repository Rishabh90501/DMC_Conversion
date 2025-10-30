USE digital_marketing_campaign;

-- DIMENSION EXPLORATION --

-- Explore All Objects in the campaign Database
SELECT * FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'dm_campaign';


-- Dimension of the Database
SELECT 
    (SELECT COUNT(*) FROM dm_campaign) AS row_count,
    (SELECT COUNT(*)
     FROM INFORMATION_SCHEMA.COLUMNS
     WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'dm_campaign') AS column_count,
    ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS `size_mb`
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'dm_campaign';


-- Explore All demographic Factors
-- Explore Age Factor
SELECT DISTINCT AGE FROM dm_campaign
ORDER BY AGE ASC; -- "The Customer Age range is from 18 to 69."--

-- Explore Gender
SELECT SUM(CASE WHEN Gender = 'Male' THEN 1 ELSE 0 END) as Male,
    SUM(CASE WHEN Gender = 'Female' THEN 1 ELSE 0 END) as Female
FROM dm_campaign; -- "Among 8000 Customers there are 3161 Male and 4839 Female Customers, which makes it a Male to Female Gemder Ratio approx 2/3" -- 

-- Explore Income
SELECT DISTINCT Income FROM dm_campaign
ORDER BY Income ASC; -- "The Highest Income of our Customer is 1,49,986.00 where the lowest income is 20,014.00"--


-- Explore Engagement factors
-- Campaign Types
SELECT DISTINCT CampaignType FROM dm_campaign;
-- Campaign Channels
SELECT DISTINCT CampaignChannel FROM dm_campaign;
-- Advertising Factors
SELECT DISTINCT AdvertisingPlatform FROM dm_campaign;
-- Advertising Tools
SELECT DISTINCT AdvertisingTool FROM dm_campaign;
-- Advertisement Spend
SELECT DISTINCT AdSpend FROM dm_campaign
ORDER BY AdSpend DESC;
-- Click Through Rate Spend
SELECT DISTINCT ClickThroughRate, COUNT(CustomerID) AS Total_Customers
FROM dm_campaign GROUP BY ClickThroughRate ORDER BY Total_Customers DESC;


-- Measures Creation
-- Demograohic Factors
DELIMITER $$ -- Age Group
CREATE FUNCTION age_group(age INT) RETURNS VARCHAR(20)
DETERMINISTIC BEGIN DECLARE category VARCHAR(20);
    IF age BETWEEN 0 AND 17 THEN SET category = 'Child';
    ELSEIF age BETWEEN 18 AND 24 THEN SET category = 'Youth';
    ELSEIF age BETWEEN 25 AND 64 THEN SET category = 'Adult';
    ELSE SET category = 'Senior';
    END IF;
    RETURN category;
END $$
DELIMITER ;

DELIMITER $$ -- Income Factor
CREATE FUNCTION income_groups(income INT) RETURNS VARCHAR(50)
DETERMINISTIC BEGIN DECLARE category VARCHAR(50);
    IF income BETWEEN 0 AND 30000 THEN SET category = 'Low Income';
    ELSEIF income BETWEEN 30001 AND 50000 THEN SET category = 'Lower Middle Income';
    ELSEIF income BETWEEN 50001 AND 75000 THEN SET category = 'Middle Income';
    ELSEIF income BETWEEN 75001 AND 120000 THEN SET category = 'Upper Middle Income';
    ELSE SET category = 'High Income';
    END IF;
    RETURN category;
END $$
DELIMITER ;


DELIMITER $$
CREATE FUNCTION cust_loyalty(loyalty INT) RETURNS VARCHAR(50)
READS SQL DATA DETERMINISTIC BEGIN DECLARE lv VARCHAR(50);
    IF loyalty BETWEEN 0 AND 999 THEN SET lv = 'Bronze Tier';
    ELSEIF loyalty BETWEEN 1000 AND 1999 THEN SET lv = 'Silver Tier';
    ELSEIF loyalty BETWEEN 2000 AND 3499 THEN SET lv = 'Gold Tier';
    ELSE SET lv = 'Platinum Tier';
    END IF;
    RETURN lv;
END $$
DELIMITER ;


DELIMITER $$
CREATE FUNCTION conversion_prob(p_conversion_rate DECIMAL(10,4), p_conversion INT)
RETURNS VARCHAR(50)
DETERMINISTIC BEGIN DECLARE v_label VARCHAR(50);
    IF p_conversion = 1 THEN SET v_label = 'High Probability';
    ELSE
        IF p_conversion_rate IS NULL OR p_conversion_rate <= 0 THEN SET v_label = 'No Probability';
        ELSEIF p_conversion_rate >= 0.20 THEN SET v_label = 'High Probability';
        ELSE SET v_label = 'Low Probability';
        END IF;
    END IF;
    RETURN v_label;
END $$
DELIMITER ;


DELIMITER $$
CREATE FUNCTION pp_group(pre_purchase INT) 
RETURNS VARCHAR(50)
DETERMINISTIC
BEGIN DECLARE item VARCHAR(50);
    IF pre_purchase = 0 THEN SET item = 'New Customer';
    ELSEIF pre_purchase BETWEEN 1 AND 3 THEN SET item = 'Occasional Buyer';
    ELSE SET item = 'Frequent Buyer';
    END IF;
    RETURN item;
END $$
DELIMITER ;


-- DATA EXPLORATION

-- Explore All Campaign Types with the Channels based on Customer Count
SELECT DISTINCT CampaignType,
	CampaignChannel, 
    Gender,
	COUNT(CustomerID) AS Total_Customers,
    SUM(CASE WHEN Conversion = 1 THEN 1 ELSE 0 END) AS Total_Conversion,
    SUM(CASE WHEN Conversion = 0 THEN 1 ELSE 0 END) AS Total_Nonconversion,
	ROUND((SUM(CASE WHEN Conversion = 1 THEN 1 ELSE 0 END) / COUNT(*) * 100), 2) AS Overall_Conversion_Rate
FROM dm_campaign
GROUP BY  CampaignType, CampaignChannel, Gender
ORDER BY  CampaignType ASC;


-- Explore Overall Customer Conversion Rate
SELECT COUNT(*) AS Total_Customers,
	SUM(CASE WHEN Conversion = 1 THEN 1 ELSE 0 END) AS Total_Conversion,
    SUM(CASE WHEN Conversion = 0 THEN 1 ELSE 0 END) AS Total_Nonconversion,
	ROUND((SUM(CASE WHEN Conversion = 1 THEN 1 ELSE 0 END) / COUNT(*) * 100), 2) AS Overall_Conversion_Rate
FROM dm_campaign; 
-- "Among all 8000 Customers the Conversion rate is 87.65% where 7012 is Converted which leaves use with 988 non converted customer i.e. around 12% of the customers."


SELECT
  CustomerID,
  ConversionRate,
  Conversion,
  conversion_prob(ConversionRate , Conversion) AS Conversion_Probability
FROM dm_campaign
LIMIT 50;

-- Customer Segementaion by Age
SELECT age_group(Age) AS Age_Group,
	COUNT(CustomerID) AS Total_Customers,
    ROUND((SUM(CASE WHEN Conversion = 1 THEN 1 ELSE 0 END) / COUNT(*) * 100), 2) AS Overall_Conversion_Rate
FROM dm_campaign
GROUP BY Age_Group; 
-- "Amongs the Customers thier are 1031 Youths(12.89%), 6215 Adults(77.69%) & 754 Senior(9.42%)". 
-- "Here the Conversion Rate for Youth, Adult & Senior are 88.05%, 8.47% & 86.13% respectively".


-- Explore Income Group Conversion
SELECT income_groups(Income) AS Income_Group,
	COUNT(CustomerID) AS Total_Customers,
    ROUND((SUM(CASE WHEN Conversion = 1 THEN 1 ELSE 0 END) / COUNT(*) * 100), 2) AS Overall_Conversion_Rate
FROM dm_campaign
GROUP BY Income_Group
ORDER BY CASE 
	WHEN Income_Group = "Low Income" THEN 1
	WHEN Income_Group = "Lower Middle Income" THEN 2
	WHEN Income_Group = "Middle Income" THEN 3
	WHEN Income_Group = "Upper Middle Income" THEN 4
	WHEN Income_Group = "High Income" THEN 5
    ELSE 6
    END; -- "We can see higher the income group more the conversion rate"


-- Explore All Campaign Types and Channels based on Gender Factor
SELECT DISTINCT CampaignType,
	CampaignChannel, 
    SUM(CASE WHEN Gender = 'Male' THEN 1 ELSE 0 END) AS Male,
    SUM(CASE WHEN Gender = 'Female' THEN 1 ELSE 0 END) AS Female,
    COUNT(*) AS Total_Count,
	ROUND((COUNT(*) / (SELECT COUNT(*) FROM dm_campaign) * 100), 2) AS Cust_perc
FROM dm_campaign
GROUP BY CampaignType, CampaignChannel
ORDER BY Cust_perc DESC;


-- Explore Customer Conversion Rate based on Gender and Campaign
SELECT DISTINCT CampaignType,
	CampaignChannel, 
	ROUND((SUM(CASE WHEN Gender = 'Male' AND Conversion = 1 THEN 1 ELSE 0 END) / 
		NULLIF(SUM(CASE WHEN Gender = 'Male' THEN 1 ELSE 0 END), 0) * 100), 2) AS Male_Conv_Rate,
    ROUND((SUM(CASE WHEN Gender = 'Female' AND Conversion = 1 THEN 1 ELSE 0 END) / 
		NULLIF(SUM(CASE WHEN Gender = 'Female' THEN 1 ELSE 0 END), 0) * 100), 2) AS Female_Conv_Rate,
    ROUND((SUM(CASE WHEN Conversion = 1 THEN 1 ELSE 0 END) / COUNT(*) * 100), 2) AS Overall_Conversion_Rate
FROM dm_campaign
GROUP BY CampaignType, CampaignChannel
ORDER BY Overall_Conversion_Rate DESC;


-- Measure Exploration
-- 1. What is the overall conversion rate and how does it vary by gender?
SELECT Gender,
	COUNT(*) AS Total_Customers,
    SUM(CASE WHEN Conversion = 1 THEN 1 ELSE 0 END) AS Overall_Conversion,
	ROUND((SUM(CASE WHEN Conversion = 1 THEN 1 ELSE 0 END) / COUNT(*) * 100), 2) AS Conversion_Rate
FROM dm_campaign
GROUP BY Gender;
-- We can see eventhough difference between number of female to male customers is around 1000 but the difference in 
-- conversion between female to male is close to 1500 (i.e. "1.5 times the difference of female to male customers.")
 
 
 -- 2.Which campaign channels and types have the highest conversion rates?
 SELECT CampaignChannel, CampaignType,
       ROUND((SUM(Conversion)/COUNT(*))*100,2) AS Conversion_Rate,
       COUNT(*) AS Total_Customers
FROM dm_campaign 
GROUP BY CampaignChannel, CampaignType
ORDER BY Conversion_Rate DESC;
-- The Highest 5 Conversion rates comes from a single Campaign type "Conversion".
-- Top 5 Campaign Channel from the Highest Campaign Type are (SEO, PPC, Email, Referral & Social Media) respectively.


-- 3. How does conversion rate vary across different income groups?
SELECT income_groups(Income) AS Income_Group,
       ROUND((SUM(Conversion)/COUNT(*))*100,2) AS Conversion_Rate
FROM dm_campaign 
GROUP BY Income_Group
ORDER BY MIN(Income); 
-- "We can see higher the income group more the conversion rate"


-- 4. What is the relationship between customer engagement metrics and conversion?
SELECT Conversion,
       ROUND(AVG(ClickThroughRate),2) AS Avg_CTR,
       ROUND(AVG(WebsiteVisits),2) AS Avg_Website_Visits,
       ROUND(AVG(TimeOnSite),2) AS Avg_Time_On_Site,
       ROUND(AVG(EmailOpens),2) AS Avg_Email_Opens,
       ROUND(AVG(EmailClicks),2) AS Avg_Email_Clicks,
       ROUND(AVG(PreviousPurchases),2) AS Avg_Past_Purchases,
       ROUND(AVG(LoyaltyPoints),2) AS Avg_Email_Opens
FROM dm_campaign 
GROUP BY Conversion;
-- "For all converted customers the average engagement metrics are higher than every non converted customers"


-- 5. Which advertising platforms and tools deliver the highest conversion rates?
SELECT AdvertisingPlatform, AdvertisingTool,
       ROUND((SUM(Conversion)/COUNT(*))*100,2) AS Conversion_Rate,
       AVG(AdSpend) AS Avg_Ad_Spend
FROM dm_campaign 
GROUP BY AdvertisingPlatform, AdvertisingTool
HAVING COUNT(*) > 50  -- Minimum sample size
ORDER BY Conversion_Rate DESC;
-- "Since it has a single adv platform and tool it doesn't matter which has higest conversion it will be same as overall conversion rate(87.65)"


-- 6. How does previous purchase behavior relate to conversion probability?
SELECT conversion_prob(ConversionRate, Conversion) AS Conversion_Probability,
	pp_group(PreviousPurchases) AS Purchase_History,
    SUM(Conversion) AS Conversion
FROM dm_campaign 
GROUP BY Conversion_Probability, Purchase_History
ORDER BY Conversion_Probability DESC;
-- "We can see even if the customer is a Frequent buyer if the Conversion Probability is low there will be no conversion"

-- 7. What is the optimal ad spend range for maximum conversions?
SELECT MIN(AdSpend) AS Min_Adspend, 
ROUND(AVG(AdSpend),2) AS Avg_Adspend, 
MAX(AdSpend) AS Max_Adspend 
FROM dm_campaign; -- "With this I can determined the Low , Medium & High Spend range"

SELECT CASE 
          WHEN AdSpend <= 500 THEN 'Low Spend'
          WHEN AdSpend BETWEEN 500.01 AND 2500 THEN 'Medium Spend'
          ELSE 'High Spend' 
       END AS Spend_Group,
       ROUND((SUM(Conversion)/COUNT(*))*100,2) AS Conversion_Rate,
       ROUND(SUM(AdSpend),2) AS Total_Spend,
       SUM(Conversion) AS Total_Conversions
FROM dm_campaign 
GROUP BY Spend_Group
ORDER BY MIN(AdSpend); 
-- "For maxium Conversion the best Advertisement Spend range is above 2500" 


-- 8. How do age demographics affect conversion behavior?
SELECT 
	age_group(Age) AS Age_Group,
	ROUND((SUM(Conversion)/COUNT(*))*100,2) AS Conversion_Rate,
	COUNT(*) AS Customer_Count
FROM dm_campaign 
GROUP BY Age_Group
ORDER BY MIN(Age);
-- "Even though there is hardly any differnce in conversion rate for age factor." 
-- "But the highest conversion with 88.05% comes under the age group of (25 to 64) And next highest belongs to above 64 Age group."


-- 9. What combination of engagement metrics predicts conversion best?
SELECT Conversion,
    ROUND(AVG(ClickThroughRate),2) AS Avg_CTR,
    ROUND(AVG(PagesPerVisit),2) AS Avg_Pages_Per_Visit,
	ROUND(AVG(WebsiteVisits),2) AS Avg_Website_Visit,
	ROUND(AVG(TimeOnSite),2) AS Avg_TOS,
	ROUND(AVG(SocialShares),2) AS Avg_Social_Shares,
	ROUND(AVG(EmailOpens),2) AS Avg_Open_Email
FROM dm_campaign 
GROUP BY Conversion;
-- "The Best Combination for predicting conversion best is CTR (0.16), Pages Per View (5.65), Website Visit (25.18), Time On Site (7.93), Social Shares (49.68) & Email Open (9.74)" 

-- 10. Are there any data quality issues or missing values in key columns?
SELECT COUNT(*) as Total_Records,
       SUM(CASE WHEN CustomerID IS NULL THEN 1 ELSE 0 END) as Missing_CustomerID,
       SUM(CASE WHEN Age IS NULL THEN 1 ELSE 0 END) as Missing_Age,
       SUM(CASE WHEN Income IS NULL THEN 1 ELSE 0 END) as Missing_Income,
       SUM(CASE WHEN Conversion IS NULL THEN 1 ELSE 0 END) as Missing_Conversion
FROM dm_campaign;
-- "There are no missing data in any of the Key columns"


-- Data Creation

-- Demographic Data
SELECT CustomerID,
    age_group(Age) AS Age_Group,
    Gender,
    income_groups(Income) AS Income_Group
FROM dm_campaign;

-- Engagement Data
SELECT CustomerID,
	CASE WHEN AdSpend <= 500 THEN 'Low Spend' WHEN AdSpend BETWEEN 500.01 AND 2500 THEN 'Medium Spend' 
        ELSE 'High Spend' END AS AdSpend_Group,
	pp_group(PreviousPurchases) AS Pre_Purchase_Group,
    cust_loyalty(LoyaltyPoints) AS Customer_Loyalty,
    conversion_prob(ConversionRate, Conversion) AS Conv_Probability
FROM dm_campaign; 