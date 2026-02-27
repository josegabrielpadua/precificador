import streamlit as st
from streamlit_option_menu import option_menu

from views import precificador, frete_magazine, ia

st.set_page_config(layout="wide")

with st.sidebar:
    selected = option_menu(
        "Menu Principal",
        ["Precificador", "Frete Magazine", "IA"],
        icons=["calculator-fill", "truck", "robot"],
        menu_icon="list",
        default_index=0,
    )

_PAGINAS = {
    "Precificador":   precificador.render,
    "Frete Magazine": frete_magazine.render,
    "IA":             ia.render,
}

pagina = _PAGINAS.get(selected)
if pagina:
    pagina()



