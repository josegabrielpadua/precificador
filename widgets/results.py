import streamlit as st
import pandas as pd
import plotly.express as px


def exibir_resultados(results: dict) -> None:
    """
    Exibe o painel completo de resultados de precificação.
    """
    st.markdown("---")
    st.subheader("📊 Resultados do Cálculo")

    # ── Extração dos valores ─────────────────────────────────────────────────
    preco_venda_inicial         = results.get("preco_venda_inicial", 0)
    lucro_liquido_inicial       = results.get("lucro_liquido_inicial", 0)
    margem_percent_inicial      = results.get("margem_lucro_percent_inicial", 0)
    preco_com_desconto_inicial  = results.get("preco_com_desconto_inicial", preco_venda_inicial)

    preco_sugerido              = results.get("preco_venda_sugerido", 0)
    lucro_liquido_sugerido      = results.get("lucro_liquido_sugerido", 0)
    margem_percent_sugerido     = results.get("margem_lucro_percent_sugerido", 0)
    preco_com_desconto_sugerido = results.get("preco_com_desconto_sugerido", preco_sugerido)

    margem_desejada     = results.get("margem_lucro_desejado", 0)
    custo_total_produto = results.get("custo_total_produto", 0)
    valor_imposto       = results.get("valor_imposto", 0)
    valor_comissao_var  = results.get("valor_comissao_var", 0)
    valor_comissao_fixa = results.get("valor_comissao_fixa", 0)
    desconto_percent    = results.get("desconto_percent", 0)
    rebate_valor        = results.get("rebate_valor", 0)
    cashback_percent    = results.get("cashback_percent", 0)
    cashback_calculado  = results.get("cashback_calculado", 0)

    # Suporta formato antigo (valor_tarifa + valor_frete separados)
    # e novo formato ML (tarifa_inicial + tarifa_preco_sugerido)
    custo_envio_inicial  = results.get("tarifa_inicial",        results.get("valor_tarifa", 0))
    custo_envio_sugerido = results.get("tarifa_preco_sugerido", results.get("valor_tarifa", 0))
    valor_frete          = results.get("valor_frete", 0)

    # ── Resultado com preço inicial ──────────────────────────────────────────
    st.markdown("#### 🏷️ Resultado com Preço Inicial Informado")

    if desconto_percent > 0:
        st.write(
            f"_Preço Inicial com Desconto ({desconto_percent:.1f}%): "
            f"R$ {preco_com_desconto_inicial:.2f}_"
        )

    col1, col2, col3 = st.columns(3)
    col1.metric("Preço de Venda Inicial", f"R$ {preco_venda_inicial:.2f}")

    with col2:
        st.metric("Lucro Líquido (Inicial)", f"R$ {lucro_liquido_inicial:.2f}")
        cor = "blue" if margem_percent_inicial >= margem_desejada else "red"
        label = "Acima" if cor == "blue" else "Abaixo"
        st.markdown(f":{cor}[Resultado Margem: {label} da meta]")

    col3.metric(
        "Margem (Inicial)",
        f"{margem_percent_inicial:.2f}%",
        delta=f"{margem_percent_inicial - margem_desejada:.2f} pts vs Desejada",
        delta_color="normal",
    )

    if custo_envio_inicial > 0:
        st.caption(f"📦 Custo de envio (preço inicial): R$ {custo_envio_inicial:.2f}")

    if rebate_valor > 0:
        st.write(f"**_:orange[Valor do Rebate (Input): R$ {rebate_valor:.2f}]_**")
        st.write(
            f"**_:orange[Lucro Líquido Inicial + Rebate: "
            f"R$ {lucro_liquido_inicial + rebate_valor:.2f}]_**"
        )
        st.caption("_Rebate considerado na meta de margem para esta plataforma, se aplicável._")

    # ── Resultado com preço sugerido ─────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### ✨ Resultado com Preço Sugerido")

    delta_vs_inicial = (
        f"{((preco_sugerido - preco_venda_inicial) / preco_venda_inicial * 100):.1f}% vs Inicial"
        if preco_venda_inicial > 0 and preco_sugerido != preco_venda_inicial
        else None
    )
    col1, col2, col3 = st.columns(3)
    col1.metric("Preço de Venda Sugerido", f"R$ {preco_sugerido:.2f}", delta_vs_inicial)
    col2.metric("Lucro Líquido (Sugerido)", f"R$ {lucro_liquido_sugerido:.2f}")
    col3.metric(
        "Margem de Lucro (Sugerido)",
        f"{margem_percent_sugerido:.2f}%",
        delta=f"{margem_percent_sugerido - margem_desejada:.2f} pts vs Desejada",
    )

    if custo_envio_sugerido != custo_envio_inicial:
        st.caption(
            f"📦 Custo de envio mudou com o preço sugerido: "
            f"R$ {custo_envio_inicial:.2f} → R$ {custo_envio_sugerido:.2f}"
        )
    elif custo_envio_sugerido > 0:
        st.caption(f"📦 Custo de envio (preço sugerido): R$ {custo_envio_sugerido:.2f}")

    if rebate_valor > 0:
        st.write(
            f"**_:orange[Lucro Líquido Sugerido + Rebate: "
            f"R$ {lucro_liquido_sugerido + rebate_valor:.2f}]_**"
        )

    # ── Detalhes do cálculo ──────────────────────────────────────────────────
    st.markdown("---")
    expand = margem_percent_inicial < margem_desejada
    with st.expander("Ver Detalhes do Cálculo (Baseado no Preço Sugerido)", expanded=expand):
        st.write(f"**Preço de Venda Base (Sugerido):** R$ {preco_sugerido:.2f}")

        if desconto_percent > 0:
            st.write(
                f"**Desconto Aplicado ({desconto_percent:.1f}%):** "
                f"- R$ {preco_sugerido * desconto_percent / 100:.2f}"
            )
            st.write(f"**Preço Efetivo Sugerido (com desconto):** R$ {preco_com_desconto_sugerido:.2f}")
        else:
            st.write(f"**Preço Efetivo Sugerido:** R$ {preco_sugerido:.2f}")

        st.write(f"**Cashback Oferecido ao Cliente (% input):** {cashback_percent:.1f}%")
        if cashback_calculado > 0:
            st.write(f"**Valor Cashback Calculado:** + R$ {cashback_calculado:.2f}")
            st.caption("*Cashback calculado apenas quando Desconto > 0 em algumas plataformas.")
        else:
            st.write("**Valor Cashback Calculado:** R$ 0.00")

        st.markdown("---")
        st.subheader("Custos (Baseado no Preço Sugerido):")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.write(f"**Custo do Produto ({results.get('quantidade', 1)} un.):** - R$ {custo_total_produto:.2f}")
            st.write(f"**Imposto ({results.get('imposto_percent', 0):.1f}%):** - R$ {valor_imposto:.2f}")
            st.write(f"**Comissão Variável ({results.get('comissao_percent', 0) * 100:.1f}%):** - R$ {valor_comissao_var:.2f}")
        with col_c2:
            st.write(f"**Comissão Fixa:** - R$ {valor_comissao_fixa:.2f}")
            st.write(f"**Custo de Envio:** - R$ {custo_envio_sugerido:.2f}")
            if valor_frete > 0:
                st.write(f"**Frete adicional:** - R$ {valor_frete:.2f}")

        st.markdown("---")
        total_custos = (
            custo_total_produto + valor_imposto + valor_comissao_var
            + valor_comissao_fixa + custo_envio_sugerido + valor_frete
        )
        receita_efetiva = preco_com_desconto_sugerido + cashback_calculado
        st.write(f"**Total de Custos:** R$ {total_custos:.2f}")
        st.write(f"**Receita Efetiva Sugerida:** R$ {receita_efetiva:.2f}")
        st.write(f"**Lucro Líquido Calculado (antes de Rebate):** R$ {lucro_liquido_sugerido:.2f}")
        if rebate_valor > 0:
            st.write(f"**_:orange[+ Rebate Fixo:]_** R$ {rebate_valor:.2f}")
            st.write(
                f"**_:orange[= Lucro Líquido Final:]_** "
                f"R$ {lucro_liquido_sugerido + rebate_valor:.2f}"
            )

    # ── Gráfico de composição ────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Visualização da Composição do Preço (Baseado no Preço Sugerido)")

    chart_data = pd.DataFrame({
        "Componente": [
            "Custo Produto", "Imposto", "Comissão Var.", "Comissão Fixa",
            "Custo de Envio", "Frete Adicional", "Lucro Líquido (antes Rebate)",
        ],
        "Valor": [
            max(0, custo_total_produto), max(0, valor_imposto), max(0, valor_comissao_var),
            max(0, valor_comissao_fixa), max(0, custo_envio_sugerido),
            max(0, valor_frete), max(0, lucro_liquido_sugerido),
        ],
    })
    chart_data = chart_data[chart_data["Valor"] > 0.005]

    if not chart_data.empty:
        receita_chart = preco_com_desconto_sugerido + cashback_calculado
        diferenca = receita_chart - chart_data["Valor"].sum()
        if abs(diferenca) > 0.01:
            label = "Ajuste Arredond." if diferenca > 0 else "Ajuste Negativo"
            nova_linha = pd.DataFrame([{"Componente": label, "Valor": abs(diferenca)}])
            chart_data = pd.concat([chart_data, nova_linha], ignore_index=True)

        fig = px.pie(
            chart_data,
            values="Valor",
            names="Componente",
            title=f"Composição da Receita Efetiva Sugerida (R$ {receita_chart:.2f})",
            hole=0.3,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label", hoverinfo="label+percent+value")
        fig.update_layout(showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Não há dados suficientes para gerar o gráfico de composição.")


__all__ = ["exibir_resultados"]