/**
 * Project Editor — VS Code-style multi-file viewer
 * Fetches files from GitHub raw content and renders them in an IDE-like component.
 */
(function () {
  'use strict';

  // Language detection from file extension
  var langMap = {
    py: 'Python', pyi: 'Python',
    yml: 'YAML', yaml: 'YAML',
    json: 'JSON',
    toml: 'TOML',
    ini: 'INI', cfg: 'INI',
    conf: 'Conf',
    sh: 'Bash', bash: 'Bash',
    dockerfile: 'Dockerfile',
    hcl: 'HCL', tf: 'Terraform',
    js: 'JavaScript', ts: 'TypeScript',
    html: 'HTML', css: 'CSS', xml: 'XML',
    sql: 'SQL', md: 'Markdown',
    txt: 'Text', env: 'Env',
    makefile: 'Makefile'
  };

  // File icon color by extension
  var iconColors = {
    py: '#3572A5', yml: '#cb171e', yaml: '#cb171e',
    json: '#f1c40f', toml: '#9c4221', dockerfile: '#0db7ed',
    sh: '#28c840', bash: '#28c840', env: '#28c840',
    hcl: '#844fba', tf: '#844fba',
    js: '#f7df1e', ts: '#3178c6',
    html: '#e34c26', css: '#1572b6',
    cfg: '#6b7280', conf: '#6b7280', ini: '#6b7280',
    md: '#083fa1', txt: '#6b7280'
  };

  function detectLang(filename) {
    var lower = filename.toLowerCase();
    if (lower === 'dockerfile') return 'Dockerfile';
    if (lower === 'makefile') return 'Makefile';
    if (lower === '.env' || lower.startsWith('.env.')) return 'Env';
    var ext = lower.split('.').pop();
    return langMap[ext] || 'Text';
  }

  function getIconColor(filename) {
    var lower = filename.toLowerCase();
    if (lower === 'dockerfile') return '#0db7ed';
    if (lower === 'makefile') return '#6b7280';
    var ext = lower.split('.').pop();
    return iconColors[ext] || '#6b7280';
  }

  function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // ─── Syntax highlighters (VS Code Dark+ palette) ──────────────────────────

  function highlightPython(code) {
    var e = escapeHtml(code);
    // Comments
    e = e.replace(/(#[^\n]*)/g, '<span style="color:#6a9955;font-style:italic">$1</span>');
    // Triple-quoted strings
    e = e.replace(/("""[\s\S]*?"""|'''[\s\S]*?''')/g, '<span style="color:#ce9178">$1</span>');
    // Strings
    e = e.replace(/((?:f|r|b)?&quot;(?:[^&]|&(?!quot;))*?&quot;|(?:f|r|b)?&#039;(?:[^&]|&(?!#039;))*?&#039;)/g, '<span style="color:#ce9178">$1</span>');
    // Decorators
    e = e.replace(/(@\w+)/g, '<span style="color:#dcdcaa">$1</span>');
    // Keywords
    e = e.replace(/\b(import|from|class|def|return|if|elif|else|for|while|try|except|finally|with|as|async|await|yield|raise|pass|break|continue|and|or|not|in|is|None|True|False|self|lambda)\b/g, '<span style="color:#569cd6">$1</span>');
    // Built-in functions
    e = e.replace(/\b(print|len|range|type|int|str|float|list|dict|set|tuple|isinstance|getattr|setattr|super|open|enumerate|zip|map|filter|sorted|reversed|any|all|min|max|sum|abs|round|format|input|id|hash|repr|iter|next)\b/g, '<span style="color:#dcdcaa">$1</span>');
    // Numbers
    e = e.replace(/\b(\d+(?:\.\d+)?)\b/g, '<span style="color:#b5cea8">$1</span>');
    return e;
  }

  function highlightYAML(code) {
    var e = escapeHtml(code);
    e = e.replace(/(#.*$)/gm, '<span style="color:#6a9955;font-style:italic">$1</span>');
    e = e.replace(/(^|\s+)([a-zA-Z_][a-zA-Z0-9_.-]*)(:)/gm, '$1<span style="color:#569cd6">$2</span><span style="color:#d4d4d4">$3</span>');
    e = e.replace(/(:\s*)(&quot;[^&]*?&quot;)/g, '$1<span style="color:#ce9178">$2</span>');
    e = e.replace(/(:\s*)(&#039;[^&]*?&#039;)/g, '$1<span style="color:#ce9178">$2</span>');
    e = e.replace(/(:\s*)(\d+(?:\.\d+)?)([\s,\n]|$)/gm, '$1<span style="color:#b5cea8">$2</span>$3');
    e = e.replace(/(:\s*)(true|false|yes|no|null)([\s,\n]|$)/gmi, '$1<span style="color:#569cd6">$2</span>$3');
    e = e.replace(/^(\s*)(-)(\s)/gm, '$1<span style="color:#6b7280">$2</span>$3');
    return e;
  }

  function highlightDockerfile(code) {
    var e = escapeHtml(code);
    e = e.replace(/(#[^\n]*)/g, '<span style="color:#6a9955;font-style:italic">$1</span>');
    e = e.replace(/^(FROM|RUN|CMD|COPY|ADD|EXPOSE|ENV|ARG|WORKDIR|ENTRYPOINT|USER|VOLUME|HEALTHCHECK|LABEL|SHELL|STOPSIGNAL|ONBUILD|MAINTAINER)\b/gm, '<span style="color:#569cd6">$1</span>');
    e = e.replace(/\b(AS)\b/g, '<span style="color:#569cd6">$1</span>');
    e = e.replace(/(&quot;[^&]*?&quot;)/g, '<span style="color:#ce9178">$1</span>');
    e = e.replace(/(\$\{?\w+\}?)/g, '<span style="color:#9cdcfe">$1</span>');
    e = e.replace(/(--\w[\w-]*)/g, '<span style="color:#9cdcfe">$1</span>');
    return e;
  }

  function highlightTOML(code) {
    var e = escapeHtml(code);
    e = e.replace(/(#.*$)/gm, '<span style="color:#6a9955;font-style:italic">$1</span>');
    e = e.replace(/^(\[[\w."-]+\])/gm, '<span style="color:#569cd6;font-weight:600">$1</span>');
    e = e.replace(/^([a-zA-Z_][\w-]*)\s*(=)/gm, '<span style="color:#9cdcfe">$1</span> <span style="color:#d4d4d4">$2</span>');
    e = e.replace(/(=\s*)(&quot;[^&]*?&quot;)/g, '$1<span style="color:#ce9178">$2</span>');
    e = e.replace(/(=\s*)(\d+(?:\.\d+)?)/g, '$1<span style="color:#b5cea8">$2</span>');
    e = e.replace(/(=\s*)(true|false)/gi, '$1<span style="color:#569cd6">$2</span>');
    return e;
  }

  function highlightJSON(code) {
    var e = escapeHtml(code);
    e = e.replace(/(&quot;(?:[^&]|&(?!quot;))*?&quot;)(\s*:)/g, '<span style="color:#9cdcfe">$1</span>$2');
    e = e.replace(/(:\s*)(&quot;(?:[^&]|&(?!quot;))*?&quot;)/g, '$1<span style="color:#ce9178">$2</span>');
    e = e.replace(/(:\s*)(\d+(?:\.\d+)?)/g, '$1<span style="color:#b5cea8">$2</span>');
    e = e.replace(/(:\s*)(true|false|null)\b/g, '$1<span style="color:#569cd6">$2</span>');
    return e;
  }

  function highlightBash(code) {
    var e = escapeHtml(code);
    e = e.replace(/(#[^\n]*)/g, '<span style="color:#6a9955;font-style:italic">$1</span>');
    e = e.replace(/(&quot;[^&]*?&quot;)/g, '<span style="color:#ce9178">$1</span>');
    e = e.replace(/(\$\{?\w+\}?)/g, '<span style="color:#9cdcfe">$1</span>');
    e = e.replace(/(--[\w-]+)/g, '<span style="color:#9cdcfe">$1</span>');
    return e;
  }

  function highlightHCL(code) {
    var e = escapeHtml(code);
    e = e.replace(/(#[^\n]*|\/\/[^\n]*)/g, '<span style="color:#6a9955;font-style:italic">$1</span>');
    e = e.replace(/\b(resource|data|variable|output|module|provider|terraform|locals|backend)\b/g, '<span style="color:#569cd6">$1</span>');
    e = e.replace(/(&quot;[^&]*?&quot;)/g, '<span style="color:#ce9178">$1</span>');
    e = e.replace(/(=\s*)(\d+)/g, '$1<span style="color:#b5cea8">$2</span>');
    e = e.replace(/(=\s*)(true|false)\b/g, '$1<span style="color:#569cd6">$2</span>');
    return e;
  }

  function highlightCode(content, lang) {
    switch (lang) {
      case 'Python': return highlightPython(content);
      case 'YAML': return highlightYAML(content);
      case 'Dockerfile': return highlightDockerfile(content);
      case 'TOML': return highlightTOML(content);
      case 'JSON': return highlightJSON(content);
      case 'Bash': case 'Env': return highlightBash(content);
      case 'HCL': case 'Terraform': return highlightHCL(content);
      default: return escapeHtml(content);
    }
  }

  // Build file tree structure from flat file paths
  function buildTree(files) {
    var root = { name: '', children: [], isDir: true };
    files.forEach(function (f) {
      var parts = f.path.split('/');
      var current = root;
      for (var i = 0; i < parts.length; i++) {
        var part = parts[i];
        var isLast = i === parts.length - 1;
        if (isLast) {
          current.children.push({ name: part, path: f.path, isDir: false });
        } else {
          var existing = null;
          for (var j = 0; j < current.children.length; j++) {
            if (current.children[j].isDir && current.children[j].name === part) {
              existing = current.children[j];
              break;
            }
          }
          if (!existing) {
            existing = { name: part, path: parts.slice(0, i + 1).join('/'), children: [], isDir: true };
            current.children.push(existing);
          }
          current = existing;
        }
      }
    });
    // Sort: dirs first, then alphabetical
    function sortTree(node) {
      if (!node.children) return;
      node.children.sort(function (a, b) {
        if (a.isDir !== b.isDir) return a.isDir ? -1 : 1;
        return a.name.localeCompare(b.name);
      });
      node.children.forEach(sortTree);
    }
    sortTree(root);
    return root;
  }

  function renderTreeNode(node, depth, selectedPath, onSelect) {
    var html = '';
    var pl = (depth * 16 + 8) + 'px';

    if (node.isDir) {
      var isOpen = true; // all expanded by default
      html += '<button class="pe-tree-item pe-tree-dir" style="padding-left:' + pl + '" data-path="' + escapeHtml(node.path) + '">'
        + '<i class="bi bi-chevron-down pe-tree-chevron"></i>'
        + '<i class="bi bi-folder-fill" style="color:#f7c948;margin-right:4px;font-size:0.8rem"></i>'
        + '<span>' + escapeHtml(node.name) + '</span></button>';
      html += '<div class="pe-tree-children">';
      node.children.forEach(function (child) {
        html += renderTreeNode(child, depth + 1, selectedPath, onSelect);
      });
      html += '</div>';
    } else {
      var isActive = node.path === selectedPath;
      var color = getIconColor(node.name);
      html += '<button class="pe-tree-item pe-tree-file' + (isActive ? ' active' : '') + '" '
        + 'style="padding-left:' + ((depth * 16 + 8 + 18)) + 'px" data-path="' + escapeHtml(node.path) + '">'
        + '<i class="bi bi-file-earmark-text" style="color:' + color + ';margin-right:4px;font-size:0.75rem"></i>'
        + '<span>' + escapeHtml(node.name) + '</span></button>';
    }
    return html;
  }

  // Render line-numbered code with syntax highlighting
  function renderCode(content, lang) {
    var highlighted = highlightCode(content, lang);
    var lines = highlighted.split('\n');
    if (lines[lines.length - 1] === '') lines.pop();
    var lineNums = '';
    var codeLines = '';
    for (var i = 0; i < lines.length; i++) {
      lineNums += '<div class="pe-ln">' + (i + 1) + '</div>';
      codeLines += '<div class="pe-code-line">' + (lines[i] || ' ') + '</div>';
    }
    return '<div class="pe-code-wrap"><div class="pe-line-nums">' + lineNums + '</div><pre class="pe-code-pre"><code>' + codeLines + '</code></pre></div>';
  }

  // Initialize a single editor instance
  function initEditor(container) {
    var repo = container.dataset.repo;
    var branch = container.dataset.branch || 'main';
    var name = container.dataset.name || repo;
    var filePaths = container.dataset.files.split(',').map(function (f) { return f.trim(); });

    var baseUrl = 'https://raw.githubusercontent.com/' + repo + '/' + branch + '/';
    var files = []; // { path, name, content, lang }
    var activeIndex = 0;

    var treeEl = container.querySelector('.pe-file-tree');
    var tabsEl = container.querySelector('.pe-tabs');
    var codeArea = container.querySelector('.pe-code-area');
    var statusLang = container.querySelector('.pe-statusbar-lang');
    var statusInfo = container.querySelector('.pe-statusbar-info');

    // Fetch all files
    Promise.all(filePaths.map(function (path) {
      return fetch(baseUrl + path)
        .then(function (res) {
          if (!res.ok) throw new Error('HTTP ' + res.status);
          return res.text();
        })
        .then(function (content) {
          return { path: path, name: path.split('/').pop(), content: content, lang: detectLang(path.split('/').pop()) };
        })
        .catch(function () {
          return { path: path, name: path.split('/').pop(), content: '# Failed to fetch: ' + path, lang: 'Text' };
        });
    })).then(function (results) {
      files = results;
      render();
    });

    function render() {
      renderSidebar();
      renderTabs();
      renderContent();
      updateStatus();
    }

    function renderSidebar() {
      var tree = buildTree(files);
      var html = '';
      tree.children.forEach(function (child) {
        html += renderTreeNode(child, 0, files[activeIndex].path);
      });
      treeEl.innerHTML = html;

      // Bind click events
      treeEl.querySelectorAll('.pe-tree-file').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var path = btn.dataset.path;
          for (var i = 0; i < files.length; i++) {
            if (files[i].path === path) { activeIndex = i; break; }
          }
          render();
        });
      });

      treeEl.querySelectorAll('.pe-tree-dir').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var children = btn.nextElementSibling;
          var chevron = btn.querySelector('.pe-tree-chevron');
          if (children && children.classList.contains('pe-tree-children')) {
            var isHidden = children.style.display === 'none';
            children.style.display = isHidden ? '' : 'none';
            chevron.classList.toggle('bi-chevron-down', isHidden);
            chevron.classList.toggle('bi-chevron-right', !isHidden);
          }
        });
      });
    }

    function renderTabs() {
      var html = '';
      files.forEach(function (f, i) {
        var color = getIconColor(f.name);
        var cls = i === activeIndex ? 'pe-tab active' : 'pe-tab';
        html += '<button class="' + cls + '" data-idx="' + i + '">'
          + '<i class="bi bi-file-earmark-text" style="color:' + color + ';font-size:0.7rem"></i> '
          + escapeHtml(f.name) + '</button>';
      });
      // Copy button in tab bar
      html += '<button class="pe-tab-copy" title="Copy file contents"><i class="bi bi-clipboard"></i> Copy</button>';
      tabsEl.innerHTML = html;

      tabsEl.querySelectorAll('.pe-tab').forEach(function (tab) {
        tab.addEventListener('click', function () {
          activeIndex = parseInt(tab.dataset.idx);
          render();
        });
      });

      tabsEl.querySelector('.pe-tab-copy').addEventListener('click', function () {
        var btn = this;
        navigator.clipboard.writeText(files[activeIndex].content).then(function () {
          btn.innerHTML = '<i class="bi bi-check-lg"></i> Copied';
          btn.classList.add('copied');
          setTimeout(function () {
            btn.innerHTML = '<i class="bi bi-clipboard"></i> Copy';
            btn.classList.remove('copied');
          }, 2000);
        });
      });
    }

    function renderContent() {
      codeArea.innerHTML = renderCode(files[activeIndex].content, files[activeIndex].lang);
    }

    function updateStatus() {
      var f = files[activeIndex];
      var lineCount = f.content.split('\n').length;
      if (f.content.endsWith('\n')) lineCount--;
      statusLang.textContent = f.lang + ' · UTF-8';
      statusInfo.textContent = 'Ln ' + lineCount + ' · ' + files.length + ' files';
    }
  }

  // Auto-init all editors on page load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      document.querySelectorAll('.pe-editor').forEach(initEditor);
    });
  } else {
    document.querySelectorAll('.pe-editor').forEach(initEditor);
  }
})();
