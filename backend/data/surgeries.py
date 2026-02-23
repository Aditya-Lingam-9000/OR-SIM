"""
backend/data/surgeries.py
Surgery type definitions and complete machine dictionaries for all 3 surgeries.

Machine dict structure:
    MACHINES[SurgeryType.X] = {
        <index: int>: {
            "name":        str   — exact canonical machine name (used as key everywhere)
            "description": str   — what the machine does during this surgery
            "aliases":     list  — common shorthand the doctor might say
                                   (used by MedGemma for fuzzy matching)
        }
    }
"""

from enum import Enum


class SurgeryType(Enum):
    HEART_TRANSPLANT = "Heart Transplantation"
    LIVER_RESECTION  = "Liver Resection"
    KIDNEY_PCNL      = "Kidney PCNL"

    def __str__(self) -> str:
        return self.value


# ─────────────────────────────────────────────────────────────────────────────
# HEART TRANSPLANTATION
# ─────────────────────────────────────────────────────────────────────────────
_HEART = {
    0: {
        "name":        "Patient Monitor",
        "description": "Continuously monitors ECG, arterial blood pressure, SpO2, "
                       "CVP, and core temperature throughout the transplant.",
        "aliases":     ["monitor", "vitals monitor", "cardiac monitor", "hemodynamic monitor"],
    },
    1: {
        "name":        "Ventilator",
        "description": "Provides controlled mechanical ventilation via endotracheal "
                       "tube during the procedure and until weaning post-transplant.",
        "aliases":     ["vent", "breathing machine", "mechanical ventilation"],
    },
    2: {
        "name":        "Anesthesia Machine",
        "description": "Delivers inhalational anesthetic agents (isoflurane/sevoflurane) "
                       "mixed with oxygen and air for general anesthesia maintenance.",
        "aliases":     ["anesthesia", "gas machine", "anaesthesia machine"],
    },
    3: {
        "name":        "Cardiopulmonary Bypass Machine",
        "description": "Takes over heart and lung function during cardiac arrest phase; "
                       "oxygenates and pumps blood through the patient's body.",
        "aliases":     ["bypass machine", "heart-lung machine", "CPB", "bypass pump", "pump"],
    },
    4: {
        "name":        "Perfusion Pump",
        "description": "Delivers cardioplegia solution to arrest the donor heart and "
                       "delivers preservative perfusate to maintain graft viability.",
        "aliases":     ["perfusion", "cardioplegia pump", "del nido pump"],
    },
    5: {
        "name":        "Defibrillator",
        "description": "Delivers electrical shocks to restore normal sinus rhythm "
                       "after reperfusion of the transplanted heart.",
        "aliases":     ["defib", "shock machine", "cardioverter"],
    },
    6: {
        "name":        "Electrocautery Unit",
        "description": "Provides monopolar and bipolar electrosurgical current for "
                       "cutting tissue and coagulating bleeding vessels.",
        "aliases":     ["cautery", "bovie", "electrosurgical unit", "ESU", "diathermy"],
    },
    7: {
        "name":        "Suction Device",
        "description": "Removes blood and fluids from the operative field to maintain "
                       "clear surgical visibility throughout the procedure.",
        "aliases":     ["suction", "suction machine", "aspirator"],
    },
    8: {
        "name":        "Blood Warmer",
        "description": "Warms transfused blood products to body temperature to prevent "
                       "hypothermia-induced coagulopathy.",
        "aliases":     ["blood warmer", "fluid warmer", "Ranger", "warming unit"],
    },
    9: {
        "name":        "Warming Blanket",
        "description": "Bair Hugger forced-air warming system maintains normothermia "
                       "during re-warming phase and sternal closure.",
        "aliases":     ["warming blanket", "bair hugger", "forced air warmer", "patient warmer"],
    },
    10: {
        "name":        "Surgical Lights",
        "description": "Overhead surgical LED lights provide shadow-free illumination "
                       "of the operative field.",
        "aliases":     ["lights", "OR lights", "overhead lights", "surgical lamp", "theatre lights"],
    },
    11: {
        "name":        "Instrument Table",
        "description": "Sterile back table and Mayo stand holding all surgical "
                       "instruments, sutures, and implants prepared by the scrub nurse.",
        "aliases":     ["instrument table", "back table", "mayo stand", "scrub table"],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# LIVER RESECTION
# ─────────────────────────────────────────────────────────────────────────────
_LIVER = {
    0: {
        "name":        "Patient Monitor",
        "description": "Monitors ECG, NIBP/ABP, SpO2, EtCO2, temperature and urine "
                       "output — critical during Pringle manoeuvre for liver ischaemia.",
        "aliases":     ["monitor", "vitals monitor", "hemodynamic monitor"],
    },
    1: {
        "name":        "Ventilator",
        "description": "Maintains mechanical ventilation; low tidal volumes plus low "
                       "PEEP strategy reduces hepatic venous pressure during resection.",
        "aliases":     ["vent", "breathing machine", "mechanical ventilation"],
    },
    2: {
        "name":        "Anesthesia Machine",
        "description": "Delivers total intravenous anesthesia (TIVA) or volatile agents; "
                       "isoflurane preferred for its hepatoprotective properties.",
        "aliases":     ["anesthesia", "gas machine", "anaesthesia machine"],
    },
    3: {
        "name":        "Electrocautery Unit",
        "description": "Monopolar and bipolar cautery for parenchymal transection and "
                       "vessel sealing during hepatectomy.",
        "aliases":     ["cautery", "bovie", "electrosurgical unit", "ESU", "diathermy"],
    },
    4: {
        "name":        "Argon Beam Coagulator",
        "description": "Uses ionised argon gas to conduct monopolar current across the "
                       "liver cut surface for rapid haemostasis without direct contact.",
        "aliases":     ["argon beam", "ABC", "argon coagulator", "ABC unit"],
    },
    5: {
        "name":        "Ultrasonic Dissector (CUSA)",
        "description": "Cavitron Ultrasonic Surgical Aspirator fragments and aspirates "
                       "liver parenchyma while sparing bile ducts and blood vessels.",
        "aliases":     ["CUSA", "ultrasonic dissector", "cavitron", "ultrasonic aspirator"],
    },
    6: {
        "name":        "Suction Device",
        "description": "Removes blood, bile, and irrigant from the operative field and "
                       "the CUSA dissection plume.",
        "aliases":     ["suction", "aspirator", "suction machine"],
    },
    7: {
        "name":        "Cell Saver",
        "description": "Autologous blood salvage system — collects shed blood, washes "
                       "and re-infuses red cells to reduce allogeneic transfusion.",
        "aliases":     ["cell saver", "autotransfusion", "cell salvage", "CATS"],
    },
    8: {
        "name":        "Fluid Warmer",
        "description": "Warms IV fluids and blood products inline to prevent "
                       "hypothermia during large-volume resuscitation.",
        "aliases":     ["fluid warmer", "blood warmer", "hot line", "level 1"],
    },
    9: {
        "name":        "Laparoscopy Tower",
        "description": "Provides HD video display for laparoscopic or hand-assisted "
                       "approach; includes camera unit, light source, and recorder.",
        "aliases":     ["laparoscopy tower", "lap tower", "video tower", "camera tower"],
    },
    10: {
        "name":        "CO2 Insufflator",
        "description": "Maintains pneumoperitoneum at 12–15 mmHg pressure for "
                       "laparoscopic liver resection.",
        "aliases":     ["insufflator", "CO2 insufflator", "pneumoperitoneum machine"],
    },
    11: {
        "name":        "Surgical Lights",
        "description": "Overhead LED surgical lights for open or hand-assisted "
                       "hepatic resection.",
        "aliases":     ["lights", "OR lights", "overhead lights", "surgical lamp"],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# KIDNEY PCNL (Percutaneous Nephrolithotomy)
# ─────────────────────────────────────────────────────────────────────────────
_KIDNEY_PCNL = {
    0: {
        "name":        "Patient Monitor",
        "description": "Monitors vitals in prone or supine position; SpO2 and "
                       "EtCO2 are critical due to prone-position ventilation risks.",
        "aliases":     ["monitor", "vitals monitor", "hemodynamic monitor"],
    },
    1: {
        "name":        "Fluoroscopy C-Arm",
        "description": "Real-time X-ray guidance for percutaneous renal access, "
                       "wire placement, tract dilation, and sheath positioning.",
        "aliases":     ["c-arm", "fluoroscopy", "x-ray", "image intensifier", "fluoro"],
    },
    2: {
        "name":        "Nephroscope Unit",
        "description": "Rigid nephroscope with light source and irrigation channel "
                       "for direct visualisation of the collecting system and stones.",
        "aliases":     ["nephroscope", "scope", "rigid scope", "nephroscopy unit"],
    },
    3: {
        "name":        "Lithotripsy Device",
        "description": "Pneumatic or ultrasonic lithotripter fragments kidney stones "
                       "inside the collecting system for irrigation and extraction.",
        "aliases":     ["lithotripsy", "lithotripter", "stone crusher", "EMS", "Swiss LithoClast"],
    },
    4: {
        "name":        "Irrigation Pump",
        "description": "Delivers pressurised saline irrigation through the nephroscope "
                       "sheath for stone clearance and field visibility.",
        "aliases":     ["irrigation pump", "pump", "saline pump", "pressure pump"],
    },
    5: {
        "name":        "Suction Device",
        "description": "Aspirates irrigant, stone fragments, and blood clots from "
                       "the collecting system during nephroscopy.",
        "aliases":     ["suction", "aspirator", "suction machine"],
    },
    6: {
        "name":        "Anesthesia Machine",
        "description": "Provides general or spinal/epidural anesthesia; prone "
                       "positioning demands careful airway and ventilator management.",
        "aliases":     ["anesthesia", "gas machine", "anaesthesia machine"],
    },
    7: {
        "name":        "Surgical Lights",
        "description": "Overhead surgical lights for the procedural field; often "
                       "reduced for fluoro visibility.",
        "aliases":     ["lights", "OR lights", "overhead lights", "surgical lamp"],
    },
    8: {
        "name":        "Electrocautery Unit",
        "description": "Used for access site haemostasis and any ancillary "
                       "open/laparoscopic steps during the procedure.",
        "aliases":     ["cautery", "bovie", "electrosurgical unit", "ESU"],
    },
    9: {
        "name":        "Contrast Injector",
        "description": "Power injector delivers contrast medium through ureteric "
                       "catheter for retrograde pyelogram to confirm access.",
        "aliases":     ["contrast injector", "contrast pump", "power injector", "pyelogram injector"],
    },
    10: {
        "name":        "Video Tower",
        "description": "Displays the nephroscope camera feed on HD monitor for surgeon "
                       "and team visualisation during endoscopic stone work.",
        "aliases":     ["video tower", "monitor tower", "endoscopy tower", "camera tower"],
    },
    11: {
        "name":        "Stone Retrieval System",
        "description": "Nitinol baskets and forceps passed through the nephroscope "
                       "working channel for stone fragment extraction.",
        "aliases":     ["stone basket", "retrieval system", "nitinol basket", "stone extractor"],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Master lookup
# ─────────────────────────────────────────────────────────────────────────────
MACHINES: dict[SurgeryType, dict[int, dict]] = {
    SurgeryType.HEART_TRANSPLANT: _HEART,
    SurgeryType.LIVER_RESECTION:  _LIVER,
    SurgeryType.KIDNEY_PCNL:      _KIDNEY_PCNL,
}


def get_machine_names(surgery: SurgeryType) -> list[str]:
    """Return ordered list of canonical machine names for a surgery."""
    return [v["name"] for v in MACHINES[surgery].values()]


def get_machine_by_name(surgery: SurgeryType, name: str) -> dict | None:
    """Look up a machine entry by canonical name (case-insensitive)."""
    name_lower = name.lower()
    for entry in MACHINES[surgery].values():
        if entry["name"].lower() == name_lower:
            return entry
    return None


def get_machines_formatted(surgery: SurgeryType) -> str:
    """
    Return a numbered text block of all machines + descriptions,
    formatted for injection into the MedGemma system prompt.

    Example:
        0. Patient Monitor — Continuously monitors ECG, ...
        1. Ventilator — Provides controlled mechanical ventilation ...
        ...
    """
    lines = []
    for idx, entry in MACHINES[surgery].items():
        lines.append(f"  {idx:2d}. {entry['name']} — {entry['description']}")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# CLI self-test
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    for stype in SurgeryType:
        names = get_machine_names(stype)
        print(f"\n{'='*60}")
        print(f"  {stype}  ({len(names)} machines)")
        print(f"{'='*60}")
        print(get_machines_formatted(stype))
