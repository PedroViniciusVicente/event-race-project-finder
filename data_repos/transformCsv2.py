import json
import csv

def extrair_dados_para_csv(arquivo_json, arquivo_csv):
    with open(arquivo_json, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    # Campos expandidos para incluir as novas métricas
    campos_csv = [
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

    with open(arquivo_csv, 'w', newline='', encoding='utf-8') as f_csv:
        writer = csv.DictWriter(f_csv, fieldnames=campos_csv)
        writer.writeheader()

        for projeto in dados.get("matching_projects", []):
            # Extrai os dados de analysis_results
            analysis_results = projeto.get("analysis_results", {})
            matching_details = analysis_results.get("matching_files_details", [])

            # Combina todos os keywords encontrados em todos os arquivos matching
            all_test_keywords = set()
            all_async_keywords = set()
            async_breakdown = {}
            files_async_info = []

            for detail in matching_details:
                all_test_keywords.update(detail.get('found_test_keywords', []))
                all_async_keywords.update(detail.get('found_async_keywords', []))
                
                # Coleta informações de async keywords por arquivo
                file_async_counts = detail.get('async_keyword_counts', {})
                if file_async_counts:
                    file_path = detail.get('file_path', 'unknown')
                    total_async_in_file = detail.get('total_async_occurrences_in_file', 0)
                    files_async_info.append(f"{file_path}:{total_async_in_file}")
                    
                    # Soma no breakdown geral
                    for keyword, count in file_async_counts.items():
                        async_breakdown[keyword] = async_breakdown.get(keyword, 0) + count

            # Prepara string do breakdown de async keywords
            async_breakdown_str = ';'.join([f"{k}:{v}" for k, v in async_breakdown.items()])
            files_async_counts_str = ';'.join(files_async_info)

            linha = {
                'repo_url': projeto.get('repo_url', ''),
                'repo_name': projeto.get('repo_name', ''),
                'pr_url': projeto.get('pr_url', ''),
                'author': projeto.get('author', ''),
                'title': projeto.get('title', ''),
                'matching_js_test_files': ';'.join(projeto.get('matching_js_test_files', [])),
                'matched_terms': ';'.join(projeto.get('matched_terms', [])),
                'found_test_keywords': ';'.join(sorted(all_test_keywords)),
                'found_async_keywords': ';'.join(sorted(all_async_keywords)),
                # Novas métricas
                'total_async_keywords_count': analysis_results.get('total_async_keywords_count', 0),
                'files_changed_in_pr': analysis_results.get('files_changed_in_pr', 0),
                'lines_changed_in_pr': analysis_results.get('lines_changed_in_pr', 0),
                'total_test_files': analysis_results.get('total_test_files', 0),
                'files_with_test_and_async': analysis_results.get('files_with_test_and_async', 0),
                'created_at': projeto.get('created_at', ''),
                'merged_at': projeto.get('merged_at', ''),
                'async_keywords_breakdown': async_breakdown_str,
                'files_async_counts': files_async_counts_str
            }
            writer.writerow(linha)

    print(f"Dados extraídos para {arquivo_csv}")
    print(f"Total de projetos processados: {len(dados.get('matching_projects', []))}")


# Exemplos de uso:

# Versão resumida (uma linha por PR)
extrair_dados_para_csv('data_repos/enhanced_filtered_race_condition_prs-3-teste.json', 'data_repos/enhanced_saida3-teste.csv')


print("Conversão concluída! Verifique os arquivos CSV gerados.")