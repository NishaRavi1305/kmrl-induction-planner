import pandas as pd
from datetime import datetime, timedelta

def _days_to_earliest_expiry(fit_row, tomorrow):
    try:
        dates = [
            fit_row.get("rolling_expiry"),
            fit_row.get("signalling_expiry"),
            fit_row.get("telecom_expiry"),
        ]
        dates = [d.date() if pd.notna(d) else None for d in dates]
        future = [(d - tomorrow).days for d in dates if d is not None]
        return min(future) if future else None
    except Exception:
        return None

def _ml_predict(features_df, max_mileage):
    risk_scores = []
    labels = []
    try:
        from sklearn.ensemble import RandomForestClassifier
        import numpy as np

        X_syn = []
        y_syn = []

        # Low-risk
        for km in [1000, 3000, 5000, 7000]:
            for d in [15, 30, 60]:
                X_syn.append([km, d, 0, 0]); y_syn.append(0)
                X_syn.append([km, d, 1, 0]); y_syn.append(0)
        # Medium-risk
        for km in [max_mileage-500, max_mileage, max_mileage+200]:
            for d in [3, 7, 14]:
                X_syn.append([km, d, 0, 0]); y_syn.append(1)
                X_syn.append([km, d, 1, 0]); y_syn.append(1)
        # High-risk
        for km in [max_mileage+500, max_mileage+1500, max_mileage+3000]:
            for d in [-5, 0, 2]:
                X_syn.append([km, d, 1, 1]); y_syn.append(1)
                X_syn.append([km, d, 0, 1]); y_syn.append(1)

        X_syn = pd.DataFrame(X_syn, columns=["km", "days_to_expiry", "needs_cleaning", "jobcard_open"])
        y_syn = pd.Series(y_syn)

        rf = RandomForestClassifier(n_estimators=60, max_depth=6, random_state=42)
        rf.fit(X_syn, y_syn)

        feats = features_df.fillna({"days_to_expiry": 30})
        feats["needs_cleaning"] = feats["needs_cleaning"].astype(int)
        feats["jobcard_open"] = feats["jobcard_open"].astype(int)

        proba = rf.predict_proba(feats[["km","days_to_expiry","needs_cleaning","jobcard_open"]])[:,1]
        risk_scores = proba.tolist()

        for p in proba:
            if p >= 0.66:
                labels.append("⚠️ High Risk (Service Soon)")
            elif p >= 0.33:
                labels.append("△ Medium Risk")
            else:
                labels.append("✅ Low Risk")

        return risk_scores, labels

    except Exception:
        # Heuristic fallback
        for _, r in features_df.iterrows():
            km = r.get("km", 0) or 0
            dte = r.get("days_to_expiry", 30)
            needs_clean = int(r.get("needs_cleaning", 0) or 0)
            jc_open = int(r.get("jobcard_open", 0) or 0)

            risk = 0.0
            if km > max_mileage:
                over = min((km - max_mileage) / max(max_mileage,1), 1.5)
                risk += 0.45 * min(1.0, 0.2 + over)
            else:
                risk += 0.10 * (km / max(max_mileage,1))

            if dte is not None:
                if dte <= 0:
                    risk += 0.35
                elif dte <= 3:
                    risk += 0.25
                elif dte <= 7:
                    risk += 0.15
                else:
                    risk += 0.05

            risk += 0.06 * needs_clean
            risk += 0.22 * jc_open
            risk = max(0.0, min(1.0, risk))
            risk_scores.append(risk)

            if risk >= 0.66:
                labels.append("⚠️ High Risk (Service Soon)")
            elif risk >= 0.33:
                labels.append("△ Medium Risk")
            else:
                labels.append("✅ Low Risk")

        return risk_scores, labels


def run_optimizer(required_service:int, max_cleaning_slots:int=2, max_mileage:int=8000):
    try:
        jobcards = pd.read_csv("data_samples/jobcards.csv")
        fitness = pd.read_csv("data_samples/fitness.csv")
        cleaning = pd.read_csv("data_samples/cleaning.csv")
        mileage = pd.read_csv("data_samples/mileage.csv")

        try: pd.read_csv("data_samples/branding.csv")
        except: pass
        try: pd.read_csv("data_samples/stabling.csv")
        except: pass

        for col in ["rolling_expiry","signalling_expiry","telecom_expiry"]:
            fitness[col] = pd.to_datetime(fitness[col], errors="coerce")

        tomorrow = datetime.now().date() + timedelta(days=1)
        plan = []
        feature_rows = []
        trains = jobcards["train_id"].unique()
        cleaning_count = 0

        for t in trains:
            status = "Standby"
            reason = ""
            jc_rows = jobcards[jobcards["train_id"]==t]
            fit_rows = fitness[fitness["train_id"]==t]
            clean_rows = cleaning[cleaning["train_id"]==t]
            mil_rows = mileage[mileage["train_id"]==t]

            km_val = None
            dte_val = None
            needs_clean_flag = 0
            jc_open_flag = 0

            if jc_rows.empty or fit_rows.empty or clean_rows.empty or mil_rows.empty:
                status="IBL"
                reason="Missing data"
            else:
                jc = jc_rows.iloc[0]
                fit = fit_rows.iloc[0]
                clean = clean_rows.iloc[0]
                mil = mil_rows.iloc[0]

                km_val = int(mil.get("km_since_last_service",0)) if pd.notna(mil.get("km_since_last_service")) else None
                dte_val = _days_to_earliest_expiry(fit, tomorrow)
                needs_clean_flag = 1 if str(clean.get("needs_cleaning","")).lower()=="yes" else 0
                jc_open_flag = 1 if str(jc.get("status","")).lower()=="open" else 0

                if jc_open_flag==1:
                    status="IBL"
                    reason="Open jobcard"
                elif any([pd.notna(fit.get(col)) and fit[col].date()<tomorrow for col in ["rolling_expiry","signalling_expiry","telecom_expiry"]]):
                    status="IBL"
                    reason="Expired fitness certificate"
                elif km_val and km_val > max_mileage:
                    status="Standby"
                    reason=f"High mileage ({km_val} km)"
                elif needs_clean_flag==1:
                    if cleaning_count<max_cleaning_slots:
                        cleaning_count+=1
                        status="IBL"
                        reason="Cleaning slot assigned"
                    else:
                        status="Standby"
                        reason="Needs cleaning but no slot left"
                else:
                    reason="Healthy"

            plan.append({
                "train_id": t,
                "status": status,
                "reason": reason,
                "km_since_last_service": km_val,
                "Rakes Assigned": 1  # Default for demo; can be replaced with real allocation logic
            })

            feature_rows.append({
                "train_id": t,
                "km": km_val if km_val is not None else 0,
                "days_to_expiry": dte_val if dte_val is not None else 30,
                "needs_cleaning": needs_clean_flag,
                "jobcard_open": jc_open_flag
            })

        # Balanced mileage
        high_mileage_trains = [e for e in plan if e["km_since_last_service"] and e["km_since_last_service"]>max_mileage]
        num_to_promote = len(high_mileage_trains)//2
        for e in high_mileage_trains[:num_to_promote]:
            if e["status"]!="Service":
                e["status"]="Service"
                e["reason"]="Promoted for balanced mileage distribution"
        for e in high_mileage_trains[num_to_promote:]:
            if e["status"]!="Service":
                e["status"]="IBL"
                e["reason"]=f"Exceeded mileage threshold ({max_mileage} km)"

        # Promotion to meet required_service
        service_count = sum(1 for e in plan if e["status"]=="Service")
        for e in plan:
            if e["status"]=="Standby" and service_count<required_service:
                e["status"]="Service"
                e["reason"]="Promoted to meet service quota"
                service_count+=1

        # AI/ML inference
        features_df = pd.DataFrame(feature_rows)
        risk_scores, labels = _ml_predict(features_df, max_mileage)
        label_map = {row["train_id"]:(risk_scores[i],labels[i]) for i,row in enumerate(feature_rows)}
        for e in plan:
            score,label = label_map.get(e["train_id"],(None,None))
            e["AI_risk_score"]=round(float(score),3) if score is not None else None
            e["AI_recommendation"]=label if label else "N/A"

        return {"required_service": required_service, "plan": plan}

    except Exception as ex:
        return {"error": str(ex)}
