import pandas as pd

# 1. Carregar o arquivo consolidado
nome_arquivo = 'prs_lote_consolidado.csv'

print(f"Lendo o arquivo {nome_arquivo}...")
df = pd.read_csv(nome_arquivo)

# 2. Verificar linhas duplicadas
# O método duplicated() retorna True para linhas que já apareceram antes
duplicadas = df[df.duplicated(keep=False)] # keep=False mostra todas as ocorrências da duplicata

total_duplicadas = df.duplicated().sum()

if total_duplicadas > 0:
    print(f"\n[ALERTA] Foram encontradas {total_duplicadas} linhas duplicadas!")
    print("\nAbaixo estão alguns exemplos de linhas que possuem cópias identicas:")
    print(df[df.duplicated()].head(10)) # Mostra as primeiras 10 duplicatas
    
    # Opcional: Salvar as duplicatas em um arquivo para análise
    # duplicadas.to_csv('linhas_duplicadas_encontradas.csv', index=False)
else:
    print("\n[LIMPO] Não foram encontradas linhas exatamente iguais no arquivo.")

# 3. Exemplo de como remover as duplicatas se você desejar
# Se quiser gerar um novo arquivo sem essas duplicatas, descomente as linhas abaixo:
# df_limpo = df.drop_duplicates()
# df_limpo.to_csv('prs_lote_sem_duplicatas.csv', index=False)
# print("\nArquivo 'prs_lote_sem_duplicatas.csv' gerado com sucesso.")