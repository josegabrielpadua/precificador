from __future__ import annotations

from typing import Callable

import streamlit as st

MAX_ITERACOES = 200_000
STEP = 0.01


def encontrar_preco_otimo(
    preco_inicial: float,
    margem_desejada: float,
    calcular_lucro: Callable[[float], float],
    calcular_margem: Callable[[float, float], float],
    desconto: float = 0.0,
) -> tuple[float, float, float]:

    preco = preco_inicial
    lucro = calcular_lucro(preco)
    margem = calcular_margem(lucro, preco)
    iteracoes = 0

    if margem < margem_desejada:
        while margem < margem_desejada and iteracoes < MAX_ITERACOES:
            preco += STEP
            lucro = calcular_lucro(preco)
            margem = calcular_margem(lucro, preco)
            iteracoes += 1

    elif margem > margem_desejada:
        while margem > margem_desejada and iteracoes < MAX_ITERACOES:
            preco -= STEP
            if preco <= STEP:
                preco = STEP
                break
            lucro = calcular_lucro(preco)
            margem = calcular_margem(lucro, preco)
            iteracoes += 1

        # Correção de overshooting
        if margem < margem_desejada and preco > STEP:
            preco += STEP
            lucro = calcular_lucro(preco)
            margem = calcular_margem(lucro, preco)

    if iteracoes >= MAX_ITERACOES:
        st.warning(
            f"Não foi possível encontrar o preço ideal em {MAX_ITERACOES} iterações. "
            "O preço/margem pode estar instável ou inatingível."
        )

    preco_sugerido = round(preco, 2)
    lucro_sugerido = calcular_lucro(preco_sugerido)
    preco_efetivo = preco_sugerido * (1 - desconto / 100)
    margem_sugerida = calcular_margem(lucro_sugerido, preco_sugerido)

    return preco_sugerido, lucro_sugerido, margem_sugerida
