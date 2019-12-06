# Caluma: Guide

## About this guide

Goals:
- get a simple app running
- understand concepts behind caluma
  - build a form
  - design a simple workflow

## Installation

To install Caluma, you'll need to have [Docker](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/) installed on your system.

Afterwards, create a new directory for your project, copy our [example docker-compose.yml file](https://github.com/projectcaluma/caluma/blob/master/docker-compose.yml) into it and finally run the following command:

Per default, Caluma is running with production settings. To bypass the security-related configuration steps needed for a prodoction system, create a new file called `docker-compose.override.yml` with the following content:

```yml
version: "3.4"
services:
  caluma:
    environment:
      - ENV=development
```

Set the UID of the user inside the container::

```bash
echo "UID=$(id --user)" > .env
```

Afterwards, start the containers by running

```bash
docker-compose up -d
```

You can now access [GraphiQL](https://github.com/graphql/graphiql) at [http://localhost:8000/graphql](http://localhost:8000/graphql). We'll use graphiql to interact with the Caluma service in the coming sections.

Install the ember.js framework. Therefore you need [node.js](https://nodejs.org/en/) and [npm](https://www.npmjs.com/get-npm).

To install ember.js run

```bash
npm install -g ember-cli
```

Create a new ember app

```bash
ember new caluma-demo
```

Inside the new app install the ember-caluma addon

```bash
ember install ember-caluma
```

## Ember-caluma (set up the frontend)

To make `ember-caluma` work a few steps must be followed. The
form builder is a [routable engine](http://ember-engines.com) which must be mounted in `app/router.js`:

```bash
Router.map(function() {
  // ...

  this.mount("ember-caluma", {
    as: "form-builder",
    path: "/form-builder"
  });
});
```

To make `ember-apollo-client` work, we need to pass it as dependency for our engine in `app/app.js`. Additionally, we need to specify `ember-intl` as a dependency so that the the application has access to the addon's translations.

```bash
const App = Application.extend({
  // ...

  engines: {
    emberCaluma: {
      dependencies: {
        services: [
          "apollo", // ember-apollo-client for graphql
          "notification", // ember-uikit for notifications
          "router", // ember router for navigation
          "intl", // ember-intl for i18n
          "caluma-options", // service to configure ember-caluma
          "validator" // service for generic regex validation
        ]
      }
    }
  }
});
```

Also, since our form builder needs to customize the apollo service in order to support [fragments on unions and interfaces](https://www.apollographql.com/docs/react/advanced/fragments.html#fragment-matcher), create a new service `app/services/apollo.js` and extend the apollo service with the provided mixin:

```bash
import ApolloService from "ember-apollo-client/services/apollo";
import CalumaApolloServiceMixin from "ember-caluma/mixins/caluma-apollo-service-mixin";

export default ApolloService.extend(CalumaApolloServiceMixin, {});
```

It is crucial to define the options for the apollo service in
`config/environment.js`:

```bash
module.exports = function(environment) {
  // ...

  apollo: {
    apiURL: "/graphql"
  },
};
```

To use the ember-uikit notification service, it ist important to 
config some attributes in `ember-cli-build.js`:

```bash
module.exports = function(defaults) {
  let app = new EmberApp(defaults, {
    "ember-uikit": {
      notification: {
        "timeout": 5000,
        "group": null,
        "pos": "top-center",
      }
    }
  });
```

Last but not least import `ember-uikit` and `ember-caluma` to
apply styling in `app/styles/app.scss`:

```bash
// https://github.com/uikit/uikit/blob/master/src/scss/variables-theme.scss
// custom variable definitions go here

$modal-z-index: 1;
@import "ember-uikit";
@import "ember-caluma";
```

To show some texts in the form-builder you have to add translations to
`translations/en-us.yaml`. As example like this:

```yaml
caluma:
  form-builder:
    global:
      optional: optional
      save: Save
    question:
      widgetOverrides:
        powerselect: Powerselect
    form:
      all: All petitions
      new: New petition 
      empty: You don't have any petitions yet.
      name: Name
      slug: Slug
      description: Description
      isArchived: Archived
      isPublished: Published
    notification:
      form:
        create:
          error: Error
```
