# Pasca, E.M.; Delinschi, D.; Erdei, R.; Baraian, I.; Matei, O.D. (2025) - A Vulnerable-by-Design IoT Sensor Framework for Cybersecurity in Smart Agriculture

**Summary:**

This paper introduces a "vulnerable-by-design" containerized IoT framework specifically developed for cybersecurity research in smart agriculture. The framework simulates both cybersecurity vulnerabilities and sensor health anomalies within agricultural settings, addressing critical research gaps related to reproducibility, interaction between sensor health and security threats, and real-world validation. The authors use a tomato greenhouse case study to demonstrate how combined DDoS attacks and sensor faults (specifically, a stuck fault) can mask critical temperature increases, leading to potential yield reductions.

The framework implements various cybersecurity vulnerabilities including Broken Object Level Authorization (BOLA), DDoS botnet participation, and command injection, along with four types of sensor faults: stuck, drift, spike, and dropout readings. The study highlights the complex interplay between these elements, revealing that sensor faults can either mask or amplify the detectability of security attacks. For instance, spike faults surprisingly enhanced BOLA attack detectability, while dropout faults masked command injection attacks.

A key contribution is the systematic generation of labeled datasets that capture both security vulnerabilities and sensor health anomalies, providing a valuable resource for training machine learning models for attack detection. LSTM-based validation achieved moderate recall and strong precision, demonstrating the utility of the generated dataset. The paper emphasizes the practical implications for agricultural monitoring, showing how security attacks combined with sensor faults can directly impact crop production and farm profitability.

**Key Contributions:**

*   **Vulnerable-by-Design Framework:** Development of a containerized IoT framework for smart agriculture, integrating both cybersecurity vulnerabilities and sensor health anomalies.
*   **Reproducibility and Testbed:** Addresses reproducibility challenges through an open-source, containerized testbed.
*   **Interaction Analysis:** Explores the complex interplay between sensor faults (stuck, drift, spike, dropout) and cybersecurity attacks (BOLA, DDoS, command injection), identifying masking and amplification effects.
*   **Dataset Generation:** Generates structured, labeled datasets for machine learning-based attack detection, suitable for LLM integration.
*   **Agricultural Impact Quantification:** Demonstrates how combined attacks and sensor faults can lead to quantifiable agricultural impacts, such as yield reduction in a tomato greenhouse.
*   **LSTM Validation:** Validates the utility of the generated dataset with LSTM models for attack detection.