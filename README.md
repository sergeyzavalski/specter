
## Tasks

Implement the following endpoints. You don’t need authentication — focus on the data logic and clean code.
**http://localhost:8080/swagger/**
### 1. Company Filtering

As a user I want to be able to filter the company dataset. 

I want to be able to filter by

- funding amount 
**http://localhost:8080/companies?total_funding_usd__gte=10000&limit=10&offset=0**
- founded date 
**http://localhost:8080/companies?founded_date__gte=2015&limit=10&offset=0**
- employee_count 
**http://localhost:8080/companies?employee_count__lte=2015&order_by=employee_count&limit=10&offset=0**
- and keywords against `short_description` 
**http://localhost:8080/companies?short_description__icontains=Airbnb&order_by=employee_count&limit=10&offset=0**

*Note*: The filtering should happen in the database, not in Python. 

### 2. User Statuses

In addition to the filters in 1., I also want to be able to filter by the companies already viewed / liked / disliked and **not** viewed / liked disliked. 

**http://localhost:8080/users/user_2mePtBmb3vnaRfBBd3xjIZAhusY/companies-statuses?statuses__liked=true&statuses__viewed=false&limit=10&offset=0**

For example: 

- return all liked companies by user
 **http://localhost:8080/users/user_2mePtBmb3vnaRfBBd3xjIZAhusY/companies-statuses?statuses__liked=true&limit=10&offset=0**
- return all companies NOT viewed and founded after 2020.
 **http://localhost:8080/users/user_2mePtBmb3vnaRfBBd3xjIZAhusY/companies-statuses?founded_date__gt=2020&statuses__liked=true&limit=10&offset=0**

### 3. Update User Status

I want to be able to update the status for a given company, so that the client can record whether a company has been viewed, liked, or disliked

**curl -X 'PATCH' \
  'http://localhost:8080/companies/5e3a7f160aa7a3270a54ce5f/user_2mePtBmb3vnaRfBBd3xjIZAhusY/statuses' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "liked": false,
  "viewed": true
}'**

### 4. Support sorting

supporting sorting on the 3 numeric columns mentioned above

**remove minus for ascending ordering**

**http://localhost:8080/companies?employee_count__gte=2010&order_by=-founded_date&limit=10&offset=0**

### 5. Testing

Please include what you think are the most important cases for testing, and be prepared to discuss this during the interview.

**preferably all combinations of filtering and ordering should be tested, depending on frontend, also /companies-statuses endpoint depends of clickhouse connecting to postgres, so has to be tested on big amounts of rows in user_company_status table**


---------------------------------------------------------------------------------------------------------------------


## Questions

During the interview we will ask about the following, please be prepared to be able to answer these.

**#1 Scale**

If our dataset grows 1000x - would anything change in your design? 

**only in case table be sharded**

If we include other datasets that are required to be queried, how does this change the design?
**new table service for serving new table has to be added in same code style**


**#2 Consistency**

You accept `status=liked` while a concurrent request sets `disliked`. How do you deal with that? 
**regarding status there should not be concurrent requests as this status is connected to company and user_id, anyway, in all possible cases optimistic or pessimistic lockings should be used depending on RPS**

**#3 Deployment**

How would you deploy this for development and production.
**docker containers are enough for development and k8s should be used in production**

**#4 Monitoring**

How would you end up monitoring this for failures, alerts, etc.
**you can use Sentry and correlation-id for tracing specific request from user. all of these depends of type of deployment**