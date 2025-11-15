(() => {
  const STORAGE_KEY = "alihouse-theme";
  const root = document.documentElement;
  const themeToggle = document.querySelector(".theme-toggle");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)");

  const applyTheme = (theme) => {
    const normalized = theme === "dark" ? "dark" : "light";
    root.setAttribute("data-theme", normalized);
    if (themeToggle) {
      themeToggle.setAttribute("aria-pressed", normalized === "dark");
      const icon = themeToggle.querySelector(".theme-toggle__icon");
      if (icon) {
        icon.textContent = normalized === "dark" ? "🌙" : "☀️";
      }
    }
  };

  const storedTheme = localStorage.getItem(STORAGE_KEY);
  if (storedTheme) {
    applyTheme(storedTheme);
  } else if (prefersDark.matches) {
    applyTheme("dark");
  } else {
    applyTheme("light");
  }

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const current = root.getAttribute("data-theme") === "dark" ? "dark" : "light";
      const next = current === "dark" ? "light" : "dark";
      applyTheme(next);
      localStorage.setItem(STORAGE_KEY, next);
    });
  }

  prefersDark.addEventListener("change", (event) => {
    if (!localStorage.getItem(STORAGE_KEY)) {
      applyTheme(event.matches ? "dark" : "light");
    }
  });

  const menuToggle = document.querySelector(".menu-toggle");
  const nav = document.querySelector(".nav");

  const setMenuState = (isOpen) => {
    if (!menuToggle || !nav) return;
    nav.dataset.open = String(isOpen);
    menuToggle.setAttribute("aria-expanded", String(isOpen));
    if (isOpen) {
      document.body.classList.add("menu-open");
    } else {
      document.body.classList.remove("menu-open");
    }
  };

  if (menuToggle && nav) {
    menuToggle.addEventListener("click", () => {
      const next = nav.dataset.open !== "true";
      setMenuState(next);
    });

    nav.addEventListener("click", (event) => {
      if (event.target instanceof HTMLElement && event.target.tagName === "A" && window.innerWidth <= 720) {
        setMenuState(false);
      }
    });

    window.addEventListener("resize", () => {
      if (window.innerWidth > 720) {
        setMenuState(false);
      }
    });

    document.addEventListener("click", (event) => {
      if (!menuToggle.contains(event.target) && !nav.contains(event.target) && window.innerWidth <= 720) {
        setMenuState(false);
      }
    });
  }
})();

