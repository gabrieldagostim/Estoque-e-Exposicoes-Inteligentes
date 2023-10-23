# Importando as Blibliotecas
import pandas as pd

# Importando os dados

# Planilha onde os produtos são mapeados
linkker_df = pd.read_excel('linkker.xlsx')

# Planilha das exposições
expositor_df = pd.read_csv('exp.csv', sep=';')

# Mix total
mix_total_df = pd.read_csv('mix_total.csv', sep=';', encoding='latin1')


# Cadastro de usuário do abastecimento - Informação do analista responsável no abastecimento por departamento e seção
usuario_abastecimento = pd.read_excel('cadastro_usuario_abastecimento.xlsx')

# Limpando a planilha Linkker

lojas_validas = [43, 51, 94, 108, 116, 124, 167, 175, 183, 205, 221, 230, 248, 256, 264, 272,
                 299]  # Obs: Lojas não presentes temos uma regra de corte (uma espécie de limiter, que não precisa que a loja seja analisada - regra de negócio)
posicoes_compativeis = ['PE', 'PG', 'ILHA']  # Limpeza dos móveis diferentes dos três possíveis
em_linha = mix_total_df['RMS']  # verifica se o produto está em linha na Rede

linkker_df = linkker_df[
    (linkker_df['CÓDIGO DA LOJA'].isin(lojas_validas)) &  # Verifica se o produto está em linha
    (linkker_df['OBS'].isin(posicoes_compativeis)) &  # Verifica se a posição é valida
    (~linkker_df['CÓDIGO SKU'].isnull()) &  # Verifica se o campo código está vazio
    (linkker_df['CÓDIGO SKU'].isin(em_linha))  # Verifica se o produto está em linha (na rede)
    ]

# Retira as colunas que não vai ser útil para análise
colunas_manter = ['CÓDIGO DA LOJA', 'TIPO DE PEX', 'POSIÇÃO', 'OBS', 'INÍCIO DO PERÍODO', 'FIM DO PERÍODO',
                  'DATA DA VENDA', 'TIPO DE PERÍODO', 'USER QUE VENDEU', 'NOME SKU', 'CÓDIGO SKU']
linkker_df = linkker_df.loc[:, colunas_manter]


# Limpando e ajustando o DataFrame exp_df

def ajustar_formato(valor):
    if isinstance(valor, str):
        valor = valor.replace('.', '').replace(',', '.')
    return valor


# Aplicando a função na coluna QTDVENDA_30_DIAS
expositor_df['QTDVENDA_30_DIAS'] = expositor_df['QTDVENDA_30_DIAS'].apply(ajustar_formato)

# Convertendo a coluna para o tipo numérico
expositor_df['QTDVENDA_30_DIAS'] = pd.to_numeric(expositor_df['QTDVENDA_30_DIAS'], errors='coerce')

colunas_manter = ['CODIGO', 'LOJA', 'ILHA_CAP', 'PE_CAP', 'PG_CAP', 'SALDO_CD', 'QTDVENDA_30_DIAS']

exp_df = expositor_df.loc[:, colunas_manter] # Ajustando ordem das colunas e selecionando o que vamos utilizar

# Renomeando as colunas do DF
column_mapping = {
    'CODIGO': 'codigo',
    'CÓDIGO DA LOJA': 'loja',
    'ILHA_CAP': 'ilha',
    'PE_CAP': 'pe',
    'PG_CAP': 'pg',
    'QTDVENDA_30_DIAS': 'venda_30',
    'SALDO_CD': 'saldo_cd',

}

exp_df.rename(columns=column_mapping, inplace=True)

lkr_cols = linkker_df.columns  # Visualizar as colunas da linkker, como ficou após limpar a base
exp_cols = exp_df.columns  # Visualizar as colunas dos expositores, e conferir com a linkker

print('Colunas expositor: ', exp_cols)
print('Colunas linkker: ', lkr_cols)

linkker_df['INÍCIO DO PERÍODO'].dtypes


# Unindo as bases do expositor com a linkker baseado no código da loja e código do SKU
merged_df = linkker_df.merge(exp_df[['LOJA', 'codigo', 'venda_30', 'pe', 'pg', 'ilha', 'saldo_cd']],
                             left_on=['CÓDIGO DA LOJA', 'CÓDIGO SKU'],
                             right_on=['LOJA', 'codigo'],
                             how='left')

# Copiando os valores de venda_30  do merged_df para linkker_df
linkker_df['venda_30'] = merged_df['venda_30']

# Selecionar as colunas relevantes após a junção
result_df = merged_df[
    ['CÓDIGO DA LOJA', 'TIPO DE PEX', 'INÍCIO DO PERÍODO', 'FIM DO PERÍODO', 'DATA DA VENDA', 'TIPO DE PERÍODO',
     'USER QUE VENDEU', 'POSIÇÃO', 'OBS', 'NOME SKU', 'CÓDIGO SKU', 'venda_30', 'pe', 'pg', 'ilha', 'saldo_cd']].copy()

# preencher os valores vazios por zero
result_df['venda_30'] = result_df['venda_30'].fillna(0)

# Ajustando tipos de colunas
result_df.loc[:, 'pe'] = result_df['pe'].astype(float)
result_df.loc[:, 'pg'] = result_df['pg'].astype(float)
result_df.loc[:, 'ilha'] = result_df['ilha'].astype(float)
result_df.loc[:, 'saldo_cd'] = result_df['saldo_cd'].astype(float)

# Converter a coluna 'venda_30' para float
result_df['venda_30'] = result_df['venda_30'].astype(float)

# Filtrar o DataFrame para manter apenas as linhas onde 'saldo_cd' é maior que 1
result_df_filtrado = result_df[result_df['saldo_cd'] > 1]

# Agrupar e somar as Vendas por 'CÓDIGO DA LOJA' e 'POSIÇÃO'
agrup_soma_vda_loja_posicao = result_df_filtrado.groupby(['CÓDIGO DA LOJA', 'POSIÇÃO'])['venda_30'].sum().reset_index()

# Fazendo o merge com o DataFrame original
result_df = pd.merge(result_df, agrup_soma_vda_loja_posicao, on=['CÓDIGO DA LOJA', 'POSIÇÃO'], how='left')

# Chave de pesquisa entre o DF mix_total e result_df
chave_mix = 'RMS'
chave_result = 'CÓDIGO SKU'

# Colunas a serem selecionadas do mix_total_df
colunas_selecionadas_mix = ['SISTEMATICA', 'NOME_COMPRADOR', 'NOME_DEPARTAMENTO', 'SECAO', 'NOME_SECAO']

# Procura no mix total as colunas sistemática, comprador, departamento, seção, nome da seção e adiciona no DataFrame
result_df = result_df.merge(mix_total_df[colunas_selecionadas_mix + [chave_mix]],
                            how='left',
                            left_on=chave_result,
                            right_on=chave_mix)

# Remover a coluna utilizada como chave
result_df.drop(columns=[chave_mix], inplace=True)

# Valida e deixa somente os itens que são sistemática 1

sistematica_validas = [1] 

result_df = result_df[result_df['SISTEMATICA'].isin(sistematica_validas)]

# Renomeando as colunas do DF

column_mapping = {
    'CÓDIGO DA LOJA': 'loja',
    'venda_30_y': 'soma_venda_posicao',
    'venda_30_x': 'venda_30',
    'TIPO DE PEX': 'exp_nome',
    'INÍCIO DO PERÍODO': 'dt_inicio',
    'FIM DO PERÍODO': 'dt_fim',
    'TIPO DE PERÍODO': 'tipo_periodo',
    'USER QUE VENDEU': 'user_log',
    'DATA DA VENDA': 'dt_log',
    'POSIÇÃO': 'posicao_movel',
    'OBS': 'tipo_movel',
    'NOME SKU': 'nome_sku',
    'CÓDIGO SKU': 'codigo_sku',
    'SISTEMATICA': 'sistematica',
    'NOME_COMPRADOR': 'comprador',
    'NOME_DEPARTAMENTO': 'departamento',
    'SECAO': 'secao_id',
    'NOME_SECAO': 'secao'
}

result_df.rename(columns=column_mapping, inplace=True)

result_df['ilha'] = result_df['ilha'].fillna(0)
result_df['pg'] = result_df['pg'].fillna(0)
result_df['pe'] = result_df['pe'].fillna(0)


def map_capacidade(row):
    if row['tipo_movel'] == 'ILHA':
        return row['ilha']
    elif row['tipo_movel'] == 'PG':
        return row['pg']
    elif row['tipo_movel'] == 'PE':
        return row['pe']
    else:
        return None


result_df['capac_movel_mapeado'] = result_df.apply(map_capacidade, axis=1)

# Analisar os Produtos na Loja x Posição que não tem Exposição cadastrada

# Filtra os itens mapeados sem cadastro de expositor
itens_sem_exposicao_df = result_df[result_df['capac_movel_mapeado'] == 0].copy()

# Atribui um analista de abastecimento correspondente por seção
itens_sem_exposicao_df = itens_sem_exposicao_df.merge(usuario_abastecimento[['secao_id', 'analista_abastecimento']],
                                                      on='secao_id', how='left')

# Remove linhas com valores NaN na coluna 'analista_abastecimento'
# É um departamento que não é vai volume na linkker
# pelo abastecimento pelos parâmetros cadastrados na planilha usuario_abastecimento

itens_sem_exposicao_df = itens_sem_exposicao_df.dropna(subset=['analista_abastecimento'])

# Retira as colunas que não vai ser útil para essa análise

colunas_manter_exp = ['departamento', 'secao', 'loja', 'codigo_sku', 'nome_sku', 'posicao_movel', 'tipo_movel',
                      'capac_movel_mapeado', 'analista_abastecimento']
itens_sem_exposicao_df = itens_sem_exposicao_df.loc[:, colunas_manter_exp]

# Criar um arquivo Excel
nome_arquivo_excel = "Relatorio_itens_sem_expositor_cadastrado.xlsx"
writer = pd.ExcelWriter(nome_arquivo_excel, engine='xlsxwriter')

# Salvar cada DataFrame em uma tabela separada
analistas = itens_sem_exposicao_df['analista_abastecimento'].unique()

for analista in analistas:
    analista_df = itens_sem_exposicao_df[itens_sem_exposicao_df['analista_abastecimento'] == analista]
    analista_df.to_excel(writer, sheet_name=analista, index=False)

# Fechar o arquivo Excel
writer.close()

print(f"Arquivo {nome_arquivo_excel} exportado com sucesso.")

# Tirar itens com saldo CD < 1
colunas_manter = ['loja', 'exp_nome', 'dt_inicio', 'dt_fim', 'dt_log', 'tipo_periodo', 'user_log', 'posicao_movel',
                  'tipo_movel', 'nome_sku', 'codigo_sku', 'venda_30', 'pe', 'pg', 'ilha', 'saldo_cd',
                  'soma_venda_posicao', 'sistematica', 'comprador', 'departamento', 'secao_id', 'secao',
                  'capac_movel_mapeado']

linhas = result_df['saldo_cd'] > 1
result_df = result_df.loc[linhas, colunas_manter]

# Tirar itens com venda_30 0
colunas_manter = ['loja', 'exp_nome', 'dt_inicio', 'dt_fim', 'dt_log', 'tipo_periodo', 'user_log', 'posicao_movel',
                  'tipo_movel', 'nome_sku', 'codigo_sku', 'venda_30', 'pe', 'pg', 'ilha', 'saldo_cd',
                  'soma_venda_posicao', 'sistematica', 'comprador', 'departamento', 'secao_id', 'secao',
                  'capac_movel_mapeado']
linhas = result_df['venda_30'] > 0

result_df = result_df.loc[linhas, colunas_manter]

# Criar uma nova coluna 'qtd_exp_calc' inicialmente preenchida com zeros
result_df['qtd_exp_calc_posicao'] = 0

# Iterar pelas linhas do DataFrame para calcular os valores da nova coluna
for index, row in result_df.iterrows():
    venda_30 = row['venda_30']
    soma_venda_posicao = row['soma_venda_posicao']
    capac_movel_mapeado = row['capac_movel_mapeado']
    saldo_cd = row['saldo_cd']

    if saldo_cd > 1:  # Verificar se o saldo_cd é maior que 1
        if soma_venda_posicao != 0:
            qtd_exp_temp = (venda_30 / soma_venda_posicao) * capac_movel_mapeado # Aplicando a formula do calculo das exposições
            result_df.at[index, 'qtd_exp_calc_posicao'] = qtd_exp_temp

result_df['qtd_exp_calc_total'] = result_df.groupby(['loja', 'codigo_sku'])['qtd_exp_calc_posicao'].transform('sum')

result_df.to_excel('Relatório_comercial_agrupado.xlsx')

result_df['análise'] = 'Verificar'

# Converter as colunas para tipos numéricos
result_df['qtd_exp_calc_total'] = result_df['qtd_exp_calc_total'].astype(float)
result_df['venda_30'] = result_df['venda_30'].astype(float)

remover_linhas = result_df['qtd_exp_calc_total'] <= result_df['venda_30']  # Modificação aqui
result_df.loc[remover_linhas, 'análise'] = 'Remover'

result_df = result_df[result_df['análise'] == 'Verificar']

# Ajustando formatações
result_df['dt_inicio'] = pd.to_datetime(result_df['dt_inicio']).copy()
result_df['dt_fim'] = pd.to_datetime(result_df['dt_fim']).copy()
result_df['dt_log'] = pd.to_datetime(result_df['dt_log']).copy()

result_df['dt_inicio'] = result_df['dt_inicio'].dt.strftime('%d/%m/%Y').copy()
result_df['dt_fim'] = result_df['dt_fim'].dt.strftime('%d/%m/%Y').copy()
result_df['dt_log'] = result_df['dt_log'].dt.strftime('%d/%m/%Y').copy()

result_df['qtd_rep_cod_sku'] = result_df.groupby(['loja', 'codigo_sku'])['codigo_sku'].transform('count')
result_df['qtd_exp_calc_total'] = result_df['qtd_exp_calc_total'].round(0)
result_df['qtd_exp_calc_total'] = result_df['qtd_exp_calc_total'].astype(int).astype(str)

# Organizando as colunas
colunas_manter = ['comprador', 'exp_nome', 'tipo_periodo', 'loja', 'codigo_sku', 'nome_sku', 'posicao_movel',
                  'tipo_movel', 'venda_30', 'qtd_exp_calc_total', 'qtd_rep_cod_sku', 'análise']
result_df = result_df.loc[:, colunas_manter]

grupos_comprador = result_df.groupby('comprador')

# Criar um arquivo Excel e adicionar abas para cada comprador
arquivo_excel = "Relatório_comercial.xlsx"
writer = pd.ExcelWriter(arquivo_excel, engine='openpyxl')

# Adicionar cada grupo como uma aba separada
for comprador, grupo in grupos_comprador:
    nome_aba = comprador[:31]  # Limitar o tamanho do nome da aba para 31 caracteres (limite do Excel)
    grupo.to_excel(writer, sheet_name=nome_aba, index=False)

writer.close();

print('Relatório_comercial gerado com Sucesso!')
