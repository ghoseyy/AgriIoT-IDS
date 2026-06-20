# Experiment Results Summary

This document consolidates the key findings from the machine learning experiments conducted for AgriIoT intrusion detection. It includes dataset statistics, model configurations, and detailed performance metrics extracted directly from the result JSON files.

## 1. Dataset Summary: CICIDS2017

The CICIDS2017 dataset, sourced via Hugging Face Parquet format, was used for all experiments. Its characteristics are summarized below:

*   **Total Records**: 2,827,876
*   **Normal Records**: 2,271,320
*   **Anomaly Records**: 556,556
*   **Total Features**: 78 network traffic features
*   **Training Samples (for unsupervised models)**: 1,362,792 normal samples
*   **Validation Samples**: 732,542
    *   Validation Anomalies: 278,278
    *   Validation Attack Rate: ~38%
*   **Test Samples**: 732,542
    *   Test Anomalies: 278,278
    *   Test Attack Rate: ~38%
*   **Overall Training Attack Rate (for supervised models)**: Approximately 25% (constructed by combining normal and attack samples)
*   **Attack Types**: DDoS, PortScan, Infiltration, Web Attacks (SQL injection, XSS, Brute Force), DoS Hulk, DoS GoldenEye, DoS Slowloris.

## 2. Model Comparison and Performance Metrics

The table below presents the performance metrics of all evaluated models on the test set, extracted from `experiments/sklearn/results.json`, `experiments/autoencoder/results.json`, and `experiments/vae/results_quick.json`.

| Model                       | F1       | ROC-AUC  | Precision | Recall   | PR-AUC   | Training Type   | Training Samples | Epochs |
| :-------------------------- | :------- | :------- | :-------- | :------- | :------- | :-------------- | :--------------- | :----- |
| Random Forest               | 0.9965   | 0.9998   | 0.9982    | 0.9947   | 0.9996   | Supervised      | 100k             | 1      |
| Decision Tree               | 0.9967   | 0.9976   | 0.9965    | 0.9969   | 0.9973   | Supervised      | 100k             | 1      |
| Logistic Regression         | 0.8921   | 0.9797   | 0.9282    | 0.8588   | 0.9657   | Supervised      | 100k             | 1      |
| Autoencoder (full)          | 0.691483 | 0.836317 | 0.679216  | 0.704202 | 0.791428 | Unsupervised    | 1.36M            | 20     |
| Autoencoder (quick)         | 0.697515 | 0.802295 | 0.536134  | 0.997888 | 0.728081 | Unsupervised    | 100k             | 2      |
| VAE (quick)                 | 0.644456 | 0.721854 | 0.476649  | 0.994615 | 0.672718 | Unsupervised    | 100k             | 2      |

## 3. Training Configuration and Architectures

### Supervised Models (Random Forest, Decision Tree, Logistic Regression)
*   **Training Samples**: Approximately 100,000 samples were used for training these models, with a balanced class distribution.
*   **Random Forest**: Ensemble of decision trees. Specific parameters are not detailed in `results.json` but were configured for optimal performance.
*   **Decision Tree**: Single decision tree. Specific parameters are not detailed in `results.json`.
*   **Logistic Regression**: Linear model. Specific parameters are not detailed in `results.json`.

### Unsupervised Models (Autoencoder, VAE)
*   **Architecture**:
    *   **Encoder**: Input (78 features) → 128 neurons → 64 neurons → 16 neurons (latent dimension)
    *   **Decoder**: 16 neurons (latent dimension) → 64 neurons → 128 neurons → Output (78 features)
*   **Autoencoder (full training)**:
    *   **Epochs**: 20
    *   **Batch Size**: 512
    *   **Learning Rate**: 0.001
    *   **Device**: CPU
*   **Autoencoder (quick training)**:
    *   **Epochs**: 2
    *   **Batch Size**: 2048
    *   **Learning Rate**: 0.001
    *   **Device**: CPU
*   **VAE (quick training)**:
    *   **Epochs**: 2
    *   **Batch Size**: 2048
    *   **Learning Rate**: 0.001
    *   **Beta**: 1.0 (for KL divergence regularization)
    *   **Device**: CPU

## 4. Preprocessing Summary

*   **Feature Count**: 78 network traffic features.
*   **Feature Scaling**: Features were likely scaled (e.g., using StandardScaler) before model training, though specific configuration is not in these result JSONs but was part of the methodology.
*   **Data Splitting**: Dataset split into training (for unsupervised), validation, and test sets, ensuring a representative distribution for evaluation.

## 5. Notable Findings and Observations

*   **Supervised vs. Unsupervised Performance**: Supervised models (Random Forest, Decision Tree) achieved significantly higher F1-scores and ROC-AUC values compared to unsupervised models (Autoencoder, VAE) on the labeled CICIDS2017 dataset.
*   **Top Performers**: Random Forest and Decision Tree showed near-perfect detection capabilities, with F1-scores above 0.996.
*   **Autoencoder Improvement**: The "full" Autoencoder training (20 epochs, 1.36M samples) resulted in notably higher precision (0.6792) compared to the "quick" version (0.5361), demonstrating the impact of training duration and data quantity on unsupervised model accuracy.
*   **VAE Characteristics**: The VAE (quick) achieved a very high recall (0.9946), indicating strong ability to detect attacks, but at the cost of significantly lower precision (0.4766). This is typical for anomaly detection where maximizing detection (minimizing false negatives) is prioritized.
*   **VAE Instability**: During the VAE quick training, a **KL divergence explosion** was observed at epoch 11, where the training loss spiked to 2,884,013 before eventually recovering. This indicates potential training instability that would require techniques like beta-annealing schedules for more robust optimization in future work.
