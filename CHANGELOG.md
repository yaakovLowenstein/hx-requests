# Changelog

<!--next-version-placeholder-->

## v0.40.0 (2025-12-30)

### Feature

* Add support for nested subdirectories in hx_requests folder ([`e258c0e`](https://github.com/yaakovLowenstein/hx-requests/commit/e258c0e165b3eaf2eadf45beb77083dfbe848638))

### Documentation

* Add documentation for nested subdirectories in hx_requests folder ([`3a0662f`](https://github.com/yaakovLowenstein/hx-requests/commit/3a0662f0c87ab6d4e8fa63bfd88d3aa0f39f3f86))

## v0.39.0 (2025-10-28)

### Feature

* Just to update version 🤦 ([`6a8bd6f`](https://github.com/yaakovLowenstein/hx-requests/commit/6a8bd6f73ade6170984c7bb8f612a0f7c73289eb))

### Breaking

* The attribute `hx_requests_allow_additive` on `HtmxViewMixin` has been renamed to `use_global_hx_rules` and its default value changed from `False` to `True`. Update your views accordingly. ([`6a8bd6f`](https://github.com/yaakovLowenstein/hx-requests/commit/6a8bd6f73ade6170984c7bb8f612a0f7c73289eb))

## v0.38.2 (2025-10-27)

### Fix

* Fix wrong named attribute for allowed_hx_requests in HtmxViewMixin ([`764d8cb`](https://github.com/yaakovLowenstein/hx-requests/commit/764d8cb68543b4a054187ba4b9a5b7890bb2c167))

## v0.38.1 (2025-10-27)

### Fix

* Fix bug in HxRequests allowlist logic ([`bf5f4d3`](https://github.com/yaakovLowenstein/hx-requests/commit/bf5f4d39650674724568a6b5e13263985ab2aee7))

## v0.38.0 (2025-10-27)

### Feature

* Add security controls for requiring authentication ([`d43ce23`](https://github.com/yaakovLowenstein/hx-requests/commit/d43ce23943ddcb0a8406c6d8840d32f209c09cd7))
* Change security contorls to be on view and not hxrequest class ([`b35fb01`](https://github.com/yaakovLowenstein/hx-requests/commit/b35fb01d8b9498591a4a90987a889d8e64910a91))

### Breaking

* The new setting HX_REQUESTS_REQUIRE_AUTH defaults to True, meaning that all HxRequests now require an authenticated user by default. Existing projects must explicitly set HX_REQUESTS_REQUIRE_AUTH = False in their settings to restore the previous behavior of allowing unauthenticated HxRequests or add HX_REQUESTS_UNAUTHENTICATED_ALLOW to specify which HxRequests are allowed without authentication. ([`d43ce23`](https://github.com/yaakovLowenstein/hx-requests/commit/d43ce23943ddcb0a8406c6d8840d32f209c09cd7))
* The security controls for HxRequests have been reworked. Instead of defining allowed apps and urls on the HxRequest class, views can now define an allow list of HxRequest names that are permitted to be used in that view. ([`b35fb01`](https://github.com/yaakovLowenstein/hx-requests/commit/b35fb01d8b9498591a4a90987a889d8e64910a91))

### Documentation

* Docs for securing HxRequests via authentication ([`d632c41`](https://github.com/yaakovLowenstein/hx-requests/commit/d632c418fb5d031cc3e1955ee679a30ac45ef511))
* Update docs to reflect per-view HxRequest controls ([`0d147e1`](https://github.com/yaakovLowenstein/hx-requests/commit/0d147e1617c99bcff0e13c32ea868b2ef0642259))

## v0.37.2 (2025-10-24)

### Fix

* Strip app namespace from view names in urlname_from_request ([`c085240`](https://github.com/yaakovLowenstein/hx-requests/commit/c08524001c64c3fe9ad94bb9a3c341937ed0420c))

## v0.37.1 (2025-10-24)

### Fix

* Fix hx_name assignment in HtmxViewMixin ([`e8e0f42`](https://github.com/yaakovLowenstein/hx-requests/commit/e8e0f429e3a38ddd9888c24d0bb4adbbb3cc3aa6))

## v0.37.0 (2025-10-24)

### Feature

* Add security controls for HxRequests to enforce app boundaries ([`5fe7060`](https://github.com/yaakovLowenstein/hx-requests/commit/5fe7060cabc1027b3142fba9f3f12618ae4c5224))

### Breaking

* HxRequests are now restricted by default. Update settings and HxRequest classes to allow cross-app usage as needed. ([`5fe7060`](https://github.com/yaakovLowenstein/hx-requests/commit/5fe7060cabc1027b3142fba9f3f12618ae4c5224))

### Documentation

* Fix index ([`7bf28ca`](https://github.com/yaakovLowenstein/hx-requests/commit/7bf28cac0b8cfb0163b10a42e668359a5ac3fd8a))
* Update docs format ([`76dedb7`](https://github.com/yaakovLowenstein/hx-requests/commit/76dedb7476ca487c8cba182dfe2c5890d2f671c6))

## v0.36.2 (2025-08-27)

### Fix

* Set return types to HttpResponse in FormHxRequest ([`22cf268`](https://github.com/yaakovLowenstein/hx-requests/commit/22cf2682b00d2a278c15b2a44d01f677531208a6))

## v0.36.1 (2025-07-21)

### Fix

* Error handling when refreshing hx object on post ([`3049198`](https://github.com/yaakovLowenstein/hx-requests/commit/3049198be4e7d90e4cd15583a81fa768d9e3fb56))
* Error handling when refreshing hx object on post ([`9411c8b`](https://github.com/yaakovLowenstein/hx-requests/commit/9411c8b48625e555132a4b93bef87e9b2e3f43fc))

## v0.36.0 (2025-07-04)

### Feature

* Add use_current_url option to BaseHxRequest ([`919c833`](https://github.com/yaakovLowenstein/hx-requests/commit/919c83309cccefd45d780ea5f5d5a39aebd46622))

### Documentation

* Fix typos in docs ([`343dd46`](https://github.com/yaakovLowenstein/hx-requests/commit/343dd46fa1327527fe7f406c2dea34606ce36960))

## v0.35.5 (2025-03-20)

### Fix

* Add reference that views template is used by default ([`76e5cfd`](https://github.com/yaakovLowenstein/hx-requests/commit/76e5cfd12454cacbb3bd085aaf42778809f58256))

### Documentation

* Small changes ([`f1a8fd5`](https://github.com/yaakovLowenstein/hx-requests/commit/f1a8fd51a1ce6d17ed5cf20c81ce3601304cdfc1))
* Add to index ([`e50aa94`](https://github.com/yaakovLowenstein/hx-requests/commit/e50aa94de87cc7459fcd97999fc17cb16947fe73))
* Add link to demo site ([`ff492ce`](https://github.com/yaakovLowenstein/hx-requests/commit/ff492ce198017b101f1f847b764ba6dc6f2e3f51))
* Add docs about passing through GET parameters not as kwargs ([`ba9d938`](https://github.com/yaakovLowenstein/hx-requests/commit/ba9d938196d17fe0d52a000b33b064de44493ca0))

## v0.35.4 (2025-02-26)

### Fix

* Allow django greater than 3.2 ([`ea0cc49`](https://github.com/yaakovLowenstein/hx-requests/commit/ea0cc495806c8515eb8a2b965478c40d0ad46f9c))

### Documentation

* Fix language in use_modals.rst ([`c7a9015`](https://github.com/yaakovLowenstein/hx-requests/commit/c7a9015e62d3aab331de2da8fa30829c77fd5809))
* Fix type ([`fbfc080`](https://github.com/yaakovLowenstein/hx-requests/commit/fbfc0807549c766d63d8c1aebc9304628069b180))
* Add refresh context explanation ([`b035c1a`](https://github.com/yaakovLowenstein/hx-requests/commit/b035c1a0c60b3b003a7fb5a993d139c1a7191b48))
* Fix typo ([`4abdc81`](https://github.com/yaakovLowenstein/hx-requests/commit/4abdc8159d224d55e4fc2beef6796de1f4f4fe15))
* Add modal explanation ([`4735c70`](https://github.com/yaakovLowenstein/hx-requests/commit/4735c708ef82f96bb29ca4a992cf469385e356c9))
* Updates ([`43eade9`](https://github.com/yaakovLowenstein/hx-requests/commit/43eade987043230063c560791b11de37c797aaa4))
* Updates ([`ee79edb`](https://github.com/yaakovLowenstein/hx-requests/commit/ee79edbf16bd14029baed263783af63dcf3aa321))
* Explanation on the serialization process ([`059a67b`](https://github.com/yaakovLowenstein/hx-requests/commit/059a67b2862af0e3a7b6f11cf5c2f09b29d38698))
* Update to docs ([`e51ad14`](https://github.com/yaakovLowenstein/hx-requests/commit/e51ad14f3184d9a489b28f39f9c1776e4adffcac))
* Add explanation to top level index ([`ea934ed`](https://github.com/yaakovLowenstein/hx-requests/commit/ea934ed45e017cbbe566cc730eb59c16ce35ab5d))
* Add explanation for how HxRequests work ([`c6b9058`](https://github.com/yaakovLowenstein/hx-requests/commit/c6b905890075272fad53de9d19c9b7617d1acec5))
* Add how to opt out of views context ([`d53f4ab`](https://github.com/yaakovLowenstein/hx-requests/commit/d53f4abd78beddbef4fe987986ded0acd6dceff2))
* Fixup index ([`0759538`](https://github.com/yaakovLowenstein/hx-requests/commit/0759538b48223b5bb2aa2bdd4fe343d94f8b9179))
* Add more how tos ([`06f29f0`](https://github.com/yaakovLowenstein/hx-requests/commit/06f29f0342d5ada59a24afef173556879cabfc17))
* Add how to for GET params in POST request ([`b516c23`](https://github.com/yaakovLowenstein/hx-requests/commit/b516c235154b6139b11fe6375f5ea40ee3d1fb67))
* Add how to access hx object in template ([`9be215f`](https://github.com/yaakovLowenstein/hx-requests/commit/9be215f07d7f29cfcd96595d9ca9fea72ecbe017))
* Fixup ([`3add63f`](https://github.com/yaakovLowenstein/hx-requests/commit/3add63f9e4b397d4a8a808ba485c00bd280a3527))
* Add headers to how-tos ([`35b9445`](https://github.com/yaakovLowenstein/hx-requests/commit/35b9445e0348399659dc0d14c9e915b7dec691ac))
* Fixup how-to add add_context ([`7bc2f54`](https://github.com/yaakovLowenstein/hx-requests/commit/7bc2f541ab2c48de62f72395282ce25e341d3900))
* Fix typo in how_tos/delete.rst ([`15bbc14`](https://github.com/yaakovLowenstein/hx-requests/commit/15bbc144316f17b6f5d01f39feae5ebfcb52818e))
* Add how to form kwargs to index ([`97faaec`](https://github.com/yaakovLowenstein/hx-requests/commit/97faaecca2ea7af74864ed299b21a20753232393))
* Remove old form docs ([`8057c76`](https://github.com/yaakovLowenstein/hx-requests/commit/8057c76c8b5ccac0c17f21e9ac0563b4bb590f2e))
* Add how to for adding form kwargs ([`ca95966`](https://github.com/yaakovLowenstein/hx-requests/commit/ca95966be94b2e92b8209a496401bab7917aba1b))
* Remove quickstart guide ([`028b92e`](https://github.com/yaakovLowenstein/hx-requests/commit/028b92ec204ebaa521b203e13fd6bcda33fadeca))
* Add context how to - to index ([`178fd5f`](https://github.com/yaakovLowenstein/hx-requests/commit/178fd5f833f987de65fdaab6f247f800e4b28b6f))
* Add docs for how to add context to an HxRequest ([`21f01f5`](https://github.com/yaakovLowenstein/hx-requests/commit/21f01f54a375b130f4a695448174852c4d1ca6ed))
* Add note about use_full_path ([`8f7a90a`](https://github.com/yaakovLowenstein/hx-requests/commit/8f7a90a56d4fdca7f6617ba47b8857cc7cfc17fa))
* Add links to hx tags reference docs ([`fd61a4e`](https://github.com/yaakovLowenstein/hx-requests/commit/fd61a4e369ec2ed4ec21c847942018c94fc0de61))
* Redo hx tags reference ([`d4432a7`](https://github.com/yaakovLowenstein/hx-requests/commit/d4432a75622d8a8f41d11c8824a5c462b4aa764e))
* Redo config docs ([`48b5481`](https://github.com/yaakovLowenstein/hx-requests/commit/48b5481e9129bfb9a00a815b055548e8ce7beb1e))
* Update ([`bcc268b`](https://github.com/yaakovLowenstein/hx-requests/commit/bcc268ba44adbc7bfbdc2839baa9bfcea102d701))
* Update ([`7a5b64c`](https://github.com/yaakovLowenstein/hx-requests/commit/7a5b64c3876820aac5954a07e977530c89d94244))
* Updates ([`ece6130`](https://github.com/yaakovLowenstein/hx-requests/commit/ece61301a76d878ed1cd008ad4c4e81e0b9c63a5))
* Updates ([`ae29e0a`](https://github.com/yaakovLowenstein/hx-requests/commit/ae29e0a3f9063a96c3399ce6f62b2be957a1cd27))
* Remove old modals docs ([`c231335`](https://github.com/yaakovLowenstein/hx-requests/commit/c23133556cfbdfb6c6963914e390aee2063142a8))

## v0.35.3 (2025-02-09)

### Fix

* Refresh view object if refresh_view_context_on_post is True ([`881f36c`](https://github.com/yaakovLowenstein/hx-requests/commit/881f36ccc8e46302f703083819833c7179649cc4))

### Documentation

* Add how to use modals to the how tos ([#148](https://github.com/yaakovLowenstein/hx-requests/issues/148)) ([`0a49361`](https://github.com/yaakovLowenstein/hx-requests/commit/0a493616be811bb0dd0f57e922cbaf7bec9c85e5))
* Fix typo ([`6398c00`](https://github.com/yaakovLowenstein/hx-requests/commit/6398c009059560118aa59d6812d109886440922e))
* Update form tutorial ([`fc296b2`](https://github.com/yaakovLowenstein/hx-requests/commit/fc296b29e61459b6616d7d88196d58e299e10886))
* Add form tutorial to index ([`057e636`](https://github.com/yaakovLowenstein/hx-requests/commit/057e6363a8e47354764780860331ecd01a88e77a))
* Fix typos and mistakes in basic tutorial ([`5eaab46`](https://github.com/yaakovLowenstein/hx-requests/commit/5eaab4608850b2a3851192bc347c64f14d7bb8d2))
* Add form tutorial ([`734c05b`](https://github.com/yaakovLowenstein/hx-requests/commit/734c05bd9a77f325095b6d4f94ff7f20fdb93b7e))
* Add example directory structures to how to register hx-requests docs ([`2aaa64e`](https://github.com/yaakovLowenstein/hx-requests/commit/2aaa64e5ad9342e555fdd2666b128340b30c1536))

## v0.35.2 (2025-02-05)

### Fix

* Allow any 3.x version of python ([`8b8d2bd`](https://github.com/yaakovLowenstein/hx-requests/commit/8b8d2bdfc1f302d274b90e6c65eb7f225b604939))

## v0.35.1 (2025-02-05)

### Fix

* Revert close modal trigger name to what it was before ([`f2a6286`](https://github.com/yaakovLowenstein/hx-requests/commit/f2a6286d3fe6c40f0afec85d33e5b390e877f97d))

## v0.35.0 (2025-02-04)

### Fix

* Replace HXRequest with HxRequest in the documentation ([`dbde0fe`](https://github.com/yaakovLowenstein/hx-requests/commit/dbde0fe430a9876bc478f7161d07e9ffc23becd5))
* Rename HxRequest classes to be more semantic ([`03a4442`](https://github.com/yaakovLowenstein/hx-requests/commit/03a4442390abe7a170e0100412412c1de292fe22))

### Breaking

* Imports and references to the classes need to be updated. BaseHXRequest -> BaseHxRequest FormHXRequest -> FormHxRequest DeleteHxRequest -> DeleteHxRequest HXModal -> ModalHxRequest HXFormModal -> FormModalHxRequest ([`03a4442`](https://github.com/yaakovLowenstein/hx-requests/commit/03a4442390abe7a170e0100412412c1de292fe22))

## v0.34.0 (2025-02-04)

### Feature

* Use GET_template and GET_block for modal body ([`3c12f24`](https://github.com/yaakovLowenstein/hx-requests/commit/3c12f24a8d551efbe11db75e4849ef07494fc0ed))
* Add support for nested hx-requests in hx_requests dir ([`250b93c`](https://github.com/yaakovLowenstein/hx-requests/commit/250b93c24b7641e18e96304377c52649bb45a9e9))
* Add support for multiple blocks per template ([`627339e`](https://github.com/yaakovLowenstein/hx-requests/commit/627339e72adcfd3eb12be23cb78cd85161ddb41b))
* Add block list support when using a dict ([`dc6aec6`](https://github.com/yaakovLowenstein/hx-requests/commit/dc6aec6a5be5e471b8d1cead24ca1603c30879b5))

### Fix

* Pin poetry version to 1.8.5 in publish_package.yml ([`6c23de5`](https://github.com/yaakovLowenstein/hx-requests/commit/6c23de5366d01b343b2e75627bec53831fddc4a5))
* Fix new modal rendering method not working with invalid forms ([`478268a`](https://github.com/yaakovLowenstein/hx-requests/commit/478268a2de2bc9c5246d15898b6eca4ddf5be33f))


### Breaking

* Modals no longer use body_template and they render the html for the body and add it to the context instead of putting the body_template in the context. ([`3c12f24`](https://github.com/yaakovLowenstein/hx-requests/commit/3c12f24a8d551efbe11db75e4849ef07494fc0ed))

### Documentation

* Update modal docs ([`3e4b278`](https://github.com/yaakovLowenstein/hx-requests/commit/3e4b278f826a8981b7dd021c64b923d7767f53f6))
* Add docs on registering hx-requests ([`030b194`](https://github.com/yaakovLowenstein/hx-requests/commit/030b194257ea03e6f4a6b8ff89b27b8e91e8a0dd))
* Fix readme formatting ([`ad3b382`](https://github.com/yaakovLowenstein/hx-requests/commit/ad3b382cb624e2ac336f9ab8c4e2bad7b4e698a3))
* Remove installation guide ([`5721457`](https://github.com/yaakovLowenstein/hx-requests/commit/5721457d82f4fba43758052f28cd50a5f7663cbf))
* Add basic tutorial ([`68b4e65`](https://github.com/yaakovLowenstein/hx-requests/commit/68b4e6525f4a6c1778e78d3dc3d776dce22adaf6))

## v0.33.2 (2024-12-10)

### Fix

* Adjust POST_block type hints to reflect acceptable usage ([`90ab2f9`](https://github.com/yaakovLowenstein/hx-requests/commit/90ab2f90a2b63fd6cbee31286864dc51942bf89e))

### Documentation

* Add documentation for POST_block usage ([`b0f255c`](https://github.com/yaakovLowenstein/hx-requests/commit/b0f255c16d97371b96252eff90b89236a96833a7))

## v0.33.1 (2024-12-03)

### Fix

* Use base manager to get model instance ([`69de1d1`](https://github.com/yaakovLowenstein/hx-requests/commit/69de1d14b32c9790bca62ece772eb3d825c66dca))

### Documentation

* Replace black with ruff badge in readme ([`85c4f58`](https://github.com/yaakovLowenstein/hx-requests/commit/85c4f581d3a7161535f2c8c1103c96673c27d54e))
* README.md to reflect new CI ([`c56b7ff`](https://github.com/yaakovLowenstein/hx-requests/commit/c56b7ffdc80991bd9090201703b2f0ef2a43461b))

## v0.33.0 (2024-09-10)

### Breaking

* cleanup package versions ([`ed928a0`](https://github.com/yaakovLowenstein/hx-requests/commit/ed928a0049dadd4871c95404879dc0c7b1aa4e72))

### Documentation

* Update CHANGELOG.md ([`c537c8a`](https://github.com/yaakovLowenstein/hx-requests/commit/c537c8a97c2d8485325fe45fc087f5b064106844))

## v0.32.1 (2024-09-04)

### Fix

* Fix bug with get_views_context ([`f6ed918`](https://github.com/yaakovLowenstein/hx-requests/commit/f6ed918e4dbbf5cd4845da17a0d1174055fb2e1f))

## v0.32.0 (2024-09-04)

### Feature

* Add refresh_views_context_on_POST to BaseHXRequest ([`bce66bd`](https://github.com/yaakovLowenstein/hx-requests/commit/bce66bd7f6bf1121b60b25bde7f6aa7d8e3f9c58))

### Documentation

* Add docs for refresh_views_context_on_POST ([`723a491`](https://github.com/yaakovLowenstein/hx-requests/commit/723a491af621ec446edfc91c802e44295348304e))
* Add motivation page ([`1c0cd57`](https://github.com/yaakovLowenstein/hx-requests/commit/1c0cd5788ca688662e555382db41a7e3415b388a))

## v0.31.1 (2024-08-14)

### Fix

* Update changelog for breaking changes ([`8df969f`](https://github.com/yaakovLowenstein/hx-requests/commit/8df969f124f9cce3146df045e51a671ade8423c5))

## v0.31.0 (2024-08-14)

This version is a major update with lots of breaking changes. However, still only a minor version bump
because the package is still under development. Though, this release gets us closer to a mature package
and a 1.0.0 release

### Feature

* Add hx_url template tag ([`3c47bbb`](https://github.com/yaakovLowenstein/hx-requests/commit/3c47bbb6e0be54ce97c3291eda656d7031e1e523))
* Use RequestContext for hx_request context ([`b4e19fc`](https://github.com/yaakovLowenstein/hx-requests/commit/b4e19fccfcd1a29153df59db30a52d9cf78a3e1e))
* Change the way HXRequests are registered ([`ea2ee74`](https://github.com/yaakovLowenstein/hx-requests/commit/ea2ee742575534fce71e033e3e489b6608bf95b4))

### Fix

* Fix bug in HtmxViewMixin._get_hx_request_classes ([`e797a2e`](https://github.com/yaakovLowenstein/hx-requests/commit/e797a2ea5c47a144fdc547b3971ef86d64ad276a))
* Raise an exception if duplicate HxRequest names are found ([`7c9fa47`](https://github.com/yaakovLowenstein/hx-requests/commit/7c9fa47a2cdf51fada1e61adabe5f44de5c5caaa))

### Documentation

* Update docs to reflect changes in messages setting ([`5865870`](https://github.com/yaakovLowenstein/hx-requests/commit/5865870ecee3d4dd9f72c7d39adf5a28c02ec841))
* Update docs for delete HX request ([`6c6b94b`](https://github.com/yaakovLowenstein/hx-requests/commit/6c6b94bdaf0d769fc168828d3dc3b3d2463becb8))

### Breaking

* hx_requests no longer have an extra_context attribute.
* The hx_messages module has been removed.
    Messages are now set using Django's messaging framework.
    The HXMessages class has been removed and the messages attribute
    has been removed from the BaseHxRequest class. Messages are
    now set using Django's messages module.

    `self.messages.success()` has been replaced with`messages.success(request, message)`
    and the same for `self.messages.error()`, `self.messages.warning()`,
    `self.messages.info()` and `self.messages.debug()`. ([`35caf9a`](https://github.com/yaakovLowenstein/hx-requests/commit/35caf9a58ae4a5eee78c7de8200bff177bc13e29))
* `DeleteHXRequest`'s `handle_delete` has been updated to `delete`. If you have overridden `handle_delete`
    in your `DeleteHXRequest`, you will need to change it to `delete`. ([`4022933`](https://github.com/yaakovLowenstein/hx-requests/commit/4022933d26db5d649eba12efa1346fd296ea29f0))
* modalFormValid is renamed to closeHxModal. All trigger's of modalFormValid need to be replaced with closeHxModal.
    The modal template as well will need to be updated to handle closeHxModal.(and if using Alpin.js modal-form-valid
    needs to be changed to close-hx-modal) ([`786c6a3`](https://github.com/yaakovLowenstein/hx-requests/commit/786c6a334d5227bc7d158f58bdbe609422080e37))
* The render_hx template tag has been removed.
    It has been replaced by the hx_get and hx_post template tags.
    The hx_get and hx_post template tags are more explicit
    and easier to understand. The render_hx template tag was
    confusing and not as clear as the hx_get and hx_post template tags. ([`0018ca5`](https://github.com/yaakovLowenstein/hx-requests/commit/0018ca563170d9cd9100b80ce9c26c139d856afe))
* `get_post_context_data` has been renamed to `get_context_on_POST` for consistency with the other methods. ([`971ec74`](https://github.com/yaakovLowenstein/hx-requests/commit/971ec74d0e07e2c94b83fcc425ae9ca30395dfb8))
* Underscores have been added to private methods
    in the hx_requests module.

    setup_hx_request -> _setup_hx_request
    render_templates -> _render_templates
    get_messages_html -> _get_messages_html
    get_response -> _get_response ([`7af28b3`](https://github.com/yaakovLowenstein/hx-requests/commit/7af28b3f2316321b247babf75679e9e6dc52ff42))
* Default message setting was moved from the post method to form_valid and form_invalid.
  Therefore if form_valid or form_invalid are overridden messages need to be explicitly set
  in those methods. ([`bcf9df2`](https://github.com/yaakovLowenstein/hx-requests/commit/bcf9df2758830d055d4b796558ac62ede4b71057))
* The way the view's context is added to the hx-request's context has changed. The new way is more efficient but is also breaking.
  The view's context is now setup prior to the form_valid. Therefore updates in the form_valid will not be reflected
  in the context of the POST_template. To refresh the view's context for the POST_template, set refresh_views_context_on_POST to True.
  **Note**: This is only really needed in detail views. List views use querysets which are lazy evaluated and therefore do pick up
            on changes made in form_valid. The detail view uses a model instance and therefore is evaluated.
## What's Changed
* Major Changes by @yaakovLowenstein in https://github.com/yaakovLowenstein/hx-requests/pull/102


**Full Changelog**: https://github.com/yaakovLowenstein/hx-requests/compare/v0.30.0...v0.31.0

## v0.30.0 (2024-08-09)

### Feature

* Add get_context_on_GET ([`d31f4e6`](https://github.com/yaakovLowenstein/hx-requests/commit/d31f4e67bfe0a58e57394d5ef8af01a37f8f631e))

## v0.29.3 (2024-07-25)

### Fix

* Fix bug with triggers ([`44e9edf`](https://github.com/yaakovLowenstein/hx-requests/commit/44e9edfa63473efb3fa1a833e9d965985c8eb8a5))

## v0.29.2 (2024-07-18)

### Fix

* Reset swap type when form invalid ([`0f51bf4`](https://github.com/yaakovLowenstein/hx-requests/commit/0f51bf42f7d5f6e9e4c8a5216b13a4c362185d8d))

## v0.29.1 (2024-07-17)

### Fix

* Update django-render-block to 0.10 ([`4084ccc`](https://github.com/yaakovLowenstein/hx-requests/commit/4084ccc2e341c3f8e7351f132d76c78233cc1a4f))

## v0.29.0 (2024-07-10)

### Feature

* Move view's get call to the hx_request ([`7e79422`](https://github.com/yaakovLowenstein/hx-requests/commit/7e794225694ff2b2b2cae479dd17f4a2417554fc))

### Breaking

* Everything should work as before, however it is breaking because the setup_hx_request function now has parameters for *args and **kwargs. These are the view's args and kwargs and are needed to setup the view from the hx_request ([`7e79422`](https://github.com/yaakovLowenstein/hx-requests/commit/7e794225694ff2b2b2cae479dd17f4a2417554fc))

## v0.28.1 (2024-05-15)

### Fix

* Fix get_triggers method in FormModalHxRequest class when form is invalid ([`df23c7a`](https://github.com/yaakovLowenstein/hx-requests/commit/df23c7a528e834277c86da29d396c5703ba3cdce))

## v0.28.0 (2024-05-02)

### Feature

* Json serialize date, datetime, decimal ([`8a4db23`](https://github.com/yaakovLowenstein/hx-requests/commit/8a4db236eee07e8594014ff16fd67f0358b40faf))

## v0.27.2 (2024-03-29)

### Fix

* Fix bug with modal_template ([`6924cdc`](https://github.com/yaakovLowenstein/hx-requests/commit/6924cdc64f58de9e8dedc3708e8e174c6f4a1528))

## v0.27.1 (2024-03-29)

### Fix

* Fix bug with misnamed variable ([`154a119`](https://github.com/yaakovLowenstein/hx-requests/commit/154a119fe43e37c5a80c061bd3564c05655e3616))

## v0.27.0 (2024-03-29)

### Feature

* Remove modal templates ([`c27e317`](https://github.com/yaakovLowenstein/hx-requests/commit/c27e3174fb7063829175c46942668017d262ecdf))
* Add the ability to set the modal title and body classes ([`e8037ba`](https://github.com/yaakovLowenstein/hx-requests/commit/e8037ba2188faf37f2778ea22111ec259cd20504))

### Fix

* Use body_template instead of GET_template for ModalHxRequest ([`f28723e`](https://github.com/yaakovLowenstein/hx-requests/commit/f28723ea3cb1b341e1e7e48544d99af9c2b4377f))
* Change HX_REQUESTS_MODAL_BODY_SELECTOR to HX_REQUESTS_MODAL_BODY_ID ([`b79abde`](https://github.com/yaakovLowenstein/hx-requests/commit/b79abde9e0067579872833605a19cec4d09eb105))

### Breaking

* The default modal templates have been removed. You will need to create your own modal templates if you want to use the modal functionality. See the docs for more information. ([`c27e317`](https://github.com/yaakovLowenstein/hx-requests/commit/c27e3174fb7063829175c46942668017d262ecdf))
* The GET_template is no longer used for the ModalHxRequest. Instead the body_template is used. What was previously set as GET_template should now be set as body_template. ([`f28723e`](https://github.com/yaakovLowenstein/hx-requests/commit/f28723ea3cb1b341e1e7e48544d99af9c2b4377f))
* HX_REQUESTS_MODAL_BODY_SELECTOR is now HX_REQUESTS_MODAL_BODY_ID and the default is now #hx_modal_body. (set hx_modal_body as the html id on the modal body) ([`b79abde`](https://github.com/yaakovLowenstein/hx-requests/commit/b79abde9e0067579872833605a19cec4d09eb105))

### Documentation

* Update docs for modals ([`25ce372`](https://github.com/yaakovLowenstein/hx-requests/commit/25ce372535bcff29643809182cca0e1ab42a9875))

## v0.26.2 (2024-03-26)

### Fix

* Fix issue with lists in GET params ([`a83fada`](https://github.com/yaakovLowenstein/hx-requests/commit/a83fadaeb24b9b2a9b6ede94cc5cec2cb8a43f3e))

## v0.26.1 (2024-03-25)

### Fix

* Fix issue with extra_context overriding regular context ([`cd955c7`](https://github.com/yaakovLowenstein/hx-requests/commit/cd955c70223efa13e96ed5a8d68d23ad8fb2ff04))

## v0.26.0 (2024-03-21)

### Feature

* Add kwargs_as_context option to BaseHxRequest ([`8eecaa6`](https://github.com/yaakovLowenstein/hx-requests/commit/8eecaa61bcbcfeab6a7d2774fd794711ccbcd285))

### Breaking

* kwargs will now be added to the context directly by default. If you do not want this, you can set kwargs_as_context to False. Any code that relies on kwargs being in the hx_kwargs context variable will need to be updated to use the new context. For example, if you were doing `hx_kwargs.some_key` in the template you will need to change it to `some_key` OR set kwargs_as_context to False. ([`8eecaa6`](https://github.com/yaakovLowenstein/hx-requests/commit/8eecaa61bcbcfeab6a7d2774fd794711ccbcd285))

### Documentation

* Update docs ([`13ce5fd`](https://github.com/yaakovLowenstein/hx-requests/commit/13ce5fd94e37fa8d8fc5fec3f8b3f86735de6437))

## v0.25.0 (2024-03-11)

### Feature

* Add option to set initial in form from kwargs ([`b140786`](https://github.com/yaakovLowenstein/hx-requests/commit/b140786b26167ee5c257c2f6d7ec431c794a66f2))

## v0.24.0 (2024-03-11)

### Feature

* Add method to set HX-Trigger ([`a66efcf`](https://github.com/yaakovLowenstein/hx-requests/commit/a66efcf94665256fe20696e25e5ee15ef902c28e))

## v0.23.1 (2024-03-11)

### Fix

* Fix the way serialization is being done ([`f510a53`](https://github.com/yaakovLowenstein/hx-requests/commit/f510a531c36a283bb9dfdba7a62e2f398f7d0e9d))

## v0.23.0 (2024-03-05)

### Feature

* Change message tag to tags and add __str__ method to Message ([`c006405`](https://github.com/yaakovLowenstein/hx-requests/commit/c006405ab5b77e4b4bc6705ec73c7c39fc1ebac8))

## v0.22.0 (2024-03-04)

### Feature

* Only call get_context_data if the view defines one ([`d904b12`](https://github.com/yaakovLowenstein/hx-requests/commit/d904b12c846b1b8befa9bc85a4762b9ff71af463))
* Add opt-out for views context `get_views_context` ([`9df3c17`](https://github.com/yaakovLowenstein/hx-requests/commit/9df3c17e5b223cad9010f879d482c5e6d0155cb7))
* Change the way 'gets' are handled ([`881b596`](https://github.com/yaakovLowenstein/hx-requests/commit/881b596ad53dec40ee78bd311fc71693493ae214))

### Documentation

* Add documentation for get_views_context ([`df4e689`](https://github.com/yaakovLowenstein/hx-requests/commit/df4e689282e019dc41f91cbfa002b8df2f62f168))
* Add documentation about setting up views' gets ([`857e522`](https://github.com/yaakovLowenstein/hx-requests/commit/857e522366e589f94af612ea41fc5ad937b666ab))

## v0.21.0 (2024-02-29)

### Feature

* Add support for using a dict for blocks ([`eed8baf`](https://github.com/yaakovLowenstein/hx-requests/commit/eed8baf471928f0846f8136921db42d8b1a7108c))

### Documentation

* Update README.md contributing section ([`4e65870`](https://github.com/yaakovLowenstein/hx-requests/commit/4e6587065a4e13daf0673fe739d96cbb20c7e34b))
* Add a docstring to the render_templates method ([`dfc8a31`](https://github.com/yaakovLowenstein/hx-requests/commit/dfc8a316d65ff9a9609b7023d987c5b085d6ee2e))
* Add more examples for out-of-band swaps ([`88d7805`](https://github.com/yaakovLowenstein/hx-requests/commit/88d78052f446f00add9c0788b1b6354e3dc53920))

## v0.20.4 (2024-02-27)

### Fix

* Fix bug that the views kwargs were not passed to get_context_data ([`4083e5c`](https://github.com/yaakovLowenstein/hx-requests/commit/4083e5c6a17c1552ca828d5fd0dfead2291f28ec))

## v0.20.3 (2024-02-23)

### Fix

* Fix a couple of bugs in get_url ([`5f388d8`](https://github.com/yaakovLowenstein/hx-requests/commit/5f388d8c8741fbd639a7cd25f5c75f341f55e29e))

## v0.20.2 (2024-02-12)

### Fix

* Fix bug with url kwargs ([`8b38ef6`](https://github.com/yaakovLowenstein/hx-requests/commit/8b38ef6cb91c410053dbad471e126078f8fe846e))

## v0.20.1 (2024-02-09)

### Fix

* Fix bugs in serialization and with use_full_path ([`a429e89`](https://github.com/yaakovLowenstein/hx-requests/commit/a429e89eed2897bc97a7b3515d16083b9b2d3466))

### Documentation

* Use html+django for syntax highlighting in html code blocks ([`7d4aca0`](https://github.com/yaakovLowenstein/hx-requests/commit/7d4aca0db6aaf0fd830ed63ca1ddf0804f2a043c))

## v0.20.0 (2024-02-09)

### Feature

* Allow multiple templates and blocks to be passed in ([`a48a179`](https://github.com/yaakovLowenstein/hx-requests/commit/a48a179aa894cac24f7383c95a6ff475c4032111))

### Documentation

* Add documentation for out-of-band ([`76a3f49`](https://github.com/yaakovLowenstein/hx-requests/commit/76a3f497a4de889ff9562c6429232c351138ffb7))

## v0.19.0 (2024-02-08)

### Feature

* Pass extra kwargs to hx request setup ([`8551bab`](https://github.com/yaakovLowenstein/hx-requests/commit/8551babc28ddd4f76923e4a5425dfdaabb0e7315))
* Route hx request directly to hx request handler ([`a053727`](https://github.com/yaakovLowenstein/hx-requests/commit/a053727ad38b32ed7be7e4c892148c9411ac4d7c))

### Fix

* Update kwargs with extras instead overriding ([`392452f`](https://github.com/yaakovLowenstein/hx-requests/commit/392452fe35890aefa2556ea7a28a4e41f0f57b72))

## v0.18.4 (2024-02-08)

### Fix

* Remove View inheritance from HtmxViewMixin ([`64fa163`](https://github.com/yaakovLowenstein/hx-requests/commit/64fa163fc197853e5394c6aa23e9823f69b0ccf0))

### Documentation

* Update view docs ([`9fa8f01`](https://github.com/yaakovLowenstein/hx-requests/commit/9fa8f0134c45d3c4d030fab5e8f2f757ece36b23))

## v0.18.3 (2024-02-08)

### Fix

* Exception when missing csrf ([`0c49042`](https://github.com/yaakovLowenstein/hx-requests/commit/0c49042bd723e34148cb20d64e846ebd92a574a6))

## v0.18.2 (2024-02-07)

### Fix

* Remove object from persisting with use_full_path ([`043fbb0`](https://github.com/yaakovLowenstein/hx-requests/commit/043fbb070ca3d4fec697001fa7bf9c81aef6cdf5))

## v0.18.1 (2024-01-16)

### Fix

* Fix issue in get_url where it would not properly handle query params ([`608195c`](https://github.com/yaakovLowenstein/hx-requests/commit/608195c37ed79ca6a52ed562c382f29723125fa5))

## v0.18.0 (2024-01-11)

### Feature

* Default GET and POST templates to view template ([`f24c307`](https://github.com/yaakovLowenstein/hx-requests/commit/f24c30765939cf9d385d516650b8be6c229744c3))

### Fix

* Give default value to HX_REQUESTS_USE_DJANGO_MESSAGE_TAGS ([`82c457c`](https://github.com/yaakovLowenstein/hx-requests/commit/82c457cf189b694c62ecd9e4f02a46b0101b9bd5))

## v0.17.0 (2024-01-11)

### Feature

* Add ability for hx url to use the full path (Includes query params) ([`d500ebb`](https://github.com/yaakovLowenstein/hx-requests/commit/d500ebb1ae23b72f7b4085da4caf08a313f30bf0))

## v0.16.1 (2023-11-09)

### Fix

* Fix bug in close_modal_on_save ([`2d264c5`](https://github.com/yaakovLowenstein/hx-requests/commit/2d264c535109913875c7b736457e846e2f0e2a5c))

## v0.16.0 (2023-11-09)

### Feature

* Revert "feat: Add new attributes to FormHxRequest and FormModal" ([`2990cf5`](https://github.com/yaakovLowenstein/hx-requests/commit/2990cf572bc654e64f728a47def5a4de1b10a19b))

### Fix

* Add back in close_modal_on_save ([`b4a18ab`](https://github.com/yaakovLowenstein/hx-requests/commit/b4a18ab0aebb4c7d05c41555c10d5c7094d88c76))

## v0.15.1 (2023-11-08)

### Fix

* Add a way to add context to body of modal ([`5045fb4`](https://github.com/yaakovLowenstein/hx-requests/commit/5045fb4dc81525fe6a1fbcef18d89b90aaef22f2))

## v0.15.0 (2023-10-06)

### Feature

* Fix semantic release by pinning version ([`af203cc`](https://github.com/yaakovLowenstein/hx-requests/commit/af203cc308f6be15c8acfb4e2d7b73be675679e8))
* Add new attributes to FormHxRequest and FormModal ([`572ce7f`](https://github.com/yaakovLowenstein/hx-requests/commit/572ce7f6d82fb0b019a52213e3057889685c5fa9))

### Fix

* Version bump commit ([`66e5492`](https://github.com/yaakovLowenstein/hx-requests/commit/66e54927bfe8b6c2810a275ef9606696724fa80c))

## v0.14.3 (2023-07-11)

### Fix

* Fix bug when no csrftoken ([`06bbfd2`](https://github.com/yaakovLowenstein/hx-requests/commit/06bbfd2ebb7c86f6dcee50cccb20000f275e18ee))

## v0.14.2 (2023-05-25)
### Fix
* Group docs dependencies separately ([`e5ea4ef`](https://github.com/yaakovLowenstein/hx-requests/commit/e5ea4ef6228bf79ab44a1dfe43051ed1c07e67f2))

## v0.14.1 (2023-05-25)
### Fix
* Remove stale code ([`597a13e`](https://github.com/yaakovLowenstein/hx-requests/commit/597a13e317ea47492f626e0a062a9b42c0925441))

### Documentation
* Documentation edits ([`b15f176`](https://github.com/yaakovLowenstein/hx-requests/commit/b15f176da3defaa77be9230c64ae49394406a6ac))

## v0.14.0 (2023-05-19)
### Feature
* Using django-render-block give the option to just return a block ([`dceca31`](https://github.com/yaakovLowenstein/hx-requests/commit/dceca3197230cc5a4b0dfae05a047e62de416bdd))

### Documentation
* Remove contributing from read the docs ([`f39acce`](https://github.com/yaakovLowenstein/hx-requests/commit/f39accebd93fa9e468cc493f59671b043c620add))
* Fix typos ([`6f90f4b`](https://github.com/yaakovLowenstein/hx-requests/commit/6f90f4bfa85c4093709ba0646b836c22a0fa0a20))
* Add docs about rendering a block ([`204577c`](https://github.com/yaakovLowenstein/hx-requests/commit/204577cef0351cea31eb81ffdd2ced63b529c9bc))

## v0.13.2 (2023-05-19)
### Fix
* Fix typo in setting name ([`71eda85`](https://github.com/yaakovLowenstein/hx-requests/commit/71eda85edd7c74602e3485b2d0bd9f210c051b45))

### Documentation
* Fix wrong path to modal ([`ab394aa`](https://github.com/yaakovLowenstein/hx-requests/commit/ab394aa07d307b36bc524e69991ad037f81e461d))

## v0.13.1 (2023-05-18)
### Fix
* Fix bug in modal due to no body selector ([`2512f8f`](https://github.com/yaakovLowenstein/hx-requests/commit/2512f8f1ef8c2adaf31c1be8884a3bd8c25c3961))

## v0.13.0 (2023-05-18)
### Feature
* Add custom modal template ([`1b42cef`](https://github.com/yaakovLowenstein/hx-requests/commit/1b42cef0412fdc603411b4e34b1761a3987c257d))

### Fix
* Fix type ([`fe56758`](https://github.com/yaakovLowenstein/hx-requests/commit/fe56758e9dd42627fdf824c5ea20654a6b6181ef))

### Documentation
* Update to docs to reflect new custom modal ([`fc8af97`](https://github.com/yaakovLowenstein/hx-requests/commit/fc8af972a947545d5025be325be566db1fa112c4))

## v0.12.0 (2023-05-16)
### Feature
* Add hx_get and hx_post templatetags ([`471ed08`](https://github.com/yaakovLowenstein/hx-requests/commit/471ed086ece3ae8a16819d8229f52896428e9650))

### Fix
* When passing in body to modal via template tag use mark_safe ([`d471261`](https://github.com/yaakovLowenstein/hx-requests/commit/d471261ad908f7001b37fc9ac03e6a0192715d56))

### Documentation
* Fix references to old methods ([`7972387`](https://github.com/yaakovLowenstein/hx-requests/commit/797238781d45f74856f1f6d64362aa3a536455f0))

## v0.11.2 (2023-05-11)
### Fix
* Cast kwarg value to string ([`8bcb072`](https://github.com/yaakovLowenstein/hx-requests/commit/8bcb072593813ec1d1a206fb78f66f409742e95b))

## v0.11.1 (2023-05-11)
### Fix
* Fix bug that wasn't urlencoding the kwargs ([`acb74c2`](https://github.com/yaakovLowenstein/hx-requests/commit/acb74c26d386e2ff916803b118238a77170beea7))

## v0.11.0 (2023-05-11)
### Feature
* Empty commit to bump version ([`b467c81`](https://github.com/yaakovLowenstein/hx-requests/commit/b467c81f3a4c0348afff1f8df76872cf090577b4))

### Documentation
* Test again for autodoc ([#4](https://github.com/yaakovLowenstein/hx-requests/issues/4)) ([`b8c36e5`](https://github.com/yaakovLowenstein/hx-requests/commit/b8c36e51902808a2dd7977aa9587b2cba20bb874))
* Retry autodocs ([`c9ec154`](https://github.com/yaakovLowenstein/hx-requests/commit/c9ec154760586a495c8b6a952e18b71450cc46fc))
* Retry ([`2ebcb83`](https://github.com/yaakovLowenstein/hx-requests/commit/2ebcb8325d48ec2075f5e9c5f46dd027ef9bcce3))
* Add sphinx-autodoc-api ([`1d28e8a`](https://github.com/yaakovLowenstein/hx-requests/commit/1d28e8aa70940ba8e143a9a778c462e12fa395bf))
* Testing readthedocs ([`ffaf095`](https://github.com/yaakovLowenstein/hx-requests/commit/ffaf0954add15596bf5f4160b18a1099dd98bca5))
* Trying to get readthedocs to work with docstrings ([`de14adc`](https://github.com/yaakovLowenstein/hx-requests/commit/de14adcce22ef59b6b0b0222607f815fc158905e))
* Trying to get readthedocs to recognize docstrings ([`680fc98`](https://github.com/yaakovLowenstein/hx-requests/commit/680fc9887d35bb1c2d02274379d188a198c01559))
* Add requirements and yml for readthedocs ([`f50a7b3`](https://github.com/yaakovLowenstein/hx-requests/commit/f50a7b3004f38c0b059328850c2669768bc92d3b))
* Fix typo in quickstart ([`8d03c06`](https://github.com/yaakovLowenstein/hx-requests/commit/8d03c06c44f6ecbe54f462be7623961b2c02f32c))
* Add reference documentation for DeleteHxRequest ([`58fe070`](https://github.com/yaakovLowenstein/hx-requests/commit/58fe070c30b2ee2c7d764ce64df3a8cdb72cf787))
* Add in docstrings for FormHxRequest ([`558bac8`](https://github.com/yaakovLowenstein/hx-requests/commit/558bac8230f2ecf8d34b54544339e2664aa94352))
* Add reference docs for FormHxRequest ([`263c533`](https://github.com/yaakovLowenstein/hx-requests/commit/263c533c1d2b166957a77c52c91c1cbf30f3a0c7))

## v0.10.2 (2023-05-02)
### Fix
* Update lock file based on changes to toml ([`deb6f79`](https://github.com/yaakovLowenstein/hx-requests/commit/deb6f796ca186836dbc2fd3ea11a9b26a524784f))

## v0.10.1 (2023-05-02)
### Fix
* Move sphinx to a dev dependency ([`a47885c`](https://github.com/yaakovLowenstein/hx-requests/commit/a47885c701f3de3ed1819c5e7dc6cd426dccc19e))

## v0.10.0 (2023-05-02)
### Feature
* Merge HXRequestsGET and HXRequestPOST into one base class ([`9557070`](https://github.com/yaakovLowenstein/hx-requests/commit/95570704acc4428bcd9865320aaba3a9505fe721))

### Fix
* Move resfresh object into get_post_context_data ([`77c0621`](https://github.com/yaakovLowenstein/hx-requests/commit/77c06217158747c3d48d9521b9c134469d7f6af7))

### Documentation
* Update docs for merging of get and post into one base class ([`37b8b4c`](https://github.com/yaakovLowenstein/hx-requests/commit/37b8b4cb833f93c067585d780d951e16147c0d32))
* Add section on hx tags ([`325eecb`](https://github.com/yaakovLowenstein/hx-requests/commit/325eecb711d5f87ab1fbc6d157039f100a8c675c))
* Add section on messages ([`85076f8`](https://github.com/yaakovLowenstein/hx-requests/commit/85076f8f70a91fa0af576cef1811153e64c95b69))
* Fix up README ([`47feddc`](https://github.com/yaakovLowenstein/hx-requests/commit/47feddc521281fd4a0cc6431ed1508b34886b676))
* Update README ([`a8a0b54`](https://github.com/yaakovLowenstein/hx-requests/commit/a8a0b54e8da1cd4bdfc34bcd17d618698bacfa49))
* Finish up modal docs ([`135bd23`](https://github.com/yaakovLowenstein/hx-requests/commit/135bd23644e54f821a3d183e6e77e7e7febe3627))
* Add docs on deleting ([`4bb7100`](https://github.com/yaakovLowenstein/hx-requests/commit/4bb71007e649048c5938de8f9eaf8bfce74512e9))
* Finish up Using Forms and add stub for settings ([`fccadb0`](https://github.com/yaakovLowenstein/hx-requests/commit/fccadb055eea9ec2e113c17711a28cb68dee269d))
* Start on forms documentation ([`8e51494`](https://github.com/yaakovLowenstein/hx-requests/commit/8e5149415499ac0ce09d956257ea5cc777e1e8ce))
* Write up quickstart docs ([`411dc14`](https://github.com/yaakovLowenstein/hx-requests/commit/411dc14474b160e7ae0ac01163cbc433dfe69d93))
* Outline the docs ([`bf37ef4`](https://github.com/yaakovLowenstein/hx-requests/commit/bf37ef4f2c58739c85af8484aec1d84fe7c516fe))
* Add docs on installation ([`6c472da`](https://github.com/yaakovLowenstein/hx-requests/commit/6c472da66ce92aa5edd48b45da5ed209ae0b7724))
* Change theme to sphinx_rtd_theme ([`d81d9ca`](https://github.com/yaakovLowenstein/hx-requests/commit/d81d9ca422b9ed7116f3295123ff77734328ad97))
* Run sphinx quickstart to start off documentation ([`01180ee`](https://github.com/yaakovLowenstein/hx-requests/commit/01180eeed1d0582a15f24a3b55e5c02104189080))

## v0.9.0 (2023-04-10)
### Feature
* Clean up code in views ([`5fdfc65`](https://github.com/yaakovLowenstein/hx-requests/commit/5fdfc650926f16a27e53a5df1b5fce54f302e31c))

## v0.8.0 (2023-04-10)
### Feature
* Add better exception message for not finding an hx_request ([`d8da795`](https://github.com/yaakovLowenstein/hx-requests/commit/d8da7954c98aaa2b36ca73519336f8809ce90a6f))

## v0.7.2 (2023-04-10)
### Fix
* Fix issue with no_swap when form is invalid ([`a9e0ae1`](https://github.com/yaakovLowenstein/hx-requests/commit/a9e0ae1332ccfa53a9ed2761ff6b6b9b40e12a5e))

## v0.7.1 (2023-04-10)
### Fix
* Updates to modal ([`be36e2f`](https://github.com/yaakovLowenstein/hx-requests/commit/be36e2f03ef4495f0974b398da11b1cc8b6b46ba))
* Fix 🐛 that was not usign modal wrapper id in close modal js ([`4d2ab88`](https://github.com/yaakovLowenstein/hx-requests/commit/4d2ab88f2b387157cda685e28b287f32a7825f50))

## v0.7.0 (2023-04-09)
### Feature
* Add ability to not do a swap in Post request ([`5838114`](https://github.com/yaakovLowenstein/hx-requests/commit/5838114b59ff79c8d1b083818f7ca6f3456167d3))

## v0.6.2 (2023-04-09)
### Fix
* Add default for modal body selector ([`1196807`](https://github.com/yaakovLowenstein/hx-requests/commit/119680745e14f55551fcaf7980a524c231554bbc))

## v0.6.1 (2023-04-09)
### Fix
* Fix bugs in modal ([`7bcc85a`](https://github.com/yaakovLowenstein/hx-requests/commit/7bcc85a6e1c4b8acc2debb74b09e7d84bff1a8fe))
* Refactor close modal js ([`8dcfd46`](https://github.com/yaakovLowenstein/hx-requests/commit/8dcfd46de3e774edcbaeed7dba23074bc2d49b0a))

## v0.6.0 (2023-04-05)
### Feature
* Change the way messages are handled ([`360beac`](https://github.com/yaakovLowenstein/hx-requests/commit/360beac06c0b838b68b761d762e92cfa2e89708b))

## v0.5.3 (2023-04-04)
### Fix
* Fix bug in js ([`21be816`](https://github.com/yaakovLowenstein/hx-requests/commit/21be816444d1b4984f0c93d32afcdd8ec3ecc08b))

## v0.5.2 (2023-04-04)
### Fix
* Remove extra '?' ([`bbdf063`](https://github.com/yaakovLowenstein/hx-requests/commit/bbdf063cd23f11f70fc9139a059c9908f34a42d9))

## v0.5.1 (2023-04-04)
### Fix
* Fix ternary in messages_alerts js ([`ca05b00`](https://github.com/yaakovLowenstein/hx-requests/commit/ca05b00bfd029622e78c2dfc2590783318cb80f0))
* Fix 🐛 in messages_alerts js ([`e95605b`](https://github.com/yaakovLowenstein/hx-requests/commit/e95605bb5773d0c5d2cf799dc94f3cc170272b0c))

## v0.5.0 (2023-04-04)
### Feature
* Add new messages template for alerts ([`daa774f`](https://github.com/yaakovLowenstein/hx-requests/commit/daa774fba5015f64b5b3d8b39b478e76ccfe087f))

## v0.4.6 (2023-04-04)
### Fix
* Move js vars in messages so that they are not global ([`a9e0370`](https://github.com/yaakovLowenstein/hx-requests/commit/a9e0370de1535b9fa404f746891495493efc02a4))
* Change level to tag in hx messages ([`7111e22`](https://github.com/yaakovLowenstein/hx-requests/commit/7111e22dc87debde68b9448213cfe80be5384c69))
* Remove nested hx messages settings ([`046e8e2`](https://github.com/yaakovLowenstein/hx-requests/commit/046e8e2059a68b590ebe7a4832da4f800ea8b628))

## v0.4.5 (2023-04-02)
### Fix
* Fix show_messages bool not being used when form is invalid ([`a16c21c`](https://github.com/yaakovLowenstein/hx-requests/commit/a16c21c96dbf2c74d8df93320c6a7d3e4c1f509c))

## v0.4.4 (2023-04-02)
### Fix
* Fix bug in messages.html was appening alert twice ([`e5db88f`](https://github.com/yaakovLowenstein/hx-requests/commit/e5db88f493b133471bf2cbce0210e73d1e74a614))
* Fix bug in hx_requests that not checking self.show_messages ([`3749519`](https://github.com/yaakovLowenstein/hx-requests/commit/37495191d3c52b634cb0c2e8b7295edb4fb7facc))
* Add to error message for not having message_tags defined ([`59cb447`](https://github.com/yaakovLowenstein/hx-requests/commit/59cb447f6307ff32a7e783a012b6783fe2a127fa))

## v0.4.3 (2023-04-02)
### Fix
* Fix bug in init of HXMessages ([`7f9367d`](https://github.com/yaakovLowenstein/hx-requests/commit/7f9367da9c093ca220f956b52ed3d1ee33997095))

## v0.4.2 (2023-04-02)
### Fix
* 🐛 in trying to use dynamic functions for types of messages ([`56a5604`](https://github.com/yaakovLowenstein/hx-requests/commit/56a5604ca5f35d8459717970096193e321bfab84))

## v0.4.1 (2023-04-02)
### Fix
* Fix bug in hx_messages ([`9006a89`](https://github.com/yaakovLowenstein/hx-requests/commit/9006a89c08782be0c5439d709007ba78a6c9f338))

## v0.4.0 (2023-04-02)
### Feature
* Use HXMessages in HXRequests ([`abefebc`](https://github.com/yaakovLowenstein/hx-requests/commit/abefebc288889fda550b047093f2793eb3a514d0))
* Add hx_messages ([`d3d6100`](https://github.com/yaakovLowenstein/hx-requests/commit/d3d6100653513735b7ba339284feabcaaf848ada))

### Fix
* Rename seting for hx_messages ([`616f36c`](https://github.com/yaakovLowenstein/hx-requests/commit/616f36c78fc3922a6fef89d3496598db99187669))
* Rename setting for using messages ([`c7750f0`](https://github.com/yaakovLowenstein/hx-requests/commit/c7750f0b15dfe8536f2cadcffaae555d344a5bc8))

## v0.3.0 (2023-03-31)
### Feature
* Add option HXRequestPOST to return empty ([`69f43df`](https://github.com/yaakovLowenstein/hx-requests/commit/69f43dfffab583185e632dcede7654263eb7d810))

## v0.2.3 (2023-03-30)
### Fix
* Bold the top line of the error message ([`e14cb7d`](https://github.com/yaakovLowenstein/hx-requests/commit/e14cb7d56209b9c22a479185a5ca63149975bccf))

## v0.2.2 (2023-03-29)
### Fix
* Remove check from views if the app is this package ([`ff7623c`](https://github.com/yaakovLowenstein/hx-requests/commit/ff7623c1b2f953161c57c6953eab140a424a4b8e))

## v0.2.1 (2023-03-29)
### Fix
* Fix bug in modal template ([`6c0425d`](https://github.com/yaakovLowenstein/hx-requests/commit/6c0425d60a8229fd4c789978a73e9a9c466fd876))

## v0.2.0 (2023-03-29)
### Feature
* Add HXRequestModal ([`919cc74`](https://github.com/yaakovLowenstein/hx-requests/commit/919cc74ec55866c60640f6584b58506b8acb5cf5))

### Fix
* Rename templates folder to hx_requests ([`c63adfb`](https://github.com/yaakovLowenstein/hx-requests/commit/c63adfb82350068277c954576b8d152bd614b780))

## v0.1.2 (2023-03-29)
### Fix
* Add skip actions for semantic relesase commits ([`bd290f6`](https://github.com/yaakovLowenstein/hx-requests/commit/bd290f6abd7d6340521a3a64320b72ba4c63ce3f))

## v0.1.1 (2023-03-29)
### Fix
* Fig bug with conflicting versions ([`51bd499`](https://github.com/yaakovLowenstein/hx-requests/commit/51bd49904f7a98a47988585717dcbd97a1cb6996))
* Add proper settings to toml for semantic-release ([`1a00018`](https://github.com/yaakovLowenstein/hx-requests/commit/1a000189bf97698acc4c8461dd59a7f5d359fd73))

## v0.1.0 (2023-03-28)
### Feature
* Add option for form errors to be added to error message ([`766bddd`](https://github.com/yaakovLowenstein/hx-requests/commit/766bddd6db82210eed3b5c6492324619b91d0461))

### Fix
* Fix bug in GH actions ([`1eb9faf`](https://github.com/yaakovLowenstein/hx-requests/commit/1eb9faf7804447e5aedd55521f3a89d476b15495))
* Set user in GH actions ([`09ab95a`](https://github.com/yaakovLowenstein/hx-requests/commit/09ab95ad28c795cb76b8fd70eda5f0e2e5578002))
* Test semantic release ([`57f4839`](https://github.com/yaakovLowenstein/hx-requests/commit/57f48397801e8b27f342e31c4eceaa6f745220d4))
* Change runs on in GH action to ubuntu ([`2b0cfaa`](https://github.com/yaakovLowenstein/hx-requests/commit/2b0cfaa6387b88d30c3711ad4684b15909339c10))
* Remove runs on from GH action ([`b0d1172`](https://github.com/yaakovLowenstein/hx-requests/commit/b0d1172bbe5238074a53269196eef95a7187c9ef))
* Move .github dir to top level ([`d4b25b4`](https://github.com/yaakovLowenstein/hx-requests/commit/d4b25b40e618ca385f587627dcf282382eb6cce6))
* Add auto versioning with GH actions ([`00d11a0`](https://github.com/yaakovLowenstein/hx-requests/commit/00d11a08b3e37de6ba9a054b60a307420d66741e))

### Documentation
* Fix space between badges in README ([`abb8fb4`](https://github.com/yaakovLowenstein/hx-requests/commit/abb8fb4f45d10754d3b22a44e05f99f4f8e9c0f5))
* Fix badge in README ([`6de8fab`](https://github.com/yaakovLowenstein/hx-requests/commit/6de8fabcc96d7a818b425cdf9ba05f37e21b0bc9))
