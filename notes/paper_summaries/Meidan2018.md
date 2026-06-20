# Paper Summary: Meidan2018

-   **BibTeX Key**: Meidan2018
-   **Title**: N-BaIoT: Network-based Detection of IoT Botnet Attacks Using Deep Autoencoders
-   **Authors**: Yair Meidan, Michael Bohadana, Yael Mathov, Yisroel Mirsky, Dominik Breitenbacher, Asaf Shabtai, and Yuval Elovici
-   **Year**: 2018
-   **Publication Venue**: IEEE Pervasive Computing

---

## Research Objective
To propose and empirically evaluate a novel network-based anomaly detection method, N-BaIoT, which extracts behavioral snapshots of the network and uses deep autoencoders to detect anomalous network traffic emanating from compromised IoT devices, specifically targeting IoT botnet attacks. The objective is to achieve accurate and instantaneous detection, including of previously unseen botnet behaviors, with a low false alarm rate.

## Problem Addressed
The rapid proliferation of IoT devices, which are more easily compromised than desktop computers, has led to a significant increase in IoT-based botnet attacks. Existing botnet detection methods often focus on early operational steps (propagation, C&C communication) and can be bypassed by continuously evolving botnets. Host-based detection techniques are often unrealistic for IoT due to device constraints (limited computation, memory, energy), lack of manufacturer support for installing host-based anomaly detectors, and the need for a non-distributed solution in enterprise scenarios with numerous IoT devices. A pressing need exists for a centralized, highly effective, and accurate method to detect compromised IoT devices launching attacks, including zero-day botnets.

## Methodology
The proposed method, N-BaIoT, relies on deep autoencoders for each device, trained on statistical features extracted from benign traffic data.
*   **Main Stages**:
    1.  **Data Collection**: Raw network traffic data (pcap format) is captured using port mirroring on the switch through which organizational traffic flows. Benign traffic is collected immediately following an IoT device's installation to ensure clean training data.
    2.  **Feature Extraction**: Whenever a packet arrives, behavioral snapshots of hosts and protocols are taken. 115 traffic statistics are extracted over five temporal windows (100ms, 500ms, 1.5sec, 10sec, and 1min). These features capture packet size (mean, variance), packet count, and packet jitter, aggregated by Source IP, Source MAC-IP, Channel, and Socket. These features are designed to be computed incrementally and rapidly for real-time detection.
    3.  **Anomaly Detector Training**:
        *   **Model**: Deep Autoencoders are used as the base anomaly detector, with a separate model maintained for each IoT device. Autoencoders are trained *only* on benign instances to learn normal behaviors, succeeding at reconstructing normal observations but failing on abnormal ones (anomalies).
        *   **Architecture**: Each autoencoder has an input layer dimension equal to the number of features (115). It includes four hidden encoder layers (decreasing sizes: 75%, 50%, 33%, 25% of input dimension) and four corresponding decoder layers (increasing sizes). The code layer between encoder/decoder performs efficient dimensionality reduction.
        *   **Hyperparameter Optimization**: Learning rate (η) and number of epochs are optimized using an optimization set (DSopt) to minimize the Mean Squared Error (MSE) between the model's input and its reconstructed output. This prevents overfitting the training set (DStrn).
        *   **Anomaly Threshold (`tr*`)**: Calculated as the sum of the sample mean and standard deviation of MSE over DSopt. An instance with MSE > `tr*` is considered anomalous.
        *   **Window Size (`ws*`)**: To reduce false alarms (single instances often generate 5-7% false positives), the abnormality decision is based on a sequence of instances. `ws*` is the shortest sequence length for which a majority vote produces 0% FPR on DSopt.
    4.  **Continuous Monitoring**: The optimized model is applied to continuously observed packets. A majority vote over a window of `ws*` instances determines if an entire stream is anomalous, triggering an alert for potential malicious activity.
*   **Comparison Baselines**: Local Outlier Factor (LOF), One-Class SVM, and Isolation Forest, all optimized with `tr` and `ws` for fair comparison.
*   **Experimental Setup**: Lab setup replicating a typical organizational data flow. Nine commercial IoT devices (e.g., Danmini Doorbell, Ecobee Thermostat, Philips Baby Monitor, Security Cameras, Samsung Webcam) were infected with real-world Mirai and BASHLITE botnets. Network traffic was captured via port mirroring using Wireshark.

## ML Models Used
*   **Deep Autoencoders**: Core model for unsupervised anomaly detection.
*   **Comparison Algorithms**: Local Outlier Factor (LOF), One-Class Support Vector Machine (OC-SVM), Isolation Forest (IF).

## Datasets Used
The **N-BaIoT dataset** was generated and is publicly available (http://archive.ics.uci.edu/ml/datasets/detection of IoT botnet attacks N BaIoT). It consists of real network traffic captured from nine commercial IoT devices infected with two widely known IoT botnet families: **Mirai** and **BASHLITE**. Traffic data was collected before and after infection.
*   **Mirai Attacks**: Scan, Ack, Syn, UDP, UDPplain.
*   **BASHLITE Attacks**: Scan, Junk, UDP, TCP, COMBO.

## Preprocessing
*   **Data Collection**: Raw PCAP data.
*   **Feature Extraction**: 115 traffic statistics are extracted incrementally from packets over multiple time windows.
*   **Data Splitting**: Each device's benign data was chronologically divided into three equidimensional sets: DStrn (training), DSopt (optimization), and DStst (test, with malicious data appended).

## Evaluation Metrics
*   True Positive Rate (TPR)
*   False Positive Rate (FPR)
*   Detection Time (milliseconds)

## Results
*   **Exceptional Detection (TPR)**: The N-BaIoT method achieved a **TPR of 100%**, successfully detecting every single attack launched by every compromised IoT device.
*   **Low False Alarm Rate (FPR)**: Demonstrated a mean FPR of **0.007 ± 0.01**, which was significantly lower and more consistent than SVM (0.026 ± 0.029), Isolation Forest (0.027 ± 0.041), and LOF (0.086 ± 0.081).
*   **Instantaneous Detection Time**: Required only **174 ± 212 milliseconds** to detect the attacks, often much less. This enables stopping attacks in less than a second, a substantial reduction from typical DDoS attack durations.
*   **Autoencoder Superiority**: Deep autoencoders consistently outperformed LOF, OC-SVM, and IF in terms of TPR, FPR, and detection time for most devices. This is attributed to their ability to learn nonlinear structures and fit common patterns, and their constrained complexity preventing learning trivial identity functions.
*   **Traffic Predictability**: The difficulty in capturing normal traffic behavior (and thus FPR) varied among IoT devices, correlated with device capabilities and network communications. Devices with more diverse capabilities (e.g., Philips B120N/10 baby monitor) had higher FPR.

## Limitations
*   The evaluation was conducted in a controlled lab environment rather than a live, diverse real-world deployment, potentially limiting the generalizability of some findings.
*   The approach focuses on network-based detection, assuming central monitoring.
*   The adaptability of the method for devices with highly variable or less predictable traffic behaviors requires further investigation.

## Future Work
*   Further define and investigate the subject of traffic predictability, both theoretically and empirically, and its formalization with static and dynamic device features.
*   Evaluate transfer learning techniques to assess models trained on specific devices when applied to identical devices in different organizational networks, to save training time and detect pre-contaminated devices.

## Research Gaps Identified
*   Lack of effective methods for detecting IoT botnet attacks, especially in the "execution of attack" phase.
*   Unsuitability of host-based detection for many IoT devices due to constraints.
*   Need for anomaly detection methods capable of identifying previously "unseen" botnet behaviors.
*   Scarcity of publicly available datasets for IoT botnets.

## Relevance to AgriIoT IDS
**Extremely relevant**. This paper provides compelling evidence for the effectiveness of deep autoencoders for *unsupervised, network-based anomaly detection* of IoT botnet attacks. This is a crucial aspect for AgriIoT, as botnets pose a significant threat, and detecting zero-day attacks without labeled data is essential. The paper's emphasis on instantaneous detection, low false alarm rates, and resource-efficient (network-based, not on-device) anomaly detection aligns perfectly with the requirements of AgriIoT environments. The use of real IoT device traffic in the N-BaIoT dataset makes the findings directly applicable. The future work on traffic predictability and transfer learning also offers valuable directions for enhancing AgriIoT security.
