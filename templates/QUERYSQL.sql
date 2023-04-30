-- Get the scenario and the score for each scenario in SQL 
SELECT Answer.scenario, SUM(Response.Score) FROM `Response` 
INNER JOIN `Answer` on Response.Answer_ID = Answer.id
GROUP BY Answer.Scenario;


-- GET THE SCORES FOR THE ATTRIBUTES IN DATABASE
SELECT Attribute.name, SUM(total_score) FROM (SELECT Answer.scenario, SUM(Response.Score) as total_score FROM `Response` 
INNER JOIN `Answer` on Response.Answer_ID = Answer.id
GROUP BY Answer.Scenario) as results 
INNER JOIN `Scenario_Attribute` on `Scenario_Attribute`.`scenario`=results.Scenario
INNER JOIN `Attribute` on `Attribute`.`id` = `Scenario_Attribute`.`attribute`
GROUP BY Attribute.id;

-- ANOTHER WAY 
SELECT Attribute.name, SUM(Response.score) FROM `Response` 
INNER JOIN `Answer` on Response.Answer_ID = Answer.id
INNER JOIN Scenario on Answer.scenario = Scenario.Scenario_ID
INNER JOIN Scenario_Attribute on Scenario_Attribute.scenario = Scenario.Scenario_ID
INNER JOIN Attribute on Scenario_Attribute.attribute = Attribute.id
GROUP BY Attribute.id;