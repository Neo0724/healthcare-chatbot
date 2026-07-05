## Table of Contents

| Section A......................................................................................................................................... 3   |
|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| Project Scope Overview.............................................................................................................. 3                 |
| Objective................................................................................................................................. 3           |
| Benefits ................................................................................................................................... 3         |
| Stakeholder Mapping.................................................................................................................. 6                |
| Project Team Structure ............................................................................................................. 10                |
| Risk Management ..................................................................................................................... 11               |
| Risk 1.................................................................................................................................... 12          |
| Risk 2.................................................................................................................................... 13          |
| Risk 3.................................................................................................................................... 14          |
| Risk 4.................................................................................................................................... 14          |
| Migration Strategy .................................................................................................................... 15             |
| Re-architecture Strategy........................................................................................................ 15                    |
| Lift-and-Shift strategy........................................................................................................... 16                  |
| Re-platforming strategy ........................................................................................................ 16                    |
| Comparison of Three Migration Strategy............................................................................. 17                                 |
| Suggestion for Migration Strategy........................................................................................ 17                           |
| Product-Based WBS............................................................................................................. 18                      |
| Section B....................................................................................................................................... 20    |
| C....................................................................................................................................... 24            |
| Section                                                                                                                                                |
| Project Charter .......................................................................................................................... 24          |
| Introduction........................................................................................................................... 28             |

| Requirements ........................................................................................................................            |   29 |
|--------------------------------------------------------------------------------------------------------------------------------------------------|------|
| User Acceptance Test (UAT) Plan ...........................................................................................                      |   32 |
| Objectives .............................................................................................................................         |   32 |
| Acceptance Criteria...............................................................................................................               |   32 |
| Test Scenarios .......................................................................................................................           |   33 |
| Cloud Readiness Assessment....................................................................................................                   |   35 |
| Key considerations before migrating to cloud......................................................................                               |   35 |
| Readiness factors (technical, cultural, operational) ..............................................................                              |   36 |
| Cultural Readiness ................................................................................................................              |   36 |
| Operational Readiness ..........................................................................................................                 |   36 |
| Initial recommendations........................................................................................................                  |   37 |
| Reference ...................................................................................................................................... |   38 |

## Section A

## Project Scope Overview

## Objective

The Enterprise Data Warehouse (EDW) project aims to transition UpharMax's aging on-premises Microsoft  SQL  Server-based  data  warehouse  and  its  legacy  Informatica  ETL  pipelines  to  a scalable, serverless cloud-native  platform,  like  Snowflake,  Amazon  Redshift,  or  Google BigQuery.  The  goal  of  this  transition  is  to  modernize  data  ingestion  and  processing  using capabilities  of  dbt,  Fivetran,  or  Apache  Airflow  to  allow  near  real-time  analytics  that  support predictive  modeling,  customer  personalization,  and  demand  forecasting.  The  modernization project also aims to enhance data governance, protect UpharMax from potential regulatory issues with PDPA and GDPR, as well as being able to better provide data consistency cross-enterprise operations and migrate with minimum downtime to mitigate impacts on business operations.

## Benefits

## Scalability &amp; Flexibility

The  cloud-native  EDW  supports  dynamic  storage  and  processing  scaling  in  line  with  actual demand. This means, as data volumes rise due to increased UpharMax's retail outlets, e -commerce site, and logistics partners, the EDW cloud storage and processing capacity will scale up as needed, avoiding bottlenecks during high demands, and ensure lower costs incurred for UpharMax during low-demand, or no-demand periods as the cloud-native EDW can scale down. The ability to bring in new data sources, whether IoT, mobile apps, or external market data, is optimized and simplified as the person doing it only has to define a new data source; the cloud-native EDW takes care of everything. Upgrading to new versions of the platform is also non-intrusive and does not require any additional infrastructure investment to support the upgrade that results in long downtimes.

## Cost Efficiency

The  shift  to  a  pay-as-you-go  cloud  model  leads  to  significant  depreciation  of  the  capital expenditure.  The  need  to  purchase  proprietary  hardware  tools,  updates,  server  maintenance, physical  data  center  operations,  and  everything  related  to  technology  and  infrastructure  is transferred to a selected cloud provider such as Amazon AWS or Azure. The remaining internal IT teams share responsibility for fully managing infrastructure, and operational costs become more predictable and based solely on cloud resources usage. This allows internal teams to stop overprovisioning and have targeted operational costs. Cloud costs can then translate into operational savings that can support analytic initiatives, customer engagement or other aspects of business innovation.  The  shift  to  pay-as-you-go  also  includes  the  elimination  of  systems  and  hardware upgrades, associated power consumption and cooling, required on-site disaster recovery problem and implementations, and etcetera. The solution is financially sustainable over the long haul.

## Improved Data Quality &amp; Consistency

Cloud-native  EDW  centralized  governance  supports  business  rules,  data  definitions,  data formatting and processing across business units so that data silos are eliminated from the data lifecycle. Badman and Kosinski (2025) stated that data silos are collections of isolated data, which is  difficult  for  the  data  to  be  shared  across  different  departments,  business  units,  and  systems. Siloed data is an obstacle for organization to maintain data quality and make data-driven decision. Automated data transformation pipelines enable the ingestion of data to create warehouses and dashboards of multiple datasets without creating duplicates, consolidating into a single trusted source of truth i.e. analytics data, with careful execution that leads to greater trust in reporting and dashboards for persuasively supporting data-driven decision-making. With modern data-modeling practices, UpharMax can increase accuracy, minimize data reconciliation efforts, maintain data standards across jurisdictions and business units, and improve operational efficiency with the use of  shared  data  infrastructure  and  capability  in  collaborative  areas,  while  advancing  strategic practices in data-oriented municipalities with trust, collaboration and innovation.

## Faster Insights &amp; Decision-Making

Modernization  will  replace  long-standing  ETL  batch  jobs  with  near  real-time  data  ingestion pipelines, making it possible for analytics to be updated continuously, instead of once per night.

Mazlum Tosun (2023) claimed that cloud services such as Cloud Storage, Dataflow, and BigQuery are  responsible  for  ETL  batch  pipeline  such  as  extract,  transformation  and  load.  These  batch pipelines can be orchestrated by cloud services such as Apache Airflow and Cloud Composer. This provides assurance that managers, analysts, and decision-makers can work in the most current context. With faster, more emerging insights, the business can adjust more readily for changes in customer behaviors, identify emerging trends in the market sooner, and respond to supply chain disruptions  more  effectively.  The  reduction  of  latency  from  data  generation  to  actual  use  is  a competitive  advantage  that  provides  benefits  for  the  business,  capitalizing  quickly  by  taking advantage of new opportunities or mitigating a potential or emerging risk, ultimately providing greater operational agility and responsiveness to market changes.

## Enhanced Security &amp; Compliance

The leading cloud platforms offer advanced built-in security functionalities including encryption and  decryption  of  data  at  rest  and  in  transit,  fine-grained  role-based  access  control  (RBACs), identity management, and continuous monitoring of all activity. According to Amazon (2025), RBAC is one of the access control models provided by AWS. It manages resources access based on predefined roles that align with the business logic. These cloud assets can protect sensitive customer and operational data from unauthorized access and breaches. Compliance tools available on cloud platforms can automate the protection of customer data for adherence to regulations like the PDPA and GDPR with built-in consent management, data retention policy management, and audit  logging,  reduce  legal  and  financial  risk,  and  provide  enhanced  consumer  trust  that  data protection will become a distinctive operational capability for UpharMax. Where possible, cloud systems can also carry updates and security patches to minimize exposure to risk. Amazon (2025) stated  that  AWS  is  custom-built  for  different  country  including  Malaysia,  and  the  services provided by AWS to the world are aligned with Personal Data Protection Act 2010 (PDPA), and AWS are recognized for following the security measures including ISO 27001, ISO 27017, ISO 27018, PCI DSS Level 1, and SOC 1, 2 and 3. AWS also stated that personal data that is uploaded to AWS services under AWS accounts is in compliance with the GDPR.

## Future-Readiness

The advanced EDW architecture will be designed to support advanced analytics and technology scenarios:  AI/ML,  IoT,  and  big  data  processing  frameworks.  This  also  allows  for  AI-enabled demand  forecasting,  ML-driven  customer  segmentation,  and  real-time  inventory  management capabilities.  The  platform  will  be  flexible  enough  that,  as  business  demands  evolve  or  new opportunities for data-driven decision making are identified, UpharMax will be able to quickly add and enable solutions without requiring re-engineering or making large capital expenditures for change. By creating a future-ready infrastructure, UpharMax will be able to remain competitive and  disciplined  in  a  competitive  marketplace  while  also  being  able  to  innovate  with  existing technologies that do not require a paradigm shift.

## Stakeholder Mapping

## Internal Stakeholders

| Stakeholder s                                  | Interest   | Role                                                                               | Influence (power of stakeholder )   | Reasons of high/medium/low                         |
|------------------------------------------------|------------|------------------------------------------------------------------------------------|-------------------------------------|----------------------------------------------------|
| Executive Leadership Team (CEO, CFO, COO, CIO) | High       | Provide strategic direction, approve budget, ensure consistency with company goals | High                                | Can approve, pause, cancel the initiative entirely |

| Project Sponsor                                                       | High   | Oversight project and ensure resources and support are available                    | High   | Has the authority to escalate issues, secure resources                                                           |
|-----------------------------------------------------------------------|--------|-------------------------------------------------------------------------------------|--------|------------------------------------------------------------------------------------------------------------------|
| IT Department                                                         | High   | Maintain current systems, support migration, ensure integration with existing tech. | Medium | Only control key technical resources and ensure systems are available during migration                           |
| Data& Analytics Team (Data Engineers, Data Analysts, Data Scientists) | High   | Use the data warehouse daily; require improved speed, quality, and real-time access | Medium | Influence requirements, data quality standards, and testing. Only drive design changes, cannot stop the project. |
| ERP/CRM/ POS/ Supply Chain                                            | Medium | Provide and validate source data                                                    | Medium | They control authority over source data integration                                                              |

| System Owners                   |        | for integration                                                     |        |                                                                                                     |
|---------------------------------|--------|---------------------------------------------------------------------|--------|-----------------------------------------------------------------------------------------------------|
| Compliance &Legal Team          | High   | Ensures adherence to PDPA, GDPR, and regional regulations           | High   | Can terminate project if PDPA, GDPR, or other regulatory requirements are not met                   |
| Finance Department              | Medium | Tracks project spending and measures ROI                            | Medium | Can approve or reject extra spending and influence cost decisions, but not the overall architecture |
| E- commerce Team                | High   | Needs real- time online transaction , logistics, and inventory data | Low    | Supply requirements and feedback, but limited control over priorities.                              |
| HR Department                   | Medium | Manages staff training and resources allocation                     | Low    | Involve in training and user adoption, but not in architecture or funding.                          |
| Security& Risk Managemen t Team | High   | Overseas data security and risk                                     | High   | Can block deployment if data security or risk management standards aren't satisfied                 |

| mitigation during migration.   |
|--------------------------------|

## External Stakeholders

| Stakeholders                                                        | Inter est   | Role                                                                  | Influe nce   | Reasons of high/medium/low                                                                                                   |
|---------------------------------------------------------------------|-------------|-----------------------------------------------------------------------|--------------|------------------------------------------------------------------------------------------------------------------------------|
| AdvTech Software and Technologies Sdn. Bhd. (Delivery Partner)      | High        | Designs and implements migration; ensures project meets objectives.   | High         | Be responsible on the design, build, and migration execution. Directly determines whether the project meets technical goals. |
| AdvTech Project Manager                                             | High        | Manages vendor-side planning,                                         | High         | Controls the delivery plan, timelines, and quality. Manages dependencies that can make or break the schedule                 |
| Cloud Service Provider (Snoflake, AWS Redshift, or Google BigQuery) | Medi um     | Hosts the data warehouse; ensures performance, uptime, and compliance | High         | Controls the infrastructure environment, scalability and compliance certifications                                           |
| Third-Party Vendors/Partner s                                       | Medi um     | Provide operational data; need smooth data integration                | Low          | Provide operational data for integration, but have no decision-making authority                                              |

| System Integrators   | High   | Assist in hybrid cloud/on-prem transitions                        | High    | Responsible for connecting the new cloud warehouse with ERP, CRM, POS and other systems. If they fail or delay, the new system might not be function as expected.   |
|----------------------|--------|-------------------------------------------------------------------|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| End-user             | High   | Ultimately benefit from better personalizatio n and service speed | Mediu m | Their feedback only influences adoption success and workflow design, but do not decide budgets or other main choices.                                               |

## Project Team Structure

<!-- image -->

## Risk Management

As UpharMax Sdn. Bhd. migrates from its legacy system to a serverless platform to improve their data environment, the company will face multiple challenges while business continues to operate. In  every  software  project,  risk  management  is  a  major  knowledge  area  within  the  software management process. It provides an effective approach to identify, analyze, and respond to risk throughout the project life cycle while guiding the project to meet its objectives. It is especially crucial when the project has high uncertainty. To successfully apply the approach, we will be using a risk register table.

## Risk register content:

1. Risk ID: Identification number to identify each risk event.
2. Risk Description: Detailed explanation of the risk event.
3. Risk Category: Differentiated into external or internal risk.
- a. External - Risk that comes from outside the organization such as government, other companies or attackers.
- b. Internal - Risk that come from within the organization
4. Root Cause: What causes the risk to happen?
5. Trigger: Indicators or symptoms of actual risk events.
6. Probability of Occurrence: How likely will the risk occur. (1 - 5)
- a. 1 = Rare
- b. 2 = Unlikely
- c. 3 = Possible
- d. 4 = Likely
- e. 5 = Almost Certain
7. Risk rating: How severe are the consequences if the risk occurs. (1 - 5)
- a. 1 = Negligible
- b. 2 = Minor
- c. 3 = Moderate
- d. 4 = Major
- e. 5 = Critical

8. Risk Score (Probability multiply by Risk Rating): Priority to fix the risk (1 - 25)
- a. 1 - 5 = Low
- b. 6 - 12 = Medium
- c. 13 - 19 = High
- d. 20 - 25 = Critical
9. Risk Impact: The effect of the risk may bring.
10. Potential financial loss: The estimated financial loss caused by the risk event.
11. Risk Owner: People that are responsible for the corresponding risk.
12. Approach: Ways to avoid the risk from happening.
13. Mitigation plan: Ways to mitigate the risk during or after the risk happens.
14. Status: The current progress of the risk (Ongoing, Closed, Pending, Planned).
15. Comments: Detailed explanation for status.

Below is the risk register table for UpharMax Sdn. Bhd.

Risk 1

| Risk ID                   | R01                                                                                                                                                  |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| Risk Description          | Potential data breach                                                                                                                                |
| Risk Category             | Internal                                                                                                                                             |
| Root Cause                | Poor security control leads insiders without privileges to gain access to system, unauthorized access, weak Multi-Factor Authentication (MFA) policy |
| Trigger                   | Confidential data that contains employee's and customer's personal information being leaked to outsiders                                             |
| Probability of Occurrence | 1                                                                                                                                                    |
| Risk rating               | 4                                                                                                                                                    |
| Risk Score                | 4                                                                                                                                                    |
| Risk Impact               | Loss of privacy, Increased vulnerability, Damaged reputation                                                                                         |
| Potential Financial Loss  | RM200,000 - RM300,000                                                                                                                                |
| Risk Owner                | IT Department, Security &Risk Management Team, Data &Analytics Team                                                                                  |

| Approach (Preventive plan)   | Utilize comprehensive frameworks such as Identity and Access Management (IAM) to strengthen access control, implement latest technologies to improve MFA systems, Conduct regular checking on audit logs   |
|------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Mitigation Plan              | Identify the compromised data, immediately shut down affected systems                                                                                                                                      |
| Status                       | Closed                                                                                                                                                                                                     |
| Comments                     | Enforced MFA, no incident for one month                                                                                                                                                                    |

Risk 2

| Risk ID                    | R02                                                                                                                                                               |
|----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Risk Description           | Poor communication engagement among project team members and stakeholders                                                                                         |
| Risk Category              | Internal                                                                                                                                                          |
| Root Cause                 | Poor listening and comprehension, lack of clarification in documentation, poor interaction among team members and stakeholders, Poor leadership skills            |
| Trigger                    | Unfulfilled project requirements, Increased disputes among team members, Delay in tasks                                                                           |
| Probability of Occurrence  | 4                                                                                                                                                                 |
| Risk rating                | 4                                                                                                                                                                 |
| Risk Score                 | 16                                                                                                                                                                |
| Risk Impact                | Project costs overrun, Delays in project deliverables, Disappoints stakeholders                                                                                   |
| Potential Financial Loss   | RM8000 - RM12,000 / each delayed day                                                                                                                              |
| Risk Owner                 | Project Sponsor, Executive Leadership Team, HR Department                                                                                                         |
| Approach (Preventive plan) | Clearly define project scopes and requirements, utilize software communication tools, hold regular meetings among team members, Provide training for team members |
| Mitigation Plan            | Identify the department where project problem arises, Settle conflicts and disputes among team members                                                            |
| Status                     | Open                                                                                                                                                              |
| Comments                   | Weekly review meetings to reduce confusion                                                                                                                        |

Risk 3

| Risk ID                    | R03                                                                                                                                                                                                                                        |
|----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Risk Description           | Fail to obey regulatory compliance such as Personal Data Protection Act(PDPA) and General Data Protection Regulation (GDPR)                                                                                                                |
| Risk Category              | External                                                                                                                                                                                                                                   |
| Root Cause                 | Financial constraints, lacking national regulations knowledge, failed to update regulatory compliance policy, Incomplete or outdated documentation, poorly defined requirements, Lack of oversight                                         |
| Trigger                    | Legal notice sent from authorities or regulators, new data privacy regulations announced, Data auditing reveals incomplete records                                                                                                         |
| Probability of Occurrence  | 2                                                                                                                                                                                                                                          |
| Risk rating                | 5                                                                                                                                                                                                                                          |
| Risk Score                 | 10                                                                                                                                                                                                                                         |
| Risk Impact                | Financial penalty, Lawsuits, Damaged reputation, Operation disrupted                                                                                                                                                                       |
| Potential Financial Loss   | PDPA Penalty: Not exceeding RM300,000 GDPR Penalty: - Art. 83(5) GDPR: Up to RM100 million or 4% of total global turnover - Art. 83(4) GDPR: Up to RM50 million or 2% of total global turnover                                             |
| Risk Owner                 | Compliance &Legal Team,IT Department, Executive Leadership Team                                                                                                                                                                            |
| Approach (Preventive plan) | Allocate budget for regulatory compliance activities, hire national regulation legal lawyer, Detailed redefine compliance requirements, update regulatory compliance policy regularly, has multiple level of regulatory compliance review. |
| Mitigation Plan            | Update missing compliance policy immediately, Conduct emergency compliance review                                                                                                                                                          |
| Status                     | Pending                                                                                                                                                                                                                                    |
| Comments                   | Pending for budget approval                                                                                                                                                                                                                |

Risk 4

| Risk ID          | R04                             |
|------------------|---------------------------------|
| Risk Description | Downtime or Unstable connection |
| Risk Category    | Internal                        |

| Root Cause                 | UpharMax data warehouse migrating to cloud-native, serverless data platform                                                                                           |
|----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Trigger                    | User complaints, System logs report high downtime or latency                                                                                                          |
| Probability of Occurrence  | 4                                                                                                                                                                     |
| Risk rating                | 5                                                                                                                                                                     |
| Risk Score                 | 20                                                                                                                                                                    |
| Risk Impact                | Reduced revenue, Operation disrupted, Unsatisfied users                                                                                                               |
| Potential Financial Loss   | Approximately RM1.41 million / downtime or unstable connection hour                                                                                                   |
| Risk Owner                 | IT Department, Data& Analytics Team, ERP/CRM/POS/ Supply Chain System Owners& Legal Team, IT Department, Executive Leadership Team                                    |
| Approach (Preventive plan) | Schedule migration during off-peak hours, set up backup server, Perform migration testing, Maintenance work announcement, Issue maintenance notification in advanced. |
| Mitigation Plan            | Perform emergency maintenance, implement rollback to stable backed up server if fail migration                                                                        |
| Status                     | Mitigated                                                                                                                                                             |
| Comments                   | Successful failover test                                                                                                                                              |

## Migration Strategy

## Re-architecture Strategy

Amazon Web Services (2025) stated that re-architect migration strategy is to modify the existing application architectures when migrating to the cloud environment, which allows the application to  take  advantage  of  all  the  cloud-native  features.  Improvement of  the  application's  agility, scalability, and performance would be made. In comparison to the lift-and-shift migration strategy, different components of the application such as database, backend, and frontend can be refactored to  run  on  dedicated  services  provided  by  the  cloud  environment  such  as  Amazon  RDS,  AWS Lambda, AWS Beanstalk, and more, which results in better performance and reliability as these services are designed to perform certain tasks effectively and efficiently. Additionally, (Batchu, 2025) claimed that re-architecture migration involves design principles which are dedicated to the cloud environment such as serverless computing services, microservices architectures, and event-

driven  processing  models.  These  designs  allow  the  data  processing  workflows  to  be  done  by utilizing these cloud-native services. However, this strategy has the highest complexity compared to lift-and-shift and re-platforming as many aspects of the migration process must be planned such as  application  dependencies,  business  maintenance  and  data  synchronization  requirements  (p. 606). In short, re-architecture strategy allows the application to take advantage of the dedicated services that are natively provided by the cloud provider, which leads to long-term benefits, but has the highest implementation complexity.

## Lift-and-Shift strategy

According to IBM (n.d.), lift and shift are rehosting processes in which an application from an environment migrates to another environment such as from an on-premises data center to a cloud environment.  This  process  does  not  change  the  application's  settings  and  architecture  such  as operating system, environment and associated data. The main advantages are simplicity and speed when deploying an application to another environment, as no or little modifications are required during the migration. This saves lots of money and time to redevelop the application compared to other migration strategies (pp. 1-16). The disruption of application can be predicted and minimal because the application architecture, code design and user interface remain the same (AWS, 2025, p. 24). Thus, the application user experience will be the same as it was on-premises.

However, there are potential downsides to this migration strategy. An application that is optimized on-premises may not be optimized in a cloud environment. An unoptimized application deployed to the cloud may lead to unexpected high cost (Rite, 2024, p. 14). This is because cloud provides unlimited scalability and pay as you use concepts. Moreover, an on-premises application may not fully utilize all benefits of cloud such as containerization, microservice architecture and managed services (Rite, 2024, p. 16). These benefits will improve application performance, flexibility and ease of managing servers.

## Re-platforming strategy

According to Sharma (2025), Re-platforming migration strategy is the balance of lift and shift strategy and Re-architecture strategy. In this strategy, minor modification is required to increase compatibility with the cloud environment. The core parts of application such as OS, environment

and data associated remain unchanged and gain few cloud benefits as stated above. For instance, the  application  can  change  from  monolithic  architecture  to  microservice  architecture.  This enhances the application performance, scalability and efficiency beyond the lift-and-shift strategy and with less effort compared to Re-architecture strategy.

## Comparison of Three Migration Strategy

| Factor                         | Lift-and-Shift   | Re-platforming   | Re-architecture   |
|--------------------------------|------------------|------------------|-------------------|
| Initial Cost                   | Low              | Moderate         | High              |
| Migration Time                 | Fast             | Moderate         | Slow              |
| Cloud Optimization Utilization | Low              | Moderate         | High              |
| Complexity                     | Low              | Moderate         | High              |
| Performance Gain               | Limited          | Moderate         | High              |
| Development Effort             | Low              | Moderate         | High              |
| Maintenance cost               | Low              | Moderate         | High              |

Lift-and-shift  strategy  mainly  offers  benefits  on  low  initial  cost,  fast  migration  time  and  low complexity  when  migrating  applications  to  cloud.  However,  it  may  not  be  a  very  optimized solution and perfect choice in the long term, as it did not utilize the full benefits and efficiency of cloud.  On  the  other  hand,  even  though  the  Re-architecture  strategy  provides  an  optimized migration approach, this strategy requires a high initial investment of cost, resources and long migration time. Re-platforming offers a balance between these two migration strategies in terms of cost, time and optimization of the cloud.

## Suggestion for Migration Strategy

Re-Architecture migration strategy is the most suitable approach for UpharMax Sdn Bhd. Because of the need to support 300 retail outlets, a high-load e-commerce platform and many systems, the infrastructure should have high scalability and performance. Besides that, Re-architecture allows the entire application to be redeveloped for more compatibility with the cloud native serverless data platform and cloud data pipelines. This approach ensures the whole system is fully optimized

for  cloud  environments  and  leads  to  higher  performance,  better  scalability  and  greater  cost efficiency.

## Product-Based WBS

1.      Final Modernized Data Warehouse
2. 1.1  Cloud data warehouse environment
3. 1.1.1   Cloud account configuration (Account, User group, MFA)
4. 1.1.2 Cloud data warehouse configuration (Snowflake, redshift, S3…)
5. 1.1.3  Cloud  security  and  access  control  configuration  (VPC,  IAM  roles, ACL, data encryption)
6. 1.1.4 Cloud monitoring configuration (alert and alarm, logging report)
7. 1.2  Modernized data pipelines
8. 1.2.1       Data ingestion pipelines (Fivetran)
9. 1.2.2       Data transformation layer (dbt)
10. 1.2.3       Pipeline orchestration layer (Apache airflow)
11. 1.3  Legacy system data migration
12. 1.3.1       Data migration strategy document (Data to migrate, data migration approach, security, recovery plan)
13. 1.3.2       Migrated schema
14. 1.3.3       Migrated data
15. 1.3.4    Data validation reconciliation report (Validate if the data is migrated correctly)
16. 1.4  Data analytics and visualization platform
17. 1.4.1       BI platform configuration
18. 1.4.2       Semantic layer
19. 1.4.3       Analytic and visualization dashboard
20. 1.5  Testing deliverables
21. 1.5.1       Test plan
22. 1.5.2       White-Box testing
23. 1.5.3       Black-Box testing
24. 1.5.4       User Acceptance testing

## Section B

## WBS

## Note: All the tasks that have 0 days as their duration is a Milestone

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

## Section C

## Project Charter

| Document Name    | Project Charter                      |
|------------------|--------------------------------------|
| Reference Number | -                                    |
| Version          | V1.0                                 |
| Project Code     | UECS2033 Software Project Management |
| Status           | Completed                            |
| Date Released    | 22/8/2025                            |

<!-- image -->

|              | Name           | Position        | Signature   |
|--------------|----------------|-----------------|-------------|
| Prepared By: | Neo Chean Ming | Project Manager |             |
| Approved By: | Chan Hoe Kit   | Project Sponsor |             |

| 1.0 Project Identification   | 1.0 Project Identification                                                                                                                                                                                                                                                                  |
|------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name                         | Enterprise Data Warehouse Modernization Project                                                                                                                                                                                                                                             |
| Description                  | In order to allow real-time analytics and enhance scalability, UpharMax is modernising its outdated on-premises data warehouse by moving to a cloud-native platform. The program must secure local regulatory compliance while handling a difficult move with little business interruption. |
| Project Sponsor              | Chan Hoe Kit                                                                                                                                                                                                                                                                                |
| Project Manager              | Neo Chean Ming                                                                                                                                                                                                                                                                              |

| 2.0 Project Team Resources (key Stakeholders)   | 2.0 Project Team Resources (key Stakeholders)   | 2.0 Project Team Resources (key Stakeholders)   | 2.0 Project Team Resources (key Stakeholders)   |                              |
|-------------------------------------------------|-------------------------------------------------|-------------------------------------------------|-------------------------------------------------|------------------------------|
|                                                 | Name                                            | Department                                      | Email                                           | Authority level              |
| Data & Analytics Team Leader                    | Chong Yi Heng                                   | IT department                                   | yiheng.chong @upharmax.com                      | High (Approver)              |
| Finance Manager                                 | Fong Gyn Shen                                   | Finance Department                              | gynshen.fong @upharmax.com                      | Medium (Consulted)           |
| HR Manager                                      | Angel Yap Yoon Ying                             | HR Department                                   | yap.angel@uphar max.com                         | Medium (Consulted)           |
| Compliance & Legal Team Leader                  | Dilan Rhaj                                      | Compliance & Legal Team                         | rhaj.dilan @upharmax.com                        | High (Approver - Compliance) |
| AdvTech Project Manager                         | Rajesh Kumar                                    | AdvTech Project Manager                         | rajesh.kumar@ad vtech.com                       | High (Informed/Respo nsible) |

## 3.0 PROJECT OBJECTIVES (PURPOSE)

- The on-premises data warehouse, which was constructed using Informatica and Microsoft SQL Server, was successfully retired and migrated.
- Deploy a scalable, cost-effective, cloud-native data platform (e.g., Snowflake, Amazon Redshift, or Google BigQuery).
- To facilitate demand forecasting, customer personalisation, and predictive analytics, enable real-time or almost real-time data access.
- Enhance data governance, consistency, and quality in all departments and areas.
- Improve flexibility and scalability to meet expanding business requirements and data volumes.
- Assure Security and Compliance: To guarantee adherence to PDPA, GDPR, and other local laws, put strong data governance, security procedures, and access controls in place.

## 4.0 PROJECT SCOPE

- Migration of legacy on-premises data warehouse to a cloud-native, serverless platform (Snowflake, AWS Redshift, or Google BigQuery).
- High security standards are achieved in the cloud environment
- Data cleansing and standardization to eliminate duplicates and improve data quality.
- High availability and disaster recovery setup in the new cloud environment.

## 4.0 PROJECT SCOPE

- Modernize and redesign ETL/ELT pipelines using contemporary tools (dbt, Fivetran, Apache Airflow) to replace legacy processes and improve efficiency.
- Cloud platform for data analytic and visualization of the migrated data.

| 5.0 KEY PROJECT DELIVERABLES        | 5.0 KEY PROJECT DELIVERABLES                                                                                                                                                                            |
|-------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name                                | Description                                                                                                                                                                                             |
| Cloud environment                   | A fully configured cloud environment, which consists of the necessary cloud services and security such as RBAC and MFA.                                                                                 |
| Data pipeline                       | A fully functional data pipeline, which includes dbt, Fivetran and Apache Airflow that are required for data migration.                                                                                 |
| Migrated data                       | All the migrated data from the legacy system to the cloud environment                                                                                                                                   |
| PDPA and GDPR compliance report     | A report which documents how the migrated cloud data warehouse complies with PDPA and GDPR regulations.                                                                                                 |
| Risk register and mitigation report | A report that outlines the possible risk that the project might face and the ways of mitigating them                                                                                                    |
| Cloud architecture documentation    | A document which includes the idea behind the cloud architecture and cloud environment, which may include the reason for each used cloud services and guidelines on how to access the cloud environment |
| BI Dashboard                        | Aservice inside the cloud environment that provides features such as data analysis and visualization                                                                                                    |
| Training tutorials                  | A list of tutorials on the guidelines on how to access the new system in the cloud environment, which will be given during training period                                                              |
| Final audit summary                 | A report which includes all the necessary project information such as financial expenses, compliance verification and validation, fulfilled functional and non- functional requirements.                |

## 6.0 PROJECT CHARTER SIGNOFF

Project Sponsor: Chan Hoe Kit

Date:  25 August 2025

Project Manager: Neo Chean Ming

Date:  23 August 2025

Data &amp; Analytics Team Leader: Chong Yi Heng

Date:  23 August 2025

Finance Manager: Fong Gyn Shen

Date:  23 August 2025

HR Manager: Angel Yap Yoon Ying

Date:  23 August 2025

Compliance &amp; Legal Team Leader: Dilan Rhaj

Date:  23 August 2025

AdvTech Project Manager: Rajesh Kumar

Date:  23 August 2025

## Software Requirements Specification [SRS]

| Document Name    | Software Requirement Specification [SRS]   |
|------------------|--------------------------------------------|
| Reference Number | -                                          |
| Version          | V1.0                                       |
| Project Code     | UECS2033 Software Project Management       |
| Status           | Completed                                  |
| Date Released    | 12/8/2025                                  |

|              | Name           | Position        | Signature   |
|--------------|----------------|-----------------|-------------|
| Prepared By: | Neo Chean Ming | Project Manager |             |
| Approved By: | Chan Hoe Kit   | Project Sponsor |             |

## Introduction

This SRS document defines the functional and non-functional requirements for UpharMax Sdn. Bhd 's  migration from  a  traditional  on-premises  data  warehouse,  which  is  built  on  legacy technologies, to a cloud-native data platform environment by implementing re-architect migration strategy. We will ensure that all the functionality of the legacy system will be migrated safely, and adequate documentation will be made by the project team to ensure a clear reference in the future.

## Scope

## Scope Included

All the existing functions for the legacy system will be migrated to the cloud-native data platform environment. For example, cloud environment setup such as MFA, security, data encryption, data storage and processing services, modern pipelines environment such as dbt, Fivetran and Apache Airflow, and BI dashboard for data analytic and visualization. We will also make sure that the migrated  system  is  compliant  with  regulatory  compliance  such  as  PDPA  and  GDPR.  Quality assurance  processes  will  be  executed  to  ensure  that  the  system  has  met  the  current  industry

requirements. The documentation of the cloud-native data platform environment and BI dashboard will be made along the way.

## Scope Excluded

We will not develop the features which are not defined in the migration scope, and the functionality of the legacy system will not be maintained by the project team.

## Requirements

## Functional Requirements

| ID   | Requirement                                                                                                                             |
|------|-----------------------------------------------------------------------------------------------------------------------------------------|
| FR01 | The system shall migrate existing ETL processes and data into cloud-native platform.                                                    |
| FR02 | The system shall receive data from multiple systems such as ERP, CRM, POS and supply chain systems.                                     |
| FR03 | The system shall send processed data to multiple systems such as ERP, CRM, POS and supply chain systems.                                |
| FR04 | The system shall support batch and real-time data processing for predictive analytics, demand forecasting and customer personalization. |
| FR05 | The system shall provide data storage for the migrated data                                                                             |
| FR06 | The system shall automatically perform data analysis on data stored.                                                                    |
| FR07 | The system shall automatically generate reports to visualize the data.                                                                  |
| FR08 | The system shall provide BI tools                                                                                                       |
| FR09 | The system shall provide a dashboard for users to view the generated report                                                             |
| FR10 | The system shall allow data export in JSON and CSV format                                                                               |
| FR11 | The system shall automatically detect and resolve data quality issues such as duplicate datasets and inconsistent data quality.         |
| FR12 | The system shall provide completed logs of user activities such as data access, system changes and user login.                          |
| FR13 | The system shall allow administrator to manage cloud user accounts                                                                      |
| FR14 | The system shall automatically notify the user through email when any error is detected.                                                |
| FR15 | The system shall automatically notify the administrator when the allocated budget exceeds the cloud defined threshold.                  |
| FR16 | The system shall support data cleaning before storing in the cloud platform.                                                            |

## Non-functional Requirements

| ID    | Requirement                                                                                                                        | Category of NFR   |
|-------|------------------------------------------------------------------------------------------------------------------------------------|-------------------|
| NFR01 | The system shall achieve 99.999% uptime monthly                                                                                    | Availability      |
| NFR02 | The system shall be hosted on at least 3 Availability Zone for each hosted region to prevent data loss during disasters            | Availability      |
| NFR03 | The system shall be accessed via web browsers with active internet connection                                                      | Compatibility     |
| NFR04 | The system's data processing and migration processes shall comply with PDPA and GDPR regulations                                   | Compliance        |
| NFR05 | The system's data storage and database shall have at least 25,000 IOPS for quicker data migration                                  | Performance       |
| NFR06 | The system's BI dashboard shall response within 1500 ms for datasets query                                                         | Performance       |
| NFR07 | The system shall perform weekly backup of the cloud data storage and database                                                      | Reliability       |
| NFR08 | The system shall perform weekly snapshots of the cloud instance                                                                    | Reliability       |
| NFR09 | The system's cloud data storage and database shall automatically scale up and down depending on the storage utilization            | Scalability       |
| NFR10 | The system's data processing instance shall automatically scale horizontally upon reaching 80% utilization to distribute workloads | Scalability       |
| NFR11 | The system shall encrypt client's sensitive information using AES-256                                                              | Security          |
| NFR12 | The system shall have Role Based Access Control setup to prevent unauthorized use                                                  | Security          |
| NFR13 | The system shall configure firewall such as security groups and network Access Control List to prevent cyber attack                | Security          |
| NFR14 | The system shall create PEM key files to allow authorized developers to access the cloud instance remotely and safely              | Security          |
| NFR15 | The system shall create user group and user role for authorized users to access the cloud data platform                            | Security          |
| NFR16 | The system's BI dashboard shall follow the Schneiderman's Eight Golden Rules interface design                                      | Usability         |
| NFR17 | The system shall provide documentations for all developed features in the cloud environment                                        | Usability         |

## SOFTWARE REQUIREMENT SPECIFICATION SIGN OFF

Project Sponsor: Chan Hoe Kit

Date:  19 August 2025

Project Manager: Neo Chean Ming

Date:  19 August 2025

Data &amp; Analytics Team Leader: Chong Yi Heng

Date:  19 August 2025

Finance Manager: Fong Gyn Shen

Date:  19 August 2025

HR Manager: Angel Yap Yoon Ying

Date:  19 August 2025

Compliance &amp; Legal Team Leader: Dilan Rhaj

Date:  19 August 2025

AdvTech Project Manager: Rajesh Kumar

Date:  19 August 2025

## User Acceptance Test (UAT) Plan

| Document Name    | User Acceptance Test Plan            |
|------------------|--------------------------------------|
| Reference Number | -                                    |
| Version          | V1.0                                 |
| Project Code     | UECS2033 Software Project Management |
| Status           | Completed                            |
| Date Released    | 2/12/2025                            |

|              | Name         | Position        |         | Signature   |
|--------------|--------------|-----------------|---------|-------------|
| Prepared By: | Rajesh Kumar | AdvTech Manager | Project |             |
| Approved By: | Chan Hoe Kit | Project Sponsor |         |             |

## Objectives

The purpose of UAT is to confirm that the updated Enterprise Data Warehouse (EDW) meets the business needs of UpharMax Sdn. Bhd. and works as intended in the real world. Specifically, that the  migrated  data  is  correct,  reporting  dashboards  work  as  expected,  regulatory  compliance (PDPA,  GDPR)  is  achieved,  and  that  the  cloud  solution  meets  the  required  criteria  for performance, scalability, and usability before it is fully deployed.

## Acceptance Criteria

The UAT will be considered successful if the following criteria are met:

- ❖ ETL/ELT  pipelines  successfully  process  and  load  data  within  the  defined  SLA  time window.
- ❖ Business  Intelligence  (BI)  dashboards  and  reports  generate  without  errors  and  reflect correct, real-time data.

- ❖ Role-based  access  control,  encryption,  and  compliance  checks  (PDPA,  GDPR)  are validated.
- ❖ No critical defect remains unresolved at time of sign-off
- ❖ End users confirm that the system meets their functional and usability expectations.

## Test Scenarios

| Scenario ID   | Test Scenario                                                                     | Expected Outcome                                               |
|---------------|-----------------------------------------------------------------------------------|----------------------------------------------------------------|
| TS01          | Validate data migration accuracy by comparing legacyEDW and new cloud EDWdatasets | Data matches with 99.5+ accuracy                               |
| TS02          | Test ETL/ELT jobs using dbt/Fivetran pipelines                                    | Data loads successfully within SLA with no failures            |
| TS03          | Generate standard sales and inventory reports from BI dashboard                   | Reports display correct and consistent data across all regions |
| TS04          | Perform role-based access control test for Finance, Sales, and IT users           | Users can only access permitted datasets and dashboards        |
| TS05          | Validate compliance with PDPA and GDPR during data retrieval and storage          | Compliance requirements are met, no unauthorized access        |
| TS06          | Conduct performance test with peak-hour queries                                   | Reports load within agreed response time (e.g., <5 seconds)    |
| TS07          | Test audit trail and logging features                                             | All user and system activities are recorded and retrievable    |

## USER ACCEPTANCE TEST PLAN SIGN OFF

Project Sponsor: Chan Hoe Kit

Date:  19 August 2025

Project Manager: Neo Chean Ming

Date:  19 August 2025

Data &amp; Analytics Team Leader: Chong Yi Heng

Date:  19 August 2025

Finance Manager: Fong Gyn Shen

Date:  19 August 2025

HR Manager: Angel Yap Yoon Ying

Date:  19 August 2025

Compliance &amp; Legal Team Leader: Dilan Rhaj

Date:  19 August 2025

AdvTech Project Manager: Rajesh Kumar

Date:  19 August 2025

## Cloud Readiness Assessment

UpharMax Sdn. Bhd. should conduct readiness assessment before migration as it will help the company to determine if the company has the ability to successfully migrate to cloud platform. According to RapidFire Tools (2024), a cloud readiness assessment is a comprehensive evaluation that assesses the technical, operational, financial and strategic factors to determine organizations' preparedness and ensures a smooth and effective cloud migration.

## Key considerations before migrating to cloud

According to Svitla Systems (2024), the  key considerations before migrating to the cloud are data security and privacy, regulatory compliance, cost management and skill gap.

| Considerations            | Explanation                                                                                                                                                                                         |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Data Security and Privacy | ● Trust between companies depends on careful consideration on how sensitive data is managed. ● High probability for data breach due to weak data security and privacy leads to service disruptions. |
| Regulatory Compliance     | ● High complexity in regulations compliance due to frequent changes.                                                                                                                                |
| Skill Gap                 | ● Teams lack expertise in cloud. ● Teams requires continuous training and skill development to update their skills                                                                                  |
| Cost Management           | ● Cloud migration is costly for large organizations. ● Additional expenses arise from company training, compliance requirements, and ongoing subscription fees                                      |

## Readiness factors (technical, cultural, operational)

## Technical Readiness

Technical  readiness  allows  organizations  to  determine  whether  their  current  IT  infrastructure, application and data is compatible with cloud migration. According to Pacheco (2024), before migrating, organizations need to evaluate the following conditions such as workload complexity, resource requirements, data security needs, best cloud fit for each workload, app and component dependencies as well as physical appliances needed during migration. This is because a complex workload with multiple dependencies may be more challenging to migrate compared to a selfcontained one (paras 8 - 9). Technical readiness is crucial for UpharMax Sdn. Bhd., since the company is migrating from a legacy system to a serverless environment. Legacy applications with multiple dependencies may be required to refactor and data pipelines may also need to be rebuilt to be suitable for cloud services.

## Cultural Readiness

Cultural  readiness  allows  organizations  to  determine  whether  their  employees  and  leaders  are ready  to  adopt  cloud  technologies.  According  to  Bahaa-El-Din  (2024),  cultural  readiness  is evaluated  based  on  factors  such  as  adaptability  to  change,  openness  to  innovation,  leadership support,  fairness  perceptions,  learning  opportunities  and  employee  involvement.  The  factors mentioned by Bahaa-El-Din are about the influence of how employees and leaders embrace cloud adoption. In the scenario of UpharMax Sdn. Bhd., cultural readiness is significant as the company is accustomed to legacy systems. Hence, some employees may resist the transition due to their unfamiliarity with cloud serverless platform environments.

## Operational Readiness

Operational readiness allows organizations to determine whether their processes and workflows have the abilities to support cloud operations. According to Pacheco(2024), organizations should consider the teams' readiness based on factors such as the readin ess to change work practices, training  requirements  needed  and  establishment  of  maintenance  windows  or  moratoriums  to handle  potential  outages  during  migration.  In  the  case  of  UpharMax  Sdn.  Bhd,  operational readiness is important as their business must continue to operate while the migration takes place.

If the company does not fulfil the operational requirements, it may cause extended downtime and business disruptions.

## Initial recommendations

Before starting the process of migration, here are some initial recommendations that UpharMax Sdn Bhd should follow. The company can begin with pilot testing that starts with small scale testing before moving the system as whole to the cloud platform. According to Chinamanagonda (2024),  pilot  migration  aims  to  validate  an  organization's  technical,  operational,  and  financial assumptions to minimize risks such as data loss and service disruptions before committing the full migration  (p.  22).  Organization  starts  by  moving  non-critical  components  to  the  target  cloud environment first in order to assess infrastructure compatibility, measure performance benchmarks, and evaluate the sustainability of the services under real operational conditions. This is an excellent approach for UpharMax Sdn Bhd as the company is transitioning from an old onpremises data with complex ETL batch windows to a serverless platform.

## Reference

- Amazon Web Services.  (2025).  About  the  migration  strategies  -  AWS  Prescriptive  Guidance. [online] Available at: https://docs.aws.amazon.com/prescriptive-guidance/latest/largemigration-guide/migration-strategies.html#refactor [Accessed 16 Aug. 2025].
- Amazon Web Services.  (2025).  About  the  migration  strategies  -  AWS  Prescriptive  Guidance. [online] Available at: https://docs.aws.amazon.com/prescriptive-guidance/latest/largemigration-guide/migration-strategies.html#refactor [Accessed 16 Aug. 2025].
- Amazon. (2025). Analysis and visualization - Data Warehousing on AWS . [online] Available at: https://docs.aws.amazon.com/whitepapers/latest/data-warehousing-on-aws/analysis-andvisualization.html [Accessed 23 Aug. 2025].
- Amazon.  (2025). General  Data  Protection  Regulation  (GDPR)  Center .  [online]  Available  at: https://aws.amazon.com/compliance/gdpr-center/ [Accessed 16 Sep. 2025].
- Amazon. (2025). Malaysia Data Privacy . [online] Available at: https://aws.amazon.com/compliance/malaysia-data-privacy/ [Accessed 16 Sep. 2025].
- Amazon. (2025). Types of access control  - AWS Prescriptive Guidance .  [online]  Available  at: https://docs.aws.amazon.com/prescriptive-guidance/latest/saas-multitenant-api-accessauthorization/access-control-types.html [Accessed 16 Sep. 2025].
- Badman, A. and Kosinski, M. (2025). Data Silos . [online] Ibm.com. Available at: https://www.ibm.com/think/topics/data-silos [Accessed 16 Sep. 2025].
- Bahaa-El-Din,  M.  (2024).  Cultivating  Organizational  Culture  for  Successful  Cloud  Adoption: Strategy for  Successful Integration and  Adoption.  [online]  Aalto.fi. Available  at: https://aaltodoc.aalto.fi/items/ac3c5c8a-ee2d-441f-8847-cefe9980188d [Accessed 16 Sep. 2025].
- Batchu, K.C. (2025). Scalable Framework for Cloud Data Migration: Architecture, Strategy and Best Practices. Journal Of Engineering And Computer Sciences , [online] 4(7), pp.604 -611. Available at: https://sarcouncil.com/2025/07/scalable-framework-for-cloud-datamigration-architecture-strategy-and-best-practices [Accessed 16 Aug. 2025].
- Batchu, K.C. (2025). Scalable Framework for Cloud Data Migration: Architecture, Strategy and Best Practices. Journal  Of Engineering And Computer Sciences ,  [online]  4(7),  pp.604 -611. Available at: https://sarcouncil.com/2025/07/scalable-framework-for-cloud-datamigration-architecture-strategy-and-best-practices [Accessed 16 Aug. 2025].

- Cuello, C. (2025, April 1). Data Migration Checklist: A Comprehensive Guide for Successful Data Migration . Rivery; Comeet  Jobs. https://rivery.io/data-learning-center/complete-datamigration-checklist/
- Databricks. (2025). Semantic Layer . [online] Available at: https://www.databricks.com/glossary/semantic-layer [Accessed 23 Aug. 2025].
- Fivetran  (2023). Data  ingestion:  Definition,  types  and  challenges .  [online]  Fivetran.com. Available at: https://www.fivetran.com/learn/data-ingestion [Accessed 23 Aug. 2025].
- Global Compliance News. (2016). Data Protection Enforcement in Malaysia . [online] Available at: https://www.globalcompliancenews.com/data-privacy/data-protection-enforcement-inmalaysia/ [Accessed 16 Sep. 2025].
- Gnaneswaran, D. (2018). Cybersecurity threats to cost organizations in Malaysia US$12.2 billion in economic losses -Microsoft Malaysia News Center . [online] Microsoft. Available at: https://news.microsoft.com/en-my/2018/07/12/cybersecurity-threats-to-costorganizations-in-malaysia-us12-2-billion-in-economic-losses/ [Accessed 16 Sep. 2025].
- Hui, X. (2023). The Costly Impact of Server Downtime: 1Hr Can Drain Profits . [online] Exabytes Blog. Available at: https://www.exabytes.my/blog/server-downtime-can-drain-yourprofits/ [Accessed 16 Sep. 2025].
- IBM (2021). Lift and Shift . [online] Ibm.com. Available at: https://www.ibm.com/think/topics/liftand-shift.
- Lin, G. (2022). How  Airflow  +  dbt  Work  Together . [online] dbt Labs. Available at: https://www.getdbt.com/blog/dbt-airflow [Accessed 23 Aug. 2025].
- Mazlum  Tosun  (2023). ETL  Batch  pipeline  with  Cloud  Storage,  Dataflow  and  BigQuery orchestrated by Airflow/Composer . [online] Medium. Available at: https://medium.com/google-cloud/etl-batch-pipeline-with-cloud-storage-dataflow-andbigquery-orchestrated-by-airflow-composer-896625aed586 [Accessed 16 Sep. 2025].
- Pacheco, M. (2024). Key Considerations to Complete a Cloud Readiness Assessment .  [online] TierPoint, LLC. Available at: https://www.tierpoint.com/blog/cloud-readinessassessments-help-reduce-cloud-migration-risks/ [Accessed 15 Sep. 2025].
- PixelQA (2024). Cloud Security Testing Explained | How to Secure Cloud Environments . [online] Pixelqa.com. Available at: https://www.pixelqa.com/blog/post/securing-the-cloud-anintroduction-to-cloud-security-testing [Accessed 23 Aug. 2025].

- RapidFire Tools.  (2024).  What  is  a  Cloud  Readiness  Assessment?  |  RapidFire  Tools.  [online] Available at: https://www.rapidfiretools.com/blog/cloud-readiness-assessment/ [Accessed 15 Sep. 2025].
- Rasiksuhail (2023). Orchestrating dbt with Airflow: A Step-by-Step Guide to Automating Data Pipelines -Part I . [online] Medium. Available at: https://rasiksuhail.medium.com/orchestrating-dbt-with-airflow-a-step-by-step-guide-toautomating-data-pipelines-part-i-7a6db8ebc974 [Accessed 23 Aug. 2025].
- Risk  register  template    https://www.rocketlane.com/blogs/how-to-create-a-project-risk-registerfree-template
- Sharma,  B.P.  (2025)  'Optimizing  Cloud  Migration  Strategies  for  Large -Scale  Enterprises:  A Comparative Analysis of Lift-and-Shift, Replatforming, and Refactoring Approaches', Advances  in  Theoretical  Computation,  Algorithmic  Foundations,  and Emerging Paradigms , 15(2), pp. 1 -14. Available at: https://heilarchive.com/index.php/ATCAEP/article/view/2025-FEB-04 (Accessed: 23 August 2025).
- Svitla  Systems.  (2024).  Cloud  Migration  Readiness  Assessment ᐈ Svitla  Systems.  [online] Available at: https://svitla.com/blog/cloud-migration-readiness/ [Accessed 15 Sep. 2025].
- Uddin, M.N. (2024). The Benefits and Limitations of Lift and Shift Cloud Migration . [online] Rite Software. Available at: https://rite.digital/blog/the-benefits-and-limitations-of-lift-andshift-cloud-migration/ [Accessed 20 Sep. 2025].
- What is data migration? | Definition and common processes .  (n.d.).  Cloudflare.com. Retrieved August 23, 2025, from https://www.cloudflare.com/learning/cloud/what-is-datamigration/
- Wolford, B. (2018). What are the GDPR Fines? - GDPR.eu .  [online]  GDPR.eu.  Available  at: https://gdpr.eu/fines/ [Accessed 16 Sep. 2025].