"""
Medico HMS — Import Medical Codes Management Command
Imports ICD-10 and CPT code datasets from JSON files.

Usage:
    python manage.py import_medical_codes --type icd10 --file data/icd10_codes.json
    python manage.py import_medical_codes --type cpt --file data/cpt_codes.json
    python manage.py import_medical_codes --seed  # Load sample data for development
"""

import json
import logging

from django.core.management.base import BaseCommand

from apps.codes.models import CPTCode, ICD10Code

logger = logging.getLogger("apps.codes")

# Sample ICD-10 codes for development
SAMPLE_ICD10_CODES = [
    {"code": "A00", "description": "Cholera", "category": "Certain infectious and parasitic diseases", "chapter": "I"},
    {"code": "A09", "description": "Infectious gastroenteritis and colitis, unspecified", "category": "Intestinal infectious diseases", "chapter": "I"},
    {"code": "B20", "description": "Human immunodeficiency virus [HIV] disease", "category": "HIV disease", "chapter": "I"},
    {"code": "C34.1", "description": "Malignant neoplasm of upper lobe, bronchus or lung", "category": "Malignant neoplasms", "chapter": "II"},
    {"code": "C50.9", "description": "Malignant neoplasm of breast, unspecified", "category": "Malignant neoplasms", "chapter": "II"},
    {"code": "D50.9", "description": "Iron deficiency anemia, unspecified", "category": "Nutritional anemias", "chapter": "III"},
    {"code": "E11.9", "description": "Type 2 diabetes mellitus without complications", "category": "Diabetes mellitus", "chapter": "IV"},
    {"code": "E11.65", "description": "Type 2 diabetes mellitus with hyperglycemia", "category": "Diabetes mellitus", "chapter": "IV"},
    {"code": "E78.5", "description": "Dyslipidemia, unspecified", "category": "Metabolic disorders", "chapter": "IV"},
    {"code": "F32.9", "description": "Major depressive disorder, single episode, unspecified", "category": "Mood disorders", "chapter": "V"},
    {"code": "F41.1", "description": "Generalized anxiety disorder", "category": "Anxiety disorders", "chapter": "V"},
    {"code": "G43.9", "description": "Migraine, unspecified", "category": "Episodic and paroxysmal disorders", "chapter": "VI"},
    {"code": "I10", "description": "Essential (primary) hypertension", "category": "Hypertensive diseases", "chapter": "IX"},
    {"code": "I21.9", "description": "Acute myocardial infarction, unspecified", "category": "Ischemic heart diseases", "chapter": "IX"},
    {"code": "I25.10", "description": "Atherosclerotic heart disease of native coronary artery", "category": "Ischemic heart diseases", "chapter": "IX"},
    {"code": "I48.91", "description": "Unspecified atrial fibrillation", "category": "Other cardiac arrhythmias", "chapter": "IX"},
    {"code": "I50.9", "description": "Heart failure, unspecified", "category": "Heart failure", "chapter": "IX"},
    {"code": "J06.9", "description": "Acute upper respiratory infection, unspecified", "category": "Acute upper respiratory infections", "chapter": "X"},
    {"code": "J18.9", "description": "Pneumonia, unspecified organism", "category": "Pneumonia", "chapter": "X"},
    {"code": "J44.1", "description": "Chronic obstructive pulmonary disease with acute exacerbation", "category": "COPD", "chapter": "X"},
    {"code": "J45.20", "description": "Mild intermittent asthma, uncomplicated", "category": "Asthma", "chapter": "X"},
    {"code": "K21.0", "description": "Gastro-esophageal reflux disease with esophagitis", "category": "Diseases of esophagus", "chapter": "XI"},
    {"code": "K35.80", "description": "Unspecified acute appendicitis", "category": "Diseases of appendix", "chapter": "XI"},
    {"code": "K80.20", "description": "Calculus of gallbladder without cholecystitis", "category": "Cholelithiasis", "chapter": "XI"},
    {"code": "M54.5", "description": "Low back pain", "category": "Dorsalgia", "chapter": "XIII"},
    {"code": "N18.3", "description": "Chronic kidney disease, stage 3", "category": "Renal tubulo-interstitial diseases", "chapter": "XIV"},
    {"code": "N39.0", "description": "Urinary tract infection, site not specified", "category": "Other disorders of urinary system", "chapter": "XIV"},
    {"code": "R07.9", "description": "Chest pain, unspecified", "category": "Symptoms involving circulatory system", "chapter": "XVIII"},
    {"code": "R50.9", "description": "Fever, unspecified", "category": "General symptoms and signs", "chapter": "XVIII"},
    {"code": "S72.001A", "description": "Fracture of unspecified part of neck of right femur, initial encounter", "category": "Injuries to hip and thigh", "chapter": "XIX"},
    {"code": "Z00.00", "description": "Encounter for general adult medical examination without abnormal findings", "category": "General examination", "chapter": "XXI"},
    {"code": "Z23", "description": "Encounter for immunization", "category": "Immunization", "chapter": "XXI"},
]

# Sample CPT codes for development
SAMPLE_CPT_CODES = [
    {"code": "99201", "description": "Office or other outpatient visit, new patient, straightforward", "category": "Evaluation and Management", "rvu": "0.93"},
    {"code": "99202", "description": "Office visit, new patient, low complexity", "category": "Evaluation and Management", "rvu": "1.60"},
    {"code": "99203", "description": "Office visit, new patient, moderate complexity", "category": "Evaluation and Management", "rvu": "2.60"},
    {"code": "99204", "description": "Office visit, new patient, moderate to high complexity", "category": "Evaluation and Management", "rvu": "3.50"},
    {"code": "99205", "description": "Office visit, new patient, high complexity", "category": "Evaluation and Management", "rvu": "4.56"},
    {"code": "99211", "description": "Office visit, established patient, minimal", "category": "Evaluation and Management", "rvu": "0.18"},
    {"code": "99212", "description": "Office visit, established patient, straightforward", "category": "Evaluation and Management", "rvu": "0.93"},
    {"code": "99213", "description": "Office visit, established patient, low complexity", "category": "Evaluation and Management", "rvu": "1.30"},
    {"code": "99214", "description": "Office visit, established patient, moderate complexity", "category": "Evaluation and Management", "rvu": "1.92"},
    {"code": "99215", "description": "Office visit, established patient, high complexity", "category": "Evaluation and Management", "rvu": "2.80"},
    {"code": "99221", "description": "Initial hospital inpatient care, straightforward/low", "category": "Hospital Inpatient", "rvu": "2.20"},
    {"code": "99222", "description": "Initial hospital inpatient care, moderate", "category": "Hospital Inpatient", "rvu": "3.07"},
    {"code": "99223", "description": "Initial hospital inpatient care, high complexity", "category": "Hospital Inpatient", "rvu": "4.08"},
    {"code": "99281", "description": "Emergency department visit, self-limited", "category": "Emergency Department", "rvu": "0.45"},
    {"code": "99285", "description": "Emergency department visit, high severity", "category": "Emergency Department", "rvu": "4.00"},
    {"code": "36415", "description": "Collection of venous blood by venipuncture", "category": "Surgery", "rvu": "0.17"},
    {"code": "71046", "description": "Radiologic examination, chest, 2 views", "category": "Radiology", "rvu": "0.70"},
    {"code": "74177", "description": "CT abdomen and pelvis with contrast", "category": "Radiology", "rvu": "2.89"},
    {"code": "80048", "description": "Basic metabolic panel", "category": "Pathology/Laboratory", "rvu": "0.00"},
    {"code": "80053", "description": "Comprehensive metabolic panel", "category": "Pathology/Laboratory", "rvu": "0.00"},
    {"code": "85025", "description": "Complete blood count (CBC) with differential WBC", "category": "Pathology/Laboratory", "rvu": "0.00"},
    {"code": "81001", "description": "Urinalysis, automated, with microscopy", "category": "Pathology/Laboratory", "rvu": "0.00"},
    {"code": "93000", "description": "Electrocardiogram, routine, with interpretation", "category": "Medicine", "rvu": "0.70"},
    {"code": "90471", "description": "Immunization administration", "category": "Medicine", "rvu": "0.17"},
]


class Command(BaseCommand):
    help = "Import medical codes (ICD-10, CPT) from JSON files or seed sample data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--type",
            type=str,
            choices=["icd10", "cpt"],
            help="Type of codes to import",
        )
        parser.add_argument(
            "--file",
            type=str,
            help="Path to JSON file containing the codes",
        )
        parser.add_argument(
            "--seed",
            action="store_true",
            help="Load sample/seed data for development",
        )

    def handle(self, *args, **options):
        if options["seed"]:
            self._seed_data()
            return

        code_type = options.get("type")
        file_path = options.get("file")

        if not code_type or not file_path:
            self.stderr.write(
                self.style.ERROR("Please specify --type and --file, or use --seed")
            )
            return

        with open(file_path) as f:
            data = json.load(f)

        if code_type == "icd10":
            self._import_icd10(data)
        elif code_type == "cpt":
            self._import_cpt(data)

    def _seed_data(self):
        """Load sample medical codes for development."""
        self.stdout.write("Seeding ICD-10 codes...")
        icd10_objects = []
        for item in SAMPLE_ICD10_CODES:
            icd10_objects.append(
                ICD10Code(
                    code=item["code"],
                    description=item["description"],
                    category=item.get("category", ""),
                    chapter=item.get("chapter", ""),
                )
            )

        # Use update_or_create pattern for idempotency
        created_count = 0
        for obj in icd10_objects:
            _, created = ICD10Code.objects.update_or_create(
                code=obj.code,
                defaults={
                    "description": obj.description,
                    "category": obj.category,
                    "chapter": obj.chapter,
                },
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"  ✅ {created_count} ICD-10 codes created, {len(icd10_objects) - created_count} updated")
        )

        self.stdout.write("Seeding CPT codes...")
        cpt_created = 0
        for item in SAMPLE_CPT_CODES:
            _, created = CPTCode.objects.update_or_create(
                code=item["code"],
                defaults={
                    "description": item["description"],
                    "category": item.get("category", ""),
                    "rvu": item.get("rvu") if item.get("rvu") else None,
                },
            )
            if created:
                cpt_created += 1

        self.stdout.write(
            self.style.SUCCESS(f"  ✅ {cpt_created} CPT codes created, {len(SAMPLE_CPT_CODES) - cpt_created} updated")
        )

        self.stdout.write(self.style.SUCCESS("\n🎉 Sample medical codes loaded successfully!"))

    def _import_icd10(self, data):
        """Import ICD-10 codes from JSON data."""
        self.stdout.write(f"Importing {len(data)} ICD-10 codes...")
        created_count = 0
        for item in data:
            _, created = ICD10Code.objects.update_or_create(
                code=item["code"],
                defaults={
                    "description": item.get("description", ""),
                    "category": item.get("category", ""),
                    "chapter": item.get("chapter", ""),
                    "is_billable": item.get("is_billable", True),
                },
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"✅ Imported {created_count} new ICD-10 codes")
        )

    def _import_cpt(self, data):
        """Import CPT codes from JSON data."""
        self.stdout.write(f"Importing {len(data)} CPT codes...")
        created_count = 0
        for item in data:
            _, created = CPTCode.objects.update_or_create(
                code=item["code"],
                defaults={
                    "description": item.get("description", ""),
                    "category": item.get("category", ""),
                    "rvu": item.get("rvu"),
                },
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"✅ Imported {created_count} new CPT codes")
        )
