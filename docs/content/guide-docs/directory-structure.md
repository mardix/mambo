## Directory Structure


```
.
|
├── pages/
|
├── static/
|
├── content/
|
├── data/
|
├── templates/
|
├── mambo.yml
|
└── .build/

```

{% raw %}
### pages

Pages are the building blocks of the sites. Any `.html` or `.md` file in this directory will be rendered as a page. 

Pages are composed of frontmatter, template and content.

Jinja2 is the template engine used in the template pages.

Pages have access to the following context: `{{ page.* }}`, `{{ site.* }}`, `{{ data.* }}`, including all the methods and filters available.

They will created the same way they are created under the pages folder, and for convenience, they will be `pretty-url` where the extension of the file will not be displayed.


```
/pages/
|
├── index.html    # => https://mysitename.com/
├── contact.html  # => https://mysitename.com/contact
├── /about/
|   ├── organization.html  # => https://mysitename.com/about/organization
```

### static

Hold the static assets files. This directory will be copied to the `.build` directory as is.

To link to files from this directory, `static_url` is a global function that will return the full path of the file. ie: `<img src='{{ static_url('my-image.png') }}'>`



### content

Contains page content to be included on the page. Files must be in either `.html` or `.md` file.
This is created for the organization of the site. But it is identical to *templates* folder. 

However, when including files from content, the path must be prefixed with `content/`,  

```html 

<h1>Some text</h1>

{% include "content/my-file.md" %}

```

### data

Contains JSON files that can be used in the template.

The data is placed in the `{{ data }}` global context. It uses the name of the file as the data key. For example if a file is name `data/cars.json`, it will be access at `{{ data.cars }}`

To exclude a file, prefix it with an underscore. ie  `_w.json`. 


```
# data/cars.json
{
  "list_cars": ["BMW", "Benz", "Audi", ]
}

#------

# pages/my-cars.html

<ul>
  {% for car in data.cars.list_cars %}
  <li>{{ car }}</li>
  {% endfor %}
</ul>


```

### templates

Contains templates files of the sites. This includes layouts, partials, macros etc. Anything related to templates should be placed in here. If you want to create a content file to include, it is recommended to place it in the `/content` folder.

### .build

Contains the rendered site with all the pages and assets. This directory is purged and regenerated on each `build` or `serve`.

When your site is ready to be deployed by using `mambo build`, that's the directory to upload to your server.


### mambo.yml

`mambo.yml` is the global configuration file. It's placed at the root of the site. Refer to Config docs for more info.

{% endraw %}
