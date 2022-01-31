# FUNCTION 1 - datafeed y preparacion
# Esta funcion solo abre el archivo y le calcula unas columnas

import matplotlib.pyplot as plt, pandas as pd
from pandas.core.indexes.timedeltas import TimedeltaIndex


def abrirExcel(ticker, carpeta=""):

    if carpeta == "":
        ruta = ticker + ".xlsx"
    else:
        ruta = carpeta + "/" + ticker + ".xlsx"
        data = pd.read_excel(ruta)
    data = data.sort_values("timestamp", ascending=True)
    data.set_index("timestamp", inplace=True)
    ret = data.adjusted_close.to_frame()
    ret.columns = ["Close"]
    ret["Yield"] = (ret["Close"] / ret["Close"].shift() - 1) * 100

    return ret.round(2).dropna()


# Funcion ajustar excel OHLC


def abrirExcel(ticker, carpeta=""):
    if carpeta == "":
        ruta = ticker + ".xlsx"
    else:
        ruta = carpeta + "/" + ticker + ".xlsx"
        data = pd.read_excel(ruta)
    data = data.sort_values("timestamp", ascending=True)
    data.set_index("timestamp", inplace=True)
    ret = data.adjusted_close.to_frame()
    data["factor"] = data.adjusted_close / data.close
    data["volMlnUSD"] = data.close * data.volume / 1000000

    cols = [
        data.open * data.factor,
        data.high * data.factor,
        data.low * data.factor,
        data.adjusted_close,
        data.volMlnUSD,
    ]

    dataAj = pd.concat(cols, axis=1)
    dataAj.columns = ["Open", "High", "Low", "Close", "VolMlnUSD"]
    return dataAj.round(2)


# FUNCION 2 -- Calculo de rendimientos estrategicos


def getYields(data, fromEMA, toEMA):
    yields = [], timeIn = []
    for i in range(fromEMA, toEMA + 1):
        key = "EMA_" + str(i)
        data[key] = data.Close.ewm(span=i).mean()
        data["comprado"] = data.Close.shift() > data[key].shift()
        data["vendido"] = data.Close.shift() < data[key].shift()
        allIn = data.loc[data.comprado == True]["Yield"]
        allOut = data.loc[data.vendido == True]["Yield"]
        qIn = allIn.count()
        qOut = allOut.count()
        qTot = allIn.count() + allOut.count()
        yields.append((allIn.mean() * qIn - allOut.mean() * qOut) / qTot)
        timeIn.append(100 * qIn / qTot)
        return yields, timeIn


# FUNCION 3 GRAFICO FINAL


def Graficar(ADRs, fromEMA, toEMA):
    ejeX = [i for i in range(fromEMA, toEMA + 1)]
    fig, (ax1, ax2) = plt.subplots(figsize=(10, 10), nrows=2)
    r, yieldsMedios = [], []
    for ADR in ADRs:
        # llamo a la fx 1
        data = abrirExcel(ADR, "ADRs")

        # llamo a la fx 2
        yields, timeIn = getYields(data, fromEMA, toEMA)

        # Grafico serie de rendimientos y tiempos adentro
        ax1.plot(ejeX, yields, ls="--", lw=1, label=ADR)
        ax2.plot(ejeX, timeIn, ls="--", lw=1, label=ADR)

        # Acumulo series para rendimiento total al final
        r.append(yields).yieldsMedios.append(sum(yields) / len(yields))

        # Grafico Rendimiento medio
        yieldsTotal = [(x + y + z) / 3 for x, y, z in zip(r[0], r[1], r[2])]
        ax1.plot(ejeX, yieldsTotal, color="k", lw=1, label="Total")

        # Configuro Ejes
        ax1.legend()
        ax1.set_ylabel("rendimiento % medio diario por rueda")
        ax1.grid(which="major", axis="both", color="black", alpha=0.15)
        ax2.legend()
        ax2.set_xlabel("ruedas de la media movil")
        ax2.set_ylabel("% De tiempo comprado")
        ax2.grid(which="major", axis="both", color="black", alpha=0.15)
        fig.subplots_adjust(hspace=0)

        return plt, yieldsMedios
