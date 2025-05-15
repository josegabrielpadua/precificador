import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from io import BytesIO
import plotly.express as px
import math 
from google_ai.ai import AIGoogle


def to_excel(df):
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

def calcular_custo_frete(row, reputacao):

    try:
        valor_produto = pd.to_numeric(row['Preço POR'], errors='coerce')
        if pd.isna(valor_produto):
             return None 
    except KeyError:
        return None 

    try:
        comprimento_m = pd.to_numeric(row["COMPRIMENTO"], errors="coerce") / 100
        largura_m = pd.to_numeric(row["LARGURA"], errors="coerce") / 100
        altura_m = pd.to_numeric(row["ALTURA"], errors="coerce") / 100

        # Handle potential NaN values if conversion fails
        if pd.isna(comprimento_m) or pd.isna(largura_m) or pd.isna(altura_m):
            return None # Or some indicator of an error/missing data

        peso = (comprimento_m * largura_m * altura_m) * 167
    except (TypeError, KeyError, ValueError):
         # Handle cases where columns are missing or not convertible
         return None # Indicate calculation failed

    custo_base = 0

    if valor_produto <= 79:
        custo_base = 0
    elif peso <= 0.5:
        custo_base = 27.90
    elif 0.5 < peso <= 1:
        custo_base = 32.90
    elif 1 < peso <= 2:
        custo_base = 35.90
    elif 2 < peso <= 5:
        custo_base = 44.90
    elif 5 < peso <= 9:
        custo_base = 47.90
    elif 9 < peso <= 13:
        custo_base = 52.90
    elif 13 < peso <= 17:
        custo_base = 57.90
    elif 17 < peso <= 23:
        custo_base = 62.90
    elif 23 < peso <= 29:
        custo_base = 67.90
    elif 29 < peso <= 30:
        custo_base = 69.90
    elif 30 < peso <= 40:
        custo_base = 179.90
    elif 40 < peso <= 50:
        custo_base = 189.90
    elif 50 < peso <= 60:
        custo_base = 199.90
    elif 60 < peso <= 70:
        custo_base = 209.90
    elif 70 < peso <= 80:
        custo_base = 219.90
    elif 80 < peso <= 90:
        custo_base = 229.90
    elif 90 < peso <= 100:
        custo_base = 239.90
    elif 100 < peso <= 110:
        custo_base = 249.90
    elif 110 < peso <= 120:
        custo_base = 259.90
    elif 120 < peso <= 130:
        custo_base = 269.90
    elif 130 < peso <= 140:
        custo_base = 279.90
    elif 140 < peso <= 150:
        custo_base = 289.90
    elif 150 < peso <= 160:
        custo_base = 299.90
    elif 160 < peso <= 170:
        custo_base = 309.90
    elif 170 < peso <= 180:
        custo_base = 319.90
    elif 180 < peso <= 190:
        custo_base = 329.90
    elif 190 < peso <= 200:
        custo_base = 339.90
    else: 
        custo_base = 349.90

    final_custo = custo_base 
    if reputacao == 99.9: 
        final_custo = custo_base * 0.25 
    elif reputacao >= 0.97:
        final_custo = custo_base * 0.50 
    elif 0.92 <= reputacao < 0.97:
        final_custo = custo_base * 0.75 

    return max(0, final_custo)

def recomendar_preco_amazon(comissao, comissao_fixa, quantidade, preco_custo, frete, preco_venda, imposto, tarifa, desconto=0.0, cashback=0.0):

    preco_venda_efetivo = preco_venda
    cashback_valor = 0


    if preco_venda <= 0:
        return -float('inf') 

    if desconto > 0:

        cashback_valor = preco_venda * (cashback / 100) 
        preco_venda_efetivo = preco_venda * (1 - desconto / 100)

        if preco_venda_efetivo <= 0:
             return -float('inf')

        x = preco_venda_efetivo * (comissao / 100) 
        y = preco_venda_efetivo * (imposto / 100) 
        
        lucro_liquido = preco_venda_efetivo + cashback_valor - frete - x - y - comissao_fixa - tarifa - (preco_custo * quantidade)
    else:
        x = preco_venda_efetivo * (comissao / 100) 
        y = preco_venda_efetivo * (imposto / 100)

        lucro_liquido = preco_venda_efetivo - frete - x - y - 0 - comissao_fixa - tarifa - (preco_custo * quantidade)

    return lucro_liquido

def recomendar_preco_magazine(quantidade, preco_custo, frete, preco_venda, imposto, comissao, desconto=0.0, cashback=0.0):

    tarifa_fixa = 5.0 if preco_venda >= 10 else 0.0

    preco_venda_efetivo = preco_venda
    cashback_valor = 0

    if preco_venda <= 0:
        return -float('inf')

    if desconto > 0:

        cashback_valor = preco_venda * (cashback / 100)
        preco_venda_efetivo = preco_venda * (1 - desconto / 100)
        if preco_venda_efetivo <= 0: return -float('inf')

        x = preco_venda_efetivo * comissao 
        y = preco_venda_efetivo * (imposto / 100) 

        lucro_liquido = preco_venda_efetivo + cashback_valor - frete - x - y - tarifa_fixa - (preco_custo * quantidade)
    else:
        x = preco_venda_efetivo * comissao
        y = preco_venda_efetivo * (imposto / 100)

        lucro_liquido = preco_venda_efetivo - frete - x - y - 0 - tarifa_fixa - (preco_custo * quantidade)

    return lucro_liquido

def recomendar_preco_shopee(quantidade, preco_custo, frete, preco_venda, imposto, desconto=0.0, cashback=0.0):
    comissao = 0.20 
    tarifa_fixa = 4.0

    preco_venda_efetivo = preco_venda
    cashback_valor = 0 


    if preco_venda <= 0:
        return -float('inf')

    if desconto > 0:
       
        preco_venda_efetivo = preco_venda * (1 - desconto / 100)
        if preco_venda_efetivo <= 0: return -float('inf')

        x = preco_venda_efetivo * comissao
        y = preco_venda_efetivo * (imposto / 100)
       
        lucro_liquido = preco_venda_efetivo - frete - x - y - tarifa_fixa - (preco_custo * quantidade)
    else:
        x = preco_venda_efetivo * comissao
        y = preco_venda_efetivo * (imposto / 100)
       
        lucro_liquido = preco_venda_efetivo - frete - x - y - 0 - tarifa_fixa - (preco_custo * quantidade)

    return lucro_liquido
# --- ^ ^ ^ END OF MODIFICATION ^ ^ ^ ---

def recomendar_preco_mercadolivre(quantidade, preco_custo, preco_venda, frete, comissao, imposto, tarifa_fixa_base, desconto=0.0, cashback=0.0):
    
    tarifa_fixa_efetiva = 0 # Default

    
    if preco_venda <= 0:
        return -float('inf')

    
    if tarifa_fixa_base > 0:
         tarifa_fixa_efetiva = tarifa_fixa_base
    else: 
        if preco_venda >= 79:
            tarifa_fixa_efetiva = 0 
        elif preco_venda < 29:
            tarifa_fixa_efetiva = 6.25
        elif 29 <= preco_venda < 50:
            tarifa_fixa_efetiva = 6.50
        elif 50 <= preco_venda < 79:
            tarifa_fixa_efetiva = 6.75

    preco_venda_efetivo = preco_venda
    cashback_valor = 0 

    if desconto > 0:
        
        preco_venda_efetivo = preco_venda * (1 - desconto / 100)
        if preco_venda_efetivo <= 0: return -float('inf')

        x = preco_venda_efetivo * comissao
        y = preco_venda_efetivo * (imposto / 100)
       
        lucro_liquido = preco_venda_efetivo - frete - x - y - tarifa_fixa_efetiva - (preco_custo * quantidade)
    else:
        x = preco_venda_efetivo * comissao
        y = preco_venda_efetivo * (imposto / 100)

        lucro_liquido = preco_venda_efetivo - frete - x - y - 0 - tarifa_fixa_efetiva - (preco_custo * quantidade)

    return lucro_liquido

def recomendar_preco_direta(quantidade, preco_custo, preco_venda, frete, imposto, desconto=0.0, cashback=0.0):

    comissao = 0.0
    tarifa_fixa = 0.0


    preco_venda_efetivo = preco_venda
    cashback_valor = 0 

    if preco_venda <= 0:
        return -float('inf')

    if desconto > 0:
       
        preco_venda_efetivo = preco_venda * (1 - desconto / 100) 
        if preco_venda_efetivo <= 0: return -float('inf')

        x = preco_venda_efetivo * comissao # Will be 0
        y = preco_venda_efetivo * (imposto / 100)
        
        lucro_liquido = preco_venda_efetivo - frete - x - y - tarifa_fixa - (preco_custo * quantidade)
    else:
        x = preco_venda_efetivo * comissao 
        y = preco_venda_efetivo * (imposto / 100)
        lucro_liquido = preco_venda_efetivo - frete - x - y - 0 - tarifa_fixa - (preco_custo * quantidade)

    return lucro_liquido

def calcular_preco_nota_fiscal(quantidade, preco_custo, ipi, bonificacao, bonificacao_porcentagem):

    if quantidade <= 0:
        return 0 

    valor_total_calculado = 0
    valor_total = preco_custo * quantidade
    valor_ipi = valor_total * (ipi / 100)

    if bonificacao > 0:
        valor_total_calculado = valor_total + valor_ipi - bonificacao
    elif bonificacao_porcentagem > 0:
        valor_bonificado = valor_total * (bonificacao_porcentagem / 100)
        valor_total_calculado = valor_total + valor_ipi - valor_bonificado
    else:
        valor_total_calculado = valor_total + valor_ipi

    return valor_total_calculado


def display_detailed_results(results):


    st.markdown("---")
    st.subheader("📊 Resultados do Cálculo")


    preco_venda_inicial = results.get('preco_venda_inicial', 0)
    lucro_liquido_inicial = results.get('lucro_liquido_inicial', 0)
    margem_lucro_percent_inicial = results.get('margem_lucro_percent_inicial', 0)
    preco_com_desconto_inicial = results.get('preco_com_desconto_inicial', preco_venda_inicial) 

    suggested_price = results.get('preco_venda_sugerido', 0)
    lucro_liquido_sugerido = results.get('lucro_liquido_sugerido', 0) 
    margem_lucro_percent_sugerido = results.get('margem_lucro_percent_sugerido', 0) 

    margem_desejada = results.get('margem_lucro_desejado', 0)
    custo_total_produto = results.get('custo_total_produto', 0)
    valor_imposto = results.get('valor_imposto', 0)
    valor_comissao_var = results.get('valor_comissao_var', 0)
    valor_comissao_fixa = results.get('valor_comissao_fixa', 0)
    valor_tarifa = results.get('valor_tarifa', 0)
    valor_frete = results.get('valor_frete', 0)
    desconto_percent = results.get('desconto_percent', 0)
    preco_com_desconto_sugerido = results.get('preco_com_desconto_sugerido', suggested_price) 
    rebate_valor = results.get('rebate_valor', 0) 
    cashback_percent = results.get('cashback_percent', 0)
    cashback_calculado = results.get('cashback_calculado', 0) 

    st.markdown("#### 🏷️ Resultado com Preço Inicial Informado")

    if desconto_percent > 0:
        st.write(f"_Preço Inicial com Desconto ({desconto_percent:.1f}%): R$ {preco_com_desconto_inicial:.2f}_")

    col1_init, col2_init, col3_init = st.columns(3)

    with col1_init:
        st.metric("Preço de Venda Inicial", f"R$ {preco_venda_inicial:.2f}")

    with col2_init:
        st.metric("Lucro Líquido (Inicial)", f"R$ {lucro_liquido_inicial:.2f}")
        color_inicial = "blue" if margem_lucro_percent_inicial >= margem_desejada else "red"
        st.markdown(f":{color_inicial}[Resultado Margem: {'Acima' if color_inicial=='blue' else 'Abaixo'} da meta]")


    with col3_init:

        st.metric("Margem (Inicial)", f"{margem_lucro_percent_inicial:.2f}%",
                  delta=f"{margem_lucro_percent_inicial - margem_desejada:.2f} pts vs Desejada",

                  delta_color="normal"
                 )

    if rebate_valor > 0:
         st.write(f"**_:orange[Valor do Rebate (Input): R$ {rebate_valor:.2f}]_**")
         st.write(f"**_:orange[Lucro Líquido Inicial + Rebate: R$ {(lucro_liquido_inicial + rebate_valor):.2f}]_**")
         st.caption("_Rebate considerado na meta de margem para esta plataforma, se aplicável._")


    st.markdown("---") 

    st.markdown("#### ✨ Resultado com Preço Sugerido")

    col1, col2, col3 = st.columns(3)
    col1.metric("Preço de Venda Sugerido", f"R$ {suggested_price:.2f}",
                f"{((suggested_price - preco_venda_inicial) / preco_venda_inicial * 100) if preco_venda_inicial > 0 else 0:.1f}% vs Inicial" if preco_venda_inicial != suggested_price else None)
    col2.metric("Lucro Líquido (Sugerido)", f"R$ {lucro_liquido_sugerido:.2f}") # Base profit
    col3.metric("Margem de Lucro (Sugerido)", f"{margem_lucro_percent_sugerido:.2f}%", # Margin used for target
                f"{margem_lucro_percent_sugerido - margem_desejada:.2f} pts vs Desejada")

    if rebate_valor > 0:
         st.write(f"**_:orange[Lucro Líquido Sugerido + Rebate: R$ {(lucro_liquido_sugerido + rebate_valor):.2f}]_**")

    st.markdown("---")


    expand_details = margem_lucro_percent_inicial < margem_desejada
    with st.expander("Ver Detalhes do Cálculo (Baseado no Preço Sugerido)", expanded=expand_details):
        st.write(f"**Preço de Venda Base (Sugerido):** R$ {suggested_price:.2f}")
        if desconto_percent > 0:
            st.write(f"**Desconto Aplicado ({desconto_percent:.1f}%):** - R$ {(suggested_price * desconto_percent / 100):.2f}")
            st.write(f"**Preço Efetivo Sugerido (com desconto):** R$ {preco_com_desconto_sugerido:.2f}")
        else:
             st.write(f"**Preço Efetivo Sugerido:** R$ {suggested_price:.2f}")

        st.write(f"**Cashback Oferecido ao Cliente (% input):** {cashback_percent:.1f}%")
        if cashback_calculado > 0:
             st.write(f"**Valor Cashback Calculado (Baseado no Preço Sugerido*):** + R$ {cashback_calculado:.2f}")
             st.caption("*Conforme lógica original, cashback só foi calculado/adicionado se Desconto > 0 em algumas plataformas.")
        else:
             st.write(f"**Valor Cashback Calculado:** R$ 0.00")


        st.markdown("---")
        st.subheader("Custos (Baseado no Preço Sugerido):")
        col_custo1, col_custo2 = st.columns(2)
        with col_custo1:
            st.write(f"**Custo do Produto ({results.get('quantidade', 1)} un.):** - R$ {custo_total_produto:.2f}")
            st.write(f"**Imposto ({results.get('imposto_percent', 0):.1f}%):** - R$ {valor_imposto:.2f}")
            st.write(f"**Comissão Variável ({results.get('comissao_percent', 0)*100:.1f}%):** - R$ {valor_comissao_var:.2f}")

        with col_custo2:
            st.write(f"**Comissão Fixa:** - R$ {valor_comissao_fixa:.2f}")
            st.write(f"**Tarifa Fixa/Peso:** - R$ {valor_tarifa:.2f}")
            st.write(f"**Frete:** - R$ {valor_frete:.2f}")

        st.markdown("---")
        total_custos = custo_total_produto + valor_imposto + valor_comissao_var + valor_comissao_fixa + valor_tarifa + valor_frete
        receita_efetiva_calc = preco_com_desconto_sugerido + cashback_calculado
        lucro_liquido_base_sugerido = lucro_liquido_sugerido

        st.write(f"**Receita Efetiva Sugerida (Preço Sugerido com desc. + Cashback calc.):** R$ {receita_efetiva_calc:.2f}")
        st.write(f"**Total de Custos:** R$ {total_custos:.2f}")
        st.write(f"**Lucro Líquido Calculado (Sugerido, antes de Rebate):** R$ {lucro_liquido_base_sugerido:.2f}") # Use suggested profit
        if rebate_valor > 0:
             st.write(f"**_:orange[+ Rebate Fixo:]_** R$ {rebate_valor:.2f}")
             st.write(f"**_:orange[= Lucro Líquido Final (Sugerido):]_** R$ {(lucro_liquido_base_sugerido + rebate_valor):.2f}")


    st.markdown("---")
    st.subheader("Visualização da Composição do Preço (Baseado no Preço Sugerido)")

    chart_data = {
        'Componente': [
            'Custo Produto', 'Imposto', 'Comissão Var.', 'Comissão Fixa',
            'Tarifa', 'Frete', 'Lucro Líquido (Sugerido, antes Rebate)' 
        ],
        'Valor': [
            max(0, custo_total_produto), max(0, valor_imposto), max(0, valor_comissao_var),
            max(0, valor_comissao_fixa), max(0, valor_tarifa), max(0, valor_frete),
            max(0, lucro_liquido_sugerido) 
        ]
    }
    df_chart = pd.DataFrame(chart_data)
    df_chart = df_chart[df_chart['Valor'] > 0.005] 

    if not df_chart.empty:
        total_chart_value = df_chart['Valor'].sum()
       
        revenue_effective_chart = preco_com_desconto_sugerido + cashback_calculado


        difference = revenue_effective_chart - total_chart_value
        if abs(difference) > 0.01: 

             df_chart['Componente'] = df_chart['Componente'].astype('object')
             new_row = pd.DataFrame([{'Componente': 'Ajuste Arredond.' if difference > 0 else 'Ajuste Negativo', 'Valor': abs(difference)}])
             df_chart = pd.concat([df_chart, new_row], ignore_index=True)


        fig = px.pie(df_chart, values='Valor', names='Componente',
                     title=f"Composição da Receita Efetiva Sugerida (R$ {revenue_effective_chart:.2f})",
                     hole=0.3)
        fig.update_traces(textposition='inside', textinfo='percent+label', hoverinfo='label+percent+value')
        fig.update_layout(showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Não há dados suficientes para gerar o gráfico de composição.")



def handle_amazon():
    st.subheader("Precificador Amazon")
    amazonprec = st.selectbox("Escolha a opção: ", ["Amazon com tarifa(Peso)", "Amazon sem tarifa(Peso)"], key="amazon_option")

    col1, col2 = st.columns(2)
    with col1:
        quantidade = st.number_input("Quantidade:", value=1.0, min_value=1.0, step=1.0, key="amz_qtd")
        preco_custo = st.number_input("Preço de Custo Unitário:", value=1.0, min_value=0.0, step=0.01, format="%.2f", key="amz_custo")
        preco_venda = st.number_input("Preço de Venda Inicial:", value=1.0, min_value=0.01, step=0.01, format="%.2f", key="amz_venda")
        frete = st.number_input("Custo Frete (se aplicável):", min_value=0.0, value=0.0, step=0.01, format="%.2f", key="amz_frete")
        margem_lucro_desejado = st.number_input("Margem de lucro desejada (%): ", min_value=0.0, max_value=100.0, value=10.0, step=0.1, format="%.1f", key="amz_margem")

    with col2:
        imposto = st.number_input("Imposto (%):", value=0.0, min_value=0.0, max_value=100.0, step=0.1, format="%.1f", key="amz_imposto")
        comissao = st.number_input("Comissão (%): ", value=0.0, min_value=0.0, max_value=100.0, step=0.1, format="%.1f", key="amz_comissao_pct")
        comissao_fixa = st.number_input("Comissão Valor Fixo: ", value=0.0, min_value=0.0, step=0.01, format="%.2f", key="amz_comissao_fixa")
        desconto = st.number_input("Desconto (%):", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f", key="amz_desconto")
        cashback = st.number_input("Cashback para Cliente (%):", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f", key="amz_cashback")

    tarifa = 0.0
    if amazonprec == "Amazon com tarifa(Peso)":
        peso_g = st.number_input("Peso (em gramas):", min_value=0.0, value=0.0, step=1.0, key="amz_peso")
        if peso_g <= 100: tarifa = 14.05
        elif peso_g <= 200: tarifa = 14.55
        elif peso_g <= 300: tarifa = 15.05
        elif peso_g <= 400: tarifa = 15.65
        elif peso_g <= 500: tarifa = 16.25
        elif peso_g <= 750: tarifa = 16.85
        elif peso_g <= 1000: tarifa = 17.45
        elif 1000 < peso_g <= 2000: tarifa = 18.50 
        elif 2000 < peso_g <= 5000: tarifa = 22.00 
        else: tarifa = 25.00 + (math.ceil(max(0, peso_g - 5000) / 1000)) * 2.50 
        st.info(f"Tarifa calculada baseada no peso: R$ {tarifa:.2f}")
    else: 
        tarifa = 0.0
        st.info("Tarifa baseada no peso não aplicada para esta opção.")

    if st.button("Calcular Preço Amazon", key="amz_calc_btn"):
        preco_venda_inicial = preco_venda
        rebate = 0 
        def calculate_profit(current_price):
            return recomendar_preco_amazon(
                comissao=comissao, comissao_fixa=comissao_fixa, quantidade=quantidade,
                preco_custo=preco_custo, frete=frete, preco_venda=current_price,
                imposto=imposto, tarifa=tarifa, desconto=desconto, cashback=cashback
            )

        lucro_liquido_inicial = calculate_profit(preco_venda_inicial)
        preco_com_desconto_inicial = preco_venda_inicial * (1 - desconto / 100)

        margem_inicial_calculada = ((lucro_liquido_inicial / preco_com_desconto_inicial) * 100) if preco_com_desconto_inicial > 0 else 0


       
        lucro_liquido = lucro_liquido_inicial 
        margem_atual = margem_inicial_calculada 
        preco_venda = preco_venda_inicial 

        max_iterations = 200000 
        iterations = 0
        step = 0.01 

        if margem_atual < margem_lucro_desejado:
            while margem_atual < margem_lucro_desejado and iterations < max_iterations:
                preco_venda += step
                lucro_liquido = calculate_profit(preco_venda)
                preco_com_desconto_atual = preco_venda * (1 - desconto / 100)
                
                margem_atual = ((lucro_liquido / preco_com_desconto_atual) * 100) if preco_com_desconto_atual > 0 else 0
                iterations += 1
        elif margem_atual > margem_lucro_desejado:

             while margem_atual > margem_lucro_desejado and iterations < max_iterations:
                 preco_venda -= step
                 if preco_venda <= step: 
                     preco_venda = step
                     lucro_liquido = calculate_profit(preco_venda)
                     preco_com_desconto_atual = preco_venda * (1 - desconto / 100)
                     margem_atual = ((lucro_liquido / preco_com_desconto_atual) * 100) if preco_com_desconto_atual > 0 else -float('inf')
                     break 
                 lucro_liquido = calculate_profit(preco_venda)
                 preco_com_desconto_atual = preco_venda * (1 - desconto / 100)
                 margem_atual = ((lucro_liquido / preco_com_desconto_atual) * 100) if preco_com_desconto_atual > 0 else 0
                 iterations += 1
    
             if margem_atual < margem_lucro_desejado and preco_venda > step :
                  preco_venda += step
                  lucro_liquido = calculate_profit(preco_venda)
                  preco_com_desconto_atual = preco_venda * (1 - desconto / 100)
                  margem_atual = ((lucro_liquido / preco_com_desconto_atual) * 100) if preco_com_desconto_atual > 0 else 0


        if iterations >= max_iterations:
            st.warning(f"Não foi possível encontrar o preço ideal em {max_iterations} iterações. O preço/margem pode estar instável ou inatingível.")
    
            preco_venda_sugerido = round(preco_venda, 2)
            lucro_final_sugerido = lucro_liquido
            margem_final_sugerida = margem_atual
            preco_com_desconto_final = preco_com_desconto_atual
        else:

            preco_venda_sugerido = round(preco_venda, 2) 
            lucro_final_sugerido = calculate_profit(preco_venda_sugerido) 
            preco_com_desconto_final = preco_venda_sugerido * (1 - desconto / 100)
            margem_final_sugerida = ((lucro_final_sugerido / preco_com_desconto_final) * 100) if preco_com_desconto_final > 0 else 0

       
        valor_imposto_final = preco_com_desconto_final * (imposto / 100)
        valor_comissao_var_final = preco_com_desconto_final * (comissao / 100)
        custo_total_produto_final = preco_custo * quantidade
        cashback_calculado_final = 0
        if desconto > 0: 
            cashback_calculado_final = preco_venda_sugerido * (cashback / 100)


        results_data = {
            "platform": "Amazon",
            "preco_venda_inicial": preco_venda_inicial,
            "lucro_liquido_inicial": lucro_liquido_inicial,
            "margem_lucro_percent_inicial": margem_inicial_calculada,
            "preco_com_desconto_inicial": preco_com_desconto_inicial,

            "preco_venda_sugerido": preco_venda_sugerido,
            "lucro_liquido_sugerido": lucro_final_sugerido,
            "margem_lucro_percent_sugerido": margem_final_sugerida,

            "margem_lucro_desejado": margem_lucro_desejado,
            "quantidade": quantidade,
            "preco_custo": preco_custo,
            "custo_total_produto": custo_total_produto_final,
            "imposto_percent": imposto,
            "valor_imposto": valor_imposto_final,
            "comissao_percent": comissao / 100, 
            "valor_comissao_var": valor_comissao_var_final,
            "comissao_fixa": comissao_fixa,
            "valor_comissao_fixa": comissao_fixa,
            "tarifa": tarifa, 
            "valor_tarifa": tarifa,
            "frete": frete,
            "valor_frete": frete,
            "desconto_percent": desconto,
            "preco_com_desconto_sugerido": preco_com_desconto_final,
            "cashback_percent": cashback,
            "cashback_calculado": cashback_calculado_final,
            "rebate_valor": rebate 
        }

        display_detailed_results(results_data)


def handle_magazine():
    st.subheader("Precificador Magazine Luiza")
    magazineprec = st.selectbox("Escolha a opção de comissão: ", ['Magazine 12,80%', 'Magazine 18%'], key="magalu_option")
    comissao = 0.1280 if magazineprec == 'Magazine 12,80%' else 0.18

  
    col1, col2 = st.columns(2)
    with col1:
        quantidade = st.number_input("Quantidade:", value=1.0, min_value=1.0, step=1.0, key="mag_qtd")
        preco_custo = st.number_input("Preço de Custo Unitário:", value=1.0, min_value=0.0, step=0.01, format="%.2f", key="mag_custo")
        preco_venda = st.number_input("Preço de Venda Inicial:", value=1.0, min_value=0.01, step=0.01, format="%.2f", key="mag_venda")
        frete = st.number_input("Custo Frete:", min_value=0.0, value=0.0, step=0.01, format="%.2f", key="mag_frete")
        margem_lucro_desejado = st.number_input("Margem de lucro desejada (%): ", min_value=0.0, max_value=100.0, value=12.0, step=0.1, format="%.1f", key="mag_margem")

    with col2:
        imposto = st.number_input("Imposto (%):", value=0.0, min_value=0.0, max_value=100.0, step=0.1, format="%.1f", key="mag_imposto")
        desconto = st.number_input("Desconto (%):", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f", key="mag_desconto")
        cashback = st.number_input("Cashback para Cliente (%):", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f", key="mag_cashback")

        rebate_fixo = st.number_input("Rebate Fixo (Valor R$): ", value=0.0, min_value=0.0, step=0.01, format="%.2f", key="mag_rebate_fixo")
    

    st.info(f"Comissão selecionada: {comissao*100:.2f}%. Tarifa fixa de R$ 5,00 aplicada se preço >= R$ 10,00.")

    if st.button("Calcular Preço Magazine", key="mag_calc_btn"):
        preco_venda_inicial = preco_venda
       

        def calculate_profit(current_price):

            return recomendar_preco_magazine(
                quantidade=quantidade, preco_custo=preco_custo, frete=frete,
                preco_venda=current_price, imposto=imposto, comissao=comissao,
                desconto=desconto, cashback=cashback
            )


        lucro_liquido_inicial = calculate_profit(preco_venda_inicial)
        preco_com_desconto_inicial = preco_venda_inicial * (1 - desconto / 100)

        margem_inicial_calculada = (((lucro_liquido_inicial + rebate_fixo) / preco_com_desconto_inicial) * 100) if preco_com_desconto_inicial > 0 else 0

        lucro_liquido = lucro_liquido_inicial
        margem_atual = margem_inicial_calculada
        preco_venda = preco_venda_inicial

        max_iterations = 200000
        iterations = 0
        step = 0.01

        if margem_atual < margem_lucro_desejado:
             while margem_atual < margem_lucro_desejado and iterations < max_iterations:
                 preco_venda += step
                 lucro_liquido = calculate_profit(preco_venda)
                 preco_com_desconto_atual = preco_venda * (1 - desconto / 100)

                 margem_atual = (((lucro_liquido + rebate_fixo) / preco_com_desconto_atual) * 100) if preco_com_desconto_atual > 0 else 0

                 iterations += 1
        elif margem_atual > margem_lucro_desejado:

             while margem_atual > margem_lucro_desejado and iterations < max_iterations:
                 preco_venda -= step
                 if preco_venda <= step: preco_venda = step; break
                 lucro_liquido = calculate_profit(preco_venda)
                 preco_com_desconto_atual = preco_venda * (1 - desconto / 100)

                 margem_atual = (((lucro_liquido + rebate_fixo) / preco_com_desconto_atual) * 100) if preco_com_desconto_atual > 0 else -float('inf')

                 iterations += 1

             if margem_atual < margem_lucro_desejado and preco_venda > step:
                 preco_venda += step
                 lucro_liquido = calculate_profit(preco_venda)
                 preco_com_desconto_atual = preco_venda * (1 - desconto / 100)

                 margem_atual = (((lucro_liquido + rebate_fixo) / preco_com_desconto_atual) * 100) if preco_com_desconto_atual > 0 else 0
        


        if iterations >= max_iterations:
            st.warning(f"Não foi possível encontrar o preço ideal em {max_iterations} iterações. O preço/margem pode estar instável ou inatingível.")
            preco_venda_sugerido = round(preco_venda, 2)
            lucro_final_sugerido = lucro_liquido
            margem_final_sugerida = margem_atual
            preco_com_desconto_final = preco_com_desconto_atual
        else:

            preco_venda_sugerido = round(preco_venda, 2)
            lucro_final_sugerido = calculate_profit(preco_venda_sugerido)
            preco_com_desconto_final = preco_venda_sugerido * (1 - desconto / 100)

            margem_final_sugerida = (((lucro_final_sugerido + rebate_fixo) / preco_com_desconto_final) * 100) if preco_com_desconto_final > 0 else 0



        tarifa_fixa_final = 5.0 if preco_venda_sugerido >= 10 else 0.0
        valor_imposto_final = preco_com_desconto_final * (imposto / 100)
        valor_comissao_var_final = preco_com_desconto_final * comissao
        custo_total_produto_final = preco_custo * quantidade
        cashback_calculado_final = 0
        if desconto > 0:
            cashback_calculado_final = preco_venda_sugerido * (cashback / 100)

        results_data = {
            "platform": "Magazine Luiza",
            "preco_venda_inicial": preco_venda_inicial,
            "lucro_liquido_inicial": lucro_liquido_inicial,
            "margem_lucro_percent_inicial": margem_inicial_calculada,
            "preco_com_desconto_inicial": preco_com_desconto_inicial,

            "preco_venda_sugerido": preco_venda_sugerido,
            "lucro_liquido_sugerido": lucro_final_sugerido, 
            "margem_lucro_percent_sugerido": margem_final_sugerida,

            "margem_lucro_desejado": margem_lucro_desejado,
            "quantidade": quantidade,
            "preco_custo": preco_custo,
            "custo_total_produto": custo_total_produto_final,
            "imposto_percent": imposto,
            "valor_imposto": valor_imposto_final,
            "comissao_percent": comissao,
            "valor_comissao_var": valor_comissao_var_final,
            "comissao_fixa": 0.0,
            "valor_comissao_fixa": 0.0,
            "tarifa": tarifa_fixa_final,
            "valor_tarifa": tarifa_fixa_final,
            "frete": frete,
            "valor_frete": frete,
            "desconto_percent": desconto,
            "preco_com_desconto_sugerido": preco_com_desconto_final,
            "cashback_percent": cashback,
            "cashback_calculado": cashback_calculado_final,

            "rebate_valor": rebate_fixo

        }

        display_detailed_results(results_data)

def handle_shopee():
    st.subheader("Precificador Shopee")
    comissao = 0.20 
    tarifa_fixa = 4.0
 
    col1, col2 = st.columns(2)
    with col1:
        quantidade = st.number_input("Quantidade:", value=1.0, min_value=1.0, step=1.0, key="shp_qtd")
        preco_custo = st.number_input("Preço de Custo Unitário:", value=1.0, min_value=0.0, step=0.01, format="%.2f", key="shp_custo")
        preco_venda = st.number_input("Preço de Venda Inicial:", value=1.0, min_value=0.01, step=0.01, format="%.2f", key="shp_venda")

        frete = st.number_input("Custo Frete:", min_value=0.0, value=0.0, step=0.01, format="%.2f", key="shp_frete")

        margem_lucro_desejado = st.number_input("Margem de lucro desejada (%): ", min_value=0.0, max_value=100.0, value=12.0, step=0.1, format="%.1f", key="shp_margem")

    with col2:
        imposto = st.number_input("Imposto (%):", value=0.0, min_value=0.0, max_value=100.0, step=0.1, format="%.1f", key="shp_imposto")
        desconto = st.number_input("Desconto (%):", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f", key="shp_desconto")
        cashback = 0 
        rebate = 0   


    st.info(f"Comissão fixa de {comissao*100:.0f}%, Tarifa fixa de R$ {tarifa_fixa:.2f}.")

    if st.button("Calcular Preço Shopee", key="shp_calc_btn"):
        preco_venda_inicial = preco_venda

        def calculate_profit(current_price):
 
            return recomendar_preco_shopee(
                quantidade=quantidade, preco_custo=preco_custo, frete=frete, 
                preco_venda=current_price, imposto=imposto, desconto=desconto

            )


        lucro_liquido_inicial = calculate_profit(preco_venda_inicial)
        preco_com_desconto_inicial = preco_venda_inicial * (1 - desconto / 100)

        margem_inicial_calculada = ((lucro_liquido_inicial / preco_com_desconto_inicial) * 100) if preco_com_desconto_inicial > 0 else 0
   


        lucro_liquido = lucro_liquido_inicial
        margem_atual = margem_inicial_calculada
        preco_venda = preco_venda_inicial

        max_iterations = 200000
        iterations = 0
        step = 0.01

        if margem_atual < margem_lucro_desejado:
            while margem_atual < margem_lucro_desejado and iterations < max_iterations:
                preco_venda += step
                lucro_liquido = calculate_profit(preco_venda)
                preco_com_desconto_atual = preco_venda * (1 - desconto / 100)
          
                margem_atual = ((lucro_liquido / preco_com_desconto_atual) * 100) if preco_com_desconto_atual > 0 else 0
                iterations += 1
        elif margem_atual > margem_lucro_desejado:
  
             while margem_atual > margem_lucro_desejado and iterations < max_iterations:
                 preco_venda -= step
                 if preco_venda <= step: preco_venda = step; break
                 lucro_liquido = calculate_profit(preco_venda)
                 preco_com_desconto_atual = preco_venda * (1 - desconto / 100)
                 margem_atual = ((lucro_liquido / preco_com_desconto_atual) * 100) if preco_com_desconto_atual > 0 else -float('inf')
                 iterations += 1
        
             if margem_atual < margem_lucro_desejado and preco_venda > step:
                 preco_venda += step
                 lucro_liquido = calculate_profit(preco_venda)
                 preco_com_desconto_atual = preco_venda * (1 - desconto / 100)
                 margem_atual = ((lucro_liquido / preco_com_desconto_atual) * 100) if preco_com_desconto_atual > 0 else 0


        if iterations >= max_iterations:
            st.warning(f"Não foi possível encontrar o preço ideal em {max_iterations} iterações. O preço/margem pode estar instável ou inatingível.")
            preco_venda_sugerido = round(preco_venda, 2)
            lucro_final_sugerido = lucro_liquido
            margem_final_sugerida = margem_atual
            preco_com_desconto_final = preco_com_desconto_atual
        else:

            preco_venda_sugerido = round(preco_venda, 2)
            lucro_final_sugerido = calculate_profit(preco_venda_sugerido)
            preco_com_desconto_final = preco_venda_sugerido * (1 - desconto / 100)
            margem_final_sugerida = ((lucro_final_sugerido / preco_com_desconto_final) * 100) if preco_com_desconto_final > 0 else 0


        valor_imposto_final = preco_com_desconto_final * (imposto / 100)
        valor_comissao_var_final = preco_com_desconto_final * comissao
        custo_total_produto_final = preco_custo * quantidade
        cashback_calculado_final = 0 

        results_data = {
            "platform": "Shopee",
            "preco_venda_inicial": preco_venda_inicial,
            "lucro_liquido_inicial": lucro_liquido_inicial,
            "margem_lucro_percent_inicial": margem_inicial_calculada,
            "preco_com_desconto_inicial": preco_com_desconto_inicial,

            "preco_venda_sugerido": preco_venda_sugerido,
            "lucro_liquido_sugerido": lucro_final_sugerido,
            "margem_lucro_percent_sugerido": margem_final_sugerida,

            "margem_lucro_desejado": margem_lucro_desejado,
            "quantidade": quantidade,
            "preco_custo": preco_custo,
            "custo_total_produto": custo_total_produto_final,
            "imposto_percent": imposto,
            "valor_imposto": valor_imposto_final,
            "comissao_percent": comissao,
            "valor_comissao_var": valor_comissao_var_final,
            "comissao_fixa": 0.0,
            "valor_comissao_fixa": 0.0,
            "tarifa": tarifa_fixa,
            "valor_tarifa": tarifa_fixa,
 
            "frete": frete,
            "valor_frete": frete,
         
            "desconto_percent": desconto,
            "preco_com_desconto_sugerido": preco_com_desconto_final,
            "cashback_percent": cashback,
            "cashback_calculado": cashback_calculado_final,
            "rebate_valor": rebate
        }

        display_detailed_results(results_data)

def handle_mercadolivre():
    st.subheader("Precificador Mercado Livre")
    ml_options = {
        "Clássico / Tarifa Padrão": {"comissao": 0.12, "tarifa_base": 0},
        "Clássico / Super Mercado": {"comissao": 0.14, "tarifa_base": 2},
        "Premium / Tarifa Padrão": {"comissao": 0.17, "tarifa_base": 0},
        "Premium / Super Mercado": {"comissao": 0.19, "tarifa_base": 2}
    }

    def format_ml_option(option_key):
        details = ml_options[option_key]
        comissao_pct = details['comissao'] * 100
        tarifa_base = details['tarifa_base']
        tarifa_str = 'Tarifa Fixa Padrão (<R$79)' if tarifa_base == 0 else f'Fixa R$ {tarifa_base:.2f}'
        return f"{option_key} ({comissao_pct:.0f}% + {tarifa_str})"

    mercadolivreprec = st.selectbox(
        "Escolha o tipo de anúncio e tarifa:",
        list(ml_options.keys()),
        format_func=format_ml_option,
        key="ml_option"
    )

    comissao = ml_options[mercadolivreprec]["comissao"]
    tarifa_fixa_base = ml_options[mercadolivreprec]["tarifa_base"]


    col1, col2 = st.columns(2)
    with col1:
        quantidade = st.number_input("Quantidade:", value=1.0, min_value=1.0, step=1.0, key="ml_qtd")
        preco_custo = st.number_input("Preço de Custo Unitário:", value=1.0, min_value=0.0, step=0.01, format="%.2f", key="ml_custo")
        preco_venda = st.number_input("Preço de Venda Inicial:", value=1.0, min_value=0.01, step=0.01, format="%.2f", key="ml_venda")
        frete = st.number_input("Custo Frete (Repassado ou Grátis):", min_value=0.0, value=0.0, step=0.01, format="%.2f", key="ml_frete")
        margem_lucro_desejado = st.number_input("Margem de lucro desejada (%): ", min_value=0.0, max_value=100.0, value=10.0, step=0.1, format="%.1f", key="ml_margem")

    with col2:
        imposto = st.number_input("Imposto (%):", value=0.0, min_value=0.0, max_value=100.0, step=0.1, format="%.1f", key="ml_imposto")
        desconto = st.number_input("Desconto (%):", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f", key="ml_desconto")
        cashback = 0 
        rebate = st.number_input("Rebate (Valor Fixo): ", value=0.0, min_value=0.0, step=0.01, format="%.2f", key="ml_rebate") # Original had this input

    st.warning("A Tarifa Fixa Padrão é aplicada apenas para produtos abaixo de R$ 79,00 (valores: R$6.25 <29, R$6.50 <50, R$6.75 <79). Acima disso (>= R$79), a tarifa fixa padrão é R$ 0, mas considere o custo do frete grátis no campo 'Custo Frete'.")
    st.info(f"Comissão: {comissao*100:.0f}%. {'Tarifa base fixa: R$ {:.2f}'.format(tarifa_fixa_base) if tarifa_fixa_base > 0 else 'Tarifa base: Padrão (calculada abaixo de R$ 79)'}.")


    if st.button("Calcular Preço Mercado Livre", key="ml_calc_btn"):
        preco_venda_inicial = preco_venda

        def calculate_profit(current_price, current_tarifa_base):

            return recomendar_preco_mercadolivre(
                quantidade=quantidade, preco_custo=preco_custo, preco_venda=current_price,
                frete=frete, comissao=comissao, imposto=imposto,
                tarifa_fixa_base=current_tarifa_base, 
                desconto=desconto, cashback=cashback
            )

  
        def get_effective_tariff_value(current_price, base_tariff_type):
            if base_tariff_type > 0: return base_tariff_type 
            else:
                if current_price >= 79: return 0.0
                elif current_price < 29: return 6.25
                elif 29 <= current_price < 50: return 6.50
                elif 50 <= current_price < 79: return 6.75
            return 0.0 

  
        lucro_liquido_inicial = calculate_profit(preco_venda_inicial, tarifa_fixa_base)
        preco_com_desconto_inicial = preco_venda_inicial * (1 - desconto / 100)
 
        margem_inicial_calculada = (((lucro_liquido_inicial + rebate) / preco_com_desconto_inicial) * 100) if preco_com_desconto_inicial > 0 else 0

        lucro_liquido = lucro_liquido_inicial
        margem_atual = margem_inicial_calculada
        preco_venda = preco_venda_inicial

        max_iterations = 200000
        iterations = 0
        step = 0.01

        if margem_atual < margem_lucro_desejado:
             while margem_atual < margem_lucro_desejado and iterations < max_iterations:
                 preco_venda += step
                 
                 lucro_liquido = calculate_profit(preco_venda, tarifa_fixa_base)
                 preco_com_desconto_atual = preco_venda * (1 - desconto / 100)
                
                 margem_atual = (((lucro_liquido + rebate) / preco_com_desconto_atual) * 100) if preco_com_desconto_atual > 0 else 0
                 iterations += 1
        elif margem_atual > margem_lucro_desejado:

             while margem_atual > margem_lucro_desejado and iterations < max_iterations:
                 preco_venda -= step
                 if preco_venda <= step: preco_venda = step; break
                 lucro_liquido = calculate_profit(preco_venda, tarifa_fixa_base)
                 preco_com_desconto_atual = preco_venda * (1 - desconto / 100)
                 margem_atual = (((lucro_liquido + rebate) / preco_com_desconto_atual) * 100) if preco_com_desconto_atual > 0 else -float('inf')
                 iterations += 1

             if margem_atual < margem_lucro_desejado and preco_venda > step:
                 preco_venda += step
                 lucro_liquido = calculate_profit(preco_venda, tarifa_fixa_base)
                 preco_com_desconto_atual = preco_venda * (1 - desconto / 100)
                 margem_atual = (((lucro_liquido + rebate) / preco_com_desconto_atual) * 100) if preco_com_desconto_atual > 0 else 0


        if iterations >= max_iterations:
            st.warning(f"Não foi possível encontrar o preço ideal em {max_iterations} iterações. O preço/margem pode estar instável ou inatingível.")
            preco_venda_sugerido = round(preco_venda, 2)
            lucro_final_sugerido = lucro_liquido
            margem_final_sugerida = margem_atual
            preco_com_desconto_final = preco_com_desconto_atual
        else:
     
            preco_venda_sugerido = round(preco_venda, 2)
     
            lucro_final_sugerido = calculate_profit(preco_venda_sugerido, tarifa_fixa_base)
            preco_com_desconto_final = preco_venda_sugerido * (1 - desconto / 100)

            margem_final_sugerida = (((lucro_final_sugerido + rebate) / preco_com_desconto_final) * 100) if preco_com_desconto_final > 0 else 0


        tarifa_fixa_efetiva_final_valor = get_effective_tariff_value(preco_venda_sugerido, tarifa_fixa_base)

        valor_imposto_final = preco_com_desconto_final * (imposto / 100)
        valor_comissao_var_final = preco_com_desconto_final * comissao
        custo_total_produto_final = preco_custo * quantidade
        cashback_calculado_final = 0 

        results_data = {
            "platform": "Mercado Livre",
            "preco_venda_inicial": preco_venda_inicial,
            "lucro_liquido_inicial": lucro_liquido_inicial,
            "margem_lucro_percent_inicial": margem_inicial_calculada,
            "preco_com_desconto_inicial": preco_com_desconto_inicial,

            "preco_venda_sugerido": preco_venda_sugerido,
            "lucro_liquido_sugerido": lucro_final_sugerido, 
            "margem_lucro_percent_sugerido": margem_final_sugerida, 

            "margem_lucro_desejado": margem_lucro_desejado,
            "quantidade": quantidade,
            "preco_custo": preco_custo,
            "custo_total_produto": custo_total_produto_final,
            "imposto_percent": imposto,
            "valor_imposto": valor_imposto_final,
            "comissao_percent": comissao,
            "valor_comissao_var": valor_comissao_var_final,
            "comissao_fixa": 0.0,
            "valor_comissao_fixa": 0.0,
            "tarifa": tarifa_fixa_efetiva_final_valor, 
            "valor_tarifa": tarifa_fixa_efetiva_final_valor,
            "frete": frete,
            "valor_frete": frete,
            "desconto_percent": desconto,
            "preco_com_desconto_sugerido": preco_com_desconto_final,
            "cashback_percent": cashback,
            "cashback_calculado": cashback_calculado_final,
            "rebate_valor": rebate 
        }

        display_detailed_results(results_data)

def handle_venda_direta():
    st.subheader("Precificador Venda Direta")

    
    col1, col2 = st.columns(2)
    with col1:
        quantidade = st.number_input("Quantidade:", value=1.0, min_value=1.0, step=1.0, key="vd_qtd")
        preco_custo = st.number_input("Preço de Custo Unitário:", value=1.0, min_value=0.0, step=0.01, format="%.2f", key="vd_custo")
        preco_venda = st.number_input("Preço de Venda Inicial:", value=1.0, min_value=0.01, step=0.01, format="%.2f", key="vd_venda")
        frete = st.number_input("Custo Frete:", min_value=0.0, value=0.0, step=0.01, format="%.2f", key="vd_frete")

    with col2:
        imposto = st.number_input("Imposto (%):", value=0.0, min_value=0.0, max_value=100.0, step=0.1, format="%.1f", key="vd_imposto")
        margem_lucro_desejado = st.number_input("Margem de lucro desejada (%): ", min_value=0.0, max_value=100.0, value=12.0, step=0.1, format="%.1f", key="vd_margem")
        desconto = 0 
        cashback = 0
        rebate = 0

    st.info("Cálculo simplificado para venda direta (sem comissões ou tarifas de marketplace).")

    if st.button("Calcular Preço Venda Direta", key="vd_calc_btn"):
        preco_venda_inicial = preco_venda

        def calculate_profit(current_price):
            return recomendar_preco_direta(
                quantidade=quantidade, preco_custo=preco_custo, preco_venda=current_price,
                frete=frete, imposto=imposto, desconto=desconto, cashback=cashback
            )

        
        lucro_liquido_inicial = calculate_profit(preco_venda_inicial)
        preco_com_desconto_inicial = preco_venda_inicial 
        
        margem_inicial_calculada = ((lucro_liquido_inicial / preco_com_desconto_inicial) * 100) if preco_com_desconto_inicial > 0 else 0
       
        lucro_liquido = lucro_liquido_inicial
        margem_atual = margem_inicial_calculada
        preco_venda = preco_venda_inicial

        max_iterations = 200000
        iterations = 0
        step = 0.01

        if margem_atual < margem_lucro_desejado:
             while margem_atual < margem_lucro_desejado and iterations < max_iterations:
                 preco_venda += step
                 lucro_liquido = calculate_profit(preco_venda)
                 preco_com_desconto_atual = preco_venda 
                 margem_atual = ((lucro_liquido / preco_com_desconto_atual) * 100) if preco_com_desconto_atual > 0 else 0
                 iterations += 1
        elif margem_atual > margem_lucro_desejado:
         
             while margem_atual > margem_lucro_desejado and iterations < max_iterations:
                 preco_venda -= step
                 if preco_venda <= step: preco_venda = step; break
                 lucro_liquido = calculate_profit(preco_venda)
                 preco_com_desconto_atual = preco_venda
                 margem_atual = ((lucro_liquido / preco_com_desconto_atual) * 100) if preco_com_desconto_atual > 0 else -float('inf')
                 iterations += 1
           
             if margem_atual < margem_lucro_desejado and preco_venda > step:
                 preco_venda += step
                 lucro_liquido = calculate_profit(preco_venda)
                 preco_com_desconto_atual = preco_venda
                 margem_atual = ((lucro_liquido / preco_com_desconto_atual) * 100) if preco_com_desconto_atual > 0 else 0

        if iterations >= max_iterations:
            st.warning(f"Não foi possível encontrar o preço ideal em {max_iterations} iterações. O preço/margem pode estar instável ou inatingível.")
            preco_venda_sugerido = round(preco_venda, 2)
            lucro_final_sugerido = lucro_liquido
            margem_final_sugerida = margem_atual
            preco_com_desconto_final = preco_com_desconto_atual
        else:
        
            preco_venda_sugerido = round(preco_venda, 2)
            lucro_final_sugerido = calculate_profit(preco_venda_sugerido)
            preco_com_desconto_final = preco_venda_sugerido 
            margem_final_sugerida = ((lucro_final_sugerido / preco_com_desconto_final) * 100) if preco_com_desconto_final > 0 else 0


        valor_imposto_final = preco_com_desconto_final * (imposto / 100)
        custo_total_produto_final = preco_custo * quantidade

        results_data = {
            "platform": "Venda Direta",
            "preco_venda_inicial": preco_venda_inicial,
            "lucro_liquido_inicial": lucro_liquido_inicial,
            "margem_lucro_percent_inicial": margem_inicial_calculada,
            "preco_com_desconto_inicial": preco_com_desconto_inicial,

            "preco_venda_sugerido": preco_venda_sugerido,
            "lucro_liquido_sugerido": lucro_final_sugerido,
            "margem_lucro_percent_sugerido": margem_final_sugerida,

            "margem_lucro_desejado": margem_lucro_desejado,
            "quantidade": quantidade,
            "preco_custo": preco_custo,
            "custo_total_produto": custo_total_produto_final,
            "imposto_percent": imposto,
            "valor_imposto": valor_imposto_final,
            "comissao_percent": 0.0,
            "valor_comissao_var": 0.0,
            "comissao_fixa": 0.0,
            "valor_comissao_fixa": 0.0,
            "tarifa": 0.0,
            "valor_tarifa": 0.0,
            "frete": frete,
            "valor_frete": frete,
            "desconto_percent": desconto,
            "preco_com_desconto_sugerido": preco_com_desconto_final,
            "cashback_percent": cashback,
            "cashback_calculado": 0,
            "rebate_valor": rebate
        }

        display_detailed_results(results_data)


def handle_nota_fiscal():
    st.subheader("Calculadora de Custo de Nota Fiscal")

    col1, col2 = st.columns(2)
    with col1:
        quantidade = st.number_input("Quantidade Comprada:", value=1, min_value=1, step=1, key="nf_qtd")
     
        preco_custo = st.number_input("Preço de Custo Unitário (NF):", value=0.0000, min_value=0.0, format="%.4f", step=0.0001, key="nf_custo")
        ipi = st.number_input("IPI (%):", value=0.0, min_value=0.0, format="%.3f", step=0.001, key="nf_ipi")

    with col2:
        bonificacao = st.number_input("Bonificação (Valor Total R$):", value=0.0, min_value=0.0, format="%.2f", key="nf_bon_valor")
        bonificacao_porcentagem = st.number_input("Bonificação (% sobre Valor Total Produtos):", value=0.0, min_value=0.0, format="%.2f", key="nf_bon_pct")

    if st.button("Calcular Custo NF", key="nf_calc_btn"):
        if quantidade <= 0:
             st.error("A quantidade deve ser maior que zero.")
             return 

        if bonificacao > 0 and bonificacao_porcentagem > 0:
            st.warning("Informe a bonificação OU em valor OU em porcentagem, não ambos. Usando apenas o valor informado.")
            bonificacao_porcentagem = 0 

        resultado_total = calcular_preco_nota_fiscal(
            quantidade=quantidade, preco_custo=preco_custo, ipi=ipi,
            bonificacao=bonificacao, bonificacao_porcentagem=bonificacao_porcentagem
        )

        custo_unitario_final = resultado_total / quantidade if quantidade > 0 else 0

        st.markdown("---")
        st.subheader("Resultados do Cálculo da Nota Fiscal")

        valor_total_sem_ipi = preco_custo * quantidade
        valor_ipi_calc = valor_total_sem_ipi * (ipi / 100)
        valor_bonificacao_calc = 0
        if bonificacao > 0:
            valor_bonificacao_calc = bonificacao
        elif bonificacao_porcentagem > 0:
             valor_bonificacao_calc = valor_total_sem_ipi * (bonificacao_porcentagem / 100)


        st.metric("Valor Total Produtos (NF)", f"R$ {valor_total_sem_ipi:.4f}")
        st.metric("Valor IPI Calculado", f"+ R$ {valor_ipi_calc:.4f}")
        if valor_bonificacao_calc > 0:
            st.metric("Valor da Bonificação Aplicada", f"- R$ {valor_bonificacao_calc:.2f}") 
        st.metric("Valor Total Final Calculado (NF)", f"R$ {resultado_total:.4f}", delta_color="inverse")
        st.metric("Custo Unitário Final Efetivo", f"R$ {custo_unitario_final:.4f}") 


        st.markdown("---")
        st.write("Detalhamento:")
        data = {
             'Componente': ['Valor Produtos (Qtd x Custo Unit.)', 'Valor IPI', 'Bonificação Aplicada', 'Valor Final'],
             'Valor (R$)': [f"{valor_total_sem_ipi:.4f}", f"+ {valor_ipi_calc:.4f}", f"- {valor_bonificacao_calc:.2f}", f"= {resultado_total:.4f}"]
         }
        st.table(pd.DataFrame(data))




st.set_page_config(layout="wide") 


with st.sidebar:
    selected = option_menu(
        "Menu Principal",
        ["Precificador", "Frete Magazine", "IA"],
        icons=['calculator-fill', 'truck', 'robot'],
        menu_icon="list",
        default_index=0 
    )

if selected == "Precificador":
    st.title("📈 Precificador Inteligente")
    st.caption("Calcule o preço de venda ideal para diversas plataformas.")


    plataforma = st.selectbox(
        "Escolha a Plataforma:",
        ["Amazon", "Magazine Luiza", "Shopee", "Mercado Livre", "Venda Direta", "Nota Fiscal"] 
    )

    platform_handlers = {
        "Amazon": handle_amazon,
        "Magazine Luiza": handle_magazine,
        "Shopee": handle_shopee,
        "Mercado Livre": handle_mercadolivre,
        "Venda Direta": handle_venda_direta,
        "Nota Fiscal": handle_nota_fiscal
    }


    if plataforma in platform_handlers:
        platform_handlers[plataforma]()
    else:
        st.error("Plataforma selecionada não é válida.")

elif selected == "IA":

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if texto := st.chat_input("Diga alguma coisa"):
      
        st.session_state.chat_history.append({"role": "user", "content": texto})

        ai_google = AIGoogle(prompt_user='''
                              Você é um assistente especialista, você deve instruir ao usuário como usar o precificador do site
                             innovamed.streamlit.app, 

                             O criador é José Pádua, o github é: https://github.com/josegabrielpadua,

                             Se o usuário perguntar sobre quem é José Gabriel ou José Pádua, você deve falar baseado nisso:

                             José Gabriel é estudante do 7º semestre de Engenharia de Software, com perfil analítico. 

                             Ao da formação, ele vem desenvolvendo projetos com foco em análise de dados, utilizando ferramentas como Python, MySQL, Git /Github e bibliotecas especializadas como Pandas, NumPy, Matplotlib, Plotly e Scikit-learn, com conhecimentos aplicados em machine learning.

                             Você deve informar também que essa inteligência artificial, que no caso é você, foi pré-programada por mim: José Pádua. 


                             você não deve ajudar o usuário em hipótese alguma dando os resultados das contas. Mas deve instruir como funciona
                             as taxas, fretes, comissões dos marketplaces, e até mostrar como é feito os cálculos. 

                             Mercado Livre:

                             Se o preço de venda for maior ou igual a R$ 79,00, então a tarifa fixa será igual a 0.
                             Se o preço de venda for menor do que R$ 29,00, então a tarifa fixa será R$ 6,25.
                             Se o preço de venda for maior ou igual a R$ 29 e menor do que R$ 50,00, então a tarifa fixa é igual a R$ 6,50.
                             Se o preço de venda for maior ou igual a R$ 50,00 e menor do que R$ 79,00, então a tarifa fixa é igual a R$ 6,75.

                            a comissão dos anúncios clássicos são 12% e dos anúncios premium são 17%. 
                            
                            Já dos anúncios de super mercado é bem variado, conselhe sempre o usuário para que consulte sempre no próprio marketplace.
                            
                            O frete é cobrado quando o preço de venda é maior do que R$ 79,00. Geralmente é R$ 24,95 em média, mas varia de produto a produto, e de caso a caso. 
                             Sempre conselhe o usuário da média de frete, e sempre lembre de conselhar de consultar no próprio anúncio o valor que irá ficar o frete de envio.

                            
                            Shopee:
                             
                            A comissão é um valor aplicado em todas as vendas realizadas na Shopee. Esse montante é utilizado para manter e aprimorar os serviços e benefícios oferecidos pela plataforma, tanto para compradores quanto para vendedores.



                            A comissão é cobrada exclusivamente sobre o valor do produto vendido, desconsiderando o valor do frete, que é arcado pelo comprador ou pela Shopee (quando se utiliza o cupom de frete). Veja a seguir:

                            Para vendedores que não fazem parte do Programa de Frete Grátis: 12,5% de comissão padrão + 1,5% de taxa de transação + R$4 por item vendido;
                            Para vendedores que fazem parte do Programa de Frete Grátis: 12,5% de comissão padrão + 1,5% de taxa de transação + 6% de Taxa de Transporte + R$4 por item vendido.
                                                         
                             Caso o usuário pergunte sobre uma taxa de alguma plataforma, você deverá somente responder sobre mercado livre, shopee e magalu
                             que são as informações que você estará atualizado, essa sua base de conhecimento terá embasamento nessa data atual de 05/2025. 
                             
                            Magalu:
                             
                            A comissão dos pedidos vendidos no Magalu Marketplace segue o modelo das tabelas abaixo:

                            Tabela de comissão – Modelo no fluxo (parcelado):

                            

                            Categoria	Comissão
                            Moda e Acessórios	18%
                            Demais categorias	14,80%
                            

                            Tabela de comissão – Modelo antecipado:

                            

                            Categoria	Comissão
                            Moda e Acessórios	20%
                            Demais categorias	18%
                            

                            Além disso, todos os pedidos acima de R$10 contam com um custo fixo de R$5,00, que irá se somar ao valor da comissão. 

                            Veja como funciona: 

                            Pedido com 1 produto <R$79,00	Pedido com 1 ou mais produtos >R$79,00
                            Coparticipação ZERO
                            +
                            Custo fixo por pedido R$5,00

                            Coparticipação aplicada
                            +Custo fixo por pedido R$5,00
                             
                            Sobre Frete:
                            
                            DESPACHO NO PRAZO (Nova Tabela Coparticipação)
                            Faixa Peso	<92% (0% DE DESCONTO)	ENTRE 92 e 97% (25% DE DESCONTO)	>97% (50% DE DESCONTO)	FULFILLMENT (75% DE DESCONTO)
                            Até 500gr	R$ 35,90	R$ 26,93	R$ 17,95	R$ 8,98
                            De 500gr a 1kg	R$ 40,90	R$ 30,68	R$ 20,45	R$ 10,23
                            De 1kg a 2kg	R$ 42,90	R$ 32,18	R$ 21,45	R$ 10,73
                            De 2kg a 5kg	R$ 50,90	R$ 38,18	R$ 25,45	R$ 12,73
                            De 5kg a 9kg	R$ 77,90	R$ 58,43	R$ 38,95	R$ 19,48
                            De 9kg a 13kg	R$ 98,90	R$ 74,18	R$ 49,45	R$ 24,73
                            De 13kg a 17kg	R$ 111,90	R$ 83,93	R$ 55,95	R$ 27,98
                            De 17kg a 23kg	R$ 134,90	R$ 101,18	R$ 67,45	R$ 33,73
                            De 23kg a 30kg	R$ 148,90	R$ 111,68	R$ 74,45	R$ 37,23
                            De 30kg a 40kg	R$ 159,90	R$ 119,93	R$ 79,95	R$ 39,98
                            De 40kg a 50kg	R$ 189,90	R$ 142,43	R$ 94,95	R$ 47,48
                            De 50kg a 60kg	R$ 197,90	R$ 148,43	R$ 98,95	R$ 49,48
                            De 60kg a 70kg	R$ 206,90	R$ 155,18	R$ 103,45	R$ 51,73
                            De 70kg a 80kg	R$ 215,90	R$ 161,93	R$ 107,95	R$ 53,98
                            De 80kg a 90kg	R$ 225,90	R$ 169,43	R$ 112,95	R$ 56,48
                            De 90kg a 100kg	R$ 235,90	R$ 176,93	R$ 117,95	R$ 58,98
                            De 100kg a 110kg	R$ 245,90	R$ 184,43	R$ 122,95	R$ 61,48
                            De 110kg a 120kg	R$ 256,90	R$ 192,68	R$ 128,45	R$ 64,23
                            De 120kg a 130kg	R$ 267,90	R$ 200,93	R$ 133,95	R$ 66,98
                            De 130kg a 140kg	R$ 279,90	R$ 209,93	R$ 139,95	R$ 69,98
                            De 140kg a 150kg	R$ 289,90	R$ 217,43	R$ 144,95	R$ 72,48
                            De 150kg a 160kg	R$ 304,90	R$ 228,68	R$ 152,45	R$ 76,23
                            De 160kg a 170kg	R$ 317,90	R$ 238,43	R$ 158,95	R$ 79,48
                            De 170kg a 180kg	R$ 334,90	R$ 251,18	R$ 167,45	R$ 82,98
                            De 180kg a 190kg	R$ 345,90	R$ 259,43	R$ 172,95	R$ 86,48
                            De 190kg a 200kg	R$ 360,90	R$ 270,68	R$ 180,45	R$ 90,23
                            Acima de 200kg	R$ 375,90	R$ 281,93	R$ 187,95	R$ 93,98
                            
                            Existem as faixas de 0%, 25% e 50% de desconto no frete.
 

                            🔹Quando o seu indicador “Despacho no Prazo” está menor que 92%, seguindo a nova Política de Frete, você não terá nenhum desconto e arcará com 100% do custo do frete.

                            🔹Se o seu indicador “Despacho no Prazo” estiver entre 92% e 97%, você terá 25% de desconto e arcará com 75% do custo do frete.

                            🔹Se o seu indicador “Despacho no Prazo” ultrapassar 97%, você terá 50% de desconto e arcará com 50% do custo do frete.
                            
                            Se o usuário perguntar sobre como funciona os cálculos, você deve instruir assim:
                            
                            resultado com a comissão subtraída = preço de venda - comissão% 
                            lucro líquido = resultado com a comissão subtraída - tarifa fixa - frete - custo do produto
                            margem de lucro = (lucro líquido / preço de venda) * 100
                             
                            Se o usuário perguntar sobre a aba Precificador você deve dizer a ele que na aba precificação, existem as opções:
                            Amazon, Mercado Livre, Shopee, Magazine Luíza, Venda Direta, Nota Fiscal. 
                             
                            Se o usuário perguntar sobre as taxas da Amazon, você deve informar a ele que está desatualizado a base de dados, e que é melhor o usuário consultar isso por fora, de forma educada.
                             
                            Se o usuário perguntar da Amazon, Mercado Livre, Shopee e Magazine Luíza, você deve instruir que é um precificador desses marketplaces, já contendo as tarifas, comissões, 
                            as regras incluídas por padrão. Mas, que tem campos que o usuário deve colocar manualmente, como por exemplo: rebate, fretes e taxas adicionais que tiver. 
                            
                            Se o usuário perguntar sobre Nota Fiscal:
                            
                            Você deve informar que é um campo para facilitar no cálculo de produtos que vem na nota que possuem IPI e bonificações na nota. Dando de maneira assertiva o custo do produto contendo
                            essas variavéis informadas pelo o usuário.
                            
                            Se o usuário perguntar sobre Venda direta:
                             
                            Você deve informar que é um campo para fazer calculos sem conter nenhuma tarifa fixa ou comissão embutida no cálculo. 
                            
                            Se o usuário perguntar sobre a aba Frete Magazine, você deve informar ao usuário que é uma aba onde é possível dar upload em um arquivo excel, onde antigamente o usuário baixava a planilha dos produtos e podia dar upload na planilha nessa aba,
                            o usuário escolhia qual era a reputação dele no marketplace e ele calculava os fretes de cada produto baseado em um cálculo de tamanho e peso que tinha antigamente na plataforma. Atualmente está desatualizado, por isso não é funcional por agora. 
    
                             ''',
        response=f'{texto}')

        response = ai_google.interaction()

        st.session_state.chat_history.append({"role": "assistant", "content": response.content})

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])



elif selected == "Frete Magazine":

    st.title("🚚 Calculadora de Frete - Magazine Luiza")
    st.caption("Estime o custo de frete com base na sua reputação e dados do produto.")


    with st.sidebar:
        st.markdown("---") 
        options = st.radio(
            "**Sua Reputação no Magalu**",
            ["< 92% (sem desconto)",
             "Entre 92% e 97% (desconto 25%)",
             ">= 97% (desconto 50%)",
             "Líder/Outros (desconto 75%)"],
            index=None, 
            key="reputacao_radio",
            help="Selecione o nível de reputação para aplicar o desconto de frete correto."
        )


    reputacao_valor = None
    if options == "< 92% (sem desconto)":
        reputacao_valor = 0.91 
    elif options == "Entre 92% e 97% (desconto 25%)":
        reputacao_valor = 0.93 
    elif options == ">= 97% (desconto 50%)":
        reputacao_valor = 0.99 
    elif options == "Líder/Outros (desconto 75%)":
         reputacao_valor = 99.9


    uploaded_files = st.file_uploader(
        "Importe a(s) planilha(s) de produtos do Magalu (.xlsx)",
        accept_multiple_files=True,
        type=['xlsx'],
        help="Faça upload dos arquivos Excel exportados do Magalu contendo as abas 'PRODUTO' e 'PREÇO'."
        )

    if not uploaded_files:
        st.info("Aguardando upload da planilha de produtos Magalu...")

    if uploaded_files and reputacao_valor is None:
        st.warning("Por favor, **selecione sua reputação** na barra lateral para calcular o frete.")

    all_results_df = pd.DataFrame() 
    calculation_attempted = False 


    if uploaded_files and reputacao_valor is not None:
        calculation_attempted = True 
        for uploaded_file in uploaded_files:
            try:
                st.write(f"**Processando arquivo:** `{uploaded_file.name}`")

                xls = pd.ExcelFile(uploaded_file, engine='openpyxl')

       
                required_sheets = ['PRODUTO', 'PREÇO']
                missing_sheets = [sheet for sheet in required_sheets if sheet not in xls.sheet_names]
                if missing_sheets:
                     st.error(f"Arquivo '{uploaded_file.name}' não contém a(s) aba(s) necessária(s): {', '.join(missing_sheets)}. Pulando este arquivo.")
                     continue

                df_magazine_produto = pd.read_excel(xls, skiprows=2, sheet_name='PRODUTO')
                df_magazine_preco = pd.read_excel(xls, sheet_name='PREÇO', skiprows=2)


                if 'SKU' not in df_magazine_produto.columns or 'SKU' not in df_magazine_preco.columns:
                    st.error(f"Coluna 'SKU' não encontrada em uma das abas do arquivo '{uploaded_file.name}'. Pulando este arquivo.")
                    continue
                df_magazine_produto['SKU'] = df_magazine_produto['SKU'].astype(str).str.strip()
                df_magazine_preco['SKU'] = df_magazine_preco['SKU'].astype(str).str.strip()


                df_joined = pd.merge(df_magazine_produto, df_magazine_preco, on='SKU', how='inner', suffixes=('_prod', '_preco'))


                status_col = 'Status do Produto'
                if status_col not in df_joined.columns:
                     st.warning(f"Coluna '{status_col}' não encontrada no arquivo '{uploaded_file.name}'. Não foi possível filtrar por produtos publicados.")
                else:

                    df_joined[status_col] = df_joined[status_col].astype(str).fillna('').str.lower()
                    df_joined = df_joined[df_joined[status_col] == 'publicado']


                if df_joined.empty:
                    st.warning(f"Nenhum produto 'Publicado' com SKU correspondente encontrado no arquivo '{uploaded_file.name}'.")
                    continue


                required_cols_map = {
                    'SKU': 'SKU',
                    'TITULO': 'TITULO',
                    'Preço POR': 'Preço POR', 
                    'COMPRIMENTO': 'COMPRIMENTO', 
                    'LARGURA': 'LARGURA', 
                    'ALTURA': 'ALTURA' 
                }
                missing_cols = [col for col in required_cols_map.keys() if col not in df_joined.columns]
                if missing_cols:
                     st.error(f"Arquivo '{uploaded_file.name}' não contém as colunas necessárias: {', '.join(missing_cols)}. Pulando este arquivo.")
                     continue


                df_filtered = df_joined[list(required_cols_map.keys())].copy() 

 
                df_filtered["Custo Frete Estimado"] = df_filtered.apply(
                    lambda row: calcular_custo_frete(row=row, reputacao=reputacao_valor),
                    axis=1
                )

            
                df_filtered["Custo Frete Estimado"] = pd.to_numeric(df_filtered["Custo Frete Estimado"], errors='coerce')

                all_results_df = pd.concat([all_results_df, df_filtered], ignore_index=True)

            except Exception as e:
                st.error(f"Erro inesperado ao processar o arquivo '{uploaded_file.name}'. Verifique o formato do arquivo.")
                st.exception(e) 


    if not all_results_df.empty:
        st.markdown("---")
        st.subheader("Resultados do Cálculo de Frete")

        df_display = all_results_df.copy()

        df_display['Custo Frete Estimado'] = df_display['Custo Frete Estimado'].apply(lambda x: f"R$ {x:.2f}" if pd.notna(x) else "Erro/Dados Inválidos")

        df_display = df_display.fillna("Dado Ausente")

        st.dataframe(df_display, use_container_width=True)


        df_download = all_results_df.copy()

        df_download.fillna({'Custo Frete Estimado': -1}, inplace=True) 

        df_download = df_download.fillna("Dado Ausente")


        df_xlsx = to_excel(df_download)
        st.download_button(
            label='📥 Baixar Planilha de Fretes Estimados',
            data=df_xlsx,
            file_name='frete_magalu_estimado.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    elif calculation_attempted: 
         st.info("Nenhum produto válido encontrado nos arquivos processados para cálculo de frete.")


    elif uploaded_files and reputacao_valor is None:
        st.info("Selecione sua reputação na barra lateral para processar os arquivos e calcular o frete.")