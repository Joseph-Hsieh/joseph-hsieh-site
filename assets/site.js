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
})();
