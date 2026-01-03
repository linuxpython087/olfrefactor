import pandas as pd
from contenu.core.infrastructure.model_region_pays import Country, Region
from django.core.management.base import BaseCommand
from django.db import transaction

FILE_PATH = "./contenu/data/Repartition-Regions-Pays-OLF.xlsx"


class Command(BaseCommand):
    help = "Import regions and countries from OLF Excel file"

    def handle(self, *args, **options):
        self.stdout.write("📥 Lecture du fichier Excel...")

        df = pd.read_excel(FILE_PATH)

        # ============================
        # NORMALISATION DES COLONNES
        # ============================
        df.columns = (
            df.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("-", "_")
        )

        self.stdout.write(f"📊 Colonnes détectées : {list(df.columns)}")

        # ============================
        # VALIDATION STRUCTURE
        # ============================
        required_cols = {
            "code_iso",
            "nom_pays_olf",
            "olf_regions",
            "continent",
        }

        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Colonnes manquantes: {missing}")

        # ============================
        # NETTOYAGE DES DONNÉES
        # ============================
        df = df.dropna(subset=["code_iso", "olf_regions", "continent"])
        df["code_iso"] = df["code_iso"].astype(str).str.strip()
        df["olf_regions"] = df["olf_regions"].astype(str).str.strip()
        df["continent"] = df["continent"].astype(str).str.strip()
        df["nom_pays_olf"] = df["nom_pays_olf"].astype(str).str.strip()

        # ============================
        # IMPORT
        # ============================
        with transaction.atomic():

            # -------- REGIONS --------
            self.stdout.write("🌍 Import des régions...")

            regions_map = {}

            region_df = df[["olf_regions", "continent"]].drop_duplicates()

            for _, row in region_df.iterrows():
                region, _ = Region.objects.get_or_create(
                    name=row["olf_regions"],
                    continent=row["continent"],
                )

                regions_map[(row["olf_regions"], row["continent"])] = region

            # -------- COUNTRIES --------
            self.stdout.write("🏳️ Import des pays...")

            existing_codes = set(Country.objects.values_list("code_iso", flat=True))

            countries_to_create = []

            for _, row in df.iterrows():
                code = row["code_iso"]

                if not code or code in existing_codes:
                    continue

                region = regions_map.get((row["olf_regions"], row["continent"]))

                if not region:
                    continue

                countries_to_create.append(
                    Country(
                        code_iso=code,
                        name=row["nom_pays_olf"],
                        region=region,
                    )
                )

            Country.objects.bulk_create(countries_to_create, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS("✅ Import régions & pays terminé"))
