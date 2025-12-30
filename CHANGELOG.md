# v12.2.4 (30 December 2025)
### Fix

* **minio:** Add region parameter to support garage s3 storage ([`f58f589`](https://github.com/derrabauke/caluma/commit/f58f5893c376168d109e7d3ac5e855ddfc298bd5))

# v12.2.3 (24 November 2025)
### Fix

* Downgrade minio because of breaking changes ([`b9ae27a`](https://github.com/projectcaluma/caluma/commit/b9ae27a1c10594d42e8e759432ab9ff6d8583093))

### Documentation

* **work_flow redo:** Add some examples to make clear where the redoable condition is tested ([`67cf01b`](https://github.com/projectcaluma/caluma/commit/67cf01b32a2bba7bc3711eeda7d0b4580dd8fae8))
* Update release procedure in maintainer instructions ([`b664ec5`](https://github.com/projectcaluma/caluma/commit/b664ec5b238636b43ebb7bf334fb954bdadf4f04))

# v12.2.2 (25 September 2025)

### Fix

* **jexl:** Remove whitespace in stringify transform ([`dd44dd8`](https://github.com/projectcaluma/caluma/commit/dd44dd84d230a7b9b61e6fcc608ad5ab85f21f80))

### Documentation

* **format-validators:** Add missing question argument to docstring ([`25fbcb7`](https://github.com/projectcaluma/caluma/commit/25fbcb7504d721a4c44cff3949a4a99dee18b09d))

# v12.2.1 (12 September 2025)

### Fix

* **format-validators:** Expose format validators on question graphs ([`7b35221`](https://github.com/anehx/caluma/commit/7b352216caf1275b21f25d063b003ff47812b893))

# v12.2.0 (12 September 2025)

### Feature

* **format-validators:** Add question as context when validating ([`b4b62a5`](https://github.com/anehx/caluma/commit/b4b62a57f3f74c1d1460b8d949ddbd843b955068))
* **format-validators:** Allow dynamic arguments for error messages ([`bdd77c7`](https://github.com/anehx/caluma/commit/bdd77c7d429eb0017e5dba8ffb968b4a25b7a657))

# v12.1.0 (11 September 2025)

### Feature

* **form:** Allow custom validators on all questions ([`fdf6fde`](https://github.com/anehx/caluma/commit/fdf6fde4e3878abc7c88c21483f0e8bfed3f04cb))
* **format-validator:** Use gettext to define translated messages ([`7cb5840`](https://github.com/anehx/caluma/commit/7cb584039b69117365e767ac12e5b325b1f9a770))

### Fix

* **schema:** Fix expected graphql type for is_hidden on options ([`1fdd679`](https://github.com/anehx/caluma/commit/1fdd6794a8fb54a2a9b1bb5d1ffd76b41bad9312))

# v12.0.0 (03 September 2025)

### Feature

* **deps:** Update dependencies ([`9343a04`](https://github.com/anehx/caluma/commit/9343a0473d32d124598498bf3638cd027f308b26))

### Breaking

* This removes support for Python < 3.12. Django 5.2 also drops support for PostgreSQL 13 which will therefore not be tested by Caluma anymore. If you're using Caluma as an app with Django 4.2 it is still expected to work. ([`9343a04`](https://github.com/anehx/caluma/commit/9343a0473d32d124598498bf3638cd027f308b26))

# v11.3.0 (16 April 2025)

### Feature

* **gql:** Add filter for multiple task slugs to allTasks ([`347aa2a`](https://github.com/anehx/caluma/commit/347aa2a00cb13b3220c675cd505d5e4c50f1f865))

### Fix

* **history:** Make history aware of potential proxy models ([`f336c67`](https://github.com/anehx/caluma/commit/f336c672594e439f2bc3fc04601e40dbc1f79e6b))

# v11.2.1 (24 March 2025)

### Fix

* **structure:** Take form for a new row set from the fastloader ([`2480a31`](https://github.com/projectcaluma/caluma/commit/2480a31633f54eb46aa06665c94c9256249cfe85))

# v11.2.0 (17 March 2025)

### Feature

* **copy:** Adds on_copy to datasources to alter dynamic values ([`9c076e5`](https://github.com/projectcaluma/caluma/commit/9c076e5053844bae9bbe5913124b0cc4b6053303))
* Use uuid7 instead of uuid4 from now on ([`915e454`](https://github.com/projectcaluma/caluma/commit/915e454cdc5fdb729e2c8b8ba6e600600cf3e932))

### Fix

* **perf:** Don't load full document in memory if not needed for options ([`506bec9`](https://github.com/projectcaluma/caluma/commit/506bec927ae75af95829297ad143124320dac985))

# v11.1.4 (25 April 2025)

### Fix

* **perf:** Keep auth http session alive across requests ([`18d4d6a`](https://github.com/projectcaluma/caluma/commit/18d4d6aae6e719fd0423ccaf6dd4f0a8ff69723f))

# v11.1.3 (15 April 2025)

### Fix

* **structure:** Take form for a new row set from the fastloader ([`a08f566`](https://github.com/projectcaluma/caluma/commit/a08f5669a96ca6e421285a10a29e479077b7c848))

# v11.1.2 (07 March 2025)

### Fix

* **perf:** Don't load full document in memory if not needed for options ([`581d2d0`](https://github.com/projectcaluma/caluma/commit/581d2d056daeee0394c94f20dd64c36ff12a7be8))
* A few other code cleanups (CI, small refactorings)

# v11.1.1 (04 March 2025)

### Fix

* **structure:** Correctly update structure in-place for recalculations ([`8cccc7e`](https://github.com/projectcaluma/caluma/commit/8cccc7ef60fd5b7f9b0459e2c26b324485dc523a))
* **structure:** Fix passing of global validation context for structure ([`2b1f7e4`](https://github.com/projectcaluma/caluma/commit/2b1f7e413c0063cca9bed5b47c387378d9bc3343))

# v11.1.0 (04 March 2025)

### Feature

* **forms:** Extend structure fastloader to support multiple documents ([`28ca840`](https://github.com/projectcaluma/caluma/commit/28ca8403fc4c96bdb8ef2f4cb0d1ede056444003))

### Fix

* Deterministic option sort ([`8f2a25a`](https://github.com/projectcaluma/caluma/commit/8f2a25a331a7bb5c94bfc05ab6b1fc9a13521cfe))
* **structure:** Question options should not be loaded multiple times ([`cba8fbe`](https://github.com/projectcaluma/caluma/commit/cba8fbe2565cdb1932f7c1af2f2791ec0591beb3))


# v11.0.2 (04 March 2025)

### Fix

* **deps:** Fix django-filter version range ([`f7a7f7c`](https://github.com/projectcaluma/caluma/commit/f7a7f7c412f634a4c145ac3ea6ff727e03f9de79))

# v11.0.1 (03 March 2025)

### Fix

* Pass correct parameter  dealing in calc field recalculation ([`1536ab8`](https://github.com/projectcaluma/caluma/commit/1536ab8c66bc5bb352d3ca04175d82ba0f514d4a))
* **form:** Error when saving an answer that does't belong to a form ([`c27a045`](https://github.com/projectcaluma/caluma/commit/c27a0459e8d43b7b989fd2f4b5881a033d715cb1))
* **validators:** Import exception from the correct place ([`6fe8566`](https://github.com/projectcaluma/caluma/commit/6fe8566706e9676de0dc538002c60ee9d0c3d780))
* **jexl:** Fix crashes in form validation when validating options ([`a9ed291`](https://github.com/projectcaluma/caluma/commit/a9ed2915ae6e6ad302da449cc1eacfd745a7730e))


# v11.0.0 (28 February 2025)


### Feature

* **structure:** Introduce a fast-loading mechanism ([`e82cb5e`](https://github.com/projectcaluma/caluma/commit/e82cb5ea005904e96fa98339a7f50ee964b8325b))

### Fix

* **structure:** Correctly sort questions and table rows ([`36a6080`](https://github.com/projectcaluma/caluma/commit/36a60809033dfa3b8d34b45a0369f0224e5b94ab))

### Breaking

* Code that uses the form jexl and / or structure code most likely will need to be rewritten. The changes are small-ish, but still semantically not exactly equal. ([`7c997b7`](https://github.com/projectcaluma/caluma/commit/7c997b70850a4c4e7f046714d8a1ab56a89ef950))
  See https://github.com/projectcaluma/caluma/pull/2356 for further details.
* While not yet (technically) breaking, we do not support Python versions
  of 3.9 and earlier. Update your Python to 3.10 or ideally, 3.13. Support
  for Python versions will be according to Python's own version schedule:
  https://devguide.python.org/versions/

# v10.7.0 (09 January 2025)

### Feature

* **float:** Add step configuration ([`a8c265a`](https://github.com/projectcaluma/caluma/commit/a8c265a87666e87621eda8441eac81371c652199))


# v10.6.0 (09 January 2025)

### Feature

* **workflow:** Add indices to created_at and deadline of work item ([`8e7b8d7`](https://github.com/projectcaluma/caluma/commit/8e7b8d7e100adf58d14296338f76077f1ad077bc))

### Fix

* **form:** Optimize calculated question performance ([#2339](https://github.com/projectcaluma/caluma/issues/2339)) ([`db6468b`](https://github.com/projectcaluma/caluma/commit/db6468be0ae72ea572d805c65ad424c8bfabebde))
* **build:** Don't crash build step due to missing readme at this stage ([`75f3c93`](https://github.com/projectcaluma/caluma/commit/75f3c932c2a7575a6a3ffef60c1639a7e1d72d82))
* Update (and pin) graphene dependency ([`7572c55`](https://github.com/projectcaluma/caluma/commit/7572c55572326a45bc455736e33282a9c2ee6d69))


# v10.5.1 (16 October 2024)

### Fix

* **visibilities:** Don't crash in the suppressable visibility resolver ([`26fd823`](https://github.com/projectcaluma/caluma/commit/26fd82366a8ae3389e3d2d498605bf136cd6924d))


# v10.5.0 (15 October 2024)

### Feature

* **visibilities:** Make visibilities suppressable on n:1 relationships ([`0899cc7`](https://github.com/projectcaluma/caluma/commit/0899cc75372af0e3fdfbfaa16932419364a39a6f))

### Fix

* **perf:** Add indexes for frequently filtered attributes on work item ([`b9a2032`](https://github.com/projectcaluma/caluma/commit/b9a2032b6dc396c016766ae3a1bd80ad3dc8b0c1))


# v10.4.0 (26 September 2024)
### Feature

* **jexl:** Add length transform ([`b4fbd99`](https://github.com/projectcaluma/caluma/commit/b4fbd997b866f82b3b65bcc0fb6e1237ca69e0df))

### Fix

* **form:** Speed up copying of documents ([`fac7a98`](https://github.com/projectcaluma/caluma/commit/fac7a986de97cd8fb1a7d1f8444df8c83afeab3a))
* Add missing "is_hidden" to SaveOptionSerializer ([`ab63598`](https://github.com/projectcaluma/caluma/commit/ab63598d1051739eb3989d48d446e61e8d19568b))


# v10.3.1 (9 August 2024)
### Fix

* **deps:** Update dependencies ([`322dc23`](https://github.com/projectcaluma/caluma/commit/322dc23853ebfd4c7f2039523da3c268cb623d49))
* **jexl:** Always add root info ([`7b154f8`](https://github.com/projectcaluma/caluma/commit/7b154f82bc9525548a2203d1a8cd022fca026fbc))
* **code of conduct:** Contact mail address ([`29aaf2e`](https://github.com/projectcaluma/caluma/commit/29aaf2e725f726140330be766d8ebc4e054e82af))

# v10.3.0 (15 July 2024)
### Feature

* feat: allow calculated fields to depend on other calculated fields ([`92a8c1b`](https://github.com/projectcaluma/caluma/commit/92a8c1bd4734673cd2b37ac86236c2e6cc3ca5e8))

* feat(options): implement is_hidden jexl on options

    This commit adds an `is_hidden` jexl to Options. This will be evaluated
    and enforced on saving of answers. Addiotionally, the Options got a new
    filter `visible_in_document`. ([`38ca1c4`](https://github.com/projectcaluma/caluma/commit/38ca1c4570a02bc3086b9897eff19956cf46c3ec))

### Fix

* fix(docker): install dependencies as caluma user ([`9623107`](https://github.com/projectcaluma/caluma/commit/962310774681c32845fb8c17b4eeadbdc686ae0d))

# v10.2.0 (21 May 2024)
### Feature

* feat(form): add more case info to jexl context ([`ab73edd`](https://github.com/projectcaluma/caluma/commit/ab73eddb03215d288c782e12ca15e04bc7dc2e48))

* feat(jexl): add main_case_form to info object

    This is convenient when you&#39;d like to write a JEXL expression in a task
    form attached to some work item, that depends on the main case&#39;s form. ([`bcb9136`](https://github.com/projectcaluma/caluma/commit/bcb913668e2454ca0dd0c8990eba310efef32b96))

### Fix

* fix(validation): do not block __typename when introspection is disabled

The `DisableIntrospection` validator rejects everything that could
lead to insight into the schema. Sadly, our frontends rely on having
`__typename` available, thus we need our own validator that allows this
specific introspection key (but not anything else) ([`46f2184`](https://github.com/projectcaluma/caluma/commit/46f21840610be6ddb3569a2b96b7866ae9f33e12))

# v10.1.1 (8 February 2024)
### Fix

* Do not query for non-existent buckets in healthz ([`7d5e8ab`](https://github.com/projectcaluma/caluma/commit/7d5e8ab0d2188ee10f9b304737c5835ccb0d0e49))


# v10.1.0 (8 February 2024)

### Feature
* **settings:** Add setting to limit query depth ([`dde9c9a`](https://github.com/projectcaluma/caluma/commit/dde9c9a22306edd717e40bde7603d75178887fb9))

### Fix

* Defer calculation of calc answers until after creating a new doc ([`8111843`](https://github.com/projectcaluma/caluma/commit/81118437498ec902d62fe2611232c2b1d29fb10e))


# v10.0.0 (31 Jan 2024)

## Breaking

* chore: drop deprecated id filter on cases filterset
  BREAKING CHANGE: you now must use the `ids` filter instead ([`e6356fa`](https://github.com/projectcaluma/caluma/commit/e6356fa7dea5f7848dd1c8758ea9000ab736c452))

* chore: update lots of dependencies
  Notable change: replacing `psycopg2` with `psycopg`, version 3

  BREAKING CHANGE: This drops support for PostgreSQL versions 9, 10 and 11,
  as well as Python 3.8.

* feat(healthz)!: overhaul health-checks for them to be less intrusive

  This commit contains no changes. Its only purpose is to mark the commit
  `54c545f3d484661f8c9b29b1ce20384b8df5bfc5` as breaking, because this was
  forgotten.

  BREAKING CHANGE: In the healthz response, the key `database models` has
  been dropped. ([`4a585da`](https://github.com/projectcaluma/caluma/commit/4a585da789d111806faf8e4bfb130f5d71e0a889))

## Feature

* feat: disable introspection via validation rules property ([`21afd5d`](https://github.com/projectcaluma/caluma/commit/21afd5d9343a900fc262f5edb75137462d8403f2))
* feat: implement flat_answer_map (analog to ember-caluma) ([`d96d33e`](https://github.com/projectcaluma/caluma/commit/d96d33e575abdb079adf97f3918ba6d04b34fadd))
* feat(filters): add EXACT_WORD lookup type to SearchAnswer ([`23c0e55`](https://github.com/projectcaluma/caluma/commit/23c0e552a91dd882a79e1f76407159c4383a2861))
* feat(healthz): overhaul health-checks for them to be less intrusive ([`54c545f`](https://github.com/projectcaluma/caluma/commit/54c545f3d484661f8c9b29b1ce20384b8df5bfc5))

## Fix

* fix(graphene): add a custom metaclass factory for interface types ([`d56f131`](https://github.com/projectcaluma/caluma/commit/d56f13134cf781ce4b46c81b55efb922a8a549f2))
* fix(analytics/tests): do not assume sorted output ([`136f1ae`](https://github.com/projectcaluma/caluma/commit/136f1aed9af31d72108f8fa4cf56272e2a5ad6a6))
* fix: new keycloak versions omit groups in claims if no groups are set ([`d88affa`](https://github.com/projectcaluma/caluma/commit/d88affaee5129164bc034a4897b8c40bb2e1cc10))
* fix: only save updated fields in post_complete case logic ([`8c9edae`](https://github.com/projectcaluma/caluma/commit/8c9edaebaa3be2c0c90797b8f848b430102f2287))
* fix(healthz): do not warn about expected events ([`b747c1f`](https://github.com/projectcaluma/caluma/commit/b747c1f6d89932f16d65a495bf213156982e4542))


# v9.3.3 (5 January 2024)
### Fix
* Only save updated fields in post_complete case logic ([`eeabb02`](https://github.com/projectcaluma/caluma/commit/eeabb02b2812e50b1f279cf04bd13518f5f9872d))

# v9.3.2 (21 December 2023)
### Fix
* New keycloak versions omit groups in claims if no groups are set ([`d88affa`](https://github.com/projectcaluma/caluma/commit/d88affaee5129164bc034a4897b8c40bb2e1cc10))

# v9.3.1 (1 September 2023)
### Fix
* **migrations:** Make app prefix migration language independent ([`2f3a5d3`](https://github.com/projectcaluma/caluma/commit/2f3a5d3a86c133da531cc0204adb9d7094ff1e15))

# v9.3.0 (22 August 2023)
### Feature
* **form:** Add show_validation property for action buttons ([`6dea57e`](https://github.com/projectcaluma/caluma/commit/6dea57e35657559288625a24c9ab6bb62e76b4e4))

# v9.2.0 (15 August 2023)
### Feature
* **core:** Add meta intersection filter ([`1a54a7f`](https://github.com/projectcaluma/caluma/commit/1a54a7f1798d4f816a29e2c68935294899fa2a88))

### Fix
* **analytics:** Fix meta field extraction ([`704ffb9`](https://github.com/projectcaluma/caluma/commit/704ffb907d7863f9928fe10bb8826e226c286cb0))

# v9.1.0 (17 July 2023)

### Feature
* **jexl:** Add flatten transform ([`42144cb`](https://github.com/projectcaluma/caluma/commit/42144cb64ec43baa52db82cf1304d700f6e6673e))

### Fix
* Also catch ValueError and ZeroDivision errors on early jexl evaluation ([`0fe96ea`](https://github.com/projectcaluma/caluma/commit/0fe96ea9268781b2ab604c2e6398f27baf407f8b))

### Documentation
* **jexl:** Update question jexl docstring ([`cdf1e73`](https://github.com/projectcaluma/caluma/commit/cdf1e7369f08eb7de8af9ec821b7331276a60ab9))


# v9.0.0 (9 June 2023)

### Feature
* **auth:** Only use userinfo for auth (drop introspect) ([`d065ef8`](https://github.com/projectcaluma/caluma/commit/d065ef8fd52f0c09d7c5f660c72441ef1cb3a0a6))
* **analytics:** Support accessing sub-cases and their parent ([`6dfc4f9`](https://github.com/projectcaluma/caluma/commit/6dfc4f9c5f7eeb92042447e77954639d298a907b))

### Breaking
* setting the `OIDC_INTROSPECT_*` and `OIDC_CLIENT_AS_USERNAME` env vars is obsolete now. Auth now only calls the userinfo endpoint without any fallback to the introspect endpoint. This will possibly have an impact on the `username` property of the user object. If your extensions depend on that property, please update them if necessary. Additionally, all requests sent to Caluma must include the `openid`-scope. ([`d065ef8`](https://github.com/projectcaluma/caluma/commit/d065ef8fd52f0c09d7c5f660c72441ef1cb3a0a6))


# v8.0.0 (12 May 2023)

### Fix
* **workflow:** Provide context to WorkItemValidator ([`2fb5308`](https://github.com/projectcaluma/caluma/commit/2fb530874869898a0e03ce9af16038003ce1f56a))

**This is the long overdue stable release of Caluma v8. For a detailed description of the changes to v7, please refer to the changelogs of the v8 beta versions.**


# v8.0.0-beta.30 (10 May 2023)

### Fix

* **analytics:** Fix aliases exceeding 63 bytes ([`cdca090`](https://github.com/projectcaluma/caluma/commit/cdca090e6a8cafbeb3dde5aad29bb1c866dea518))


# v8.0.0-beta.29 (13 April 2023)

### Feature

- **filters:** Add filters for modified_at ([`16fdb73`](https://github.com/projectcaluma/caluma/commit/16fdb732f127fb06038784e87582441f303526de))


# v8.0.0-beta.28 (21 March 2023)

### Feature
* **filters:** Add useful deadline filters to workitems ([`f74d641`](https://github.com/projectcaluma/caluma/commit/f74d641eac81151aa0b7a435f804a43078a952a2))


# v8.0.0-beta.27 (10 March 2023)

### Feature
* **filters:** Support word combinations in SearchAnswersFilter ([`4c3e910`](https://github.com/projectcaluma/caluma/commit/4c3e910db65cc34677856a97b07b812c3db28233))
* **workflow:** Add case_document_forms filter to work item ([`e351de3`](https://github.com/projectcaluma/caluma/commit/e351de3b9c4c48e70f529295b13a61cc5052daec))


# v8.0.0-beta.26 (20 February 2023)

### Fix
* **form:** Fix validation in document validity graph ([`6b859fa`](https://github.com/projectcaluma/caluma/commit/6b859fa1f76762a8fcfadff7f1010ec4b17d02f4))


# v8.0.0-beta.25 (17 February 2023)

This release provides a management command for recalculating calculated Answers that
contain values from `TableQuestions`. Due to a bug, answers to calculated questions
were wrong under certain conditions, if they contained values from table rows. This
command recalculates all of them.

If you use `CalculatedFloatQuestions` in your forms, it is advised to run this command:

```shell
python manage.py recalculate_calc_answers
```

### Fix
* Replace faulty migration for calc answers with a command ([`4a3e85c`](https://github.com/projectcaluma/caluma/commit/4a3e85cf5a1ac105541dde1b04d8081d01a90e12))


# v8.0.0-beta.24 (17 February 2023)

### Feature
* **analytics:** Add support for calculated questions ([`196ab05`](https://github.com/projectcaluma/caluma/commit/196ab054abb94aa4e27900ade6c3920b14829ee6))

### Fix
* Fix calc answer evaluation when adding new table rows ([`cb668ba`](https://github.com/projectcaluma/caluma/commit/cb668ba88371fe5d48ee4402348ec9182068ee18))
* **workflow:** Emit post_create_work_item when redo is set to ready ([`5e9744a`](https://github.com/projectcaluma/caluma/commit/5e9744a0b9cbcc2fdbf741f77fa1603b8d3bf69d))
* **analytics:** Handle missing dates ([`a06181a`](https://github.com/projectcaluma/caluma/commit/a06181a11994a9e40600b419753b83d35557b76e))
* **analytics:** Properly quote expressions ([`3ff7f36`](https://github.com/projectcaluma/caluma/commit/3ff7f368c87f1f058ad0420fb14e8fda522ccffd))


# v8.0.0-beta.23 (26 January 2023)

### Fix
* **analytics:** Fix form identifier; disable subform form ([`94542ac`](https://github.com/projectcaluma/caluma/commit/94542aca4c9e9d5df26240aee1e465ad01c4db58))
* Properly quote aliases - small additional fixes ([`535c703`](https://github.com/projectcaluma/caluma/commit/535c7030a019672ce72d2db8efe532cfab492125))


# v8.0.0-beta.22 (12 December 2022)

### Feature
* **analytics:** Add support for form name extraction ([`1df3f53`](https://github.com/projectcaluma/caluma/commit/1df3f536a7968b5d0f6bf0dcc0392af338e36bcb))
* Allow using client id as user for client-secret auth ([`3e45c61`](https://github.com/projectcaluma/caluma/commit/3e45c61a9feda916fefc06ab6f2764bbe415bf5f))

### Fix
* Do not crash when django-extensions is missing ([`6028be3`](https://github.com/projectcaluma/caluma/commit/6028be3d297ec76bd0b584553fb56679a85a43b9))
* **analytics:** Fix commandline output crash with certain aliases ([`1839423`](https://github.com/projectcaluma/caluma/commit/1839423b5ef5559b392138c04881abbb204a2c0e))
* **analytics:** Do not crash with more complex visibility layers ([`71be082`](https://github.com/projectcaluma/caluma/commit/71be0822e467bfe5edf757b8068c483a91c73f18))
* **analytics:** Do not output summary for simple tables ([`34205cf`](https://github.com/projectcaluma/caluma/commit/34205cfe9a7ffc6cc9e3d2d4ae807f0a25e59cad))


# v8.0.0-beta.21 (17 November 2022)

### Feature
* **data_source:** Add question and context arguments for data sources ([`cb2739e`](https://github.com/projectcaluma/caluma/commit/cb2739ed40a7afabf95f2ce0386b38dc07d919bb))

### Breaking
* The method `get_data` on data sources receives two new arguments `question` (caluma question model) and `context` (dict). The method `validate_answer_value` on data sources receives a new argument `context` (dict).  ([`cb2739e`](https://github.com/projectcaluma/caluma/commit/cb2739ed40a7afabf95f2ce0386b38dc07d919bb))


# v8.0.0-beta.20 (10 November 2022)

### Feature
* **workflow:** Include family field on case schema model ([`aea98f9`](https://github.com/projectcaluma/caluma/commit/aea98f9d24e9eba3ae82bb789a1bcb12f62f5324))
* **filters:** Add `visibleInDocument`-filter for questions ([`9f5caa2`](https://github.com/projectcaluma/caluma/commit/9f5caa2527e27fc4185d7fcca4339a60ec0ccb83))
* **analytics:** Enable reordering of analytics fields ([`59eadbc`](https://github.com/projectcaluma/caluma/commit/59eadbc799a2486f7606ce6d5d1eac3d12b86398))

### Fix
* Fix breaking change introduced in 59eadbc ([`34be9bf`](https://github.com/projectcaluma/caluma/commit/34be9bfedfd893e0dd86f117df8b61d011359f53))
* Remove order_by in field_ordering, refactor test ([`121a433`](https://github.com/projectcaluma/caluma/commit/121a433cbf12b7151aab7cab88611ab77f531adb))


# v8.0.0-beta.19 (27 September 2022)

### Fix
* **deps:** Pin graphene-django to v3.0.0b7 ([`3efc320`](https://github.com/projectcaluma/caluma/commit/3efc3209e79d8ea010802e9c11bd0e1b91f0c8b2))


# v8.0.0-beta.18 (12 September 2022)

### Feature
* **analytics:** Provide option labels ([`d1f7a38`](https://github.com/projectcaluma/caluma/commit/d1f7a380caa664e9b24dc6f205f212952a63e63c))
* **cases:** Add filter to exclude child cases ([`dd58f6c`](https://github.com/projectcaluma/caluma/commit/dd58f6c1d0f8df73b620616d061bc90f73a6a8e8))


# v8.0.0-beta.17 (9 September 2022)

### Fix
* **events:** Don't emit create work item events when updating ([`4f2f491`](https://github.com/projectcaluma/caluma/commit/4f2f4916d62e689b59b805bdfdb6bf12e76d53d7))

### Breaking
* The `saveWorkItem` mutation doesn't emit `pre_create_work_item` `post_create_work_item` anymore since this is not the expected behaviour.  ([`4f2f491`](https://github.com/projectcaluma/caluma/commit/4f2f4916d62e689b59b805bdfdb6bf12e76d53d7))


# v8.0.0-beta.16 (1 September 2022)

### Fix
* **redo:** Recalculate deadline after updating a redo work item to ready ([`f803fbe`](https://github.com/projectcaluma/caluma/commit/f803fbe9951b09bd677ba3b8c5dda88af258203b))
* **permissions:** Make sure user permission classes call super ([`6e1945b`](https://github.com/projectcaluma/caluma/commit/6e1945b7a75f15b9ffefcb33173d4202523147af))


# v8.0.0-beta.15 (26 August 2022)

### Feature
* **flow:** Allow flows to not have tasks in next if redoable is given ([`867b796`](https://github.com/projectcaluma/caluma/commit/867b796394c55fda5960d6b889cc594f55594b52))
* **reopen case:** Allow reopening child cases of ready work items ([`e073cad`](https://github.com/projectcaluma/caluma/commit/e073cad3afb204af18e484f6b59758fdcba09476))
* **workflow:** Add is_redoable property to work item schema ([`709965d`](https://github.com/projectcaluma/caluma/commit/709965d9822433b58e00d51ec71500fb4865a802))
* **workflow:** Add search answer filter to work item filters ([`0ceb2c6`](https://github.com/projectcaluma/caluma/commit/0ceb2c6db8405c7eb611cb58bca7881a51e22cdc))
* **caluma:** Add new work item order key ([`a794211`](https://github.com/projectcaluma/caluma/commit/a794211421846099173a72300309b693888eabe1))

### Fix
* **redo:** Fix workflow of work items in status redo ([`abbdb92`](https://github.com/projectcaluma/caluma/commit/abbdb924c4d8fa004d4c5eb0f56748218810de49))
* **analytics:** Handle None and ignore 0 in summary ([`d5c9669`](https://github.com/projectcaluma/caluma/commit/d5c96692c69db4323593563d3cda0298feba38dc))

### Breaking
* This removes the deprecated properties `userinfo` and `introspection` on the base user class which have been deprecated for a long time.  ([`b4fd9e2`](https://github.com/projectcaluma/caluma/commit/b4fd9e227f5e85c89f800b018e1ca2ae079c434b))
* This drops the `saveCase` mutation which has been deprecated for a long time.  ([`6cf701d`](https://github.com/projectcaluma/caluma/commit/6cf701d749e34182c6a2e495b3050f3f47bc17b6))


# v8.0.0-beta.14 (18 August 2022)

### Fix
* Exclude not supported questions from answer search
([`a27681c`](https://github.com/projectcaluma/caluma/commit/a27681ca59079c6783d4498e12f3cfcca17ba53a))
* Fix multifile migration again
([`d812956`](https://github.com/projectcaluma/caluma/commit/d812956cffde04f1d10ffc05e674a6942ef19892))
* Handle files from history that don't exist anymore in migration
([`21611c3`](https://github.com/projectcaluma/caluma/commit/21611c3636c4a66c67ff2f2593649feca2f6f547))


# v8.0.0-beta.13 (15 August 2022)

### Fix
* **historical-schema:** Fetch the correct historical files
([`2580e80`](https://github.com/projectcaluma/caluma/commit/2580e80fceb5bdaa2636ffbc30e1f9bf16eac46b))
* **form:** Migration problem with historicalanswer
([`a8633b6`](https://github.com/projectcaluma/caluma/commit/a8633b60acc0b3d1ecfc180faf3f4c611f82f293))
* Multiple fixes for analytics
([`e78b8d2`](https://github.com/projectcaluma/caluma/commit/e78b8d28a7349c953541c3b4953b8fe7f5476ac6))


# v8.0.0-beta.12 (5 August 2022)

### Feature
* **workflow:** Add ids filter to case
([`89b70ec`](https://github.com/projectcaluma/caluma/commit/89b70ecf4cc098b8d43d0ddfe87491483f1ab6ae))
* **form:** Multiple files in file questions
([`4600ed0`](https://github.com/projectcaluma/caluma/commit/4600ed09bbb3efab6d25308d74384eef8f1a97f1))
* **core:** Allow input type override
([`215cdb7`](https://github.com/projectcaluma/caluma/commit/215cdb75f8bff500fcad9f3c58d4593f0b60f4b4))
* Searchanswers in forms
([`6a75f17`](https://github.com/projectcaluma/caluma/commit/6a75f17dbc66605a0624fb8b3b3777b30450d513))

### Fix
* **form:** Fix and test search_answers
([`371a4f0`](https://github.com/projectcaluma/caluma/commit/371a4f0b019509d06b090908369710aafc2d48b0))
* **analytics:** Provide more correct supported functions in analytics
([`2130f34`](https://github.com/projectcaluma/caluma/commit/2130f34b367549cc71eb0977afc25984fc03bab7))
* **log:** Minio stat errors shouldn't be errors
([`701bafc`](https://github.com/projectcaluma/caluma/commit/701bafcd1ba0686a06b32c626928eaed0ca6e26b))
* **workflow:** Remove and fix ordering keys
([`409e54f`](https://github.com/projectcaluma/caluma/commit/409e54f3719205c07551b038f8de302708165de4))
* **schema:** Reopen case schema clarification
([`6153b45`](https://github.com/projectcaluma/caluma/commit/6153b453d92ace28593cb666dc7a399d2a7c9779))

### Breaking
* This renames the question type constant for file questions, and changes the
semantics of the answer value for file questions as well: It is now a list of
dicts instead of a single string. The response type for querying file(s) answers
now also is a list instead of a single dict.
([`4600ed0`](https://github.com/winged/caluma/commit/4600ed09bbb3efab6d25308d74384eef8f1a97f1))


# v8.0.0-beta.11 (6 July 2022)

### Feature
* **core:** Allow input type override ([`ec4c899`](https://github.com/projectcaluma/caluma/commit/ec4c8997187452a12e091d3e94c6851e7c235156))

### Fix
* **form:** Use potentially prefetched answer document set for table rows ([`58e0a7c`](https://github.com/projectcaluma/caluma/commit/58e0a7c16747f8f0ec9a92c90171e898bbbe98e0))
* **schema:** Reopen case schema clarification ([`a394273`](https://github.com/projectcaluma/caluma/commit/a3942731645dcb94cc64923664be0c3733892d14))


# v8.0.0-beta.10 (24 June 2022)

### Fix
* **document:** Fix label of copied dynamic options ([`00383fc`](https://github.com/projectcaluma/caluma/commit/00383fcb8cbe06bfd53e26067be33ad1bcc975a7))


# v8.0.0-beta.9 (24 June 2022)

### Fix
* **document:** Copy dynamic options when copying documents ([`67910d9`](https://github.com/projectcaluma/caluma/commit/67910d96b98721be9953920ca23bddc33f4521ea))
* ReopenCase should disregard WorkItems in status REDO ([`dded3a8`](https://github.com/projectcaluma/caluma/commit/dded3a8b1f54b4efcb4c654966dc2234d9909ddb))
* **deps:** Update dependencies of dependencies ([`e3a5de3`](https://github.com/projectcaluma/caluma/commit/e3a5de38c3a9b1d1456e9fbee6f108913dc7b6df))
* **form:** Set questions of searchAnswers as required ([`fb7ad5f`](https://github.com/projectcaluma/caluma/commit/fb7ad5feb120abeaf3ea45670fa5349c86eb8464))

### Breaking
* searchAnswers questions list is now required  ([`fb7ad5f`](https://github.com/projectcalum/caluma/commit/fb7ad5feb120abeaf3ea45670fa5349c86eb8464))


# v8.0.0-beta.8 (20 June 2022)

### Fix
* **default answer:** Don't set document when copying default answers ([`7b5ce74`](https://github.com/projectcaluma/caluma/commit/7b5ce74a8a62a8b0415226eb784cc8aae811f9c3))


# v8.0.0-beta.7 (9 June 2022)

### Fix
* **pivot_table:** Pass context to child query ([`34f59a2`](https://github.com/projectcaluma/caluma/commit/34f59a2aa6b0b9fc0fa1eed6fdf7c84e9e62c666))
* **build:** Conftest should be in generated package ([`b82b6b3`](https://github.com/projectcaluma/caluma/commit/b82b6b3f15cca05dc98fb0b4c2e1adb6d5da3eb5))


# v8.0.0-beta.6 (28 April 2022)

### Feature
* **ordering:** Remove unused ordering attributes and add missing ([`9cbdd7d`](https://github.com/projectcaluma/caluma/commit/9cbdd7d050a79fb0125523932fc0398e6f9b115c))
* **events:** Cleanup deprecated events ([`1bf5792`](https://github.com/projectcaluma/caluma/commit/1bf57920de8a96bef75a45078e7915c560b59bff))
* **filters:** Clean up all the old filter syntax ([`ad008cd`](https://github.com/projectcaluma/caluma/commit/ad008cd8b1d612b176114b4e3f4e3c5924e644b2))

### Breaking

#### Remove unused ordering attributes and add missing ([`9cbdd7d`](https://github.com/projectcaluma/caluma/commit/9cbdd7d050a79fb0125523932fc0398e6f9b115c))

This removes various orderings that do not make sense and were not used:

- On all connections:
  - `created_by_user`
  - `created_by_group`
  - `modified_by_user`
  - `modified_by_group`
- `Answer`
  - `document`
  - `file`
- `Document`
  - `source`

The following ordering attributes were added because they make sense:

- `Case`
  - `created_at`
  - `modified_at`
- `Flow`
  - `created_at`
  - `modified_at`
- `Task`
  - `created_at`
  - `modified_at`
- `Workflow`
  - `created_at`
  - `modified_at`
- `AnalyticsField`
  - `created_at`
  - `modified_at`
  - `alias`
- `DynamicOption`
  - `created_at`
  - `modified_at`
  - `slug`
  - `label`
  - `question`
- `Flow`
  - `created_at`
  - `modified_at`
  - `task`

#### Cleanup deprecated events ([`1bf5792`](https://github.com/projectcaluma/caluma/commit/1bf57920de8a96bef75a45078e7915c560b59bff))

The following deprecated events were removed:

- `created_work_item`
- `completed_work_item`
- `skipped_work_item`
- `suspended_work_item`
- `resumed_work_item`
- `completed_case`
- `created_case`
- `suspended_case`
- `resumed_case`
- `canceled_work_item`
- `cancelled_work_item`
- `canceled_case`
- `cancelled_case`

#### Clean up all the old filter syntax ([`ad008cd`](https://github.com/projectcaluma/caluma/commit/ad008cd8b1d612b176114b4e3f4e3c5924e644b2))

We have for a long time had two syntaxes for filtering, one of which was deprecated for over a year now and only kept for backwards compatibility. Finally, the old form has to go.

Old:
```graphql
query foo {
    allWorkItems(status: $status) {...}
}
```

New:
```graphql
query foo {
    allWorkItems(filter: [{status: $status}]) {...}
}
```

The new syntax also allows reusing the same filter type twice to narrow down the result set even more. It also supports inverting the filters to implement explicit exclusion. It is now time to get rid of the old syntax.

The following changes are breaking:

- Removed deprecated `slug` filters in favor or `slugs` filters
- Removed top level filters
- Removed `orderByQuestionAnswerValue` filter in favor of `documentAnswer` in the top level orderset
- Removed `orderBy` in filtersets in favor of top level `order` orderset
- Removed ordering by static meta attributes (configured with `META_FIELDS` in favor of `meta` in the top level orderset


# v8.0.0-beta.5 (19 April 2022)

### Fix
* **deps:** Lock graphql-core to 3.1.x to avoid import error ([`04f35c8`](https://github.com/projectcaluma/caluma/commit/04f35c8d26a78a2c8f8a5ab943e3326677929516))


# v8.0.0-beta.4 (13 April 2022)

### Fix
* **deps:** Bump django from 3.2.12 to 3.2.13 ([`76b9e0a`](https://github.com/projectcaluma/caluma/commit/76b9e0aae601cb5de1f58b2671461b62fe0aeea4))
* **docs:** Fix incorrect documentation of createdAfter and createdBefore filters ([`a8ba2bb`](https://github.com/projectcaluma/caluma/commit/a8ba2bb672939d9ad1676e7a7f19a29e66b8cb2d))


# v8.0.0-beta.3 (6 April 2022)

### Feature
* **analytics:** Support for additional starting objects ([`4f24b5b`](https://github.com/projectcaluma/caluma/commit/4f24b5be997e194e0547129e9a5e2d43553b53f5))
* **test:** Fixture for running a block of code at a given faked time ([`8e3ab7a`](https://github.com/projectcaluma/caluma/commit/8e3ab7a1ba389871c92143e7ca1494fdc18d2163))
* Reopen case and ready work items ([`ed7ff26`](https://github.com/projectcaluma/caluma/commit/ed7ff267c08b5ed0e3258a1e527b492eb4e2fe93))
* **analytics:** Summary row ([`4e7bd5c`](https://github.com/projectcaluma/caluma/commit/4e7bd5c391159fccab38f77d949c66251401457f))
* **analytics:** Pivot table implementation ([`ccc6bab`](https://github.com/projectcaluma/caluma/commit/ccc6bab44a87d7b766f531694f4805ef5828b77c))
* **test:** Add at_date fixture ([`649f657`](https://github.com/projectcaluma/caluma/commit/649f65735faf5b9e2adb7d5020dab744fd58cf3d))

### Fix
* **docker:** Fix standalone docker image command ([`93f2158`](https://github.com/projectcaluma/caluma/commit/93f215873cc82dbecc34aa4e21d477d77aa6b025))
* **filter:** Do not crash on empty query param in filter ([`c9bb93c`](https://github.com/projectcaluma/caluma/commit/c9bb93c5204eba263f6bd96eb4d4b96a4faff6d2))
* **graphene:** Write a failing test for the getRootForms query ([`d2dd1af`](https://github.com/projectcaluma/caluma/commit/d2dd1af6261ce85265f046fc54a1db59b739a358))


# v8.0.0-beta.2 (24 March 2022)

### Fix
* **relay:** Make extraction of global ids more defensive ([`392b4f7`](https://github.com/projectcaluma/caluma/commit/392b4f7ce920c0bb308f9d465c24b6d1cba97acb))

# v8.0.0-beta.1 (23 March 2022)

### Fix
* **workflow:** Fix creating work items when completed ones exist ([`b2cc0a8`](https://github.com/projectcaluma/caluma/commit/b2cc0a866888595be3010e71ca0a3d543fc6eb51))
* **document:** Remove duplicate filtering on answer ([`c92f3ed`](https://github.com/projectcaluma/caluma/commit/c92f3ede09d782478d4c7aff487bde42c56f999c))


# v8.0.0-beta.0 (17 March 2022)

### Feature
* **workflow:** Allow multiple instance work items to continue async ([`510ce48`](https://github.com/projectcaluma/caluma/commit/510ce48002efaf5d62d39069419dc5759fd44258))
* **workflow:** Only create work item if they don't exist yet ([`7e32891`](https://github.com/projectcaluma/caluma/commit/7e32891f120811d3f8fcda4d07ce049a499c0928))
* **analytics:** Introduce analytics table ([#1572](https://github.com/projectcaluma/caluma/issues/1572)) ([`94db1d3`](https://github.com/projectcaluma/caluma/commit/94db1d33d00134e451333e4c184f99b7d3434aac))
* **workflow:** Implement WorkItem redo pattern ([#1656](https://github.com/projectcaluma/caluma/issues/1656)) ([`d01e284`](https://github.com/projectcaluma/caluma/commit/d01e28405e8d1419a6e357149b543c39ea8025f6))

### Fix
* **graphene:** Avoid default connection limit ([`edaf287`](https://github.com/projectcaluma/caluma/commit/edaf287ca3a57626e1e33de1aa9eab637c8b5f22))
* **validation:** Only skip validation for none or empty strings ([`9603db4`](https://github.com/projectcaluma/caluma/commit/9603db4594da651f7118702422a0311277191ae8))
* **format-validators:** Don't run format validation on empty values ([`ce2f5ca`](https://github.com/projectcaluma/caluma/commit/ce2f5ca79d57b350affd975b5a9fbb6064ca1bb5))
* **analytic:** Add default ordering for fields and available fields ([`513de29`](https://github.com/projectcaluma/caluma/commit/513de291a107e58961394c796f6a9579f4cd1698))
* **analytics:** Parse date parts to integer for consistency ([`28c3387`](https://github.com/projectcaluma/caluma/commit/28c3387071fae14f1c5a6e2d3154b256b6c8e342))
* **options:** Keep order of selected options the same as the value ([`d57cd12`](https://github.com/projectcaluma/caluma/commit/d57cd12bbb48eeae3828f9c44af3e16168cbfd25))
* **deps:** Fix deprecation warning for collections module ([`4476805`](https://github.com/projectcaluma/caluma/commit/4476805fa3fefb3a9e432eeffbd94c987d7bfeed))
* Restrict valid filters for choice questions ([#1680](https://github.com/projectcaluma/caluma/issues/1680)) ([`549d24d`](https://github.com/projectcaluma/caluma/commit/549d24d0281b9df29da69257f83d36d719884269))
* **form:** Update or create answers when copying to a new document ([`ca0d17e`](https://github.com/projectcaluma/caluma/commit/ca0d17e3c26b30a3fa055b0c40d00b909bc798dd))

### Breaking
* If you run Caluma as a Python module and still run 3.7, this will break ([`94db1d3`](https://github.com/projectcaluma/caluma/commit/94db1d33d00134e451333e4c184f99b7d3434aac))

### Documentation
* Fix links in README.md ([`43afdf5`](https://github.com/projectcaluma/caluma/commit/43afdf55eabab8bcbc6054aa1e03757fbf92890a))


# v7.15.2 (20 March 2022)

### Fix
* **document:** Remove duplicate filtering on answer ([`c92f3ed`](https://github.com/projectcaluma/caluma/commit/c92f3ede09d782478d4c7aff487bde42c56f999c))


# v7.15.1 (15 March 2022)

### Fix
* **graphene:** Avoid default connection limit ([`23969ee`](https://github.com/projectcaluma/caluma/commit/23969ee56291fd59ccdc6d418e30c726fa3aadce))


# v7.15.0 (25 January 2022)

### Feature
* **workflow:** Implement WorkItem redo pattern ([#1656](https://github.com/projectcaluma/caluma/issues/1656)) ([`d01e284`](https://github.com/projectcaluma/caluma/commit/d01e28405e8d1419a6e357149b543c39ea8025f6))
* **form:** Enable hint messages on questions ([#1655](https://github.com/projectcaluma/caluma/issues/1655)) ([`7adf401`](https://github.com/projectcaluma/caluma/commit/7adf4014c220bdf582c3b7fcbaf98f421ef40092))

### Fix
* **settings:** Use int for MINIO_PRESIGNED_TTL_MINUTES ([#1632](https://github.com/projectcaluma/caluma/issues/1632)) ([`cc9f89f`](https://github.com/projectcaluma/caluma/commit/cc9f89f7d356038851f1fa3f9ec343d60e5ee256))


# v7.14.3 (20 March 2022)

### Fix
* **document:** Remove duplicate filtering on answer ([`c92f3ed`](https://github.com/projectcaluma/caluma/commit/c92f3ede09d782478d4c7aff487bde42c56f999c))


# v7.14.2 (10. March 2022)

### Fix
* **validation:** Only skip validation for none or empty strings ([`b030904`](https://github.com/projectcaluma/caluma/commit/b030904bcbd663398af7a1db07a3174074bb9324))
* **format-validators:** Don't run format validation on empty values ([`dcea2b5`](https://github.com/projectcaluma/caluma/commit/dcea2b5cbade42ce7509b9a538dec96dd49810e2))


# v7.14.1 (16. February 2022)

### Fix
* **form:** Update or create answers when copying to a new document ([`9f436af`](https://github.com/projectcaluma/caluma/commit/9f436afe58aea07d39241034ac247e57f9d6103c))


# v7.14.0 (1 December 2021)

### Feature
* **config:** Validate permission decorators ([#1615](https://github.com/projectcaluma/caluma/issues/1615)) ([`a63a6d3`](https://github.com/projectcaluma/caluma/commit/a63a6d34e075fd086647cdfbd36b5eb8cbf83850))
* Expose more CORS related configurations via environment variables ([`d88165c`](https://github.com/projectcaluma/caluma/commit/d88165c3fbb738fc9fc675cb74c4730a2d91ce4e))
* **form:** Add new action button question type ([`2b3086f`](https://github.com/projectcaluma/caluma/commit/2b3086fec19658c2ea27a6f7ed089817d31da550))
* **workflow:** Extend group jexl context object ([`ce3f4fe`](https://github.com/projectcaluma/caluma/commit/ce3f4feaed3434ddb3008623920371edc37a6331))
* **events:** Allow the `sender` to be used in filter_events ([`6104cbd`](https://github.com/projectcaluma/caluma/commit/6104cbd5589ed9dba00b973c2ed0cb085314611c))
* **signals:** Introduce event filter ([`e597a99`](https://github.com/projectcaluma/caluma/commit/e597a99020f937538605fe02c494ec05e0354ec1))

### Fix
* **selected_options:** Handle selected options if value is empty array ([#1621](https://github.com/projectcaluma/caluma/issues/1621)) ([`f097912`](https://github.com/projectcaluma/caluma/commit/f097912575dc213b3a70b4e51610bc8ffe620aad))
* **schema:** Define interface for dynamic questions ([`d607544`](https://github.com/projectcaluma/caluma/commit/d60754476884ba97447f4ed4aef93c800849ba1a))
* Set created_by fields on FormQuestions ([`89ba971`](https://github.com/projectcaluma/caluma/commit/89ba971a342c958abfd08c7858ce9b507ec319ab))

### Documentation
* Fix custom visibility code snippet ([`d4abb69`](https://github.com/projectcaluma/caluma/commit/d4abb695c1391d6153a3b8e80109d86235b1c740))
* **guide:** Update guide to use ember-caluma v9 addons ([`4d3c9fc`](https://github.com/projectcaluma/caluma/commit/4d3c9fcd0b4d78cefa58c73bb4383daf318c03be))


# v7.13.0 (27 August 2021)

### Feature
* **config:** Introduce configurable user factory ([`8a49aaf`](https://github.com/projectcaluma/caluma/commit/8a49aaf7f911d4df50a354915530bfcd034ec91b))

### Fix
* **documentation:** Updated readme to reflect that GraphiQL is not available anymore ([`b6204e8`](https://github.com/projectcaluma/caluma/commit/b6204e8c89308a4878590c7026744af547f69a90))
* **serializers:** Do not implicitly monkeypatch rest framework ([`86b8a05`](https://github.com/projectcaluma/caluma/commit/86b8a05eaa7de391a2e650445f4f4cbb2ac02d25))
* Prettier choice question error message ([`acbc25c`](https://github.com/projectcaluma/caluma/commit/acbc25ca55b6e0dc339ec67ee19e1f712376938b))



# v7.12.0 (23 June 2021)

### Feature
* **jexl:** Allow optional answer transforms with default value ([`72dfa5b`](https://github.com/projectcaluma/caluma/commit/72dfa5bdf532025cb4ea35d671b944c011969a4a))


# v7.11.3 (10 June 2021)

Minor release only containing dependency updates. The release is done mainly because if this commit:

 * chore: update pyjexl [`03546ce`]\
   The bugfix https://github.com/mozilla/pyjexl/pull/23 (short-circuit
   evaluation) is critical for us, so we're pulling it in explicitly until
   there is a new pyjexl release.


# v7.11.2 (8 June 2021)

### Fix
* Extend uwsgi buffer ([`324d9d3`](https://github.com/projectcaluma/caluma/commit/324d9d397173cf2033600d12316dbce7bf23156c))
* **form:** Fetch selected_options of corresp. question and document ([`df97a5d`](https://github.com/projectcaluma/caluma/commit/df97a5de83c3190164dda57aa3712d5b421b4867))

# v7.11.1 (7 June 2021)

### Fix
* **validation:** Exclude hidden cells in answer transforms for tables ([`36b0972`](https://github.com/projectcaluma/caluma/commit/36b09720da6ef3e5a57da725ce65c1b6ba4e9ee3))


# v7.11.0 (28 May 2021)

### Feature
* Make selected option(s) accessible from answers
([`824d9a8`](https://github.com/projectcaluma/caluma/commit/824d9a87bf0ffb498e11b93388e84150c497ae2b))
* **forms:** Add question filter for forms
([`142e18b`](https://github.com/projectcaluma/caluma/commit/142e18b592a8d1ca6987be18f2245edbc4577ccd))
* **question:** Add filters for sub and row form on questions
([`3b14abf`](https://github.com/projectcaluma/caluma/commit/3b14abf825840aeaf9e97e0a2c3c4085a43f9bb0))


# v7.10.0 (23 April 2021)

### Feature
* Add IN lookup for json fields (#1472) (95bc2c3c88cab3d68137996a3daafdf3a1dd6c42)

### Fix
* Fix regression for union visibilities (e9a948c851e1bb9266e3e64205c9f21d0b3dca72)


# v7.9.1 (20 April 2021)

### Fix
* **document:** Pass current user to copy document function ([`178602f`](https://github.com/projectcaluma/caluma/commit/178602f1d57c1413cbc5d84a38f98923fa4c4f10))


# v7.9.0 (31 March 2021)

### Feature
* Health endpoint ([#1354](https://github.com/projectcaluma/caluma/issues/1354)) ([`bfc4951`](https://github.com/projectcaluma/caluma/commit/bfc49516caafaef216d00bfec4bdfb1047af77c9))

### Fix
* **workflow:** Correctly set workitem name from task ([#1448](https://github.com/projectcaluma/caluma/issues/1448)) ([`1095de4`](https://github.com/projectcaluma/caluma/commit/1095de43e319c4b89ab80a304ff031763beca4c4))


# v7.8.1 (30. March 2021)

### Fix
* **form:** Modified_content on row documents ([`75822ef`](https://github.com/projectcaluma/caluma/commit/75822efd29bc5cfc96af205631cfb4975666b43a))
* **file:** Ignore errors due to missing file ([#1440](https://github.com/projectcaluma/caluma/issues/1440)) ([`63d9f94`](https://github.com/projectcaluma/caluma/commit/63d9f94a5fb7de749dd2074f28acdaebd3409ec5))


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
