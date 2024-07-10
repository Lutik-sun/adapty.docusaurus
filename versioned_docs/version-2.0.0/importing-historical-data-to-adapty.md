---
title: "Importing historical data to Adapty"
description: ""
metadataTitle: ""
---

# Importing historical data to Adapty

After you install Adapty SDK and release the app, you can find your users and subscribers in the [Profiles](profiles-crm) section. But what if you have legacy infrastructure and want to migrate to Adapty? Or just want to see your existing data in Adapty?

:::info
Data import is not mandatory

Adapty will automatically grant access levels to the historical users and restore their purchase events once they open the app with the SDK on board. For that use case, there is no need for importing historical data. The import will ensure percise analytics if you have a lot of historical transactions, but generaly not required for the migration.
:::

You can export your data to a CSV file and then import it to Adapty. Let's see how to do that.

## Data format

Please, note, that we expect **separate** files for [iOS](https://docs.google.com/spreadsheets/d/1QXs-zeoGnrljVbL7OnIFHs3YLdwkYzNk5-VAu2TqPVk/edit?usp=sharing), [Android](https://docs.google.com/spreadsheets/d/1xJW4t9Sr1gvviMRzpTtChLJ8hEQTbojqsxZxIcr-ymM/edit?usp=sharing) and Stripe. Hopefully, fields without descriptions are self-explained. 

| Field name | Description |
|----------|-----------|
| **user_id** | Id of your user |
| **subscription_expiration_date** | The date of subscription expiration, i.g. next charging date, datetime with timezone (2020-12-31T23:59:59-06:00) |
| **created_at** | Datetime of profile creation (2019-12-31T23:59:59-06:00) |
| **birthday** | date (2000-12-31) |
| **email** |  |
| **facebook_user_id** |  |
| **gender** | f|m |
| **phone_number** |  |
| **country** | format [ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) |
| **first_name** |  |
| **last_name** |  |
| **last_seen** | datetime with timezone (2020-12-31T23:59:59-06:00) |
| **idfa** | iOS Identifier for advertiser |
| **idfv** |  |
| **advertising_id** | It's similar to idfa, but for Android |
| **amplitude_user_id** |  |
| **amplitude_device_id** |  |
| **mixpanel_user_id** |  |
| **appmetrica_profile_id** |  |
| **appmetrica_device_id** |  |
| **appsflyer_id** |  |
| **adjust_device_id** |  |
| **facebook_anonymous_id** |  |
| **branch_id** |  |
| **attribution_source** | appsflyer|adjust|branch|apple_search_ads |
| **attribution_status** | organic|non_organic|unknown |
| **attribution_channel** |  |
| **attribution_campaign** |  |
| **attribution_ad_group** |  |
| **attribution_ad_set** |  |
| **attribution_creative** |  |
| **apple_original_transaction_id** | <p>The original transaction ID or OTID ([learn more](https://developer.apple.com/documentation/appstoreserverapi/originaltransactionid)), used in StoreKit 2 import mechanism. As one user can have multiple OTIDs, it is enough to provide at least one for successful import.</p><p></p><p>**Note:** We require In-app purchase API credentials for this import to be set up in your Adapty Dashboard. Learn how to do it [here](in-app-purchase-api-storekit-2).</p> |
| **google_product_id** |  |
| **google_purchase_token** |  |
| **google_is_subscription** | 1|0 |
| **stripe_token** | Token of a Stripe object that represents a unique purchase. Could either be a token of Stripe's Subscription (`sub_...`) or Payment Intent (`pi_...`). |


:::warning
Required Fields

There are 2 groups of required fields: **user_id** and data identifying purchase for the corresponding platform:

- iOS: **apple_original_transaction_id**
- Android: **google_product_id+google_purchase_token+google_is_subscription**
- Web: **stripe_token**

Without them Adapty won't be able to fetch transactions.

We highly recommend passing the **country**. If it's not passed, we will use the USD price and the United States country as a fallback.

If you want the cohort analytics to be precise, please specify **created_at** as well, otherwise we'll have to assume that date from the first purchase date.
:::

- Make sure that the column names are specified and the same as in the table above, check for typos. 
- Don't bother adding empty columns for data you don't have.
- Please, make sure there are no extra columns, that are not mentioned in the table.
- Separate values by commas and **don't** take values in quotation marks.
- That there may be several **apple_original_transaction_id**'s for one user. In that case, we need all of them. Otherwise, we may not be able to restore consumable purchases. Please, put them into different lines.

Once again, please refer to the examples above. If the file is more than 1 GB, please attach a data sample with just ~100 lines so we can check it. 

Upload the files to Google Disk (you can compress them, but please keep them separate) and share the link with our team. 

## Prices (only for iOS)

In order for us to fetch the prices and price changes for all iOS products, including the legacy products that will never be purchased through Adapty SDK, kindly share the docs with those prices.  
You don't need to bother creating the correct format, as it is already provided by Apple. Here is how you can get it from Apple Connect:

1. Open the desired subscription
2. "View all Subscription Pricing" here


<div style={{ textAlign: 'center' }}>
  <img 
    src="https://files.readme.io/98dd52e-CleanShot_2023-08-25_at_11.55.082x.png" 
    alt="Importing Historical Data to Adapty - Photo 2" 
    style={{ width: 'auto', border: '1px solid grey' }}
  />
</div>





3. And "Download" here


<div style={{ textAlign: 'center' }}>
  <img 
    src="https://files.readme.io/96f5919-CleanShot_2023-08-25_at_11.56.052x.png" 
    alt="Image" 
    style={{ width: 'auto', border: '1px solid grey' }}
  />
</div>





Below is an example of a file you should get. We'll understand the products' IDs from the names of the **folders** that collect the prices, so please name the folders, separately for each product. For some reason, Apple doesn't mention the product name anywhere in the exported file, so it must be done manually. Probably, there will be several folders, please add them to a flat archive to make sure nothing gets lost.  
Please, refer to [this example](https://drive.google.com/file/d/1IvJ11ezX_c2HIbr3NvTubQQfXKz5GvBY/view?usp=sharing).


<div style={{ textAlign: 'center' }}>
  <img 
    src="https://files.readme.io/32eaf05-Screenshot_2022-12-23_at_00.14.21.png" 
    alt="Importing Historical Data to Adapty - Photo 4" 
    style={{ width: '60%', border: '1px solid grey' }}
  />
</div>





Finally, please, make sure to set up the [App Store price increase logic](https://docs.adapty.io/docs/general#4-app-store-price-increase-logic) to avoid any analytics discrepancies. Please, confirm that you've done it in your request to Support. Yes, we really care for the precision of our analytics 🤓

## Import data to Adapty

Right now we don't have an automatic tool for that. Please contact us using the chat widget on the dashboard or just email us at [support@adapty.io](mailto:support@adapty.io).

Do not worry - importing historical data will not create any duplicates, even if that data overlaps with the one you already have in Adapty.