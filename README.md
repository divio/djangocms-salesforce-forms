Django CMS Salesforce Forms
===========================

An knockoff of aldryn-forms that submits to *SalesForce
Marketing Cloud (SFMC)*.

Example Data Extension configuration in the ``Form_Submission_Data``
Data Extension.


| Attribute Name      | Data Type | Length | Nullable |
|:--------------------|:----------|:-------|:---------|
| SubscriberKey       | Text      | 254    | No       |
| EmailAddress        | Email     | 254    | No       |
| Trigger Key         | Text      | 255    | Yes      |
| First Name          | Text      | 25     | Yes      |
| Last Name           | Text      | 25     | Yes      |
| Job Title           | Text      | 100    | Yes      |
| Company Name        | Text      | 100    | Yes      |
| Street Address      | Text      | 100    | Yes      |
| Phone Number        | Phone     | 50     | Yes      |
| City                | Text      | 50     | Yes      |
| Postal Code         | Text      | 25     | Yes      |
| State_Region        | Text      | 25     | Yes      |
| Country             | Text      | 50     | Yes      |
| Name of Form        | Text      | 100    | No       |
| Date Submitted      | Date      |        | Yes      |
| MarketingQuestion1  | Text      | 255    | Yes      |
| MarketingAnswer1    | Text      | 255    | Yes      |
| MarketingQuestion2  | Text      | 255    | Yes      |
| MarketingAnswer2    | Text      | 255    | Yes      |
| MarketingQuestion3  | Text      | 255    | Yes      |
| MarketingAnswer3    | Text      | 255    | Yes      |
| MarketingQuestion4  | Text      | 255    | Yes      |
| MarketingAnswer4    | Text      | 255    | Yes      |
| MarketingQuestion5  | Text      | 255    | Yes      |
| MarketingAnswer5    | Text      | 255    | Yes      |
| MarketingQuestion6  | Text      | 255    | Yes      |
| MarketingAnswer6    | Text      | 255    | Yes      |
| MarketingQuestion7  | Text      | 255    | Yes      |
| MarketingAnswer7    | Text      | 255    | Yes      |
| MarketingQuestion8  | Text      | 255    | Yes      |
| MarketingAnswer8    | Text      | 255    | Yes      |
| MarketingQuestion9  | Text      | 255    | Yes      |
| MarketingAnswer9    | Text      | 255    | Yes      |
| MarketingQuestion10 | Text      | 255    | Yes      |
| MarketingAnswer10   | Text      | 255    | Yes      |


https://help.marketingcloud.com/en/documentation/exacttarget/subscribers/web_collect/#section_16


### Running tests

```bash
make setup
make test
```
