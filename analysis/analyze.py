#!/usr/bin/env python3
"""Аналіз CSV-телеметрії QGroundControl (лаб. робота №7, варіант 9).

Використання:
    python3 analysis/analyze.py "telemetry/2026-10-21 23-01-13 vehicle1.csv"
    python3 analysis/analyze.py FILE.csv --start 800 --end 1150   # ручний діапазон рядків

Результат (у results/): graph1_altitude.png, graph2_airspeed.png,
graph3_groundspeed.png, table_7_4.md, flight_segment.csv
Залежності: pandas, numpy, matplotlib
"""
import argparse, math, os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---- Параметри варіанта 9 ----
H, V = 35.0, 4.0
TARGET = (-35.3624857, 149.1642559)

def find_col(df, names, required=True):
    """Знайти стовпець за списком можливих назв (точний збіг, без урахування регістру)."""
    low = {c.lower(): c for c in df.columns}
    for n in names:
        if n.lower() in low:
            return low[n.lower()]
    if required:
        sys.exit(f"Не знайдено стовпець {names}. Доступні стовпці:\n" + ", ".join(df.columns))
    return None

def parse_hms(series):
    """'00:05:45' -> секунди; число -> число."""
    td = pd.to_timedelta(series.astype(str), errors="coerce")
    num = pd.to_numeric(series, errors="coerce")
    return td.dt.total_seconds().fillna(num).fillna(0)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(a))

def _blocks(active):
    blocks, i = [], 0
    while i < len(active):
        if active[i]:
            j = i
            while j + 1 < len(active) and active[j + 1]:
                j += 1
            blocks.append((i, j)); i = j + 1
        else:
            i += 1
    return blocks

def pick_segment(df, alt, ft):
    """Останній політ, де набрано ~H.
    1) за лічильником flightTime (росте між arm і disarm, після посадки завмирає);
    2) запасний варіант - за висотою > 0.3 м."""
    a = pd.to_numeric(df[alt], errors="coerce").fillna(0)
    candidates = []
    if ft is not None:
        f = parse_hms(df[ft])
        grow = (f.diff().fillna(0) > 0).to_numpy()
        grow = grow | np.roll(grow, -1)          # додати рядок arm (перед першим приростом)
        candidates.append(grow)
    candidates.append((a > 0.3).to_numpy())
    for k, active in enumerate(candidates):
        good = [b for b in _blocks(active) if a.iloc[b[0]:b[1]+1].max() >= 0.9*H]
        if good:
            i0, i1 = good[-1]
            if not (ft is not None and k == 0):
                i0 = max(0, i0 - 3); i1 = min(len(df) - 1, i1 + 10)
            return i0, i1
    print("Автоматично політ не знайдено.")
    print(f"Макс. висота у файлі ({alt}): {a.max():.2f}; рядків з висотою > {0.9*H:.0f} м: {(a >= 0.9*H).sum()}")
    sys.exit("Задайте --start/--end вручну або надішліть цей вивід.")

def shade(ax, t_takeoff, t_land, tmax):
    ax.axvspan(0, t_takeoff, color="#cfe2ff", alpha=.7, label="Зліт")
    ax.axvspan(t_takeoff, t_land, color="#d4edda", alpha=.7, label="Горизонтальний політ")
    ax.axvspan(t_land, tmax, color="#ffe5d0", alpha=.7, label="Посадка")

def plot(t, y, ylabel, title, label, color, ref, ref_label, ph, path):
    fig, ax = plt.subplots(figsize=(9, 4.5))
    shade(ax, *ph, t.max())
    ax.plot(t, y, color=color, lw=2, label=label)
    if ref is not None:
        ax.axhline(ref, color="red", ls="--", lw=1, label=ref_label)
    ax.set_xlim(0, t.max()); ax.set_xlabel("Час від arm, с"); ax.set_ylabel(ylabel)
    ax.set_title(title); ax.grid(alpha=.3); ax.legend(loc="best", fontsize=8)
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results"))
    ap.add_argument("--start", type=int); ap.add_argument("--end", type=int)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    df = pd.read_csv(a.csv, low_memory=False)
    print(f"Рядків: {len(df)}, стовпців: {df.shape[1]}")
    alt  = find_col(df, ["altitudeRelative", "altitude_relative"])
    asp  = find_col(df, ["airSpeed", "airspeed"])
    gsp  = find_col(df, ["groundSpeed", "groundspeed"])
    lat  = find_col(df, ["gps.lat", "latitude"])
    lon  = find_col(df, ["gps.lon", "longitude"])
    roll = find_col(df, ["roll"], False)
    pitch = find_col(df, ["pitch"], False)
    ft   = find_col(df, ["flightTime"], False)
    amsl = find_col(df, ["altitudeAMSL"], False)
    mode = find_col(df, ["flightMode"], False)
    arm  = find_col(df, ["armed"], False)
    for c in (alt, asp, gsp, lat, lon, roll, pitch, amsl):
        if c: df[c] = pd.to_numeric(df[c], errors="coerce")

    if a.start is not None and a.end is not None:
        i0, i1 = a.start, a.end
    else:
        i0, i1 = pick_segment(df, alt, ft)
    seg = df.iloc[i0:i1+1].reset_index(drop=True)
    seg.to_csv(os.path.join(a.out, "flight_segment.csv"), index=False)

    # Час від arm: за Timestamp, якщо є, інакше 1 запис = 1 с
    ts = find_col(seg, ["Timestamp"], False)
    t = None
    if ts:
        try:
            tt = pd.to_datetime(seg[ts]); t = (tt - tt.iloc[0]).dt.total_seconds().to_numpy()
        except Exception:
            t = None
    if t is None or t.max() <= 0:
        t = np.arange(len(seg), dtype=float)
    t = pd.Series(t)

    alts = seg[alt]
    near = alts >= 0.98*H
    t_takeoff = float(t[near.idxmax()])                 # досягнення ~H
    t_land = float(t[near[::-1].idxmax()])              # останній момент на ~H
    ph = (t_takeoff, t_land)

    cruise = seg[(t > t_takeoff + 25) & (t < t_land - 20)]
    mean_cruise = cruise[gsp].mean()
    d_target = haversine(seg[lat].iloc[-1], seg[lon].iloc[-1], *TARGET)
    modes = ", ".join(map(str, seg[mode].dropna().unique())) if mode else "Auto (за QGC; у CSV поля режиму немає)"
    armtxt = "disarmed → armed → disarmed"
    if arm:
        armtxt = f"{seg[arm].iloc[0]} → {seg[arm].iloc[len(seg)//2]} → {seg[arm].iloc[-1]}"

    rows = [
        ("Час зльоту", f"≈ {t_takeoff:.0f} с від arm до досягнення {H:.0f} м"),
        ("Найбільша висота", f"{alts.max():.1f} м (відносна)" + (f"; {seg[amsl].max():.1f} м AMSL" if amsl else "")),
        ("Найбільша швидкість", f"{seg[gsp].max():.2f} м/с (наземна), {seg[asp].max():.2f} м/с (повітряна)"),
        ("Середня швидкість на крейсері", f"{mean_cruise:.2f} м/с (відхилення {abs(mean_cruise-V)/V*100:.1f} %)"),
        ("Час польоту", f"{t.iloc[-1]:.0f} с ({int(t.iloc[-1]//60)} хв {int(t.iloc[-1]%60)} с)"),
        ("Початкова координата", f"{seg[lat].iloc[0]:.7f}; {seg[lon].iloc[0]:.7f}"),
        ("Кінцева координата", f"{seg[lat].iloc[-1]:.7f}; {seg[lon].iloc[-1]:.7f}"),
        ("Відстань кінця польоту до цілі", f"{d_target:.2f} м"),
    ]
    if roll:  rows.append(("Максимальний roll", f"{seg[roll].abs().max():.1f}° (на {t[seg[roll].abs().idxmax()]:.0f} с)"))
    if pitch: rows.append(("Максимальний pitch", f"{seg[pitch].abs().max():.1f}°"))
    rows += [("Режими польоту", modes), ("Стан arm до та після місії", armtxt)]

    md = "| Показник | Значення |\n|---|---|\n" + "\n".join(f"| {k} | {v} |" for k, v in rows)
    open(os.path.join(a.out, "table_7_4.md"), "w", encoding="utf-8").write(md + "\n")
    print("\n" + md)
    print(f"\nЕтапи: зліт 0–{t_takeoff:.0f} с, горизонтальний {t_takeoff:.0f}–{t_land:.0f} с, посадка {t_land:.0f}–{t.max():.0f} с")
    print(f"Сегмент: рядки {i0}–{i1} (для ручного керування: --start {i0} --end {i1})")

    plot(t, alts, "Висота, м", "Відносна висота від часу", "Висота (altitudeRelative)", "blue",
         H, f"Задана H = {H:.0f} м", ph, os.path.join(a.out, "graph1_altitude.png"))
    plot(t, seg[asp], "Швидкість, м/с", "Повітряна швидкість від часу", "Повітряна (airSpeed)", "green",
         V, f"Задана V = {V:.0f} м/с", ph, os.path.join(a.out, "graph2_airspeed.png"))
    plot(t, seg[gsp], "Швидкість, м/с", "Наземна швидкість від часу", "Наземна (groundSpeed)", "purple",
         V, f"Задана V = {V:.0f} м/с", ph, os.path.join(a.out, "graph3_groundspeed.png"))
    print("Графіки та таблицю збережено в", os.path.abspath(a.out))

if __name__ == "__main__":
    main()
