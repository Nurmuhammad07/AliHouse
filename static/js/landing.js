// Landing page animations
(() => {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const element = entry.target;
        const delay = parseInt(element.dataset.delay || 0);
        const animate = element.dataset.animate || "fadeInUp";

        setTimeout(() => {
          element.classList.add("animated");
        }, delay);
      }
    });
  }, observerOptions);

  // Observe all animated elements
  document.querySelectorAll("[data-animate]").forEach((el) => {
    observer.observe(el);
  });

  // Enhanced counter animation
  const animateCounter = (element, target, hasPlus = false, duration = 2000) => {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;

    const updateCounter = () => {
      current += increment;
      if (current < target) {
        element.textContent = Math.floor(current) + (hasPlus ? "+" : "");
        requestAnimationFrame(updateCounter);
      } else {
        element.textContent = target + (hasPlus ? "+" : "");
      }
    };

    updateCounter();
  };

  // Animate counters when stats section is visible
  const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const statCards = entry.target.querySelectorAll(".stat-card");
        statCards.forEach((card) => {
          const numberEl = card.querySelector(".stat-number");
          if (numberEl && !card.classList.contains("counted")) {
            card.classList.add("counted");
            const text = numberEl.textContent;
            const number = parseInt(text.replace(/\D/g, ""));
            if (!isNaN(number)) {
              numberEl.textContent = "0";
              if (text.includes("+")) {
                numberEl.textContent = "0+";
              }
              setTimeout(() => {
                animateCounter(numberEl, number, text.includes("+"));
              }, 300);
            }
          }
        });
      }
    });
  }, observerOptions);

  const statsSection = document.querySelector(".landing-stats");
  if (statsSection) {
    statsObserver.observe(statsSection);
  }

  // Parallax effect for hero section
  let lastScrollY = 0;
  const heroSection = document.querySelector(".landing-hero");
  if (heroSection) {
    window.addEventListener("scroll", () => {
      const scrollY = window.scrollY;
      if (scrollY < window.innerHeight) {
        const parallaxValue = scrollY * 0.5;
        heroSection.style.transform = `translateY(${parallaxValue}px)`;
      }
      lastScrollY = scrollY;
    });
  }

  // Add smooth reveal animations for buttons
  const buttons = document.querySelectorAll(".button");
  buttons.forEach((button, index) => {
    button.style.opacity = "0";
    button.style.transform = "translateY(20px)";
    setTimeout(() => {
      button.style.transition = "all 0.6s cubic-bezier(0.4, 0, 0.2, 1)";
      button.style.opacity = "1";
      button.style.transform = "translateY(0)";
    }, 400 + index * 100);
  });
})();

