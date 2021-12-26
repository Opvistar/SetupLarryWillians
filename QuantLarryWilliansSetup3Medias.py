# =============================================================================
# Autor: @opvistar (Twitter) - dez.2021                                       #
# SETUP LARRY WILLIANS 3 MÉDIAS MÓVEIS                                        #
# DESCRIÇÃO DO SETUP : https://www.youtube.com/watch?v=QXzkrR-dX1E            #
# VERSÃO: 1.2.0 (26.12.21)                                                    #
# HISTORICO ALTERACOES                                                        #
# 1.1.0 - adicionei nova feature, agora salva CSV para visualizar no Excel    #
# entretanto o cabeçalho tem que ser inserido manualmente.                    #
# separador é ";"                                                             #
# 1.2.0 - (a) agora verifica se abriu em gap acima ou abaixo das SMA3min#     #
# e SMA3max# # tomando cuidado pra comprar na abertura se preço não cruza     #
# essas médias (b) desabiilitei o código da operação de VENDA                 # 
#                                                                             #
# 1.2.1 - (a) bug de comparação da SMA21 na venda, ">" para "<"               #
#         l_sma21[x-1] < l_sma21[x-2]                                         #
#         (b) agora arquivos identificam se é compra/venda                    #
#==============================================================================

import datetime
import pandas as pd
import Migracao_Tryd_para_Python  as migratryd


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
import csv


###################################################################################################################################
#                                                                                                                                 #
######                                                     INICIO DO PROGRAMA                                                ######
#                                                                                                                                 #
###################################################################################################################################

   

#############     PARÂMETROS DE CONFIGURACAO     ################
LISTA_B3 = {"WIN"}     # lista de ativos que vou pegar os dados (TICKER DA B3!!)
PERIODOS_SMA = 21
NUMERO_DE_DIAS = 2000     # qtdade dias que vai pegar do histórico do Tryd
DESABILITA_VENDA = False   # somente operacões de compra = True
###############################################################  


# converte arquivo do Tryd para datframe Python 
migratryd.ConverteArquivosTryd(LISTA_B3,NUMERO_DE_DIAS)

dict_ativos_precos = {}

# crio uma lista de arrays com dados das operacoes    0           1            2            3       4         5     
#                                                 DATA_en    DATA_sai      ENTRADA    SAIDA     RESULTADO  ACUMULADO  
DATA_EN  = 0
DATA_SAI = 1
ENTRADA  = 2                          
SAIDA    = 3
RESULTADO = 4
ACUMULADO = 5
TIPO      = 6

if( DESABILITA_VENDA ):
    texto ="_Compra_"
else:
    texto = "_Compra_Venda_"


for ativo in LISTA_B3:
 
     file_name_py  =  ativo + "_python.csv"
     lSucesso = True
     ativo_python = pd.DataFrame(columns = ["Data","Abertura", "Fechamento","Maxima","Minima"])    
     
     try:         
         ativo_python = pd.read_csv(file_name_py, encoding = "ISO-8859-1")
     except ( IOError, NameError,PermissionError,FileNotFoundError) as e:
         print("#################################################################################################")
         print("         ### ATENÇÃO ### ocorreu um problema na leitura do arquivo .csv do ativo : " + ativo + " ..." )
         print(e)
         lSucesso = False
         print("#################################################################################################")
     if lSucesso and len(ativo_python) > 0:   
        print("Leitura arquivo .csv do ativo " + ativo + ' bem sucedida...' )
         
        # cria dicionario para cada ticker com o historico de preços
        dict_ativos_precos[ativo] = ativo_python       
print('\n')

##################################################################
#######################  INICIO DO ALGORITMO #####################
##################################################################
# itero sobre lista de ativos
nome_arquivo = "Resultado_" + texto + datetime.datetime.now().strftime('%Y_%d_%m_%H_%M_%S') + ".txt"
file_relat = open( nome_arquivo, "a")  # DEBUG
if dict_ativos_precos:


    for kx_ativo, vx_preco in sorted(dict_ativos_precos.items()):
        historico = []
        # inverto as linhas (de forma que linha 0 fique por ultimo e ultima linha por primeiro)   
        vx_preco  = vx_preco[::-1]
        
        sma21 = vx_preco['Fechamento'].rolling(window = PERIODOS_SMA).mean()
        sma3_max = vx_preco['Maxima'].rolling(window = 3 ).mean()
        sma3_min = vx_preco['Minima'].rolling(window = 3 ).mean()
        
        # comeca do ultimo para o 1o
        # só encerro a operação no outro dia, pois não sei se abriu e bateu na SMA3_max primeiro ou na SMA3_min primeiro, só 
        # tenho 3 informações do dia: abertura, fechamento, max e min, mas não sei o caminho ao longo desse dia.
        # 
        
        # transforma  a porra toda em list porque é muito mais facil de trabalhar que essa merda de dataframe....        
        l_sma21      = sma21.tolist()
        l_sma3_max   = sma3_max.tolist()
        l_sma3_min   = sma3_min.tolist()
        l_preco_max  =  vx_preco['Maxima'].tolist()        
        l_preco_min  = vx_preco['Minima'].tolist()
        l_preco_abe  = vx_preco['Abertura'].tolist()        
        l_preco_Data = vx_preco['Data'].tolist()

        for x in range(PERIODOS_SMA + 1,len(l_preco_Data), 1):
             
            if not historico:
                acumulado = 0
                saida = 0
            else:
                
                elemento_historico = historico[len(historico)-1]
                acumulado = elemento_historico[ACUMULADO]
                saida = elemento_historico[SAIDA]

            # se for diferente de -1, não tem operação aberta...
            if( saida != -1):

                ## VERIFICO SE A MEDIA MOVEL SMA21 TA SUBINDO...
                if( (l_preco_min[x] < l_sma3_min[x]) and  l_sma21[x-1] > l_sma21[x-2] ): # SMA21 mais recente maior que anterior

                    # tenho que verificar se abriu em gap de baixa, as vezes abriu em gap e a máxima do dia ainda está abaixo da SMA3min.
                    
                    # se já abriu abaixo da SMA3_min, já compro na abertura
                    if( l_preco_abe[x] < l_sma3_min[x]): 
                       historico.append( [l_preco_Data[x],"",l_preco_abe[x],-1,0,acumulado,"COMPRA"] )
                    else:
                    # neste caso efetua a compra do ativo quando cruza SMA3min 
                        historico.append( [l_preco_Data[x],"",l_sma3_min[x],-1,0,acumulado,"COMPRA"] )

                # ## VERIFICO SE A MEDIA MOVEL SMA21 TA DESCENDO...
                elif( (l_preco_max[x] > l_sma3_max[x]) and  l_sma21[x-1] < l_sma21[x-2] and not DESABILITA_VENDA): # SMA21 mais recente menor que anterior
                    # efetua a venda do ativo                      
                    if( l_preco_abe[x] > l_sma3_max[x]): 
                       # se abriu em gap de alta, ja vendo na abertura
                       historico.append( [l_preco_Data[x],"",l_preco_abe[x],-1,0,acumulado,"VENDA"] )
                    else:                    
                        historico.append( [l_preco_Data[x],"",l_sma3_max[x],-1,0,acumulado,"VENDA"] ) 
                    
            # operacao em aberto, verifica se pode encerrar                    
            else:    
                # agora verifico se algum dos criterios foram atendidos...
                elemento_historico = historico[len(historico)-1]    
                                 
                if( l_preco_max[x] >= l_sma3_max[x] and elemento_historico[TIPO] == "COMPRA"):
                     # encerra a operaçã0 de compra

                    # tenho que verificar se abriu em gap de alta, as vezes abriu em gap e a mínima do dia ainda está acima do SMA3max.
                   
                    # se abriu com gap, já zero na abertura
                    if( l_preco_abe[x] > l_sma3_max[x]): 
                        elemento_historico[SAIDA] = l_preco_abe[x]
                    else:
                        # senao zera ao tocar na SMA3max                        
                        elemento_historico[SAIDA] = l_sma3_max[x]
                        
                    elemento_historico[DATA_SAI] = l_preco_Data[x]
                    elemento_historico[RESULTADO] = elemento_historico[SAIDA] - elemento_historico[ENTRADA]
                    elemento_historico[ACUMULADO] = elemento_historico[ACUMULADO] + elemento_historico[RESULTADO]
                    historico[len(historico)-1] = elemento_historico
                    
                elif( l_preco_min[x] <= l_sma3_min[x] and elemento_historico[TIPO] == "VENDA" and not DESABILITA_VENDA):
                    #encerra a operação de venda se abriu abaixo da SMA3max    
                    if(l_preco_abe[x] < l_sma3_min[x]):  
                        # se abriu com gap, já zero na abertura
                        elemento_historico[SAIDA] = l_preco_abe[x]
                    else:              
                        # senao zera ao tocar na SMA3min
                        elemento_historico[SAIDA] = l_sma3_min[x]
                        
                    elemento_historico[DATA_SAI] = l_preco_Data[x]
                    elemento_historico[RESULTADO] = elemento_historico[ENTRADA] - elemento_historico[SAIDA]
                    elemento_historico[ACUMULADO] = elemento_historico[ACUMULADO] + elemento_historico[RESULTADO]
                    historico[len(historico)-1] = elemento_historico                    


        print('\n',file=file_relat)        
        print("Resultados para o ativo :" + kx_ativo +'\n',file=file_relat )
        tabela = pd.DataFrame(historico,columns=['DATA_EN', 'DATA_SAI', 'ENTRADA','SAIDA','RESULTADO','ACUMULADO','TIPO'])
        print('==================================================================================================',file=file_relat)       
        print(tabela.round(decimals=2),file=file_relat)
        
        historico_csv = [ ]

            
        for x in range(0,len(historico), 1): 
            elemento_historico = historico[x] 
            elemento_historico[SAIDA]     = str(round(elemento_historico[SAIDA],2)).replace('.',',')
            elemento_historico[ENTRADA]   = str(round(elemento_historico[ENTRADA],2)).replace('.',',')
            elemento_historico[RESULTADO] = str(round(elemento_historico[RESULTADO],2)).replace('.',',')
            elemento_historico[ACUMULADO] = str(round(elemento_historico[ACUMULADO],2)).replace('.',',')
            historico_csv.append(elemento_historico)
            
        with open("Planilha_"+ texto + kx_ativo +"_"+ datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S') + '.csv', 'w', newline='\n') as csvfile:
            writer = csv.writer(csvfile)
            csvwriter = csv.writer(csvfile,delimiter =';')
            # 'Numerador','Denominador','Preço_NUM','Preço_DEN','Ratio_Ult' 'Ratio Inst' 'Ratio_medio','Ratio_2D_minus','Ratio_2D_plus','Ratio_3D_minus','Ratio_3D_plus','Ratio_4D_minus','Ratio_4D_plus' 
            csvwriter.writerows(historico_csv)        
        
        
        
print("Backtest conluído, verifique o arquivo " + nome_arquivo)    
file_relat.close()    


