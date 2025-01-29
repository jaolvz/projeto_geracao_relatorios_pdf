import pandas as pd
from fpdf import FPDF


bitrix= pd.read_csv('bitrix.csv', encoding='ISO-8859-1', sep=';')
baixas = pd.read_csv('baixas.csv',encoding='ISO-8859-1', sep=';')
baixas = baixas[baixas['DATA BAIXA'].notna()]

#vivo = pd.read_csv('vivo.csv' , encoding='ISO-8859-1', sep=';')
#tabela_vivo = vivo[['Unnamed: 6','Unnamed: 7','Unnamed: 11','Unnamed: 30', 'Unnamed: 31','Unnamed: 41']]

tabela_bitrix = bitrix[['Movimento Principal','Empresa: CNPJ/CPF','Empresa: Nome da empresa','Total','Contato: Primeiro nome', 'SDR','Closer','Front','STATUS']].head(197)
tabela_bitrix['Total'] = tabela_bitrix['Total'].str.replace(',', '.').astype(float)
tabela_bitrix['SDR'] = tabela_bitrix['SDR'].str.upper()
tabela_bitrix['Closer'] = tabela_bitrix['Closer'].str.upper()
tabela_bitrix = tabela_bitrix.replace('DESIREE BORBA', 'DESIREE RIENTE')

comercial1 = ['RAFAELA ASSIS','JULIA GOMES','MATHEUS SOUZA','BEATRIZ FERREIRA','JULIANA BERNARDINO']
comercial2 = ['DESIREE RIENTE','ALEXIA RODRIGUES','JHENIFER CASIMIRO']
comercialnv = ['NEA BARROS','PEDRO LUCAS']

def buscar_baixas(nome, tabela_baixas):
    df_filtrado =  tabela_baixas[(tabela_baixas['Contato: Primeiro nome']== nome)]
    razoes_sociais_baixadas=[]
    for index, row in df_filtrado.iterrows():
        razoes_sociais_baixadas.append(row['NOME CLIENTE'])
    return razoes_sociais_baixadas

def soma_total_da_faixa(arquivo_bitrix,nome, variacao):
    
    if variacao == 'comercial':
        movimentos_possiveis = [
            'Alta', 'Link', 'BL - Gpon', 'VVN','Portabilidade PF-PJ', 'Portabilidade', 'Portabilidade PJ-PJ'
]   
    elif variacao == 'closer':
        movimentos_possiveis = [
            'Alta'
]  

    df_filtrado =  arquivo_bitrix[(arquivo_bitrix['Contato: Primeiro nome']== nome) & (arquivo_bitrix['Movimento Principal'].isin(movimentos_possiveis))]

    return df_filtrado['Total'].sum()

def trunc(num):
    formatted_num = f"{num:.10f}"  # Format the number to 10 decimal places
    return formatted_num[:formatted_num.find('.') + 3]  # Keep only up to 2 decimal places

def verificar_mei(cnpj, nome_fantasia):
    nome_fantasia = nome_fantasia.replace('.', '')
    if str(cnpj)[:8]== nome_fantasia[:8]:
        return True
    return False

def calculo_sdr (nome, tabela_bitrix):
    df_filtrado =  tabela_bitrix[(tabela_bitrix['SDR']== nome)]
    total_comissionamento = 0.0
    alta =0.025
    renovacao = 0.01
    energia_B = 0.025
    energia_A =0.001
    rzsocial_alta=[]
    total_alta =0
    rzsocial_renovacao=[]
    total_renovacao =0
    
    for index, row in df_filtrado.iterrows():

        if row['Movimento Principal'] == 'Alta' or row['Movimento Principal'] == 'Portabilidade PF-PJ' or row['Movimento Principal'] == 'Portabilidade' or row['Movimento Principal'] == 'Portabilidade PJ-PJ' :
            comissão = row['Total']
            comissão = (comissão*alta)
            rzsocial_alta.append(row['Empresa: Nome da empresa'])
            total_comissionamento  += comissão
            total_alta+=comissão
            comissão=0  

    #Renovação
        elif row['Movimento Principal'] == 'Renovação Móvel' or row['Movimento Principal'] == 'Renovação Fixa':
            comissão = row['Total']
            comissão =  (comissão*renovacao)
            rzsocial_renovacao.append(row['Empresa: Nome da empresa'])
            total_comissionamento  += comissão
            total_renovacao+=comissão
            comissão=0  
        
        #falta energia A
     
        #falta energia 
    
   
    return trunc(total_comissionamento), rzsocial_alta,total_alta, rzsocial_renovacao,total_renovacao

def calculo_comercial(nome, tabela_bitrix):
    df_filtrado =  tabela_bitrix[(tabela_bitrix['Contato: Primeiro nome']== nome)]
    meta_batida = False
    rzsocial_mei = []
    total_mei = 0
    rzsocial_prepos=[]
    total_prepos= 0
    rzsocial_renovacao = []
    total_renovacao= 0
    rzsocial_alta= []
    total_alta= 0
    rzsocial_bl = []
    total_bl=0

    if nome in comercial1:
        if soma_total_da_faixa(tabela_bitrix, nome,'comercial') <= 1500:
            movel_alta = 0.05  # 5% como valor decimal
        else:
            movel_alta = 0.20  # 20% como valor decimall
            meta_batida= True
        BL_VVN_LINK_SIP = 0.25  
        MEI = 0.04  
        pre_pos = 0.10  
        renovacao = 0.10 

    elif nome in comercial2:
        if soma_total_da_faixa(tabela_bitrix, nome, 'comercial') <= 1500:
            movel_alta = 0.10  
        else:
            movel_alta = 0.25  # 20% como valor decimall
            meta_batida= True
        BL_VVN_LINK_SIP = 0.25 
        MEI = 0.04  
        pre_pos = 0.10  
        renovacao = 0.10
        
    else:
        
        movel_alta = 0.10 
        BL_VVN_LINK_SIP = 0.20  
        MEI = 0.04  
        pre_pos = 0.10  
        renovacao = 0.10  

    for index, row in df_filtrado.iterrows():
        
        if verificar_mei(row['Empresa: CNPJ/CPF'],row['Empresa: Nome da empresa']):
            comissão = row['Total']
            comissão = (comissão*MEI)
            rzsocial_mei.append(row['Empresa: Nome da empresa'])
            total_mei+=comissão
            comissão=0  
        
        #pre-pos 
        elif row['Movimento Principal'] == 'Mig Pre/Pos':
            comissão = row['Total']
            comissão = (comissão*pre_pos)
            rzsocial_prepos.append(row['Empresa: Nome da empresa'])
            total_prepos+=comissão
            comissão=0  

    #Renovação
        elif row['Movimento Principal'] == 'Renovação Móvel':
            comissão = row['Total']
            comissão =  (comissão*renovacao)
            rzsocial_renovacao.append(row['Empresa: Nome da empresa'])
            total_renovacao+=comissão
            comissão=0  
        
        #BANDA LARGA, VVN, LINK
        elif row['Movimento Principal'] == 'BL - Gpon' or row['Movimento Principal'] == 'VVN' or row['Movimento Principal'] == 'Link':
            comissão = row['Total']
            comissão =  (comissão*BL_VVN_LINK_SIP) 
            rzsocial_bl.append(row['Empresa: Nome da empresa'])
            total_bl+=comissão
            comissão=0  

        #ALTA 
        elif row['Movimento Principal'] == 'Alta' or row['Movimento Principal'] == 'Portabilidade PF-PJ' or row['Movimento Principal'] == 'Portabilidade' or row['Movimento Principal'] == 'Portabilidade PJ-PJ' :
            comissão = row['Total']
            comissão = (comissão*movel_alta)
            rzsocial_alta.append(row['Empresa: Nome da empresa'])
            total_alta+=comissão
            comissão=0  
    total_comissionamento = float(trunc(total_alta)) + float(trunc(total_bl))+float(trunc(total_mei))+float(trunc(total_prepos))+float(trunc(total_renovacao))
    return trunc(total_comissionamento),meta_batida,rzsocial_alta,total_alta,rzsocial_bl, total_bl,rzsocial_mei, total_mei,rzsocial_prepos, total_prepos, rzsocial_renovacao,total_renovacao

def calculo_closer (nome, tabela_bitrix):
    df_filtrado =  tabela_bitrix[(tabela_bitrix['Closer']== nome)]
    meta_batida = False
    if  soma_total_da_faixa (tabela_bitrix,nome,'closer') <=1500:
        alta = 0.05
    else:
        alta =0.10
    BL_VVN_LINK_SIP = 0.15
    pre_pos = 0.10
    MEI = 0.04
    renovacao = 0.10
    energia_B = 0.05
    energia_A =0.025
    rzsocial_mei = []
    total_mei = 0
    rzsocial_prepos=[]
    total_prepos= 0
    rzsocial_renovacao = []
    total_renovacao= 0
    rzsocial_alta= []
    total_alta= 0
    rzsocial_bl = []
    total_bl=0
    for index, row in df_filtrado.iterrows():
        
        if verificar_mei(row['Empresa: CNPJ/CPF'],row['Empresa: Nome da empresa']):
            comissão = row['Total']
            comissão = (comissão*MEI) 
            rzsocial_mei.append(row['Empresa: Nome da empresa'])
            total_mei+=comissão
            comissão=0  
        
        #pre-pos 
        elif row['Movimento Principal'] == 'Mig Pre/Pos':
            comissão = row['Total']
            comissão = (comissão*pre_pos)
            rzsocial_prepos.append(row['Empresa: Nome da empresa'])
            total_prepos+=comissão
            comissão=0  

    #Renovação
        elif row['Movimento Principal'] == 'Renovação Móvel':
            comissão = row['Total']
            comissão =  (comissão*renovacao)   
            rzsocial_renovacao.append(row['Empresa: Nome da empresa'])
            total_renovacao+=comissão
            comissão=0  
        
        #BANDA LARGA, VVN, LINK
        elif row['Movimento Principal'] == 'BL - Gpon' or row['Movimento Principal'] == 'VVN' or row['Movimento Principal'] == 'Link':
            comissão = row['Total']
            comissão =  (comissão*BL_VVN_LINK_SIP)   
            rzsocial_bl.append(row['Empresa: Nome da empresa'])
            total_bl+=comissão
            comissão=0  

        #ALTA 
        elif row['Movimento Principal'] == 'Alta' or row['Movimento Principal'] == 'Portabilidade PF-PJ' or row['Movimento Principal'] == 'Portabilidade' or row['Movimento Principal'] == 'Portabilidade PJ-PJ' :
            comissão = row['Total']
            comissão = (comissão*alta)
            rzsocial_alta.append(row['Empresa: Nome da empresa'])
            total_alta+=comissão
            comissão=0  
        #falta ENERGIA A
        #falta energia B
    total_comissionamento = float(trunc(total_alta)) + float(trunc(total_bl))+float(trunc(total_mei))+float(trunc(total_prepos))+float(trunc(total_renovacao))
    return   total_comissionamento, rzsocial_alta,total_alta, rzsocial_bl,total_bl,rzsocial_mei,total_mei, rzsocial_prepos,total_prepos, rzsocial_renovacao,total_renovacao

todos_funcionarios = comercial1+comercial2+comercialnv

for funcionario in todos_funcionarios:
    nome_foco =funcionario
    total_sdr,altas_sdr,valor_altas_sdr,renovacao_sdr,valor_renovacao_sdr= calculo_sdr(nome_foco,tabela_bitrix)
    total_closer, alta_closer, total_alta_closer , bl_closer, total_bl_closer, mei_closer, total_mei_closer,prepos_closer, total_prepos_closer, renovacao_closer, total_renovacao_closer = calculo_closer(nome_foco, tabela_bitrix)
    total_comercial,meta_comercial, alta_comercial, total_alta_comercial , bl_comercial, total_bl_comercial, mei_comercial, total_mei_comercial,prepos_comercial, total_prepos_comercial, renovacao_comercial, total_renovacao_comercial = calculo_comercial(nome_foco, tabela_bitrix)


    class PDF (FPDF):
        def header(self):
            page_width = self.w
            
            # Largura da imagem (ajuste conforme necessário)
            image_width = 75
            
            # Calcula a posição X para centralizar a imagem
            x_position = (page_width - image_width) / 2
            
            # Adiciona a imagem centralizada
            self.image('logo.png', x_position, 10, image_width)
            

            self.ln(29)
        def footer(self):
            self.set_y(-15)  
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C') 
    pdf = PDF('P', 'mm', 'Letter')
    pdf.add_page()

    pdf.set_font("helvetica", "B", 13)
    pdf.cell(0, 10, 'Resultado Bônus de Campanha - Dezembro/2024',align='C')
    pdf.ln()
    pdf.line(10, pdf.get_y(), pdf.w - 10, pdf.get_y())
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(40, 10, f'{nome_foco}')
    pdf.ln()

    total_bonus_campanha =float(total_closer)+float(total_comercial)+float(total_sdr)

    pdf.set_font("helvetica", "B", 10)
    pdf.cell(40, 10, f'Comissão direta de 5% - R${trunc(total_bonus_campanha*(5/100))} ')
    pdf.ln()
    pdf.cell(40, 10, f'Bônus de Campanha SDR - R${total_sdr} ')
    pdf.ln()
    pdf.cell(40, 10, f'Bônus de Campanha Closer - R${total_closer} ')
    pdf.ln()
    pdf.cell(40, 10, f'Bônus de Campanha Comercial - R${total_comercial} ')
    pdf.ln()
    pdf.cell(40, 10, f'Ajustes')
    pdf.ln()
    pdf.cell(40, 10, f'Total = R${trunc(total_bonus_campanha)}')
    pdf.ln()
    pdf.line(10, pdf.get_y(), pdf.w - 10, pdf.get_y())



    #SDR
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, f'SDR - R${trunc(float(total_sdr))}',align='C')
    pdf.ln()
    #alta SDR
    if valor_altas_sdr:
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(40, 10, f'Bônus de  Campanha Alta - R$ {trunc(valor_altas_sdr)}')
        pdf.ln()

        pdf.set_font("helvetica", "", 10)
        for rzsocial in altas_sdr: 
            pdf.cell(40, 10, f'{rzsocial}')
            pdf.ln()

    #RENOVACAOS SDR
    if valor_renovacao_sdr:
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(40, 10, f'Bônus de Campanha Renovação - R$ {trunc(valor_renovacao_sdr)}')
        pdf.ln()

        pdf.set_font("helvetica", "", 10)
        for rzsocial in renovacao_sdr: 
            pdf.cell(40, 10, f'{rzsocial}')
            pdf.ln()

    pdf.line(10, pdf.get_y(), pdf.w - 10, pdf.get_y())

    #CLOSER
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, f'Closer - R${total_closer}',align='C')
    pdf.ln()
    #renovacao closer
    if total_renovacao_closer:
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(40, 10, f'Bônus de Campanha Renovação - R$ {trunc(total_renovacao_closer)}')
        pdf.ln()

        pdf.set_font("helvetica", "", 10)
        for rzsocial in renovacao_closer: 
            pdf.cell(40, 10, f'{rzsocial}')
            pdf.ln()
    #bl vvn e etc closer
    if total_bl_closer:
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(40, 10, f'Bônus de Campanha BL/VVN/LINK/SIP - R$ {trunc(total_bl_closer)}')
        pdf.ln()

        pdf.set_font("helvetica", "", 10)
        for rzsocial in bl_closer: 
            pdf.cell(40, 10, f'{rzsocial}')
            pdf.ln()
    #mei closer

    if total_mei_closer:
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(40, 10, f'Bônus de Campanha MEI - R$ {trunc(total_mei_closer)}')
        pdf.ln()

        pdf.set_font("helvetica", "", 10)
        for rzsocial in mei_closer: 
            pdf.cell(40, 10, f'{rzsocial}')
            pdf.ln() 
    #prepos closer
    if total_prepos_closer:
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(40, 10, f'Bônus de Campanha Pré-Pós - R$ {trunc(total_prepos_closer)}')
        pdf.ln()

        pdf.set_font("helvetica", "", 10)
        for rzsocial in prepos_closer: 
            pdf.cell(40, 10, f'{rzsocial}')
            pdf.ln()
    #alta closer
    if total_alta_closer:
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(40, 10, f'Bônus de Campanha Alta - R$ {trunc(total_alta_closer)}')
        pdf.ln()

        pdf.set_font("helvetica", "", 10)
        for rzsocial in alta_closer: 
            pdf.cell(40, 10, f'{rzsocial}')
            pdf.ln()

    pdf.line(10, pdf.get_y(), pdf.w - 10, pdf.get_y())

    #COMERCIAL
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, f'Comercial - R${total_comercial}',align='C')
    pdf.ln()

    #renovação comercial
    if total_renovacao_comercial:
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(40, 10, f'Bônus de Campanha Renovação - R$ {trunc(total_renovacao_comercial)}')
        pdf.ln()
        pdf.set_font("helvetica", "", 10)
        for rzsocial in renovacao_comercial: 
            pdf.cell(40, 10, f'{rzsocial}')
            pdf.ln()

    #alta comercial
    if total_alta_comercial:
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(40, 10, f'Bônus de Campanha Alta- R$ {trunc(total_alta_comercial)}')
        pdf.ln()
        pdf.set_font("helvetica", "", 10)
        for rzsocial in alta_comercial: 
            pdf.cell(40, 10, f'{rzsocial}')
            pdf.ln()

    #bl comercial
    if total_bl_comercial:
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(40, 10, f'Bônus de Campanha BL/VVN/LINK/SIP- R$ {trunc(total_bl_comercial)}')
        pdf.ln()
        pdf.set_font("helvetica", "", 10)
        for rzsocial in bl_comercial: 
            pdf.cell(40, 10, f'{rzsocial}')
            pdf.ln()


    #prepos comercial
    if total_prepos_comercial:
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(40, 10, f'Bônus de Campanha Pré-Pós - R$ {trunc(total_prepos_comercial)}')
        pdf.ln()

        pdf.set_font("helvetica", "", 10)
        for rzsocial in prepos_comercial: 
            pdf.cell(40, 10, f'{rzsocial}')
            pdf.ln()        

    #mei comercial

    if total_mei_comercial:
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(40, 10, f'Bônus de Campanha MEI - R$ {trunc(total_mei_comercial)}')
        pdf.ln()

        pdf.set_font("helvetica", "", 10)

    pdf.line(10, pdf.get_y(), pdf.w - 10, pdf.get_y())


    #BAIXAS
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, f'Ajustes',align='C')
    pdf.ln()
    pdf.set_font("helvetica", "", 10)
    for rzsocial in buscar_baixas(nome_foco,baixas):
        pdf.cell(40, 10, f'{rzsocial}')
        pdf.ln()

    pdf.output(f'{nome_foco}.pdf')  
