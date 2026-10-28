---
breadcrumbs: [Google Workspace]
canonical_url: https://developers.google.com/workspace/drive/labels/reference/rest/v2beta/labels.permissions
content_sha256: a66f6e5aab5f6ca4178a9fe66b3ad8447e4e5497ef405c2bec28ad2997e9ca8b
converter: html-to-markdown/3.x
description: The permission that applies to a principal (user, group, audience) on a label.
extractor: profile:devsite
fetched_at: '2026-10-28T14:03:02Z'
keywords: [json representation, labelrole, rest resource, labelpermission, label permissions, group, string, principal]
last_modified: '2026-02-24T16:58:12Z'
low_confidence: false
profile: devsite
quality_flags: [html_table_kept, uncrawled_internal]
quality_score: 1.0
render: http
sitemap_lastmod: '2026-02-24T16:58:25+00:00'
source_url: https://developers.google.com/workspace/drive/labels/reference/rest/v2beta/labels.permissions
title: 'REST Resource: labels.permissions'
---

# REST Resource: labels.permissions

- [Resource: LabelPermission](#LabelPermission)
  - [JSON representation](#LabelPermission.SCHEMA_REPRESENTATION)
  - [LabelRole](#LabelPermission.LabelRole)
- [Methods](#METHODS_SUMMARY)

<a id="LabelPermission"></a>

## Resource: LabelPermission {#resource:-labelpermission}

The permission that applies to a principal (user, group, audience) on a label.

<a id="LabelPermission.SCHEMA_REPRESENTATION"></a>

<table>
<thead>
<tr>
<th>JSON representation</th>
</tr>
</thead>
<tbody>
<tr>
<td><div></div><div><pre><span>{</span>
  <span>"name"</span><span>: </span><span>string</span><span>,</span>
  <span>"email"</span><span>: </span><span>string</span><span>,</span>
  <span>"role"</span><span>: </span><span>enum (<code><a href="#LabelPermission.LabelRole">LabelRole</a></code>)</span><span>,</span>
  <span>"person"</span><span>: </span><span>string</span><span>,</span>
  <span>"group"</span><span>: </span><span>string</span><span>,</span>
  <span>"audience"</span><span>: </span><span>string</span>
<span>}</span></pre></div></td>
</tr>
</tbody>
</table>

<table id="LabelPermission.FIELDS-table">
<colgroup>
<col>
<col>
</colgroup>
<thead>
<tr>
<th colspan="2">Fields</th>
</tr>
</thead>
<tbody>
<tr id="LabelPermission.FIELDS.name">
<td><code>name</code></td>
<td>
<p><code>string</code></p>
<p>Resource name of this permission.</p>
</td>
</tr>
<tr id="LabelPermission.FIELDS.email">
<td><code>email</code></td>
<td>
<p><code>string</code></p>
<p>Specifies the email address for a user or group pricinpal. Not populated for audience principals. User and Group permissions may only be inserted using email address. On update requests, if email address is specified, no principal should be specified.</p>
</td>
</tr>
<tr id="LabelPermission.FIELDS.role">
<td><code>role</code></td>
<td>
<p><code>enum (<code><a href="#LabelPermission.LabelRole">LabelRole</a></code>)</code></p>
<p>The role the principal should have.</p>
</td>
</tr>
<tr id="LabelPermission.FIELDS.oneof_principal">
<td colspan="2">Union field <code>principal</code>. The principal this permission applies to. Must be either an email, user, group, or audience. Example: * people/12345 * groups/45678 * audiences/default <code>principal</code> can be only one of the following:</td>
</tr>
<tr id="LabelPermission.FIELDS.person">
<td><code>person</code></td>
<td>
<p><code>string</code></p>
<p>Person resource name.</p>
</td>
</tr>
<tr id="LabelPermission.FIELDS.group">
<td><code>group</code></td>
<td>
<p><code>string</code></p>
<p>Group resource name.</p>
</td>
</tr>
<tr id="LabelPermission.FIELDS.audience">
<td><code>audience</code></td>
<td>
<p><code>string</code></p>
<p>Audience to grant a role to. The magic value of <code>audiences/default</code> may be used to apply the role to the default audience in the context of the organization that owns the Label.</p>
</td>
</tr>
</tbody>
</table>

<a id="LabelPermission.LabelRole"></a>

### LabelRole {#labelrole}

Roles are concentric with subsequent role.

<table id="LabelPermission.LabelRole.ENUM_VALUES-table">
<colgroup>
<col>
<col>
</colgroup>
<thead>
<tr>
<th colspan="2">Enums</th>
</tr>
</thead>
<tbody>
<tr id="LabelPermission.LabelRole.ENUM_VALUES.LABEL_ROLE_UNSPECIFIED">
<td><code>LABEL_ROLE_UNSPECIFIED</code></td>
<td>Unknown role.</td>
</tr>
<tr id="LabelPermission.LabelRole.ENUM_VALUES.READER">
<td><code>READER</code></td>
<td>A reader can read the label and associated metadata applied to Drive items.</td>
</tr>
<tr id="LabelPermission.LabelRole.ENUM_VALUES.APPLIER">
<td><code>APPLIER</code></td>
<td>An applier can write associated metadata on Drive items in which they also have write access to. Implies <code>READER</code>.</td>
</tr>
<tr id="LabelPermission.LabelRole.ENUM_VALUES.ORGANIZER">
<td><code>ORGANIZER</code></td>
<td>An organizer can pin this label in shared drives they manage and add new appliers to the label.</td>
</tr>
<tr id="LabelPermission.LabelRole.ENUM_VALUES.EDITOR">
<td><code>EDITOR</code></td>
<td>Editors can make any update including deleting the label which also deletes the associated Drive item metadata. Implies <code>APPLIER</code>.</td>
</tr>
</tbody>
</table>

<a id="METHODS_SUMMARY"></a>

<table id="METHODS_SUMMARY-table">
<colgroup>
<col>
<col>
</colgroup>
<thead>
<tr>
<th colspan="2"><h2 id="methods">Methods</h2></th>
</tr>
</thead>
<tbody>
<tr>
<td>
<h3 id="batchdelete"><code><a href="https://developers.google.com/workspace/drive/labels/reference/rest/v2beta/labels.permissions/batchDelete">batchDelete</a></code></h3></td>
<td> Deletes Label permissions.</td>
</tr>
<tr>
<td>
<h3 id="batchupdate"><code><a href="https://developers.google.com/workspace/drive/labels/reference/rest/v2beta/labels.permissions/batchUpdate">batchUpdate</a></code></h3></td>
<td> Updates Label permissions.</td>
</tr>
<tr>
<td>
<h3 id="create"><code><a href="labels.permissions/create.md">create</a></code></h3></td>
<td> Updates a Label's permissions.</td>
</tr>
<tr>
<td>
<h3 id="delete"><code><a href="https://developers.google.com/workspace/drive/labels/reference/rest/v2beta/labels.permissions/delete">delete</a></code></h3></td>
<td> Deletes a Label's permission.</td>
</tr>
<tr>
<td>
<h3 id="list"><code><a href="https://developers.google.com/workspace/drive/labels/reference/rest/v2beta/labels.permissions/list">list</a></code></h3></td>
<td> Lists a Label's permissions.</td>
</tr>
</tbody>
</table>
