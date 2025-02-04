import tkinter as tk
from tkinter import messagebox, ttk
import os
import requests
import yfinance as yf  # Installera med: pip install yfinance

# Lista över aktier
AKTIER = ["Ericsson", "Electrolux", "AstraZeneca"]
FUNDAMENTA_FILE = "fundamenta.txt"
KURSER_FILE = "kurser.txt"
OMX_FILE = "omx.txt"

# Hämtar fundamentala data från fil
def läs_fundamenta():
    data = {}
    if not os.path.exists(FUNDAMENTA_FILE):
        messagebox.showerror("Fel", "Filen fundamenta.txt saknas!")
        return data
    with open(FUNDAMENTA_FILE, "r", encoding="utf-8") as f:
        lines = f.read().strip().split("\n")
        for i in range(0, len(lines), 4):
            namn = lines[i]
            soliditet = lines[i+1]
            pe = lines[i+2]
            ps = lines[i+3]
            data[namn] = {"soliditet": soliditet, "pe": pe, "ps": ps}
    return data

# Hämtar kurser från fil
def läs_kurser():
    data = {}
    if not os.path.exists(KURSER_FILE):
        messagebox.showerror("Fel", "Filen kurser.txt saknas!")
        return data
    with open(KURSER_FILE, "r", encoding="utf-8") as f:
        aktie = None
        for line in f:
            line = line.strip()
            if line in AKTIER:
                aktie = line
                data[aktie] = []
            else:
                try:
                    data[aktie].append(float(line.split()[1]))
                except:
                    continue
    return data

# Hämtar OMX-index från fil
def läs_omx():
    data = []
    if not os.path.exists(OMX_FILE):
        messagebox.showerror("Fel", "Filen omx.txt saknas!")
        return data
    with open(OMX_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data.append(float(line.split()[1]))
            except:
                continue
    return data

# Webbscraping: Hämta aktiekurser från Yahoo Finance
def hämta_aktiekurs(aktie):
    aktie_tickers = {
        "Ericsson": "ERIC",
        "Electrolux": "ELUX-B.ST",
        "AstraZeneca": "AZN.L"
    }
    ticker = aktie_tickers.get(aktie)
    if not ticker:
        return None
    try:
        aktie_data = yf.Ticker(ticker)
        kurs = aktie_data.history(period="1d")["Close"].iloc[-1]
        return round(kurs, 2)
    except:
        return None

# Fundamental analys
def fundamental_analys():
    aktie = aktie_var.get()
    data = läs_fundamenta()
    if aktie in data:
        result = f"Soliditet: {data[aktie]['soliditet']}%\nP/E-tal: {data[aktie]['pe']}\nP/S-tal: {data[aktie]['ps']}"
    else:
        result = "Ingen data hittades."
    messagebox.showinfo(f"Fundamental analys - {aktie}", result)

# Teknisk analys
def teknisk_analys():
    aktie = aktie_var.get()
    kurser = läs_kurser()
    omx = läs_omx()
    
    if aktie not in kurser or len(kurser[aktie]) < 2 or len(omx) < 2:
        messagebox.showerror("Fel", "Ej tillräckligt med data.")
        return

    start = kurser[aktie][0]
    slut = hämta_aktiekurs(aktie) or kurser[aktie][-1]
    avkastning = (slut / start) - 1

    start_omx = omx[0]
    slut_omx = omx[-1]
    avkastning_omx = (slut_omx / start_omx) - 1

    betavärde = avkastning / avkastning_omx if avkastning_omx != 0 else 0
    högsta = max(kurser[aktie])
    lägsta = min(kurser[aktie])

    result = f"Kursutveckling: {round(avkastning * 100, 2)}%\nBetavärde: {round(betavärde, 2)}\nHögsta kurs: {högsta}\nLägsta kurs: {lägsta}"
    messagebox.showinfo(f"Teknisk analys - {aktie}", result)

# Rangordna aktier efter betavärde
def rangordna_aktier():
    kurser = läs_kurser()
    omx = läs_omx()
    betavärden = {}

    for aktie, kurs in kurser.items():
        if len(kurs) < 2 or len(omx) < 2:
            continue
        start = kurs[0]
        slut = hämta_aktiekurs(aktie) or kurs[-1]
        avkastning = (slut / start) - 1
        avkastning_omx = (omx[-1] / omx[0]) - 1
        betavärde = avkastning / avkastning_omx if avkastning_omx != 0 else 0
        betavärden[aktie] = round(betavärde, 2)

    sorted_aktier = sorted(betavärden.items(), key=lambda x: x[1], reverse=True)
    result = "\n".join([f"{i+1}. {aktie} - {beta}" for i, (aktie, beta) in enumerate(sorted_aktier)])
    messagebox.showinfo("Rangordning av aktier", result)

# GUI
def skapa_gui():
    global aktie_var
    root = tk.Tk()
    root.title("Aktieanalys")

    tk.Label(root, text="Välj aktie:").pack(pady=5)
    aktie_var = tk.StringVar(root)
    aktie_var.set(AKTIER[0])
    aktie_dropdown = ttk.Combobox(root, textvariable=aktie_var, values=AKTIER, state="readonly")
    aktie_dropdown.pack(pady=5)

    tk.Button(root, text="Fundamental analys", command=fundamental_analys).pack(pady=5)
    tk.Button(root, text="Teknisk analys", command=teknisk_analys).pack(pady=5)
    tk.Button(root, text="Rangordna aktier", command=rangordna_aktier).pack(pady=5)
    tk.Button(root, text="Avsluta", command=root.quit).pack(pady=10)

    root.mainloop()

# Starta GUI
if __name__ == "__main__":
    skapa_gui()