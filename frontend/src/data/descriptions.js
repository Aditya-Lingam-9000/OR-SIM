/**
 * data/descriptions.js
 * Frontend description lookup for all 3D-hoverable OR objects.
 *
 *  • MACHINE_DESCRIPTIONS  — canonical machine name → short description
 *  • ROLE_DESCRIPTIONS     — personnel role → short description
 *  • DOCTOR_NAMES / NURSE_NAMES — random name pools (one pick per session)
 *  • pickRandom(arr)       — helper to draw one entry at random
 */

// ── Machine descriptions ──────────────────────────────────────────────────────
export const MACHINE_DESCRIPTIONS = {
  'Patient Monitor':
    'Continuously monitors vital signs including ECG, arterial blood pressure, SpO₂, CVP, and core temperature throughout the procedure.',
  'Ventilator':
    'Provides controlled mechanical ventilation via endotracheal tube, delivering precise tidal volumes and respiratory rates during general anaesthesia.',
  'Anesthesia Machine':
    'Delivers inhalational anaesthetic agents mixed with oxygen and air, maintaining depth of general anaesthesia with integrated vaporiser controls.',
  'Cardiopulmonary Bypass Machine':
    'Temporarily takes over heart and lung function, oxygenating and pumping blood through the body during the cardiac arrest phase of surgery.',
  'Perfusion Pump':
    'Delivers cardioplegia solution to arrest the heart and administers preservative perfusate to maintain graft viability during transplantation.',
  'Defibrillator':
    'Delivers controlled electrical shocks to terminate life-threatening arrhythmias and restore normal sinus rhythm after cardiac intervention.',
  'Electrocautery Unit':
    'Provides monopolar and bipolar electrosurgical current for precisely cutting tissue and coagulating bleeding vessels with minimal thermal spread.',
  'Suction Device':
    'Removes blood, irrigation fluid, and operative debris from the surgical field via regulated vacuum suction.',
  'Blood Warmer':
    'Rapidly warms transfused blood products to body temperature to prevent hypothermia and coagulopathy during massive transfusion.',
  'Warming Blanket':
    'Maintains patient normothermia using forced-air warming, reducing the risk of hypothermia during prolonged surgical procedures.',
  'Surgical Lights':
    'Ceiling-mounted dual-head surgical lighting system providing high-intensity, shadowless illumination over the operative field with adjustable focus and colour temperature.',
  'Instrument Table':
    'Sterile back table holding all surgical instruments, sutures, and consumables arranged by the scrub nurse for immediate intraoperative access.',
  'Cell Saver':
    'Collects, washes, and re-infuses the patient\'s own shed blood, significantly reducing the need for allogeneic blood transfusion.',
  'Transesophageal Echo Unit':
    'Provides real-time cardiac imaging via a transesophageal probe, allowing continuous assessment of ventricular function and valve morphology.',
  'Intra-Aortic Balloon Pump':
    'Provides mechanical cardiac support by cyclically inflating/deflating a balloon in the descending aorta, improving coronary perfusion and reducing afterload.',
  'Fluoroscopy C-Arm':
    'Mobile X-ray imaging system providing real-time fluoroscopic guidance for accurate instrument placement and intraoperative implant positioning.',
  'Laparoscopy Tower':
    'Integrated video system housing the camera processor, light source, and HD monitor for laparoscopic surgery visualisation.',
  'CO2 Insufflator':
    'Delivers controlled CO₂ gas to inflate the peritoneal cavity, creating the working space necessary for laparoscopic procedures.',
  'Harmonic Scalpel':
    'Ultrasonically-activated blade that simultaneously cuts and coagulates tissue using high-frequency vibration with minimal thermal damage to surrounding structures.',
  'LigaSure Vessel Sealer':
    'Advanced vessel sealing system that fuses blood vessels up to 7 mm using precise bipolar energy delivery and tissue compression.',
  'Irrigation System':
    'Delivers warmed saline irrigation to the operative field to maintain clear visibility and prevent thermal injury during electrosurgery.',
  'Irrigation Pump':
    'Provides continuous pressurised irrigation fluid flow to the operative field, maintaining visibility during endoscopic procedures.',
  'Irrigation/Aspiration System':
    'Dual-function device that simultaneously delivers balanced salt solution and aspirates lens cortex material during phacoemulsification.',
  'Robotic Surgery Console':
    'Surgeon console for the da Vinci robotic system, translating hand and finger movements into precise micro-scale surgical instrument motions.',
  'Nephroscope Unit':
    'Rigid endoscope system providing direct visualisation inside the renal collecting system for percutaneous kidney stone management.',
  'Lithotripsy Device':
    'Uses pneumatic, ultrasonic, or laser energy to fragment kidney stones into small pieces safe for basket retrieval and aspiration.',
  'Stone Retrieval System':
    'Basket and forceps-based system for capturing and removing stone fragments from the renal collecting system under nephroscopic guidance.',
  'Contrast Injector':
    'Power injector delivering iodinated contrast medium at precise rates during fluoroscopic or CT-guided intraoperative imaging.',
  'Video Tower':
    'Cart-based system housing the endoscope processor, light source, HD recording unit, and monitor for minimally invasive surgery.',
  'Phacoemulsification Unit':
    'Uses ultrasonic vibration to emulsify the cloudy crystalline lens, which is then aspirated through a small incision during cataract surgery.',
  'Anterior Segment OCT':
    'Optical coherence tomography system providing micron-level cross-sectional imaging of anterior eye structures including cornea and anterior chamber.',
  'Auto-Keratometer':
    'Automated device measuring corneal curvature to calculate the precise refractive power of the intraocular lens implant.',
  'Intraocular Lens Injector':
    'Pre-loaded injector delivering the folded IOL through a 2–3 mm incision, where it unfolds and is positioned in the capsular bag.',
  'Eye Pressure Monitor':
    'Continuously monitors intraocular pressure during ophthalmic procedures to detect and prevent vision-threatening pressure fluctuations.',
  'Ophthalmic Cautery Unit':
    'Miniaturised electrocautery device designed for delicate haemostasis in ophthalmic procedures with minimal surrounding tissue damage.',
  'Viscoelastic Injector':
    'Delivers viscoelastic ophthalmic gel into the anterior chamber to protect corneal endothelium and maintain the surgical space during IOL implantation.',
  'Oscillating Saw':
    'High-precision power saw for bone osteotomies in orthopaedic procedures, oscillating at high frequency to minimise soft-tissue trauma.',
  'Bone Cement Mixer':
    'Vacuum mixing system for preparing polymethylmethacrylate (PMMA) bone cement with controlled porosity for cemented prosthesis fixation.',
  'Pulsed Lavage System':
    'Delivers pulsatile irrigation to thoroughly clean the medullary canal of fat, blood, and debris prior to cemented implant insertion.',
  'Acetabular Reamer':
    'Sequential power reaming system precisely preparing the acetabular socket to the correct diameter for press-fit cup implantation.',
  'Tourniquet System':
    'Pneumatic tourniquet providing limb exsanguination and a bloodless operative field for extremity orthopaedic procedures.',
  'Nerve Stimulator':
    'Handheld electrical nerve stimulator identifying and mapping motor nerve branches to prevent inadvertent neurological injury during dissection.',
  'Epidural/Spinal Unit':
    'Integrated anaesthesia system for administering spinal or epidural anaesthetic agents under real-time pressure monitoring and aspiration confirmation.',
  'Patient Positioning System':
    'Specialised table attachments, pads, and supports ensuring optimal surgical access while maintaining safe skeletal and neurovascular alignment.',
  'Pedicle Screw System':
    'Instrumentation set for placing titanium pedicle screws, connecting rods, and spacers to stabilise and compress the spinal fusion construct.',
  'Bone Graft Harvester':
    'System for harvesting autologous bone from the iliac crest or local site to pack the interbody space and promote spinal fusion.',
  'Neuromonitoring System':
    'Continuous electrophysiological monitoring system (SSEP/MEP/EMG) providing real-time alerts of neurological compromise during spinal or cranial surgery.',
  'Ultrasonic Bone Scalpel':
    'Piezosurgery device cutting mineralised tissue with ultrasonic energy while protecting adjacent nerves, dura, and soft tissue from thermal damage.',
  'Foetal Monitor':
    'Continuous cardiotocography system monitoring foetal heart rate and uterine contractions to detect intraoperative foetal distress during Caesarean section.',
  'Oxytocin Infusion Pump':
    'Precision syringe pump delivering oxytocin after uterine delivery to promote sustained uterine contraction and reduce postpartum haemorrhage risk.',
  'Neonatal Resuscitation Unit':
    'Integrated resuscitation station with radiant warmer, oxygen blender, suction, and cardiac monitoring for immediate newborn stabilisation.',
  'Infant Warmer':
    'Servo-controlled overhead radiant heat warmer maintaining neonate normothermia immediately after delivery in the operating theatre.',
  'Fluid Warmer':
    'In-line intravenous fluid warming device heating crystalloids and blood products to 37 °C before systemic administration.',
  'Heparin Infusion Pump':
    'Precision syringe pump delivering calibrated heparin doses to maintain target activated clotting time levels during vascular or cardiac procedures.',
  'Pressure Transducer System':
    'Invasive arterial and central venous pressure transducer system providing continuous haemodynamic waveform monitoring with electronic zeroing.',
  'Intraoperative Ultrasound':
    'High-frequency probe for real-time intraoperative imaging aiding tumour margin delineation, vessel identification, and needle guidance.',
  'Ultrasound Guidance Unit':
    'Portable ultrasound system used to guide needle placement, vascular line insertion, or regional anaesthesia nerve blocks in real time.',
  'Argon Beam Coagulator':
    'Non-contact haemostasis device channelling ionised argon gas to direct radiofrequency current for broad surface coagulation on liver or vascular tissue.',
  'Hepatic Retractor System':
    'Specialised self-retaining retractor system providing stable hepatobiliary field exposure without requiring manual surgeon retraction.',
  'Cholangiography Unit':
    'Fluoroscopic imaging unit used intraoperatively to visualise bile-duct anatomy and confirm complete clearance of biliary stones.',
  'Drainage System':
    'Closed suction or passive gravity drainage collecting postoperative wound fluid and preventing haematoma or seroma formation.',
  'Suction/Irrigation Device':
    'Combination laparoscopic probe for simultaneous operative field irrigation and fluid aspiration during minimally invasive procedures.',
  'Vessel Sealer':
    'Advanced energy device sealing and dividing blood vessels and tissue bundles with a single jaw compression-and-energy sequence.',
  'Bipolar Vessel Sealer':
    'Bipolar energy device precisely sealing vessels and lymphatics with minimal lateral thermal spread in delicate anatomical planes.',
  'Bipolar Cautery Unit':
    'Bipolar electrosurgical generator for precise tissue coagulation between two forceps tips, routinely used in thyroid and head-neck surgery.',
  'Clip Applier':
    'Endoscopic clip applicator for ligating vascular pedicles, the cystic duct, and tubular structures during laparoscopic procedures.',
  'Morcellation Containment System':
    'Contained power morcellation bag enabling laparoscopic removal of large uterine specimens with full tissue containment to prevent dissemination.',
  'Uterine Manipulator System':
    'Transcervical device allowing controlled intraoperative uterine positioning to facilitate laparoscopic hysterectomy exposure and approach.',
  'Gamma Probe System':
    'Handheld gamma radiation detector intraoperatively locating sentinel lymph nodes labelled with technetium-99m radiotracer for targeted biopsy.',
  'Tissue Expander Kit':
    'Sub-pectoral silicone tissue expander placed at primary mastectomy for staged breast reconstruction with adjustable fill ports.',
  'Haemostatic Agent Applicator':
    'Delivery device for topical haemostatic agents (oxidised cellulose, gelatin sponge, fibrin glue) to control surface and oozing bleeding.',
  'ICP Monitor':
    'Intracranial pressure monitoring system providing continuous real-time ICP waveform data via external ventricular drain or fibre-optic bolt.',
  'Neurosurgical Microscope':
    'Motorised operating microscope with coaxial illumination and magnification up to 40× for microneurosurgical procedures and tumour resection.',
  'Cranial Drill System':
    'High-speed pneumatic or electric cranial drill for creating burr holes and performing controlled bone-flap elevation during craniotomy.',
  'Ultrasonic Aspirator':
    'Cavitational ultrasonic surgical aspirator (CUSA) fragmenting and aspirating neoplastic or vascular brain tissue with minimal normal-brain disruption.',
  'Microscope Tower':
    'Video-integrated surgical microscope tower combining HD digital imaging with exoscopic or co-axial illumination for ENT or spine microsurgery.',
  'Microscope Camera Tower':
    'Camera-integrated microscope system recording high-resolution intraoperative footage for real-time documentation and surgical team education.',
  'Retractor System':
    'Self-retaining or table-mounted mechanical retraction system holding wound edges open to expose deep surgical structures without manual effort.',
  'Nerve Monitoring System':
    'Continuous intraoperative neuromonitoring with EMG electrodes and nerve stimulator providing real-time recurrent laryngeal nerve integrity alerts.',
  'Magnification Loupes System':
    'Prismatic optical loupes providing 2.5–6× visual magnification for enhanced delineation of delicate anatomical structures.',
  'Calcium/PTH Analyser':
    'Point-of-care analyser providing rapid parathyroid hormone and ionised calcium results within minutes during parathyroid or thyroid surgery.',
  'Endovascular Stent Graft System':
    'Modular stent graft device deployed under fluoroscopic guidance to endovascularly exclude the aortic aneurysm sac from systemic arterial pressure.',
  'Double-Lumen Ventilator':
    'Advanced ventilator using a double-lumen endotracheal tube to enable independent single-lung ventilation during thoracic surgical procedures.',
  'One-Lung Ventilation Monitor':
    'Monitors gas exchange and lung mechanics during single-lung ventilation, providing early warnings of hypoxaemia and CO₂ retention.',
  'Bronchoscopy Unit':
    'Flexible or rigid bronchoscope system for airway inspection, bronchial stump assessment, and therapeutic intervention during thoracic surgery.',
  'Thoracoscopy Tower':
    'Video-assisted thoracic surgery (VATS) platform housing the thoracoscopic camera, light source, and integration with robotic instruments.',
  'Surgical Stapler':
    'Linear or circular mechanical stapling device creating haemostatic and air-tight staple lines for gastrointestinal or pulmonary resection and anastomosis.',
  'Nasogastric Suction Unit':
    'Controlled suction system maintaining nasogastric tube drainage to decompress the stomach and prevent aspiration during abdominal surgery.',
  'Patient Warmer':
    'Full-body patient warming system maintaining normothermia during prolonged surgery using forced-air or conductive blanket technology.',
}

// ── Surgical light tooltip ────────────────────────────────────────────────────
export const SURGICAL_LIGHT_DESCRIPTION =
  'Dual-head ceiling-mounted surgical lighting assembly providing high-intensity, shadowless illumination over the operative field, with six-axis articulation for precise positioning and adjustable colour temperature (4,000–5,000 K).'

// ── Patient tooltip ───────────────────────────────────────────────────────────
export const PATIENT_DESCRIPTION_TEMPLATE = (name, surgery) =>
  `${name} is undergoing ${surgery}. The patient is under general anaesthesia with continuous multi-parameter haemodynamic monitoring, endotracheal ventilation, and sterile field preparation.`

// ── Personnel role descriptions ───────────────────────────────────────────────
export const ROLE_DESCRIPTIONS = {
  surgeon:
    'Lead operating surgeon directing all primary incisions, organ manipulation, and critical intraoperative decision-making throughout the procedure.',
  assistant:
    'Assistant surgeon providing counter-traction, haemostasis support, and instrument handling whilst maintaining optimal surgical field exposure.',
  anesthesiologist:
    'Anaesthesiologist managing the airway, inhalational agent delivery, and continuous haemodynamic optimisation from induction to emergence.',
  nurse:
    'Scrub nurse maintaining sterile field integrity, anticipating instrument needs, swab counts, and passing equipment to the surgical team.',
}

// ── Name pools ─────────────────────────────────────────────────────────────────
export const DOCTOR_FIRST_NAMES = [
  'Priya Mehta', 'James Okafor', 'Sofia Lindqvist', 'Arjun Nair',
  'Chen Wei', 'Amara Diallo', 'Lucas Ferreira', 'Elena Volkova',
  'Omar Khalid', 'Yuki Tanaka', 'Isabelle Dumont', 'Rafael Torres',
  'Aditya Sharma', 'Nina Reyes', 'Marcus Adler', 'Fatou Diagne',
]

export const NURSE_FIRST_NAMES = [
  'Fatima Al-Rashid', 'Chloe Beaumont', 'Samuel Osei',
  'Maria Santos', 'Aiko Yamamoto', 'David Okonkwo',
  'Preethi Iyer', 'Lena Hoffmann', 'Jamal Hassan', 'Ana Kovač',
]

export const PATIENT_FIRST_NAMES = [
  'Arthur', 'Beatrice', 'Carlos', 'Diana', 'Ethan',
  'Fatima', 'George', 'Hana', 'Ivan', 'Jasmine',
]
export const PATIENT_LAST_NAMES = [
  'Anderson', 'Brennan', 'Castillo', 'Drummond', 'Ellis',
  'Fernandez', 'Garcia', 'Holbrook', 'Ibarra', 'Jensen',
]

// ── Random pick helper ────────────────────────────────────────────────────────
export function pickRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)]
}
