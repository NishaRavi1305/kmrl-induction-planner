# gen_samples.py
import os
import random
import pandas as pd
from datetime import datetime, timedelta

os.makedirs("data_samples", exist_ok=True)

def gen_train_ids(n):
    return [f"T{str(i+1).zfill(3)}" for i in range(n)]

def write_jobcards(train_ids, p_open=0.15):
    rows = []
    for t in train_ids:
        status = "Open" if random.random() < p_open else "Closed"
        rows.append({"train_id": t, "status": status})
    pd.DataFrame(rows).to_csv("data_samples/jobcards.csv", index=False)

def write_fitness(train_ids, pct_expired=0.1):
    rows = []
    today = datetime.now().date()
    for t in train_ids:
        # some expiry dates in past (expired), some future
        def rand_expiry(expired=False):
            if expired:
                days = -random.randint(1, 30)
            else:
                days = random.randint(7, 120)
            return (today + timedelta(days=days)).isoformat()
        expired_flag = random.random() < pct_expired
        rows.append({
            "train_id": t,
            "rolling_expiry": rand_expiry(expired_flag),
            "signalling_expiry": rand_expiry(expired_flag if random.random()<0.5 else False),
            "telecom_expiry": rand_expiry(expired_flag if random.random()<0.2 else False),
        })
    pd.DataFrame(rows).to_csv("data_samples/fitness.csv", index=False)

def write_cleaning(train_ids, p_needs=0.2):
    rows = []
    for t in train_ids:
        rows.append({
            "train_id": t,
            "needs_cleaning": "Yes" if random.random() < p_needs else "No"
        })
    pd.DataFrame(rows).to_csv("data_samples/cleaning.csv", index=False)

def write_mileage(train_ids, low=2000, high=20000, skew_high_pct=0.25):
    rows = []
    for t in train_ids:
        if random.random() < skew_high_pct:
            km = random.randint(int(high*0.8), high+5000)
        else:
            km = random.randint(low, int(high*0.8))
        rows.append({"train_id": t, "km_since_last_service": km})
    pd.DataFrame(rows).to_csv("data_samples/mileage.csv", index=False)

def write_branding(train_ids, pct_branding=0.25):
    rows = []
    campaigns = [f"B{str(i).zfill(2)}" for i in range(1, 10)]
    for t in train_ids:
        if random.random() < pct_branding:
            c = random.choice(campaigns)
            exposure = random.randint(2, 30)
            window_end = (datetime.now().date() + timedelta(days=random.randint(5,60))).isoformat()
            rows.append({"train_id": t, "campaign_id": c, "min_exposure_hours": exposure, "window_end": window_end})
        else:
            rows.append({"train_id": t, "campaign_id": "", "min_exposure_hours": "", "window_end": ""})
    pd.DataFrame(rows).to_csv("data_samples/branding.csv", index=False)

def write_stabling(train_ids, bays=10):
    rows = []
    for i, t in enumerate(train_ids):
        bay = f"Bay-{(i % bays) + 1}"
        rows.append({"train_id": t, "stabling_bay": bay})
    pd.DataFrame(rows).to_csv("data_samples/stabling.csv", index=False)

if __name__ == "__main__":
    # pick a size
    n_trains = 50   # change to 20, 100, etc.
    ids = gen_train_ids(n_trains)
    write_jobcards(ids, p_open=0.12)
    write_fitness(ids, pct_expired=0.12)
    write_cleaning(ids, p_needs=0.22)
    write_mileage(ids, low=2000, high=20000, skew_high_pct=0.28)
    write_branding(ids, pct_branding=0.3)
    write_stabling(ids, bays=12)
    print(f"Generated sample CSVs for {n_trains} trains in data_samples/")
