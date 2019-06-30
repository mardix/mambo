## CLI

[TOC]

The Mambo makes a `mambo` executable available to you in your terminal.

NOTE: Besides `mambo setup`, all commands must be executed in the directory containing the Mambo files.


### `mambo setup` 

To create a new site directory and initialize Mambo in it.

```html
 cd ~
 mambo setup mysitename.com
```

### `mambo init` 

Initialize Mambo in the current directory if it doesn't exist

```html
mambo init
```

### `mambo create`

Allows to create new pages. By default pages will be created as `.html`, to create them as markdown, add the `.md` as file extension. Page can only be either `html` or `md` (markdown), any other format will be ignored.

```html
mambo create hello-world 
```

#### Create multiple pages

To create multiples pages, separate them by space

```html
mambo create hello-world page1.md pag2.html another-page
```

### `mambo serve` 

To serve the site in development mode. By default it will run on port `8000` -> `127.0.0.1:8000`, a browser window will be open. 

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

### `mambo build`

Build the site to be deployed to production servers. The content will be placed in `.build` directory, which can be uploaded to AWS, Netlify, Firebase, FTP, etc.

```html
mambo build
```

#### Options

```html
-i | --info [ -i ] boolean, default False: To display build information
--env [ --env prod ] : Select the environment to build

```

### `mambo clean`

To cleanup the `.build` directory

```html
mambo clean
```