from jobspy import scrape_jobs

def retrieve_jobs(search_term: str, location: str, results_wanted: int, posted_within_hours: int):
    sites = ['indeed', 'linkedin', 'glassdoor', 'google']  
   
    return scrape_jobs(
            site_name=sites,
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            hours_old=posted_within_hours,
            country_indeed=location,
            description_format='markdown',
            linkedin_fetch_description=True,
            proxies=None,
            ca_cert=None,
            verbose=1,
            proxy="http://user:pass@proxyhost:port"
        )