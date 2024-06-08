SELECT 
CURRENT_DATE() as run_date, 
  DATE_TRUNC(timestamp, month) AS month, 
  file.project, 
  count(*) 
FROM 
  `bigquery-public-data.pypi.file_downloads`
WHERE 
   DATE(timestamp)
    BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    AND CURRENT_DATE()
GROUP BY 1 ,2,3 ;
