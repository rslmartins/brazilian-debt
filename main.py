import pandas as pd
import matplotlib.pyplot as plt
from itertools import cycle
from matplotlib import colormaps as cm
import numpy as np


# Define presidential terms with start and end dates and president names
def ext_to_date(data):
    data = data.rstrip().lstrip()
    if data!="atualidade":
        data = data.replace(" de ","/")
        meses = {"janeiro":"01", "fevereiro":"02", r"março":"03", "abril":"04", 
                 "maio":"05", "junho": "06", "julho":"07", "agosto": "08", 
                 "setembro":"09", "outubro":"10", "novembro":"11", "dezembro":"12"}
        for x in meses.keys():
            if x in data:
                data=data.replace(x,meses[x])
        data = data.replace("º", "").replace("°", "")
        return pd.to_datetime(data, dayfirst=True).date()
    elif data=="atualidade":
        return pd.Timestamp.now().date()

def plot(title:str, yaxis_title: str, debt_column: str, logy: bool, pdf_file: str) -> None:
        # Create a figure and axis
        fig, ax = plt.subplots()

        # Set the title of the plot and its y label
        plt.title(title)
        plt.ylabel(yaxis_title)

        # Convert the index to datetime
        df_gdp_debt.index = pd.to_datetime(df_gdp_debt.index)

        # Plot a log plot
        df_gdp_debt[debt_column].plot(logy=logy, ax=ax, label="", color="white")

        # Get a colormap and create an iterator for it
        cmap = cm.get_cmap("tab20b")
        colors = cycle(cmap.colors)

        # Add shaded regions for presidential terms and labels with distinct colors
        for start, end, president in presidential_terms:
                color = next(colors)
                ax.axvspan(start, end, alpha=1.0, color=color, label=president)

        # Set the legend
        ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))

        # Save the plot to a PDF file
        plt.savefig(pdf_file, bbox_inches="tight")

        # Show the plot
        plt.show()

# Vectorized function of the function ext_to_date
vectorized_ext_to_date = np.vectorize(ext_to_date)

# Acquire political data
tables = pd.read_html("https://pt.wikipedia.org/wiki/Lista_de_presidentes_do_Brasil")
df_presidents = tables[0]
df_presidents.columns = ["_".join(col) for col in df_presidents.columns]
df_presidents.columns = [col.split("_")[0] for col in df_presidents.columns]
df_presidents.rename({"Período do mandato (duração do mandato)": "Duração do mandato"}, axis=1, inplace=True)
df_presidents = df_presidents.loc[:,["Duração do mandato","Presidente"]]
df_presidents = df_presidents.loc[(~df_presidents["Duração do mandato"].str.contains("Eleito", na=False)) &
                                  (~df_presidents["Presidente"].str.contains("República", na=False)) &
                                  (~df_presidents["Presidente"].str.contains("Junta", na=False))]
df_presidents["Duração do mandato"] = df_presidents["Duração do mandato"].str.split("(")
df_presidents["Duração do mandato"] = df_presidents["Duração do mandato"].str[0].str.split("–")
df_presidents[["Início", "Fim"]] = pd.DataFrame(df_presidents["Duração do mandato"].tolist(), index=df_presidents.index)
df_presidents = df_presidents.drop("Duração do mandato", axis=1)
df_presidents["Início"] = vectorized_ext_to_date(df_presidents["Início"])
df_presidents["Fim"] = vectorized_ext_to_date(df_presidents["Fim"])
df_presidents = df_presidents.drop_duplicates()

# Acquire financial data
df_debt = pd.read_html("http://www.ipeadata.gov.br/ExibeSerie.aspx?serid=38367", decimal=",", thousands=".")[2]
df_gdp = pd.read_html("http://www.ipeadata.gov.br/ExibeSerie.aspx?serid=31973", decimal=",", thousands=".")[2]

# Remove the first row
df_debt.drop([0], axis=0, inplace=True)
df_gdp.drop([0], axis=0, inplace=True)

# Rename columns
df_debt.rename({0: "", 1: "Dívida em US$ (bilhões)"}, axis=1, inplace=True)
df_gdp.rename({0: "", 1: "PIB em US$ (milhões)"}, axis=1, inplace=True)

# Data as index
df_debt = df_debt.set_index("")
df_gdp = df_gdp.set_index("")

# Align political data with financial data chronologically, and then classify presidents according to that timeline
first_year = df_debt.index[0]
first_date = pd.Timestamp(f"01/01/{first_year}").date()
df_presidents = df_presidents.loc[(df_presidents['Início'] <= first_date) & (df_presidents['Fim'] >= first_date) |
                                  (df_presidents['Início'] >= first_date), :]
presidential_terms = [(row["Início"],row["Fim"],row["Presidente"]) for index, row in df_presidents.iterrows()]

# Transform columns into float
df_debt["Dívida em US$ (bilhões)"] = df_debt["Dívida em US$ (bilhões)"].astype(float)
df_gdp["PIB em US$ (milhões)"] = df_gdp["PIB em US$ (milhões)"].astype(float)

# Create a new dataframe called df_gdp_debt with a new column stating the debt as percentage
df_gdp_debt = pd.merge(df_gdp, df_debt, left_index=True, right_index=True)
df_gdp_debt["Dívida/PIB"] = (df_gdp_debt["Dívida em US$ (bilhões)"] * 1_000 ) / df_gdp_debt["PIB em US$ (milhões)"] * 100                
print(df_gdp_debt.loc[df_gdp_debt["Dívida/PIB"]==max(df_gdp_debt["Dívida/PIB"]), :])
plot("Relação da dívida externa bruta do Brasil \n em relação ao seu PIB", "%", "Dívida/PIB", False, "relative-debt.pdf")
plot("Dívida externa bruta brasileira", "US$ (bilhões)", "Dívida em US$ (bilhões)", True, "absolute-debt.pdf")

