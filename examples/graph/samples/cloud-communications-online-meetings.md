---
canonical_url: https://learn.microsoft.com/en-us/graph/cloud-communications-online-meetings
content_sha256: dfd531bf30aea02b7d8995bc85812a2acd769e9e75ae2c7437d670bf36e8316a
converter: html-to-markdown/3.x
description: Use the cloud communications API in Microsoft Graph to create or join online meetings. Create a meeting that takes place in the future or instantaneously.
etag: '"V7hnZSeA9iPiT4OuVMcfZY9IZCw="'
extractor: profile:mslearn
fetched_at: '2026-10-28T13:59:18Z'
keywords: [join online meetings, meeting coordinates, cloud communications api, online meetings provide, create]
last_modified: '2024-11-07T08:00:00Z'
locale: en-us
low_confidence: false
profile: mslearn
quality_flags: [uncrawled_internal]
quality_score: 1.0
render: http
sitemap_lastmod: '2024-11-07'
source_url: https://learn.microsoft.com/en-us/graph/cloud-communications-online-meetings
title: Create or join online meetings
version: v1.0
---

# Create or join online meetings {#create-or-join-online-meetings}

Use the cloud communications API in Microsoft Graph to create or join online meetings. Online meetings provide the ability to specify certain details, such as the subject of the meeting and who all the attendees are. You can also set the date and time for when the meeting starts and ends.

Online meetings provide the flexibility to create a meeting that takes place in the future or instantaneously. The ability to set up a meeting that starts immediately after it's created is ideal for unexpected issues and other incidents that require the immediate attention of the attendees.

> [!NOTE]
>
> This set of APIs allows the flexibility and richer integration with Microsoft Teams or Skype capabilities; it does not update or create any event in a calendar. For a convenient approach to add an online meeting to an Outlook calendar, use the calendar API. See [Choose an API in Microsoft Graph to create and join online meetings](https://learn.microsoft.com/en-us/graph/choose-online-meeting-api) for more information.

## Create an online meeting {#create-an-online-meeting}

When you create an online meeting, you receive [coordinates](https://learn.microsoft.com/en-us/graph/api/resources/onlinemeeting) for the meeting. When participants join the meeting using these meeting coordinates, a group call is created.

When all the participants leave the group call, the group call ends. Participants can still rejoin the meeting afterward using the same meeting coordinates, but this will create another group call.

> [!NOTE]
>
> The created meetings do not appear on calendars.

## Join an online meeting {#join-an-online-meeting}

After an online meeting is created, users can join in two ways:

1. Through the browser, using the **joinWebURL** that was returned as part of the [meeting coordinates](https://learn.microsoft.com/en-us/graph/api/resources/onlinemeeting).

2. Through the [create call API](https://learn.microsoft.com/en-us/graph/api/application-post-calls#example-5-join-scheduled-meeting-with-service-hosted-media), which requires that you provide the [meeting coordinates](https://learn.microsoft.com/en-us/graph/api/resources/onlinemeeting), ([organizermeetinginfo](https://learn.microsoft.com/en-us/graph/api/resources/organizermeetinginfo), and [chatInfo](https://learn.microsoft.com/en-us/graph/api/resources/chatinfo)).

## Related content {#related-content}

- [Online meeting permissions](https://learn.microsoft.com/en-us/graph/permissions-reference)
- [Choose an API in Microsoft Graph to create and join online meetings](https://learn.microsoft.com/en-us/graph/choose-online-meeting-api)
- [Teams API overview](https://learn.microsoft.com/en-us/graph/teams-concept-overview)

---

## Feedback {#ms--feedback}

Was this page helpful?
