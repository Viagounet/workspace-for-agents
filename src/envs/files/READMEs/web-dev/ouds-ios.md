<h1 align="center">OUDS iOS</h1>

<p align="center">
  OUDS iOS provides Orange iOS components to developers and a demo application.
  <br>
  <a href="https://github.com/Orange-OpenSource/ouds-ios/issues/new?assignees=pylapp&labels=%F0%9F%90%9E%20bug%2C%F0%9F%94%8D+triage&template=bug_report.yml&title=[Bug]%3A+Bug+Summary">Report bug</a>
  ·
  <a href="https://github.com/Orange-OpenSource/ouds-ios/issues/new?assignees=pylapp&labels=feature%2C%F0%9F%94%8D%20triage&template=feature_request.yml&title=[feature]%3A+">Request feature</a>
  ·
  <a href="https://ios.unified-design-system.orange.com/">Online documentation</a>
·
  <a href="https://github.com/Orange-OpenSource/ouds-ios/wiki">Wiki</a>
</p>

## Table of contents

- [Status](#status)
- [OUDS](#ouds)
- [Content](#content)
- [Import the library](#import-the-library)
- [Bugs and feature requests](#bugs-and-feature-requests)
- [Contributing](#contributing)
- [Copyright and license](#copyright-and-license)

## Status

[![MIT license](https://img.shields.io/github/license/Orange-OpenSource/ouds-ios?style=for-the-badge)](https://github.com/Orange-OpenSource/ouds-ios/blob/main/LICENSE)

[![Versions](https://img.shields.io/github/v/release/Orange-OpenSource/ouds-ios?label=Last%20version&style=for-the-badge)](https://github.com/Orange-OpenSource/ouds-ios/releases)
[![Still maintained](https://img.shields.io/maintenance/yes/2024?style=for-the-badge)](https://github.com/Orange-OpenSource/ouds-ios/issues?q=is%3Aissue+is%3Aclosed)

[![Code size](https://img.shields.io/github/languages/code-size/Orange-OpenSource/ouds-ios?style=for-the-badge)](https://github.com/Orange-OpenSource/ouds-ios)
[![Opened issues](https://img.shields.io/github/issues-raw/Orange-OpenSource/ouds-ios?style=for-the-badge)](https://github.com/Orange-OpenSource/ouds-ios/issues)

[![iOS 15.0](https://img.shields.io/badge/iOS-15.0-FF1AB2?style=for-the-badge)](https://developer.apple.com/support/app-store "iOS 15 supports")
[![Xcode 16](https://img.shields.io/badge/Xcode-16-blue?style=for-the-badge)](https://developer.apple.com/documentation/xcode-release-notes/xcode-16-release-notes)
[![Swift 6](https://img.shields.io/badge/Swift-6-orange?style=for-the-badge)](https://www.swift.org/blog/announcing-swift-6/)

## Content

This repository contains the OUDS iOS library that provides Orange iOS components for its unified design system, but also a demo application showcasing these different components.

You can find the [detailed technical documentation online](https://ios.unified-design-system.orange.com/), and also the [whole design system](https://unified-design-system.orange.com/).

Details about the project are also [available in the wiki](https://github.com/Orange-OpenSource/ouds-ios/wiki).

## Import the library

Add in *Xcode* the Swift package dependency `https://github.com/Orange-OpenSource/ouds-ios`.

Then add in your project the modules you need within:
- `OUDSModules` containing OUDS modules with features
- `OUDSComponents` containing all components embeded also inside _modules_
- `OUDSThemesInverseTheme` providing a _theme_ with inverted colors for _components_
- `OUDSThemesOrangeTheme` providing the default _Orange_ theme defining style for _components_
- `OUDS` providing basic objects and low layer of responsabilities to help to implement _themes_
- `OUDSTokensComponent` providing _component tokens_ for _components_ to add in applications and _modules_
- `OUDSTokensSemantic` providing _semantic tokens_ 
- `OUDSTokensRaw` providing _raw tokens_
- `OUDSFoundations` providing low level and utils objects.

You must define the theme you use in your app root view:

```swift
import OUDS  // To get OUDSThemeableView
import OUDSThemeOrange // To get OrangeTheme
import SwiftUI

@main
struct YourApp: App {
    var body: some Scene {
       WindowGroup {
          OUDSThemeableView(theme: OrangeTheme()) {
                // Your root view
          }
       }
    }
}
```

Then get the current thme using `@Environment(\.theme) var theme` and use it! You can also use the moudles and the components exposed by the library.

## OUDS

OUDS means "Orange Unified Design System". This is a new design system, again, but _unified_, trying to merge all requirements of Orange brands and affiliates so as to provide a unique design system, unified across all platforms and for all countries, companies, users and apps. Guidelines for TV, Android, iOS and web environments will be merged in a "cohesive" approach, and any Orange-related softwares including brand apps like Parnasse and Sosh, *Orange Innovation Cup* apps and Orange countries and affiliates app will use this project in the future. The project is open source and topics like accessibility and ecodesign are also managed. It should replace internal frameworks and also [ODS](https://github.com/Orange-OpenSource/ods-ios) in the near future.

## Bugs and feature requests

Have a bug or a feature request? Please first search for existing and closed issues. If your problem or idea is not addressed yet, [please open a new issue](https://github.com/Orange-OpenSource/ouds-ios/issues/new/choose).

## Contributing

Please read through our [contributing guidelines](https://github.com/Orange-OpenSource/ouds-ios/blob/main/.github/CONTRIBUTING.md). Included are directions for opening issues, coding standards, and notes on development. More technical details are available also in the [DEVELOP](https://github.com/Orange-OpenSource/ouds-ios/blob/main/.github/DEVELOP.md) file.

## Copyright and license

Code released under the [MIT License](https://github.com/Orange-OpenSource/ouds-ios/blob/main/LICENSE).
For images and other assets, please [refer to the NOTICE.txt](https://github.com/Orange-OpenSource/ouds-ios/blob/ain/NOTICE.txt).