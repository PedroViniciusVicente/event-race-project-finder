import json
import requests
import os
import time
import re
from typing import List, Dict, Any
from urllib.parse import urlparse
from dotenv import load_dotenv



class GitHubPRAnalyzer:
    def __init__(self, github_token: str = None):

        self.github_token = github_token
        self.session = requests.Session()
        
        if github_token:
            self.session.headers.update({
                'Authorization': f'token {github_token}',
                'Accept': 'application/vnd.github.v3+json'
            })
        
        self.pr_description_terms = [
            "race condition",
            "event race", 
            "concurrency bug",
            "flaky test",
            "race bug",
        ]
        
        self.test_file_patterns = [
            ".test.", ".spec.", "_test.", "_spec.", 
            "/test/", "/tests/", "__tests__", 
            "test.", "spec."
        ]
        
        self.test_keywords = ["describe(", "it(", "test("]
        self.async_keywords = ["promise", "async"]
    
    def load_repositories(self, json_file: str) -> List[str]:

        try:
            with open(json_file, 'r') as f:
                repos = json.load(f)
            return repos
        except FileNotFoundError:
            print(f"File {json_file} not found!")
            return []
        except json.JSONDecodeError:
            print(f"Error decoding JSON from file {json_file}")
            return []
    
    def extract_repo_info(self, github_url: str) -> tuple:

        parsed = urlparse(github_url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) >= 2:
            owner = path_parts[0]
            repo = path_parts[1]
            return owner, repo
        return None, None
    
    def make_api_request(self, url: str) -> Dict[Any, Any]:

        try:
            response = self.session.get(url)
            
            if response.status_code == 403 and 'rate limit' in response.text.lower():
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                current_time = int(time.time())
                sleep_time = max(reset_time - current_time + 1, 60)
                print(f"Rate limit reached. Waiting {sleep_time} seconds...")
                time.sleep(sleep_time)
                response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error on request: {response.status_code} - {url}")
                return {}
                
        except requests.RequestException as e:
            print(f"Error on request: {e}")
            return {}
    
    def get_pull_requests(self, owner: str, repo: str, state: str = 'all') -> List[Dict]:

        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        params = {'state': state, 'per_page': 100}
        
        all_prs = []
        page = 1
        
        while True:
            params['page'] = page
            response = self.session.get(url, params=params)
            
            if response.status_code != 200:
                break
                
            prs = response.json()
            if not prs:
                break
                
            all_prs.extend(prs)
            page += 1
            
            if page > 10:
                break
        
        return all_prs
    
    def check_pr_description(self, pr: Dict) -> bool:

        title = (pr.get('title', '') or '').lower()
        body = (pr.get('body', '') or '').lower()
        
        for term in self.pr_description_terms:
            if term.lower() in title or term.lower() in body:
                return True
        return False
    
    def get_pr_files(self, owner: str, repo: str, pr_number: int) -> List[Dict]:

        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
        return self.make_api_request(url)
    
    def is_test_file(self, filename: str) -> bool:

        filename_lower = filename.lower()
        
        for pattern in self.test_file_patterns:
            if pattern in filename_lower:
                return True
        return False
    
    def analyze_file_content(self, file_data: Dict) -> Dict[str, bool]:

        patch = file_data.get('patch', '')
        if not patch:
            return {'has_test_keywords': False, 'has_async_keywords': False}
        
        patch_lower = patch.lower()
        
        has_test_keywords = any(keyword.lower() in patch_lower for keyword in self.test_keywords)
        has_async_keywords = any(keyword.lower() in patch_lower for keyword in self.async_keywords)
        
        return {
            'has_test_keywords': has_test_keywords,
            'has_async_keywords': has_async_keywords
        }
    
    def analyze_repository(self, repo_url: str) -> List[Dict]:

        owner, repo = self.extract_repo_info(repo_url)
        if not owner or not repo:
            print(f"invalid URL: {repo_url}")
            return []
        
        print(f"Analyzing {owner}/{repo}...")
        
        prs = self.get_pull_requests(owner, repo)
        matching_prs = []
        
        for pr in prs:
            if not self.check_pr_description(pr):
                continue
            
            print(f"  Analyzing PR #{pr['number']}: {pr['title']}")
            
            files = self.get_pr_files(owner, repo, pr['number'])
            if not files:
                continue
            
            test_files = [f for f in files if self.is_test_file(f.get('filename', ''))]
            if not test_files:
                continue
            
            pr_analysis = {
                'repository': f"{owner}/{repo}",
                'pr_number': pr['number'],
                'pr_title': pr['title'],
                'pr_url': pr['html_url'],
                'pr_state': pr['state'],
                'created_at': pr['created_at'],
                'test_files': [],
                'has_matching_content': False
            }
            
            for test_file in test_files:
                file_analysis = self.analyze_file_content(test_file)
                
                file_info = {
                    'filename': test_file.get('filename', ''),
                    'status': test_file.get('status', ''),
                    'has_test_keywords': file_analysis['has_test_keywords'],
                    'has_async_keywords': file_analysis['has_async_keywords']
                }
                
                pr_analysis['test_files'].append(file_info)
                
                if file_analysis['has_test_keywords'] and file_analysis['has_async_keywords']:
                    pr_analysis['has_matching_content'] = True
            
            if pr_analysis['has_matching_content']:
                matching_prs.append(pr_analysis)
        
        return matching_prs
    
    def analyze_all_repositories(self, json_file: str, output_file: str = 'awesome_lists/awesome_list_prs_filtered.json'):

        repos = self.load_repositories(json_file)
        if not repos:
            return
                
        all_results = []
        
        for i, repo_url in enumerate(repos, 1):
            print(f"\n[{i}/{len(repos)}] {repo_url}")
            
            try:
                results = self.analyze_repository(repo_url)
                all_results.extend(results)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Error in analysis {repo_url}: {e}")
                continue
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*50}")
        print("Analysis Completed!")
        print(f"PRs Found: {len(all_results)}")
        print(f"Results stored in: {output_file}")
        
        if all_results:
            print("\nResults:")
            for result in all_results:
                print(f"- {result['repository']} - PR #{result['pr_number']}: {result['pr_title']}")


def main():

    repos_file = 'awesome_lists/awesome_list_projects_url.json'
    
    load_dotenv()
    github_token = os.getenv('GITHUB_TOKEN')
    
    analyzer = GitHubPRAnalyzer(github_token)
    analyzer.analyze_all_repositories(repos_file)


if __name__ == "__main__":
    main()