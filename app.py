import json
import os
import pandas as pd
import streamlit as st

DATA_FILE = "mes_notes.json"

COEFF_MATIERES = {
    "Maths": 16,
    "NSI": 16,
    "Phy-Chimie": 16,
    "Français": 10,
    "Hist-Géo": 6,
    "Espagnol": 6,
    "ES": 6,
    "Anglais": 6,
    "EPS": 6,
    "EMC": 2,
    "SEA": 2,
}


def charger_donnees():
  if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  return {matiere: [] for matiere in COEFF_MATIERES}


def sauvegarder_donnees(donnees):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(donnees, f, ensure_ascii=False, indent=2)


st.set_page_config(
    page_title="Calculateur de Moyenne", page_icon="🎓", layout="centered"
)

st.title("🎓 Mon Suivi de Notes")

donnees = charger_donnees()

# Calcul des moyennes
total_points = 0
total_coeffs = 0
moyennes_matieres = {}

for matiere, coeff_mat in COEFF_MATIERES.items():
  notes = donnees.get(matiere, [])
  if notes:
    somme_notes = sum(n["note"] * n["coeff_eval"] for n in notes)
    somme_coeffs = sum(n["coeff_eval"] for n in notes)
    moy = somme_notes / somme_coeffs
    moyennes_matieres[matiere] = moy
    total_points += moy * coeff_mat
    total_coeffs += coeff_mat
  else:
    moyennes_matieres[matiere] = None

moy_generale = (total_points / total_coeffs) if total_coeffs > 0 else 0.0

st.metric(
    label="Moyenne Générale",
    value=f"{moy_generale:.2f} / 20" if total_coeffs > 0 else "N/A",
)

st.divider()

# Formulaire d'ajout
st.subheader("➕ Ajouter une note")
with st.form("form_ajout", clear_on_submit=True):
  col1, col2, col3 = st.columns([2, 1, 1])
  with col1:
    matiere_choisie = st.selectbox("Matière", list(COEFF_MATIERES.keys()))
  with col2:
    note_saisie = st.number_input(
        "Note (/20)",
        min_value=0.0,
        max_value=20.0,
        step=0.25,
        value=10.0,
        format="%.2f",
    )
  with col3:
    coef_saisie = st.number_input(
        "Coef devoir",
        min_value=0.01,
        max_value=10.0,
        step=0.05,
        value=1.0,
        format="%.2f",
    )

  valider = st.form_submit_button("Enregistrer la note")
  if valider:
    donnees[matiere_choisie].append(
        {"note": note_saisie, "coeff_eval": coef_saisie}
    )
    sauvegarder_donnees(donnees)
    st.success("Note ajoutée !")
    st.rerun()

st.divider()

# Vue en onglets
tab1, tab2 = st.tabs(["📊 Bilan des matières", "✏️ Modifier / Supprimer"])

with tab1:
  df_data = []
  for mat, moy in moyennes_matieres.items():
    nb_notes = len(donnees.get(mat, []))
    df_data.append({
        "Matière": mat,
        "Moyenne": f"{moy:.2f}" if moy is not None else "-",
        "Coef Matière": COEFF_MATIERES[mat],
        "Nombre de notes": nb_notes,
    })
  st.dataframe(pd.DataFrame(df_data), use_container_width=True)

with tab2:
  st.subheader("Gérer les notes enregistrées")
  mat_gestion = st.selectbox(
      "Matière à modifier", list(COEFF_MATIERES.keys()), key="sup_mat"
  )
  notes_mat = donnees.get(mat_gestion, [])

  if not notes_mat:
    st.info("Aucune note enregistrée dans cette matière.")
  else:
    for idx, n in enumerate(notes_mat):
      with st.expander(
          f"Note n°{idx+1} : {n['note']}/20 (Coef {n['coeff_eval']})"
      ):
        c_note, c_coef = st.columns(2)
        with c_note:
          nouvelle_note = st.number_input(
              "Note",
              min_value=0.0,
              max_value=20.0,
              value=float(n["note"]),
              step=0.25,
              key=f"edit_note_{mat_gestion}_{idx}",
          )
        with c_coef:
          nouveau_coef = st.number_input(
              "Coef",
              min_value=0.01,
              max_value=10.0,
              value=float(n["coeff_eval"]),
              step=0.05,
              key=f"edit_coef_{mat_gestion}_{idx}",
          )

        btn_mod, btn_sup = st.columns(2)
        with btn_mod:
          if st.button("💾 Sauvegarder", key=f"save_{mat_gestion}_{idx}"):
            donnees[mat_gestion][idx] = {
                "note": nouvelle_note,
                "coeff_eval": nouveau_coef,
            }
            sauvegarder_donnees(donnees)
            st.success("Note mise à jour !")
            st.rerun()

        with btn_sup:
          if st.button("❌ Supprimer", key=f"del_{mat_gestion}_{idx}"):
            donnees[mat_gestion].pop(idx)
            sauvegarder_donnees(donnees)
            st.warning("Note supprimée !")
            st.rerun()
