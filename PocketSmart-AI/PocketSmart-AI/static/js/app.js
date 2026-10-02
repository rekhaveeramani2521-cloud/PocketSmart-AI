document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector("[data-nav-toggle]");
  const links = document.querySelector("[data-nav-links]");
  if (toggle && links) toggle.addEventListener("click", () => links.classList.toggle("open"));

  document.querySelectorAll("[data-loading-form]").forEach((form) => {
    form.addEventListener("submit", () => {
      const button = form.querySelector("button[type='submit']");
      if (button) {
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.textContent = "Generating...";
      }
    });
  });
});
