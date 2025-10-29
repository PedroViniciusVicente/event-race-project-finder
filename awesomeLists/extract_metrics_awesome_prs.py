import json
import csv
import requests
import time
import re
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
import base64
from datetime import datetime

class GitHubPRMetricsCollector:
    def __init__(self, headers: Dict[str, str]):
        """
        Initialize the PR metrics collector with GitHub headers
        
        Args:
            headers: Headers for HTTP requests including Authorization token
        """
        self.headers = headers
        
        # Keywords to search for
        self.test_keywords = ["describe(", "it(", "test("]
        self.async_keywords = ["promise", "async", "await"]
        
        # Rate limiting control
        self.request_count = 0
        self.start_time = time.time()
    
    def check_rate_limit(self):
        """Check and control GitHub API rate limit"""
        self.request_count += 1
        
        # GitHub allows 60 requests/hour without auth, 5000 with token
        has_token = 'Authorization' in self.headers and 'token' in self.headers.get('Authorization', '')
        max_requests = 5000 if has_token else 60
        time_window = 3600  # 1 hour in seconds
        
        elapsed_time = time.time() - self.start_time
        
        if self.request_count >= max_requests * 0.8:  # 80% of limit
            if elapsed_time < time_window:
                sleep_time = time_window - elapsed_time + 10
                print(f"Approaching rate limit. Sleeping for {sleep_time:.0f} seconds...")
                time.sleep(sleep_time)
                self.request_count = 0
                self.start_time = time.time()
    
    def get_pr_details(self, repo_name: str, pr_number: int) -> Dict:
        """
        Get detailed PR information from GitHub API
        
        Args:
            repo_name: Repository name (format: owner/repo)
            pr_number: PR number
            
        Returns:
            Dict with PR details
        """
        self.check_rate_limit()
        
        try:
            url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                pr_data = response.json()
                return {
                    'success': True,
                    'author': pr_data.get('user', {}).get('login', 'unknown'),
                    'merged_at': pr_data.get('merged_at'),
                    'closed_at': pr_data.get('closed_at'),
                    'updated_at': pr_data.get('updated_at'),
                    'body': pr_data.get('body', ''),
                    'commits': pr_data.get('commits', 0),
                    'additions': pr_data.get('additions', 0),
                    'deletions': pr_data.get('deletions', 0),
                    'changed_files': pr_data.get('changed_files', 0),
                    'merge_commit_sha': pr_data.get('merge_commit_sha'),
                    'head_sha': pr_data.get('head', {}).get('sha'),
                    'base_sha': pr_data.get('base', {}).get('sha'),
                    'labels': [label['name'] for label in pr_data.get('labels', [])],
                    'assignees': [assignee['login'] for assignee in pr_data.get('assignees', [])],
                    'reviewers': [reviewer['login'] for reviewer in pr_data.get('requested_reviewers', [])]
                }
            else:
                print(f"Error getting PR details for {repo_name}#{pr_number}: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            print(f"Error getting PR details for {repo_name}#{pr_number}: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_pr_files_info(self, repo_name: str, pr_number: int) -> Dict:
        """
        Get information about files changed in the PR
        
        Args:
            repo_name: Repository name (format: owner/repo)
            pr_number: PR number
            
        Returns:
            Dict with file change information
        """
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
                
                # Count different file types
                js_files = len([f for f in files_data if f.get('filename', '').endswith(('.js', '.ts', '.jsx', '.tsx'))])
                test_files = len([f for f in files_data if any(keyword in f.get('filename', '').lower() for keyword in ['test', 'spec', '__tests__'])])
                
                return {
                    'success': True,
                    'total_files_changed': total_files_changed,
                    'total_lines_added': total_lines_added,
                    'total_lines_deleted': total_lines_deleted,
                    'total_lines_changed': total_lines_changed,
                    'js_files_changed': js_files,
                    'test_files_changed': test_files,
                    'changed_files': files_data
                }
                
            else:
                print(f"Error getting PR files for {repo_name}#{pr_number}: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            print(f"Error getting PR files for {repo_name}#{pr_number}: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_file_content(self, repo_name: str, file_path: str, pr_sha: Optional[str] = None) -> Optional[str]:
        """
        Get file content from repository
        
        Args:
            repo_name: Repository name (format: owner/repo)
            file_path: File path
            pr_sha: PR commit SHA (optional)
            
        Returns:
            File content as string or None if not found
        """
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
                print(f"File not found: {repo_name}/{file_path}")
                return None
            else:
                print(f"Error {response.status_code} accessing: {repo_name}/{file_path}")
                return None
                
        except Exception as e:
            print(f"Error getting file content {repo_name}/{file_path}: {e}")
            return None
    
    def count_keywords_in_content(self, content: str) -> Dict:
        """
        Count occurrences of test and async keywords in content
        
        Args:
            content: File content
            
        Returns:
            Dict with keyword counts
        """
        content_lower = content.lower()
        
        test_counts = {}
        async_counts = {}
        
        for keyword in self.test_keywords:
            pattern = r'\b' + re.escape(keyword.lower().replace('(', '\\(')) + r'\b'
            matches = len(re.findall(pattern, content_lower))
            test_counts[keyword] = matches
        
        for keyword in self.async_keywords:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            matches = len(re.findall(pattern, content_lower))
            async_counts[keyword] = matches
        
        return {
            'test_counts': test_counts,
            'async_counts': async_counts,
            'total_test_occurrences': sum(test_counts.values()),
            'total_async_occurrences': sum(async_counts.values()),
            # Individual async keyword counts
            'promise_count': async_counts.get('promise', 0),
            'async_count': async_counts.get('async', 0),
            'await_count': async_counts.get('await', 0)
        }
    
    def analyze_test_file(self, repo_name: str, file_info: Dict, pr_sha: Optional[str] = None) -> Dict:
        """
        Analyze a single test file
        
        Args:
            repo_name: Repository name
            file_info: File information from JSON
            pr_sha: PR commit SHA
            
        Returns:
            Dict with file analysis results
        """
        filename = file_info['filename']
        
        # Get file content
        content = self.get_file_content(repo_name, filename, pr_sha)
        
        if content:
            keyword_counts = self.count_keywords_in_content(content)
            
            return {
                'filename': filename,
                'file_status': file_info.get('status', 'unknown'),
                'content_retrieved': True,
                'file_size_chars': len(content),
                'file_lines': len(content.split('\n')),
                'has_test_keywords': file_info.get('has_test_keywords', False),
                'has_async_keywords': file_info.get('has_async_keywords', False),
                'total_test_occurrences': keyword_counts['total_test_occurrences'],
                'total_async_occurrences': keyword_counts['total_async_occurrences'],
                'promise_count': keyword_counts['promise_count'],
                'async_count': keyword_counts['async_count'],
                'await_count': keyword_counts['await_count'],
                'test_keyword_details': keyword_counts['test_counts'],
                'async_keyword_details': keyword_counts['async_counts']
            }
        else:
            return {
                'filename': filename,
                'file_status': file_info.get('status', 'unknown'),
                'content_retrieved': False,
                'file_size_chars': 0,
                'file_lines': 0,
                'has_test_keywords': file_info.get('has_test_keywords', False),
                'has_async_keywords': file_info.get('has_async_keywords', False),
                'total_test_occurrences': 0,
                'total_async_occurrences': 0,
                'promise_count': 0,
                'async_count': 0,
                'await_count': 0,
                'test_keyword_details': {},
                'async_keyword_details': {}
            }
    
    def process_pr_data(self, pr_data: Dict) -> Dict:
        """
        Process a single PR from the JSON data
        
        Args:
            pr_data: PR data from JSON
            
        Returns:
            Dict with comprehensive PR metrics
        """
        repo_name = pr_data['repository']
        pr_number = pr_data['pr_number']
        
        print(f"Processing PR: {repo_name}#{pr_number}")
        
        # Get detailed PR information
        pr_details = self.get_pr_details(repo_name, pr_number)
        
        # Get PR files information
        pr_files_info = self.get_pr_files_info(repo_name, pr_number)
        
        # Analyze test files
        test_files_analysis = []
        total_test_keywords = 0
        total_async_keywords = 0
        total_promise = 0
        total_async_keyword = 0
        total_await = 0
        
        for test_file in pr_data.get('test_files', []):
            file_analysis = self.analyze_test_file(repo_name, test_file, pr_details.get('head_sha'))
            test_files_analysis.append(file_analysis)
            total_test_keywords += file_analysis['total_test_occurrences']
            total_async_keywords += file_analysis['total_async_occurrences']
            total_promise += file_analysis['promise_count']
            total_async_keyword += file_analysis['async_count']
            total_await += file_analysis['await_count']
            time.sleep(0.1)  # Small delay between file requests
        
        # Calculate dates
        created_date = datetime.fromisoformat(pr_data['created_at'].replace('Z', '+00:00'))
        merged_date = None
        closed_date = None
        
        if pr_details.get('success') and pr_details.get('merged_at'):
            merged_date = datetime.fromisoformat(pr_details['merged_at'].replace('Z', '+00:00'))
        
        if pr_details.get('success') and pr_details.get('closed_at'):
            closed_date = datetime.fromisoformat(pr_details['closed_at'].replace('Z', '+00:00'))
        
        # Calculate time metrics
        time_to_merge = None
        time_to_close = None
        
        if merged_date:
            time_to_merge = (merged_date - created_date).total_seconds() / 3600  # hours
        
        if closed_date:
            time_to_close = (closed_date - created_date).total_seconds() / 3600  # hours
        
        return {
            'repository': repo_name,
            'pr_number': pr_number,
            'pr_title': pr_data['pr_title'],
            'pr_url': pr_data['pr_url'],
            'pr_state': pr_data['pr_state'],
            'created_at': pr_data['created_at'],
            'author': pr_details.get('author', 'unknown') if pr_details.get('success') else 'unknown',
            'merged_at': pr_details.get('merged_at', '') if pr_details.get('success') else '',
            'closed_at': pr_details.get('closed_at', '') if pr_details.get('success') else '',
            'time_to_merge_hours': time_to_merge,
            'time_to_close_hours': time_to_close,
            
            # File metrics
            'test_files_count': len(pr_data.get('test_files', [])),
            'test_files_with_keywords': len([f for f in pr_data.get('test_files', []) if f.get('has_test_keywords') and f.get('has_async_keywords')]),
            'total_files_changed': pr_files_info.get('total_files_changed', 0) if pr_files_info.get('success') else 0,
            'total_lines_added': pr_files_info.get('total_lines_added', 0) if pr_files_info.get('success') else 0,
            'total_lines_deleted': pr_files_info.get('total_lines_deleted', 0) if pr_files_info.get('success') else 0,
            'total_lines_changed': pr_files_info.get('total_lines_changed', 0) if pr_files_info.get('success') else 0,
            'js_files_changed': pr_files_info.get('js_files_changed', 0) if pr_files_info.get('success') else 0,
            'test_files_changed': pr_files_info.get('test_files_changed', 0) if pr_files_info.get('success') else 0,
            
            # Keyword metrics
            'total_test_keyword_occurrences': total_test_keywords,
            'total_async_keyword_occurrences': total_async_keywords,
            'total_promise_occurrences': total_promise,
            'total_async_occurrences': total_async_keyword,
            'total_await_occurrences': total_await,
            'avg_test_keywords_per_file': total_test_keywords / len(pr_data.get('test_files', [])) if pr_data.get('test_files') else 0,
            'avg_async_keywords_per_file': total_async_keywords / len(pr_data.get('test_files', [])) if pr_data.get('test_files') else 0,
            'avg_promise_per_file': total_promise / len(pr_data.get('test_files', [])) if pr_data.get('test_files') else 0,
            'avg_async_per_file': total_async_keyword / len(pr_data.get('test_files', [])) if pr_data.get('test_files') else 0,
            'avg_await_per_file': total_await / len(pr_data.get('test_files', [])) if pr_data.get('test_files') else 0,
            
            # PR metrics
            'commits_count': pr_details.get('commits', 0) if pr_details.get('success') else 0,
            'labels_count': len(pr_details.get('labels', [])) if pr_details.get('success') else 0,
            'assignees_count': len(pr_details.get('assignees', [])) if pr_details.get('success') else 0,
            'reviewers_count': len(pr_details.get('reviewers', [])) if pr_details.get('success') else 0,
            
            # Additional metrics
            'has_matching_content': pr_data.get('has_matching_content', False),
            'analysis_success': pr_details.get('success', False) and pr_files_info.get('success', False),
            
            # Detailed data for further analysis
            'labels': ';'.join(pr_details.get('labels', [])) if pr_details.get('success') else '',
            'assignees': ';'.join(pr_details.get('assignees', [])) if pr_details.get('success') else '',
            'reviewers': ';'.join(pr_details.get('reviewers', [])) if pr_details.get('success') else '',
            'test_files_details': test_files_analysis
        }
    
    def json_to_csv(self, input_json_path: str, output_csv_path: str) -> Dict:
        """
        Convert JSON data to CSV with comprehensive metrics
        
        Args:
            input_json_path: Path to input JSON file
            output_csv_path: Path to output CSV file
            
        Returns:
            Dict with processing statistics
        """
        try:
            with open(input_json_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            print(f"Found {len(data)} PRs to process")
            
            # Process each PR
            processed_prs = []
            stats = {
                'total_prs': len(data),
                'successful_analyses': 0,
                'failed_analyses': 0,
                'total_test_files': 0,
                'total_matching_files': 0,
                'errors': []
            }
            
            for i, pr_data in enumerate(data, 1):
                print(f"\nProgress: {i}/{len(data)}")
                
                try:
                    pr_metrics = self.process_pr_data(pr_data)
                    processed_prs.append(pr_metrics)
                    
                    if pr_metrics['analysis_success']:
                        stats['successful_analyses'] += 1
                    else:
                        stats['failed_analyses'] += 1
                    
                    stats['total_test_files'] += pr_metrics['test_files_count']
                    stats['total_matching_files'] += pr_metrics['test_files_with_keywords']
                    
                except Exception as e:
                    error_msg = f"Error processing PR {pr_data.get('repository', 'unknown')}#{pr_data.get('pr_number', 'unknown')}: {e}"
                    print(error_msg)
                    stats['errors'].append(error_msg)
                    stats['failed_analyses'] += 1
                
                # Pause between PRs to avoid rate limiting
                if i % 5 == 0:
                    print("Pausing for 2 seconds...")
                    time.sleep(2)
            
            # Write to CSV
            if processed_prs:
                fieldnames = [
                    'repository', 'pr_number', 'pr_title', 'pr_url', 'pr_state', 'created_at',
                    'author', 'merged_at', 'closed_at', 'time_to_merge_hours', 'time_to_close_hours',
                    'test_files_count', 'test_files_with_keywords', 'total_files_changed',
                    'total_lines_added', 'total_lines_deleted', 'total_lines_changed',
                    'js_files_changed', 'test_files_changed', 'total_test_keyword_occurrences',
                    'total_async_keyword_occurrences', 'total_promise_occurrences', 
                    'total_async_occurrences', 'total_await_occurrences',
                    'avg_test_keywords_per_file', 'avg_async_keywords_per_file',
                    'avg_promise_per_file', 'avg_async_per_file', 'avg_await_per_file',
                    'commits_count', 'labels_count', 'assignees_count', 'reviewers_count', 
                    'has_matching_content', 'analysis_success', 'labels', 'assignees', 'reviewers'
                ]
                
                with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for pr_metrics in processed_prs:
                        # Remove the detailed test files data for CSV (too complex)
                        pr_metrics_clean = {k: v for k, v in pr_metrics.items() if k != 'test_files_details'}
                        writer.writerow(pr_metrics_clean)
                
                print(f"\nCSV file saved: {output_csv_path}")
                print(f"Processed {len(processed_prs)} PRs successfully")
            
            return stats
            
        except FileNotFoundError:
            print(f"File not found: {input_json_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return {}
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {}


def main():
    """Main function to run the conversion"""
    
    # GitHub token configuration
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }
    
    # File paths
    input_file = "awesomeLists/awesome_list_prs_filtered.json"  # Input JSON file
    output_file = "awesomeLists/awesome_list_final_dataset.csv"  # Output CSV file
    
    # Create collector and process data
    collector = GitHubPRMetricsCollector(headers)
    stats = collector.json_to_csv(input_file, output_file)
    
    # Print final statistics
    if stats:
        print(f"\n{'='*60}")
        print("FINAL STATISTICS")
        print(f"{'='*60}")
        print(f"Total PRs: {stats['total_prs']}")
        print(f"Successful analyses: {stats['successful_analyses']}")
        print(f"Failed analyses: {stats['failed_analyses']}")
        print(f"Total test files: {stats['total_test_files']}")
        print(f"Total matching files: {stats['total_matching_files']}")
        print(f"Success rate: {(stats['successful_analyses'] / stats['total_prs'] * 100):.1f}%")
        
        if stats['errors']:
            print(f"\nErrors ({len(stats['errors'])}):")
            for error in stats['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
    
    return stats


if __name__ == "__main__":
    main()