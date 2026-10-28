---
layout: default
permalink: /kindly/en/privacy/
app: kindly
app_name: Kindly
description: "Privacy policy for Kindly, the gratitude journal and daily quote app: what information the app collects, why it is used, and how to contact us."
image: /kindly/img/kindly-app-icon.png
lang: en
locale: en_US
alternates:
  ko: /kindly/privacy/
  en: /kindly/en/privacy/
---

# Kindly Privacy Policy

Effective: October 18, 2026 (restriction records, privacy officer, destruction, security measures and remedies added)

Kindly ("the app") does not collect information that directly identifies you, such as your name, email address or phone number. The app creates an anonymous account on each device, without sign-up, to run the community, and collects error reports and anonymous usage statistics to keep the app stable and improve it.

## 1. Information we collect and why

| Type | What is collected | Purpose | Service |
|---|---|---|---|
| Community | A randomly generated anonymous account ID, posts you write (type and text), reactions, report and block records | Running the community, handling reported posts | Supabase |
| Restrictions | If your account is restricted from posting for breaking the rules: anonymous account ID, reason, date and time | Enforcing the Terms of Use | Supabase |
| Post review | The text of posts you submit and the review result | Automatically keeping harmful posts from going public, improving the review rules | TypeSafe AI |
| Error reports | Error logs when the app crashes or hits an error, device model, OS version, app version | Finding and fixing bugs | Firebase Crashlytics |
| Usage statistics | Screen views and feature events (for example: writing a post, reacting, favouriting a quote, sharing an image), a randomly generated app installation ID, device and OS information, approximate region estimated from your IP address (the IP address itself is not stored) | Understanding how features are used and improving the app | Google Analytics for Firebase |

Usage statistics never include post text or your anonymous account ID.

We do not collect:

- Your name, email, phone number, contacts or precise location
- The advertising identifier (IDFA)
- Your activity in other apps or on websites (we do not track you)

## 2. Information stored on your device

- Today's quote, favourite quotes, the selected theme and background stay on your device (in storage shared by the app and the widget).
- Posts you bookmark in the community are kept as a copy (text and author name) only on the device of the person who bookmarked them, so they can find them in Collection. They are not sent to our servers. If the author later deletes the post or their account, we cannot reach copies already saved on other people's devices; they remain until that person removes the bookmark or the app.
- Whether you accepted the community guidelines and Terms of Use is stored on your device only.
- Deleting the app deletes this information.

## 3. Retention

- Community data: until you delete the post or your account. Deleting your account immediately deletes your posts, reactions, reports and blocks.
- Restriction records: until the account is deleted
- Post review records: until the post is deleted
- Error reports: deleted automatically 90 days after collection
- Usage statistics: deleted automatically 2 months after collection

## 4. How data is destroyed

- When the retention period ends or you ask us to delete data, we destroy it without delay.
- Server data is deleted immediately from the production database in a way that cannot be recovered. Error reports and usage statistics are deleted automatically by each service after the periods in section 3.

## 5. Service providers and international transfer

| Recipient | Country | Data | Purpose |
|---|---|---|---|
| Supabase Inc. | Republic of Korea (stored in the Seoul region) | Community data in section 1 | Server hosting |
| TypeSafe AI | Countries where the provider's servers are located | Text of submitted posts | Automated review |
| Google LLC (privacy@google.com) | The United States and other countries where Google operates data centers | Error reports and usage statistics in section 1 | Crash reporting and analytics |

- When and how: while you use the app, over encrypted connections
- Retention: as in section 3

## 6. Security measures

- All traffic between the app and our servers is encrypted (HTTPS).
- Row-level access control lets you write and delete only your own posts, and access to production data is limited to as few people as possible.
- Server admin keys and third-party service keys are never shipped in the app; they are kept separately in the server's secret store.

See https://firebase.google.com/support/privacy for how Google handles data.

## 7. Permissions

The app does not ask for camera, photos, location, contacts or notification permissions. Images are shared through your device's share sheet (iOS share sheet or Android share menu); they are saved to Photos or your gallery only if you choose that there.

## 8. Sharing

Tapping Share opens your device's share sheet. Quote images go only to the app or person you choose, and are then handled under that service's privacy policy.

## 9. Sending feedback

Settings › Send feedback opens your mail app with the app version and device model / OS version filled in. Nothing is sent unless you tap Send. We use your email only to reply and to improve the app.

## 10. Your rights

- You can delete any of your posts from its ⋯ menu.
- Settings › Delete account and data removes your account and all your posts, reactions, reports and blocks at once. Deleting only the app leaves your posts on the server, so delete them first. If you already removed the app, see [Request account deletion](/kindly/en/support/#delete-account).
- To request deletion or restriction of error reports and usage statistics, email us at the address below.

## 11. Children

The app is not directed to children under 14 and does not knowingly collect their information.

## 12. Privacy officer and contact

- Privacy officer: the Team Cumulus operator
- Contact: contact@cumulus.team

## 13. Remedies

For advice or remedies regarding a privacy infringement, you can contact these Korean authorities:

- Personal Information Dispute Mediation Committee: 1833-6972 (www.kopico.go.kr)
- Personal Information Infringement Report Center: 118 (privacy.kisa.or.kr)
- Supreme Prosecutors' Office: 1301 (www.spo.go.kr)
- Korean National Police Agency: 182 (ecrm.police.go.kr)

If this policy changes, the new version will be posted here with its effective date.
