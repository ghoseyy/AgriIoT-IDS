# Thilakarathne, N.N.; Abu Bakar, M.S.; Abas, P.E.; Yassin, H. (2025) - A novel cyber threat intelligence platform for evaluating the risk associated with smart agriculture

**Summary:**

This research introduces a novel cyber threat intelligence platform designed to evaluate and mitigate cybersecurity risks in smart agriculture, leveraging deception technology. The paper highlights the increasing vulnerability of IoT devices in agriculture to cyber threats and the lack of adequate security measures in the sector. It proposes a platform that uses deception technology, such as honeypots, to lure cybercriminals, monitor their activities, and gather threat intelligence data.

The platform's design involves creating a smart farming ecosystem with cloud-enabled infrastructure (using AWS IoT Core and DynamoDB) and integrating a T-Pot honeypot server to simulate vulnerable systems. The authors conducted a 21-day monitoring phase, during which over 700,000 attacks were recorded. The analysis of this data revealed key attack patterns, including the origins of attacks (predominantly China, the United States, and Russia), the types of services targeted (TCP and UDP), and the use of proxies/VPNs by attackers to conceal their identities. The study also identified common brute-force attempts using default credentials and targeting specific vulnerable ports.

To validate the findings, a second platform was designed using a Raspberry Pi device and an opencanary honeypot, exposed to the internet. This validation setup confirmed that even without cloud infrastructure, smart farming environments remain highly vulnerable to cyber-attacks, with similar attack patterns observed. Based on the gathered insights, the paper provides actionable recommendations for stakeholders (farmers, solution suppliers, government) to enhance security measures, emphasizing enhanced security, software updates, employee training, network segmentation, regular assessments, collaboration, compliance, incident response, and investment in threat intelligence tools.

**Key Contributions:**

*   **Cyber Threat Intelligence Platform:** Development of a novel platform using deception technology (honeypots) to gather threat intelligence in smart agriculture.
*   **Real-world Attack Data:** Collection and analysis of over 700,000 cyber-attacks targeting a simulated smart farming ecosystem over 21 days.
*   **Attack Pattern Identification:** Detailed insights into attack origins, targeted services, attacker tactics (e.g., use of proxies, default credentials), and vulnerable ports.
*   **Validation Setup:** Confirmation of findings through a secondary validation platform using Raspberry Pi and opencanary honeypot.
*   **Actionable Recommendations:** Provision of comprehensive, stakeholder-specific recommendations for mitigating cyber risks in smart agriculture.
*   **Addressing Research Gap:** First-of-its-kind research presenting a deception technology-based approach for cyber threat intelligence in smart agriculture.