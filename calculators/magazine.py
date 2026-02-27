def calcular_lucro(
    quantidade: float,
    preco_custo: float,
    frete: float,
    preco_venda: float,
    imposto: float,
    comissao: float,
    desconto: float = 0.0,
    cashback: float = 0.0,
) -> float:

    TARIFA_FIXA = 5.0 if preco_venda >= 10 else 0.0

    if preco_venda <= 0:
        return -float("inf")

    if desconto > 0:
        cashback_valor = preco_venda * (cashback / 100)
        preco_efetivo = preco_venda * (1 - desconto / 100)
        if preco_efetivo <= 0:
            return -float("inf")
    else:
        cashback_valor = 0.0
        preco_efetivo = preco_venda

    valor_comissao = preco_efetivo * comissao
    valor_imposto = preco_efetivo * (imposto / 100)
    custo_produto = preco_custo * quantidade

    return (
        preco_efetivo
        + cashback_valor
        - frete
        - valor_comissao
        - valor_imposto
        - TARIFA_FIXA
        - custo_produto
    )
