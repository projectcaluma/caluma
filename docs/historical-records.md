# Historical Records


Caluma stores every data change to the database. You can use this as an audit
trail, or implement "undo" user interfaces on top of it.
It uses [django-simple-history](https://github.com/treyhunner/django-simple-history)
for this purpose.

While you cannot disable storing historical data via configuration, it is by default not
exposed in the GraphQL API. To enable it, set `ENABLE_HISTORICAL_API` to `true`
(see [configuration.md](configuration.md) for further information).

## Cleanup

You may want to periodically cleanup the historical records. There are
three commands available for this:

 - `clean_duplicate_history`: Historical records are always created when `save()` has been called on a model. This command removes all duplicates.
 - `clean_old_history`: Remove all historical records, or the ones that are older than specified.
 - `cleanup_history`: Remove historical records that have a foreign key to a deleted related model. Supported are caluma_form models: `Answer`, `Document` and `DynamicOption`.
