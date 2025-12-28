import tkinter as tk
from tkinter import ttk, messagebox

# ---------- TEMA ----------
BG = "#0f0f0f"
PANEL = "#1c1c1c"
FG = "#eaeaea"
GREEN = "#4CAF50"
ORANGE = "#FF9800"
RED = "#f44336"
BLUE = "#2196F3"

# ---------- YARDIMCI FONKSİYONLAR ----------
def parse_score(score):
    try:
        a, b = score.split("-")
        return int(a), int(b)
    except:
        return None

def points(gf, ga):
    if gf > ga: return 3
    if gf == ga: return 1
    return 0

def risk_label(support):
    if support >= 4: return "🟢 Düşük"
    elif support >= 2: return "🟡 Orta"
    else: return "🔴 Yüksek"

def create_scrollable_frame(parent):
    canvas = tk.Canvas(parent, bg=PANEL, highlightthickness=0)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg=PANEL)
    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    return scroll_frame

# ---------- ANALİZ VE YENİ PENCERE ----------
def analyze():
    home_scores, away_scores = [], []
    home_gf, home_ga = [], []
    away_gf, away_ga = [], []
    kg_home = kg_away = 0
    over25 = 0
    iy_home_0_5 = 0
    iy_home_kg = 0
    iy_away_0_5 = 0
    iy_away_kg = 0

    try:
        # Veri Toplama
        for i in range(5):
            iy_s = parse_score(home_first_half_entries[i].get().strip())
            full_s = parse_score(home_entries[i].get().strip())
            if iy_s is None or full_s is None: raise ValueError
            gf_iy, ga_iy = iy_s
            gf, ga = full_s
            w = 1.5 if i >= 2 else 1
            home_scores.append(points(gf, ga) * w)
            home_gf.append(gf); home_ga.append(ga)
            if gf>0 and ga>0: kg_home +=1
            if gf+ga>=3: over25 +=1
            if gf_iy+ga_iy>0: iy_home_0_5 +=1
            if gf_iy>0 and ga_iy>0: iy_home_kg +=1

        for i in range(5):
            iy_s = parse_score(away_first_half_entries[i].get().strip())
            full_s = parse_score(away_entries[i].get().strip())
            if iy_s is None or full_s is None: raise ValueError
            gf_iy, ga_iy = iy_s[1], iy_s[0]
            gf, ga = full_s[1], full_s[0]
            away_scores.append(points(gf, ga))
            away_gf.append(gf); away_ga.append(ga)
            if gf>0 and ga_iy>0: kg_away +=1
            if gf+ga>=3: over25 +=1
            if gf_iy+ga_iy>0: iy_away_0_5 +=1
            if gf_iy>0 and ga_iy>0: iy_away_kg +=1
    except ValueError:
        messagebox.showerror("Hata", "Tüm skorları '2-1' formatında eksiksiz giriniz.")
        return

    # --- Hesaplamalar ---
    home_form, away_form = sum(home_scores), sum(away_scores)
    diff = home_form - away_form
    home_goal_avg, away_goal_avg = sum(home_gf)/5, sum(away_gf)/5
    home_concede_avg, away_concede_avg = sum(home_ga)/5, sum(away_ga)/5
    tempo = (home_goal_avg + away_goal_avg + home_concede_avg + away_concede_avg)/2

    # --- Profil Belirleme ---
    if tempo >=2.8 and over25 >=5: profile, pcolor = "🔥 AÇIK OYUN", RED
    elif diff>=4 and tempo<2.4: profile, pcolor = "🟢 FAVORİ – KONTROLLÜ", GREEN
    elif tempo<2.2 and over25<=3: profile, pcolor = "🧊 KISIR MAÇ", BLUE
    else: profile, pcolor = "⚠️ RİSKLİ / DENGESİZ", ORANGE

    # --- Market Verileri ---
    tekli_markets = {
        "MS1": risk_label(home_form/3), "MSX": risk_label((5-abs(diff))/2),
        "MS2": risk_label(away_form/3), "1.5 Üst": risk_label(over25/2),
        "2.5 Üst": risk_label(over25/1.5), "KG Var": risk_label((kg_home+kg_away)/2),
        "İY 0.5 Üst": risk_label((iy_home_0_5+iy_away_0_5)/2)
    }

    # --- SONUÇ PENCERESİ (TOPLEVEL) ---
    res_win = tk.Toplevel(root)
    res_win.title("Analiz Sonuçları")
    res_win.geometry("500x600")
    res_win.configure(bg=BG)

    tk.Label(res_win, text=profile, font=("Arial", 18, "bold"), bg=BG, fg=pcolor, pady=15).pack()

    style = ttk.Style()
    style.configure('TNotebook', background=BG)
    tabs = ttk.Notebook(res_win)
    tabs.pack(expand=1, fill="both", padx=10, pady=10)

    # Sekme İçeriklerini Doldurma Fonksiyonu
    def fill_tab(tab_obj, data, is_risk=True):
        container = create_scrollable_frame(tab_obj)
        for k, v in data.items():
            color = FG
            if is_risk:
                color = GREEN if "🟢" in v else ORANGE if "🟡" in v else RED
            tk.Label(container, text=f"{k} → {v}", font=("Arial", 12), bg=PANEL, fg=color, anchor="w", pady=5).pack(fill="x")

    # Sekmeleri Oluştur
    t1 = tk.Frame(tabs, bg=PANEL); tabs.add(t1, text="Tekli Marketler")
    t2 = tk.Frame(tabs, bg=PANEL); tabs.add(t2, text="Kombinasyonlar")
    t3 = tk.Frame(tabs, bg=PANEL); tabs.add(t3, text="Olası Skorlar")

    # Verileri Doldur
    fill_tab(t1, tekli_markets)
    
    # Skorlar ve Kombinasyonlar (Basit hesaplama örneği)
    ev_e = round((home_goal_avg + away_concede_avg)/2)
    dep_e = round((away_goal_avg + home_concede_avg)/2)
    skorlar = {f"{ev_e}-{dep_e}": "En Yüksek Olasılık", f"{ev_e+1}-{dep_e}": "Alternatif", f"{ev_e}-{dep_e+1}": "Sürpriz"}
    fill_tab(t3, skorlar, is_risk=False)

# ---------- ANA GUI ----------
root = tk.Tk()
root.title("Bahis Asistanı Veri Girişi")
root.geometry("800x700")
root.configure(bg=BG)

tk.Label(root, text="MAÇ VERİLERİNİ GİRİNİZ", font=("Arial", 18, "bold"), bg=BG, fg=FG, pady=20).pack()

main_frame = tk.Frame(root, bg=BG)
main_frame.pack()

def create_input_area(parent, title):
    frame = tk.LabelFrame(parent, text=title, bg=PANEL, fg=FG, padx=20, pady=10)
    entries, iy_entries = [], []
    for i in range(5):
        tk.Label(frame, text=f"{i+1}. Maç (İY / MS)", bg=PANEL, fg="#bbb", font=("Arial", 9)).pack()
        row = tk.Frame(frame, bg=PANEL)
        row.pack(pady=2)
        e_iy = tk.Entry(row, width=6, justify="center", bg="#3a3a3a", fg=FG)
        e_iy.insert(0, "0-0")
        e_iy.pack(side="left", padx=2)
        e_ms = tk.Entry(row, width=6, justify="center", bg="#2a2a2a", fg=FG, font=("Arial", 10, "bold"))
        e_ms.insert(0, "0-0")
        e_ms.pack(side="left", padx=2)
        iy_entries.append(e_iy); entries.append(e_ms)
    return frame, entries, iy_entries

home_ui, home_entries, home_first_half_entries = create_input_area(main_frame, "Ev Sahibi Son 5")
home_ui.grid(row=0, column=0, padx=20)

away_ui, away_entries, away_first_half_entries = create_input_area(main_frame, "Deplasman Son 5")
away_ui.grid(row=0, column=1, padx=20)

tk.Button(root, text="ANALİZ ET VE SONUÇLARI AÇ", font=("Arial", 14, "bold"), 
          bg=GREEN, fg="white", padx=20, pady=10, command=analyze).pack(pady=30)

root.mainloop()
