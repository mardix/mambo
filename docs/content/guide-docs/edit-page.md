## Edit Pages

To create a new page, 

```html
mambo create your-page-name
```

or multipage with

```html
mambo create hello-world page1.md pag2.html another-page
```

### Front Matter

Front-matter is a block of YAML at the beginning of the file that is used to configure settings for that page. Front-matter is started and terminated by three dashes

```yaml
---
title: This is a title
description: This is a description
tags:
  - a
  - b
  - c
---
```

{% raw %}
Data from your front matter can easily be accessed in the template `{{ page.* }}`, ie: `{{ page.title }}` will display the title.
{% endraw %}

### Templating

### Data

Mambo allows you to use data to populate your template. The data can come from the page directly from the frontmatter, or the global site data,  or from a collection of files, a json file file,

#### Page Data

{% raw %}
```
{{ page }}
```
{% endraw %}

#### Site Data

{% raw %}
```
{{ site }}
```
{% endraw %}

#### Collection Data

{% raw %}
```
{{ page.collections }}
```
{% endraw %}

#### JSON Data

{% raw %}
```
{{ data }}
```
{% endraw %}

### Single File Component

