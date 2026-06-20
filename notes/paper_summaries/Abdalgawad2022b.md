# Paper Summary: Abdalgawad2022b

-   **BibTeX Key**: Abdalgawad2022b
-   **Title**: Generative Deep Learning to Detect Cyberattacks for the IoT-23 Dataset
-   **Authors**: N. Abdalgawad, A. Sajun, Y. Kaddoura, I. A. Zualkernan, and F. Aloul
-   **Year**: 2022
-   **Publication Venue**: IEEE Access

---

## Research Objective
To explore the use of generative deep learning methods, specifically Adversarial Autoencoders (AAE) and Bidirectional Generative Adversarial Networks (BiGAN), for detecting and classifying cyberattacks in IoT networks. The paper also aims to demonstrate the capability of BiGANs in detecting novel or zero-day attacks.

## Problem Addressed
The rapid growth of IoT devices leads to a vast attack surface, making them vulnerable to botnet-driven Distributed Denial of Service (DDoS) and other cyberattacks. Traditional signature-based Intrusion Detection Systems (IDS) are time-consuming to update and ineffective against zero-day attacks. There is a need for automated, robust, and adaptive IDS solutions that can handle both known and unknown attack types.

## Methodology
The study proposes and evaluates three generative deep learning models using the complete IoT-23 dataset:
*   **Adversarial Autoencoders (AAE)**: An autoencoder integrated with a Generative Adversarial Network (GAN) to reduce overfitting and influence latent space distribution.
    *   **Architecture**: Encoder maps 27 features to a 6-dimensional latent representation. A Generator reconstructs data from latent features. A Discriminator distinguishes between generated features and random samples.
    *   **Intrusion Detection**: Encoding test data to latent space, followed by a classifier (e.g., K-Nearest Neighbor - KNN).
    *   **Training**: 1000 epochs, batch size 10, Adam optimizer (LR 10^-4). Loss: Mean Squared Error (MSE) for autoencoder, Binary Cross Entropy for discriminator/generator.
*   **Bidirectional Generative Adversarial Networks (BiGAN)**: Extends GANs by adding an encoder to map data back to the latent space, allowing the discriminator to learn on concatenated inputs (real_data, encoded_latent) vs (generated_data, random_latent).
    *   **Architecture**: Encoder maps 27 features to an 8-dimensional latent representation. Generator produces network data from noise. Discriminator evaluates (input_data, encoded_latent) and (generated_data, random_latent).
    *   **Training**: 1000 epochs, batch size 32, Adam optimizer (LR 0.0002).
*   **BiGAN to Detect Unknown Attacks**: A BiGAN specifically adapted for zero-day attack detection.
    *   **Training**: Trained on both benign and known anomalous data.
    *   **Testing**: Synthetic unknown anomalies (created by randomly mutating 1-2 features) were injected to test detection capability.
    *   **Training parameters**: 40,000 epochs, batch size 32, Adam optimizer (LR 0.003), latent space 8.
*   **Baselines**: K Nearest Neighbor (KNN) and Random Forest (RF) were used for comparison.
*   **Evaluation Strategy**: Stratified 10-fold sampling for evaluation.

## ML Models Used
*   **Generative Deep Learning**:
    *   Adversarial Autoencoders (AAE)
    *   Bidirectional Generative Adversarial Networks (BiGAN)
*   **Traditional Machine Learning (for baseline comparison and post-processing)**:
    *   K-Nearest Neighbor (KNN)
    *   Random Forest (RF)

## Datasets Used
**IoT-23 dataset**: This dataset, based on network traffic from IoT devices, includes 20 malware and 3 benign captures. The benign captures were from real IoT devices (Somfy door lock, Philips Hue, Amazon Echo). `.pcap` files were processed through Zeek Network Analyzer to generate log files, which were then manually analyzed and labeled. It includes DDoS and various botnets like Mirai, Okiruk, Torii. Over 1.8 million network flows were used.

## Preprocessing
*   **Feature Removal**: `local_orig`, `local_resp` (empty), IP addresses, port numbers, `history` (sequence of values). Highly correlated features (`orig_ip_bytes`, `resp_ip_bytes`) were also dropped.
*   **Class Filtering**: Extreme minority classes with less than 100 samples were dropped (e.g., 'C&C-FileDownload', 'FileDownload', 'C&C-Torii', 'C&C-HeartBeat-FileDownload', 'PartOfAHorizontalPortScan-Attack', 'Okiru-Attack', 'C&C-Mirai').
*   **Missing Value Imputation**: Null values in `orig_bytes`, `resp_bytes`, and `duration` were replaced with the mean value of respective features.
*   **Data Type Conversion**: `duration` feature recoded from `timedelta64` to time in seconds.
*   **Duplicate Removal**: Duplicates were removed from flows after feature dropping.
*   **Categorical Encoding**: Categorical features (`service`, `proto`, `conn_state`) were one-hot encoded.
*   **Normalization**: Data normalized between 0 and 1 using min-max scaling.
*   **Class Imbalance Handling**: Combination of Random UnderSampling and SMOTE to downsample the majority class (to 25% of its original size) and upsample minority classes (to 10% of the downsampled majority class).

## Evaluation Metrics
*   **Accuracy**
*   **Recall**
*   **Precision**
*   **F1-score**: Prioritized for imbalanced datasets as it provides more meaningful results.

## Results
*   **Generative Models Outperform Baselines**: Both AAE + KNN and BiGAN + KNN models significantly outperformed traditional machine learning techniques (RF and KNN baselines), which had F1-scores as low as 0.02 in some instances.
*   **High F1-Scores**: AAE and BiGAN-based models achieved F1-Scores of **0.99** for known attack detection.
*   **Unknown Attack Detection**: The BiGAN trained to detect unknown anomalies was very effective, achieving F1-Scores of **1** when mutations were increased, and a decent F1-Score of **0.85** even for a single mutation.
*   **Performance Similarity**: AAE + KNN and BiGAN + KNN showed statistically similar performance across all metrics.
*   **Lower F1-Scores for Specific Attacks**: Classes like C&C-PartOfAHorizontalPortScan and C&C-HeartBeat had F1-scores of 0.93.

## Limitations
*   Generative models (AAE and BiGAN) were able to represent the data but struggled to generate data coming from the exact same distribution as real data, as evidenced by LOO and GAN-train evaluations where classifiers trained on generated data performed poorly on real data (or vice-versa).
*   The lower F1-scores for C&C related attacks suggest challenges in distinguishing certain complex attack types.
*   The study used a specific set of attacks and IoT devices from the IoT-23 dataset, limiting generalizability without further validation.

## Future Work
*   Retrieve additional features from `.pcap` files for richer analysis.
*   Increase the number of instances for minority classes to further improve model performance.
*   Explore shared features between different attacks to potentially detect new, unknown attacks.

## Research Gaps Identified
*   Limitations of traditional signature-based IDS against zero-day and evolving attacks.
*   Challenges in effectively detecting and classifying diverse IoT cyberattacks, particularly in handling imbalanced datasets.
*   The need for generative models to effectively detect unknown anomalies.

## Relevance to Agricultural IoT IDS
**Highly relevant**. This paper demonstrates the significant potential of generative deep learning models (AAE, BiGAN) for detecting both known and *unknown (zero-day)* cyberattacks in IoT networks, using an IoT-specific dataset (IoT-23). This is crucial for AgriIoT, where novel attack patterns might emerge, and manual labeling of attack data is difficult. The study's focus on handling imbalanced datasets and its success in outperforming traditional ML baselines make its approach highly applicable to AgriIoT IDS, where diverse and rare attack types could be prevalent and data often imbalanced. The methodology for detecting unknowns offers a promising avenue for proactive security in AgriIoT.
