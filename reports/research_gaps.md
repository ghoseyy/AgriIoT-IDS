# Research Gaps in AI-Based Intrusion Detection for Agricultural IoT Networks

This document synthesizes the key research gaps identified across the reviewed literature concerning the application of Artificial Intelligence (AI) for Intrusion Detection Systems (IDS) in Internet of Things (IoT) networks, with particular relevance to agricultural contexts. These gaps highlight areas requiring further investigation to advance the security of AgriIoT systems.

## Overarching Research Gaps

### 1. Data Availability, Quality, and Representation
*   **Lack of Up-to-Date and Representative Datasets**: A pervasive issue is the reliance on outdated or non-representative datasets (e.g., KDD Cup'99) that do not accurately reflect modern network attacks, especially those targeting IoT and AgriIoT devices (Ahmad2021, Verma2020). There's a critical need for new datasets that capture diverse and evolving attack vectors in real-world IoT and agricultural environments (Fei2024, Altulaihan2024d).
*   **Class Imbalance**: IoT datasets are often severely imbalanced, with normal traffic vastly outnumbering attack instances. This biases AI/ML models towards majority classes, leading to poor detection accuracy for rare, yet critical, attack types like R2L, U2R, or specific botnet variants (Ahmad2021, Maseer2021, Stoian, Ullah2022). Effective strategies for handling and mitigating this imbalance are continuously needed (Panigrahi).
*   **Data Heterogeneity and Complexity**: Managing heterogeneous data from diverse IoT sensors and network devices, coupled with the computational challenges of processing large volumes of data for training complex AI models, remains a significant hurdle (Ali2024a, Stoian, Ullah2022).

### 2. Generalizability and Real-World Applicability
*   **Gap Between Lab and Real-World Performance**: Many proposed IDS methodologies are tested in controlled lab environments or simulations, limiting their generalizability and proven effectiveness in dynamic, unpredictable real-world AgriIoT deployments (Ahmad2021, Meidan2018). Validation on real-world testbeds and diverse deployments is essential (Altulaihan2024d, Alfahaid2025).
*   **Resource Constraints of IoT Devices**: A critical gap is the need for lightweight and resource-efficient IDS models specifically designed for the constrained computational, memory, and energy capabilities of AgriIoT devices (Ahmad2021, Fei2024, Alfahaid2025, Li2024). Traditional complex models often incur high computational costs and latency.
*   **Scalability and Adaptability**: Existing solutions often struggle with scalability to large-scale, heterogeneous IoT networks and adaptability to continuously evolving threat landscapes (Alfahaid2025, Bella2024, Fei2024).

### 3. Advanced Threat Detection and Mitigation
*   **Detection of Novel/Zero-Day Attacks**: Traditional signature-based IDSs are ineffective against novel or zero-day attacks, highlighting a need for adaptive anomaly detection methods, particularly those leveraging generative models, that can identify previously unseen malicious behaviors (Abdalgawad2022b, Meidan2018, Ullah2021).
*   **Interaction Between Sensor Faults and Cyberattacks**: The complex interplay between sensor health anomalies and cybersecurity attacks, where sensor faults can mask or amplify attack detectability, is an underexplored area (Pasca2025).
*   **Targeted Attack Detection (e.g., DoS, Botnets, Routing Attacks)**: While some research focuses on specific attack types (e.g., DoS), there's a continuous need for robust, optimized IDS mechanisms against prevalent and evolving threats like DoS, botnets, and routing attacks, especially in resource-constrained IoT environments (Altulaihan2024d, Meidan2018, Ioannou2021, Verma2020).

### 4. Interpretability, Privacy, and Ethical Considerations
*   **Explainability (XAI)**: The "black box" nature of complex AI/DL models poses challenges for interpretability, hindering trust and rapid response in security incidents (Alfahaid2025). There's a need for more explainable AI models in IoT security.
*   **Privacy and Data Governance**: Significant concerns exist around data privacy, ownership, and regulatory frameworks within smart agriculture, especially with the increasing collection of sensitive farm data (AdebunmiOkechukwuAdewusi2022, Ahmed2024, Ali2024a, Alfahaid2025).
*   **Ethical Implications**: The broader ethical concerns of deploying AI in critical infrastructure like agriculture, particularly regarding bias, fairness, and potential misuse, require deeper investigation (Ali2024a).

### 5. Architectural and Framework Gaps
*   **Lack of Standardization**: The fragmented IoT ecosystem suffers from a lack of standardized security protocols and consistent security features across devices, complicating IDS deployment (AdebunmiOkechukwuAdewusi2022, Fei2024).
*   **Comprehensive Security at Gateways**: There's a gap in comprehensive security measures at IoT gateways, which often serve as critical aggregation and control points (Fei2024).
*   **Integrated Cybersecurity Frameworks**: The development of holistic, multi-layered cybersecurity strategies tailored specifically for smart agriculture, integrating various security mechanisms from device to cloud, is an ongoing need (AdebunmiOkechukwuAdewusi2022). This includes frameworks that can simulate and study combined cyber-physical threats (Pasca2025).

### 6. Autonomous Recovery and Response Automation
*   **Detection-Only Focus**: The overwhelming majority of AI-based IDS research, including the studies synthesized above, stops at alert generation. A broader review of agentic-AI-for-cybersecurity literature (27 papers, NIST framework-mapped) found the "Recover" function addressed by a single study (Sheth et al., 2025 IEEE Cloud Summit), targeting cloud-scale infrastructure with unrestricted compute and always-on connectivity.
*   **Adjacent work exists but misses the target** (verified via Crossref, July 2026). Recovery/self-healing research divides into four groups, none of which covers intrusion recovery on a constrained agricultural node:
    - *Cloud security recovery*: Sheth et al. (2025 IEEE Cloud Summit) — right trigger (attack), wrong resource regime.
    - *Constrained-device fault recovery*: EdgeRescue (Alanazi et al., Computation 14(4):84, 2026; 57% recovery-latency reduction) and TinyHeal (Miller, AIET 3(1), 2026) — right resource regime, but the trigger is battery depletion, interference, hardware degradation, or link variability, not an adversary.
    - *Detector self-healing*: SH-IDS (Fatima et al., Sci. Rep. 16(1), 2026) — adapts the detection model on a danger signal; the compromised node is not isolated, rolled back, or replaced.
    - *Sensor-data healing in AgriIoT*: Sahu & Tripathi (Quality & Quantity 60(2):3443–3471, 2025) — recovers corrupted/missing readings, a data-level rather than node-level problem.
    - *AgriIoT security, detection only*: SFEDRL-IDS (Benameur & Dahane, Cluster Computing 28(6), 2025) — federated DRL IDS on an irrigation system, 98.67% multiclass accuracy, stops at detection.
*   **The surviving, defensible gap**: no prior work measures recovery from a *security intrusion* on a *constrained agricultural node* under *explicit compute and connectivity limits*. This is addressed empirically in this project (see `experiments/recovery/` and Section III-E / V-A of the manuscript), which found recovery gains degrade gracefully but measurably as constraints worsen (67.1% mean MTTR improvement overall, falling to 40.9% at worst-case connectivity and compute).
*   **Dataset note**: an AgriIoT-specific labeled flow dataset now exists — Farm-flow (Ferreira et al., *Computers and Electrical Engineering* 121:109892, 2025) — which the current experiments do not use. Revalidating both tiers on it is the top follow-up item.

These identified gaps collectively underscore the need for continued, innovative research to develop robust, efficient, and context-aware AI-based IDS solutions capable of securing the unique and challenging environment of Agricultural IoT.
