# Business Impact Report

## Executive context

This analysis uses the public IBM Telco Customer Churn snapshot, which describes whether a customer departed within the last month and includes demographic, service, contract, charge, and tenure fields [1]. The reproducible CSV source is hosted in IBM’s public GitHub repository [2], with the commonly used Kaggle listing provided for recruiter-friendly provenance [3]. The dataset contains **7,043 customers**, an observed churn rate of **26.54%**, monthly recurring charges of **$456,116.60**, and **$139,130.85** in monthly recurring revenue at risk.

## What the analysis found

| Finding | Evidence | Business meaning |
|---|---:|---|
| Month-to-month contracts are the highest-risk group. | **42.7% churn** vs **2.8%** for two-year contracts, or **15.1× higher**. | Contract commitment is the clearest retention lever in the snapshot. |
| Risk is concentrated early in the relationship. | **0–12 month churn: 47.4%** vs **9.5%** for 49+ months. | The first-year customer journey is the highest-value intervention window. |
| Fiber optic customers show elevated churn. | **41.9%** churn vs **19.0%** for DSL, a **22.9-point gap**. | Investigate service quality, onboarding, pricing, and expectation gaps before broad discounting. |
| Electronic-check customers are a payment-friction segment. | **45.3%** churn vs **17.1%** for other payment methods. | Payment migration and billing-experience improvements are testable retention actions. |

## Three recommendations and scenario impact

**1. Launch a first-year onboarding and save journey.** Prioritize the **2,186 customers with 0–12 months tenure**, who carry **$68,954.25** of monthly revenue at risk. A conservative scenario in which the program protects **10% of that exposed run-rate** implies **$6,895 monthly revenue retained**, or **$82,745 annualized**, before campaign costs. The program should use early usage education, proactive support, and a 90-day contract-conversion offer rather than a blanket discount.

**2. Run a contract-conversion campaign for month-to-month customers.** Target the highest-risk contract population with a value-based offer for one-year or two-year commitment. The dataset’s most addressable combined segment—month-to-month customers using electronic checks—contains **1,850 customers**, has **53.73% churn**, and represents **$77,315.60** in monthly revenue at risk. Protecting **10%** of that segment’s exposed run-rate would retain approximately **$7,732 monthly** or **$92,777 annualized**. This is a scenario, not a causal forecast; it should be validated through a controlled test.

**3. Reduce billing friction and investigate fiber-service dissatisfaction.** Offer electronic-check customers a guided migration to automatic bank transfer or credit card, while pairing the payment intervention with a fiber service-quality diagnostic. Electronic-check customers alone represent **$84,288.75** of monthly revenue at risk. A **10% recovery scenario** implies **$8,429 monthly** or **$101,147 annualized** revenue retained. Track payment migration, complaint rate, support contacts, and 30/90-day churn as experiment metrics.

## Measurement and limitations

The recommended impact figures are **transparent sensitivity scenarios**, calculated as 10% of observed monthly revenue at risk and annualized by multiplying by 12. They are not causal estimates. The source is a customer snapshot without calendar transaction dates, so the dashboard uses retention by tenure band rather than a true month-over-month cohort trend. `Estimated CLV` is the observed `TotalCharges` field and should not be interpreted as predictive lifetime value without margin, discount, and future-survival assumptions.

## References

[1]: https://www.ibm.com/docs/en/cognos-analytics/12.1.x?topic=samples-telco-customer-churn "IBM: Telco customer churn sample documentation"

[2]: https://github.com/IBM/telco-customer-churn-on-icp4d/blob/master/data/Telco-Customer-Churn.csv "IBM GitHub: Telco-Customer-Churn.csv"

[3]: https://www.kaggle.com/datasets/blastchar/telco-customer-churn "Kaggle: Telco Customer Churn"
