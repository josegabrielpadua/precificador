"""
Página 'Precificador' — handlers de UI para cada plataforma de venda.
"""
import streamlit as st

from calculators import amazon, magazine, shopee, mercadolivre, venda_direta, nota_fiscal
from widgets.results import exibir_resultados
from utils.preco_otimizador import encontrar_preco_otimo


# ─────────────────────────────────────────────────────────────────────────────
# Helpers internos
# ─────────────────────────────────────────────────────────────────────────────

def _margem_com_desconto(lucro: float, preco: float, desconto: float, rebate: float = 0.0) -> float:
    preco_efetivo = preco * (1 - desconto / 100)
    return ((lucro + rebate) / preco_efetivo * 100) if preco_efetivo > 0 else 0.0


def _margem_sem_desconto(lucro: float, preco: float, rebate: float = 0.0) -> float:
    return ((lucro + rebate) / preco * 100) if preco > 0 else 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Amazon
# ─────────────────────────────────────────────────────────────────────────────

def handle_amazon() -> None:
    st.subheader("Precificador Amazon")

    opcao = st.selectbox(
        "Escolha a opção:",
        ["Amazon com tarifa (Peso)", "Amazon sem tarifa (Peso)"],
        key="amazon_option",
    )

    col1, col2 = st.columns(2)
    with col1:
        quantidade           = st.number_input("Quantidade:", value=1.0, min_value=1.0, step=1.0, key="amz_qtd")
        preco_custo          = st.number_input("Preço de Custo Unitário:", value=1.0, min_value=0.0, step=0.01, format="%.2f", key="amz_custo")
        preco_venda          = st.number_input("Preço de Venda Inicial:", value=1.0, min_value=0.01, step=0.01, format="%.2f", key="amz_venda")
        frete                = st.number_input("Custo Frete (se aplicável):", min_value=0.0, value=0.0, step=0.01, format="%.2f", key="amz_frete")
        margem_lucro_desejado = st.number_input("Margem de lucro desejada (%):", min_value=0.0, max_value=100.0, value=10.0, step=0.1, format="%.1f", key="amz_margem")

    with col2:
        imposto       = st.number_input("Imposto (%):", value=0.0, min_value=0.0, max_value=100.0, step=0.1, format="%.1f", key="amz_imposto")
        comissao      = st.number_input("Comissão (%):", value=0.0, min_value=0.0, max_value=100.0, step=0.1, format="%.1f", key="amz_comissao_pct")
        comissao_fixa = st.number_input("Comissão Valor Fixo:", value=0.0, min_value=0.0, step=0.01, format="%.2f", key="amz_comissao_fixa")
        desconto      = st.number_input("Desconto (%):", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f", key="amz_desconto")
        cashback      = st.number_input("Rebate da Plataforma (%):", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f", key="amz_cashback")

    tarifa = 0.0
    if opcao == "Amazon com tarifa (Peso)":
        peso_g = st.number_input("Peso (em gramas):", min_value=0.0, value=0.0, step=1.0, key="amz_peso")
        tarifa = amazon.calcular_tarifa_peso(peso_g)
        st.info(f"Tarifa calculada baseada no peso: R$ {tarifa:.2f}")
    else:
        st.info("Tarifa baseada no peso não aplicada para esta opção.")

    if not st.button("Calcular Preço Amazon", key="amz_calc_btn"):
        return

    def calcular_lucro(preco: float) -> float:
        return amazon.calcular_lucro(
            comissao=comissao, comissao_fixa=comissao_fixa, quantidade=quantidade,
            preco_custo=preco_custo, frete=frete, preco_venda=preco,
            imposto=imposto, tarifa=tarifa, desconto=desconto, cashback=cashback,
        )

    def calcular_margem(lucro: float, preco: float) -> float:
        return _margem_com_desconto(lucro, preco, desconto)

    preco_venda_inicial = preco_venda
    lucro_inicial = calcular_lucro(preco_venda_inicial)
    preco_desc_inicial = preco_venda_inicial * (1 - desconto / 100)
    margem_inicial = calcular_margem(lucro_inicial, preco_venda_inicial)

    preco_sug, lucro_sug, margem_sug = encontrar_preco_otimo(
        preco_venda_inicial, margem_lucro_desejado, calcular_lucro, calcular_margem, desconto,
    )
    preco_desc_sug = preco_sug * (1 - desconto / 100)
    cashback_calc  = preco_sug * (cashback / 100) if desconto > 0 else 0.0

    exibir_resultados({
        "platform": "Amazon",
        "preco_venda_inicial": preco_venda_inicial,
        "lucro_liquido_inicial": lucro_inicial,
        "margem_lucro_percent_inicial": margem_inicial,
        "preco_com_desconto_inicial": preco_desc_inicial,

        "preco_venda_sugerido": preco_sug,
        "lucro_liquido_sugerido": lucro_sug,
        "margem_lucro_percent_sugerido": margem_sug,
        "preco_com_desconto_sugerido": preco_desc_sug,

        "margem_lucro_desejado": margem_lucro_desejado,
        "quantidade": quantidade,
        "preco_custo": preco_custo,
        "custo_total_produto": preco_custo * quantidade,
        "imposto_percent": imposto,
        "valor_imposto": preco_desc_sug * (imposto / 100),
        "comissao_percent": comissao / 100,
        "valor_comissao_var": preco_desc_sug * (comissao / 100),
        "comissao_fixa": comissao_fixa,
        "valor_comissao_fixa": comissao_fixa,
        "tarifa": tarifa,
        "valor_tarifa": tarifa,
        "frete": frete,
        "valor_frete": frete,
        "desconto_percent": desconto,
        "cashback_percent": cashback,
        "cashback_calculado": cashback_calc,
        "rebate_valor": 0.0,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Magazine Luiza
# ─────────────────────────────────────────────────────────────────────────────

def handle_magazine() -> None:
    st.subheader("Precificador Magazine Luiza")

    opcao = st.selectbox(
        "Escolha a opção de comissão:",
        ["Magazine 12,80%", "Magazine 18%"],
        key="magalu_option",
    )
    comissao = 0.1280 if opcao == "Magazine 12,80%" else 0.18

    col1, col2 = st.columns(2)
    with col1:
        quantidade            = st.number_input("Quantidade:", value=1.0, min_value=1.0, step=1.0, key="mag_qtd")
        preco_custo           = st.number_input("Preço de Custo Unitário:", value=1.0, min_value=0.0, step=0.01, format="%.2f", key="mag_custo")
        preco_venda           = st.number_input("Preço de Venda Inicial:", value=1.0, min_value=0.01, step=0.01, format="%.2f", key="mag_venda")
        frete                 = st.number_input("Custo Frete:", min_value=0.0, value=0.0, step=0.01, format="%.2f", key="mag_frete")
        margem_lucro_desejado = st.number_input("Margem de lucro desejada (%):", min_value=0.0, max_value=100.0, value=12.0, step=0.1, format="%.1f", key="mag_margem")

    with col2:
        imposto     = st.number_input("Imposto (%):", value=0.0, min_value=0.0, max_value=100.0, step=0.1, format="%.1f", key="mag_imposto")
        desconto    = st.number_input("Desconto (%):", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f", key="mag_desconto")
        cashback    = st.number_input("Rebate da Plataforma (%):", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f", key="mag_cashback")
        rebate_fixo = st.number_input("Rebate Fixo (Valor R$):", value=0.0, min_value=0.0, step=0.01, format="%.2f", key="mag_rebate_fixo")

    st.info(f"Comissão selecionada: {comissao * 100:.2f}%. Tarifa fixa de R$ 5,00 aplicada se preço ≥ R$ 10,00.")

    if not st.button("Calcular Preço Magazine", key="mag_calc_btn"):
        return

    def calcular_lucro(preco: float) -> float:
        return magazine.calcular_lucro(
            quantidade=quantidade, preco_custo=preco_custo, frete=frete,
            preco_venda=preco, imposto=imposto, comissao=comissao,
            desconto=desconto, cashback=cashback,
        )

    def calcular_margem(lucro: float, preco: float) -> float:
        return _margem_com_desconto(lucro, preco, desconto, rebate=rebate_fixo)

    preco_venda_inicial = preco_venda
    lucro_inicial = calcular_lucro(preco_venda_inicial)
    preco_desc_inicial = preco_venda_inicial * (1 - desconto / 100)
    margem_inicial = calcular_margem(lucro_inicial, preco_venda_inicial)

    preco_sug, lucro_sug, margem_sug = encontrar_preco_otimo(
        preco_venda_inicial, margem_lucro_desejado, calcular_lucro, calcular_margem, desconto,
    )
    preco_desc_sug   = preco_sug * (1 - desconto / 100)
    tarifa_final     = 5.0 if preco_sug >= 10 else 0.0
    cashback_calc    = preco_sug * (cashback / 100) if desconto > 0 else 0.0

    exibir_resultados({
        "platform": "Magazine Luiza",
        "preco_venda_inicial": preco_venda_inicial,
        "lucro_liquido_inicial": lucro_inicial,
        "margem_lucro_percent_inicial": margem_inicial,
        "preco_com_desconto_inicial": preco_desc_inicial,

        "preco_venda_sugerido": preco_sug,
        "lucro_liquido_sugerido": lucro_sug,
        "margem_lucro_percent_sugerido": margem_sug,
        "preco_com_desconto_sugerido": preco_desc_sug,

        "margem_lucro_desejado": margem_lucro_desejado,
        "quantidade": quantidade,
        "preco_custo": preco_custo,
        "custo_total_produto": preco_custo * quantidade,
        "imposto_percent": imposto,
        "valor_imposto": preco_desc_sug * (imposto / 100),
        "comissao_percent": comissao,
        "valor_comissao_var": preco_desc_sug * comissao,
        "comissao_fixa": 0.0,
        "valor_comissao_fixa": 0.0,
        "tarifa": tarifa_final,
        "valor_tarifa": tarifa_final,
        "frete": frete,
        "valor_frete": frete,
        "desconto_percent": desconto,
        "cashback_percent": cashback,
        "cashback_calculado": cashback_calc,
        "rebate_valor": rebate_fixo,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Shopee
# ─────────────────────────────────────────────────────────────────────────────

def handle_shopee() -> None:
    st.subheader("Precificador Shopee")

    col1, col2 = st.columns(2)
    with col1:
        quantidade            = st.number_input("Quantidade:", value=1.0, min_value=1.0, step=1.0, key="shp_qtd")
        preco_custo           = st.number_input("Preço de Custo Unitário:", value=1.0, min_value=0.0, step=0.01, format="%.2f", key="shp_custo")
        preco_venda           = st.number_input("Preço de Venda Inicial:", value=1.0, min_value=0.01, step=0.01, format="%.2f", key="shp_venda")
        frete                 = st.number_input("Custo Frete:", min_value=0.0, value=0.0, step=0.01, format="%.2f", key="shp_frete")
        margem_lucro_desejado = st.number_input("Margem de lucro desejada (%):", min_value=0.0, max_value=100.0, value=12.0, step=0.1, format="%.1f", key="shp_margem")

    with col2:
        imposto  = st.number_input("Imposto (%):", value=0.0, min_value=0.0, max_value=100.0, step=0.1, format="%.1f", key="shp_imposto")
        desconto = st.number_input("Desconto (%):", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f", key="shp_desconto")

    st.info(
        f"Comissão fixa de {shopee.COMISSAO * 100:.0f}%, "
        f"Tarifa fixa de R$ {shopee.TARIFA_FIXA:.2f}."
    )

    if not st.button("Calcular Preço Shopee", key="shp_calc_btn"):
        return

    def calcular_lucro(preco: float) -> float:
        return shopee.calcular_lucro(
            quantidade=quantidade, preco_custo=preco_custo, frete=frete,
            preco_venda=preco, imposto=imposto, desconto=desconto,
        )

    def calcular_margem(lucro: float, preco: float) -> float:
        return _margem_com_desconto(lucro, preco, desconto)

    preco_venda_inicial = preco_venda
    lucro_inicial = calcular_lucro(preco_venda_inicial)
    preco_desc_inicial = preco_venda_inicial * (1 - desconto / 100)
    margem_inicial = calcular_margem(lucro_inicial, preco_venda_inicial)

    preco_sug, lucro_sug, margem_sug = encontrar_preco_otimo(
        preco_venda_inicial, margem_lucro_desejado, calcular_lucro, calcular_margem, desconto,
    )
    preco_desc_sug = preco_sug * (1 - desconto / 100)

    exibir_resultados({
        "platform": "Shopee",
        "preco_venda_inicial": preco_venda_inicial,
        "lucro_liquido_inicial": lucro_inicial,
        "margem_lucro_percent_inicial": margem_inicial,
        "preco_com_desconto_inicial": preco_desc_inicial,

        "preco_venda_sugerido": preco_sug,
        "lucro_liquido_sugerido": lucro_sug,
        "margem_lucro_percent_sugerido": margem_sug,
        "preco_com_desconto_sugerido": preco_desc_sug,

        "margem_lucro_desejado": margem_lucro_desejado,
        "quantidade": quantidade,
        "preco_custo": preco_custo,
        "custo_total_produto": preco_custo * quantidade,
        "imposto_percent": imposto,
        "valor_imposto": preco_desc_sug * (imposto / 100),
        "comissao_percent": shopee.COMISSAO,
        "valor_comissao_var": preco_desc_sug * shopee.COMISSAO,
        "comissao_fixa": 0.0,
        "valor_comissao_fixa": 0.0,
        "tarifa": shopee.TARIFA_FIXA,
        "valor_tarifa": shopee.TARIFA_FIXA,
        "frete": frete,
        "valor_frete": frete,
        "desconto_percent": desconto,
        "cashback_percent": 0.0,
        "cashback_calculado": 0.0,
        "rebate_valor": 0.0,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Mercado Livre
# ─────────────────────────────────────────────────────────────────────────────

_ML_OPCOES = {
    "Clássico / Tarifa Padrão":  {"comissao": 0.12, "tarifa_base": 0},
    "Clássico / Super Mercado":  {"comissao": 0.14, "tarifa_base": 2},
    "Premium / Tarifa Padrão":   {"comissao": 0.17, "tarifa_base": 0},
    "Premium / Super Mercado":   {"comissao": 0.19, "tarifa_base": 2},
}




"""
TRECHO ATUALIZADO — handle_mercadolivre() em views/precificador.py
Apenas as partes que mudaram estão aqui.
"""

def handle_mercadolivre() -> None:
    st.subheader("Precificador Mercado Livre")

    def _formatar_opcao(key: str) -> str:
        d = _ML_OPCOES[key]
        tarifa_str = (
            "Tarifa Fixa Padrão (<R$79)" if d["tarifa_base"] == 0
            else f"Fixa R$ {d['tarifa_base']:.2f}"
        )
        return f"{key} ({d['comissao'] * 100:.0f}% + {tarifa_str})"

    opcao = st.selectbox(
        "Escolha o tipo de anúncio e tarifa:",
        list(_ML_OPCOES.keys()),
        format_func=_formatar_opcao,
        key="ml_option",
    )
    comissao       = _ML_OPCOES[opcao]["comissao"]
    #tarifa_base    = _ML_OPCOES[opcao]["tarifa_base"]

    # ... selectbox de tipo de anúncio (inalterado) ...

    col1, col2 = st.columns(2)
    with col1:
        quantidade            = st.number_input("Quantidade:", value=1.0, min_value=1.0, step=1.0, key="ml_qtd")
        preco_custo           = st.number_input("Preço de Custo Unitário:", value=1.0, min_value=0.0, step=0.01, format="%.2f", key="ml_custo")
        preco_venda           = st.number_input("Preço de Venda Inicial:", value=1.0, min_value=0.01, step=0.01, format="%.2f", key="ml_venda")
        peso_kg               = st.number_input("Peso do produto (kg):", min_value=0.01, value=0.5, step=0.1, format="%.3f", key="ml_peso")  # ← NOVO
        margem_lucro_desejado = st.number_input("Margem de lucro desejada (%):", min_value=0.0, max_value=100.0, value=10.0, step=0.1, format="%.1f", key="ml_margem")

    with col2:
        imposto  = st.number_input("Imposto (%):", value=0.0, min_value=0.0, max_value=100.0, step=0.1, format="%.1f", key="ml_imposto")
        desconto = st.number_input("Desconto (%):", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f", key="ml_desconto")
        rebate   = st.number_input("Rebate (Valor Fixo):", value=0.0, min_value=0.0, step=0.01, format="%.2f", key="ml_rebate")

    # ── NOVO: calcular e exibir o custo de envio em tempo real ──
    custo_envio = mercadolivre.calcular_custo_envio(preco_venda, peso_kg)
    st.info(
        f"📦 Custo de envio ML (tabela 02/03/2026): **R$ {custo_envio:.2f}** "
        f"— produto R$ {preco_venda:.2f} / {peso_kg:.2f} kg"
    )

    # ... warnings e info de comissão (inalterados) ...

    if not st.button("Calcular Preço Mercado Livre", key="ml_calc_btn"):
        return
    

    def calcular_lucro(preco: float) -> float:
        # ← custo_envio agora é recalculado com o preco atual da iteração
        frete_atual = mercadolivre.calcular_custo_envio(preco, peso_kg)
        return mercadolivre.calcular_lucro(
            quantidade=quantidade, preco_custo=preco_custo, preco_venda=preco,
            frete=0.0, comissao=comissao, imposto=imposto,
            tarifa_fixa_base=frete_atual, desconto=desconto,
        )

    # ... resto do handler (encontrar_preco_otimo, exibir_resultados) inalterado ...
    # Apenas lembrar de usar custo_envio no dict final:
    #   "frete": custo_envio,
    #   "valor_frete": custo_envio,

    def calcular_margem(lucro: float, preco: float) -> float:
        return _margem_com_desconto(lucro, preco, desconto, rebate=rebate)

    preco_venda_inicial = preco_venda
    lucro_inicial = calcular_lucro(preco_venda_inicial)
    preco_desc_inicial = preco_venda_inicial * (1 - desconto / 100)
    margem_inicial = calcular_margem(lucro_inicial, preco_venda_inicial)

    preco_sug, lucro_sug, margem_sug = encontrar_preco_otimo(
        preco_venda_inicial, margem_lucro_desejado, calcular_lucro, calcular_margem, desconto,
    )
    preco_desc_sug = preco_sug * (1 - desconto / 100)

    custo_envio_inicial  = mercadolivre.calcular_custo_envio(preco_venda_inicial, peso_kg)
    custo_envio_sugerido = mercadolivre.calcular_custo_envio(preco_sug, peso_kg)


    exibir_resultados({
        "platform": "Mercado Livre",
        "preco_venda_inicial": preco_venda_inicial,
        "lucro_liquido_inicial": lucro_inicial,
        "margem_lucro_percent_inicial": margem_inicial,
        "preco_com_desconto_inicial": preco_desc_inicial,

        "preco_venda_sugerido": preco_sug,
        "lucro_liquido_sugerido": lucro_sug,
        "margem_lucro_percent_sugerido": margem_sug,
        "preco_com_desconto_sugerido": preco_desc_sug,

        "margem_lucro_desejado": margem_lucro_desejado,
        "quantidade": quantidade,
        "preco_custo": preco_custo,
        "custo_total_produto": preco_custo * quantidade,
        "imposto_percent": imposto,
        "valor_imposto": preco_desc_sug * (imposto / 100),
        "comissao_percent": comissao,
        "valor_comissao_var": preco_desc_sug * comissao,
        "comissao_fixa": 0.0,
        "valor_comissao_fixa": 0.0,
        "tarifa_inicial": custo_envio_inicial,
        "valor_tarifa_inicial": custo_envio_inicial,
        "tarifa_preco_sugerido": custo_envio_sugerido,
        "valor_tarifa_preco_sugerido": custo_envio_sugerido,
        "desconto_percent": desconto,
        "cashback_percent": 0.0,
        "cashback_calculado": 0.0,
        "rebate_valor": rebate,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Venda Direta
# ─────────────────────────────────────────────────────────────────────────────

def handle_venda_direta() -> None:
    st.subheader("Precificador Venda Direta")

    col1, col2 = st.columns(2)
    with col1:
        quantidade            = st.number_input("Quantidade:", value=1.0, min_value=1.0, step=1.0, key="vd_qtd")
        preco_custo           = st.number_input("Preço de Custo Unitário:", value=1.0, min_value=0.0, step=0.01, format="%.2f", key="vd_custo")
        preco_venda           = st.number_input("Preço de Venda Inicial:", value=1.0, min_value=0.01, step=0.01, format="%.2f", key="vd_venda")
        frete                 = st.number_input("Custo Frete:", min_value=0.0, value=0.0, step=0.01, format="%.2f", key="vd_frete")

    with col2:
        imposto               = st.number_input("Imposto (%):", value=0.0, min_value=0.0, max_value=100.0, step=0.1, format="%.1f", key="vd_imposto")
        margem_lucro_desejado = st.number_input("Margem de lucro desejada (%):", min_value=0.0, max_value=100.0, value=12.0, step=0.1, format="%.1f", key="vd_margem")

    st.info("Cálculo simplificado para venda direta (sem comissões ou tarifas de marketplace).")

    if not st.button("Calcular Preço Venda Direta", key="vd_calc_btn"):
        return

    def calcular_lucro(preco: float) -> float:
        return venda_direta.calcular_lucro(
            quantidade=quantidade, preco_custo=preco_custo, preco_venda=preco,
            frete=frete, imposto=imposto,
        )

    def calcular_margem(lucro: float, preco: float) -> float:
        return _margem_sem_desconto(lucro, preco)

    preco_venda_inicial = preco_venda
    lucro_inicial = calcular_lucro(preco_venda_inicial)
    margem_inicial = calcular_margem(lucro_inicial, preco_venda_inicial)

    preco_sug, lucro_sug, margem_sug = encontrar_preco_otimo(
        preco_venda_inicial, margem_lucro_desejado, calcular_lucro, calcular_margem,
    )

    exibir_resultados({
        "platform": "Venda Direta",
        "preco_venda_inicial": preco_venda_inicial,
        "lucro_liquido_inicial": lucro_inicial,
        "margem_lucro_percent_inicial": margem_inicial,
        "preco_com_desconto_inicial": preco_venda_inicial,

        "preco_venda_sugerido": preco_sug,
        "lucro_liquido_sugerido": lucro_sug,
        "margem_lucro_percent_sugerido": margem_sug,
        "preco_com_desconto_sugerido": preco_sug,

        "margem_lucro_desejado": margem_lucro_desejado,
        "quantidade": quantidade,
        "preco_custo": preco_custo,
        "custo_total_produto": preco_custo * quantidade,
        "imposto_percent": imposto,
        "valor_imposto": preco_sug * (imposto / 100),
        "comissao_percent": 0.0,
        "valor_comissao_var": 0.0,
        "comissao_fixa": 0.0,
        "valor_comissao_fixa": 0.0,
        "tarifa": 0.0,
        "valor_tarifa": 0.0,
        "frete": frete,
        "valor_frete": frete,
        "desconto_percent": 0.0,
        "cashback_percent": 0.0,
        "cashback_calculado": 0.0,
        "rebate_valor": 0.0,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Nota Fiscal
# ─────────────────────────────────────────────────────────────────────────────

def handle_nota_fiscal() -> None:
    st.subheader("Calculadora de Custo de Nota Fiscal")

    col1, col2 = st.columns(2)
    with col1:
        quantidade  = st.number_input("Quantidade Comprada:", value=1, min_value=1, step=1, key="nf_qtd")
        preco_custo = st.number_input("Preço de Custo Unitário (NF):", value=0.0, min_value=0.0, format="%.4f", step=0.0001, key="nf_custo")
        ipi         = st.number_input("IPI (%):", value=0.0, min_value=0.0, format="%.3f", step=0.001, key="nf_ipi")

    with col2:
        bonificacao            = st.number_input("Bonificação (Valor Total R$):", value=0.0, min_value=0.0, format="%.2f", key="nf_bon_valor")
        bonificacao_porcentagem = st.number_input("Bonificação (% sobre Valor Total Produtos):", value=0.0, min_value=0.0, format="%.2f", key="nf_bon_pct")

    if not st.button("Calcular Custo NF", key="nf_calc_btn"):
        return

    if quantidade <= 0:
        st.error("A quantidade deve ser maior que zero.")
        return

    if bonificacao > 0 and bonificacao_porcentagem > 0:
        st.warning("Informe a bonificação OU em valor OU em porcentagem. Usando apenas o valor informado.")
        bonificacao_porcentagem = 0.0

    resultado_total   = nota_fiscal.calcular_custo_nota_fiscal(
        quantidade=quantidade, preco_custo=preco_custo, ipi=ipi,
        bonificacao=bonificacao, bonificacao_porcentagem=bonificacao_porcentagem,
    )
    custo_unitario    = resultado_total / quantidade if quantidade > 0 else 0.0
    valor_total_bruto = preco_custo * quantidade
    valor_ipi         = valor_total_bruto * (ipi / 100)
    valor_bonificacao = (
        bonificacao if bonificacao > 0
        else valor_total_bruto * (bonificacao_porcentagem / 100)
    )

    st.markdown("---")
    st.subheader("Resultados do Cálculo da Nota Fiscal")
    st.metric("Valor Total Produtos (NF)", f"R$ {valor_total_bruto:.4f}")
    st.metric("Valor IPI Calculado", f"+ R$ {valor_ipi:.4f}")
    if valor_bonificacao > 0:
        st.metric("Valor da Bonificação Aplicada", f"- R$ {valor_bonificacao:.2f}")
    st.metric("Valor Total Final Calculado (NF)", f"R$ {resultado_total:.4f}", delta_color="inverse")
    st.metric("Custo Unitário Final Efetivo", f"R$ {custo_unitario:.4f}")

    st.markdown("---")
    st.write("Detalhamento:")
    st.table({
        "Componente": [
            "Valor Produtos (Qtd x Custo Unit.)",
            "Valor IPI",
            "Bonificação Aplicada",
            "Valor Final",
        ],
        "Valor (R$)": [
            f"{valor_total_bruto:.4f}",
            f"+ {valor_ipi:.4f}",
            f"- {valor_bonificacao:.2f}",
            f"= {resultado_total:.4f}",
        ],
    })


# ─────────────────────────────────────────────────────────────────────────────
# Roteador da página Precificador
# ─────────────────────────────────────────────────────────────────────────────

_PLATAFORMAS = {
    "Amazon":        handle_amazon,
    "Magazine Luiza": handle_magazine,
    "Shopee":        handle_shopee,
    "Mercado Livre": handle_mercadolivre,
    "Venda Direta":  handle_venda_direta,
    "Nota Fiscal":   handle_nota_fiscal,
}


def render() -> None:
    """Renderiza a página completa do Precificador."""
    st.title("Precificador")
    st.caption("Calcule o preço de venda ideal para diversas plataformas.")

    plataforma = st.selectbox("Escolha a Plataforma:", list(_PLATAFORMAS.keys()))

    handler = _PLATAFORMAS.get(plataforma)
    if handler:
        handler()
    else:
        st.error("Plataforma selecionada não é válida.")
