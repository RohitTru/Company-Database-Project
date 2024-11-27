SELECT j.JobID
FROM JobPosition j
JOIN Department d ON j.DepartmentID = d.Department_ID
WHERE d.DepartmentName = 'Marketing'
  AND j.PostedDate >= '2011-01-01'
  AND j.PostedDate < '2011-02-01'; 
