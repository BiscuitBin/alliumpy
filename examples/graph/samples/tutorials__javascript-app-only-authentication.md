---
canonical_url: https://learn.microsoft.com/en-us/graph/tutorials/javascript-app-only-authentication
content_sha256: b8690ae921a0a29af61f0066eaebbf7fe863337b67f759e86a6e222fe4fa9902
converter: html-to-markdown/3.x
description: Learn how to add app-only authentication to JavaScript apps to call Microsoft Graph
etag: '"56Cg1zW2/fnoJ42fuXMTxAI3Mec="'
extractor: profile:mslearn
fetched_at: '2026-10-28T13:59:47Z'
keywords: [clientsecretcredential, build javascript apps, graph, undefined, index.js, settings, add app-only authentication, azure identity client]
last_modified: '2025-06-11T19:27:00Z'
locale: en-us
low_confidence: false
profile: mslearn
quality_flags: [uncrawled_internal]
quality_score: 1.0
render: http
sitemap_lastmod: '2025-06-11'
source_url: https://learn.microsoft.com/en-us/graph/tutorials/javascript-app-only-authentication
title: Add app-only authentication to JavaScript apps for Microsoft Graph
version: v1.0
---

# Add app-only authentication to JavaScript apps for Microsoft Graph {#add-app-only-authentication-to-javascript-apps-for-microsoft-graph}

In this article, you add app-only authentication to the application you created in [Build JavaScript apps with Microsoft Graph and app-only authentication](https://learn.microsoft.com/en-us/graph/tutorials/javascript-app-only).

The [Azure Identity client library for JavaScript](https://www.npmjs.com/package/@azure/identity) provides many `TokenCredential` classes that implement OAuth2 token flows. The [Microsoft Graph JavaScript client library](https://www.npmjs.com/package/@microsoft/microsoft-graph-client) uses those classes to authenticate calls to Microsoft Graph.

## Configure Graph client for app-only authentication {#configure-graph-client-for-app-only-authentication}

In this section, you use the `ClientSecretCredential` class to request an access token by using the [client credentials flow](https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-client-creds-grant-flow).

1. Open **graphHelper.js** and add the following code.

   ```javascript
   import 'isomorphic-fetch';
   import { ClientSecretCredential } from '@azure/identity';
   import { Client } from '@microsoft/microsoft-graph-client';
   // prettier-ignore
   import { TokenCredentialAuthenticationProvider } from
     '@microsoft/microsoft-graph-client/authProviders/azureTokenCredentials/index.js';

   let _settings = undefined;
   let _clientSecretCredential = undefined;
   let _appClient = undefined;

   export function initializeGraphForAppOnlyAuth(settings) {
     // Ensure settings isn't null
     if (!settings) {
       throw new Error('Settings cannot be undefined');
     }

     _settings = settings;

     // Ensure settings isn't null
     if (!_settings) {
       throw new Error('Settings cannot be undefined');
     }

     if (!_clientSecretCredential) {
       _clientSecretCredential = new ClientSecretCredential(
         _settings.tenantId,
         _settings.clientId,
         _settings.clientSecret,
       );
     }

     if (!_appClient) {
       const authProvider = new TokenCredentialAuthenticationProvider(
         _clientSecretCredential,
         {
           scopes: ['https://graph.microsoft.com/.default'],
         },
       );

       _appClient = Client.initWithMiddleware({
         authProvider: authProvider,
       });
     }
   }
   ```

2. Replace the empty `initializeGraph` function in **index.js** with the following.

   ```javascript
   function initializeGraph(settings) {
     initializeGraphForAppOnlyAuth(settings);
   }
   ```

This code declares two private properties, a `ClientSecretCredential` object and a `Client` object. The `InitializeGraphForAppOnlyAuth` function creates a new instance of `ClientSecretCredential`, then uses that instance to create a new instance of `Client`. Every time an API call is made to Microsoft Graph through the `_appClient`, it uses the provided credential to get an access token.

## Test the ClientSecretCredential {#test-the-clientsecretcredential}

Next, add code to get an access token from the `ClientSecretCredential`.

1. Add the following function to **graphHelper.js**.

   ```javascript
   export async function getAppOnlyTokenAsync() {
     // Ensure credential isn't undefined
     if (!_clientSecretCredential) {
       throw new Error('Graph has not been initialized for app-only auth');
     }

     // Request token with given scopes
     const response = await _clientSecretCredential.getToken([
       'https://graph.microsoft.com/.default',
     ]);
     return response.token;
   }
   ```

2. Replace the empty `displayAccessTokenAsync` function in **index.js** with the following.

   ```javascript
   async function displayAccessTokenAsync() {
     try {
       const appOnlyToken = await getAppOnlyTokenAsync();
       console.log(`App-only token: ${appOnlyToken}`);
     } catch (err) {
       console.log(`Error getting app-only access token: ${err}`);
     }
   }
   ```

3. Run the following command in your CLI in the root of your project.

   ```bash
   node index.js
   ```

4. Enter `1` when prompted for an option. The application displays an access token.

   ```bash
   JavaScript Graph App-Only Tutorial

   [1] Display access token
   [2] List users
   [3] Make a Graph call
   [0] Exit

   Select an option [1...3 / 0]: 1
   App-only token: eyJ0eXAiOiJKV1QiLCJub25jZSI6IlVDTzRYOWtKYlNLVjVkRzJGenJqd2xvVUcwWS...
   ```

   > [!TIP]
   >
   > For validation and debugging purposes *only*, you can decode app-only access tokens using Microsoft's online token parser at [https://jwt.ms](https://jwt.ms). Parsing your token can be useful if you encounter token errors when calling Microsoft Graph. For example, verifying that the `role` claim in the token contains the expected Microsoft Graph permission scopes.

## Next step {#next-step}

[Get users](https://learn.microsoft.com/en-us/graph/tutorials/javascript-app-only-get-users)

---

## Feedback {#ms--feedback}

Was this page helpful?
