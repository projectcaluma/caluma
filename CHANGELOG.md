# v7.8.0 (16. March 2021)

### Feature

* Improve mapby and add stringify transform ([`5fc1c73`](https://github.com/projectcaluma/caluma/commit/5fc1c737f15deab3e4ca7457dedac8f6ba00bd82))
* Modified_content properties on document ([`e333af0`](https://github.com/projectcaluma/caluma/commit/e333af0ca5fb251d00e8c65a1c4dfc3078c55dec))
* Add modified_by_user and modified_by_group fields ([`2868866`](https://github.com/projectcaluma/caluma/commit/286886689a9ca3908b9e84c96e0c3c54949a872f))
* Allow disabling ssl verification (#1408) ([`e0d6652`](https://github.com/projectcaluma/caluma/commit/e0d6652d1274ac8f8d8a6c2f901df82c2970b9c6))

### Fix
* Minio client requires different call signature for copy ([`f878bf1`](https://github.com/projectcaluma/caluma/commit/f878bf17d67dc819b44f0a40fca458cac7e6b7d1))
* Remove unneeded default_answer field on serializer ([`3104840`](https://github.com/projectcaluma/caluma/commit/3104840f9a9c7b48c203f2b36171cf3e2b208c2a))
* New minio has different metadata structure (#1412) ([`4f021af`](https://github.com/projectcaluma/caluma/commit/4f021af1fceb36ccedd7d0671b79c66fb50f1e0a))
* Update minio client to adjust for changed exceptions ([`0783629`](https://github.com/projectcaluma/caluma/commit/07836299823ac32c0591d8034a5f9f9d92321596))
* Use fixed maxsize from newest version ([`a0ac175`](https://github.com/projectcaluma/caluma/commit/a0ac175ce6674485030b82b2df46239e05663931))
* Fix search filter when used in collection (#1392) ([`d99db68`](https://github.com/projectcaluma/caluma/commit/d99db6858b9339704bd8b52fb2d2b8eb0dea4123))

# v7.7.1 (24. February 2021)

### Fix
* Extract_global_id should not be too eager in decoding
([#1389](https://github.com/projectcaluma/caluma/issues/1389))
([`8f97dc6`](https://github.com/projectcaluma/caluma/commit/8f97dc6ef30684653d1eba8036606d28386e554a))

# v7.7.0 (12. February 2021)

### Feature
* **form:** Add python API and command for copying forms ([`7620eec`](https://github.com/projectcaluma/caluma/commit/7620eec898b70dd641b758f0f4e09c6d3bdbacf8))
* **jexl:** Add min, max, sum, round transforms ([`beb714a`](https://github.com/projectcaluma/caluma/commit/beb714ad3c95ea4d32ef81ede84c023ed635511c))
* Dump_caluma command for entire forms ([#1367](https://github.com/projectcaluma/caluma/issues/1367)) ([`20b2a79`](https://github.com/projectcaluma/caluma/commit/20b2a79fea22f2b197d5f0238b33089ce063cde5))

### Fix
* Use homebrew jexl analyzer for question extraction ([`a81c089`](https://github.com/projectcaluma/caluma/commit/a81c0898a6f5e9d847133bdf4700ad75c228a925))
* **form:** Don't validate calculated answer ([`014a804`](https://github.com/projectcaluma/caluma/commit/014a80434988d121f5cd92b8ca298a8ccf84316d))


# v7.6.0 (4. February 2021)

### Feature
* Add argument to on decorator to raise exceptions in the receiver ([`c3a3a90`](https://github.com/projectcaluma/caluma/commit/c3a3a902a30d7483f2d1ade3e2959a77a75ab7a8))

### Fix
* Calc questions not present in document ([`e111741`](https://github.com/projectcaluma/caluma/commit/e111741c90dc82d185dd3ba29ef334b8bd5e7aeb))


# v7.5.1 (2. February 2021)

### Fix
* Prevent recalculation of calculated answers for default answer changes ([`62f507c`](https://github.com/projectcaluma/caluma/commit/62f507c64e41cc5bf21deb7443d8a226c4639d67))


# v7.5.0 (22 January 2021)

### Feature
* Allow usage of form meta in question jexl ([`f3f1223`](https://github.com/projectcaluma/caluma/commit/f3f1223790fcf1aebf0908657365429557e5ed68))


# v7.4.0 (19 January 2021)

### Fix
* Validate inexisting references in calc questions ([`f4de05a`](https://github.com/projectcaluma/caluma/commit/f4de05a2e1506c15861a11a3274846d06949d7ab))
* Separate extractor for mapby arguments ([`34c6d2b`](https://github.com/projectcaluma/caluma/commit/34c6d2b370a2415517127c5f5e3e48238a00ab7c))


# v7.3.0 (14 January 2021)

### Feature
* Calculated float question ([`6a7c7ca`](https://github.com/projectcaluma/caluma/commit/6a7c7ca631a8aca66827124512c02c3e54cc5173))

### Fix
* __str__() should return string ([`df5ba3b`](https://github.com/projectcaluma/caluma/commit/df5ba3b36547492f45c02cab1904a73efa792a80))
* Use mapby args if literal, fix calculated test ([`cb49617`](https://github.com/projectcaluma/caluma/commit/cb496173b48aa282af07a01e6f91b1e314a065a8))
* Support validation of nested table answers ([`7937220`](https://github.com/projectcaluma/caluma/commit/7937220b8872faadadb0f13c6e7ca004afcf1f02))
* Use "mapby" arg if subject is answer transform ([`3a595a8`](https://github.com/projectcaluma/caluma/commit/3a595a829a6a8ab1e1499999c792a7a30bb00458))


# v7.2.1 (14 January 2021)

### Fix
* Fix validation of table questions ([`6e1cf82`](https://github.com/projectcaluma/caluma/commit/6e1cf826e84b0dc6c866ba801b1c213bc85049d4))


# v7.2.0 (23 December 2020)

### Feature
* Support multiple choice and improve choice search ([`456bf08`](https://github.com/projectcaluma/caluma/commit/456bf0805329f7c6170dcedea37545351acc7a4a))

### Fix
* Validate empty table answers correctly ([`8b00505`](https://github.com/projectcaluma/caluma/commit/8b0050532fe16f04e9ac7bf02fbe80a402645bad))


# v7.1.1 (10 December 2020)

### Fix
* Fix custom validation for save answer mutations ([`5e91341`](https://github.com/projectcaluma/caluma/commit/5e91341bad29751436ca94c8faac879277e7cb6c))


# v7.1.0 (30 November 2020)

### Feature
* Introduce API for managing default_answers ([`995138a`](https://github.com/projectcaluma/caluma/commit/995138a735ab736abe771c2b0574d72bf55fe286))
* Pass user to copy method on answer and doc ([`38941b0`](https://github.com/projectcaluma/caluma/commit/38941b0e6a336d2578b5786fd1c641565bd788a7))

### Fix
* Fix empty answers ([`fc6300b`](https://github.com/projectcaluma/caluma/commit/fc6300bd578faee85fd8ecc1b1109cd1976d3bfa))


# v7.0.3 (25 November 2020)

### Fix
* Don't use default on row_question if default table_answer exists ([`30ce974`](https://github.com/projectcaluma/caluma/commit/30ce974849b0a1d1d304e01d7158966a477bcb03))
* Fix setting default answers for sub forms ([`24d2899`](https://github.com/projectcaluma/caluma/commit/24d289941e464b90279042cbc73eb9fb897794b0))
* Use domain_logic for saving answers in form app ([`6b71559`](https://github.com/projectcaluma/caluma/commit/6b71559eb7a1dca280de625c89d7b4e65c02decc))


# v7.0.2 (23 November 2020)

### Fix
* Consequently use domain_logic for saveDocument ([`fe30966`](https://github.com/projectcaluma/caluma/commit/fe3096696bab0e3b4f62991eec643515313772b0))


# v7.0.1 (19 November 2020)

### Fix
* Move deps to setup.py ([`39e46f3`](https://github.com/projectcaluma/caluma/commit/39e46f39dd192c0b22393f05b4f401e0b55cf8d3))


# v7.0.0 (19 November 2020)

### Fix
* Pass user instead of info object to data source ([`213d84a`](https://github.com/projectcaluma/caluma/commit/213d84ad6567405f77ae9392dba024a8d06767fa))

### Breaking
* Pass the `user` to the `get_data` method of a data source instead of the whole `info` object since we don't have an info object when calling the python API. ([`213d84a`](https://github.com/projectcaluma/caluma/commit/213d84ad6567405f77ae9392dba024a8d06767fa))


# v6.7.0 (17 November 2020)

### Feature
* Handle table_questions ([`33d303c`](https://github.com/projectcaluma/caluma/commit/33d303c7427c88f9dfcde06e9828960e2d9ee795))
* Set default answers when creating new documents ([`d9c2b2e`](https://github.com/projectcaluma/caluma/commit/d9c2b2e2d49db2021e6e066d8a853f309310327b))
* Implement default_answers ([`e3dae80`](https://github.com/projectcaluma/caluma/commit/e3dae80bbe50a45051bdd826773c13eb32d582fb))
* Implement save_document form api ([`ffb422d`](https://github.com/projectcaluma/caluma/commit/ffb422d8e4ff6a146cf631a3b7f86f261ce195a7))
* Debug transforms ([`fbc5cd6`](https://github.com/projectcaluma/caluma/commit/fbc5cd663e1893770a5c2a07e59e2abf7f2b14b6))
* Useful __repr__ for most models ([`e6186cc`](https://github.com/projectcaluma/caluma/commit/e6186cc243e7d498918248fd814052db3c77dd2e))
* Add api for save_answer ([`4457413`](https://github.com/projectcaluma/caluma/commit/445741333fd77494bd323078c70d3717ad54135a))
* Create caluma_logging app for access logging ([`2602aa2`](https://github.com/projectcaluma/caluma/commit/2602aa2d8738f0e59bf4635a8b5a5fca20d4b2ce))

### Fix
* Do not use actual model in migration ([`073f01c`](https://github.com/projectcaluma/caluma/commit/073f01ceab2d5099e548bd51bda672e604b5cd78))
* Fix flaky ordering ([`1170242`](https://github.com/projectcaluma/caluma/commit/1170242d4490c70c4d5c63d3b248bc735406f0e8))
* Flaky snapshort ordering ([`73e57ea`](https://github.com/projectcaluma/caluma/commit/73e57ea58a695030cc9bbb09fa50d30d322027c7))
* Sort addressed_ and controlling_groups ([`e8eaae9`](https://github.com/projectcaluma/caluma/commit/e8eaae976e5b5417313ca14e8dad5dadbb221800))
* Do not crash during migrations ([`d6887d0`](https://github.com/projectcaluma/caluma/commit/d6887d06d99f7c6ff799055738edfeaaeaabceb6))
* Call cursor.execute with params=None ([`151394a`](https://github.com/projectcaluma/caluma/commit/151394abf46d9726391fd892e99fdc0c3e8cb7e8))
* Migrate db sequences with prefix "caluma_" ([`baf303c`](https://github.com/projectcaluma/caluma/commit/baf303c9b10a682a4e52ec2e5dde4d2325e85f13))
* Do not hang in migrations on broken data ([`bfc4304`](https://github.com/projectcaluma/caluma/commit/bfc4304bd9a22d8fc1591273c41c235c77dc7fba))


# v6.6.0 (12 September 2020)

### Feature
* add ID filter for case and work item (b6d89f315c1d79e914de575edf10945cf08d0ef2)


# v6.5.0 (11 September 2020)

### Feature
* Emit "pre_" events (dbda0a3e97e0a0ef977259d8a4e41b2912619225)

### Fix
* Don't send complete_work_item event when skip (8236481d7da4a91b66f6102592d4b9de38bf5324)
* Always send post_complete_work_item event (6b2361593bd1a1df50c49c8f7b00779a1c75cc07)


# v6.4.0 (2 September 2020)

### Feature
* suspend and resume cases and work items (5d00a44d150bee2fc58890751c2cb2bbf72ae64d)
* rootCaseMetaValue filter on allWorkItems (5aed4208fbe590ec6528ed730c35a57ecedd3379)

### Fix
* add missing transactions on serializers (9a129d1185e46329361dd4914b5c67e07f92712a)
* fix cancelling and skipping of work items with child case (07602dbf8cc9e44a50eda0b05dff1f9b8b9d63d5)


# v6.3.3 (25 August 2020)

### Fix
* Add test (31f45985d320966d266d628eaaaf848fa5bead9b)
* Make sure that one work item is always created (defc79770b7e76840e29d543bb98e5ef65fb3f89)


# v6.3.2 (17 August 2020)

### Fix
* Import djangomodelfactory from actual module path (341148f74429a4f2d032731778edce819598dce3)


# v6.3.1 (14 August 2020)

### Fix
* fix the return object of api methods (90a9102e3a9e4d9c59b49d11e5e0ec755a84c32d)


# v6.3.0 (13 August 2020)

### Feature
* add context for all case and workitem mutations (bb45477eecdc478521feac1cd746d32a79bd7cdd)
* add filter for case family (2b7271ff7ad4d3ee7f657caf20ef8d8c7a67593d)
* add filters for work item deadlines (e7eb1044c6a67e7a955229781d2ff8d98af80d48)

### Fix
* emit completed_work_item event before closing the case (2d9d236eaa0ce37f2bc8b366bbd11b447090bf42)
* enable context for skipping work items (a4f3b535514ad519f74465e743f785e0aa05994c)


# v6.2.0 (5 August 2020)

### Feature
* Add filter for filtering work items by multiple tasks (32508e587d2183e78265d32f5bff84f783430724)


# v6.1.0 (4 August 2020)

### Feature
* Add support for dynamic tasks (689f6a9940f13f7482f62a78e53ea5cc5822cffa)
* Context for DynamicGroups (9ecc69a243ea1ed21d14c17fff8ec4bf9e205169)
* Add mutation and api function for canceling work items (0b04defaccb8e78746ec1f78826febd2c247aeb7)
* Save the previous work item on the model (84cd768f99607e99cd966b95ba2aa6d6211c030e)

### Fix
* Fix flakiness by sorting the list during snapshotting (825492a27a8ce156395fbd19b99acd4f85e5e836)
* Extend test_start_case (b70b6ea1e725a935207a690016030010646c5308)
* Fix history by not using djangos update function (59ca6f5732d2fdc3ecb0191563c169066581e625)

### Documentation
* Remove duplicated intro section (175285142c6b623bf8c2132a4c73189bde5dc66e)


# v6.0.0 (29 July 2020)

### Feature
* Always send the current user to event receivers (5f0e8691b3bc98174c055d6507167ef5fe10bed8)
* Remove --keep from cleanup_history command (420c0cbaee0ff4fb7958c167c3b7b5bd353c4999)
* Extend cleanup-command for cleaning up dangling models (489bb41acb16772f258c6a5aee42def99699c489)

### Fix
* Sort the groups jexl (be5487cb4cf7864130123dff74fc4aed55d80d5d)
* Use fstring to log fstring message (538659138777c11022ebf15e90d7993d039db13e)

### Breaking
* remove --keep from cleanup_history command (420c0cbaee0ff4fb7958c167c3b7b5bd353c4999)


# v5.9.0 (1 July 2020)

### Feature
* Allow dynamic groups for group JEXL transform (15491285b4fb4fbd50c791c424ef5337f043cf46) [(Docs)](docs/extending.md#dynamic-groups)


# v5.8.1 (25 June 2020)

### Performance
* Follow-up historicalanswer migration using SQL (2fad5bc5503497eacc4a1f264756d0f05680afe4)
* Add history_question_type to HistoricalAnswer (cb93e3853f9a7d50fe9720f98b86193d427fef34)

# v5.8.0 (19 June 2020)

### Feature
* Extract code for cancelling cases and add a python API (ce74d06bdc9b0edb7080d6408f814ba434da31b4)

### Fix
* Consider workflow when completing work items (c024660d73103297dc6f96b2cdf7634190da3776)


# v5.7.0 (6 June 2020)

### Feature
* Make validation and visibility decorators chainable (b8ed8c923296ca9100f76322b0d22ea66a1cfaba)
* Add documentForms filter for allCases graph (ab14f8b96c1af838293688fd360d17c6b0466fa1)
* Expose complete and skip work item to public API (32136bdfa2f894278f1d3c5b5f660774be5761a1)
* Expose start case logic in public python api module (c78bbb72fe295fe54f81f4d49253aab6d6530c6f)

### Fix
* Remove DeprecationWarnings (262682e64cc3c6d7ca380ae6eb2fe1723ab05841)
* Fix case status when completing parallel work items (2502b309260272a525abb56a461507999ea6c3ea)
* Make tasks reusable in workflow flows (613386d7e8c9adb7fbf1e7d675b6840dccac99f8)
* Use matching question for historicalanswer (097cdcbda1e05ffb22c38630ba9dae3efd31ce37)

### Documentation
* Switch to 'id -u' when creating a pipenv (06983b664e85a7259a25ce1a543c1851a015b72c)
* Add docs for the new API functions (c5411b0cd9c51c1251925fe7db89c87a259b029c)


# v5.6.0 (28 April 2020)

### Feature
* Add filters for object creation dates (310139c03b407efa4d473c1933a48906e9007a13)
* Make created_by_group settable (ac3cb58959adcfaf386d8707416889f53ec248b8)

### Fix
* The requiredness check needs local context (2412577738dc708b1020105dd0e2eac656a332f9)
* Return table rows in sorted fashion (aa0f72539e63d9103fe138180d81d3e99f4898af)
* Ensure jexl evaluation is local to the relevant question (121bdb6ed075f6e968c7a4a250d045edec436f86)
* Properly cache is_hidden/is_required (c09a13316e2a742964c9558c10f2a9327db0c933)


# v5.5.2 (8 April 2020)

### Fix
* Fix evaluating requiredness from branch forms (062e350236f18031a4158cffe8b752192b7d2661)
* Only accepts integer or string as id (562b4c0594336392abf5a3d3f83878d37e434e42)


# v5.5.1 (27 Mar 2020)

### Fix
* fix WorkItem migration (870bd94a2a9f08d4268093649bb28f85e86811ac)

# v5.5.0 (26 Mar 2020)

### Feature
* add name filter (a804572ad6979cf26c711a7f29cd44e37cb71c6e)
* name and description (18a987370d9d6f2ec8db84ce225bd32af7de00f8)

### Fix
* fix answer transform for questions with multiple values (d0189cbac7d43ef479ff23ff0123dae23c98ca5d)

### Documentation
* add documentation about the GroupJexl (a3e5bd1e295606d64392a1205326fcad2b908092)

# v5.4.0 (24 Mar 2020)

### Feature
* Add `controllinggroups` filter to workitemfilterset (2d4b43790a3f3ea9836a87b7177f71f8b2295d7c)
* "controlling" for tasks and workitems (1ba66084d6e87de58894ed021ef99f26bfed0c90)
* Implement caluma events (3efeba0f2495a3425226bdad92a786d511852299)
* Cleanup context data for jexl expressions (4cc9a3d8b7bad18bc8378fe3611beed5b34ada18)
* Structure objects can now be accessed via dot notation (8401af5bb1eafb0a966337db294e9646b2ea3907)
* Fixture that can generate a full form and document (1e7dc050fb422274571fb8f3706c19960fa29e6b)
* Add `family_work_items` to `case` type (41b2fb764d3ef104e9d3b29cd13cd09f69f54b1a)
* Add rootcase filter (2c5145d7a2105159d244d3203b6602b5784a21e3)
* Automatically set case family (2345af3903b06b4ac66f4004ea6a28a439a05d14)
* Add case families (d7c0a662dff2f21b2226d6857b2837be35c6462e)

### Fix
* Answer transform shouldn't return value for hidden questions (984e2f9a0880eb4659917662d70ba40fdbb8d4c3)
* Remove `address_group` from `taskorderset` (92dbb5b51c99c12ecfc2d568cfb06046388766ff)
* The word "form" should always be the root form (787c30ca43578ec77ffa565e0ef0333237962d99)
* Slug fields should be 127 chars (f6c3483e19dcf549238b7408a28fb5fd9f45bb9a)

### Documentation
* Extend validation with information about jexl expressions (2d8b1d3924001302268c3b6fe04b9b8ba102347c)

# v5.3.1 (21 Feb 2020)

### Fix
* Fix loading of caluma settings (b001d6fd0eed601aea9b5e170c3f66b5dceca46d)

# v5.3.0 (20 Feb 2020)

### Feature
* Implement copydocumentmutation (613ccd3b5962d5068a49ee44090e265786feee01)
  It is now possible to copy documents
* Split settings file (c80cb4f3523fe8defc4befbe563905f9e0eb285d)
  Useful for integrating caluma as a django app
* Increase max-length of slugs to 150 (5dbfff523d6486166c8e115071ca526bbd7c60e4)
* Add support for minlength validation (4d67bcefc9659932f8edfd28f4864074c969cc95)

### Fix
* Do not validate row documents when attaching them (fee356ae9549ca0bf4df4a18f9d260f8dd544569)
* Do not crash when lamenting invalid form slug (42ce73cf3049c0305efae4d35807cc5f7a982deb)
* Handle is_required correctly in nested questions (cb78c0836d6d354aa78a6458a70ca660f6d7b32b)

### Documentation
* Add docs about usage of django apps and interfaces (c164ed340db0b7e1a2f8ca49bdc973ff8b8b8f90)
* Add hint about snapshot updates and xdist (c0269950f1261884786306c013bd01945fee6498)


# v5.2.1 (17 Feb 2020)

### Fix
* add unique_together to DynamicOption (c7460c01a4c764f580adc5c76cdca3cbe208b081)


# v5.2.0 (13 Feb 2020)

### Feature
* new filter on cases to check for answers in work items (827399264e275784ec45643143a4ceb7a05751b2)
* add indexes on timestamps and user fields (0ad0c41d79d6dddd08662a4e547094b2e5c82c3f)

### Fix
* file answers need special treatment (65e1a3787d5dcefa171694f538f69019e7d6b02d)
* fix user object creation (6ed82c6ef865e5fc203733ec35eab209ca8781fd)
* fix validation of dynamic answers (88431eaf61cf3f2c689c1417408873a1d7de055c)

### Documentation
* add guide on workflow implementation (WIP) (515add093009f9abb668e26eef00da434f176c57)


# v5.1.0 (31 Jan 2020)

### Feature

* add hierarchical inspection classes (0d746594d9d14e23b7d90b359c8869b8d3ab7afc)
  Useful for extension points and caluma-as-django-app

### Fix

* validation performance vastly improved (25570a9b220d773b5a1517bb4e0b40d27ed306f1)
  form validation query count is roughly 10% of what it used to be


# v5.0.0 (22 Jan 2020)


### Feature
* add assigned users filter (93badb4a55e91f7ffc6a3fc5828b18765cae9564)
* prefix all apps with "caluma_" (928146577f3cb2f76a4e715ba29ae4e1eb547907)
  (BREAKING CHANGE: Extension code must be updated)

### Fix
* correctly handle indirectly hidden questions (cfe616684980d732fe667099a74461d6dbfaa732)
* version bump (d2a4755c4e06d7f683165e582780ec3e5121c835)

### Documentation
* add maintainer's handbook (9f64fc4837bb5974fb7cd3caa67bb6c32bf2661e)


# v4.3.0 (18 Dec 2019)

### Feature
* make caluma installable as django app (573e87a76ca3a2b70816ce98fd08c2cc71fc5c74)


# v4.2.0 (17 Dec 2019)

### Feature
* helper to extract mutation parameters from request (197a775d332576b03853ded00c80c3abf46f4f25)
* run pytest in parallel with xdist (9a435d9d0714aef64b955c2942803a17e561a721)
* allow filtering answers to limit only visible answers (0eb037f8d1a09a7a752ac6bec58e9f4a70a17bdc)
* add pipenv setup command to setup.py (448b821ab557e0af59fcab3a976c0e00a5e98e82)

### Fix
* use root form as form property in QuestionJexl context (5f422c01cb42d0d2833f79774eb34cd4fbbdb85a)
* remove insignificant performance hack (db3d84234fa2d803f51ac3c892abba17d7c91614)
* use "development" instead of "dev" as documented (1645ed996d4f310a91fb893627158945fbbedcc3)

### Documentation
* add info about the `UID` variable (f9a8d3ffee95b39474f31dd8d79d126ff6fde006)
* add more detailed example for the pipenv workflow (16a94a81582b4164280157f559236d009ed4461d)


# v4.1.0 (28 Nov 2019)

### Feature
* make permission decorators chainable
(3052cbff33cb98ee22a7ed34c3133820121794bf)

### Fix
* validate dependencies correctly (854f6fa77048edeb9bc84d24036fff4fde2f05de)

# v4.0.0 (21 Nov 2019)

### Feature
* add created_at, closed_at, modified_at filters to work items (b83ce9c6b0b8248b82216e30c65ecb400660fdc4)

### Fix
* optimize `historical_qs_as_of` (95e5fb9865d523e0acf96c54743cebf70b6344a9)
* fix duplicate documents (68934392c56e2d1734a5046e7e5182e07ce3fd0e)
* use LocalizedValue for translations (3cf3720f94ed64367c55b700be97a955472b00e4)
* correctly handle is_hidden regarding dependencies (a068c2c04b94f94b25087c769a931ce8f549251f)

### Breaking
* allow Answers with empty value (81cbe9aae553ed91a86c1813a47085fb3b386713)

### Documentation
* explain how to use pipenv (745380f39b45fdf1d936aad87a368c2b37e75109)


# v3.0.0 (6 Nov 2019)

Version 3.0.0. Main changes:

* License changed to GPL 3.0 (or later)
* Dynamic data source improvements (Answers now store values for the case where the value won't be available in the future anymore)
* Allow skipping of work items

### Feature
* allow skipping of work items (e84f9360cb245587dab7e75d84134b7999bfa2e5)
* add `status_skipped` to possible `workitem` states (c3d99bc9d911a103796821e09f3f65bb543457ca)
* switch main license to GPL-3.0-or-later (978f18aaa725ad779bd0238b82528401f36147bb)
* implement dynamic data source (63ffe863bd17cc75c75d7834e7f38e45268022da)

### Fix
* question id/slug should be of type id (69511c17cccba36775840976d384010867256499)
* add user and group to dynamic option (ba89f88b7cec45b17e0c6036884998cdad873f0f)
* raise a 401 if user is not logged in (1b5851c2025d1e3b95353f71d2678f640847955e)
* add question to validate_answer_value method (3667e3d3aaf45459135718c401e40c02535adc01)
* fix DynamicOption model (35935ddd04861a7c2c9cc0ec8aa92de983f1c334)
* do not return questions multiple times (ec285957c661b04ed10f305fbae7b6824cfd4b97)
* remove dynamicoptionSet form schema (0391c04481097792ef608afdebb6f39d10077959)
* reintroduce ordering by deadline on work items (fed67da288aebff593cc77855b1b5c39f44d0b91)
* fix ordering by question value (1dcec885518d6f654773e07677cb58649613ede2)
* revert dynamic data source (85fab681039f5f11c484a3c525631af6e0eddd25)
* validate requiredness recursively for subforms (844b914f98f1ed002f9dbbabffaf445753a18728)
* do not validate hidden questions (1fb7bd5b93368c0c5c55bbc6e941f8208aeb2929)

### Breaking
* Add the parameter `question` to the `validate_answer_value`method and add a new lookup to check if a `dynamic_option` already exists.  (3667e3d3aaf45459135718c401e40c02535adc01)
* The `value` field on the `DynamicOption` model is renamed to `slug` and not optional anymore.  (35935ddd04861a7c2c9cc0ec8aa92de983f1c334)
* The optional `answer_value` parameter for the `DataSource.get_data()` method was reverted.  (85fab681039f5f11c484a3c525631af6e0eddd25)

### Documentation
* explain license choice (4d59af520da53b44c3771eb53c451d209c1aafa5)


# v3.0.0a1 (6 Nov 2019)

### Feature
* allow skipping of work items (e84f9360cb245587dab7e75d84134b7999bfa2e5)
* add `status_skipped` to possible `workitem` states (c3d99bc9d911a103796821e09f3f65bb543457ca)
* switch main license to GPL-3.0-or-later (978f18aaa725ad779bd0238b82528401f36147bb)
* implement dynamic data source (63ffe863bd17cc75c75d7834e7f38e45268022da)

### Fix
* add user and group to dynamic option (ba89f88b7cec45b17e0c6036884998cdad873f0f)
* raise a 401 if user is not logged in (1b5851c2025d1e3b95353f71d2678f640847955e)
* add question to validate_answer_value method (3667e3d3aaf45459135718c401e40c02535adc01)
* fix DynamicOption model (35935ddd04861a7c2c9cc0ec8aa92de983f1c334)
* do not return questions multiple times (ec285957c661b04ed10f305fbae7b6824cfd4b97)
* remove dynamicoptionSet form schema (0391c04481097792ef608afdebb6f39d10077959)
* reintroduce ordering by deadline on work items (fed67da288aebff593cc77855b1b5c39f44d0b91)
* fix ordering by question value (1dcec885518d6f654773e07677cb58649613ede2)
* revert dynamic data source (85fab681039f5f11c484a3c525631af6e0eddd25)
* validate requiredness recursively for subforms (844b914f98f1ed002f9dbbabffaf445753a18728)
* do not validate hidden questions (1fb7bd5b93368c0c5c55bbc6e941f8208aeb2929)

### Breaking
* Add the parameter `question` to the `validate_answer_value`method and add a new lookup to check if a `dynamic_option` already exists.  (3667e3d3aaf45459135718c401e40c02535adc01)
* The `value` field on the `DynamicOption` model is renamed to `slug` and not optional anymore.  (35935ddd04861a7c2c9cc0ec8aa92de983f1c334)
* The optional `answer_value` parameter for the `DataSource.get_data()` method was reverted.  (85fab681039f5f11c484a3c525631af6e0eddd25)

### Documentation
* explain license choice (4d59af520da53b44c3771eb53c451d209c1aafa5)

# v2.0.0 (18 October 2019)

This is the second major release of Caluma.

Apart from a couple of new features, we changed the license from MIT to AGPL.
The reasons for this are documented in a followup (see #749).

There's another backwards-incompatible change regarding the data sources for
dynamic (multiple) choice questions, prompting the version bump.

New in this version is also the separation between ordering and filtering in the queries,
and a cleanup command for historical data.

### Feature
* pass actual answer value to data source (3b26162db5bfd0b48b908ef7609abeddcf24af8b)
* add order filter for workflow models too (b2fb9c73d451d2292e2bdafa25b9da1151d0915b)
* add test for new order filters (344bc9d502469acc5597355d1b832e68b5893e11)
* introduce new-style ordering for form nodes (f73f8e5a6c3d287804dca88da636c515c26b2026)
* implement new order filter (012d1f19089dff4bb0125d982cc6688374e4f68a)
* start using the collection filterset factory (97394c7e523f40af102828c94dd01de7c3a97f7a)
* factory for unionized filters (686484d1e732828db2e55b7056a83925104da676)
* expose original document id (051cf01ed283dbc8b3c00a91f9a124a764f9d755)
* add cleanup command (a66582a4945c3562828cdca284e3fff8da11af98)

### Fix
* typo (9cd21c195383ec3642a0e1bc5ef2cc46c1f269ef)
* link guide (57df4a6dc35c54aa32bfb1eccef64465191f2b4a)
* don't pass self to super().__init__() call (748c99d6315d99551f9e950b3888cafd321b8b58)
* correct svg font (576e2fe71a5562f1c41fdce83ab926be0ecbab45)
* cleanup_history - add force argument (9191b4e3638f866d256ac3b40a59b6839a6d4ef5)

### Breaking
* `DataSource.get_data()` methods must accept an optional `answer_value` parameter.  (3b26162db5bfd0b48b908ef7609abeddcf24af8b)
* License change: Move to AGPL (bfb66199)

### Documentation
* update ordering documentation (85a1143b02884f75fd3c24fccfa842c5f783adf6)
* add note on deprecation of old-style filters (b93e27c49f5b57d0acbdd560766ddff2baefc041)
* extend the guide with form-builder steps (bdd183d111e844e739c74d0536d2c4e29aec7b39)
* add guide (WIP) (822f4c1c31ee3f404b5c4b9cc76d96e2a1be1a5f)
* document cleanup commands in README (dc58593af1d147bd06cb62b02f2d27459cc7f01e)


# v1.0.0 (25 September 2019)

Initial release
