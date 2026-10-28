---
breadcrumbs: [Google Workspace]
canonical_url: https://developers.google.com/workspace/chat/api/reference/rest/v1/spaces.messagePins/delete
content_sha256: cc51267f5439c0f56139a27292f2870536318227f6a7f5ce74e10ca15c38f8f3
converter: html-to-markdown/3.x
description: Deletes a message pin.
extractor: profile:devsite
fetched_at: '2026-10-28T14:04:33Z'
keywords: [http request, message pin, authorization scopes, path parameters, request body, remove format, parameters path-parameters parameters, space messagepins]
last_modified: '2026-06-01T17:25:44Z'
low_confidence: false
profile: devsite
quality_flags: [html_table_kept, uncrawled_internal]
quality_score: 1.0
render: http
sitemap_lastmod: '2026-06-01T17:25:53+00:00'
source_url: https://developers.google.com/workspace/chat/api/reference/rest/v1/spaces.messagePins/delete
title: 'Method: spaces.messagePins.delete'
---

# Method: spaces.messagePins.delete

- [HTTP request](#body.HTTP_TEMPLATE)
- [Path parameters](#body.PATH_PARAMETERS)
- [Request body](#body.request_body)
- [Response body](#body.response_body)
- [Authorization scopes](#body.aspect)
- [Try it!](https://developers.google.com/workspace/chat/api/reference/rest/v1/spaces.messagePins/delete#try-it)

Deletes a message pin.

Requires [user authentication](https://developers.google.com/workspace/chat/authenticate-authorize-chat-user) with one of the following [authorization scopes](https://developers.google.com/workspace/chat/authenticate-authorize#chat-api-scopes):

- `https://www.googleapis.com/auth/chat.spaces.pins`
- `https://www.googleapis.com/auth/chat.spaces`

<a id="body.HTTP_TEMPLATE"></a>

### HTTP request {#http-request}

`DELETE https://chat.googleapis.com/v1/{name=spaces/*/messagePins/*}`

The URL uses [gRPC Transcoding](https://google.aip.dev/127) syntax.

<a id="body.PATH_PARAMETERS"></a>

### Path parameters {#path-parameters}

<table id="body.PATH_PARAMETERS-table">
<colgroup>
<col>
<col>
</colgroup>
<thead>
<tr>
<th colspan="2">Parameters</th>
</tr>
</thead>
<tbody>
<tr id="body.PATH_PARAMETERS.name">
<td><code>name</code></td>
<td>
<p><code>string</code></p>
<p>Required. The resource name of the message pin to remove. Format: spaces/{space}/messagePins/{messagePin}</p>
</td>
</tr>
</tbody>
</table>

<a id="body.request_body"></a>

### Request body {#request-body}

The request body must be empty.

<a id="body.response_body"></a>

### Response body {#response-body}

If successful, the response body is an empty JSON object.

<a id="body.aspect"></a>

### Authorization scopes {#authorization-scopes}

Requires one of the following OAuth scopes:

- `https://www.googleapis.com/auth/chat.spaces.pins`
- `https://www.googleapis.com/auth/chat.spaces`

For more information, see the [Authorization guide](https://developers.google.com/workspace/chat/authenticate-authorize).

<a id="try-it"></a>
