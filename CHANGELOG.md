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
