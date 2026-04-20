---
layout: default
title: "Elasticsearch Single Node with Docker Compose"
description: "Deploy Elasticsearch single node using Docker Compose — with CRUD operations, cluster health, and API exploration"
author: jinnabalu
categories: [ NoSQL, Search Engine, Elasticsearch ]
tags: [ Elasticsearch, Docker ]
image: "assets/img/elk/ElasticsearchSingleNode.svg"
sitemap:
  lastmod: 2026-04-20
  priority: 0.8
  changefreq: monthly
---

<style>
  .term-page { background: #0d1117; color: #c9d1d9; font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace; }
  .term-page h1, .term-page h2, .term-page h3, .term-page h4, .term-page h5 { color: #58a6ff; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; }
  .term-page h1 { color: #f0f6fc; border-bottom: 1px solid #21262d; padding-bottom: .5rem; }
  .term-page h2 { color: #58a6ff; margin-top: 2.5rem; }
  .term-page h3 { color: #79c0ff; }
  .term-page h4, .term-page h5 { color: #a5d6ff; }
  .term-page a { color: #58a6ff; }
  .term-page a:hover { color: #79c0ff; text-decoration: underline; }
  .term-page p, .term-page li { color: #c9d1d9; line-height: 1.7; }
  .term-page code { background: #161b22; color: #7ee787; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }
  .term-page pre { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1rem 1.2rem; overflow-x: auto; position: relative; }
  .term-page pre code { background: none; color: #e6edf3; padding: 0; }
  .term-page .comment { color: #8b949e; }
  .term-card { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 1.5rem; margin-bottom: 1.5rem; }
  .term-card:hover { border-color: #58a6ff; }
  .term-badge { display: inline-block; background: #238636; color: #fff; font-size: 0.75rem; padding: 3px 10px; border-radius: 12px; margin-bottom: 0.5rem; font-weight: 600; }
  .term-badge-blue { background: #1f6feb; }
  .term-badge-yellow { background: #9e6a03; }
  .term-badge-red { background: #da3633; }
  .term-step { display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; background: #1f6feb; color: #fff; border-radius: 50%; font-weight: 700; font-size: 0.9rem; margin-right: 10px; flex-shrink: 0; }
  .term-output { background: #0d1117; border-left: 3px solid #238636; padding: 0.8rem 1rem; margin: 0.5rem 0 1rem; border-radius: 0 6px 6px 0; font-size: 0.85rem; }
  .term-output code { color: #7ee787; }
  .term-table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
  .term-table th { background: #1f6feb; color: #fff; padding: 10px 14px; text-align: left; font-size: 0.85rem; }
  .term-table td { background: #161b22; color: #c9d1d9; padding: 10px 14px; border-bottom: 1px solid #21262d; font-size: 0.85rem; }
  .term-table td code { font-size: 0.85em; }
  .term-prompt::before { content: '$ '; color: #7ee787; }
  .term-note { background: #0d1117; border: 1px solid #30363d; border-left: 3px solid #9e6a03; padding: 0.8rem 1rem; border-radius: 0 6px 6px 0; margin: 1rem 0; color: #e3b341; font-size: 0.9rem; }
  .term-prereq { display: flex; align-items: center; padding: 0.6rem 0; border-bottom: 1px solid #21262d; }
  .term-prereq:last-child { border-bottom: none; }
  .term-prereq-icon { color: #7ee787; margin-right: 10px; font-size: 1.1rem; }
</style>

<main id="main" class="main">
  <div class="term-page" style="max-width:960px; margin:0 auto; padding:2rem 1.5rem;">

    <!-- Header -->
    <nav style="margin-bottom:1.5rem;">
      <a href="/" style="color:#8b949e;font-size:0.85rem;">Home</a>
      <span style="color:#484f58;"> / </span>
      <span style="color:#c9d1d9;font-size:0.85rem;">Elasticsearch</span>
    </nav>

    <h1>Elasticsearch Single Node with Docker Compose</h1>
    <p style="color:#8b949e;font-size:1.05rem;margin-bottom:2rem;">
      Deploy a single-node Elasticsearch instance using Docker Compose. Learn cluster health APIs, CRUD operations, and explore Elasticsearch from your terminal.
    </p>

    <!-- Course Info Bar -->
    <div style="display:flex;flex-wrap:wrap;gap:1rem;margin-bottom:2rem;">
      <span class="term-badge">Beginner Friendly</span>
      <span class="term-badge-blue term-badge">Hands-on</span>
      <span style="color:#8b949e;font-size:0.85rem;display:flex;align-items:center;">
        <svg width="16" height="16" fill="#8b949e" style="margin-right:4px;" viewBox="0 0 16 16"><path d="M8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0ZM1.5 8a6.5 6.5 0 1 0 13 0 6.5 6.5 0 0 0-13 0Zm7-3.25v2.992l2.028.812a.75.75 0 0 1-.557 1.392l-2.5-1A.751.751 0 0 1 7 8.25v-3.5a.75.75 0 0 1 1.5 0Z"></path></svg>
        ~30 min
      </span>
      <a href="https://github.com/JinnaBalu/elasticsearch" target="_blank" style="color:#58a6ff;font-size:0.85rem;display:flex;align-items:center;">
        <svg width="16" height="16" fill="#58a6ff" style="margin-right:4px;" viewBox="0 0 16 16"><path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"></path></svg>
        Source Repository
      </a>
    </div>

    <hr style="border-color:#21262d;">

    <!-- Prerequisites -->
    <h2><span class="term-step">0</span> Prerequisites</h2>
    <div class="term-card">
      <div class="term-prereq">
        <span class="term-prereq-icon">&#10003;</span>
        <span>Install <a href="https://docs.docker.com/install/linux/docker-ce/ubuntu/" target="_blank">Docker</a> or <a href="https://podman.io/docs/installation" target="_blank">Podman</a></span>
      </div>
      <div class="term-prereq">
        <span class="term-prereq-icon">&#10003;</span>
        <span>Install <a href="https://docs.docker.com/compose/install/" target="_blank">Docker Compose</a></span>
      </div>
      <div class="term-prereq">
        <span class="term-prereq-icon">&#10003;</span>
        <span>Basic understanding of Docker containers and YAML</span>
      </div>
    </div>

    <!-- Step 1: Docker Compose -->
    <h2><span class="term-step">1</span> Docker Compose File</h2>
    <p>Create a <code>docker-compose.yml</code> with the following configuration:</p>
    <div class="term-card">
<pre><code><span class="comment"># docker-compose.yml</span>
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch-wolfi:8.17.4
    container_name: elasticsearch
    environment:
      - cluster.name=oio-es-cluster
      - node.name=es-node
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - network.host=0.0.0.0
      - xpack.license.self_generated.type=trial
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms1024m -Xmx1024m"
    ports: ['9200:9200']
    volumes:
      - 'es_data:/usr/share/elasticsearch/data'
    healthcheck:
      test: curl -s http://localhost:9200 >/dev/null || exit 1
      interval: 30s
      timeout: 10s
      retries: 5
volumes:
  es_data:</code></pre>
    </div>

    <!-- Step 2: Run -->
    <h2><span class="term-step">2</span> Start the Cluster</h2>
    <div class="term-card">
<pre><code><span class="comment"># Start Elasticsearch in detached mode</span>
<span class="term-prompt">docker-compose up -d</span>

<span class="comment"># Verify the container is running</span>
<span class="term-prompt">docker-compose ps -a</span>
<span class="term-prompt">docker ps -a</span></code></pre>
    </div>

    <!-- Step 3: Health & Stats -->
    <h2><span class="term-step">3</span> Cluster Health &amp; Stats</h2>
    <p>Once the container is up, explore the cluster using these APIs:</p>

    <table class="term-table">
      <thead>
        <tr><th>API</th><th>Command</th></tr>
      </thead>
      <tbody>
        <tr><td>Node list</td><td><code>curl -s localhost:9200/_cat/nodes?pretty</code></td></tr>
        <tr><td>Cluster health</td><td><code>curl -s localhost:9200/_cat/health?pretty</code></td></tr>
        <tr><td>Cluster stats</td><td><code>curl -s localhost:9200/_cluster/stats?human&amp;pretty</code></td></tr>
        <tr><td>Node stats</td><td><code>curl -s localhost:9200/_nodes/stats?pretty</code></td></tr>
        <tr><td>Specific node</td><td><code>curl -s localhost:9200/_nodes/es-node/stats?pretty</code></td></tr>
        <tr><td>List indices</td><td><code>curl -s localhost:9200/_cat/indices?pretty</code></td></tr>
        <tr><td>All indices</td><td><code>curl -s localhost:9200/_cat/indices?expand_wildcards=all&amp;pretty</code></td></tr>
        <tr><td>Index-level stats</td><td><code>curl -s localhost:9200/_nodes/stats/indices?pretty</code></td></tr>
        <tr><td>Plugins</td><td><code>curl -s localhost:9200/_nodes/plugins</code></td></tr>
      </tbody>
    </table>

    <!-- Step 4: CRUD -->
    <h2><span class="term-step">4</span> CRUD Operations</h2>

    <!-- Create Index -->
    <h3>4.1 &mdash; Create Index</h3>
    <div class="term-note">
      <strong>Without mappings:</strong> Elasticsearch auto-generates field types on the first document (dynamic mapping).<br>
      <strong>With mappings:</strong> You define field types up front for better control (e.g., <code>text</code> vs <code>keyword</code>).
    </div>
    <div class="term-card">
<pre><code><span class="term-prompt">curl -X PUT http://localhost:9200/ramayana_characters \</span>
  -H "Content-Type: application/json" -d '
{
  "mappings": {
    "properties": {
      "name": { "type": "text" },
      "description": { "type": "text" }
    }
  }
}'</code></pre>
      <div class="term-output">
<code>{"acknowledged":true,"shards_acknowledged":true,"index":"ramayana_characters"}</code>
      </div>
    </div>

    <!-- Insert Document -->
    <h3>4.2 &mdash; Insert Document</h3>
    <div class="term-card">
<pre><code><span class="term-prompt">curl -X POST http://localhost:9200/ramayana_characters/_doc \</span>
  -H "Content-Type: application/json" -d '
{
  "name": "Rama",
  "description": "Hero of the Ramayana, seventh avatar of Vishnu."
}'</code></pre>
      <div class="term-output">
<code>{"_index":"ramayana_characters","_id":"_g1qMpYBhtVSA9-yauE0","_version":1,"result":"created", ...}</code>
      </div>
      <div class="term-note">
        Copy the <code>_id</code> from the output &mdash; you'll need it for the next queries.
      </div>
    </div>

    <!-- Select All -->
    <h3>4.3 &mdash; Select All</h3>
    <div class="term-card">
<pre><code><span class="term-prompt">curl -X GET 'http://localhost:9200/ramayana_characters/_search?pretty'</span></code></pre>
      <div class="term-output">
<code>{
  "hits": {
    "total": { "value": 1 },
    "hits": [{
      "_id": "_g1qMpYBhtVSA9-yauE0",
      "_source": {
        "name": "Rama",
        "description": "Hero of the Ramayana, seventh avatar of Vishnu."
      }
    }]
  }
}</code>
      </div>
    </div>

    <!-- Select by ID -->
    <h3>4.4 &mdash; Select by ID</h3>
    <div class="term-card">
<pre><code><span class="term-prompt">export DOC_ID=_g1qMpYBhtVSA9-yauE0</span>
<span class="term-prompt">curl -X GET "http://localhost:9200/ramayana_characters/_doc/${DOC_ID}?pretty"</span></code></pre>
    </div>

    <!-- Update -->
    <h3>4.5 &mdash; Update Document</h3>
    <div class="term-card">
<pre><code><span class="term-prompt">curl -X POST "http://localhost:9200/ramayana_characters/_update/${DOC_ID}?pretty" \</span>
  -H "Content-Type: application/json" -d '
{
  "doc": {
    "name": "Raama"
  }
}'</code></pre>
      <div class="term-output">
<code>{"_index":"ramayana_characters","_id":"...","_version":2,"result":"updated"}</code>
      </div>
    </div>

    <!-- Delete -->
    <h3>4.6 &mdash; Delete Document</h3>
    <div class="term-card">
<pre><code><span class="term-prompt">curl -X DELETE "http://localhost:9200/ramayana_characters/_doc/${DOC_ID}?pretty"</span></code></pre>
      <div class="term-output">
<code>{"_index":"ramayana_characters","_id":"...","_version":3,"result":"deleted"}</code>
      </div>
    </div>

    <hr style="border-color:#21262d;margin:2.5rem 0;">

    <!-- Homework -->
    <h2><span class="term-step">&#9733;</span> Homework</h2>
    <div class="term-card">
      <table class="term-table" style="margin:0;">
        <thead><tr><th>#</th><th>Task</th><th>Goal</th></tr></thead>
        <tbody>
          <tr><td>1</td><td>Deploy &amp; Explore</td><td>Run Docker Compose, use <code>curl</code> to hit every health API</td></tr>
          <tr><td>2</td><td>Create &amp; Query</td><td>Create an index, insert 5 documents, run <code>_search</code> and get-by-ID</td></tr>
          <tr><td>3</td><td>Understand Mappings</td><td>Compare behaviour with and without explicit mappings</td></tr>
          <tr><td>4</td><td>Yellow Cluster?</td><td>Investigate why health turns yellow after creating an index (<em>hint: replica shards</em>)</td></tr>
        </tbody>
      </table>
    </div>

    <hr style="border-color:#21262d;margin:2.5rem 0;">
    <p style="color:#8b949e;text-align:center;font-size:0.85rem;">
      Source &mdash; <a href="https://github.com/JinnaBalu/elasticsearch" target="_blank">github.com/JinnaBalu/elasticsearch</a>
    </p>
  </div>
</main>