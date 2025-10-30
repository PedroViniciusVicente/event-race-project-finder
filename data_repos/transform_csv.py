import json
import csv

def extract_data_to_csv(json_file, csv_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    csv_features = [
        'repo_url', 
        'repo_name',
        'pr_url', 
        'author',
        'title',
        'matching_js_test_files', 
        'matched_terms', 
        'found_test_keywords', 
        'found_async_keywords',
        'total_async_keywords_count',
        'files_changed_in_pr',
        'lines_changed_in_pr',
        'total_test_files',
        'files_with_test_and_async',
        'created_at',
        'merged_at',
        'async_keywords_breakdown',
        'files_async_counts'
    ]

    with open(csv_file, 'w', newline='', encoding='utf-8') as f_csv:
        writer = csv.DictWriter(f_csv, fieldnames=csv_features)
        writer.writeheader()

        for project in data.get("matching_projects", []):
            analysis_results = project.get("analysis_results", {})
            matching_details = analysis_results.get("matching_files_details", [])

            all_test_keywords = set()
            all_async_keywords = set()
            async_breakdown = {}
            files_async_info = []

            for detail in matching_details:
                all_test_keywords.update(detail.get('found_test_keywords', []))
                all_async_keywords.update(detail.get('found_async_keywords', []))
                
                file_async_counts = detail.get('async_keyword_counts', {})
                if file_async_counts:
                    file_path = detail.get('file_path', 'unknown')
                    total_async_in_file = detail.get('total_async_occurrences_in_file', 0)
                    files_async_info.append(f"{file_path}:{total_async_in_file}")
                    
                    for keyword, count in file_async_counts.items():
                        async_breakdown[keyword] = async_breakdown.get(keyword, 0) + count

            async_breakdown_str = ';'.join([f"{k}:{v}" for k, v in async_breakdown.items()])
            files_async_counts_str = ';'.join(files_async_info)

            line = {
                'repo_url': project.get('repo_url', ''),
                'repo_name': project.get('repo_name', ''),
                'pr_url': project.get('pr_url', ''),
                'author': project.get('author', ''),
                'title': project.get('title', ''),
                'matching_js_test_files': ';'.join(project.get('matching_js_test_files', [])),
                'matched_terms': ';'.join(project.get('matched_terms', [])),
                'found_test_keywords': ';'.join(sorted(all_test_keywords)),
                'found_async_keywords': ';'.join(sorted(all_async_keywords)),
                'total_async_keywords_count': analysis_results.get('total_async_keywords_count', 0),
                'files_changed_in_pr': analysis_results.get('files_changed_in_pr', 0),
                'lines_changed_in_pr': analysis_results.get('lines_changed_in_pr', 0),
                'total_test_files': analysis_results.get('total_test_files', 0),
                'files_with_test_and_async': analysis_results.get('files_with_test_and_async', 0),
                'created_at': project.get('created_at', ''),
                'merged_at': project.get('merged_at', ''),
                'async_keywords_breakdown': async_breakdown_str,
                'files_async_counts': files_async_counts_str
            }
            writer.writerow(line)

    print(f"Data extracted to {csv_file}")
    print(f"Total proccessed projects: {len(data.get('matching_projects', []))}")

extract_data_to_csv('data_repos/filtered_race_condition_prs-3.json', 'data_repos/filtered_csv_3.csv')
