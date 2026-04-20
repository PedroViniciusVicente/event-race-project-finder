import csv

arquivo_final = 'prs_lote_consolidado.csv'

with open(arquivo_final, 'w', newline='', encoding='utf-8') as f_out:
    escritor = None

    for i in range(1, 23):
        nome_arquivo = f'prs_encontrados_lote_{i}.csv'
        print(f'Processando: {nome_arquivo}')
        
        with open(nome_arquivo, 'r', encoding='utf-8') as f_in:
            leitor = csv.reader(f_in)
            cabecalho = next(leitor) # Lê a primeira linha (cabeçalho)

            # Se for o primeiro arquivo, cria o escritor e grava o cabeçalho
            if escritor is None:
                escritor = csv.writer(f_out)
                escritor.writerow(cabecalho)

            # Grava o restante das linhas no arquivo final
            for linha in leitor:
                escritor.writerow(linha)

print(f"Sucesso! Todos os arquivos foram unidos em {arquivo_final}")