# Awesome Lists

To ensure the presence of relevant node-js projects in our dataset, we:

1. Using [collect_projects_names.py](collect_awesome_projects_names.py), we extracted the projects listed in awesome nodejs lists: 
    - https://github.com/sqreen/awesome-nodejs-projects
    - https://github.com/sindresorhus/awesome-nodejs

    The collected projects are listed in [awesome_list_projects_url.json](awesome_list_projects_url.json).

2. Using [filter_awesome_prs.py](filter_awesome_prs.py), we collected Pull Requests (PRs) from those projects that match our criteria (mention keywords: "event race", "race condition", "concurrency bug", "race bug", "flaky test"; modify test files with keywords: "test", "it", "describe"; and modify JavaScript files with modern resources: "promises", "async", "await").

    The filtered PRs are listed in [awesome_list_prs_filtered.json](awesome_list_prs_filtered.json).

3. Using [extract_metrics_awesome_prs.py](extract_metrics_awesome_prs.py), we extracted important metrics from the awesome PRs, such as keywords occurrances, number of lines changed, number of files added, etc.

    The extracted metrics are listed in [awesome_list_final_dataset.csv](awesome_list_final_dataset.csv).