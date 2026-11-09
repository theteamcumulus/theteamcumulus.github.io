---
layout: default
permalink: /lifestamp/en/privacy/
---

# Lifestamp Privacy Policy

Effective: from the release of version 1.0.1 on iPhone, and from the release on Google Play on Android

Lifestamp ("the app") does not collect information that directly identifies you, such as your name, email address or phone number. The photos you take and the date and time stamped on them are stored only on your device and are never sent anywhere. To keep the app stable and improve it, we collect only the error reports and usage statistics described below. No name, email address or account is attached to them.

## 1. Information we collect and why

| Type | What is collected | Purpose | Service |
|---|---|---|---|
| Error reports | Error logs when the app crashes or hits an error, device model, OS version, app version, a random installation ID, session information, network connection type, memory and storage usage, screen orientation, and app-usage events just before the error | Finding and fixing bugs | Firebase Crashlytics |
| Usage statistics | Screen views and feature events (for example: taking a photo, choosing a stamp style, sharing), a randomly generated app installation ID, device and OS information, approximate region estimated from your IP address (the IP address itself is not stored) | Understanding how features are used and improving the app | Google Analytics for Firebase |

On Android, the error details in a report contain only the exception type (class name) and the code location (stack trace). They do not contain error message text, file paths, photos, photo capture times or locations.

We do not collect:

- Your photos, the date, time and weather stamped on them, or photo location data
- The advertising identifier (IDFA on iPhone, advertising ID on Android; neither version uses advertising, and the Android app does not request the advertising ID permission), contacts or precise location
- Your activity in other apps or on websites (we do not track you)

## 2. Information stored on your device

- Photos taken in the app (original, stamped photo and thumbnail) and their capture time are kept only in the app's storage on your device.
- The weather at the time of each photo (condition and temperature) is stored with the photo's record on your device. Your location is not stored.
- Your last stamp style, aspect ratio, and the "Auto-Save to Photos" and "Show Weather on Stamp" settings are stored on your device.
- On iPhone, if you use iPhone backup (iCloud Backup or a computer backup), the app's storage is included in your backup. Backups are managed by Apple and you; we cannot access them.
- On Android, the app's storage is excluded from Google backup and device-to-device transfer. We can't guarantee how a phone maker's own migration tools behave.
- Deleting the app deletes the photos and settings in the app's storage. Copies saved to the Photos app on iPhone, or to the gallery (Photos) app on Android, must be deleted in that app.

## 3. Retention

- Error reports: deleted automatically 90 days after collection
- Usage statistics: deleted automatically 2 months after collection

## 4. Service providers and international transfer

The information in section 1 is processed by Firebase, a service of Google LLC, and is transferred to and stored on Google servers in the United States and other countries.

- Recipient: Google LLC (privacy@google.com)
- Countries: the United States and other countries where Google operates data centers
- Data: the error reports and usage statistics in section 1
- When and how: from time to time while you use the app, over an encrypted connection
- Purpose and retention: as described in sections 1 and 3

You can learn more about how Google handles this data at https://firebase.google.com/support/privacy

To get the weather for your stamp, the app sends your approximate location to Open-Meteo (from the version that includes stamp weather, on both iPhone and Android). It is sent only while weather is on: if you don't allow location or turn off "Show Weather on Stamp" in settings, nothing is sent. The app never uploads your photos.

- Recipient: OpenMeteo GmbH (Switzerland, https://open-meteo.com)
- Data: latitude and longitude reduced to about 1 km, and the IP address used for the network connection
- When and how: about every 10 minutes while the camera screen is open, over an encrypted connection
- Purpose: looking up the current weather
- Retention: may remain in Open-Meteo's server logs and is deleted after 90 days (per Open-Meteo's terms). The app developer does not receive this data.

## 5. Permissions

- Camera: used to take photos and show the stamp preview on screen.
- Add to Photos (iPhone): used to save stamped photos to the Photos app. The app cannot read or change existing photos in Photos (add-only access). You can turn off auto-save in the app's settings.
- Saving to the gallery (Android): stamped photos are saved to the gallery (Pictures/Lifestamp). No photo or storage permission is needed and the app does not read existing photos. You can turn off auto-save in the app's settings.
- Location (while using the app): used to add the current weather to your stamp, based on your approximate location. On Android the app asks only for approximate location, never precise location. No location data is added to your photos. If you don't allow it, or turn off "Show Weather on Stamp" in settings, photos are stamped without weather and your location is not used.

You can install and open the app without granting these permissions, and you can change them anytime: on iPhone in Settings > Lifestamp, on Android in Settings > Apps > Lifestamp > Permissions.

## 6. Sharing

When you tap Share, the iOS share sheet opens on iPhone and the Android share sheet opens on Android. Your photo goes only to the app or person you choose, and is then handled under that service's privacy policy.

## 7. Feedback

Tapping Settings (top right of the camera screen) > Send Feedback opens your Mail app. To help us troubleshoot, the message is pre-filled with the app version, device model and OS version. Nothing is sent until you review it and tap Send, and you can delete the pre-filled text. We use the emails we receive only to reply to you and improve the app.

## 8. Your rights

The information we collect does not directly identify you, but if you would like it deleted or its processing stopped, please email us at the address below. Once you delete the app, no further information is collected. You can remove the photos and settings on your device at any time by deleting photos in the app or deleting the app.

## 9. Children's privacy

The app is not directed at children, does not ask for age and does not separately collect personal information from children.

## 10. Contact

contact@cumulus.team

If this policy changes, we will post the new version on this page with its effective date.

### Previous versions

- From October 10, 2026 (1.0.0): no information collected
