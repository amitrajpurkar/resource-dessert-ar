/* Resource Desert Dashboard — Regenerate button + status polling */

(function () {
  "use strict";

  var regenBtn = document.getElementById("regen-btn");
  var errorBanner = document.getElementById("error-banner");
  var statusDot = document.getElementById("status-dot");

  /** Update the visible run-status indicator. */
  function setStatusUI(status, message) {
    if (!statusDot) return;
    statusDot.className = "status-dot status-dot--" + status;
    statusDot.title = status;

    if (status === "running") {
      if (regenBtn) {
        regenBtn.disabled = true;
        regenBtn.innerHTML =
          '<span class="spinner"></span> Running…';
      }
      if (errorBanner) errorBanner.classList.remove("visible");
    } else if (status === "complete") {
      if (regenBtn) {
        regenBtn.disabled = false;
        regenBtn.textContent = "Regenerate Data";
      }
      // Reload so all sections reflect the freshly generated files.
      window.location.reload();
    } else if (status === "error") {
      if (regenBtn) {
        regenBtn.disabled = false;
        regenBtn.textContent = "Regenerate Data";
      }
      if (errorBanner) {
        errorBanner.textContent = "Notebook error:\n" + (message || "(no details)");
        errorBanner.classList.add("visible");
      }
    } else {
      // idle
      if (regenBtn) {
        regenBtn.disabled = false;
        regenBtn.textContent = "Regenerate Data";
      }
    }
  }

  /** Poll /api/regenerate/status every 2 s while status == "running". */
  function pollStatus() {
    fetch("/api/regenerate/status")
      .then(function (r) { return r.json(); })
      .then(function (data) {
        setStatusUI(data.status, data.message);
        if (data.status === "running") {
          setTimeout(pollStatus, 2000);
        }
      })
      .catch(function () {
        // Network error — keep trying.
        setTimeout(pollStatus, 2000);
      });
  }

  /** Wire the Regenerate Data button click. */
  if (regenBtn) {
    regenBtn.addEventListener("click", function () {
      regenBtn.disabled = true;
      regenBtn.innerHTML = '<span class="spinner"></span> Starting…';
      if (errorBanner) errorBanner.classList.remove("visible");

      fetch("/api/regenerate", { method: "POST" })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data.status === "running") {
            setStatusUI("running", "");
            setTimeout(pollStatus, 2000);
          } else {
            // 409 — already running; start polling to catch completion.
            setStatusUI("running", "");
            setTimeout(pollStatus, 2000);
          }
        })
        .catch(function () {
          regenBtn.disabled = false;
          regenBtn.textContent = "Regenerate Data";
          if (errorBanner) {
            errorBanner.textContent = "Failed to contact server.";
            errorBanner.classList.add("visible");
          }
        });
    });
  }

  // On page load: if run_status is already "running" (server-side SSR), start polling.
  var initialStatus = document.body.dataset.runStatus;
  if (initialStatus === "running") {
    setStatusUI("running", "");
    setTimeout(pollStatus, 2000);
  }
})();
