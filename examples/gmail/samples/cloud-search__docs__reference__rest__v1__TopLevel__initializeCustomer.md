---
breadcrumbs: [Google Workspace]
canonical_url: https://developers.google.com/workspace/cloud-search/docs/reference/rest/v1/TopLevel/initializeCustomer
content_sha256: 0ea0ed7dc664b9d6fae8592b7a7e6003312fae45cb4d52c4c08fce9a2c4c3fd4
converter: html-to-markdown/3.x
description: Enables `third party` support in Google Cloud Search.
extractor: profile:devsite
fetched_at: '2026-10-28T14:02:31Z'
keywords: [google cloud search, body, enables support, search note, http request, requires admin, try enables]
last_modified: '2025-04-04T15:35:55Z'
low_confidence: false
profile: devsite
quality_flags: [uncrawled_internal]
quality_score: 1.0
render: http
sitemap_lastmod: '2025-07-24T17:08:37+00:00'
source_url: https://developers.google.com/workspace/cloud-search/docs/reference/rest/v1/TopLevel/initializeCustomer
title: 'Method: initializeCustomer'
---

# Method: initializeCustomer

- [HTTP request](#body.HTTP_TEMPLATE)
- [Request body](#body.request_body)
- [Response body](#body.response_body)
- [Authorization scopes](#body.aspect)
- [Try it!](https://developers.google.com/workspace/cloud-search/docs/reference/rest/v1/TopLevel/initializeCustomer#try-it)

Enables `third party` support in Google Cloud Search.

**Note:** This API requires an admin account to execute.

<a id="body.HTTP_TEMPLATE"></a>

### HTTP request {#http-request}

`POST https://cloudsearch.googleapis.com/v1:initializeCustomer`

The URL uses [gRPC Transcoding](https://google.aip.dev/127) syntax.

<a id="body.request_body"></a>

### Request body {#request-body}

The request body must be empty.

<a id="body.response_body"></a>

### Response body {#response-body}

If successful, the response body contains an instance of [`Operation`](https://developers.google.com/workspace/cloud-search/docs/reference/rest/v1/operations#Operation).

<a id="body.aspect"></a>

### Authorization scopes {#authorization-scopes}

Requires one of the following OAuth scopes:

- `https://www.googleapis.com/auth/cloud_search.settings.indexing`
- `https://www.googleapis.com/auth/cloud_search.settings`
- `https://www.googleapis.com/auth/cloud_search`

For more information, see the [Authorization guide](https://developers.google.com/workspace/guides/configure-oauth-consent).

<a id="try-it"></a>
