---
breadcrumbs: [Google Workspace]
canonical_url: https://developers.google.com/workspace/cloud-search/docs/reference/sdk/com/google/enterprise/cloudsearch/sdk/indexing/util/UploadRequest.IndexItemRequest
content_sha256: 9f5bf9ef06b0ce1fe48f120c9a6a304ff4c70f765869b6baaf0ab15bc86cdc2b
converter: html-to-markdown/3.x
description: public static class **UploadRequest.IndexItemRequest** extends…
extractor: profile:devsite
fetched_at: '2026-10-28T14:03:12Z'
keywords: [arg0 object, string, object remove object, direct subclasses uploadrequest.indexitemandcontentrequest, object put object, object arg1, object getordefault object]
last_modified: '2025-10-17T17:35:19Z'
low_confidence: true
profile: devsite
quality_flags: [code_blocks, html_table_kept, uncrawled_internal]
quality_score: 0.85
render: http
sitemap_lastmod: '2025-10-17T17:38:02+00:00'
source_url: https://developers.google.com/workspace/cloud-search/docs/reference/sdk/com/google/enterprise/cloudsearch/sdk/indexing/util/UploadRequest.IndexItemRequest
title: UploadRequest.IndexItemRequest
---

# UploadRequest.IndexItemRequest

public static class **UploadRequest.IndexItemRequest** extends [UploadRequest.AbstractRequest](https://developers.google.com/workspace/cloud-search/docs/reference/sdk/com/google/enterprise/cloudsearch/sdk/indexing/util/UploadRequest.AbstractRequest)

Known Direct Subclasses

[UploadRequest.IndexItemAndContentRequest](https://developers.google.com/workspace/cloud-search/docs/reference/sdk/com/google/enterprise/cloudsearch/sdk/indexing/util/UploadRequest.IndexItemAndContentRequest)

<table>
<tr>
<td><a href="https://developers.google.com/workspace/cloud-search/docs/reference/sdk/com/google/enterprise/cloudsearch/sdk/indexing/util/UploadRequest.IndexItemAndContentRequest">UploadRequest.IndexItemAndContentRequest</a></td>
<td>Request to index an Item and its content to the indexing API. </td>
</tr>
</table>

Request to index an Item to the indexing API.

- *item* is the [`Item`](https://developers.google.com/resources/api-libraries/documentation/cloudsearch/v1/java/latest/com/google/api/services/cloudsearch/v1/model/Item.html) object that needs to be updated in the indexing API.
- *isIncremental* is true if this is to be an incremental update instead of the default backfill.

An example of IndexItemRequest is:

```json
  {
    "item": {
         "name": "test123",
         "itemType": "CONTAINER_ITEM",
         "content": {
             "content_format": "TEXT"
          },
          "acl":  {
              "readers":
              [
                  {
                      "gsuitePrincipal":
                      {
                          "gsuiteDomain":true
                      }
                  }
              ]
          }
    },
    "indexItemOptions": {
        "allowUnknownGsuitePrincipals":true
    },
    "type": "items.indexItem",
    "isIncremental": "true"
  }
 
```

### Inherited Field Summary {#inherited-field-summary}

From class [com.google.enterprise.cloudsearch.sdk.indexing.util.UploadRequest.AbstractRequest](https://developers.google.com/workspace/cloud-search/docs/reference/sdk/com/google/enterprise/cloudsearch/sdk/indexing/util/UploadRequest.AbstractRequest)

<table>
<tr>
<td> public String</td>
<td><a href="https://developers.google.com/workspace/cloud-search/docs/reference/sdk/com/google/enterprise/cloudsearch/sdk/indexing/util/UploadRequest.AbstractRequest#type">type</a></td>
<td></td>
</tr>
</table>

### Public Constructor Summary {#public-constructor-summary}

<table id="pubctors">
<tr>
<td>
</td>
<td>
<div>
<span><a href="#UploadRequest.IndexItemRequest()">UploadRequest.IndexItemRequest</a></span>() </div>
</td>
</tr>
</table>

### Inherited Method Summary {#inherited-method-summary}

From class com.google.api.client.json.GenericJson

<table>
<tr>
<td> Object </td>
<td>
<div>
<span>clone</span>() </div>
</td>
</tr>
<tr>
<td> final JsonFactory </td>
<td>
<div>
<span>getFactory</span>() </div>
</td>
</tr>
<tr>
<td> GenericData </td>
<td>
<div>
<span>set</span>(String arg0, Object arg1) </div>
</td>
</tr>
<tr>
<td> final void </td>
<td>
<div>
<span>setFactory</span>(JsonFactory arg0) </div>
</td>
</tr>
<tr>
<td> String </td>
<td>
<div>
<span>toPrettyString</span>() </div>
</td>
</tr>
<tr>
<td> String </td>
<td>
<div>
<span>toString</span>() </div>
</td>
</tr>
</table>

From class com.google.api.client.util.GenericData

<table>
<tr>
<td> Object </td>
<td>
<div>
<span>clone</span>() </div>
</td>
</tr>
<tr>
<td> Set&lt;Entry&lt;String, Object&gt;&gt; </td>
<td>
<div>
<span>entrySet</span>() </div>
</td>
</tr>
<tr>
<td> final Object </td>
<td>
<div>
<span>get</span>(Object arg0) </div>
</td>
</tr>
<tr>
<td> final ClassInfo </td>
<td>
<div>
<span>getClassInfo</span>() </div>
</td>
</tr>
<tr>
<td> final Map&lt;String, Object&gt; </td>
<td>
<div>
<span>getUnknownKeys</span>() </div>
</td>
</tr>
<tr>
<td> Object </td>
<td>
<div>
<span>put</span>(Object arg0, Object arg1) </div>
</td>
</tr>
<tr>
<td> final Object </td>
<td>
<div>
<span>put</span>(String arg0, Object arg1) </div>
</td>
</tr>
<tr>
<td> final void </td>
<td>
<div>
<span>putAll</span>(Map&lt;? extends String, ?&gt; arg0) </div>
</td>
</tr>
<tr>
<td> final Object </td>
<td>
<div>
<span>remove</span>(Object arg0) </div>
</td>
</tr>
<tr>
<td> GenericData </td>
<td>
<div>
<span>set</span>(String arg0, Object arg1) </div>
</td>
</tr>
<tr>
<td> final void </td>
<td>
<div>
<span>setUnknownKeys</span>(Map&lt;String, Object&gt; arg0) </div>
</td>
</tr>
</table>

From class java.util.AbstractMap

<table>
<tr>
<td> void </td>
<td>
<div>
<span>clear</span>() </div>
</td>
</tr>
<tr>
<td> boolean </td>
<td>
<div>
<span>containsKey</span>(Object arg0) </div>
</td>
</tr>
<tr>
<td> boolean </td>
<td>
<div>
<span>containsValue</span>(Object arg0) </div>
</td>
</tr>
<tr>
<td> abstract Set&lt;Entry&lt;String, Object&gt;&gt; </td>
<td>
<div>
<span>entrySet</span>() </div>
</td>
</tr>
<tr>
<td> boolean </td>
<td>
<div>
<span>equals</span>(Object arg0) </div>
</td>
</tr>
<tr>
<td> Object </td>
<td>
<div>
<span>get</span>(Object arg0) </div>
</td>
</tr>
<tr>
<td> int </td>
<td>
<div>
<span>hashCode</span>() </div>
</td>
</tr>
<tr>
<td> boolean </td>
<td>
<div>
<span>isEmpty</span>() </div>
</td>
</tr>
<tr>
<td> Set&lt;String&gt; </td>
<td>
<div>
<span>keySet</span>() </div>
</td>
</tr>
<tr>
<td> Object </td>
<td>
<div>
<span>put</span>(String arg0, Object arg1) </div>
</td>
</tr>
<tr>
<td> void </td>
<td>
<div>
<span>putAll</span>(Map&lt;? extends K, ? extends V&gt; arg0) </div>
</td>
</tr>
<tr>
<td> Object </td>
<td>
<div>
<span>remove</span>(Object arg0) </div>
</td>
</tr>
<tr>
<td> int </td>
<td>
<div>
<span>size</span>() </div>
</td>
</tr>
<tr>
<td> String </td>
<td>
<div>
<span>toString</span>() </div>
</td>
</tr>
<tr>
<td> Collection&lt;Object&gt; </td>
<td>
<div>
<span>values</span>() </div>
</td>
</tr>
</table>

From class java.lang.Object

<table>
<tr>
<td> boolean </td>
<td>
<div>
<span>equals</span>(Object arg0) </div>
</td>
</tr>
<tr>
<td> final Class&lt;?&gt; </td>
<td>
<div>
<span>getClass</span>() </div>
</td>
</tr>
<tr>
<td> int </td>
<td>
<div>
<span>hashCode</span>() </div>
</td>
</tr>
<tr>
<td> final void </td>
<td>
<div>
<span>notify</span>() </div>
</td>
</tr>
<tr>
<td> final void </td>
<td>
<div>
<span>notifyAll</span>() </div>
</td>
</tr>
<tr>
<td> String </td>
<td>
<div>
<span>toString</span>() </div>
</td>
</tr>
<tr>
<td> final void </td>
<td>
<div>
<span>wait</span>(long arg0, int arg1) </div>
</td>
</tr>
<tr>
<td> final void </td>
<td>
<div>
<span>wait</span>(long arg0) </div>
</td>
</tr>
<tr>
<td> final void </td>
<td>
<div>
<span>wait</span>() </div>
</td>
</tr>
</table>

From interface java.util.Map

<table>
<tr>
<td> abstract void </td>
<td>
<div>
<span>clear</span>() </div>
</td>
</tr>
<tr>
<td> Object </td>
<td>
<div>
<span>compute</span>(String arg0, BiFunction&lt;? super K, ? super V, ? extends V&gt; arg1) </div>
</td>
</tr>
<tr>
<td> Object </td>
<td>
<div>
<span>computeIfAbsent</span>(String arg0, Function&lt;? super K, ? extends V&gt; arg1) </div>
</td>
</tr>
<tr>
<td> Object </td>
<td>
<div>
<span>computeIfPresent</span>(String arg0, BiFunction&lt;? super K, ? super V, ? extends V&gt; arg1) </div>
</td>
</tr>
<tr>
<td> abstract boolean </td>
<td>
<div>
<span>containsKey</span>(Object arg0) </div>
</td>
</tr>
<tr>
<td> abstract boolean </td>
<td>
<div>
<span>containsValue</span>(Object arg0) </div>
</td>
</tr>
<tr>
<td> static &lt;K, V&gt; Map&lt;String, Object&gt; </td>
<td>
<div>
<span>copyOf</span>(Map&lt;? extends K, ? extends V&gt; arg0) </div>
</td>
</tr>
<tr>
<td> static &lt;K, V&gt; Entry&lt;String, Object&gt; </td>
<td>
<div>
<span>entry</span>(String arg0, Object arg1) </div>
</td>
</tr>
<tr>
<td> abstract Set&lt;Entry&lt;String, Object&gt;&gt; </td>
<td>
<div>
<span>entrySet</span>() </div>
</td>
</tr>
<tr>
<td> abstract boolean </td>
<td>
<div>
<span>equals</span>(Object arg0) </div>
</td>
</tr>
<tr>
<td> void </td>
<td>
<div>
<span>forEach</span>(BiConsumer&lt;? super K, ? super V&gt; arg0) </div>
</td>
</tr>
<tr>
<td> abstract Object </td>
<td>
<div>
<span>get</span>(Object arg0) </div>
</td>
</tr>
<tr>
<td> Object </td>
<td>
<div>
<span>getOrDefault</span>(Object arg0, Object arg1) </div>
</td>
</tr>
<tr>
<td> abstract int </td>
<td>
<div>
<span>hashCode</span>() </div>
</td>
</tr>
<tr>
<td> abstract boolean </td>
<td>
<div>
<span>isEmpty</span>() </div>
</td>
</tr>
<tr>
<td> abstract Set&lt;String&gt; </td>
<td>
<div>
<span>keySet</span>() </div>
</td>
</tr>
<tr>
<td> Object </td>
<td>
<div>
<span>merge</span>(String arg0, Object arg1, BiFunction&lt;? super V, ? super V, ? extends V&gt; arg2) </div>
</td>
</tr>
<tr>
<td> static &lt;K, V&gt; Map&lt;String, Object&gt; </td>
<td>
<div>
<span>of</span>(String arg0, Object arg1, String arg2, Object arg3, String arg4, Object arg5, String arg6, Object arg7, String arg8, Object arg9) </div>
</td>
</tr>
<tr>
<td> static &lt;K, V&gt; Map&lt;String, Object&gt; </td>
<td>
<div>
<span>of</span>(String arg0, Object arg1, String arg2, Object arg3, String arg4, Object arg5, String arg6, Object arg7) </div>
</td>
</tr>
<tr>
<td> static &lt;K, V&gt; Map&lt;String, Object&gt; </td>
<td>
<div>
<span>of</span>(String arg0, Object arg1) </div>
</td>
</tr>
<tr>
<td> static &lt;K, V&gt; Map&lt;String, Object&gt; </td>
<td>
<div>
<span>of</span>(String arg0, Object arg1, String arg2, Object arg3, String arg4, Object arg5, String arg6, Object arg7, String arg8, Object arg9, String arg10, Object arg11, String arg12, Object arg13, String arg14, Object arg15) </div>
</td>
</tr>
<tr>
<td> static &lt;K, V&gt; Map&lt;String, Object&gt; </td>
<td>
<div>
<span>of</span>(String arg0, Object arg1, String arg2, Object arg3) </div>
</td>
</tr>
<tr>
<td> static &lt;K, V&gt; Map&lt;String, Object&gt; </td>
<td>
<div>
<span>of</span>(String arg0, Object arg1, String arg2, Object arg3, String arg4, Object arg5) </div>
</td>
</tr>
<tr>
<td> static &lt;K, V&gt; Map&lt;String, Object&gt; </td>
<td>
<div>
<span>of</span>() </div>
</td>
</tr>
<tr>
<td> static &lt;K, V&gt; Map&lt;String, Object&gt; </td>
<td>
<div>
<span>of</span>(String arg0, Object arg1, String arg2, Object arg3, String arg4, Object arg5, String arg6, Object arg7, String arg8, Object arg9, String arg10, Object arg11, String arg12, Object arg13, String arg14, Object arg15, String arg16, Object arg17) </div>
</td>
</tr>
<tr>
<td> static &lt;K, V&gt; Map&lt;String, Object&gt; </td>
<td>
<div>
<span>of</span>(String arg0, Object arg1, String arg2, Object arg3, String arg4, Object arg5, String arg6, Object arg7, String arg8, Object arg9, String arg10, Object arg11) </div>
</td>
</tr>
<tr>
<td> static &lt;K, V&gt; Map&lt;String, Object&gt; </td>
<td>
<div>
<span>of</span>(String arg0, Object arg1, String arg2, Object arg3, String arg4, Object arg5, String arg6, Object arg7, String arg8, Object arg9, String arg10, Object arg11, String arg12, Object arg13) </div>
</td>
</tr>
<tr>
<td> static &lt;K, V&gt; Map&lt;String, Object&gt; </td>
<td>
<div>
<span>of</span>(String arg0, Object arg1, String arg2, Object arg3, String arg4, Object arg5, String arg6, Object arg7, String arg8, Object arg9, String arg10, Object arg11, String arg12, Object arg13, String arg14, Object arg15, String arg16, Object arg17, String arg18, Object arg19) </div>
</td>
</tr>
<tr>
<td> static &lt;K, V&gt; Map&lt;String, Object&gt; </td>
<td>
<div>
<span>ofEntries</span>(Entry...&lt;? extends K, ? extends V&gt; arg0) </div>
</td>
</tr>
<tr>
<td> abstract Object </td>
<td>
<div>
<span>put</span>(String arg0, Object arg1) </div>
</td>
</tr>
<tr>
<td> abstract void </td>
<td>
<div>
<span>putAll</span>(Map&lt;? extends K, ? extends V&gt; arg0) </div>
</td>
</tr>
<tr>
<td> Object </td>
<td>
<div>
<span>putIfAbsent</span>(String arg0, Object arg1) </div>
</td>
</tr>
<tr>
<td> boolean </td>
<td>
<div>
<span>remove</span>(Object arg0, Object arg1) </div>
</td>
</tr>
<tr>
<td> abstract Object </td>
<td>
<div>
<span>remove</span>(Object arg0) </div>
</td>
</tr>
<tr>
<td> boolean </td>
<td>
<div>
<span>replace</span>(String arg0, Object arg1, Object arg2) </div>
</td>
</tr>
<tr>
<td> Object </td>
<td>
<div>
<span>replace</span>(String arg0, Object arg1) </div>
</td>
</tr>
<tr>
<td> void </td>
<td>
<div>
<span>replaceAll</span>(BiFunction&lt;? super K, ? super V, ? extends V&gt; arg0) </div>
</td>
</tr>
<tr>
<td> abstract int </td>
<td>
<div>
<span>size</span>() </div>
</td>
</tr>
<tr>
<td> abstract Collection&lt;Object&gt; </td>
<td>
<div>
<span>values</span>() </div>
</td>
</tr>
</table>

## Public Constructors {#public-constructors}

<a id="UploadRequest.IndexItemRequest()"></a>

#### public **UploadRequest.IndexItemRequest** () {#public-uploadrequest.indexitemrequest}

<a id="navbar_top"></a>
