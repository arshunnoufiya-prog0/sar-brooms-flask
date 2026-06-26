/* ==========================================================
   SAR BROOMS — Main JavaScript
   ========================================================== */

// Build the signature "bristle divider" SVG (echoes the broom logo)
function buildBristleDivider(svgEl) {
  if (!svgEl) return;
  const count = 80;
  const width = 1200;
  const spacing = width / count;
  let html = "";
  for (let i = 0; i < count; i++) {
    const x = i * spacing + spacing / 2;
    const sway = (i % 2 === 0) ? -3 : 3;
    const h = 14 + (i % 3) * 4;
    const opacity = 0.25 + (i % 3) * 0.15;
    html += `<line x1="${x}" y1="0" x2="${x + sway}" y2="${h}" stroke="currentColor" stroke-width="2" stroke-linecap="round" opacity="${opacity}"/>`;
  }
  svgEl.innerHTML = html;
}

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".bristle-divider svg").forEach(buildBristleDivider);

  // Image upload preview (used on Add/Edit product forms)
  const imageInput = document.getElementById("imageInput");
  const previewBox = document.getElementById("imagePreviewBox");
  const previewImg = document.getElementById("imagePreviewImg");
  const removeImageCheckbox = document.getElementById("removeImageCheckbox");

  if (imageInput && previewBox && previewImg) {
    imageInput.addEventListener("change", function () {
      const file = imageInput.files && imageInput.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = function (e) {
        previewImg.src = e.target.result;
        previewBox.classList.remove("d-none");
        if (removeImageCheckbox) removeImageCheckbox.checked = false;
      };
      reader.readAsDataURL(file);
    });
  }

  // Auto-dismiss flash messages after a few seconds
  document.querySelectorAll(".alert-auto-dismiss").forEach(function (alertEl) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
      bsAlert.close();
    }, 5000);
  });

  // Fade-up animation trigger on scroll for elements with .scroll-fade
  const scrollFadeEls = document.querySelectorAll(".scroll-fade");
  if (scrollFadeEls.length && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("fade-up");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    scrollFadeEls.forEach((el) => observer.observe(el));
  } else {
    scrollFadeEls.forEach((el) => el.classList.add("fade-up"));
  }
});
