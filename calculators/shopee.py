"""
Calculadora Shopee — tarifas válidas a partir de 01/03/2026 (vendedor CNPJ).

A comissão agora é variável por faixa de preço:
  Até R$79,99          → 20% + R$4
  R$80  – R$99,99      → 14% + R$16
  R$100 – R$199,99     → 14% + R$20
  R$200 – R$499,99     → 14% + R$26
  R$500+               → 14% + R$26

Subsídio Pix (5% ou 8%): é absorvido pela Shopee — o vendedor
recebe o mesmo valor líquido independente do meio de pagamento.
Por isso ele NÃO entra no cálculo do lucro do vendedor.
"""

# Tabela: (limite_superior, comissao_pct, tarifa_fixa)
# limite_superior = None → sem limite (última faixa)
_TABELA_COMISSAO = [
    (79.99,  0.20,  4.0),
    (99.99,  0.14, 16.0),
    (199.99, 0.14, 20.0),
    (499.99, 0.14, 26.0),
    (None,   0.14, 26.0),   # R$500+
]


def calcular_comissao(preco_venda: float) -> tuple[float, float]:
    """
    Retorna (comissao_pct, tarifa_fixa) para o preço informado.

    Regra especial: produtos abaixo de R$8 → tarifa = metade do preço.
    """
    if preco_venda < 8:
        return 0.0, preco_venda / 2

    for limite, pct, fixo in _TABELA_COMISSAO:
        if limite is None or preco_venda <= limite:
            return pct, fixo

    return 0.14, 26.0  # fallback (não deve ser atingido)


def calcular_lucro(
    quantidade: float,
    preco_custo: float,
    frete: float,
    preco_venda: float,
    imposto: float,
    desconto: float = 0.0,
) -> float:
    """
    Calcula o lucro líquido de uma venda na Shopee (CNPJ, a partir de 01/03/2026).

    Args:
        quantidade: quantidade de itens.
        preco_custo: custo unitário (R$).
        frete: custo de frete (R$).
        preco_venda: preço de venda cheio (R$).
        imposto: imposto percentual (%).
        desconto: desconto percentual (%).

    Returns:
        Lucro líquido (R$) ou -inf se o preço for inválido.
    """
    if preco_venda <= 0:
        return -float("inf")

    preco_efetivo = preco_venda * (1 - desconto / 100) if desconto > 0 else preco_venda
    if preco_efetivo <= 0:
        return -float("inf")

    comissao_pct, tarifa_fixa = calcular_comissao(preco_efetivo)

    valor_comissao = preco_efetivo * comissao_pct
    valor_imposto  = preco_efetivo * (imposto / 100)
    custo_produto  = preco_custo * quantidade

    return preco_efetivo - frete - valor_comissao - valor_imposto - tarifa_fixa - custo_produto