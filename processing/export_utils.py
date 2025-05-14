import pandas as pd

def generate_summary_sheet(data_frames: list[pd.DataFrame]) -> pd.DataFrame:
    """
    Regroupe tous les résultats par temps (en secondes)
    et calcule les moyennes pour chaque seconde.

    Args:
        data_frames (list): Liste de DataFrames contenant les résultats des vidéos.

    Returns:
        pd.DataFrame: Tableau des moyennes par temps.
    """
    # Fusionner toutes les données
    all_data = pd.concat(data_frames, ignore_index=True)

    # Créer un dictionnaire pour stocker les données par temps
    grouped_data = {}

    for _, row in all_data.iterrows():
        temps = int(round(row["temps[sec]"]))
        if temps not in grouped_data:
            grouped_data[temps] = {
                "nb_bulles": [],
                "surface_moyenne[cm²]": [],
                "ecart_type[cm²]": []
            }
        grouped_data[temps]["nb_bulles"].append(row["nb_bulles"])
        grouped_data[temps]["surface_moyenne[cm²]"].append(row["surface_moyenne[cm²]"])
        grouped_data[temps]["ecart_type[cm²]"].append(row["ecart_type[cm²]"])

    # Calculer les moyennes pour chaque temps
    summary_rows = []
    for temps, mesures in sorted(grouped_data.items()):
        summary_rows.append({
            "temps[sec]": temps,
            "nb_bulles": sum(mesures["nb_bulles"]) / len(mesures["nb_bulles"]),
            "surface_moyenne[cm²]": sum(mesures["surface_moyenne[cm²]"]) / len(mesures["surface_moyenne[cm²]"]),
            "ecart_type[cm²]": sum(mesures["ecart_type[cm²]"]) / len(mesures["ecart_type[cm²]"]),
        })

    return pd.DataFrame(summary_rows)
