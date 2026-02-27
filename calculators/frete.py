import pandas as pd

# Tabela de faixas de peso → custo base de frete (Magazine Luiza)
_TABELA_FRETE = [
    (0.5,   27.90),
    (1,     32.90),
    (2,     35.90),
    (5,     44.90),
    (9,     47.90),
    (13,    52.90),
    (17,    57.90),
    (23,    62.90),
    (29,    67.90),
    (30,    69.90),
    (40,   179.90),
    (50,   189.90),
    (60,   199.90),
    (70,   209.90),
    (80,   219.90),
    (90,   229.90),
    (100,  239.90),
    (110,  249.90),
    (120,  259.90),
    (130,  269.90),
    (140,  279.90),
    (150,  289.90),
    (160,  299.90),
    (170,  309.90),
    (180,  319.90),
    (190,  329.90),
    (200,  339.90),
]
_CUSTO_MAXIMO = 349.90


def _custo_base_por_peso(peso: float) -> float:
    for limite, custo in _TABELA_FRETE:
        if peso <= limite:
            return custo
    return _CUSTO_MAXIMO


def _fator_desconto_reputacao(reputacao: float) -> float:
    if reputacao == 99.9:
        return 0.25   # Líder → 75% de desconto
    if reputacao >= 0.97:
        return 0.50   # ≥ 97% → 50% de desconto
    if reputacao >= 0.92:
        return 0.75   # 92–97% → 25% de desconto
    return 1.0        # < 92% → sem desconto


def calcular_custo_frete(row: pd.Series, reputacao: float) -> float | None:

    try:
        valor_produto = pd.to_numeric(row["Preço POR"], errors="coerce")
        if pd.isna(valor_produto):
            return None

        comprimento_m = pd.to_numeric(row["COMPRIMENTO"], errors="coerce") / 100
        largura_m = pd.to_numeric(row["LARGURA"], errors="coerce") / 100
        altura_m = pd.to_numeric(row["ALTURA"], errors="coerce") / 100

        if any(pd.isna(v) for v in (comprimento_m, largura_m, altura_m)):
            return None

        peso = comprimento_m * largura_m * altura_m * 167
    except (KeyError, TypeError, ValueError):
        return None

    if valor_produto <= 79:
        return 0.0

    custo_base = _custo_base_por_peso(peso)
    fator = _fator_desconto_reputacao(reputacao)
    return max(0.0, custo_base * fator)
