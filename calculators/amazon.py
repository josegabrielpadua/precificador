import math


def calcular_tarifa_peso(peso_g: float) -> float:
    """Retorna a tarifa baseada no peso (gramas) para Amazon."""
    if peso_g <= 100:   return 14.05
    if peso_g <= 200:   return 14.55
    if peso_g <= 300:   return 15.05
    if peso_g <= 400:   return 15.65
    if peso_g <= 500:   return 16.25
    if peso_g <= 750:   return 16.85
    if peso_g <= 1000:  return 17.45
    if peso_g <= 2000:  return 18.50
    if peso_g <= 5000:  return 22.00
    return 25.00 + math.ceil(max(0, peso_g - 5000) / 1000) * 2.50


def calcular_lucro(
    comissao: float,
    comissao_fixa: float,
    quantidade: float,
    preco_custo: float,
    frete: float,
    preco_venda: float,
    imposto: float,
    tarifa: float,
    desconto: float = 0.0,
    cashback: float = 0.0,
) -> float:
 
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

    valor_comissao = preco_efetivo * (comissao / 100)
    valor_imposto = preco_efetivo * (imposto / 100)
    custo_produto = preco_custo * quantidade

    return (
        preco_efetivo
        + cashback_valor
        - frete
        - valor_comissao
        - valor_imposto
        - comissao_fixa
        - tarifa
        - custo_produto
    )
