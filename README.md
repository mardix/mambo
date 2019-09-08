
# Mambo 

Mambo is an elegant static site generator built in Python. 

It’s a great choice for website, blogs and documentation. Content can be written in HTML and Markdown, oganized however you want with any URL structure, and metadata can be defined in front-matter. 

---

[TOC]

---

## Command Line API

Mambo aims to be simple with a simple API.

### Install

```
pip install mambo
```
    
### Setup a site 

To setup a site, the command below will create a new directory name `/mysitename.com/`. All the necessary files and folders will be created in there.

```html
 cd ~
 mambo setup mysitename.com
```

#### Or initialize in an existing folder

All the necessary files and folders will be created in there.

```html
cd ./mysitename.com
mambo init
```

### Create a page

The command below will create a `hello-world.html` by default. To create it as markdown, add the `.md` as file extension. Page can only be either `html` or `markdown`, any other format will be ignored.

```html
mambo create hello-world 
```

#### Create multiple pages

To create multiples pages, separate them by space

```html
mambo create hello-world page1.md pag2.html another-page
```


### Serve site in dev mode 

To serve the site in evelopment mode, cd into the directory and run, a browser window will be open. By default it uses port 8000

```html
mambo serve
```

#### Options

```html
-p | --port [ -p 8001 ]: Use the specified port. Default 8000
--env [ --env prod ] : Select the environment to build
--no-livereload [ --no-livereload ]
--open-url [ --open-url ]

```

### Build site for production 

Build the site to be deployed to production. The content will be placed in `.build` directory, which can be uploaded to any servers.

```html
mambo build
```

#### Options

```html
-i | --info [ -i ] boolean, default False: To display build information
--env [ --env prod ] : Select the environment to build

```

### Clean the build directory 

To cleanup the `.build` directory

```
mambo clean 
```

---

## Structure 

```
    |
    |-- /.build
        |
    |-- /static
        |
    |-- /data
        |
    |-- /pages
        |
    |-- /content
        |
    |-- /templates
```

**/pages**:
    Contains all the pages to be built
    If the pages contain local context -> {{ page.title }}

**/static**: Hold the assets static files. This directory will be copied to the `build` as is

**/data**:
    Contains JSON data context to inject in the templates.
    To access the data, use the file name as as the namespace -> mydata.json -> {{ data.mydata }}

**/content**:
    Contains page content to be included on the page. 
    This can be an .md file, .html
    This is created for organization of the site. But it is 
    identical to *templates* folder. 
    However, when including files from content, the path must be prefixed with `content`, 
    ie: `{% include "content/my-file.md" %}`


**/templates**:
Contains all the templates to be included, including layouts, partials, macros. Anything related to templates should be placed in here. If you want to create a content file to include, it is recommended to place it in the `content` folder.

**/.build**: This where the build sites will be created. The content of this dir is ready for upload

---

## Configuration

Mambo creates `mambo.yml` which contains the configurations.

```
# Site: Global site context
# Variables under [site] will be available in the page as ie: {{ site.name }}
site:

  # base_url: REQUIRED - Site base url, the canonical url to build
  base_url: /

  # static_url: REQUIRED - Site static. If static files are placed somewhere else, you can put the path there
  static_url: /static/

  # Site name
  name: "MySiteName.com"

  # The site url
  url: 

  # Google Analytics code
  google_analytics:

  # Site Favicon
  favicon:

  # Global meta tags. They can be overwritten by page meta tags
  meta:
    keywords:
    language: en-us
    rating: General
    robots: index, follow


# Site environment: environment data will be merged with the global site settings
# ie: 'env.prod.base_url' will use the prod base_url
# At build: 'mambo build --env prod', or serve 'mambo serve --env prod'
env: 
  prod:
    base_url: /
    static_url: /static/


# Configuration when serving
serve:
  port: 8000
  livereload: True
  openwindow: True
  env: 
  generate_sitemap: True
  minify_html: False  


# Build configuration, could be the final product
build:
  # env: The site_env to build. Leave blank to have the option in the command line
  env: prod
  generate_sitemap: True
  minify_html: True 

# Global settings
globals:
  # layout: **REQUIRED - The default site layout
  layout: "layouts/default.html"

  sitemap
  
  assets
  
```

---

## Global Context

**page_url($page_name)** 

To get the url of a page.

`{{ page_url('home') }}`


**page_link($page_name, $text, $title, $id, $class)**

To build a page ahref 

`{{ page_link('about.html', title='About Us') }}`


**page_info($page_name, $key)**

Return a page meta info

`Title: {{ page_info('home', 'title')}}`


**static_url($file_path)**

Return the  url of a static asset

`{{ static_url('imgs/img.png') }}`


**script_tag($file_path)**

Create a script tag for a static file

`{{ script_tag('js/main.js') }}`


**stylesheet_tag($file_path)**

Create a stylesheet tag for a static file

`{{ stylesheet_tag('css/style.css') }}`

**format_date($date, $format)**

Format a date

`{{ format_date('2019-09-01', 'MM/DD/YYYY h:mm a') }}`


**\_\_STATIC_URL__**

Return the static url

`const static_url = "{{ __STATIC_URL__ }}" `


**[[\_\_STATIC_URL__]]**

Same as \_\_STATIC_URL__ but to be used SFC javasipt


## Site Context

**site**

All the context under the site config

```
name
base_url
static_url
...
__env__: the environment (Prod, Dev etc)
__generator__: info of the generator
    timestamp
    name
    version
```


## Page Context

**page**

All the page context and data set in the frontmatter

```
title
description
url
...
```




---

## Writing Pages

### Supported format:

Mambo support  `.html` and `.md` files. It will ignore all other extensions in the `/pages` directory

Files starting with `_` (underscore) will be ignored

### Organization:

The pages in Mambo should be arranged in the same way they are intended for the rendered website.
Without any additional configuration, the following will just work. Mambo supports content nested at any level.

    /pages
        |
        |- index.html               // <- http://a.com/
        |
        |- about-us.md              // <- http://a.com/about-us
        |
        |- /post
            |
            |- my-awesome-post.html // <- http://a.com/post/my-awesome-post.html


### Front Matter & Page Context

It enables you to include the meta data and context of the content right with it.
It only supports the Yaml format, it is placed on top of the page. 

    ---
    title: My site title
    slug: /a-new-path/
    description: 
    
    ---

Your front matter data get parsed as a local object, ie: {{ page.title }}

You can also include your own context


### Simple Pages

#### Single File Component Page

##### Template

##### Script

##### Style

Optionally you can use SCSS 


---

### Writing Dynamic Pages

---

## About

Mambo is built in Python, and features the powerful templating language Jinja2. 

Mambo allows you to write your content in either Markdown or plain HTML. 

HTML gives you full independence. Markdown, for simply writing article.

To get creative, Mambo allows you to write your HTML/JS/CSS in a single file component style. All three are powered by the powerful Jinja2 template language.

Features:

- Friendly Url
- Jinja
- HTML
- Markdown
- SCSS 
- Single file component


Technology uses:

- Jinja2: Powerful templating language
- Front Matter, to add context to the page
- Arrow to write date and time

---




## Content:



# Advanced

## Data Driven

In addition to data files, you can load a resource from any api endpoint. 

The data returned must be in the json format.



## Generators

To generate pages dynamically from a data source

##### context

Generators return a `context` key in the page variable. 

For `single` type, the context is the data for that page

For `pagination` type, the context is a list (array) of data chunk

##### paginator

Generators returns `paginator` key in the page variable, if the `type` is 'pagination'

`pagination` contains: `total_pages`, `current_pages`, `page_slug`, `index_slug`


### Generator: Single

Generate single pages from a source containing list (array) of data

    ---
    
    _generator:
        type: single
        data_source: posts
        slug: /
    ---

`data_source`:  Dot notation can be use to 
 access other node of the data: ie: 
 
    // data/posts.json
    
    {
        "all": [
            {},
            ...
        ],
        "archived": [
            {},
            ...
        ]
    }

You can access the data as:
    
    data_source: posts.archived


`slug`: Will dynamically build the slug. Having the `slug` will overwrite the 
data slug if it has one. 

`slug` format based on the data, so data token must be provided 

ie: `/{post_type}/{id}/{post_slug}`

### Generator: Pagination

Will generated a paginated 

    ---
    
    _generator:
        type: pagination
        data_source: posts
        per_page: 20
        limit: 100
        slug: /all/page/{page_num}
        index_slug: /all
    ---

---

## Single File Component

Single file component allows you to put together HTML, CSS, and JS into one file.

Upon building, Mambo will separate them and 
place them into their respective files to be 
included in the page.

```
---
title: My Page Title
---

{# Page body #}
<template>
    <h1>Hello</h1>
    <button id="myButton">My Button</button>
</template>


{# Page style #}
<style>
    .color-button {
        color: blue;
    }
</style>


{# Page script #}
<script>
    const button = document.querySelector('#myButton');
    button.addEventListener('click', () => {
        button.classList.toggle('color-button');
    });

</script>


```


## TODO
 
RSS



## WIP

## Context Variables

### site

### page
This variable holds the current page or tag object.

### data

### __info__

## Methods


## Features

- Sitemap
- Collections
- Assets
- Cache busting

Front matter

```
title:
url:
description:
collections:
 url: /post/{url}
 data_file
 content_dir
assets:
 scripts:
    -
 stylesheets:
    -
```