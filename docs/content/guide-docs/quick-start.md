## Quick Start

[TOC]

### Requirements

Mambo requires Python 3.6+

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

To serve the site in development mode, cd into the directory and run, a browser window will be open. By default it uses port 8000

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

Build the site to be deployed to production servers. The content will be placed in `.build` directory, which can be uploaded to AWS, Netlify, Firebase, FTP, etc.


```html
mambo build
```

#### Options

```html
-i | --info [ -i ] boolean, default False: To display build information
--env [ --env prod ] : Select the environment to build

```

