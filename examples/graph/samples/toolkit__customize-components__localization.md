---
canonical_url: https://learn.microsoft.com/en-us/graph/toolkit/customize-components/localization
content_sha256: ca5bc7d7b9fbd33b7fc1b2d4ea54e379067fa94db7ccbd178647479d4c8d4c67
converter: html-to-markdown/3.x
description: Use LocalizationHelper to localize Microsoft Graph Toolkit components.
etag: '"voUq+usnTVqlv4ve9kNbAhuNVRw="'
extractor: profile:mslearn
fetched_at: '2026-10-28T13:59:07Z'
keywords: [microsoft graph toolkit, strings, graph toolkit components, supported microsoft graph, tasks-base, microsoft graph sdks, microsoft graph tools, person-card-contact]
last_modified: '2025-09-04T23:33:00Z'
locale: en-us
low_confidence: false
profile: mslearn
quality_flags: []
quality_score: 1.0
render: http
sitemap_lastmod: '2025-09-04'
source_url: https://learn.microsoft.com/en-us/graph/toolkit/customize-components/localization
title: Localizing the Microsoft Graph Toolkit components
version: v1.0
---

# Localizing the Microsoft Graph Toolkit components {#localizing-the-microsoft-graph-toolkit-components}

> [!CAUTION]
>
> The Microsoft Graph Toolkit is deprecated. The retirement period begins September 1, 2025, with full retirement planned for August 28, 2026. Developers should migrate to using the Microsoft Graph SDKs or other supported Microsoft Graph tools for building web experiences. For more information, see the [deprecation announcement](https://devblogs.microsoft.com/microsoft365dev/microsoft-graph-toolkit-retirement/).

Localization is an important aspect of application development to support users with various language requirements globally.

You can localize the Microsoft Graph Toolkit components to ensure that the UI reflects the target language.

## Use LocalizationHelper to add localized strings {#use-localizationhelper-to-add-localized-strings}

None of the strings in the toolkit are localized, but you can provide your own localized strings and manage different languages through the same process you use for localizing your app. To facilitate localization, the toolkit exposes the `LocalizationHelper` static class.

The following example shows how to localize several components.

```typescript
import { LocalizationHelper } from "@microsoft/mgt-element";

LocalizationHelper.strings = {
  noResultsFound: "لم نجد أي قنوات",
  _components: {
    "login": {
      signInLinkSubtitle: "login",
      signOutLinkSubtitle: "خروج",
    },
    "people-picker": {
      inputPlaceholderText: "ابدأ في كتابة الاسم",
      noResultsFound: "لم نجد أي قنوات", // will overwrite globally defined noResultsFound in people-picker component
      loadingMessage: "...جار التحميل",
    },
    "teams-channel-picker": {
      inputPlaceholderText: "حدد قناة",
      noResultsFound: "local NoResultsFound Example",
      // loadingMessage: is default string "Loading..." for this example since not defined globally or locally
    },
    "tasks": {
      removeTaskSubtitle: "delete",
      cancelNewTaskSubtitle: "canceltest",
      newTaskPlaceholder: "newTaskTest",
      addTaskButtonSubtitle: "addme",
    },
    "person-card": {
      sendEmailLinkSubtitle: "ارسل بريد الكتروني",
      startChatLinkSubtitle: "ابدأ الدردشة",
      showExpandedDetailsButton: 'Show expanded details',
      showMoreSectionButton: "أظهر المزيد", // global declaration
    },
    "person-card-contact": {
      contactSectionTitle: "اتصل",
    },
    "person-card-organization": {
      reportsToSectionTitle: "تقارير ل",
      directReportsSectionTitle: "تقارير مباشرة",
      organizationSectionTitle: "منظمة",
      youWorkWithSubSectionTitle: "انت تعمل مع",
      userWorksWithSubSectionTitle: "يعمل مع",
    },
  },
};
```

When the `strings` property of `LocalizationHelper` is assigned, all components will automatically pick up the new strings and re-render, allowing you to change strings dynamically.

The strings can be set at a global level or per component (with the `_components:` property).

## Strings {#strings}

### Login {#login}

```typescript
"login": {
  signInLinkSubtitle: "Sign In",
  signOutLinkSubtitle: "Sign Out"
}
```

### People-Picker {#people-picker}

```typescript
"people-picker": {
  inputPlaceholderText: "Start typing a name",
  noResultsFound: `We didn't find any matches.`,
  loadingMessage: "Loading..."
}
```

### Teams-Channel-Picker {#teams-channel-picker}

```typescript
"teams-channel-picker": {
  inputPlaceholderText: "Select a channel",
  noResultsFound: `We didn't find any matches.`,
  loadingMessage: "Loading..."
}
```

### Tasks {#tasks}

```typescript
"tasks": {
  removeTaskSubtitle: "Delete Task",
  cancelNewTaskSubtitle: "cancel",
  newTaskPlaceholder: "Task...",
  addTaskButtonSubtitle: "Add"
}
```

### Tasks-Base {#tasks-base}

```typescript
"tasks-base": {
  removeTaskSubtitle: "Delete Task",
  cancelNewTaskSubtitle: "cancel",
  newTaskPlaceholder: "Task...",
  addTaskButtonSubtitle: "Add"
}
```

### Todo {#todo}

```typescript
"todo": {
  removeTaskSubtitle: "Delete Task",
  cancelNewTaskSubtitle: "cancel",
  newTaskPlaceholder: "Task...",
  addTaskButtonSubtitle: "Add"
}
```

### Person-Card {#person-card}

```typescript
"person-card": {
  sendEmailLinkSubtitle: "Send email",
  startChatLinkSubtitle: "Start chat",
  showMoreSectionButton: "Show more"
}
```

### Person-Card-Contact {#person-card-contact}

```typescript
"person-card-contact": {
  contactSectionTitle: "Contact"
}
```

### Person-Card-Organization {#person-card-organization}

```typescript
"person-card-organization": {
  reportsToSectionTitle: "Reports to",
  directReportsSectionTitle: "Direct reports",
  organizationSectionTitle: "Organization",
  youWorkWithSubSectionTitle: "You work with",
  userWorksWithSubSectionTitle: "works with"
}
```

### Person-Card-Messages {#person-card-messages}

```typescript
"person-card-messages": {
  emailsSectionTitle: "Emails"
}
```

### Person-Card-Files {#person-card-files}

```typescript
"person-card-files": {
  filesSectionTitle: "Files",
  sharedTextSubtitle: "Shared"
}
```

### Person-Card-Profile {#person-card-profile}

```typescript
"person-card-profile": {
  SkillsAndExperienceSectionTitle: "Skills & Experience",
  AboutCompactSectionTitle: "About",
  SkillsSubSectionTitle: "Skills",
  LanguagesSubSectionTitle: "Languages",
  WorkExperienceSubSectionTitle: "Work Experience",
  EducationSubSectionTitle: "Education",
  professionalInterestsSubSectionTitle: "Professional Interests",
  personalInterestsSubSectionTitle: "Personal Interests",
  birthdaySubSectionTitle: "Birthday",
  currentYearSubtitle: "Current"
}
```

### File {#file}

```typescript
'file': {
  modifiedSubtitle: 'Modified',
  sizeSubtitle: 'Size'
};
```

### File-List {#file-list}

```typescript
"file-list": {
  showMoreSubtitle: 'Show more items'
}
```

---

## Feedback {#ms--feedback}

Was this page helpful?
