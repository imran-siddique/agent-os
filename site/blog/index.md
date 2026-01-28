---
layout: default
title: Blog
nav_order: 9
description: "Agent OS blog - AI safety insights, tutorials, release notes, and community updates."
permalink: /blog/
---

# Blog
{: .fs-9 }

AI safety insights, tutorials, and project updates.
{: .fs-6 .fw-300 }

[RSS Feed](/feed.xml){: .btn .btn-outline }

---

## Latest Posts

{% assign posts = site.posts | sort: 'date' | reverse %}
{% for post in posts limit:10 %}
<article class="post-preview" markdown="1">

### [{{ post.title }}]({{ post.url | relative_url }})
{: .post-title }

<span class="post-meta">{{ post.date | date: "%B %d, %Y" }} · {{ post.author | default: "Agent OS Team" }}</span>

{{ post.excerpt }}

[Read more →]({{ post.url | relative_url }})

---

</article>
{% endfor %}

{% if site.posts.size == 0 %}
<div class="highlight-box info" markdown="1">

**Coming soon!** We're working on our first blog posts. In the meantime:

- [Read the documentation](/docs/)
- [View the FAQ](/faq/)
- [Join GitHub Discussions](https://github.com/imran-siddique/agent-os/discussions)

</div>
{% endif %}

---

## Categories

<div class="blog-categories" markdown="1">

- **Tutorials** — Step-by-step guides
- **Release Notes** — What's new in each version
- **AI Safety** — Industry insights and best practices
- **Case Studies** — Real-world deployments
- **Community** — Contributor spotlights and events

</div>

---

## Stay Updated

<div class="newsletter-signup" markdown="1">

[⭐ Star on GitHub](https://github.com/imran-siddique/agent-os){: .btn .btn-primary .mr-2 }
[📰 RSS Feed](/feed.xml){: .btn }

</div>
