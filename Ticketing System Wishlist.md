# **Ticketing System Wishlist:** **Proof of Talk 2026**

## **Core Ticket Management**

**1\. Multiple Ticket Types** Ability to create and manage the following ticket types:

* Speaker\*  
* Partner\*  
* Press Pass\*+  
* VIP  
* VIP Black  
* General  
* Investor  
* Start Up \*+

  \* \= complimentary (free)  
  \+ \= requires application to receive code 

**2\. Application-Only Tickets**

* **Start Up Pass:** Application form \+ payment required  
* **Press Pass:** Application form only, approved applicants receive a code to claim (no payment option)

**3\. Email Communications from Dashboard** Ability to send confirmation emails, vouchers, and forms directly to attendees from the admin dashboard

## **Dashboard & Filtering**

**4\. Dashboard Filters** Filterable columns in admin view:

* Voucher Code  
* Name  
* Ticket Type  
* Email  
* Company  
* Order Status  
* Payment Status

**5\. CSV Export with Filters** Ability to export data from Orders page to CSV, with active filters applied before export

**6\. Real-Time Sales Sync** API integration to Google Sheets for:

* Live sales tracking  
* Automated revenue calculations  
* Real-time reporting

## **Payment & Upgrades**

**7\. In-Order Upsell Functionality** Allow attendees to upgrade their ticket within the same order (even if original ticket was complimentary) without canceling and creating a new order. Discount codes should apply to upgraded price difference.

**8\. Simplified Ticket Claiming (No Full Account Required)** Users can claim vouchers or codes with minimal friction:

* Required fields only: Name, Company, Title, Email  
* No home address or mobile phone required to claim ticket  
* Payment details only required if ticket is paid  
* Optional: Full profile creation for additional features (referral links, social sharing)

## **Referral & Social Features**

**9\. Referral Tracking**

* Unique referral links/codes for ambassadors and affiliates  
* Track sales attributed to each referral link  
* Dashboard view of referral performance

**10\. Social Sharing with Custom Cards** After ticket confirmation, provide:

* "I'm Attending" social share button  
* Built-in social media card generator where user can add their headshot  
* Share from app if full profile is created  
* Option to share referral link alongside attendance announcement

## **Event Operations**

**11\. Mobile Check-In App**

* Mobile app for event staff to scan QR codes  
* Real-time check-in status updates  
* Offline mode capability (syncs when back online)

**12\. Referral Rewards Automation** Track referral sales and trigger automated rewards:

* Example: Sell 2x General Pass → auto-upgrade to VIP  
* Customizable reward tiers  
* Automated notification to referrer when reward is unlocked  
* Ability to manually override/adjust rewards

## **Additional Nice-to-Haves**

**13\. Voucher Code Generator** Bulk create unique voucher codes for complimentary passes with customizable prefixes (e.g., MINDS1000-XXXX)

**14\. Waitlist Management** Automatic waitlist for sold-out ticket types with email notifications when spots open

**15\. Multi-Currency Support** Accept payments in EUR and stablecoin with automatic conversion

**16\. Attendee Self-Service Portal** Allow attendees to update their own details (name, company, title, dietary restrictions) without admin intervention (if choose to enrich) 

**17\. Analytics Dashboard**

* Sales by ticket type over time  
* Conversion rates (applications → approvals → claimed tickets)  
* Referral performance leaderboard  
* Revenue forecasting based on current pace

## **Integration Requirements**

* Google Sheets API (real-time sync)  
* Stripe or similar payment processor  
* Email service (SendGrid, Mailgun, or built-in)  
* Social media sharing APIs (LinkedIn, X/Twitter)  
* QR code generation

