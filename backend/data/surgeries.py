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
    HEART_TRANSPLANT       = "Heart Transplantation"
    LIVER_RESECTION        = "Liver Resection"
    KIDNEY_PCNL            = "Kidney PCNL"
    CABG                   = "Coronary Artery Bypass Grafting"
    APPENDECTOMY           = "Appendectomy"
    CHOLECYSTECTOMY        = "Laparoscopic Cholecystectomy"
    HIP_REPLACEMENT        = "Total Hip Replacement"
    KNEE_REPLACEMENT       = "Total Knee Replacement"
    CAESAREAN_SECTION      = "Caesarean Section"
    SPINAL_FUSION          = "Spinal Fusion"
    CATARACT_SURGERY       = "Cataract Surgery"
    HYSTERECTOMY           = "Hysterectomy"
    THYROIDECTOMY          = "Thyroidectomy"
    COLECTOMY              = "Colectomy"
    PROSTATECTOMY          = "Radical Prostatectomy"
    CRANIOTOMY             = "Craniotomy"
    MASTECTOMY             = "Mastectomy"
    AORTIC_ANEURYSM_REPAIR = "Aortic Aneurysm Repair"
    GASTRECTOMY            = "Gastrectomy"
    LUNG_LOBECTOMY         = "Lung Lobectomy"

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
        "aliases":     ["defib", "shock machine", "cardioverter", "defibrillator unit"],
    },
    6: {
        "name":        "Electrocautery Unit",
        "description": "Provides monopolar and bipolar electrosurgical current for "
                       "cutting tissue and coagulating bleeding vessels.",
        "aliases":     ["cautery", "bovie", "electrosurgical unit", "ESU", "diathermy",
                        "electrosurgery unit", "bipolar electrosurgery unit"],
    },
    7: {
        "name":        "Suction Device",
        "description": "Removes blood and fluids from the operative field to maintain "
                       "clear surgical visibility throughout the procedure.",
        "aliases":     ["suction", "suction machine", "aspirator", "suction unit"],
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
    12: {
        "name":        "Cell Saver",
        "description": "Autologous blood salvage — collects and re-infuses washed red "
                       "cells from the bypass circuit and operative field.",
        "aliases":     ["cell saver", "autotransfusion", "cell salvage"],
    },
    13: {
        "name":        "Transesophageal Echo Unit",
        "description": "Intraoperative transesophageal echocardiography probe monitors "
                       "cardiac function, valve competence, and de-airing in real time.",
        "aliases":     ["TEE", "transesophageal echo", "echo machine", "TOE", "intraop echo"],
    },
    14: {
        "name":        "Intra-Aortic Balloon Pump",
        "description": "Counterpulsation device inserted via femoral artery to augment "
                       "coronary perfusion and reduce cardiac afterload post-implant.",
        "aliases":     ["IABP", "balloon pump", "aortic balloon", "intra-aortic pump"],
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
        "aliases":     ["CUSA", "ultrasonic dissector", "cavitron", "ultrasonic aspirator",
                        "CUSA device"],
    },
    6: {
        "name":        "Suction Device",
        "description": "Removes blood, bile, and irrigant from the operative field and "
                       "the CUSA dissection plume.",
        "aliases":     ["suction", "aspirator", "suction machine", "suction unit"],
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
        "aliases":     ["fluid warmer", "blood warmer", "hot line", "level 1",
                        "patient warmer", "warming unit"],
    },
    9: {
        "name":        "Laparoscopy Tower",
        "description": "Provides HD video display for laparoscopic or hand-assisted "
                       "approach; includes camera unit, light source, and recorder.",
        "aliases":     ["laparoscopy tower", "lap tower", "video tower", "camera tower",
                        "laparoscopic tower", "laparoscope tower"],
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
    12: {
        "name":        "Intraoperative Ultrasound",
        "description": "High-frequency intraoperative ultrasound probe maps intrahepatic "
                       "vascular anatomy and detects small lesions during resection.",
        "aliases":     ["IOUS", "intraop ultrasound", "liver ultrasound", "intraoperative US"],
    },
    13: {
        "name":        "Hepatic Retractor System",
        "description": "Self-retaining retractor frame provides sustained hepatic "
                       "exposure without fatiguing the assistant.",
        "aliases":     ["liver retractor", "hepatic retractor", "retractor system", "bookwalter"],
    },
    14: {
        "name":        "Haemostatic Agent Applicator",
        "description": "Delivers fibrin glue, oxidised cellulose or thrombin-gelatin "
                       "matrix to the liver cut surface to control ooze.",
        "aliases":     ["tachosil", "surgicel", "floseal", "haemostatic agent", "hemostatic applicator"],
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
        "aliases":     ["nephroscope", "scope", "rigid scope", "nephroscopy unit",
                        "nephroscope tower"],
    },
    3: {
        "name":        "Lithotripsy Device",
        "description": "Pneumatic or ultrasonic lithotripter fragments kidney stones "
                       "inside the collecting system for irrigation and extraction.",
        "aliases":     ["lithotripsy", "lithotripter", "stone crusher", "EMS", "Swiss LithoClast",
                        "lithotripsy unit", "lithotripter device"],
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
        "aliases":     ["suction", "aspirator", "suction machine", "suction unit"],
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
    12: {
        "name":        "Ultrasound Guidance Unit",
        "description": "Real-time ultrasound used as an alternative or adjunct to "
                       "fluoroscopy for safe percutaneous renal access.",
        "aliases":     ["ultrasound guide", "US guidance", "renal ultrasound", "access ultrasound"],
    },
    13: {
        "name":        "Patient Positioning System",
        "description": "Vacuum bean bag and radiolucent table attachments maintain "
                       "prone or modified supine (Valdivia) position safely.",
        "aliases":     ["positioning system", "bean bag", "prone positioner", "patient positioner"],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# CORONARY ARTERY BYPASS GRAFTING
# ─────────────────────────────────────────────────────────────────────────────
_CABG = {
    0:  {"name": "Patient Monitor",               "description": "Continuous ECG, arterial BP, CVP, PA pressure, SpO2 and temperature monitoring throughout on-pump CABG.",                              "aliases": ["monitor", "vitals monitor", "cardiac monitor", "hemodynamic monitor"]},
    1:  {"name": "Ventilator",                     "description": "Mechanical ventilation via endotracheal tube; lungs are deflated during bypass and re-expanded after decannulation.",               "aliases": ["vent", "breathing machine", "mechanical ventilation"]},
    2:  {"name": "Anesthesia Machine",              "description": "Delivers volatile and IV anesthetic agents for general anesthesia maintenance during the procedure.",                               "aliases": ["anesthesia", "gas machine", "anaesthesia machine"]},
    3:  {"name": "Cardiopulmonary Bypass Machine", "description": "Heart-lung bypass machine takes over cardiac and pulmonary function during coronary anastomosis.",                                   "aliases": ["bypass machine", "heart-lung machine", "CPB", "bypass pump", "pump"]},
    4:  {"name": "Perfusion Pump",                 "description": "Delivers cold crystalloid or blood cardioplegia to arrest and protect the myocardium during ischaemic time.",                      "aliases": ["perfusion", "cardioplegia pump", "del nido pump"]},
    5:  {"name": "Defibrillator",                  "description": "Internal paddles or external pads restore sinus rhythm after aortic cross-clamp removal and reperfusion.",                          "aliases": ["defib", "shock machine", "cardioverter", "defibrillator unit"]},
    6:  {"name": "Electrocautery Unit",             "description": "Monopolar and bipolar electrosurgery for sternotomy site haemostasis and conduit harvest.",                                        "aliases": ["cautery", "bovie", "ESU", "diathermy"]},
    7:  {"name": "Suction Device",                 "description": "Cardiotomy suction returns shed blood to the bypass reservoir; field suction maintains visibility.",                               "aliases": ["suction", "suction machine", "aspirator", "suction unit"]},
    8:  {"name": "Blood Warmer",                   "description": "Warms re-infused bypass blood to normothermia during rewarming phase prior to weaning.",                                           "aliases": ["blood warmer", "fluid warmer", "warming unit"]},
    9:  {"name": "Warming Blanket",                "description": "Forced-air warming blanket maintains patient normothermia on bypass and during sternal closure.",                                   "aliases": ["warming blanket", "bair hugger", "forced air warmer", "patient warmer"]},
    10: {"name": "Surgical Lights",                "description": "High-intensity overhead LED lights illuminate the sternal and conduit harvest fields.",                                              "aliases": ["lights", "OR lights", "overhead lights", "surgical lamp"]},
    11: {"name": "Instrument Table",               "description": "Sterile back table with bypass, vascular, and harvest instruments prepared by the scrub team.",                                    "aliases": ["instrument table", "back table", "mayo stand", "scrub table"]},
    12: {"name": "Cell Saver",                     "description": "Processes bypass-circuit and shed blood for autologous re-infusion, reducing allogeneic transfusion requirements.",              "aliases": ["cell saver", "autotransfusion", "cell salvage"]},
    13: {"name": "Intra-Aortic Balloon Pump",      "description": "Counterpulsation device supports cardiac output during weaning from bypass in high-risk patients.",                             "aliases": ["IABP", "balloon pump", "aortic balloon", "intra-aortic pump"]},
    14: {"name": "Transesophageal Echo Unit",       "description": "Intraoperative TEE evaluates ventricular function, wall motion, and de-airing before and after bypass.",                        "aliases": ["TEE", "transesophageal echo", "echo machine", "TOE", "intraop echo"]},
}

# ─────────────────────────────────────────────────────────────────────────────
# APPENDECTOMY
# ─────────────────────────────────────────────────────────────────────────────
_APPENDECTOMY = {
    0:  {"name": "Patient Monitor",        "description": "Monitors ECG, SpO2, NIBP, and EtCO2 during laparoscopic appendicectomy.",                                                  "aliases": ["monitor", "vitals monitor", "hemodynamic monitor"]},
    1:  {"name": "Ventilator",              "description": "Mechanical ventilation via endotracheal tube for general anaesthesia.",                                                        "aliases": ["vent", "breathing machine", "mechanical ventilation"]},
    2:  {"name": "Anesthesia Machine",      "description": "Delivers volatile agents and maintains airway during the procedure.",                                                          "aliases": ["anesthesia", "gas machine", "anaesthesia machine"]},
    3:  {"name": "Laparoscopy Tower",       "description": "HD camera, light source, and display unit for laparoscopic visualisation.",                                                   "aliases": ["laparoscopy tower", "lap tower", "video tower", "camera tower"]},
    4:  {"name": "CO2 Insufflator",         "description": "Creates pneumoperitoneum at 12–15 mmHg for safe trocar insertion and laparoscopic access.",                                    "aliases": ["insufflator", "CO2 insufflator", "pneumoperitoneum machine"]},
    5:  {"name": "Electrocautery Unit",     "description": "Monopolar hook and bipolar forceps for mesoappendix sealing and trocar site haemostasis.",                                    "aliases": ["cautery", "bovie", "ESU", "diathermy"]},
    6:  {"name": "Suction Device",          "description": "Aspirates purulent fluid, peritoneal washout, and smoke plume during dissection.",                                               "aliases": ["suction", "suction machine", "aspirator"]},
    7:  {"name": "Irrigation Pump",         "description": "Delivers warm saline for peritoneal and pelvis lavage when perforation or peritonitis is present.",                           "aliases": ["irrigation pump", "lavage pump", "saline pump"]},
    8:  {"name": "LigaSure Vessel Sealer",  "description": "Bipolar vessel-sealing device divides the mesoappendix vessels with minimal thermal spread.",                                 "aliases": ["ligasure", "vessel sealer", "bipolar sealer", "tissue fusion device"]},
    9:  {"name": "Surgical Stapler",        "description": "Endoscopic linear stapler transects and seals the appendix base, minimising stump leak risk.",                               "aliases": ["stapler", "endo stapler", "linear stapler", "endostapler"]},
    10: {"name": "Warming Blanket",         "description": "Maintains patient normothermia throughout the procedure.",                                                                    "aliases": ["warming blanket", "bair hugger", "forced air warmer"]},
    11: {"name": "Surgical Lights",         "description": "Overhead OR lights for port site access and any open conversion.",                                                             "aliases": ["lights", "OR lights", "overhead lights", "surgical lamp"]},
    12: {"name": "Instrument Table",        "description": "Sterile back table with laparoscopic and open conversion instruments.",                                                       "aliases": ["instrument table", "back table", "mayo stand", "scrub table"]},
    13: {"name": "Patient Warmer",          "description": "Under-body resistive heating mattress provides additional warmth especially in paediatric cases.",                              "aliases": ["patient warmer", "warming mattress", "underbody warmer", "resistive warmer"]},
}

# ─────────────────────────────────────────────────────────────────────────────
# LAPAROSCOPIC CHOLECYSTECTOMY
# ─────────────────────────────────────────────────────────────────────────────
_CHOLECYSTECTOMY = {
    0:  {"name": "Patient Monitor",             "description": "Standard intraoperative monitoring of ECG, SpO2, NIBP and EtCO2.",                                                            "aliases": ["monitor", "vitals monitor", "hemodynamic monitor"]},
    1:  {"name": "Ventilator",                   "description": "Controlled ventilation; minute volume adjustment compensates for CO2 absorption from pneumoperitoneum.",                    "aliases": ["vent", "breathing machine", "mechanical ventilation"]},
    2:  {"name": "Anesthesia Machine",            "description": "Delivers general anaesthesia; anti-emetic prophylaxis important due to high PONV risk.",                                   "aliases": ["anesthesia", "gas machine", "anaesthesia machine"]},
    3:  {"name": "Laparoscopy Tower",             "description": "4K/HD camera, xenon light source, and recording unit for gallbladder visualisation.",                                      "aliases": ["laparoscopy tower", "lap tower", "video tower", "camera tower"]},
    4:  {"name": "CO2 Insufflator",               "description": "Maintains pneumoperitoneum; pressure kept ≤12 mmHg to minimise vagal and cardiovascular effects.",                         "aliases": ["insufflator", "CO2 insufflator", "pneumoperitoneum machine"]},
    5:  {"name": "Electrocautery Unit",           "description": "Hook diathermy dissects Calot's triangle and achieves haemostasis at the gallbladder bed.",                              "aliases": ["cautery", "bovie", "ESU", "diathermy"]},
    6:  {"name": "Suction/Irrigation Device",     "description": "Combined laparoscopic suction and irrigation for bile spillage, washout, and haemostasis.",                               "aliases": ["suction irrigation", "suction irrigator", "s/i device"]},
    7:  {"name": "Clip Applier",                  "description": "Laparoscopic clip applier places titanium or polymer clips on cystic duct and cystic artery prior to division.",       "aliases": ["clip applier", "hemoclip", "endoclip", "laparoscopic clips"]},
    8:  {"name": "LigaSure Vessel Sealer",        "description": "Seals and divides cystic vessels and adhesions in complex or inflamed cholecystectomy cases.",                            "aliases": ["ligasure", "vessel sealer", "bipolar sealer"]},
    9:  {"name": "Cholangiography Unit",           "description": "Intraoperative cholangiogram equipment with contrast syringe and C-arm for bile duct anatomy before division.",      "aliases": ["cholangiography", "IOC unit", "intraop cholangiogram", "bile duct imaging"]},
    10: {"name": "Fluoroscopy C-Arm",             "description": "Mobile X-ray C-arm for intraoperative cholangiography to detect unsuspected common bile duct stones.",                  "aliases": ["c-arm", "fluoroscopy", "x-ray", "image intensifier", "fluoro"]},
    11: {"name": "Warming Blanket",               "description": "Forced-air warming maintains normothermia particularly in elderly or prolonged cases.",                                   "aliases": ["warming blanket", "bair hugger", "forced air warmer"]},
    12: {"name": "Surgical Lights",               "description": "Overhead surgical lights for port placement and any open conversion.",                                                    "aliases": ["lights", "OR lights", "overhead lights", "surgical lamp"]},
    13: {"name": "Instrument Table",              "description": "Sterile instrument table with laparoscopic and open hepatobiliary instruments.",                                          "aliases": ["instrument table", "back table", "mayo stand", "scrub table"]},
}

# ─────────────────────────────────────────────────────────────────────────────
# TOTAL HIP REPLACEMENT
# ─────────────────────────────────────────────────────────────────────────────
_HIP_REPLACEMENT = {
    0:  {"name": "Patient Monitor",        "description": "Monitors ECG, BP, SpO2 and temperature; haemodynamic stability critical during cementation.",                                   "aliases": ["monitor", "vitals monitor", "hemodynamic monitor"]},
    1:  {"name": "Ventilator",              "description": "Provides general or monitors LMA airway; spinal anaesthesia often used as an alternative.",                                      "aliases": ["vent", "breathing machine", "mechanical ventilation"]},
    2:  {"name": "Anesthesia Machine",      "description": "Delivers general anaesthesia or monitors spinal/epidural block level.",                                                          "aliases": ["anesthesia", "gas machine", "anaesthesia machine"]},
    3:  {"name": "Electrocautery Unit",     "description": "Monopolar electrosurgery for capsule incision, muscle splitting, and haemostasis around the hip.",                             "aliases": ["cautery", "bovie", "ESU", "diathermy"]},
    4:  {"name": "Pulsed Lavage System",    "description": "High-pressure pulsatile irrigation cleans the acetabulum and femoral canal before cement or cementless fixation.",             "aliases": ["pulsed lavage", "pulse lavage", "pressure irrigation", "lavage gun"]},
    5:  {"name": "Bone Cement Mixer",       "description": "Vacuum mixing system prepares PMMA cement for femoral stem fixation with minimal porosity.",                                    "aliases": ["cement mixer", "PMMA mixer", "bone cement system", "vacuum cement mixer"]},
    6:  {"name": "Oscillating Saw",         "description": "Reciprocating saw makes precise femoral neck osteotomy and acetabular rim preparation cuts.",                                  "aliases": ["oscillating saw", "bone saw", "reciprocating saw", "surgical saw"]},
    7:  {"name": "Acetabular Reamer",       "description": "Hemispherical reamers progressively enlarge the acetabulum to receive the cup implant.",                                      "aliases": ["reamer", "acetabular reamer", "cup reamer", "hip reamer"]},
    8:  {"name": "Cell Saver",              "description": "Collects and re-infuses autologous blood to reduce allogenic transfusion in revision cases.",                                  "aliases": ["cell saver", "autotransfusion", "cell salvage"]},
    9:  {"name": "Blood Warmer",            "description": "Warms transfused products inline to prevent intraoperative hypothermia.",                                                       "aliases": ["blood warmer", "fluid warmer", "warming unit"]},
    10: {"name": "Warming Blanket",         "description": "Forced-air warming maintains normothermia throughout the surgery.",                                                             "aliases": ["warming blanket", "bair hugger", "forced air warmer"]},
    11: {"name": "Surgical Lights",         "description": "Overhead surgical lights illuminate the hip field; lateral or posterior approach requires good illumination depth.",             "aliases": ["lights", "OR lights", "overhead lights", "surgical lamp"]},
    12: {"name": "Instrument Table",        "description": "Sterile table with hip arthroplasty trial components, reamers, broaches and final implants.",                                  "aliases": ["instrument table", "back table", "mayo stand", "scrub table"]},
    13: {"name": "Fluoroscopy C-Arm",       "description": "Intraoperative C-arm confirms implant position, leg length, and offset before wound closure.",                                 "aliases": ["c-arm", "fluoroscopy", "x-ray", "image intensifier", "fluoro"]},
    14: {"name": "Suction Device",          "description": "Removes blood and irrigant from the joint field to maintain surgical visibility.",                                              "aliases": ["suction", "suction machine", "aspirator", "suction unit"]},
}

# ─────────────────────────────────────────────────────────────────────────────
# TOTAL KNEE REPLACEMENT
# ─────────────────────────────────────────────────────────────────────────────
_KNEE_REPLACEMENT = {
    0:  {"name": "Patient Monitor",        "description": "Monitors haemodynamics; tourniquet-induced hypertension and reperfusion changes are common.",                                    "aliases": ["monitor", "vitals monitor", "hemodynamic monitor"]},
    1:  {"name": "Ventilator",              "description": "Controlled ventilation under general or SAB anaesthesia.",                                                                        "aliases": ["vent", "breathing machine", "mechanical ventilation"]},
    2:  {"name": "Anesthesia Machine",      "description": "Provides general anaesthesia or monitors spinal block for knee replacement.",                                                    "aliases": ["anesthesia", "gas machine", "anaesthesia machine"]},
    3:  {"name": "Tourniquet System",       "description": "Pneumatic tourniquet applied to the proximal thigh provides a bloodless operative field during bone cuts.",                      "aliases": ["tourniquet", "pneumatic tourniquet", "thigh tourniquet", "tourniquet cuff"]},
    4:  {"name": "Oscillating Saw",         "description": "Reciprocating and oscillating saws make distal femur, proximal tibia and patellar bone cuts.",                                 "aliases": ["oscillating saw", "bone saw", "reciprocating saw", "surgical saw"]},
    5:  {"name": "Pulsed Lavage System",    "description": "High-pressure saline irrigation removes bone debris and marrow fat before cementation.",                                       "aliases": ["pulsed lavage", "pulse lavage", "pressure irrigation", "lavage gun"]},
    6:  {"name": "Bone Cement Mixer",       "description": "Vacuum PMMA mixing and dispensing gun ensures uniform cement mantle for tibial and femoral components.",                       "aliases": ["cement mixer", "PMMA mixer", "bone cement system", "vacuum cement mixer"]},
    7:  {"name": "Electrocautery Unit",     "description": "Monopolar and bipolar cautery for soft tissue dissection and haemostasis during exposure.",                                    "aliases": ["cautery", "bovie", "ESU", "diathermy"]},
    8:  {"name": "Suction Device",          "description": "Continuous suction keeps the field clear during bone cutting and cementing.",                                                   "aliases": ["suction", "suction machine", "aspirator"]},
    9:  {"name": "Cell Saver",              "description": "Postoperative wound drain re-infusion or intraoperative salvage reduces transfusion in revision cases.",                      "aliases": ["cell saver", "autotransfusion", "cell salvage"]},
    10: {"name": "Warming Blanket",         "description": "Forced-air warming blanket maintains normothermia and reduces post-operative shivering.",                                       "aliases": ["warming blanket", "bair hugger", "forced air warmer"]},
    11: {"name": "Surgical Lights",         "description": "Overhead lights provide illumination for medial parapatellar arthrotomy and bone work.",                                        "aliases": ["lights", "OR lights", "overhead lights", "surgical lamp"]},
    12: {"name": "Instrument Table",        "description": "Sterile table holding TKR cutting guides, trials, final implants and cement supplies.",                                        "aliases": ["instrument table", "back table", "mayo stand", "scrub table"]},
    13: {"name": "Fluoroscopy C-Arm",       "description": "Intraoperative X-ray confirms implant position, alignment, and absence of cement gaps.",                                       "aliases": ["c-arm", "fluoroscopy", "x-ray", "image intensifier", "fluoro"]},
}

# ─────────────────────────────────────────────────────────────────────────────
# CAESAREAN SECTION
# ─────────────────────────────────────────────────────────────────────────────
_CAESAREAN_SECTION = {
    0:  {"name": "Patient Monitor",              "description": "Continuous maternal ECG, SpO2, NIBP monitoring; fetal heart rate monitored before delivery.",                            "aliases": ["monitor", "vitals monitor", "maternal monitor"]},
    1:  {"name": "Ventilator",                    "description": "Provides IPPV under general anaesthesia (used when spinal/epidural is contraindicated).",                               "aliases": ["vent", "breathing machine", "mechanical ventilation"]},
    2:  {"name": "Anesthesia Machine",             "description": "Delivers general or monitors neuraxial block; dedicated obstetric protocols to prevent awareness.",                   "aliases": ["anesthesia", "gas machine", "anaesthesia machine"]},
    3:  {"name": "Epidural/Spinal Unit",           "description": "Epidural trolley with spinal needles, intrathecal bupivacaine, and opioid adjuncts for regional anaesthesia.",     "aliases": ["epidural unit", "spinal unit", "neuraxial unit", "epidural trolley"]},
    4:  {"name": "Electrocautery Unit",            "description": "Monopolar cautery for uterine incision extension, haemostasis, and wound closure.",                                  "aliases": ["cautery", "bovie", "ESU", "diathermy"]},
    5:  {"name": "Suction Device",                 "description": "Aspirates amniotic fluid, blood and lochia from the operative field and uterine cavity.",                           "aliases": ["suction", "suction machine", "aspirator"]},
    6:  {"name": "Neonatal Resuscitation Unit",    "description": "Radiant warmer with T-piece resuscitator, suction, oxygen, and chest compression surface for the neonate.",       "aliases": ["neonatal unit", "resuscitation unit", "neo resus", "newborn resuscitator"]},
    7:  {"name": "Infant Warmer",                  "description": "Open radiant heat source maintains neonatal thermoregulation after delivery.",                                        "aliases": ["infant warmer", "radiant warmer", "baby warmer", "overhead warmer"]},
    8:  {"name": "Blood Warmer",                   "description": "Warms rapid IV fluid or blood transfusion for maternal haemorrhage management.",                                       "aliases": ["blood warmer", "fluid warmer", "warming unit"]},
    9:  {"name": "Warming Blanket",                "description": "Forced-air maternal warming reduces shivering after spinal block and blood loss.",                                    "aliases": ["warming blanket", "bair hugger", "forced air warmer"]},
    10: {"name": "Oxytocin Infusion Pump",         "description": "Syringe driver delivers IV oxytocin bolus and infusion for uterotonic effect after delivery.",                       "aliases": ["oxytocin pump", "syntocinon pump", "uterotonic pump", "infusion pump"]},
    11: {"name": "Surgical Lights",                "description": "Overhead OR lights illuminate the lower uterine segment and pelvic operative field.",                                 "aliases": ["lights", "OR lights", "overhead lights", "surgical lamp"]},
    12: {"name": "Instrument Table",               "description": "Sterile table with CS instruments, retractors, sutures and uterine repair supplies.",                                 "aliases": ["instrument table", "back table", "mayo stand", "scrub table"]},
    13: {"name": "Foetal Monitor",                 "description": "Cardiotocography unit tracks fetal heart rate and contractions in the pre-operative holding area.",                  "aliases": ["CTG", "fetal monitor", "foetal monitor", "cardiotocograph"]},
}

# ─────────────────────────────────────────────────────────────────────────────
# SPINAL FUSION
# ─────────────────────────────────────────────────────────────────────────────
_SPINAL_FUSION = {
    0:  {"name": "Patient Monitor",           "description": "Monitors ECG, invasive BP, SpO2, EtCO2, and temperature in the prone position.",                                             "aliases": ["monitor", "vitals monitor", "hemodynamic monitor"]},
    1:  {"name": "Ventilator",                 "description": "Controlled ventilation in prone position; increased airway pressures require close monitoring.",                             "aliases": ["vent", "breathing machine", "mechanical ventilation"]},
    2:  {"name": "Anesthesia Machine",         "description": "Delivers TIVA or volatile anaesthesia; TIVA preferred when neuromonitoring is used.",                                       "aliases": ["anesthesia", "gas machine", "anaesthesia machine"]},
    3:  {"name": "Fluoroscopy C-Arm",          "description": "Intraoperative lateral and AP fluoroscopy guides pedicle screw placement and confirms fusion levels.",                     "aliases": ["c-arm", "fluoroscopy", "x-ray", "image intensifier", "fluoro"]},
    4:  {"name": "Neuromonitoring System",     "description": "Intraoperative neuromonitoring (MEP/SSEP/EMG) detects spinal cord injury in real time during instrumentation.",           "aliases": ["neuromonitoring", "IONM", "neuro monitoring", "MEP monitor", "SSEP monitor"]},
    5:  {"name": "Electrocautery Unit",        "description": "Monopolar cautery for muscle stripping and bipolar for haemostasis near neural structures.",                              "aliases": ["cautery", "bovie", "ESU", "diathermy"]},
    6:  {"name": "Ultrasonic Bone Scalpel",    "description": "Piezoelectric device cuts bone with minimal thermal scatter, protecting adjacent dura and neural tissue.",                "aliases": ["ultrasonic scalpel", "bone scalpel", "SONOPET", "ultrasonic bone cutter"]},
    7:  {"name": "Suction Device",             "description": "Epidural/surgical field suction; Penfield instruments with suction tips used around neural structures.",                "aliases": ["suction", "suction machine", "aspirator"]},
    8:  {"name": "Irrigation System",          "description": "Saline irrigation of the surgical field for decompression, fusion, and disc space preparation.",                          "aliases": ["irrigation system", "saline irrigation", "wound irrigator"]},
    9:  {"name": "Pedicle Screw System",       "description": "Percutaneous or open pedicle screw and rod system provides rigid spinal stabilisation across the fusion segment.",       "aliases": ["pedicle screws", "spinal implants", "rod-screw system", "instrumentation system"]},
    10: {"name": "Bone Graft Harvester",       "description": "Trephine or rongeur harvests local autograft from spinous processes or iliac crest for fusion.",                         "aliases": ["bone harvester", "graft harvester", "iliac crest harvester", "bone collector"]},
    11: {"name": "Warming Blanket",            "description": "Upper/lower body warming blankets maintain normothermia during extended prone-position surgery.",                         "aliases": ["warming blanket", "bair hugger", "forced air warmer"]},
    12: {"name": "Surgical Lights",            "description": "Overhead and headlight illumination for the posterior spinal exposure field.",                                              "aliases": ["lights", "OR lights", "overhead lights", "surgical lamp"]},
    13: {"name": "Instrument Table",           "description": "Sterile back table with spinal retractors, curettes, rongeurs, and implant system components.",                           "aliases": ["instrument table", "back table", "mayo stand", "scrub table"]},
    14: {"name": "Microscope Tower",           "description": "Intraoperative surgical microscope provides magnified view for decompression and nerve root identification.",              "aliases": ["microscope", "surgical microscope", "neuro microscope", "operating microscope"]},
}

# ─────────────────────────────────────────────────────────────────────────────
# CATARACT SURGERY
# ─────────────────────────────────────────────────────────────────────────────
_CATARACT_SURGERY = {
    0:  {"name": "Patient Monitor",           "description": "Monitors ECG, SpO2 and BP; most cases under topical or local anaesthesia with light sedation.",                            "aliases": ["monitor", "vitals monitor", "hemodynamic monitor"]},
    1:  {"name": "Anesthesia Machine",         "description": "Standby general anaesthesia for uncooperative patients; sedation/monitoring for topical cases.",                          "aliases": ["anesthesia", "gas machine", "anaesthesia machine"]},
    2:  {"name": "Phacoemulsification Unit",   "description": "Ultrasonic phaco handpiece emulsifies the lens nucleus; simultaneous irrigation/aspiration removes debris.",              "aliases": ["phaco machine", "phaco unit", "cataract machine", "phacoemulsifier"]},
    3:  {"name": "Surgical Microscope",        "description": "Co-axial illuminated surgical microscope provides high-magnification binocular view of the anterior segment.",           "aliases": ["ophthalmic microscope", "surgical microscope", "operating microscope", "slit lamp microscope"]},
    4:  {"name": "Irrigation/Aspiration System","description": "Automated I/A handpiece polishes the posterior capsule and aspirates cortical remnants after phaco.",              "aliases": ["I/A system", "irrigation aspiration", "cortex removal system"]},
    5:  {"name": "Intraocular Lens Injector",  "description": "Single-use injector cartridge folds and delivers the foldable IOL through the micro-incision.",                          "aliases": ["IOL injector", "lens injector", "intraocular lens system"]},
    6:  {"name": "Ophthalmic Cautery Unit",    "description": "Fine-tip disposable cautery used for limbal vessel haemostasis before incision.",                                          "aliases": ["eye cautery", "ophthalmic cautery", "cautery unit"]},
    7:  {"name": "Auto-Keratometer",           "description": "Measures corneal curvature preoperatively for IOL power calculation (biometry).",                                          "aliases": ["keratometer", "biometer", "autokeratometer", "IOLMaster"]},
    8:  {"name": "Anterior Segment OCT",       "description": "Intraoperative OCT images the anterior chamber for real-time guidance during phaco and IOL orientation.",              "aliases": ["AS-OCT", "anterior OCT", "intraop OCT", "iOCT"]},
    9:  {"name": "Viscoelastic Injector",      "description": "Syringe with cannula fills the anterior chamber with OVD to protect the corneal endothelium.",                          "aliases": ["viscoelastic", "OVD injector", "viscoat", "healon injector"]},
    10: {"name": "Eye Pressure Monitor",       "description": "Measures IOP continuously via air-puff or contact tonometry throughout the case.",                                        "aliases": ["IOP monitor", "tonometer", "eye pressure monitor", "intraocular pressure monitor"]},
    11: {"name": "Surgical Lights",            "description": "Overhead OR lights supplemented by microscope coaxial illumination for the eye field.",                                   "aliases": ["lights", "OR lights", "overhead lights", "surgical lamp"]},
    12: {"name": "Instrument Table",           "description": "Sterile mayo stand with phaco handpieces, cannulas, and IOL insertion cartridges.",                                       "aliases": ["instrument table", "back table", "mayo stand", "scrub table"]},
    13: {"name": "Microscope Camera Tower",    "description": "Camera unit attached to the operating microscope displays the surgical view for assistants and recording.",               "aliases": ["microscope camera", "camera tower", "microscope display", "endoscope camera tower"]},
}

# ─────────────────────────────────────────────────────────────────────────────
# HYSTERECTOMY
# ─────────────────────────────────────────────────────────────────────────────
_HYSTERECTOMY = {
    0:  {"name": "Patient Monitor",                  "description": "Standard ECG, SpO2, NIBP, EtCO2 monitoring; Trendelenburg position requires careful haemodynamic watch.",       "aliases": ["monitor", "vitals monitor", "hemodynamic monitor"]},
    1:  {"name": "Ventilator",                         "description": "IPPV managing increased airway pressures from steep Trendelenburg and pneumoperitoneum.",                        "aliases": ["vent", "breathing machine", "mechanical ventilation"]},
    2:  {"name": "Anesthesia Machine",                 "description": "Delivers volatile/TIVA general anaesthesia with muscle relaxation for abdominal access.",                      "aliases": ["anesthesia", "gas machine", "anaesthesia machine"]},
    3:  {"name": "Laparoscopy Tower",                  "description": "Full HD camera, light source, and monitor tower for total laparoscopic hysterectomy (TLH).",                  "aliases": ["laparoscopy tower", "lap tower", "video tower", "camera tower"]},
    4:  {"name": "CO2 Insufflator",                    "description": "Creates and maintains pneumoperitoneum; high-flow allows rapid recovery after suction.",                         "aliases": ["insufflator", "CO2 insufflator", "pneumoperitoneum machine"]},
    5:  {"name": "Electrocautery Unit",                "description": "Monopolar and bipolar cautery for parametrial dissection and vaginal cuff closure.",                           "aliases": ["cautery", "bovie", "ESU", "diathermy"]},
    6:  {"name": "Harmonic Scalpel",                   "description": "Ultrasonic vessel sealing and cutting through the broad ligament and uterine vasculature.",                     "aliases": ["harmonic", "ultrasonic scalpel", "harmonic ace", "ultrasonic cutting device"]},
    7:  {"name": "Suction/Irrigation Device",          "description": "Combined suction and irrigation for pelvic haemostasis and vaginal cuff washout.",                             "aliases": ["suction irrigation", "suction irrigator", "s/i device"]},
    8:  {"name": "Uterine Manipulator System",         "description": "Intrauterine manipulator anteverts/retroflexes the uterus and delineates the colpotomy ring.",               "aliases": ["uterine manipulator", "RUMI manipulator", "KOH colpotomy system", "manipulator"]},
    9:  {"name": "Vessel Sealer",                      "description": "Advanced bipolar vessel sealer (LigaSure/ENSEAL) divides ovarian pedicles and broad ligament.",              "aliases": ["vessel sealer", "ligasure", "ENSEAL", "bipolar sealer"]},
    10: {"name": "Morcellation Containment System",    "description": "Contained specimen morcellator bag removes the uterine specimen through a small port safely.",               "aliases": ["morcellator", "containment bag", "specimen bag", "morcellation bag"]},
    11: {"name": "Warming Blanket",                    "description": "Forced-air patient warming compensates for heat loss during prolonged lithotomy position.",                   "aliases": ["warming blanket", "bair hugger", "forced air warmer"]},
    12: {"name": "Surgical Lights",                    "description": "Overhead OR lights for port placement; external illumination assists vaginal cuff suturing.",                 "aliases": ["lights", "OR lights", "overhead lights", "surgical lamp"]},
    13: {"name": "Instrument Table",                   "description": "Sterile back table with laparoscopic, robotic, and vaginal hysterectomy instruments.",                        "aliases": ["instrument table", "back table", "mayo stand", "scrub table"]},
}

# ─────────────────────────────────────────────────────────────────────────────
# THYROIDECTOMY
# ─────────────────────────────────────────────────────────────────────────────
_THYROIDECTOMY = {
    0:  {"name": "Patient Monitor",           "description": "Standard ECG, SpO2, NIBP monitoring; neck extension position monitored for haemodynamic shifts.",                         "aliases": ["monitor", "vitals monitor", "hemodynamic monitor"]},
    1:  {"name": "Ventilator",                 "description": "Intubation with reinforced/armoured ETT; nerve monitoring requires avoidance of neuromuscular blocking agents.",       "aliases": ["vent", "breathing machine", "mechanical ventilation"]},
    2:  {"name": "Anesthesia Machine",         "description": "Delivers TIVA or volatile anaesthesia; propofol TIVA preferred to preserve NIM tube signal quality.",                  "aliases": ["anesthesia", "gas machine", "anaesthesia machine"]},
    3:  {"name": "Nerve Monitoring System",    "description": "Intraoperative neuromonitoring (NIM) with EMG endotracheal tube detects recurrent laryngeal nerve injury.",             "aliases": ["NIM system", "nerve monitor", "RLN monitor", "intraoperative nerve monitor"]},
    4:  {"name": "Harmonic Scalpel",           "description": "Ultrasonic vessel sealer/divider for thyroid vasculature with minimal lateral thermal spread near the RLN.",          "aliases": ["harmonic", "ultrasonic scalpel", "harmonic ace"]},
    5:  {"name": "Electrocautery Unit",        "description": "Bipolar forceps for small vessel and parathyroid bed haemostasis.",                                                       "aliases": ["cautery", "bovie", "ESU", "diathermy", "bipolar cautery"]},
    6:  {"name": "Suction Device",             "description": "Field suction keeps the dissection plane and nerve monitoring field clear of blood.",                                     "aliases": ["suction", "suction machine", "aspirator"]},
    7:  {"name": "Magnification Loupes System","description": "Surgical loupes (×2.5–4.5) or operating microscope for parathyroid and RLN identification.",                              "aliases": ["loupes", "magnification loupes", "surgical loupes", "magnification system"]},
    8:  {"name": "Calcium/PTH Analyser",       "description": "Rapid intraoperative PTH assay confirms adequate parathyroid function after parathyroidectomy.",                        "aliases": ["PTH analyser", "calcium analyser", "parathyroid monitor", "rapid PTH"]},
    9:  {"name": "Bipolar Cautery Unit",       "description": "Fine-tip bipolar forceps provides precise coagulation around the parathyroid glands.",                                  "aliases": ["bipolar cautery", "bipolar forceps", "fine bipolar"]},
    10: {"name": "Retractor System",           "description": "Self-retaining retractor (e.g. Joll's) holds neck skin flaps and exposes the thyroid lobe.",                            "aliases": ["retractor", "jolls retractor", "thyroid retractor", "neck retractor"]},
    11: {"name": "Warming Blanket",            "description": "Body warming to prevent post-operative hypothermia during supine neck-extension positioning.",                          "aliases": ["warming blanket", "bair hugger", "forced air warmer"]},
    12: {"name": "Surgical Lights",            "description": "Overhead and headlight illumination for deep neck dissection.",                                                            "aliases": ["lights", "OR lights", "overhead lights", "surgical lamp"]},
    13: {"name": "Instrument Table",           "description": "Sterile mayo stand with thyroid dissection instruments, clips, and drain supplies.",                                      "aliases": ["instrument table", "back table", "mayo stand", "scrub table"]},
}

# ─────────────────────────────────────────────────────────────────────────────
# COLECTOMY
# ─────────────────────────────────────────────────────────────────────────────
_COLECTOMY = {
    0:  {"name": "Patient Monitor",        "description": "Monitors ECG, NIBP/ABP, SpO2, EtCO2 and UO; epidural analgesia effects watched carefully.",                               "aliases": ["monitor", "vitals monitor", "hemodynamic monitor"]},
    1:  {"name": "Ventilator",              "description": "IPPV throughout; lung-protective strategy for prolonged laparoscopic procedures.",                                          "aliases": ["vent", "breathing machine", "mechanical ventilation"]},
    2:  {"name": "Anesthesia Machine",      "description": "Volatile or TIVA general anaesthesia combined with epidural for enhanced recovery.",                                        "aliases": ["anesthesia", "gas machine", "anaesthesia machine"]},
    3:  {"name": "Laparoscopy Tower",       "description": "HD laparoscopic camera, light source, and display for minimally invasive colonic resection.",                              "aliases": ["laparoscopy tower", "lap tower", "video tower", "camera tower"]},
    4:  {"name": "CO2 Insufflator",         "description": "Pneumoperitoneum creation and maintenance; CO2 absorption monitored by anaesthesia team.",                                  "aliases": ["insufflator", "CO2 insufflator", "pneumoperitoneum machine"]},
    5:  {"name": "Electrocautery Unit",     "description": "Monopolar hook and bipolar cautery for mesenteric dissection and abdominal wall haemostasis.",                            "aliases": ["cautery", "bovie", "ESU", "diathermy"]},
    6:  {"name": "Vessel Sealer",           "description": "Advanced bipolar vessel sealer (LigaSure) divides mesenteric vessels during mobilisation.",                               "aliases": ["vessel sealer", "ligasure", "bipolar sealer"]},
    7:  {"name": "Surgical Stapler",        "description": "Circular and linear staplers form colorectal anastomosis and divide the bowel.",                                            "aliases": ["stapler", "circular stapler", "linear stapler", "endo stapler", "EEA stapler"]},
    8:  {"name": "Suction/Irrigation Device","description": "Combined suction and warm saline lavage of the abdominal cavity.",                                                         "aliases": ["suction irrigation", "suction irrigator", "s/i device"]},
    9:  {"name": "Cell Saver",              "description": "Blood salvage for complex or extended resections to minimise allogenic transfusion.",                                      "aliases": ["cell saver", "autotransfusion", "cell salvage"]},
    10: {"name": "Warming Blanket",         "description": "Forced-air warming prevents hypothermia during lengthy colonic procedures.",                                                 "aliases": ["warming blanket", "bair hugger", "forced air warmer"]},
    11: {"name": "Surgical Lights",         "description": "Overhead lights for port placement, specimen extraction, and open-conversion anastomosis.",                                 "aliases": ["lights", "OR lights", "overhead lights", "surgical lamp"]},
    12: {"name": "Instrument Table",        "description": "Sterile back table with laparoscopic, stapling, and open colorectal instruments.",                                         "aliases": ["instrument table", "back table", "mayo stand", "scrub table"]},
    13: {"name": "Fluoroscopy C-Arm",       "description": "Intraoperative C-arm used for anastomotic leak test or ureteric stent-guided ureter identification.",                     "aliases": ["c-arm", "fluoroscopy", "x-ray", "image intensifier", "fluoro"]},
}

# ─────────────────────────────────────────────────────────────────────────────
# RADICAL PROSTATECTOMY
# ─────────────────────────────────────────────────────────────────────────────
_PROSTATECTOMY = {
    0:  {"name": "Patient Monitor",          "description": "ICU-grade monitoring in steep Trendelenburg; includes invasive arterial BP and CVP.",                                        "aliases": ["monitor", "vitals monitor", "hemodynamic monitor"]},
    1:  {"name": "Ventilator",                "description": "IPPV in steep Trendelenburg; careful pressure-controlled mode for lung protection.",                                        "aliases": ["vent", "breathing machine", "mechanical ventilation"]},
    2:  {"name": "Anesthesia Machine",        "description": "TIVA preferred for robotic cases to maintain signal quality in neuromonitoring.",                                           "aliases": ["anesthesia", "gas machine", "anaesthesia machine"]},
    3:  {"name": "Robotic Surgery Console",   "description": "da Vinci surgeon console provides 3D magnified vision and articulated wristed instrument control.",                      "aliases": ["da vinci", "robot console", "surgical robot", "robotic console"]},
    4:  {"name": "CO2 Insufflator",           "description": "High-flow insufflator maintains pneumoperitoneum in steep Trendelenburg position.",                                        "aliases": ["insufflator", "CO2 insufflator", "pneumoperitoneum machine"]},
    5:  {"name": "Electrocautery Unit",       "description": "Monopolar and bipolar electrosurgery for bladder neck dissection and haemostasis.",                                       "aliases": ["cautery", "bovie", "ESU", "diathermy"]},
    6:  {"name": "Harmonic Scalpel",          "description": "Ultrasonic cutting and sealing for neurovascular bundle dissection with low thermal spread.",                             "aliases": ["harmonic", "ultrasonic scalpel", "harmonic ace"]},
    7:  {"name": "Suction/Irrigation Device", "description": "Combined field suction and warm saline lavage during anastomosis and haemostasis.",                                       "aliases": ["suction irrigation", "suction irrigator"]},
    8:  {"name": "Nerve Stimulator",          "description": "Intraoperative nerve stimulation identifies and preserves the cavernous neurovascular bundles.",                          "aliases": ["nerve stimulator", "neurostimulator", "cavernous nerve stimulator"]},
    9:  {"name": "Bipolar Vessel Sealer",     "description": "Advanced bipolar sealer controls prostatic pedicles and dorsal venous complex.",                                          "aliases": ["bipolar sealer", "vessel sealer", "ligasure"]},
    10: {"name": "Laparoscopy Tower",         "description": "Standalone HD laparoscopy tower used for robotic docking verification and port placement.",                               "aliases": ["laparoscopy tower", "lap tower", "video tower", "camera tower"]},
    11: {"name": "Warming Blanket",           "description": "Upper-body forced-air warming maintains normothermia during steep Trendelenburg.",                                         "aliases": ["warming blanket", "bair hugger", "forced air warmer"]},
    12: {"name": "Surgical Lights",           "description": "Overhead OR lights used during port placement and post-undocking wound closure.",                                          "aliases": ["lights", "OR lights", "overhead lights", "surgical lamp"]},
    13: {"name": "Instrument Table",          "description": "Sterile back table with robotic, laparoscopic, and open conversion instruments.",                                         "aliases": ["instrument table", "back table", "mayo stand", "scrub table"]},
}

# ─────────────────────────────────────────────────────────────────────────────
# CRANIOTOMY
# ─────────────────────────────────────────────────────────────────────────────
_CRANIOTOMY = {
    0:  {"name": "Patient Monitor",         "description": "Invasive arterial BP, CVP, ICP, SpO2, EtCO2 monitoring; cerebral perfusion pressure calculated continuously.",             "aliases": ["monitor", "vitals monitor", "hemodynamic monitor", "neuro monitor"]},
    1:  {"name": "Ventilator",               "description": "Controlled ventilation targets PaCO2 35–40 mmHg; hyperventilation reserved for acute brain herniation.",                "aliases": ["vent", "breathing machine", "mechanical ventilation"]},
    2:  {"name": "Anesthesia Machine",       "description": "TIVA with propofol/remifentanil preserves cerebral autoregulation and motor evoked potential signals.",                 "aliases": ["anesthesia", "gas machine", "anaesthesia machine"]},
    3:  {"name": "Neurosurgical Microscope",  "description": "High-zoom binocular microscope for brain tumour, vascular and skull base surgery dissection.",                            "aliases": ["neuromicroscope", "surgical microscope", "neuro microscope", "operating microscope"]},
    4:  {"name": "Cranial Drill System",     "description": "High-speed cranial perforator and craniotome makes burr holes and safely lifts the bone flap.",                          "aliases": ["cranial drill", "craniotome", "perforator", "bone drill"]},
    5:  {"name": "Neuromonitoring System",   "description": "MEP, SSEP, ECoG and cranial nerve EMG monitoring protects eloquent cortex and cranial nerves.",                          "aliases": ["neuromonitoring", "IONM", "MEP monitor", "SSEP monitor", "intraop neuromonitoring"]},
    6:  {"name": "Ultrasonic Aspirator",     "description": "CUSA neurosurgical aspirator fragments and aspirates tumour tissue with precision near neural structures.",             "aliases": ["CUSA", "ultrasonic aspirator", "CUSA neurosurgery", "cavitron neuro"]},
    7:  {"name": "Bipolar Cautery Unit",     "description": "Fine-jeweller-tip bipolar forceps provides coagulation on brain surface vessels and tumour pedicles.",                  "aliases": ["bipolar cautery", "bipolar", "fine bipolar", "bipolar forceps"]},
    8:  {"name": "Suction Device",           "description": "Variable-suction Frazier-tip suckers maintain visibility in the cranial cavity and around neurovascular structures.",  "aliases": ["suction", "suction machine", "aspirator", "frazier suction"]},
    9:  {"name": "Irrigation System",        "description": "Warm saline irrigation cools bipolar tips, removes clot, and maintains moist brain surface.",                            "aliases": ["irrigation system", "saline irrigation", "wound irrigator"]},
    10: {"name": "ICP Monitor",              "description": "Intracranial pressure monitoring catheter or bolt tracks ICP and CPP throughout the procedure.",                          "aliases": ["ICP monitor", "intracranial pressure monitor", "bolt monitor", "EVD monitor"]},
    11: {"name": "Fluoroscopy C-Arm",        "description": "Intraoperative fluoroscopy or O-arm for aneurysm clip confirmation or tumour localisation.",                              "aliases": ["c-arm", "fluoroscopy", "x-ray", "image intensifier", "o-arm"]},
    12: {"name": "Warming Blanket",          "description": "Lower-body forced-air warming prevents heat loss during prolonged cranial procedures.",                                    "aliases": ["warming blanket", "bair hugger", "forced air warmer"]},
    13: {"name": "Surgical Lights",          "description": "Overhead OR lights supplement the microscope illumination for wound opening and closure.",                                 "aliases": ["lights", "OR lights", "overhead lights", "surgical lamp"]},
    14: {"name": "Instrument Table",         "description": "Sterile back table with neurosurgical patties, retractors, clips, and microscope accessories.",                           "aliases": ["instrument table", "back table", "mayo stand", "scrub table"]},
}

# ─────────────────────────────────────────────────────────────────────────────
# MASTECTOMY
# ─────────────────────────────────────────────────────────────────────────────
_MASTECTOMY = {
    0:  {"name": "Patient Monitor",        "description": "Standard ECG, SpO2, NIBP and temperature monitoring during breast surgery under general anaesthesia.",                     "aliases": ["monitor", "vitals monitor", "hemodynamic monitor"]},
    1:  {"name": "Ventilator",              "description": "IPPV; lateral tilt positioning requires careful ventilator pressure management.",                                           "aliases": ["vent", "breathing machine", "mechanical ventilation"]},
    2:  {"name": "Anesthesia Machine",      "description": "General anaesthesia with TIVA or volatile agents; PECS/serratus plane blocks for multimodal analgesia.",                   "aliases": ["anesthesia", "gas machine", "anaesthesia machine"]},
    3:  {"name": "Electrocautery Unit",     "description": "Monopolar cutting and coagulation throughout mastectomy skin flap dissection and axillary clearance.",                    "aliases": ["cautery", "bovie", "ESU", "diathermy"]},
    4:  {"name": "Harmonic Scalpel",        "description": "Ultrasonic cutting and coagulation minimises smoke plume and thermal spread in axillary dissection.",                      "aliases": ["harmonic", "ultrasonic scalpel", "harmonic ace"]},
    5:  {"name": "Suction Device",          "description": "Field suction during mastectomy and axillary dissection; postoperative drain suction for seroma prevention.",            "aliases": ["suction", "suction machine", "aspirator"]},
    6:  {"name": "Gamma Probe System",      "description": "Handheld gamma probe localises the sentinel lymph node after isotope injection for axillary staging.",                 "aliases": ["gamma probe", "sentinel node probe", "lymph node probe", "SLNB probe"]},
    7:  {"name": "Tissue Expander Kit",     "description": "Sub-pectoral tissue expander with access port placed at time of mastectomy for staged reconstruction.",                  "aliases": ["tissue expander", "expander", "breast expander", "reconstruction expander"]},
    8:  {"name": "Argon Beam Coagulator",   "description": "Non-contact argon plasma coagulation seals the chest wall and skin flap ooze after mastectomy.",                         "aliases": ["argon beam", "ABC", "argon coagulator"]},
    9:  {"name": "Drainage System",         "description": "Closed-suction Jackson-Pratt drains placed in the mastectomy cavity and axilla to prevent seroma.",                     "aliases": ["drain", "drainage system", "JP drain", "closed suction drain"]},
    10: {"name": "Blood Warmer",            "description": "Inline fluid and blood warmer for haemorrhagic cases or immediate reconstruction.",                                         "aliases": ["blood warmer", "fluid warmer", "warming unit"]},
    11: {"name": "Warming Blanket",         "description": "Forced-air warming for patient normothermia during breast and/or axillary surgery.",                                       "aliases": ["warming blanket", "bair hugger", "forced air warmer"]},
    12: {"name": "Surgical Lights",         "description": "Overhead OR lights provide even illumination for skin flap elevation and axillary dissection.",                            "aliases": ["lights", "OR lights", "overhead lights", "surgical lamp"]},
    13: {"name": "Instrument Table",        "description": "Sterile table with breast surgery, sentinel node, and reconstruction instruments.",                                        "aliases": ["instrument table", "back table", "mayo stand", "scrub table"]},
}

# ─────────────────────────────────────────────────────────────────────────────
# AORTIC ANEURYSM REPAIR
# ─────────────────────────────────────────────────────────────────────────────
_AORTIC_ANEURYSM_REPAIR = {
    0:  {"name": "Patient Monitor",                 "description": "Invasive arterial line, PA catheter/TOE, CVP, urine output and temperature monitoring for open AAA.",             "aliases": ["monitor", "vitals monitor", "hemodynamic monitor"]},
    1:  {"name": "Ventilator",                       "description": "Prolonged IPPV; lung-protective strategy important given risk of ischaemia-reperfusion injury.",                 "aliases": ["vent", "breathing machine", "mechanical ventilation"]},
    2:  {"name": "Anesthesia Machine",               "description": "General anaesthesia; epidural/spinal adjunct can provide post-operative analgesia for open repair.",             "aliases": ["anesthesia", "gas machine", "anaesthesia machine"]},
    3:  {"name": "Cardiopulmonary Bypass Machine",   "description": "Partial bypass for thoracoabdominal aneurysm; left heart bypass or full CPB for thoracic extension.",          "aliases": ["bypass machine", "heart-lung machine", "CPB", "bypass pump", "pump"]},
    4:  {"name": "Cell Saver",                       "description": "Autologous blood salvage is mandatory given anticipated large blood loss during aortic repair.",                "aliases": ["cell saver", "autotransfusion", "cell salvage"]},
    5:  {"name": "Heparin Infusion Pump",            "description": "Delivers systemic heparin bolus and maintains anticoagulation throughout clamp time.",                          "aliases": ["heparin pump", "anticoagulation pump", "infusion pump", "heparin infusion"]},
    6:  {"name": "Electrocautery Unit",              "description": "Monopolar and bipolar electrosurgery for retroperitoneal exposure, dissection, and haemostasis.",               "aliases": ["cautery", "bovie", "ESU", "diathermy"]},
    7:  {"name": "Suction Device",                   "description": "High-volume suction during aortic cross-clamping, graft sewing, and declamping haemorrhage.",                  "aliases": ["suction", "suction machine", "aspirator"]},
    8:  {"name": "Blood Warmer",                     "description": "Rapid infusion warming system handles large-volume blood product transfusion.",                                   "aliases": ["blood warmer", "fluid warmer", "rapid infuser", "warming unit"]},
    9:  {"name": "Transesophageal Echo Unit",         "description": "Intraoperative TOE monitors ventricular function, volume status, and endograft/open repair endpoints.",       "aliases": ["TEE", "transesophageal echo", "echo machine", "TOE", "intraop echo"]},
    10: {"name": "Fluoroscopy C-Arm",                "description": "EVAR/TEVAR: real-time fluoroscopy guides wire, sheath, and endograft deployment within the aorta.",           "aliases": ["c-arm", "fluoroscopy", "x-ray", "image intensifier", "fluoro"]},
    11: {"name": "Endovascular Stent Graft System",  "description": "Modular stent graft system (EVAR device) is deployed under fluoroscopy via femoral access.",                 "aliases": ["stent graft", "EVAR device", "endograft", "endovascular graft"]},
    12: {"name": "Pressure Transducer System",       "description": "Multi-channel pressure transducers measure aortic, renal, femoral and graft pressures during repair.",         "aliases": ["pressure transducer", "pressure monitoring system", "transducer system"]},
    13: {"name": "Warming Blanket",                  "description": "Forced-air warming and under-body mattress maintain normothermia during prolonged aortic repair.",              "aliases": ["warming blanket", "bair hugger", "forced air warmer"]},
    14: {"name": "Surgical Lights",                  "description": "Overhead lights for retroperitoneal/abdominal incision with additional headlight for deep field.",            "aliases": ["lights", "OR lights", "overhead lights", "surgical lamp"]},
    15: {"name": "Instrument Table",                 "description": "Sterile back table with aortic clamps, synthetic grafts, EVAR equipment, and vascular instruments.",          "aliases": ["instrument table", "back table", "mayo stand", "scrub table"]},
}

# ─────────────────────────────────────────────────────────────────────────────
# GASTRECTOMY
# ─────────────────────────────────────────────────────────────────────────────
_GASTRECTOMY = {
    0:  {"name": "Patient Monitor",          "description": "Standard ECG, ABP, CVP, SpO2 monitoring; epidural analgesia block level monitored continuously.",                         "aliases": ["monitor", "vitals monitor", "hemodynamic monitor"]},
    1:  {"name": "Ventilator",                "description": "Lung-protective IPPV; head-up (reverse Trendelenburg) position used for upper GI access.",                              "aliases": ["vent", "breathing machine", "mechanical ventilation"]},
    2:  {"name": "Anesthesia Machine",        "description": "Volatile or TIVA general anaesthesia; thoracic epidural provides multimodal analgesia.",                                 "aliases": ["anesthesia", "gas machine", "anaesthesia machine"]},
    3:  {"name": "Laparoscopy Tower",         "description": "4K laparoscopic camera system for minimal-access total or subtotal gastrectomy.",                                         "aliases": ["laparoscopy tower", "lap tower", "video tower", "camera tower"]},
    4:  {"name": "CO2 Insufflator",           "description": "Maintains pneumoperitoneum during laparoscopic gastric dissection and lymphadenectomy.",                                  "aliases": ["insufflator", "CO2 insufflator", "pneumoperitoneum machine"]},
    5:  {"name": "Electrocautery Unit",       "description": "Monopolar and hook diathermy for omentum mobilisation and adhesiolysis.",                                                "aliases": ["cautery", "bovie", "ESU", "diathermy"]},
    6:  {"name": "Harmonic Scalpel",          "description": "Ultrasonic cutting and sealing through the gastrocolic ligament and gastric vessels.",                                   "aliases": ["harmonic", "ultrasonic scalpel", "harmonic ace"]},
    7:  {"name": "Surgical Stapler",          "description": "Linear and circular staplers transect the stomach and form the gastrojejuno-anastomosis.",                               "aliases": ["stapler", "circular stapler", "linear stapler", "endo stapler", "EEA stapler"]},
    8:  {"name": "Suction/Irrigation Device", "description": "Field suction and abdominal lavage throughout the gastric and esophageal dissection.",                                    "aliases": ["suction irrigation", "suction irrigator"]},
    9:  {"name": "Nasogastric Suction Unit",  "description": "Low-pressure nasogastric suction decompresses the new gastric remnant and monitors anastomotic output.",               "aliases": ["NG tube", "nasogastric tube", "stomach tube", "NG suction"]},
    10: {"name": "Cell Saver",                "description": "Blood salvage in extensive D2 dissection cases or open gastrectomy with significant haemorrhage.",                    "aliases": ["cell saver", "autotransfusion", "cell salvage"]},
    11: {"name": "Warming Blanket",           "description": "Forced-air warming prevents hypothermia in prolonged upper GI oncological resection.",                                   "aliases": ["warming blanket", "bair hugger", "forced air warmer"]},
    12: {"name": "Surgical Lights",           "description": "Overhead lights for specimen extraction incision and anastomosis under direct vision.",                                  "aliases": ["lights", "OR lights", "overhead lights", "surgical lamp"]},
    13: {"name": "Instrument Table",          "description": "Sterile back table with gastric retractors, stapling devices, and anastomosis supplies.",                                "aliases": ["instrument table", "back table", "mayo stand", "scrub table"]},
}

# ─────────────────────────────────────────────────────────────────────────────
# LUNG LOBECTOMY
# ─────────────────────────────────────────────────────────────────────────────
_LUNG_LOBECTOMY = {
    0:  {"name": "Patient Monitor",              "description": "Full invasive monitoring: arterial BP, CVP, SpO2, EtCO2 and core temperature during one-lung ventilation.",         "aliases": ["monitor", "vitals monitor", "hemodynamic monitor"]},
    1:  {"name": "Double-Lumen Ventilator",       "description": "Dual-lumen ETT enables selective one-lung ventilation, isolating the operative side during dissection.",          "aliases": ["double lumen ventilator", "DLT ventilator", "one-lung vent", "OLV ventilator"]},
    2:  {"name": "Anesthesia Machine",            "description": "Delivers volatile agents or TIVA; carefully manages FiO2 and PEEP during one-lung ventilation.",                   "aliases": ["anesthesia", "gas machine", "anaesthesia machine"]},
    3:  {"name": "Thoracoscopy Tower",            "description": "4K thoracoscopic camera, light source and display unit for VATS lobectomy.",                                         "aliases": ["thoracoscopy tower", "VATS tower", "video tower", "thoracoscope tower"]},
    4:  {"name": "CO2 Insufflator",               "description": "Provides low-pressure CO2 insufflation for thoracoscopic access in non-intubated or difficult cases.",             "aliases": ["insufflator", "CO2 insufflator", "chest insufflator"]},
    5:  {"name": "Electrocautery Unit",           "description": "Monopolar hook and bipolar cautery for pleural dissection and haemostasis in the thoracic cavity.",               "aliases": ["cautery", "bovie", "ESU", "diathermy"]},
    6:  {"name": "Harmonic Scalpel",              "description": "Ultrasonic cutting and coagulation through pulmonary ligament and hilar tissue dissection.",                       "aliases": ["harmonic", "ultrasonic scalpel", "harmonic ace"]},
    7:  {"name": "Surgical Stapler",              "description": "Endoscopic vascular and reticulating staplers divide pulmonary artery branches, veins, and bronchus.",             "aliases": ["stapler", "vascular stapler", "endo stapler", "linear stapler"]},
    8:  {"name": "Suction Device",                "description": "Pleural cavity suction removes blood clot, irrigation, and aerosol during thoracoscopic work.",                   "aliases": ["suction", "suction machine", "aspirator"]},
    9:  {"name": "One-Lung Ventilation Monitor",  "description": "Continuous SpO2 and capnography monitoring of the non-ventilated lung during surgical collapse.",                  "aliases": ["OLV monitor", "one-lung monitor", "lung ventilation monitor"]},
    10: {"name": "Cell Saver",                    "description": "Autologous blood salvage during open or complex VATS lobectomy for significant haemorrhage.",                     "aliases": ["cell saver", "autotransfusion", "cell salvage"]},
    11: {"name": "Bronchoscopy Unit",             "description": "Flexible bronchoscope confirms double-lumen tube position and clears secretions before OLV.",                      "aliases": ["bronchoscope", "bronchoscopy unit", "flexible bronchoscope", "fibreoptic bronchoscope"]},
    12: {"name": "Warming Blanket",               "description": "Forced-air blanket maintains normothermia during prolonged thoracic procedures in lateral decubitus.",             "aliases": ["warming blanket", "bair hugger", "forced air warmer"]},
    13: {"name": "Surgical Lights",               "description": "Overhead lights used at port sites, utility incision, and chest drain placement.",                                  "aliases": ["lights", "OR lights", "overhead lights", "surgical lamp"]},
    14: {"name": "Instrument Table",              "description": "Sterile back table with thoracoscopic, stapling and open thoracotomy instruments and chest drains.",                 "aliases": ["instrument table", "back table", "mayo stand", "scrub table"]},
}

# ─────────────────────────────────────────────────────────────────────────────
# Master lookup
# ─────────────────────────────────────────────────────────────────────────────
MACHINES: dict[SurgeryType, dict[int, dict]] = {
    SurgeryType.HEART_TRANSPLANT:       _HEART,
    SurgeryType.LIVER_RESECTION:        _LIVER,
    SurgeryType.KIDNEY_PCNL:            _KIDNEY_PCNL,
    SurgeryType.CABG:                   _CABG,
    SurgeryType.APPENDECTOMY:           _APPENDECTOMY,
    SurgeryType.CHOLECYSTECTOMY:        _CHOLECYSTECTOMY,
    SurgeryType.HIP_REPLACEMENT:        _HIP_REPLACEMENT,
    SurgeryType.KNEE_REPLACEMENT:       _KNEE_REPLACEMENT,
    SurgeryType.CAESAREAN_SECTION:      _CAESAREAN_SECTION,
    SurgeryType.SPINAL_FUSION:          _SPINAL_FUSION,
    SurgeryType.CATARACT_SURGERY:       _CATARACT_SURGERY,
    SurgeryType.HYSTERECTOMY:           _HYSTERECTOMY,
    SurgeryType.THYROIDECTOMY:          _THYROIDECTOMY,
    SurgeryType.COLECTOMY:              _COLECTOMY,
    SurgeryType.PROSTATECTOMY:          _PROSTATECTOMY,
    SurgeryType.CRANIOTOMY:             _CRANIOTOMY,
    SurgeryType.MASTECTOMY:             _MASTECTOMY,
    SurgeryType.AORTIC_ANEURYSM_REPAIR: _AORTIC_ANEURYSM_REPAIR,
    SurgeryType.GASTRECTOMY:            _GASTRECTOMY,
    SurgeryType.LUNG_LOBECTOMY:         _LUNG_LOBECTOMY,
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
