---
canonical_url: https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0
content_sha256: d51ae2a7c8d029ce58a46e7a2fdbc17fb8b92a38133744e7b62387140c16094a
converter: html-to-markdown/3.x
description: Item is the main data model in the OneDrive API. Everything is an item.
etag: '"3qnHb1RNvCm8U1F3Tghk0M5SpWY="'
extractor: profile:mslearn
fetched_at: '2026-10-28T13:58:44Z'
keywords: [item, read-only, file, collection, retention label, url, folder, string]
last_modified: '2024-06-28T08:00:00Z'
locale: en-us
low_confidence: false
profile: mslearn
quality_flags: [uncrawled_internal]
quality_score: 1.0
render: http
source_url: https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0
title: driveItem resource type
version: v1.0
---

# driveItem resource type {#driveitem-resource-type}

Namespace: microsoft.graph

The **driveItem** resource represents a file, folder, or other item stored in a drive.

All file system objects in OneDrive and SharePoint are returned as **driveItem** resources. Items in SharePoint document libraries can be represented as [listItem](https://learn.microsoft.com/en-us/graph/api/resources/listitem?view=graph-rest-1.0) or **driveItem** resources.

There are two primary ways of addressing a **driveItem** resource:

- By the **driveItem** unique identifier using `drive/items/{item-id}`
- By file system path using `/drive/root:/path/to/file`

For more information, see [addressing driveItems](https://learn.microsoft.com/en-us/graph/onedrive-addressing-driveitems).

**driveItem** resources have facets modeled as properties that provide data about the driveItem's identities and capabilities. For example:

- Folders have a [**folder facet**](https://learn.microsoft.com/en-us/graph/api/resources/folder?view=graph-rest-1.0)
- Files have a [**file facet**](https://learn.microsoft.com/en-us/graph/api/resources/file?view=graph-rest-1.0).
- Images have an [**image facet**](https://learn.microsoft.com/en-us/graph/api/resources/image?view=graph-rest-1.0) in addition to their file facet.
- Images taken with a camera (photos) have a [**photo facet**](https://learn.microsoft.com/en-us/graph/api/resources/photo?view=graph-rest-1.0) that identifies the item as a photo and provides the properties of when the photo was taken and with what device.

Items with the **folder** facet act as containers of items and therefore have a `children` reference pointing to a collection of **driveItems** under the folder.

> **Note:** In OneDrive for Business or SharePoint document libraries, the **cTag** property isn't returned, if the **driveItem** has a [folder](https://learn.microsoft.com/en-us/graph/api/resources/folder?view=graph-rest-1.0) facet.

## Methods {#methods}

| Method                                                                                                                               | Return Type                                                                                                                                | Description                                                                                                                                                                                              |
| ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Get item](https://learn.microsoft.com/en-us/graph/api/driveitem-get?view=graph-rest-1.0)                                            | [driveItem](https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0)                                           | Retrieve the metadata for a **driveItem** in a drive.                                                                                                                                                    |
| [Get analytics](https://learn.microsoft.com/en-us/graph/api/itemanalytics-get?view=graph-rest-1.0)                                   | [itemAnalytics](https://learn.microsoft.com/en-us/graph/api/resources/itemanalytics?view=graph-rest-1.0)                                   | Get analytics for this resource.                                                                                                                                                                         |
| [Get activities by interval](https://learn.microsoft.com/en-us/graph/api/itemactivitystat-getactivitybyinterval?view=graph-rest-1.0) | [itemActivityStat](https://learn.microsoft.com/en-us/graph/api/resources/itemactivitystat?view=graph-rest-1.0)                             | Get a collection of **itemActivityStats** within the specified time interval.                                                                                                                            |
| [Get recent activities](https://learn.microsoft.com/en-us/graph/api/itemactivity-list?view=graph-rest-1.0)                           | [itemActivity](https://learn.microsoft.com/en-us/graph/api/resources/itemactivity?view=graph-rest-1.0) collection                          | List the recent [activities](https://learn.microsoft.com/en-us/graph/api/resources/itemactivity?view=graph-rest-1.0) that took place on a [drive](https://learn.microsoft.com/en-us/graph/api/resources/drive?view=graph-rest-1.0), [list](https://learn.microsoft.com/en-us/graph/api/resources/list?view=graph-rest-1.0), item, or within an item hierarchy. |
| [List children](../../v1.0/driveitem-list-children.md)                             | [driveItem](https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0) collection                                | Return a collection of **driveItems** in the children relationship of a **driveItem**.                                                                                                                   |
| [List versions](https://learn.microsoft.com/en-us/graph/api/driveitem-list-versions?view=graph-rest-1.0)                             | [driveItemVersion](https://learn.microsoft.com/en-us/graph/api/resources/driveitemversion?view=graph-rest-1.0) collection                  | Retrieve the versions of a file in the current user's drive.                                                                                                                                             |
| [Create folder](https://learn.microsoft.com/en-us/graph/api/driveitem-post-children?view=graph-rest-1.0)                             | [driveItem](https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0)                                           | Create a **driveItem** in the specified drive.                                                                                                                                                           |
| [Update item](https://learn.microsoft.com/en-us/graph/api/driveitem-update?view=graph-rest-1.0)                                      | [driveItem](https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0)                                           | Update a **driveItem** in the drive.                                                                                                                                                                     |
| [Upload](https://learn.microsoft.com/en-us/graph/api/driveitem-put-content?view=graph-rest-1.0)                                      | [driveItem](https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0)                                           | Upload content to the **driveItem**.                                                                                                                                                                     |
| [Download file](https://learn.microsoft.com/en-us/graph/api/driveitem-get-content?view=graph-rest-1.0)                               | download Url                                                                                                                               | Download content of a **driveItem**.                                                                                                                                                                     |
| [Download specific file format](https://learn.microsoft.com/en-us/graph/api/driveitem-get-content-format?view=graph-rest-1.0)        | download Url                                                                                                                               | Download content of a **driveItem** with a specific format.                                                                                                                                              |
| [Delete item](https://learn.microsoft.com/en-us/graph/api/driveitem-delete?view=graph-rest-1.0)                                      | None                                                                                                                                       | Delete a **driveItem**.                                                                                                                                                                                  |
| [Restore item](https://learn.microsoft.com/en-us/graph/api/driveitem-restore?view=graph-rest-1.0)                                    | [driveItem](https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0)                                           | Restore a deleted [driveItem](https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0) that is currently in the [recycle bin](https://learn.microsoft.com/en-us/graph/api/resources/recyclebin?view=graph-rest-1.0). |
| [Permanently delete item](https://learn.microsoft.com/en-us/graph/api/driveitem-permanentdelete?view=graph-rest-1.0)                 | None                                                                                                                                       | Permanently delete a **driveItem** by using its ID.                                                                                                                                                      |
| [Move item](https://learn.microsoft.com/en-us/graph/api/driveitem-move?view=graph-rest-1.0)                                          | [driveItem](https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0)                                           | Move a **driveItem** to a new parent item.                                                                                                                                                               |
| [Copy item](https://learn.microsoft.com/en-us/graph/api/driveitem-copy?view=graph-rest-1.0)                                          | details about how to [monitor the progress](https://learn.microsoft.com/en-us/graph/long-running-actions-overview) of the copy             | Create a copy of a **driveItem** (including any children).                                                                                                                                               |
| [Search items](https://learn.microsoft.com/en-us/graph/api/driveitem-search?view=graph-rest-1.0)                                     | [driveItem](https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0) collection                                | Search the hierarchy of items for items matching a query.                                                                                                                                                |
| [Track changes](https://learn.microsoft.com/en-us/graph/api/driveitem-delta?view=graph-rest-1.0)                                     | delta link                                                                                                                                 | List any changes in the drive.                                                                                                                                                                           |
| [Follow item](https://learn.microsoft.com/en-us/graph/api/driveitem-follow?view=graph-rest-1.0)                                      | [driveItem](https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0)                                           | Follow a **driveItem**.                                                                                                                                                                                  |
| [Unfollow item](https://learn.microsoft.com/en-us/graph/api/driveitem-unfollow?view=graph-rest-1.0)                                  | None                                                                                                                                       | Unfollow a **driveItem**.                                                                                                                                                                                |
| [Get thumbnails](https://learn.microsoft.com/en-us/graph/api/driveitem-list-thumbnails?view=graph-rest-1.0)                          | [driveItem](https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0) collection                                | List **driveItems** with their thumbnails.                                                                                                                                                               |
| [Create sharing link](https://learn.microsoft.com/en-us/graph/api/driveitem-createlink?view=graph-rest-1.0)                          | sharing link                                                                                                                               | Create a link to share the **driveItem**.                                                                                                                                                                |
| [Add permissions](https://learn.microsoft.com/en-us/graph/api/driveitem-invite?view=graph-rest-1.0)                                  | [permission](https://learn.microsoft.com/en-us/graph/api/resources/permission?view=graph-rest-1.0) collection                              | Send a sharing invite to a user.                                                                                                                                                                         |
| [List permissions](https://learn.microsoft.com/en-us/graph/api/driveitem-list-permissions?view=graph-rest-1.0)                       | [permission](https://learn.microsoft.com/en-us/graph/api/resources/permission?view=graph-rest-1.0) collection                              | Retrieve the collection of permissions on an **driveItem**.                                                                                                                                              |
| [Create permission](https://learn.microsoft.com/en-us/graph/api/driveitem-post-permissions?view=graph-rest-1.0)                      | [permission](https://learn.microsoft.com/en-us/graph/api/resources/permission?view=graph-rest-1.0)                                         | Create a new [permission](https://learn.microsoft.com/en-us/graph/api/resources/permission?view=graph-rest-1.0) object on a [driveItem](https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0). |
| [Delete permission](https://learn.microsoft.com/en-us/graph/api/permission-delete?view=graph-rest-1.0)                               | None                                                                                                                                       | Remove the permission from the **driveItem**.                                                                                                                                                            |
| [Revoke grants on sharing link](https://learn.microsoft.com/en-us/graph/api/permission-revokegrants?view=graph-rest-1.0)             | [permission](https://learn.microsoft.com/en-us/graph/api/resources/permission?view=graph-rest-1.0)                                         | Revoke access to a [listItem](https://learn.microsoft.com/en-us/graph/api/resources/listitem?view=graph-rest-1.0) or [driveItem](https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0) granted via a sharing link by removing the specified [driveRecipient](https://learn.microsoft.com/en-us/graph/api/resources/driverecipient?view=graph-rest-1.0) entries from the link. |
| [Get WebSocket channel](https://learn.microsoft.com/en-us/graph/api/subscriptions-socketio?view=graph-rest-1.0)                      | [subscription](https://learn.microsoft.com/en-us/graph/api/resources/subscription?view=graph-rest-1.0)                                     | Receive near-real-time change notifications for a drive using socket.io.                                                                                                                                 |
| [Preview item](https://learn.microsoft.com/en-us/graph/api/driveitem-preview?view=graph-rest-1.0)                                    | json object                                                                                                                                | Obtain short-lived embeddable URLs for an item in order to render a temporary preview.                                                                                                                   |
| [Check in files](https://learn.microsoft.com/en-us/graph/api/driveitem-checkin?view=graph-rest-1.0)                                  | None                                                                                                                                       | Check in a checked out **driveItem** resource, which makes the version of the document available to others.                                                                                              |
| [Check out files](https://learn.microsoft.com/en-us/graph/api/driveitem-checkout?view=graph-rest-1.0)                                | None                                                                                                                                       | Check out a **driveItem** resource to prevent others from editing the document, and prevent your changes from being visible until the documented is [checked in](https://learn.microsoft.com/en-us/graph/api/driveitem-checkin?view=graph-rest-1.0). |
| [Discard checkout](https://learn.microsoft.com/en-us/graph/api/driveitem-discardcheckout?view=graph-rest-1.0)                        | None                                                                                                                                       | Discard a previously [checked out](https://learn.microsoft.com/en-us/graph/api/driveitem-checkout?view=graph-rest-1.0) **driveItem**.                                                                    |
| [Extract sensitivity labels](https://learn.microsoft.com/en-us/graph/api/driveitem-extractsensitivitylabels?view=graph-rest-1.0)     | [extractSensitivityLabelsResult](https://learn.microsoft.com/en-us/graph/api/resources/extractsensitivitylabelsresult?view=graph-rest-1.0) | Extract one or more sensitivity labels assigned to a drive item and update the metadata of a drive item with the latest details of the assigned label.                                                   |
| [Assign sensitivity label](https://learn.microsoft.com/en-us/graph/api/driveitem-assignsensitivitylabel?view=graph-rest-1.0)         | String                                                                                                                                     | Asynchronously assign a sensitivity label to a **driveItem**.                                                                                                                                            |
| [Get retention label](https://learn.microsoft.com/en-us/graph/api/driveitem-getretentionlabel?view=graph-rest-1.0)                   | [itemRetentionLabel](https://learn.microsoft.com/en-us/graph/api/resources/itemretentionlabel?view=graph-rest-1.0)                         | Get metadata information for a retention label applied on a **driveItem**.                                                                                                                               |
| [Set retention label](https://learn.microsoft.com/en-us/graph/api/driveitem-setretentionlabel?view=graph-rest-1.0)                   | [itemRetentionLabel](https://learn.microsoft.com/en-us/graph/api/resources/itemretentionlabel?view=graph-rest-1.0)                         | Apply (set) a retention label on a **driveItem** (files and folders).                                                                                                                                    |
| [Remove retention label](https://learn.microsoft.com/en-us/graph/api/driveitem-removeretentionlabel?view=graph-rest-1.0)             | None                                                                                                                                       | Remove a retention label from a **driveItem**.                                                                                                                                                           |
| [Lock or unlock record](https://learn.microsoft.com/en-us/graph/api/driveitem-lockorunlockrecord?view=graph-rest-1.0)                | [itemRetentionLabel](https://learn.microsoft.com/en-us/graph/api/resources/itemretentionlabel?view=graph-rest-1.0)                         | Lock or unlock a retention label on a **driveItem** that classifies content as records.                                                                                                                  |
| [Create upload session](https://learn.microsoft.com/en-us/graph/api/driveitem-createuploadsession?view=graph-rest-1.0)               | [uploadSession](https://learn.microsoft.com/en-us/graph/api/resources/uploadsession?view=graph-rest-1.0)                                   | Create an upload session to allow your app to upload files up to the maximum file size.                                                                                                                  |

## Properties {#properties}

| Property             | Type                                                                                                             | Description                                                                                                                                                             |
| -------------------- | ---------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| audio                | [audio](https://learn.microsoft.com/en-us/graph/api/resources/audio?view=graph-rest-1.0)                         | Audio metadata, if the item is an audio file. Read-only. Read-only. Only on OneDrive Personal.                                                                          |
| bundle               | [bundle](https://learn.microsoft.com/en-us/graph/api/resources/bundle?view=graph-rest-1.0)                       | Bundle metadata, if the item is a bundle. Read-only.                                                                                                                    |
| content              | Stream                                                                                                           | The content stream, if the item represents a file.                                                                                                                      |
| createdBy            | [identitySet](identityset.md)             | Identity of the user, device, and application that created the item. Read-only.                                                                                         |
| createdDateTime      | DateTimeOffset                                                                                                   | Date and time of item creation. Read-only.                                                                                                                              |
| cTag                 | String                                                                                                           | An eTag for the content of the item. This eTag isn't changed if only the metadata is changed. **Note** This property isn't returned if the item is a folder. Read-only. |
| deleted              | [deleted](https://learn.microsoft.com/en-us/graph/api/resources/deleted?view=graph-rest-1.0)                     | Information about the deleted state of the item. Read-only.                                                                                                             |
| description          | String                                                                                                           | Provides a user-visible description of the item. Read-write. Only on OneDrive Personal.                                                                                 |
| eTag                 | String                                                                                                           | eTag for the entire item (metadata + content). Read-only.                                                                                                               |
| file                 | [file](https://learn.microsoft.com/en-us/graph/api/resources/file?view=graph-rest-1.0)                           | File metadata, if the item is a file. Read-only.                                                                                                                        |
| fileSystemInfo       | [fileSystemInfo](https://learn.microsoft.com/en-us/graph/api/resources/filesysteminfo?view=graph-rest-1.0)       | File system information on client. Read-write.                                                                                                                          |
| folder               | [folder](https://learn.microsoft.com/en-us/graph/api/resources/folder?view=graph-rest-1.0)                       | Folder metadata, if the item is a folder. Read-only.                                                                                                                    |
| id                   | String                                                                                                           | The unique identifier of the item within the Drive. Read-only.                                                                                                          |
| image                | [image](https://learn.microsoft.com/en-us/graph/api/resources/image?view=graph-rest-1.0)                         | Image metadata, if the item is an image. Read-only.                                                                                                                     |
| lastModifiedBy       | [identitySet](identityset.md)             | Identity of the user, device, and application that last modified the item. Read-only.                                                                                   |
| lastModifiedDateTime | DateTimeOffset                                                                                                   | Date and time the item was last modified. Read-only.                                                                                                                    |
| location             | [geoCoordinates](https://learn.microsoft.com/en-us/graph/api/resources/geocoordinates?view=graph-rest-1.0)       | Location metadata, if the item has location data. Read-only.                                                                                                            |
| malware              | [malware](https://learn.microsoft.com/en-us/graph/api/resources/malware?view=graph-rest-1.0)                     | Malware metadata, if the item was detected to contain malware. Read-only.                                                                                               |
| name                 | String                                                                                                           | The name of the item (filename and extension). Read-write.                                                                                                              |
| package              | [package](https://learn.microsoft.com/en-us/graph/api/resources/package?view=graph-rest-1.0)                     | If present, indicates that this item is a package instead of a folder or file. Packages are treated like files in some contexts and folders in others. Read-only.       |
| parentReference      | [itemReference](https://learn.microsoft.com/en-us/graph/api/resources/itemreference?view=graph-rest-1.0)         | Parent information, if the item has a parent. Read-write.                                                                                                               |
| pendingOperations    | [pendingOperations](https://learn.microsoft.com/en-us/graph/api/resources/pendingoperations?view=graph-rest-1.0) | If present, indicates that one or more operations that might affect the state of the driveItem are pending completion. Read-only.                                       |
| photo                | [photo](https://learn.microsoft.com/en-us/graph/api/resources/photo?view=graph-rest-1.0)                         | Photo metadata, if the item is a photo. Read-only.                                                                                                                      |
| publication          | [publicationFacet](https://learn.microsoft.com/en-us/graph/api/resources/publicationfacet?view=graph-rest-1.0)   | Provides information about the published or checked-out state of an item, in locations that support such actions. This property isn't returned by default. Read-only.   |
| remoteItem           | [remoteItem](https://learn.microsoft.com/en-us/graph/api/resources/remoteitem?view=graph-rest-1.0)               | Remote item data, if the item is shared from a drive other than the one being accessed. Read-only.                                                                      |
| root                 | [root](https://learn.microsoft.com/en-us/graph/api/resources/root?view=graph-rest-1.0)                           | If this property is non-null, it indicates that the driveItem is the top-most driveItem in the drive.                                                                   |
| searchResult         | [searchResult](https://learn.microsoft.com/en-us/graph/api/resources/searchresult?view=graph-rest-1.0)           | Search metadata, if the item is from a search result. Read-only.                                                                                                        |
| shared               | [shared](https://learn.microsoft.com/en-us/graph/api/resources/shared?view=graph-rest-1.0)                       | Indicates that the item was shared with others and provides information about the shared state of the item. Read-only.                                                  |
| sharepointIds        | [sharepointIds](https://learn.microsoft.com/en-us/graph/api/resources/sharepointids?view=graph-rest-1.0)         | Returns identifiers useful for SharePoint REST compatibility. Read-only.                                                                                                |
| size                 | Int64                                                                                                            | Size of the item in bytes. Read-only.                                                                                                                                   |
| specialFolder        | [specialFolder](https://learn.microsoft.com/en-us/graph/api/resources/specialfolder?view=graph-rest-1.0)         | If the current item is also available as a special folder, this facet is returned. Read-only.                                                                           |
| video                | [video](https://learn.microsoft.com/en-us/graph/api/resources/video?view=graph-rest-1.0)                         | Video metadata, if the item is a video. Read-only.                                                                                                                      |
| webDavUrl            | String                                                                                                           | WebDAV compatible URL for the item.                                                                                                                                     |
| webUrl               | String                                                                                                           | URL that displays the resource in the browser. Read-only.                                                                                                               |

> **Note:** The eTag and cTag properties work differently on containers (folders). The cTag value is modified when content or metadata of any descendant of the folder is changed. The eTag value is only modified when the folder's properties are changed, except for properties that are derived from descendants (like **childCount** or **lastModifiedDateTime**).

## Relationships {#relationships}

| Relationship       | Type                                                                                                                      | Description                                                                                                                                                                                              |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| activities         | [itemActivity](https://learn.microsoft.com/en-us/graph/api/resources/itemactivity?view=graph-rest-1.0) collection         | The list of recent activities that took place on this item.                                                                                                                                              |
| analytics          | [itemAnalytics](https://learn.microsoft.com/en-us/graph/api/resources/itemanalytics?view=graph-rest-1.0) resource         | Analytics about the view activities that took place on this item.                                                                                                                                        |
| children           | driveItem collection                                                                                                      | Collection containing Item objects for the immediate children of Item. Only items representing folders have children. Read-only. Nullable.                                                               |
| createdByUser      | [user](https://learn.microsoft.com/en-us/graph/api/resources/users)                                                       | Identity of the user who created the item. Read-only.                                                                                                                                                    |
| lastModifiedByUser | [user](https://learn.microsoft.com/en-us/graph/api/resources/users)                                                       | Identity of the user who last modified the item. Read-only.                                                                                                                                              |
| listItem           | [listItem](https://learn.microsoft.com/en-us/graph/api/resources/listitem?view=graph-rest-1.0)                            | For drives in SharePoint, the associated document library list item. Read-only. Nullable.                                                                                                                |
| permissions        | [permission](https://learn.microsoft.com/en-us/graph/api/resources/permission?view=graph-rest-1.0) collection             | The set of permissions for the item. Read-only. Nullable.                                                                                                                                                |
| retentionLabel     | [itemRetentionLabel](https://learn.microsoft.com/en-us/graph/api/resources/itemretentionlabel?view=graph-rest-1.0)        | Information about retention label and settings enforced on the **driveItem**. Read-write.                                                                                                                |
| subscriptions      | [subscription](https://learn.microsoft.com/en-us/graph/api/resources/subscription?view=graph-rest-1.0) collection         | The set of subscriptions on the item. Only supported on the root of a drive.                                                                                                                             |
| thumbnails         | [thumbnailSet](https://learn.microsoft.com/en-us/graph/api/resources/thumbnailset?view=graph-rest-1.0) collection         | Collection of [thumbnailSet](https://learn.microsoft.com/en-us/graph/api/resources/thumbnailset?view=graph-rest-1.0) objects associated with the item. For more information, see [getting thumbnails](https://learn.microsoft.com/en-us/graph/api/driveitem-list-thumbnails?view=graph-rest-1.0). Read-only. Nullable. |
| versions           | [driveItemVersion](https://learn.microsoft.com/en-us/graph/api/resources/driveitemversion?view=graph-rest-1.0) collection | The list of previous versions of the item. For more info, see [getting previous versions](https://learn.microsoft.com/en-us/graph/api/driveitem-list-versions?view=graph-rest-1.0). Read-only. Nullable. |
| workbook           | [workbook](https://learn.microsoft.com/en-us/graph/api/resources/workbook?view=graph-rest-1.0)                            | For files that are Excel spreadsheets, access to the workbook API to work with the spreadsheet's contents. Nullable.                                                                                     |

## Instance Attributes {#instance-attributes}

Instance attributes are properties with special behaviors. These properties are temporary and either define behavior the service should perform or provide short-term property values, like a download URL for an item that expires.

| Property name                     | Type   | Description                                                                                                                                                                                              |
| --------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| @microsoft.graph.conflictBehavior | string | The conflict resolution behavior for actions that create a new item. You can use the values *fail*, *replace*, or *rename*. The default for PUT is *replace*. An item is never returned with this annotation. Write-only. |
| @microsoft.graph.downloadUrl      | string | A URL that can be used to download this file's content. Authentication isn't required with this URL. Read-only.                                                                                          |
| @microsoft.graph.sourceUrl        | string | This instance annotation can be used to instruct the service to download the contents of the URL when issuing a PUT request, and stores it as the file. Write-only.                                      |

> **Notes:** The parameter `@microsoft.graph.conflictBehavior` should be included in the URL instead of the body of the request.
>
> The `@microsoft.graph.downloadUrl` value is a short-lived URL and can't be cached. The URL is invalidated after for a short period of time (1 hour). Removing file permissions for a user might not immediately invalidate the URL.
>
> Using the `@microsoft.graph.sourceUrl` property for file uploading is [not supported](https://learn.microsoft.com/en-us/onedrive/developer/rest-api/api/driveitem_upload_url?view=odsp-graph-online#remarks&preserve-view=true) in OneDrive for Business, SharePoint Online, and SharePoint Server 2016.

## JSON representation {#json-representation}

The following JSON representation shows the resource type.

The **driveItem** resource is derived from [**baseItem**](https://learn.microsoft.com/en-us/graph/api/resources/baseitem?view=graph-rest-1.0) and inherits properties from that resource.

```json
{
  "audio": { "@odata.type": "microsoft.graph.audio" },
  "bundle": { "@odata.type": "microsoft.graph.bundle" },
  "content": { "@odata.type": "Edm.Stream" },
  "cTag": "string (etag)",
  "deleted": { "@odata.type": "microsoft.graph.deleted"},
  "description": "string",
  "file": { "@odata.type": "microsoft.graph.file" },
  "fileSystemInfo": { "@odata.type": "microsoft.graph.fileSystemInfo" },
  "folder": { "@odata.type": "microsoft.graph.folder" },
  "image": { "@odata.type": "microsoft.graph.image" },
  "location": { "@odata.type": "microsoft.graph.geoCoordinates" },
  "malware": { "@odata.type": "microsoft.graph.malware" },
  "package": { "@odata.type": "microsoft.graph.package" },
  "pendingOperations": { "@odata.type": "microsoft.graph.pendingOperations" },
  "photo": { "@odata.type": "microsoft.graph.photo" },
  "publication": {"@odata.type": "microsoft.graph.publicationFacet"},
  "remoteItem": { "@odata.type": "microsoft.graph.remoteItem" },
  "root": { "@odata.type": "microsoft.graph.root" },
  "searchResult": { "@odata.type": "microsoft.graph.searchResult" },
  "shared": { "@odata.type": "microsoft.graph.shared" },
  "sharepointIds": { "@odata.type": "microsoft.graph.sharepointIds" },
  "size": 1024,
  "specialFolder": { "@odata.type": "microsoft.graph.specialFolder" },
  "video": { "@odata.type": "microsoft.graph.video" },
  "webDavUrl": "string",

  /* relationships */
  "activities": [{"@odata.type": "microsoft.graph.itemActivity"}],
  "analytics": {"@odata.type": "microsoft.graph.itemAnalytics"},
  "children": [{ "@odata.type": "microsoft.graph.driveItem" }],
  "createdByUser": { "@odata.type": "microsoft.graph.user" },
  "retentionLabel": { "@odata.type": "microsoft.graph.itemRetentionLabel" },
  "lastModifiedByUser": { "@odata.type": "microsoft.graph.user" },
  "permissions": [ {"@odata.type": "microsoft.graph.permission"} ],
  "subscriptions": [ {"@odata.type": "microsoft.graph.subscription"} ],
  "thumbnails": [ {"@odata.type": "microsoft.graph.thumbnailSet"}],
  "versions": [ {"@odata.type": "microsoft.graph.driveItemVersion"}],

  /* inherited from baseItem */
  "createdBy": {"@odata.type": "microsoft.graph.identitySet"},
  "createdDateTime": "String (timestamp)",
  "eTag": "string",
  "id": "string (identifier)",
  "lastModifiedBy": {"@odata.type": "microsoft.graph.identitySet"},
  "lastModifiedDateTime": "String (timestamp)",
  "name": "string",
  "parentReference": {"@odata.type": "microsoft.graph.itemReference"},
  "webUrl": "string",

  /* instance annotations */
  "@microsoft.graph.conflictBehavior": "string",
  "@microsoft.graph.downloadUrl": "url",
  "@microsoft.graph.sourceUrl": "url"
}
```

---

## Feedback {#ms--feedback}

Was this page helpful?
