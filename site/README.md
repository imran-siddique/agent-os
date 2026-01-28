# Agent OS Documentation Site

This directory contains the Jekyll-based documentation site for Agent OS.

## Local Development

### Prerequisites

- Ruby 3.0+
- Bundler

### Setup

```bash
cd site
bundle install
```

### Run locally

```bash
bundle exec jekyll serve
```

Visit http://localhost:4000

### Build for production

```bash
JEKYLL_ENV=production bundle exec jekyll build
```

## Site Structure

```
site/
├── _config.yml           # Jekyll configuration
├── _includes/            # Partial templates
│   └── head_custom.html  # Custom head (SEO/AEO)
├── _layouts/             # Page layouts
├── assets/
│   ├── css/              # Stylesheets
│   └── images/           # Images
├── docs/                 # Documentation
│   ├── concepts/         # Core concepts
│   ├── tutorials/        # Step-by-step guides
│   ├── api/              # API reference
│   ├── modules/          # Module documentation
│   ├── integrations/     # Framework integrations
│   └── extensions/       # IDE extensions
├── learn/                # Learning resources
├── use-cases/            # Industry use cases
├── compare/              # Comparison pages
├── faq/                  # FAQ (AEO optimized)
├── blog/                 # Blog posts
├── glossary.md           # Terminology glossary
└── index.md              # Homepage
```

## SEO/AEO Optimization

The site is optimized for search engines and AI answer engines:

### SEO Features
- Meta tags (title, description, keywords)
- Open Graph tags for social sharing
- Twitter Card tags
- XML sitemap (auto-generated)
- robots.txt
- Canonical URLs
- Semantic HTML structure

### AEO Features
- Schema.org structured data
- FAQ page with FAQPage schema
- HowTo schema for tutorials
- SoftwareApplication schema
- Organization schema
- Clear, direct answers to common questions

## Adding Content

### New Documentation Page

```markdown
---
layout: default
title: Page Title
parent: Parent Section
nav_order: 1
permalink: /docs/section/page/
description: "Page description for SEO"
---

# Page Title

Content here...
```

### New Tutorial

```markdown
---
layout: default
title: Tutorial Title
parent: Tutorials
grand_parent: Documentation
nav_order: 1
permalink: /docs/tutorials/tutorial-name/
description: "Tutorial description for SEO"
---

# Tutorial Title
{: .no_toc }

Brief description.
{: .fs-6 .fw-300 }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Step 1: ...
```

### New Blog Post

```markdown
---
layout: post
title: "Blog Post Title"
date: 2026-01-28
author: Author Name
categories: [category1, category2]
tags: [tag1, tag2]
description: "Post description for SEO"
---

Content here...
```

## Deployment

The site auto-deploys to GitHub Pages when changes are pushed to the `site/` directory on the main branch.

Manual deployment:
1. Go to Actions tab
2. Select "Deploy Documentation Site"
3. Click "Run workflow"

## Theme

Using [Just the Docs](https://just-the-docs.github.io/just-the-docs/) theme with customizations in `assets/css/custom.css`.

## Contributing

1. Fork the repository
2. Make changes in the `site/` directory
3. Test locally with `bundle exec jekyll serve`
4. Submit a pull request
