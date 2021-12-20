# SetupLarryWillians
Setup Larry Willians (detalhes em https://www.youtube.com/watch?v=QXzkrR-dX1E

Este script executa o setup LW de 3 médias móveis SMA21(fechamento) SMA3(max) e SMA3(min). O script usa com arquivos de entrada os arquivos CSV gerados pelo Tryd (homebroker). 
Os arquivos salvos pelo Tryd deverão estar no formato <TICKER_B3>_Tryd.csv (exemplo: ABEV3_Tryd.csv)

São dois scripts:

*** Migracao_Tryd_para_Python.py ***
Este scripts le os arquivos gerados pelo Tryd e os converte em tabelas que são tranformadas em DATAFRAME para posterior processamento. Os arquivos gerados tem a nomemclatura <TICKER_B3>_Python.csv (ex. ABEV3_Python.csv).

*** QuantLarryWilliansSetup3Medias.py ***
Este script tem parâmetros de configuração
LISTA_B3 = {"TAEE11","ENBR3", "ITSA4","TRPL4"}  # lista de ativos que vou pegar os dados (pode ser qq quantidade)
PERIODOS_SMA = 21                               # nr de períodos da SMA mais longa (default é 21)
NUMERO_DE_DIAS = 600                            # dias que vai pegar do histórico do Tryd (default é 600)
DESABILITA_VENDA = True                         # somente operacões de compra (default é True), se False vai operar na ponta vendida também

O resultado do backtest é armazenado em arquivo txt de formato Resultado_ANO_MES_DIA_HORA_MINUTO.txt (ex. Resultado_2021_19_12_21_16_10.txt)

NOTA: SÓ FUNCIONA PARA TIMEFRAME DIÁRIO.
