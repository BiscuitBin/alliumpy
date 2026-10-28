---
breadcrumbs: [Google Workspace]
canonical_url: https://developers.google.com/workspace/admin/domain-shared-contacts/overview
content_sha256: db0129d262446a759a486ff43a104c320cf9b1a0b426b6c0516304ec74d324c0
converter: html-to-markdown/3.x
description: The Domain Shared Contacts API lets applications get and update external contacts shared with all users in a Google Workspace domain. Shared contacts are visible to all users of a Google Workspace…
extractor: profile:devsite
fetched_at: '2026-10-28T14:02:24Z'
keywords: [domain shared contacts, shared contacts api, google data apis, google workspace domain, shared contacts]
last_modified: '2026-09-03T22:21:54Z'
low_confidence: false
profile: devsite
quality_flags: [uncrawled_internal]
quality_score: 1.0
render: http
sitemap_lastmod: '2026-09-10T21:46:31+00:00'
source_url: https://developers.google.com/workspace/admin/domain-shared-contacts/overview
title: Domain Shared Contacts API overview
---

# Domain Shared Contacts API overview

The Domain Shared Contacts API lets applications get and update external contacts shared with all users in a Google Workspace domain. Shared contacts are visible to all users of a Google Workspace domain and all Google services have access to the contact list.

> [!WARNING]
>
> The Domain Shared Contacts API is for *external* contacts only. Using this API to create contact information for internal users or groups can result in duplicate information and unexpected behavior. To manage Google Workspace internal users' contact information, use the [Directory API](https://developers.google.com/workspace/admin/directory).

Use the Domain Shared Contacts API to create, edit, or delete shared contacts, and query for contacts matching specific criteria.

The Domain Shared Contacts API is only available to Google Workspace accounts. To use the API, [enable the Domain Shared Contacts API in the Admin console](https://support.google.com/a/answer/60757). Changes can take up to 24 hours to reflect in auto-complete and the contact manager.

This document background on the Domain Shared Contacts API and examples for managing contacts using XML and HTTP. To learn more, see the [client libraries](https://developers.google.com/api-client-library).

## Audience {#audience}

This document is for developers writing client applications that manipulate Google contact lists using HTTP and XML. It assumes knowledge of the [Google Data APIs protocol](https://developers.google.com/gdata/docs/2.0/basics).

Linux and macOS users can try the examples in this document using [curl](https://curl.haxx.se/) or [wget](https://www.gnu.org/software/wget/). See [Use curl with Google Data APIs](https://developers.google.com/gdata/articles/using_cURL).

## Principles {#principles}

The Domain Shared Contacts API follows the principles of the [Google Data APIs](https://developers.google.com/gdata/docs/developers-guide). Google Data APIs are based on Atom 1.0, RSS 2.0, and the Atom Publishing Protocol.

## Specify a version {#specify_a_version}

All requests sent using the Domain Shared Contacts API should specify version 3.0:

```text
GData-Version: 3.0
```

If you can't set HTTP headers, specify `v=3.0` as a query parameter. The HTTP header method is recommended.

> [!NOTE]
>
> Client libraries supply version headers automatically. Don't use the `v=3.0` parameter with a client library.
