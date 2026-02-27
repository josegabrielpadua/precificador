def calcular_custo_nota_fiscal(
    quantidade: int,
    preco_custo: float,
    ipi: float,
    bonificacao: float = 0.0,
    bonificacao_porcentagem: float = 0.0,
) -> float:
    """
    Calcula o custo total de uma nota fiscal com IPI e bonificação.

    Args:
        quantidade: quantidade de itens comprados.
        preco_custo: preço unitário na NF (R$).
        ipi: IPI percentual (%).
        bonificacao: desconto em valor fixo total (R$).
        bonificacao_porcentagem: desconto percentual sobre o total de produtos (%).

    Returns:
        Valor total final da nota fiscal (R$).
    """
    if quantidade <= 0:
        return 0.0

    valor_total = preco_custo * quantidade
    valor_ipi = valor_total * (ipi / 100)

    if bonificacao > 0:
        return valor_total + valor_ipi - bonificacao

    if bonificacao_porcentagem > 0:
        valor_bonificado = valor_total * (bonificacao_porcentagem / 100)
        return valor_total + valor_ipi - valor_bonificado

    return valor_total + valor_ipi
