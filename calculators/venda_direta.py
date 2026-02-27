def calcular_lucro(
    quantidade: float,
    preco_custo: float,
    preco_venda: float,
    frete: float,
    imposto: float,
    desconto: float = 0.0,
) -> float:
  
    if preco_venda <= 0:
        return -float("inf")

    preco_efetivo = preco_venda * (1 - desconto / 100) if desconto > 0 else preco_venda
    if preco_efetivo <= 0:
        return -float("inf")

    valor_imposto = preco_efetivo * (imposto / 100)
    custo_produto = preco_custo * quantidade

    return preco_efetivo - frete - valor_imposto - custo_produto
