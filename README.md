## DASH APP World map of work immigration to the United Kingdom

The following repository contains a dash app to visualise open data with immigration statistics in the UK.
It is based on data [made pubicly available by the Home Office](https://www.gov.uk/government/publications/immigration-statistics-october-to-december-2016/work#data-tables).

It is based on the [Dash]() framework for webapps and and [plot.ly]() for responsive graphs.


A live version can be found on [https://dash-map-uk.herokuapp.com](https://dash-map-uk.herokuapp.com).

To run locally:

```
git clone <this_repository>
virtualenv -p python3 env/
pip install -r requirements.txt
python app.py
``` 
 
 

### Foreword and key facts 

Every year, over 180,000 non-EU nationals (like myself) apply for a work or student visa to come to the United Kingdom. These indivduals are highly skilled workers, enterpreneurs, sportpersons, etc. Typically the application process involves proving to the Home Office that the visa is intended to fill a technical gap in the country, which might involve showing that the job is in the shortage occupations list or passing through a residents labours market test. A complete list of companies that sponsor or have sponsored work visas can be found here. 
 
The present dashboard shows the evolution of legal work immigration since 2005. It is based on freely available official This interactive visualisation accounts for statistics of legal immigration in the UK. The points-based system visa was proposed in 2005 and started to be fully implemented in 2008, coinciding with a drop of more than 37\% in the total work visas. Further, in 2009,  the UK started a policy called [hostile enviroment](https://en.wikipedia.org/wiki/Home_Office_hostile_environment_policy), which claims to have reduced illegal immigration, but data is not available to support that claim.  

Work-related visas are: 

High-value (Tier 1), Skilled (Tier 2), Youth mobility and temporary workers (Tier 5), as well as non-PBS/Other work visas

Student-related visas mainly include Tier 4 (and excludes short-term study). Statistics for rejected applications are only available per country including all categories, and visitors. A FOIA request has been made for the missing information.