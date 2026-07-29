(function(){
  "use strict";

  /* ---- theme ---- */
  var root = document.documentElement;
  var saved = null;
  try { saved = localStorage.getItem('bb-theme'); } catch(e){}
  if(saved){ root.setAttribute('data-theme', saved); }
  document.querySelectorAll('.theme-toggle').forEach(function(btn){
    btn.addEventListener('click', function(){
      var cur = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', cur);
      try { localStorage.setItem('bb-theme', cur); } catch(e){}
    });
  });

  /* ---- mobile menu ---- */
  var burger = document.querySelector('.nav-burger');
  var menu = document.querySelector('.mobile-menu');
  if(burger && menu){
    burger.addEventListener('click', function(){ menu.classList.add('open'); document.body.style.overflow='hidden'; });
    menu.querySelectorAll('[data-close]').forEach(function(el){
      el.addEventListener('click', function(){ menu.classList.remove('open'); document.body.style.overflow=''; });
    });
  }

  /* ---- reveal on scroll ---- */
  var revealEls = document.querySelectorAll('.reveal');
  if('IntersectionObserver' in window && revealEls.length){
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(entry){
        if(entry.isIntersecting){ entry.target.classList.add('in'); io.unobserve(entry.target); }
      });
    }, { threshold: 0, rootMargin: '0px 0px 0px 0px' });
    revealEls.forEach(function(el){ io.observe(el); });
    // Safety net: IntersectionObserver can miss elements in edge cases (sticky
    // containers, elements already in view before the observer attaches, slow
    // paint timing). Never leave content permanently invisible.
    setTimeout(function(){
      revealEls.forEach(function(el){ el.classList.add('in'); });
    }, 900);
  } else {
    revealEls.forEach(function(el){ el.classList.add('in'); });
  }

  /* ---- reading progress bar ---- */
  var bar = document.querySelector('.progress-bar');
  if(bar){
    window.addEventListener('scroll', function(){
      var h = document.documentElement;
      var scrolled = (h.scrollTop) / (h.scrollHeight - h.clientHeight) * 100;
      bar.style.width = Math.min(100, Math.max(0, scrolled)) + '%';
    }, { passive:true });
  }

  /* ---- TOC scrollspy ---- */
  var tocLinks = document.querySelectorAll('.toc-wrap a');
  if(tocLinks.length){
    var targets = Array.prototype.map.call(tocLinks, function(a){ return document.querySelector(a.getAttribute('href')); }).filter(Boolean);
    window.addEventListener('scroll', function(){
      var pos = window.scrollY + 140;
      var current = targets[0];
      targets.forEach(function(t){ if(t.offsetTop <= pos){ current = t; } });
      tocLinks.forEach(function(a){ a.classList.remove('active'); });
      if(current){
        var match = document.querySelector('.toc-wrap a[href="#' + current.id + '"]');
        if(match) match.classList.add('active');
      }
    }, { passive:true });
  }

  /* ---- FAQ accordion ---- */
  document.querySelectorAll('.faq-item').forEach(function(item){
    var q = item.querySelector('.faq-q');
    if(q) q.addEventListener('click', function(){ item.classList.toggle('open'); });
  });

  /* ---- search modal ---- */
  var searchTriggers = document.querySelectorAll('[data-search-open]');
  var searchModal = document.querySelector('.search-modal');
  if(searchModal){
    var input = searchModal.querySelector('input');
    var results = searchModal.querySelector('.search-results');
    var closeBtn = searchModal.querySelector('[data-search-close]');
    var open = function(){
      searchModal.classList.add('open');
      document.body.style.overflow = 'hidden';
      setTimeout(function(){ input && input.focus(); }, 50);
    };
    var close = function(){ searchModal.classList.remove('open'); document.body.style.overflow=''; };
    searchTriggers.forEach(function(t){ t.addEventListener('click', open); });
    if(closeBtn) closeBtn.addEventListener('click', close);
    searchModal.addEventListener('click', function(e){ if(e.target === searchModal) close(); });
    document.addEventListener('keydown', function(e){
      if(e.key === 'Escape') close();
      if((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k'){ e.preventDefault(); open(); }
    });
    if(input && window.BB_ARTICLES){
      input.addEventListener('input', function(){
        var q = input.value.trim().toLowerCase();
        if(!q){ results.innerHTML = ''; return; }
        var matches = window.BB_ARTICLES.filter(function(a){
          return a.title.toLowerCase().indexOf(q) > -1 || a.category.toLowerCase().indexOf(q) > -1 || a.tags.join(' ').toLowerCase().indexOf(q) > -1;
        }).slice(0, 6);
        results.innerHTML = matches.map(function(a){
          return '<a class="search-result" href="' + a.url + '">' +
                 '<span class="sr-cat">' + a.category + '</span>' +
                 '<span class="sr-title">' + a.title + '</span></a>';
        }).join('') || '<p class="search-empty">No articles found for "' + q + '"</p>';
      });
    }
  }
})();
