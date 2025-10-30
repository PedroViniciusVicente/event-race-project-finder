import json
import requests
import time
import re
import os
from dotenv import load_dotenv
from typing import List, Dict, Tuple, Optional
import base64

class GitHubTestAnalyzer:
    def __init__(self, headers: Dict[str, str]):

        self.headers = headers
        
        self.test_keywords = ["describe(", "it(", "test("]
        self.async_keywords = ["promise", "async", "await"]
        
        self.request_count = 0
        self.start_time = time.time()
    
    def check_rate_limit(self):

        self.request_count += 1
        
        has_token = 'Authorization' in self.headers and 'token' in self.headers.get('Authorization', '')
        max_requests = 5000 if has_token else 60
        time_window = 3600
        
        elapsed_time = time.time() - self.start_time
        
        if self.request_count >= max_requests * 0.8:
            if elapsed_time < time_window:
                sleep_time = time_window - elapsed_time + 10
                time.sleep(sleep_time)
                self.request_count = 0
                self.start_time = time.time()
    
    def get_pr_files_info(self, repo_name: str, pr_number: int) -> Dict:

        self.check_rate_limit()
        
        try:
            url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}/files"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                files_data = response.json()
                
                total_files_changed = len(files_data)
                total_lines_added = sum(file_info.get('additions', 0) for file_info in files_data)
                total_lines_deleted = sum(file_info.get('deletions', 0) for file_info in files_data)
                total_lines_changed = total_lines_added + total_lines_deleted
                
                changed_files = []
                for file_info in files_data:
                    changed_files.append({
                        'filename': file_info.get('filename'),
                        'additions': file_info.get('additions', 0),
                        'deletions': file_info.get('deletions', 0),
                        'changes': file_info.get('changes', 0),
                        'status': file_info.get('status'),  # added, modified, deleted, renamed
                        'patch': file_info.get('patch', '')  # diff content
                    })
                
                return {
                    'total_files_changed': total_files_changed,
                    'total_lines_added': total_lines_added,
                    'total_lines_deleted': total_lines_deleted,
                    'total_lines_changed': total_lines_changed,
                    'changed_files': changed_files,
                    'success': True
                }
                
            elif response.status_code == 404:
                return {'success': False, 'error': 'PR not found'}
            elif response.status_code == 403:
                time.sleep(60)
                return {'success': False, 'error': 'Rate limit or access denied'}
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_file_content(self, repo_name: str, file_path: str, pr_sha: Optional[str] = None) -> Optional[str]:

        self.check_rate_limit()
        
        try:
            if pr_sha:
                url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}?ref={pr_sha}"
            else:
                url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"
            
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                file_data = response.json()
                
                if 'content' in file_data:
                    content = base64.b64decode(file_data['content']).decode('utf-8')
                    return content
                    
            elif response.status_code == 404:
                return None
            elif response.status_code == 403:
                time.sleep(60)
                return None
            else:
                return None
                
        except requests.exceptions.RequestException as e:
            return None
        except Exception as e:
            return None
    
    def get_pr_commit_sha(self, repo_name: str, pr_number: int) -> Optional[str]:

        self.check_rate_limit()
        
        try:
            url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                pr_data = response.json()
                return pr_data['head']['sha']
            else:
                return None
                
        except Exception as e:
            return None
    
    def count_async_keywords_in_content(self, content: str) -> Dict:

        content_lower = content.lower()
        
        async_counts = {}
        total_async_occurrences = 0
        
        for keyword in self.async_keywords:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            matches = len(re.findall(pattern, content_lower))
            async_counts[keyword] = matches
            total_async_occurrences += matches
        
        return {
            'individual_counts': async_counts,
            'total_async_occurrences': total_async_occurrences,
            'unique_async_keywords_found': len([k for k, v in async_counts.items() if v > 0])
        }
    
    def check_keywords_in_content(self, content: str) -> Tuple[bool, bool, Dict]:

        content_lower = content.lower()
        
        has_test_keywords = any(keyword.lower() in content_lower for keyword in self.test_keywords)
        
        async_info = self.count_async_keywords_in_content(content)
        has_async_keywords = async_info['total_async_occurrences'] > 0
        
        return has_test_keywords, has_async_keywords, async_info
    
    def analyze_pr(self, pr_data: Dict) -> Dict:
 
        repo_name = pr_data['repo_name']
        pr_url = pr_data['pr_url']
        pr_number = int(pr_url.split('/')[-1])
        
        print(f"\nAnalyzing PR: {pr_url}")
        
        pr_files_info = self.get_pr_files_info(repo_name, pr_number)
        
        pr_sha = self.get_pr_commit_sha(repo_name, pr_number)
        
        results = {
            'repo_name': repo_name,
            'pr_url': pr_url,
            'pr_number': pr_number,
            'author': pr_data.get('author'),
            'title': pr_data.get('title'),
            'matched_terms': pr_data.get('matched_terms', []),
            'files_analyzed': [],
            'files_with_keywords': [],
            'total_files': len(pr_data.get('js_test_files', [])),
            'files_with_test_and_async': 0,
            'analysis_success': True,
            'error_message': None,
            'pr_changes_info': pr_files_info if pr_files_info.get('success') else None,
            'total_files_changed_in_pr': pr_files_info.get('total_files_changed', 0) if pr_files_info.get('success') else 0,
            'total_lines_changed_in_pr': pr_files_info.get('total_lines_changed', 0) if pr_files_info.get('success') else 0,
            'total_async_keywords_count': 0,
            'async_keywords_per_file': []
        }
        
        try:
            total_async_count = 0
            
            for file_path in pr_data.get('js_test_files', []):
                print(f"  Analyzing file: {file_path}")
                
                file_result = {
                    'file_path': file_path,
                    'has_test_keywords': False,
                    'has_async_keywords': False,
                    'found_test_keywords': [],
                    'found_async_keywords': [],
                    'content_retrieved': False,
                    'async_keyword_counts': {},
                    'total_async_occurrences_in_file': 0
                }
                
                content = self.get_file_content(repo_name, file_path, pr_sha)
                
                if content:
                    file_result['content_retrieved'] = True
                    
                    has_test, has_async, async_info = self.check_keywords_in_content(content)
                    file_result['has_test_keywords'] = has_test
                    file_result['has_async_keywords'] = has_async
                    file_result['async_keyword_counts'] = async_info['individual_counts']
                    file_result['total_async_occurrences_in_file'] = async_info['total_async_occurrences']
                    
                    total_async_count += async_info['total_async_occurrences']
                    
                    content_lower = content.lower()
                    file_result['found_test_keywords'] = [kw for kw in self.test_keywords if kw.lower() in content_lower]
                    file_result['found_async_keywords'] = [kw for kw in self.async_keywords if kw.lower() in content_lower]
                    
                    if has_test and has_async:
                        results['files_with_test_and_async'] += 1
                        file_result['matches_criteria'] = True
                        results['files_with_keywords'].append(file_result)
                        print(f"    ✓ File meets the criteria! Async occurrences: {async_info['total_async_occurrences']}")
                    else:
                        file_result['matches_criteria'] = False
                        print(f"    - Test keywords: {has_test}, Async keywords: {has_async} (count: {async_info['total_async_occurrences']})")
                else:
                    print("    ✗ Not able to retrieve file content")
                
                results['files_analyzed'].append(file_result)
                results['async_keywords_per_file'].append({
                    'file_path': file_path,
                    'async_count': file_result['total_async_occurrences_in_file'],
                    'async_breakdown': file_result['async_keyword_counts']
                })
                
                time.sleep(0.1)
            
            results['total_async_keywords_count'] = total_async_count
            
            if pr_files_info.get('success'):
                print(f"  PR Info - Files changed: {results['total_files_changed_in_pr']}, Lines changed: {results['total_lines_changed_in_pr']}")
            print(f"  Total async keywords found: {total_async_count}")
                
        except Exception as e:
            results['analysis_success'] = False
            results['error_message'] = str(e)
            print(f"Error during analyzis of PR: {e}")
        
        return results
    
    def analyze_and_save_matching_projects(self, input_json_path: str, output_json_path: str) -> Dict:

        try:
            with open(input_json_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            pull_requests = data.get('pull_requests', [])
            print(f"Found {len(pull_requests)} PRs to analyze")
            
            matching_projects = []
            analysis_stats = {
                'total_prs_analyzed': 0,
                'successful_analyses': 0,
                'prs_with_matching_files': 0,
                'total_files_analyzed': 0,
                'total_matching_files': 0,
                'total_async_keywords_found': 0,
                'total_pr_files_changed': 0,
                'total_pr_lines_changed': 0,
                'errors': []
            }
            
            for i, pr_data in enumerate(pull_requests, 1):
                print(f"\n{'='*60}")
                print(f"Progress: {i}/{len(pull_requests)}")
                
                analysis_stats['total_prs_analyzed'] += 1
                
                try:
                    pr_result = self.analyze_pr(pr_data)
                    
                    if pr_result['analysis_success']:
                        analysis_stats['successful_analyses'] += 1
                        analysis_stats['total_files_analyzed'] += pr_result['total_files']
                        analysis_stats['total_matching_files'] += pr_result['files_with_test_and_async']
                        analysis_stats['total_async_keywords_found'] += pr_result['total_async_keywords_count']
                        analysis_stats['total_pr_files_changed'] += pr_result['total_files_changed_in_pr']
                        analysis_stats['total_pr_lines_changed'] += pr_result['total_lines_changed_in_pr']
                        
                        if pr_result['files_with_test_and_async'] > 0:
                            analysis_stats['prs_with_matching_files'] += 1
                            
                            matching_project = {
                                'repo_url': pr_data.get('repo_url'),
                                'repo_name': pr_data['repo_name'],
                                'pr_url': pr_data['pr_url'],
                                'author': pr_data.get('author'),
                                'title': pr_data.get('title'),
                                'body': pr_data.get('body'),
                                'created_at': pr_data.get('created_at'),
                                'merged_at': pr_data.get('merged_at'),
                                'matched_terms': pr_data.get('matched_terms', []),
                                'matching_js_test_files': [f['file_path'] for f in pr_result['files_with_keywords']],
                                'analysis_results': {
                                    'total_test_files': pr_result['total_files'],
                                    'files_with_test_and_async': pr_result['files_with_test_and_async'],
                                    'matching_files_details': pr_result['files_with_keywords'],
                                    'total_async_keywords_count': pr_result['total_async_keywords_count'],
                                    'files_changed_in_pr': pr_result['total_files_changed_in_pr'],
                                    'lines_changed_in_pr': pr_result['total_lines_changed_in_pr'],
                                    'async_keywords_per_file': pr_result['async_keywords_per_file'],
                                    'pr_changes_detailed': pr_result['pr_changes_info']
                                }
                            }
                            
                            matching_projects.append(matching_project)
                            print(f"✓ PR added - {pr_result['files_with_test_and_async']} file(s), {pr_result['total_async_keywords_count']} async keywords")
                        else:
                            print("- PR does not have files that meet the criteria")
                    else:
                        analysis_stats['errors'].append({
                            'pr_url': pr_data.get('pr_url', 'unknown'),
                            'error': pr_result.get('error_message', 'Unknown error')
                        })
                        
                except Exception as e:
                    error_msg = f"Error during analysis of PR {pr_data.get('pr_url', 'unknown')}: {e}"
                    print(error_msg)
                    analysis_stats['errors'].append({
                        'pr_url': pr_data.get('pr_url', 'unknown'),
                        'error': str(e)
                    })
                
                if i % 10 == 0:
                    time.sleep(2)
            
            analysis_stats['success_rate'] = (analysis_stats['successful_analyses'] / analysis_stats['total_prs_analyzed'] * 100) if analysis_stats['total_prs_analyzed'] > 0 else 0
            analysis_stats['match_rate'] = (analysis_stats['prs_with_matching_files'] / analysis_stats['successful_analyses'] * 100) if analysis_stats['successful_analyses'] > 0 else 0
            analysis_stats['unique_repositories'] = len(set(p['repo_name'] for p in matching_projects))
            analysis_stats['avg_async_keywords_per_matching_pr'] = (analysis_stats['total_async_keywords_found'] / analysis_stats['prs_with_matching_files']) if analysis_stats['prs_with_matching_files'] > 0 else 0
            analysis_stats['avg_files_changed_per_pr'] = (analysis_stats['total_pr_files_changed'] / analysis_stats['successful_analyses']) if analysis_stats['successful_analyses'] > 0 else 0
            analysis_stats['avg_lines_changed_per_pr'] = (analysis_stats['total_pr_lines_changed'] / analysis_stats['successful_analyses']) if analysis_stats['successful_analyses'] > 0 else 0
            
            output_data = {
                'metadata': {
                    'analysis_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'input_file': input_json_path,
                    'search_criteria': {
                        'test_keywords': self.test_keywords,
                        'async_keywords': self.async_keywords,
                        'requirement': 'Files must contain at least one test keyword AND one async keyword'
                    },
                    'statistics': analysis_stats
                },
                'matching_projects': matching_projects
            }
            
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n{'='*80}")
            print("Analysis Completed!")
            print(f"{'='*80}")
            print(f"Projects that meet the criteria saved in: {output_json_path}")
            print(f"Total projects found: {len(matching_projects)}")
            
            return analysis_stats
            
        except FileNotFoundError:
            print(f"File not found: {input_json_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return {}
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {}
    
    def generate_summary_report(self, results: List[Dict]) -> Dict:

        total_prs = len(results)
        successful_analyses = len([r for r in results if r.get('analysis_success', False)])
        prs_with_matching_files = len([r for r in results if r.get('files_with_test_and_async', 0) > 0])
        
        total_files_analyzed = sum(r.get('total_files', 0) for r in results)
        total_matching_files = sum(r.get('files_with_test_and_async', 0) for r in results)
        total_async_keywords = sum(r.get('total_async_keywords_count', 0) for r in results)
        total_files_changed = sum(r.get('total_files_changed_in_pr', 0) for r in results)
        total_lines_changed = sum(r.get('total_lines_changed_in_pr', 0) for r in results)
        
        unique_repos = set(r.get('repo_name', '') for r in results if r.get('repo_name'))
        
        top_prs = sorted(
            [r for r in results if r.get('files_with_test_and_async', 0) > 0],
            key=lambda x: x.get('files_with_test_and_async', 0),
            reverse=True
        )[:10]
        
        summary = {
            'total_prs_analyzed': total_prs,
            'successful_analyses': successful_analyses,
            'prs_with_matching_files': prs_with_matching_files,
            'total_files_analyzed': total_files_analyzed,
            'total_matching_files': total_matching_files,
            'total_async_keywords_found': total_async_keywords,
            'total_files_changed_in_all_prs': total_files_changed,
            'total_lines_changed_in_all_prs': total_lines_changed,
            'unique_repositories': len(unique_repos),
            'success_rate': (successful_analyses / total_prs * 100) if total_prs > 0 else 0,
            'match_rate': (prs_with_matching_files / successful_analyses * 100) if successful_analyses > 0 else 0,
            'avg_async_keywords_per_matching_pr': (total_async_keywords / prs_with_matching_files) if prs_with_matching_files > 0 else 0,
            'avg_files_changed_per_pr': (total_files_changed / successful_analyses) if successful_analyses > 0 else 0,
            'avg_lines_changed_per_pr': (total_lines_changed / successful_analyses) if successful_analyses > 0 else 0,
            'top_matching_prs': top_prs[:5],  # Top 5 PRs
            'repository_list': sorted(unique_repos)
        }
        
        return summary


def analyze_projects_with_criteria(headers: Dict[str, str], input_json_path: str, output_json_path: str) -> Dict:

    analyzer = GitHubTestAnalyzer(headers=headers)
    
    print("Starting analysis of JavaScript test files...")
    print(f"Input file: {input_json_path}")
    print(f"Output file: {output_json_path}")
    print("Looking for files that contain:")
    print(f"- keywords tests: {analyzer.test_keywords}")
    print(f"- keywords async: {analyzer.async_keywords}")
    
    has_token = 'Authorization' in headers and 'token' in headers.get('Authorization', '')
    if not has_token:
        print("\n  WARNING: GitHub token not found. Rate limit restricted (60 req/hour)")
    else:
        print("\n✓ Executing with GitHub authentication token")
    
    stats = analyzer.analyze_and_save_matching_projects(input_json_path, output_json_path)
    
    if stats:
        print(f"\n{'='*80}")
        print("FINAL STATISTICS")
        print(f"{'='*80}")
        print(f"Total PRs analyzed: {stats['total_prs_analyzed']}")
        print(f"Successful analyses: {stats['successful_analyses']}")
        print(f"PRs with matching files: {stats['prs_with_matching_files']}")
        print(f"Total files analyzed: {stats['total_files_analyzed']}")
        print(f"Total matching files: {stats['total_matching_files']}")
        print(f"Unique repositories found: {stats['unique_repositories']}")
        print(f"Sucess Rate: {stats['success_rate']:.1f}%")
        print(f"Matching Rate: {stats['match_rate']:.1f}%")
        print(f"Total async keywords found: {stats['total_async_keywords_found']}")
        print(f"Average async keywords per PR: {stats.get('avg_async_keywords_per_matching_pr', 0):.1f}")
        print(f"Total files changed in all PRs: {stats['total_pr_files_changed']}")
        print(f"Total linhas changed in all PRs: {stats['total_pr_lines_changed']}")
        print(f"Average files changed by PR: {stats.get('avg_files_changed_per_pr', 0):.1f}")
        print(f"Average lines changed by PR: {stats.get('avg_lines_changed_per_pr', 0):.1f}")
        
        if stats['errors']:
            print(f"\nErros encontrados: {len(stats['errors'])}")
            for error in stats['errors'][:5]:
                print(f"  - {error['pr_url']}: {error['error']}")
    
    return stats


def main():
    
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }
    
    input_file = "data_repos/race_condition_prs-2.json"
    output_file = "data_repos/filtered_race_condition_prs-2.json"

    stats = analyze_projects_with_criteria(headers, input_file, output_file)
    
    return stats


if __name__ == "__main__":
    main()