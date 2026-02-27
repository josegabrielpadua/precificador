from io import BytesIO
import pandas as pd


def to_excel(df: pd.DataFrame) -> bytes:
    """Converte um DataFrame para bytes de arquivo .xlsx."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    return output.getvalue()
