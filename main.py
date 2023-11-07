import pandas as pd
import matplotlib.pyplot as plt
from itertools import cycle
from matplotlib.cm import get_cmap

# Acquire data
df = pd.read_html("http://www.ipeadata.gov.br/ExibeSerie.aspx?serid=38367")[2]

# Remove the first row
df.drop([0], axis=0, inplace=True)

# Rename columns
df.rename({0: "", 1: "Dívida em US$ (bilhões)"}, axis=1, inplace=True)

# Data as index
df = df.set_index("")

# Debt into int
df["Dívida em US$ (bilhões)"] = df["Dívida em US$ (bilhões)"].apply(lambda x: int(x))

# Define presidential terms with start and end dates and president names
# https://pt.wikipedia.org/wiki/Lista_de_presidentes_do_Brasil
presidential_terms = [
(pd.to_datetime("1950-01-01"), pd.to_datetime("1951-01-31"), "Eurico Gaspar Dutra"),
(pd.to_datetime("1951-01-31"), pd.to_datetime("1954-08-24"), "Getúlio Vargas"),
(pd.to_datetime("1954-08-24"), pd.to_datetime("1956-01-31"), "Café Filho/Carlos Luz/Nereu Ramos"),
(pd.to_datetime("1956-01-31"), pd.to_datetime("1961-01-31"), "Juscelino Kubitschek"),
(pd.to_datetime("1961-01-31"), pd.to_datetime("1961-08-25"), "Jânio Quadros"),
(pd.to_datetime("1961-09-07"), pd.to_datetime("1964-04-02"), "João Goulart"),
(pd.to_datetime("1964-04-15"), pd.to_datetime("1967-03-15"), "Humberto Castello Branco"),
(pd.to_datetime("1967-03-15"), pd.to_datetime("1969-08-31"), "Arthur Costa e Silva"),
(pd.to_datetime("1969-10-30"), pd.to_datetime("1974-03-15"), "Emílio Médici"),
(pd.to_datetime("1974-03-15"), pd.to_datetime("1979-03-15"), "Ernesto Geisel"),
(pd.to_datetime("1979-03-15"), pd.to_datetime("1985-03-15"), "João Figueiredo"),
(pd.to_datetime("1985-03-15"), pd.to_datetime("1990-03-15"), "José Sarney"),
(pd.to_datetime("1990-03-15"), pd.to_datetime("1992-12-29"), "Fernando Collor"),
(pd.to_datetime("1992-12-29"), pd.to_datetime("1995-01-01"), "Itamar Franco"),
(pd.to_datetime("1995-01-01"), pd.to_datetime("2003-01-01"), "Fernando Henrique Cardoso"),
(pd.to_datetime("2003-01-01"), pd.to_datetime("2011-01-01"), "Lula da Silva"),
(pd.to_datetime("2011-01-01"), pd.to_datetime("2016-08-31"), "Dilma Rousseff"),
(pd.to_datetime("2016-09-01"), pd.to_datetime("2019-01-01"), "Michel Temer"),
(pd.to_datetime("2019-01-01"), pd.to_datetime("2022-12-31"), "Jair Bolsonaro")]

# Create a figure and axis
fig, ax = plt.subplots()

# Set the title of the plot and its y label
plt.title("Dívida externa bruta brasileira")
plt.ylabel("US$ (bilhões)")

# Convert the index to datetime
df.index = pd.to_datetime(df.index)

# Plot a log plot
df["Dívida em US$ (bilhões)"].plot(logy=True, ax=ax, label="", color="white")

# Get a colormap and create an iterator for it
cmap = get_cmap("tab20b")
colors = cycle(cmap.colors)

# Add shaded regions for presidential terms and labels with distinct colors
for start, end, president in presidential_terms:
    color = next(colors)
    ax.axvspan(start, end, alpha=1.0, color=color, label=president)

# Set the legend
ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))

# Save the plot to a PDF file
plt.savefig("img.pdf", bbox_inches="tight")

# Show the plot
plt.show()
