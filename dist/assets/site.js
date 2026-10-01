(function () {
  "use strict";
  var root = document.documentElement;
  root.classList.add("js");

  function toast(msg) {
    var t = document.getElementById("toast");
    if (!t) return;
    t.textContent = msg;
    t.classList.add("on");
    clearTimeout(toast._t);
    toast._t = setTimeout(function () { t.classList.remove("on"); }, 2400);
  }

  function copy(text, done, fallbackEl) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { toast(done); }, fallback);
    } else fallback();
    function fallback() {
      if (!fallbackEl || fallbackEl.querySelector("input")) return;
      var i = document.createElement("input");
      i.value = text; i.readOnly = true; i.setAttribute("aria-label", "URL");
      fallbackEl.appendChild(i); i.focus(); i.select();
    }
  }

  // Weekly tabs (home page). Without JS every category stays visible.
  document.querySelectorAll("[data-panel][data-hide]").forEach(function (p) { p.hidden = true; });

  // Bilingual (English) toggle for news summaries
  var bi = true;
  try { bi = localStorage.getItem("jh-bi") !== "0"; } catch (e) {}
  function applyBi() {
    root.classList.toggle("no-bi", !bi);
    document.querySelectorAll("[data-bi]").forEach(function (b) {
      b.setAttribute("aria-pressed", String(bi));
    });
  }
  applyBi();

  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-cat],[data-bi],[data-copymail],.share .copy");
    if (!t) return;
    if (t.hasAttribute("data-cat")) {
      var c = t.getAttribute("data-cat");
      document.querySelectorAll("[data-cat]").forEach(function (b) { b.setAttribute("aria-selected", String(b === t)); });
      document.querySelectorAll("[data-panel]").forEach(function (p) { p.hidden = p.getAttribute("data-panel") !== c; });
    } else if (t.hasAttribute("data-bi")) {
      bi = !bi;
      try { localStorage.setItem("jh-bi", bi ? "1" : "0"); } catch (x) {}
      applyBi();
    } else if (t.hasAttribute("data-copymail")) {
      copy(t.getAttribute("data-copymail"), t.getAttribute("data-done"), null);
    } else {
      copy(t.getAttribute("data-url"), t.getAttribute("data-done"), t.closest(".share"));
    }
  });
  // Keyword search across every week of the Weekly Brief (news pages).
  var form = document.querySelector(".nsearch:not(.compact)");
  var box = document.getElementById("nresults"), week = document.getElementById("nweek");
  if (form && box && week) {
    var input = form.querySelector("input[name=q]"), sel = form.querySelector("select[name=cat]"),
        clear = form.querySelector(".nsearch-clear"), i18n = {}, data = null, loading = null, timer = 0;
    try { i18n = JSON.parse(form.getAttribute("data-i18n")); } catch (e) {}
    var esc = function (s) {
      return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
      });
    };
    var fold = function (s) { return String(s || "").toLowerCase().normalize("NFKC"); };
    var mark = function (text, terms) {
      var out = esc(text);
      terms.forEach(function (t) {
        var re = new RegExp("(" + esc(t).replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "gi");
        out = out.replace(re, "<mark>$1</mark>");
      });
      return out;
    };
    var load = function () {
      if (data) return Promise.resolve(data);
      if (!loading) loading = fetch(form.getAttribute("data-index")).then(function (r) { return r.json(); })
        .then(function (d) {
          d.forEach(function (r) { r.h = fold([r.t, r.s, r.te, r.se, r.src, r.cl].join(" ")); });
          return (data = d);
        });
      return loading;
    };
    var run = function () {
      var q = input.value.trim(), cat = sel ? sel.value : "";
      var url = new URL(location.href);
      if (q) url.searchParams.set("q", q); else url.searchParams.delete("q");
      if (cat && q) url.searchParams.set("cat", cat); else url.searchParams.delete("cat");
      history.replaceState(null, "", url.pathname + url.search + url.hash);
      clear.hidden = !q;
      if (!q) { box.hidden = true; box.innerHTML = ""; week.hidden = false; return; }
      load().then(function (d) {
        var terms = fold(q).split(/\s+/).filter(Boolean);
        var hits = d.filter(function (r) {
          return (!cat || r.c === cat) && terms.every(function (t) { return r.h.indexOf(t) > -1; });
        });
        var weeks = {};
        hits.forEach(function (r) { weeks[r.w] = 1; });
        var head = hits.length
          ? (i18n.s_count || "{n}").replace("{n}", hits.length).replace("{q}", esc(q)).replace("{w}", Object.keys(weeks).length)
          : (i18n.s_none || "").replace("{q}", esc(q));
        box.innerHTML = '<p class="nresults-head">' + head + "</p>" + (hits.length ? '<div class="news">' + hits.map(function (r) {
          var en = r.te ? '<div class="en" lang="en"><h4>' + mark(r.te, terms) + "</h4><p>" + mark(r.se, terms) + "</p></div>" : "";
          return '<article class="item"><div class="when"><b>' + mark(r.src, terms) + "</b><span>" + esc(r.d) + "</span>" +
            '<a class="wk" href="' + esc(r.p) + '">' + esc(r.wl) + "</a><span class=\"cat\">" + esc(r.cl) + "</span></div>" +
            "<div><h3>" + mark(r.t, terms) + "</h3><p>" + mark(r.s, terms) + "</p>" + en +
            (r.u ? '<a class="out" href="' + esc(r.u) + '" target="_blank" rel="noopener">' + esc(i18n.source || "") + " ↗</a>" : "") +
            "</div></article>";
        }).join("") + "</div>" : "");
        box.hidden = false; week.hidden = true;
      }).catch(function () { box.hidden = true; week.hidden = false; });
    };
    form.addEventListener("submit", function (e) { e.preventDefault(); run(); });
    input.addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(run, 250); });
    if (sel) sel.addEventListener("change", run);
    clear.addEventListener("click", function () { input.value = ""; if (sel) sel.value = ""; run(); input.focus(); });
    var params = new URLSearchParams(location.search);
    if (params.get("q")) {
      input.value = params.get("q");
      if (sel && params.get("cat")) sel.value = params.get("cat");
      run();
    }
  }
})();
