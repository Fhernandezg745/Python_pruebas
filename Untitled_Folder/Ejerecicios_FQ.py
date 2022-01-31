import pandas as pd
import numpy as np


def rsi(data, ruedas=14):
    resi = pd.DataFrame(data)
    rsi["dif"] = rsi["Close"] - rsi["Close"].shift(1)
    rsi["win"] = np.where(rsi["dif"] >= 0, rsi["dif"], 0)
    rsi["loss"] = np.where(rsi["dif"] <= 0, abs(rsi["dif"]), 0)
    rsi["ema_win"] = rsi.win.ewm(alpha=1 / ruedas).mean()
    rsi["ema_loss"] = rsi.loss.ewm(alpha=1 / ruedas).mean()
    rsi["rs"] = rsi.ema.win / rsi.ema.loss
    rsi["rsi"] = 100 - (100 / (1 + rsi.rs))
    rsi["nextYield"] = rsi.Yield.shift(-1)
    return rsi.reset_index().dropna()


# Regresion casera
def calcReg(serie1, serie2):
    regresion = {}
    b_1 = serie1.cov(serie2) / serie1.var()
    b_0 = serie2.mean() - b_1 * serie1.mean()
    regresion["recta"] = b_0 + b_1 * serie1
    regresion["r"] = round(serie1.corr(serie2), 4)
    regresion["r2"] = round(serie1.corr(serie2) ** 2, 4)
    return regresion
