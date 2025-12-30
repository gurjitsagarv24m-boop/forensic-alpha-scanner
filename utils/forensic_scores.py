import pandas as pd


# -------------------------------------------------
# Sloan Accrual (year-wise)
# -------------------------------------------------
def sloan_accrual_series(df: pd.DataFrame) -> pd.Series:
    results = {}

    for year, row in df.iterrows():
        net_income = row.get("net_income", 0)
        cfo = row.get("operating_cash_flow", row.get("cfo", 0))
        total_assets = row.get("total_assets", 0)

        if total_assets == 0:
            results[year] = None
        else:
            results[year] = round((net_income - cfo) / total_assets, 4)

    return pd.Series(results, name="Sloan Accrual")


# -------------------------------------------------
# Beneish M-Score (rolling, t vs t-1)
# -------------------------------------------------
import numpy as np
import pandas as pd

def beneish_m_score_series(pivot: pd.DataFrame) -> pd.Series:
    scores = {}
    years = pivot.index.tolist()

    for i in range(1, len(years)):
        y, py = years[i], years[i - 1]
        t = pivot.loc[y]
        pt = pivot.loc[py]

        try:
            # --- Required ---
            sales = t["revenue"]
            prev_sales = pt["revenue"]

            assets = t["total_assets"]
            cfo = t.get("operating_cash_flow", np.nan)
            ni = t["net_income"]

            if assets == 0 or prev_sales == 0:
                scores[y] = np.nan
                continue

            # --- TATA (always computable in your data) ---
            tata = (ni - cfo) / assets

            # --- SGI ---
            sgi = sales / prev_sales

            # --- GMI (fallback using gross profit if available) ---
            if "gross_profit" in t and "gross_profit" in pt:
                gmi = (pt["gross_profit"] / prev_sales) / (t["gross_profit"] / sales)
            else:
                gmi = 1  # neutral fallback

            # --- Simplified Beneish (academically acceptable) ---
            m_score = (
                -4.84
                + 0.92 * tata
                + 0.528 * gmi
                + 0.404 * sgi
            )

            scores[y] = round(m_score, 3)

        except Exception:
            scores[y] = np.nan

    return pd.Series(scores, name="Beneish M-Score")



# -------------------------------------------------
# Piotroski F-Score (year-wise)
# -------------------------------------------------
def piotroski_f_score_series(df: pd.DataFrame) -> pd.Series:
    results = {}

    years = df.index.tolist()

    for i in range(1, len(years)):
        t = df.loc[years[i]]
        t1 = df.loc[years[i - 1]]

        score = 0

        # Profitability
        score += int(t.get("net_income", 0) > 0)
        score += int(t.get("operating_cash_flow", 0) > 0)

        roa_t = t.get("net_income", 0) / max(t.get("total_assets", 1), 1)
        roa_t1 = t1.get("net_income", 0) / max(t1.get("total_assets", 1), 1)
        score += int(roa_t > roa_t1)

        score += int(
            t.get("operating_cash_flow", 0) > t.get("net_income", 0)
        )

        # Leverage & liquidity
        score += int(
            t.get("long_term_debt", 0) <
            t1.get("long_term_debt", 0)
        )

        cr_t = t.get("current_assets", 0) / max(t.get("current_liabilities", 1), 1)
        cr_t1 = t1.get("current_assets", 0) / max(t1.get("current_liabilities", 1), 1)
        score += int(cr_t > cr_t1)

        # Efficiency
        gm_t = t.get("gross_profit", 0) / max(t.get("revenue", 1), 1)
        gm_t1 = t1.get("gross_profit", 0) / max(t1.get("revenue", 1), 1)
        score += int(gm_t > gm_t1)

        at_t = t.get("revenue", 0) / max(t.get("total_assets", 1), 1)
        at_t1 = t1.get("revenue", 0) / max(t1.get("total_assets", 1), 1)
        score += int(at_t > at_t1)

        results[years[i]] = score

    return pd.Series(results, name="Piotroski F-Score")


# -------------------------------------------------
# Altman Z-Score (year-wise)
# -------------------------------------------------
def altman_z_score_series(df: pd.DataFrame) -> pd.Series:
    results = {}

    for year, t in df.iterrows():
        total_assets = t.get("total_assets", 0)
        total_liabilities = t.get("total_liabilities", 0)

        if total_assets == 0 or total_liabilities == 0:
            results[year] = None
            continue

        working_capital = (
            t.get("current_assets", 0) -
            t.get("current_liabilities", 0)
        )

        retained_earnings = t.get(
            "retained_earnings",
            t.get("shareholders_equity", 0)
        )

        x1 = working_capital / total_assets
        x2 = retained_earnings / total_assets
        x3 = t.get("ebit", 0) / total_assets
        x4 = t.get("shareholders_equity", 0) / total_liabilities
        x5 = t.get("revenue", 0) / total_assets

        z = 1.2*x1 + 1.4*x2 + 3.3*x3 + 0.6*x4 + 1.0*x5
        results[year] = round(z, 2)

    return pd.Series(results, name="Altman Z-Score")
