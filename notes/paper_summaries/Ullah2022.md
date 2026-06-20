# Paper Summary: Ullah2022

-   **BibTeX Key**: Ullah2022
-   **Title**: Design and Development of RNN Anomaly Detection Model for IoT Networks
-   **Authors**: Imtiaz Ullah and Qusay H. Mahmoud
-   **Year**: 2022
-   **Publication Venue**: IEEE Access

---

## Research Objective
To design and develop novel deep learning models for anomaly detection in IoT networks, specifically focusing on Recurrent Neural Network (RNN) variants (LSTM, BiLSTM, GRU), hybrid models combining Convolutional Neural Networks (CNN) with RNNs, and lightweight binary classification models, while addressing issues like overfitting and class imbalance.

## Problem Addressed
The increasing growth of the Internet of Things (IoT) has led to a variety of cyberattacks on computer systems and networks, making cybersecurity an increasingly difficult issue to manage. Standard Intrusion Detection Systems (IDS) are often incapable of rapidly and reliably identifying complex and varied IoT network attacks, particularly low-frequency ones. Deep learning models are prone to overfitting, which compromises their resilience and effectiveness against zero-day cyberattacks.

## Methodology
The study proposes and evaluates several deep learning architectures:
*   **RNN-based Models**: LSTM, BiLSTM, and GRU models for multiclass and binary classification.
    *   **Architecture**: Input layer (64 features), four recurrent layers (LSTM, BiLSTM, or GRU), four activation layers (LeakyReLU), four normalization layers (Layer Normalization), four activity regularization layers (l1-l2), four dropout layers, one dense layer (512 neurons, LeakyReLU), and an output layer (neurons depend on number of classes).
    *   **Regularization**: Kernel, bias, and activity regularizers (l1-l2) were implemented at RNN layers. Dropout layers were used to mitigate overfitting. Early stopping (5 iterations of patience) and 5-fold cross-validation were also employed.
*   **Hybrid Models (CNN-RNN)**: Combining CNN and RNN (CNN-LSTM, CNN-BiLSTM, CNN-GRU).
    *   **Architecture**: Input layer (64 features), 1D Convolutional layer, followed by two hidden layers of recurrent neural networks (LSTM, BiLSTM, or GRU), activation, normalization, regularization, dropout layers, average pooling layer, dense layer (512 neurons, LeakyReLU), and output layer.
*   **Lightweight Binary Classification Models**: Single RNN layer (LSTM, BiLSTM, or GRU) as a hidden layer.
*   **Feature Selection**: Recursive Feature Elimination (RFE) using a Random Forest algorithm selected 64 features from the IoT-DS2 dataset.
*   **Class Imbalance Handling**: Class weights (calculated based on instances per class) and Borderline SMOTE (Synthetic Minority Over-sampling Technique) were used to balance datasets.
*   **Training**: Adam optimizer, 100 epochs, batch size 128 (for RNN models). Experiments conducted using Keras with TensorFlow backend on Google Colab.

## ML Models Used
*   **Recurrent Neural Networks (RNN)**:
    *   Long Short Term Memory (LSTM)
    *   Bidirectional Long Short Term Memory (BiLSTM)
    *   Gated Recurrent Unit (GRU)
*   **Convolutional Neural Networks (CNN)**: 1D CNN for feature learning.
*   **Hybrid Models**: Combinations of CNN and RNN variants.

## Datasets Used
A wide range of publicly available IoT network intrusion datasets were utilized:
*   NSLKDD
*   BoT-IoT [@Koroniotis2019]
*   IoT Network Intrusion (IoT-NI) [@Kang]
*   IoT-23 [@Parmisano2020]
*   MQTT-IoT-IDS2020 (MQTT) [@Hindy2020]
*   MQTTset [@Vaccari2020]
*   **IoT-DS2**: A combined dataset created from the above IoT datasets, comprising 19 classes (1 normal, 18 attack types).
Features were extracted from `.pcap` files using CICFlowmeter.

## Preprocessing
*   **Feature Removal**: Flow ID, source IP, source port, destination IP, timestamp were removed as they characterize communication inside specific IoT networks.
*   **Non-numeric Transformation**: Non-numeric features were converted into numeric features.
*   **Duplicate Removal**: Redundant instances (produced when `.pcap` data was converted to `.csv`) were removed.
*   **Normalization**: Features were normalized within the range (-1, 1) to eliminate extreme values and speed up calculations.
*   **Missing Value Imputation**: Mean imputation was used to fill missing values.
*   **Class Imbalance Handling**: Class weights and Borderline SMOTE (K=6 to 10 neighbors) were applied.

## Evaluation Metrics
*   **Accuracy**
*   **Precision**
*   **Recall (Sensitivity)**
*   **F1-score**
*   **TNR (True Negative Rate)**
*   **FPR (False Positive Rate)**
*   **FNR (False Negative Rate)**
*   **PPV (Positive Predictive Value)**
*   **NPV (Negative Predictive Value)**
*   **ROC AUC** curves were plotted for validation and testing sets.

## Results
*   **High Performance**: Proposed multiclass and binary classification models achieved high accuracy, precision, recall, and F1 scores across various datasets, outperforming previously published deep learning implementations.
*   **BiLSTM Superiority**: BiLSTM models generally outperformed LSTM and GRU models in both standalone RNN and CNN-RNN hybrid configurations.
*   **Multiclass Classification (RNN)**:
    *   NSLKDD: BiLSTM 99.82% Acc.
    *   BoT-IoT: High detection rates (>99.50% for Normal, DoS, Scan, Theft).
    *   IoT-DS2: BiLSTM 99.48% Precision, 99.46% Recall.
*   **Multiclass Classification (CNN-RNN Hybrid)**:
    *   Improved detection rates and reduced FPR/FNR compared to standalone RNNs.
    *   NSLKDD: CNNBiLSTM showed improved precision and recall.
    *   BoT-IoT: Improved detection rates, reduced FPR (0.02%), FNR (0.06%) for CNNBiLSTM.
    *   IoT-23: CNNBiLSTM 99.87% detection rate.
    *   MQTT/MQTTset: Achieved very high precision and recall (e.g., CNNBiLSTM FPR 0.0016%, FNR 0.03% for MQTT).
*   **Lightweight Binary Classification**:
    *   Achieved high accuracy (e.g., MQTTset 99.98% Acc for BiLSTM).
    *   IoT-DS2: BiLSTM 99.81% detection rate.
*   **SMOTE Effectiveness**: Borderline SMOTE showed better overall detection rate improvement than class weights, especially for minority classes, though it required more computing resources.
*   **Overfitting Mitigation**: Regularizers, dropout, and early stopping effectively reduced overfitting.

## Limitations
*   Requires a significant volume of data to outperform other techniques, which could be a challenge for small AgriIoT deployments.
*   Borderline SMOTE, while effective, requires more computing resources.
*   R2L and U2R attacks in NSLKDD had low detection rates due to rarity.
*   Certain attack types (MITM, Heartbeat, Malformed Data, C&C) in IoT-DS2 had precision rates below 98%.
*   Some models in related work (e.g., Ge et al. [41, 47]) might overfit if source port is used as a feature, as attacks are often from specific ports.

## Future Work
*   Investigate more deep learning approaches for anomaly detection in IoT networks.
*   Adopt various optimization techniques to boost detection capability on small datasets.
*   Develop and evaluate ensemble techniques for LSTM, BiLSTM, and GRU models.

## Research Gaps Identified
*   Traditional IDSs are inadequate for rapidly and reliably identifying complex and varied IoT network attacks, especially low-frequency ones.
*   The impact of overfitting in deep learning algorithms for NIDS needs continuous attention to maintain resilience against zero-day attacks.
*   Need for robust anomaly detection in diverse IoT network traffic.
*   Addressing class imbalance efficiently.

## Relevance to Agricultural IoT IDS
**Highly relevant**. This paper explores advanced deep learning models (RNNs, CNNs, and hybrid architectures) for anomaly detection across a wide range of IoT datasets, directly addressing the need for robust IDS in dynamic IoT environments. The focus on deep learning's ability to handle complex network traffic patterns and its strategies to mitigate overfitting and class imbalance are critical for AgriIoT, which can feature diverse and evolving attack patterns, as well as imbalanced data (many normal events, few attack events). The development of lightweight models for binary classification also offers potential for deployment on resource-constrained AgriIoT devices.
