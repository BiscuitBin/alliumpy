---
breadcrumbs: [Google Workspace]
canonical_url: https://developers.google.com/workspace/gmail/api/guides/handle-errors
content_sha256: f0bb0102f64945b5f6bbe41d932f4e91118db5c8fa08852e72824bc4ba81d6d2
converter: html-to-markdown/3.x
description: 'The Gmail API returns two levels of error information:'
extractor: profile:devsite
fetched_at: '2026-10-28T14:03:10Z'
keywords: [gmail api, limits, error, per-user, requests]
last_modified: '2026-09-15T17:25:47Z'
low_confidence: false
profile: devsite
quality_flags: [uncrawled_internal]
quality_score: 1.0
render: http
sitemap_lastmod: '2026-09-15T17:26:00+00:00'
source_url: https://developers.google.com/workspace/gmail/api/guides/handle-errors
title: Resolve errors
---

# Resolve errors

The Gmail API returns two levels of error information:

- HTTP error codes and messages in the header.
- A JSON object in the response body with additional details that can help you determine how to handle the error.

Your Gmail app should catch and handle all errors you encounter when using the REST API. This guide provides instructions on how to resolve specific Gmail API errors.

## HTTP status code summary {#status-codes}

| Error code                           | Description                                                                                                  |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------ |
| `200 - OK`                           | The request is successful (this is the standard response for successful HTTP requests).                      |
| `400 - Bad Request`                  | The server couldn't fulfill the request due to a client error.                                               |
| `401 - Unauthorized`                 | The request contains invalid credentials.                                                                    |
| `403 - Forbidden`                    | The server received and understood the request, but the user doesn't have permission to perform the request. |
| `404 - Not Found`                    | The requested resource couldn't be found.                                                                    |
| `429 - Too Many Requests`            | Too many requests to the API.                                                                                |
| `500, 502, 503, 504 - Server Errors` | An unexpected error occurred while processing the request.                                                   |

## 400 errors {#400-errors}

These errors mean that the request has an error, often due to a missing required parameter.

### `badRequest` {#bad-request}

This error can occur from any one of the following issues in your code:

- A required field or parameter is missing.
- A supplied value or combination of fields is invalid.
- The attachment is invalid.

> [!NOTE]
>
> This list isn't exhaustive; other issues can cause a 400 error.

The following JSON sample is a representation of this error:

```json
{
  "error": {
    "code": 400,
    "errors": [
      {
        "domain": "global",
        "location": "orderBy",
        "locationType": "parameter",
        "message": "Sorting is not supported for queries with fullText terms. Results are always in descending relevance order.",
        "reason": "badRequest"
      }
    ],
    "message": "Sorting is not supported for queries with fullText terms. Results are always in descending relevance order."
  }
}
```

To fix this error, check the `message` field and adjust your code accordingly.

## 401 errors {#401-errors}

These errors mean the request doesn't contain a valid access token.

### `authError` {#auth-error}

This error occurs when the access token you're using is either expired or invalid. Missing authorization for the requested scopes can also cause this error. The following JSON sample is a representation of this error:

```json
{
  "error": {
    "errors": [
      {
        "domain": "global",
        "reason": "authError",
        "message": "Invalid Credentials",
        "locationType": "header",
        "location": "Authorization",
      }
    ],
    "code": 401,
    "message": "Invalid Credentials"
  }
}
```

To fix this error, refresh the access token using the long-lived refresh token. If you're using a client library, it automatically handles token refresh. If this fails, direct the user through the OAuth flow, as described in [Learn about authentication and authorization](https://developers.google.com/workspace/guides/auth-overview).

For additional information on Gmail limits, see [Usage limits](https://developers.google.com/workspace/gmail/api/reference/quota).

## 403 errors {#403-errors}

These errors occur when you exceed a usage limit or the user doesn't have the correct privileges. To determine the cause, evaluate the `reason` field of the returned JSON. This error occurs in the following situations:

- Your app can't be used within the authenticated user's domain.
- The project exceeded the daily limit.
- The user exceeded the rate limit.
- The project exceeded the rate limit.

For more information, see [Usage limits](https://developers.google.com/workspace/gmail/api/reference/quota).

### `dailyLimitExceeded` {#daily-limit}

This error occurs when your project reaches its API limit. The following JSON sample is a representation of this error:

```json
{
  "error": {
    "errors": [
      {
        "domain": "usageLimits",
        "reason": "dailyLimitExceeded",
        "message": "Daily Limit Exceeded"
      }
    ],
    "code": 403,
    "message": "Daily Limit Exceeded"
  }
}
```

This error occurs when the application owner sets a quota limit to cap usage of a particular resource. To fix this error, raise the quota in the Google Cloud project. For more information, see [Manage quota limits](#manage-quotas).

### `domainPolicy` {#domain-policy}

This error occurs when the policy for the user's domain doesn't allow your app to access Gmail. The following JSON is the representation of this error:

```json
{
  "error": {
    "errors": [
      {
        "domain": "global",
        "reason": "domainPolicy",
        "message": "The domain administrators have disabled Gmail apps."
      }
    ],
    "code": 403,
    "message": "The domain administrators have disabled Gmail apps."
  }
}
```

To fix this error, try the following:

1. Inform the user that the domain doesn't allow your app to access Gmail.
2. Instruct the user to contact their domain administrator to request access for your app.

### `rateLimitExceeded` {#rate-limit}

This error indicates that the user has reached the maximum request rate for the Gmail API. This limit varies depending on the request type. The following JSON sample is a representation of this error:

```json
{
  "error": {
  "errors": [
    {
    "domain": "usageLimits",
    "message": "Rate Limit Exceeded",
    "reason": "rateLimitExceeded",
    }
  ],
  "code": 403,
  "message": "Rate Limit Exceeded"
  }
}
```

To fix this error, try the following:

- Request a [quota increase](#manage-quotas).
- Use [exponential backoff](#exponential-backoff) to retry the request.

### `userRateLimitExceeded` {#user-rate-limit}

This error occurs when a request reaches the per-user limit. The following JSON sample is a representation of this error:

```json
{
  "error": {
  "errors": [
    {
    "domain": "usageLimits",
    "reason": "userRateLimitExceeded",
    "message": "User Rate Limit Exceeded"
    }
  ],
  "code": 403,
  "message": "User Rate Limit Exceeded"
  }
}
```

To fix this error, try to optimize your application code to make fewer requests or use [exponential backoff](#exponential-backoff) to retry the request.

## 429 errors {#429-errors}

A 429 "Too many requests" error can occur due to daily per-user limits (including mail sending limits), bandwidth limits, or a per-user concurrent request limit. Information about each limit follows. However, each limit can be resolved either by [retrying failed requests](#exponential-backoff) or by splitting processing across multiple Gmail accounts.

You can't increase per-user limits. For more information about limits, see [Usage limits](https://developers.google.com/workspace/gmail/api/reference/quota).

### Mail sending limits {#mail-limits}

The Gmail API enforces the standard daily mail sending limits. These limits differ for paying Google Workspace users and trial gmail.com users. For these limits, refer to [Gmail sending limits in Google Workspace](https://support.google.com/a/answer/166852).

These limits are per-user and are shared by all of the user's clients, whether API clients, built-in or web clients, or SMTP MSA. If you exceed these limits, the API returns an HTTP 429 "Too many requests: User-rate limit exceeded (Mail sending)" error with a retry time. Exceeding daily limits might result in these errors for multiple hours before the server accepts the request.

The mail sending pipeline is complex: once the user exceeds their quota, there can be a delay of several minutes before the API begins returning 429 error responses. You can't assume that a 200 response means the email was successfully sent.

### Bandwidth limits {#bandwidth-limits}

The API has per-user upload and download [bandwidth limits](https://support.google.com/a/answer/1071518) that are equal to, but independent of, IMAP. These limits are shared across all Gmail API clients for a user.

Users typically only encounter these limits in exceptional or abusive situations. If you exceed these limits, the API returns an HTTP 429 "Too many requests: User-rate limit exceeded" error with a retry time. Exceeding daily limits might result in these errors for multiple hours before the server accepts the request.

### Concurrent requests {#concurrent-requests}

The Gmail API enforces a per-user concurrent request limit (in addition to the per-user *rate* limit). This limit is shared by all Gmail API clients accessing a user and ensures that no API client is overloading a Gmail user mailbox or their backend server.

Making many parallel requests for a single user or sending batches with a large number of requests can trigger this error. A large number of independent API clients accessing the Gmail user mailbox simultaneously can also trigger this error. If you exceed this limit, the API returns an HTTP 429 "Too many requests: Too many concurrent requests for user" error.

## 500, 502, 503, 504 errors {#5xx-errors}

These errors occur when an unexpected server error arises while processing the request. Various issues can cause these errors, including a request's timing overlapping with another request or a request for an unsupported action, such as attempting to update permissions for a single page in Google Sites instead of the entire site.

The following is a list of 5xx errors:

- 500 Backend error
- 502 Bad gateway
- 503 Service unavailable
- 504 Gateway timeout

### `backendError` {#backend-error}

This error occurs when an unexpected error arises while processing the request. The following JSON sample is a representation of this error:

```json
{
  "error": {
  "errors": [
    {
    "domain": "global",
    "reason": "backendError",
    "message": "Backend Error",
    }
  ],
  "code": 500,
  "message": "Backend Error"
  }
}
```

To fix this error, use [exponential backoff](#exponential-backoff) to retry the request.

## Retry failed requests to resolve errors {#exponential-backoff}

You can periodically retry a failed request over an increasing amount of time to handle errors related to rate limits, network volume, or response time. For example, you might retry a failed request after one second, then after two seconds, and then after four seconds. This method is called *exponential backoff*, and it's used to improve bandwidth usage and maximize throughput of requests in concurrent environments.

Start retry periods at least one second after the error.

## Manage quota limits {#manage-quotas}

To view or change usage limits for your project, or to request an increase to your quota, do the following:

1. If you don't already have a [billing account](https://cloud.google.com/billing/docs/how-to/manage-billing-account) for your project, then create one.
2. [Visit the Enabled APIs page of the API library](https://console.cloud.google.com/apis/enabled) in the API Console, and select an API from the list.
3. To view and change quota-related settings, select **Quotas**. To view usage statistics, select **Usage**.

For more information, see [View and manage quotas](https://docs.cloud.google.com/docs/quotas/view-manage).

## Batch requests {#batch}

Batch requests can improve performance, but larger batch sizes can trigger rate limiting. Don't send batches larger than 50 requests. For information on how to batch requests, refer to [Batch requests](https://developers.google.com/workspace/gmail/api/guides/batch).

## Related topics {#related}

- [Performance tips](https://developers.google.com/workspace/gmail/api/guides/performance)
- [Troubleshoot authentication and authorization issues](https://developers.google.com/workspace/gmail/api/troubleshoot-authentication-authorization)
