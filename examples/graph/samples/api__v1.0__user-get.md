---
canonical_url: https://learn.microsoft.com/en-us/graph/api/user-get?view=graph-rest-1.0
content_sha256: ba415c3da2343a617d3fc5cbcd4750d829caa08695867914c9d37ea102c530d3
converter: html-to-markdown/3.x
description: Retrieve the properties and relationships of user object.
etag: '"M49+/qZGpxCvM7Q+GxL/wgp/Oc0="'
extractor: profile:mslearn
fetched_at: '2026-10-28T13:58:38Z'
keywords: [add the sdk, attribute attribute, sdk documentation, authprovider instance, instance sdk, project and create, attribute assignments, attribute data]
last_modified: '2024-12-23T15:18:00Z'
locale: en-us
low_confidence: false
profile: mslearn
quality_flags: [uncrawled_internal]
quality_score: 1.0
render: http
source_url: https://learn.microsoft.com/en-us/graph/api/user-get?view=graph-rest-1.0
title: Get a user
version: v1.0
---

# Get a user {#get-a-user}

Namespace: microsoft.graph

Retrieve the properties and relationships of [user](../resources/v1.0/user.md) object.

This operation returns by default only a subset of the more commonly used properties for each user. These *default* properties are noted in the [Properties](../resources/v1.0/user.md#properties) section. To get properties that are *not* returned by default, do a [GET operation](https://learn.microsoft.com/en-us/graph/api/user-get?view=graph-rest-1.0) for the user and specify the properties in a `$select` OData query option. Because the **user** resource supports [extensions](../../extensibility-overview.md), you can also use the `GET` operation to get custom properties and extension data in a **user** instance.

Customers through Microsoft Entra ID for customers can also use this API operation to retrieve their details.

This API is available in the following [national cloud deployments](https://learn.microsoft.com/en-us/graph/deployments).

| Global service | US Government L4 | US Government L5 (DOD) | China operated by 21Vianet |
| -------------- | ---------------- | ---------------------- | -------------------------- |
| ✅              | ✅                | ✅                      | ✅                          |

## Permissions {#permissions}

Choose the permission or permissions marked as least privileged for this API. Use a higher privileged permission or permissions [only if your app requires it](https://learn.microsoft.com/en-us/graph/permissions-overview#best-practices-for-using-microsoft-graph-permissions). For details about delegated and application permissions, see [Permission types](https://learn.microsoft.com/en-us/graph/permissions-overview#permission-types). To learn more about these permissions, see the [permissions reference](https://learn.microsoft.com/en-us/graph/permissions-reference).

| Permission type                        | Least privileged permissions | Higher privileged permissions                                                                                      |
| -------------------------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Delegated (work or school account)     | User.Read                    | User.ReadWrite, User.ReadBasic.All, User.Read.All, User.ReadWrite.All, Directory.Read.All, Directory.ReadWrite.All |
| Delegated (personal Microsoft account) | User.Read                    | User.ReadWrite                                                                                                     |
| Application                            | User.Read.All                | User.ReadWrite.All, Directory.Read.All, Directory.ReadWrite.All                                                    |

> [!NOTE]
>
> The `User.Read` permission allows the app to read the profile, and discover relationships such as the group membership, reports, and manager of the signed-in user only.

### Permissions for specific scenarios {#permissions-for-specific-scenarios}

- To read the **employeeLeaveDateTime** property:
  - In delegated scenarios, the signed-in user needs at least one of the following Microsoft Entra roles: *Lifecycle Workflows Administrator* (least privilege), *Global Reader*; the app must be granted the *User-LifeCycleInfo.Read.All* delegated permission.
  - In app-only scenarios with Microsoft Graph permissions, the app must be granted the *User-LifeCycleInfo.Read.All* permission.
- To read the **customSecurityAttributes** property:
  - In delegated scenarios, the signed-in user must be assigned the *Attribute Assignment Administrator* role and the app granted the *CustomSecAttributeAssignment.Read.All* permission.
  - In app-only scenarios with Microsoft Graph permissions, the app must be granted the *CustomSecAttributeAssignment.Read.All* permission.
- *User-Mail.ReadWrite.All* is the least privileged permission to read and write the **otherMails** property; also allows to read some identifier-related properties on the user object.
- *User-PasswordProfile.ReadWrite.All* is the least privileged permission to read and write password reset-related properties; also allows to read some identifier-related properties on the user object.
- *User-Phone.ReadWrite.All* is the least privileged permission to read and write the **businessPhones** and **mobilePhone** properties; also allows to read some identifier-related properties on the user object.
- *User.EnableDisableAccount.All* + *User.Read.All* is the least privileged combination of permissions to read and write the **accountEnabled** property.

## HTTP request {#http-request}

For a specific user:

```http
GET /me
GET /users/{id | userPrincipalName}
```

> [!NOTE]
>
> Calling the `/me` endpoint requires a signed-in user and therefore a delegated permission. Application permissions aren't supported when using the `/me` endpoint.

> [!TIP]
>
> - When the **userPrincipalName** begins with a `$` character, the GET request URL syntax `/users/$x@y.com` fails with a `400 Bad Request` error code. The request fails because the URL violates the OData URL convention, which expects only system query options to be prefixed with a `$` character. Remove the slash (/) after `/users` and enclose the **userPrincipalName** in parentheses and single quotes, as follows: `/users('$x@y.com')`. For example, `/users('$AdeleVance@contoso.com')`.
> - To query a B2B user using the **userPrincipalName**, encode the hash (#) character. That is, replace the `#` symbol with `%23`. For example, `/users/AdeleVance_adatum.com%23EXT%23@contoso.com`.

For the signed-in user:

```http
GET /me
```

> [!NOTE]
>
> Calling the `/me` endpoint requires a signed-in user and therefore a delegated permission. Application permissions aren't supported when using the `/me` endpoint.

## Optional query parameters {#optional-query-parameters}

This method supports the `$select` [OData query parameter](../../query-parameters.md) to retrieve specific user properties, including those not returned by default.

By default, only a limited set of properties are returned (*businessPhones, displayName, givenName, id, jobTitle, mail, mobilePhone, officeLocation, preferredLanguage, surname, userPrincipalName*).

To return an alternative property set, you must specify the desired set of [user](../resources/v1.0/user.md) properties using the OData `$select` query parameter. For example, to return *displayName*, *givenName*, and *postalCode*, add the following expression to your query `$select=displayName,givenName,postalCode`.

Extension properties also support query parameters as follows:

| Extension type                     | Comments                                                                                                                                         |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| onPremisesExtensionAttributes 1-15 | Returned only with `$select`.                                                                                                                    |
| Schema extensions                  | Returned only with `$select`.                                                                                                                    |
| Open extensions                    | Returned only through the [Get open extension](https://learn.microsoft.com/en-us/graph/api/opentypeextension-get?view=graph-rest-1.0) operation. |
| Directory extensions               | Returned only with `$select`.                                                                                                                    |

## Request headers {#request-headers}

| Header        | Value                                                                                                                                      |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Authorization | Bearer {token}. Required. Learn more about [authentication and authorization](https://learn.microsoft.com/en-us/graph/auth/auth-concepts). |

## Request body {#request-body}

Don't supply a request body for this method.

## Response {#response}

If successful, this method returns a `200 OK` response code and [user](../resources/v1.0/user.md) object in the response body. It returns the default properties unless you use `$select` to specify specific properties. This method returns `202 Accepted` when the request has been processed successfully but the server requires more time to complete related background operations.

If a user with the ID doesn't exist, this method returns a `404 Not Found` error code.

## Examples {#examples}

### Example 1: Standard users request {#example-1-standard-users-request}

#### Request {#request}

By default, only a limited set of properties are returned ( *businessPhones, displayName, givenName, id, jobTitle, mail, mobilePhone, officeLocation, preferredLanguage, surname, userPrincipalName* ). This example illustrates the default request and response.

##### HTTP

```http
GET https://graph.microsoft.com/v1.0/users/87d349ed-44d7-43e1-9a83-5f2406dee5bd
```

##### C#

```csharp
// Code snippets are only available for the latest version. Current version is 5.x

// To initialize your graphClient, see https://learn.microsoft.com/en-us/graph/sdks/create-client?from=snippets&tabs=csharp
var result = await graphClient.Users["{user-id}"].GetAsync();
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### Go

```go

// Code snippets are only available for the latest major version. Current major version is $v1.*

// Dependencies
import (
	  "context"
	  msgraphsdk "github.com/microsoftgraph/msgraph-sdk-go"
	  //other-imports
)


// To initialize your graphClient, see https://learn.microsoft.com/en-us/graph/sdks/create-client?from=snippets&tabs=go
users, err := graphClient.Users().ByUserId("user-id").Get(context.Background(), nil)
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### Java

```java
// Code snippets are only available for the latest version. Current version is 6.x

GraphServiceClient graphClient = new GraphServiceClient(requestAdapter);

User result = graphClient.users().byUserId("{user-id}").get();
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### JavaScript

```javascript
const options = {
	authProvider,
};

const client = Client.init(options);

let user = await client.api('/users/87d349ed-44d7-43e1-9a83-5f2406dee5bd')
	.get();
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### PHP

```php
<?php
use Microsoft\Graph\GraphServiceClient;


$graphServiceClient = new GraphServiceClient($tokenRequestContext, $scopes);


$result = $graphServiceClient->users()->byUserId('user-id')->get()->wait();
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### PowerShell

```powershell
Import-Module Microsoft.Graph.Users

Get-MgUser -UserId $userId
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### Python

```python
# Code snippets are only available for the latest version. Current version is 1.x
from msgraph import GraphServiceClient
# To initialize your graph_client, see https://learn.microsoft.com/en-us/graph/sdks/create-client?from=snippets&tabs=python

result = await graph_client.users.by_user_id('user-id').get()
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

#### Response {#response-1}

```http
HTTP/1.1 200 OK
Content-type: application/json

{
  "businessPhones": [
       "+1 425 555 0109"
   ],
   "displayName": "Adele Vance",
   "givenName": "Adele",
   "jobTitle": "Retail Manager",
   "mail": "AdeleV@contoso.com",
   "mobilePhone": "+1 425 555 0109",
   "officeLocation": "18/2111",
   "preferredLanguage": "en-US",
   "surname": "Vance",
   "userPrincipalName": "AdeleV@contoso.com",
   "id": "87d349ed-44d7-43e1-9a83-5f2406dee5bd"
}
```

### Example 2: Signed-in user request {#example-2-signed-in-user-request}

You can get the user information for the signed-in user by replacing `/users/{id | userPrincipalName}` with `/me`.

#### Request {#request-1}

##### HTTP

```http
GET https://graph.microsoft.com/v1.0/me
```

##### C#

```csharp
// Code snippets are only available for the latest version. Current version is 5.x

// To initialize your graphClient, see https://learn.microsoft.com/en-us/graph/sdks/create-client?from=snippets&tabs=csharp
var result = await graphClient.Me.GetAsync();
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### Go

```go

// Code snippets are only available for the latest major version. Current major version is $v1.*

// Dependencies
import (
	  "context"
	  msgraphsdk "github.com/microsoftgraph/msgraph-sdk-go"
	  //other-imports
)


// To initialize your graphClient, see https://learn.microsoft.com/en-us/graph/sdks/create-client?from=snippets&tabs=go
me, err := graphClient.Me().Get(context.Background(), nil)
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### Java

```java
// Code snippets are only available for the latest version. Current version is 6.x

GraphServiceClient graphClient = new GraphServiceClient(requestAdapter);

User result = graphClient.me().get();
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### JavaScript

```javascript
const options = {
	authProvider,
};

const client = Client.init(options);

let user = await client.api('/me')
	.get();
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### PHP

```php
<?php
use Microsoft\Graph\GraphServiceClient;


$graphServiceClient = new GraphServiceClient($tokenRequestContext, $scopes);


$result = $graphServiceClient->me()->get()->wait();
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### PowerShell

```powershell
Import-Module Microsoft.Graph.Users

# A UPN can also be used as -UserId.
Get-MgUser -UserId $userId
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### Python

```python
# Code snippets are only available for the latest version. Current version is 1.x
from msgraph import GraphServiceClient
# To initialize your graph_client, see https://learn.microsoft.com/en-us/graph/sdks/create-client?from=snippets&tabs=python

result = await graph_client.me.get()
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

#### Response {#response-2}

```http
HTTP/1.1 200 OK
Content-type: application/json

{
  "businessPhones": [
       "+1 425 555 0109"
   ],
   "displayName": "Adele Vance",
   "givenName": "Adele",
   "jobTitle": "Retail Manager",
   "mail": "AdeleV@contoso.com",
   "mobilePhone": "+1 425 555 0109",
   "officeLocation": "18/2111",
   "preferredLanguage": "en-US",
   "surname": "Vance",
   "userPrincipalName": "AdeleV@contoso.com",
   "id": "87d349ed-44d7-43e1-9a83-5f2406dee5bd"
}
```

### Example 3: Use $select to retrieve specific properties of a user {#example-3-use-select-to-retrieve-specific-properties-of-a-user}

To retrieve specific properties, use the OData `$select` query parameter. For example, to return *displayName*, *givenName*, *postalCode*, and *identities*, add the following query expression to your query `$select=displayName,givenName,postalCode,identities`

#### Request {#request-2}

##### HTTP

```http
GET https://graph.microsoft.com/v1.0/users/87d349ed-44d7-43e1-9a83-5f2406dee5bd?$select=displayName,givenName,postalCode,identities
```

##### C#

```csharp
// Code snippets are only available for the latest version. Current version is 5.x

// To initialize your graphClient, see https://learn.microsoft.com/en-us/graph/sdks/create-client?from=snippets&tabs=csharp
var result = await graphClient.Users["{user-id}"].GetAsync((requestConfiguration) =>
{
	requestConfiguration.QueryParameters.Select = new string []{ "displayName","givenName","postalCode","identities" };
});
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### Go

```go

// Code snippets are only available for the latest major version. Current major version is $v1.*

// Dependencies
import (
	  "context"
	  msgraphsdk "github.com/microsoftgraph/msgraph-sdk-go"
	  graphusers "github.com/microsoftgraph/msgraph-sdk-go/users"
	  //other-imports
)

requestParameters := &graphusers.UserItemRequestBuilderGetQueryParameters{
	Select: [] string {"displayName","givenName","postalCode","identities"},
}
configuration := &graphusers.UserItemRequestBuilderGetRequestConfiguration{
	QueryParameters: requestParameters,
}

// To initialize your graphClient, see https://learn.microsoft.com/en-us/graph/sdks/create-client?from=snippets&tabs=go
users, err := graphClient.Users().ByUserId("user-id").Get(context.Background(), configuration)
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### Java

```java
// Code snippets are only available for the latest version. Current version is 6.x

GraphServiceClient graphClient = new GraphServiceClient(requestAdapter);

User result = graphClient.users().byUserId("{user-id}").get(requestConfiguration -> {
	requestConfiguration.queryParameters.select = new String []{"displayName", "givenName", "postalCode", "identities"};
});
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### JavaScript

```javascript
const options = {
	authProvider,
};

const client = Client.init(options);

let user = await client.api('/users/87d349ed-44d7-43e1-9a83-5f2406dee5bd')
	.select('displayName,givenName,postalCode,identities')
	.get();
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### PHP

```php
<?php
use Microsoft\Graph\GraphServiceClient;
use Microsoft\Graph\Generated\Users\Item\UserItemRequestBuilderGetRequestConfiguration;


$graphServiceClient = new GraphServiceClient($tokenRequestContext, $scopes);

$requestConfiguration = new UserItemRequestBuilderGetRequestConfiguration();
$queryParameters = UserItemRequestBuilderGetRequestConfiguration::createQueryParameters();
$queryParameters->select = ["displayName","givenName","postalCode","identities"];
$requestConfiguration->queryParameters = $queryParameters;


$result = $graphServiceClient->users()->byUserId('user-id')->get($requestConfiguration)->wait();
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### PowerShell

```powershell
Import-Module Microsoft.Graph.Users

Get-MgUser -UserId $userId -Property "displayName,givenName,postalCode,identities" 
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### Python

```python
# Code snippets are only available for the latest version. Current version is 1.x
from msgraph import GraphServiceClient
from msgraph.generated.users.item.user_item_request_builder import UserItemRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
# To initialize your graph_client, see https://learn.microsoft.com/en-us/graph/sdks/create-client?from=snippets&tabs=python
query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
		select = ["displayName","givenName","postalCode","identities"],
)

request_configuration = RequestConfiguration(
query_parameters = query_params,
)

result = await graph_client.users.by_user_id('user-id').get(request_configuration = request_configuration)
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

#### Response {#response-3}

```http
HTTP/1.1 200 OK
Content-type: application/json

{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users(displayName,givenName,postalCode,identities)/$entity",
    "displayName": "Adele Vance",
    "givenName": "Adele",
    "postalCode": "98004",
    "identities": [
        {
            "signInType": "userPrincipalName",
            "issuer": "contoso.com",
            "issuerAssignedId": "AdeleV@contoso.com"
        }
    ]
}
```

### Example 4: Get the value of a schema extension for a user {#example-4-get-the-value-of-a-schema-extension-for-a-user}

In this example, the ID of the schema extension is `ext55gb1l09_msLearnCourses`.

#### Request {#request-3}

##### HTTP

```http
GET https://graph.microsoft.com/v1.0/users/4562bcc8-c436-4f95-b7c0-4f8ce89dca5e?$select=ext55gb1l09_msLearnCourses
```

##### C#

```csharp
// Code snippets are only available for the latest version. Current version is 5.x

// To initialize your graphClient, see https://learn.microsoft.com/en-us/graph/sdks/create-client?from=snippets&tabs=csharp
var result = await graphClient.Users["{user-id}"].GetAsync((requestConfiguration) =>
{
	requestConfiguration.QueryParameters.Select = new string []{ "ext55gb1l09_msLearnCourses" };
});
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### Go

```go

// Code snippets are only available for the latest major version. Current major version is $v1.*

// Dependencies
import (
	  "context"
	  msgraphsdk "github.com/microsoftgraph/msgraph-sdk-go"
	  graphusers "github.com/microsoftgraph/msgraph-sdk-go/users"
	  //other-imports
)

requestParameters := &graphusers.UserItemRequestBuilderGetQueryParameters{
	Select: [] string {"ext55gb1l09_msLearnCourses"},
}
configuration := &graphusers.UserItemRequestBuilderGetRequestConfiguration{
	QueryParameters: requestParameters,
}

// To initialize your graphClient, see https://learn.microsoft.com/en-us/graph/sdks/create-client?from=snippets&tabs=go
users, err := graphClient.Users().ByUserId("user-id").Get(context.Background(), configuration)
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### Java

```java
// Code snippets are only available for the latest version. Current version is 6.x

GraphServiceClient graphClient = new GraphServiceClient(requestAdapter);

User result = graphClient.users().byUserId("{user-id}").get(requestConfiguration -> {
	requestConfiguration.queryParameters.select = new String []{"ext55gb1l09_msLearnCourses"};
});
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### JavaScript

```javascript
const options = {
	authProvider,
};

const client = Client.init(options);

let user = await client.api('/users/4562bcc8-c436-4f95-b7c0-4f8ce89dca5e')
	.select('ext55gb1l09_msLearnCourses')
	.get();
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### PHP

```php
<?php
use Microsoft\Graph\GraphServiceClient;
use Microsoft\Graph\Generated\Users\Item\UserItemRequestBuilderGetRequestConfiguration;


$graphServiceClient = new GraphServiceClient($tokenRequestContext, $scopes);

$requestConfiguration = new UserItemRequestBuilderGetRequestConfiguration();
$queryParameters = UserItemRequestBuilderGetRequestConfiguration::createQueryParameters();
$queryParameters->select = ["ext55gb1l09_msLearnCourses"];
$requestConfiguration->queryParameters = $queryParameters;


$result = $graphServiceClient->users()->byUserId('user-id')->get($requestConfiguration)->wait();
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### PowerShell

```powershell
Import-Module Microsoft.Graph.Users

Get-MgUser -UserId $userId -Property "ext55gb1l09_msLearnCourses" 
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### Python

```python
# Code snippets are only available for the latest version. Current version is 1.x
from msgraph import GraphServiceClient
from msgraph.generated.users.item.user_item_request_builder import UserItemRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
# To initialize your graph_client, see https://learn.microsoft.com/en-us/graph/sdks/create-client?from=snippets&tabs=python
query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
		select = ["ext55gb1l09_msLearnCourses"],
)

request_configuration = RequestConfiguration(
query_parameters = query_params,
)

result = await graph_client.users.by_user_id('user-id').get(request_configuration = request_configuration)
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

#### Response {#response-4}

```http
HTTP/1.1 200 OK
Content-type: application/json

{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users(ext55gb1l09_msLearnCourses)/$entity",
    "ext55gb1l09_msLearnCourses": {
        "@odata.type": "#microsoft.graph.ComplexExtensionValue",
        "courseType": "Developer",
        "courseName": "Introduction to Microsoft Graph",
        "courseId": 1
    }
}
```

### Example 5: Get the custom security attribute assignments for a user {#example-5-get-the-custom-security-attribute-assignments-for-a-user}

The following example shows how to get the custom security attribute assignments for a user.

Attribute #1

- Attribute set: `Engineering`
- Attribute: `Project`
- Attribute data type: Collection of Strings
- Attribute value: `["Baker","Cascade"]`

Attribute #2

- Attribute set: `Engineering`
- Attribute: `CostCenter`
- Attribute data type: Collection of Integers
- Attribute value: `[1001]`

Attribute #3

- Attribute set: `Engineering`
- Attribute: `Certification`
- Attribute data type: Boolean
- Attribute value: `true`

Attribute #4

- Attribute set: `Marketing`
- Attribute: `EmployeeId`
- Attribute data type: String
- Attribute value: `"QN26904"`

To get custom security attribute assignments, the calling principal must be assigned the Attribute Assignment Reader or Attribute Assignment Administrator role and must be granted the *CustomSecAttributeAssignment.Read.All* or *CustomSecAttributeAssignment.ReadWrite.All* permission.

For more examples of custom security attribute assignments, see [Examples: Assign, update, list, or remove custom security attribute assignments using the Microsoft Graph API](https://learn.microsoft.com/en-us/graph/custom-security-attributes-examples).

#### Request {#request-4}

##### HTTP

```http
GET https://graph.microsoft.com/v1.0/users/{id}?$select=customSecurityAttributes
```

##### C#

```csharp
// Code snippets are only available for the latest version. Current version is 5.x

// To initialize your graphClient, see https://learn.microsoft.com/en-us/graph/sdks/create-client?from=snippets&tabs=csharp
var result = await graphClient.Users["{user-id}"].GetAsync((requestConfiguration) =>
{
	requestConfiguration.QueryParameters.Select = new string []{ "customSecurityAttributes" };
});
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### Go

```go

// Code snippets are only available for the latest major version. Current major version is $v1.*

// Dependencies
import (
	  "context"
	  msgraphsdk "github.com/microsoftgraph/msgraph-sdk-go"
	  graphusers "github.com/microsoftgraph/msgraph-sdk-go/users"
	  //other-imports
)

requestParameters := &graphusers.UserItemRequestBuilderGetQueryParameters{
	Select: [] string {"customSecurityAttributes"},
}
configuration := &graphusers.UserItemRequestBuilderGetRequestConfiguration{
	QueryParameters: requestParameters,
}

// To initialize your graphClient, see https://learn.microsoft.com/en-us/graph/sdks/create-client?from=snippets&tabs=go
users, err := graphClient.Users().ByUserId("user-id").Get(context.Background(), configuration)
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### Java

```java
// Code snippets are only available for the latest version. Current version is 6.x

GraphServiceClient graphClient = new GraphServiceClient(requestAdapter);

User result = graphClient.users().byUserId("{user-id}").get(requestConfiguration -> {
	requestConfiguration.queryParameters.select = new String []{"customSecurityAttributes"};
});
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### JavaScript

```javascript
const options = {
	authProvider,
};

const client = Client.init(options);

let user = await client.api('/users/{id}')
	.select('customSecurityAttributes')
	.get();
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### PHP

```php
<?php
use Microsoft\Graph\GraphServiceClient;
use Microsoft\Graph\Generated\Users\Item\UserItemRequestBuilderGetRequestConfiguration;


$graphServiceClient = new GraphServiceClient($tokenRequestContext, $scopes);

$requestConfiguration = new UserItemRequestBuilderGetRequestConfiguration();
$queryParameters = UserItemRequestBuilderGetRequestConfiguration::createQueryParameters();
$queryParameters->select = ["customSecurityAttributes"];
$requestConfiguration->queryParameters = $queryParameters;


$result = $graphServiceClient->users()->byUserId('user-id')->get($requestConfiguration)->wait();
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### PowerShell

```powershell
Import-Module Microsoft.Graph.Users

Get-MgUser -UserId $userId -Property "customSecurityAttributes" 
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

##### Python

```python
# Code snippets are only available for the latest version. Current version is 1.x
from msgraph import GraphServiceClient
from msgraph.generated.users.item.user_item_request_builder import UserItemRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
# To initialize your graph_client, see https://learn.microsoft.com/en-us/graph/sdks/create-client?from=snippets&tabs=python
query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
		select = ["customSecurityAttributes"],
)

request_configuration = RequestConfiguration(
query_parameters = query_params,
)

result = await graph_client.users.by_user_id('user-id').get(request_configuration = request_configuration)
```

> For details about how to [add the SDK](https://learn.microsoft.com/en-us/graph/sdks/sdk-installation) to your project and [create an authProvider](../../sdks/choose-authentication-providers.md) instance, see the [SDK documentation](https://learn.microsoft.com/en-us/graph/sdks/sdks-overview).

#### Response {#response-5}

```http
HTTP/1.1 200 OK
Content-type: application/json

{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users(customSecurityAttributes)/$entity",
    "customSecurityAttributes": {
        "Marketing": {
            "@odata.type": "#microsoft.graph.customSecurityAttributeValue",
            "EmployeeId": "QN26904"
        },
        "Engineering": {
            "@odata.type": "#microsoft.graph.customSecurityAttributeValue",
            "Project@odata.type": "#Collection(String)",
            "Project": [
                "Baker",
                "Cascade"
            ],
            "CostCenter@odata.type": "#Collection(Int32)",
            "CostCenter": [
                1001
            ],
            "Certification": true
        }
    }
}
```

If there are no custom security attributes assigned to the user or if the calling principal doesn't have access, the following block shows the response:

```http
HTTP/1.1 200 OK
Content-type: application/json

{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users(customSecurityAttributes)/$entity",
    "customSecurityAttributes": null
}
```

---

## Feedback {#ms--feedback}

Was this page helpful?
