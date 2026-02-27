import streamlit as st
import pandas as pd

from calculators.frete import calcular_custo_frete
from utils.excel import to_excel

# Mapeamento label → valor interno de reputação
_OPCOES_REPUTACAO = {
    "< 92% (sem desconto)":              0.91,
    "Entre 92% e 97% (desconto 25%)":    0.93,
    ">= 97% (desconto 50%)":             0.99,
    "Líder/Outros (desconto 75%)":       99.9,
}

_COLUNAS_NECESSARIAS = ["SKU", "TITULO", "Preço POR", "COMPRIMENTO", "LARGURA", "ALTURA"]


def render() -> None:
    """Renderiza a página completa de cálculo de frete Magazine Luiza."""
    st.title("Calculadora de Frete - Magazine Luiza")
    st.caption("Estime o custo de frete com base na sua reputação e dados do produto.")

    with st.sidebar:
        st.markdown("---")
        opcao_reputacao = st.radio(
            "**Sua Reputação no Magalu**",
            list(_OPCOES_REPUTACAO.keys()),
            index=None,
            key="reputacao_radio",
            help="Selecione o nível de reputação para aplicar o desconto de frete correto.",
        )

    reputacao_valor = _OPCOES_REPUTACAO.get(opcao_reputacao)

    uploaded_files = st.file_uploader(
        "Importe a(s) planilha(s) de produtos do Magalu (.xlsx)",
        accept_multiple_files=True,
        type=["xlsx"],
        help="Faça upload dos arquivos Excel exportados do Magalu contendo as abas 'PRODUTO' e 'PREÇO'.",
    )

    if not uploaded_files:
        st.info("Aguardando upload da planilha de produtos Magalu...")
        return

    if reputacao_valor is None:
        st.warning("Por favor, **selecione sua reputação** na barra lateral para calcular o frete.")
        return

    all_results_df = pd.DataFrame()

    for uploaded_file in uploaded_files:
        resultado = _processar_arquivo(uploaded_file, reputacao_valor)
        if resultado is not None:
            all_results_df = pd.concat([all_results_df, resultado], ignore_index=True)

    _exibir_resultados(all_results_df, uploaded_files)


def _processar_arquivo(uploaded_file, reputacao_valor: float) -> pd.DataFrame | None:
    """Lê, valida, mescla e calcula o frete de um arquivo .xlsx do Magalu."""
    st.write(f"**Processando arquivo:** `{uploaded_file.name}`")

    try:
        xls = pd.ExcelFile(uploaded_file, engine="openpyxl")

        abas_ausentes = [a for a in ("PRODUTO", "PREÇO") if a not in xls.sheet_names]
        if abas_ausentes:
            st.error(
                f"Arquivo '{uploaded_file.name}' não contém a(s) aba(s): "
                f"{', '.join(abas_ausentes)}. Pulando."
            )
            return None

        df_produto = pd.read_excel(xls, sheet_name="PRODUTO", skiprows=2)
        df_preco   = pd.read_excel(xls, sheet_name="PREÇO",   skiprows=2)

        for df, nome_aba in ((df_produto, "PRODUTO"), (df_preco, "PREÇO")):
            if "SKU" not in df.columns:
                st.error(f"Coluna 'SKU' ausente na aba '{nome_aba}' de '{uploaded_file.name}'. Pulando.")
                return None

        df_produto["SKU"] = df_produto["SKU"].astype(str).str.strip()
        df_preco["SKU"]   = df_preco["SKU"].astype(str).str.strip()

        df = pd.merge(df_produto, df_preco, on="SKU", how="inner", suffixes=("_prod", "_preco"))

        status_col = "Status do Produto"
        if status_col not in df.columns:
            st.warning(f"Coluna '{status_col}' ausente — não foi possível filtrar por produtos publicados.")
        else:
            df[status_col] = df[status_col].astype(str).fillna("").str.lower()
            df = df[df[status_col] == "publicado"]

        if df.empty:
            st.warning(f"Nenhum produto 'Publicado' encontrado em '{uploaded_file.name}'.")
            return None

        colunas_ausentes = [c for c in _COLUNAS_NECESSARIAS if c not in df.columns]
        if colunas_ausentes:
            st.error(f"Colunas ausentes em '{uploaded_file.name}': {', '.join(colunas_ausentes)}. Pulando.")
            return None

        df_filtrado = df[_COLUNAS_NECESSARIAS].copy()
        df_filtrado["Custo Frete Estimado"] = df_filtrado.apply(
            lambda row: calcular_custo_frete(row=row, reputacao=reputacao_valor), axis=1
        )
        df_filtrado["Custo Frete Estimado"] = pd.to_numeric(
            df_filtrado["Custo Frete Estimado"], errors="coerce"
        )
        return df_filtrado

    except Exception as e:
        st.error(f"Erro inesperado ao processar '{uploaded_file.name}'. Verifique o formato.")
        st.exception(e)
        return None


def _exibir_resultados(df: pd.DataFrame, uploaded_files) -> None:
    if df.empty:
        st.info("Nenhum produto válido encontrado nos arquivos processados.")
        return

    st.markdown("---")
    st.subheader("Resultados do Cálculo de Frete")

    df_display = df.copy()
    df_display["Custo Frete Estimado"] = df_display["Custo Frete Estimado"].apply(
        lambda x: f"R$ {x:.2f}" if pd.notna(x) else "Erro/Dados Inválidos"
    )
    df_display = df_display.fillna("Dado Ausente")
    st.dataframe(df_display, use_container_width=True)

    df_download = df.copy()
    df_download.fillna({"Custo Frete Estimado": -1}, inplace=True)
    df_download = df_download.fillna("Dado Ausente")

    st.download_button(
        label="Baixar Planilha de Fretes Estimados",
        data=to_excel(df_download),
        file_name="frete_magalu_estimado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
