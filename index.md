---
layout: default
---

# Welcome to My Stories!

Here are all the stories I've written so far:

<ul>
  {% assign sorted_posts = site.posts | sort: 'title' %}
  {% for post in sorted_posts %}
    <li>
      <a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a>
    </li>
  {% endfor %}
</ul>
