document.addEventListener("DOMContentLoaded", function() {

  // ==========================================
  // 1. MOBILE NAVBAR PANELS
  // ==========================================
  const mobileToggle = document.getElementById("mobileToggle");
  const closeMobileMenu = document.getElementById("closeMobileMenu");
  const mobileMenuPanel = document.getElementById("mobileMenuPanel");
  const mobileMenuOverlay = document.getElementById("mobileMenuOverlay");

  if (mobileToggle && mobileMenuPanel && mobileMenuOverlay) {
    function toggleMobileMenu(open) {
      if (open) {
        mobileMenuPanel.classList.add("open");
        mobileMenuOverlay.classList.add("open");
        document.body.style.overflow = "hidden";
      } else {
        mobileMenuPanel.classList.remove("open");
        mobileMenuOverlay.classList.remove("open");
        document.body.style.overflow = "";
      }
    }
    mobileToggle.addEventListener("click", () => toggleMobileMenu(true));
    closeMobileMenu.addEventListener("click", () => toggleMobileMenu(false));
    mobileMenuOverlay.addEventListener("click", () => toggleMobileMenu(false));
  }

  // Mobile submenu toggle
  const subToggle = document.querySelector(".mobile-sub-toggle");
  if (subToggle) {
    subToggle.addEventListener("click", function() {
      this.classList.toggle("open");
      const subLinks = this.nextElementSibling;
      if (subLinks) subLinks.classList.toggle("open");
    });
  }

  // ==========================================
  // 2. HERO SLIDER AUTO-CYCLE
  // ==========================================
  const heroSlides = document.querySelectorAll(".hero-slide");
  const heroDots = document.querySelectorAll(".hero-dot");
  let currentSlide = 0;
  let slideInterval = null;

  if (heroSlides.length > 1 && heroDots.length > 0) {
    function showSlide(index) {
      heroSlides.forEach(slide => slide.classList.remove("active"));
      heroDots.forEach(dot => dot.classList.remove("active"));
      currentSlide = (index + heroSlides.length) % heroSlides.length;
      heroSlides[currentSlide].classList.add("active");
      heroDots[currentSlide].classList.add("active");
    }

    function nextSlide() { showSlide(currentSlide + 1); }

    function startSlideShow() {
      if (slideInterval) clearInterval(slideInterval);
      slideInterval = setInterval(nextSlide, 6000);
    }

    heroDots.forEach((dot, idx) => {
      dot.addEventListener("click", () => {
        showSlide(idx);
        startSlideShow();
      });
    });

    startSlideShow();
  }

  // ==========================================
  // 3. PRODUCT TAB SWITCHING
  // ==========================================
  const tabLinks = document.querySelectorAll(".tab-link");
  const tabContents = document.querySelectorAll(".tab-content");

  if (tabLinks.length > 0 && tabContents.length > 0) {
    tabLinks.forEach(link => {
      link.addEventListener("click", function() {
        const targetTab = this.getAttribute("data-tab");
        tabLinks.forEach(l => l.classList.remove("active"));
        tabContents.forEach(c => c.classList.remove("active"));
        this.classList.add("active");
        const targetContent = document.getElementById(targetTab);
        if (targetContent) targetContent.classList.add("active");
      });
    });
  }

  // ==========================================
  // 4. GALLERY IMAGES SWITCHING
  // ==========================================
  const galleryThumbs = document.querySelectorAll(".gallery-thumb");
  const mainGalleryImg = document.getElementById("mainGalleryImg");

  if (galleryThumbs.length > 0 && mainGalleryImg) {
    galleryThumbs.forEach(thumb => {
      thumb.addEventListener("click", function() {
        galleryThumbs.forEach(t => t.classList.remove("active"));
        this.classList.add("active");
        const newSrc = this.getAttribute("data-large");
        mainGalleryImg.setAttribute("src", newSrc);
      });
    });
  }

  // ==========================================
  // 5. FACTS COUNTER ANIMATION (IntersectionObserver)
  // ==========================================
  const counters = document.querySelectorAll(".fact-counter");
  if (counters.length > 0) {
    const counterObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const counter = entry.target;
          const target = +counter.getAttribute("data-target");
          const duration = 1500; // Animation duration in ms
          const startTime = performance.now();
          
          const animateCount = (currentTime) => {
            const elapsedTime = currentTime - startTime;
            const progress = Math.min(elapsedTime / duration, 1);
            // Ease out quad formula
            const easeProgress = progress * (2 - progress);
            const currentValue = Math.floor(easeProgress * target);
            
            counter.innerText = currentValue;
            
            if (progress < 1) {
              requestAnimationFrame(animateCount);
            } else {
              counter.innerText = target;
            }
          };
          
          requestAnimationFrame(animateCount);
          observer.unobserve(counter); // Trigger once per element
        }
      });
    }, { threshold: 0.1 });
    
    counters.forEach(counter => {
      counterObserver.observe(counter);
    });
  }

  // ==========================================
  // 6. SCROLL REVEAL ANIMATIONS
  // ==========================================
  const revealElements = document.querySelectorAll(".reveal, .reveal-left, .reveal-right");

  function runReveal() {
    revealElements.forEach(el => {
      const rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight - 60) {
        el.classList.add("visible");
      }
    });
  }

  if (revealElements.length > 0) {
    window.addEventListener("scroll", runReveal, { passive: true });
    runReveal();
  }

  // ==========================================
  // 7. BACK TO TOP BUTTON
  // ==========================================
  const backToTopBtn = document.getElementById("backToTop");

  if (backToTopBtn) {
    window.addEventListener("scroll", function() {
      backToTopBtn.classList.toggle("show", window.scrollY > 400);
    });

    backToTopBtn.addEventListener("click", function() {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // Sticky Navbar Scroll Effect (hysteresis thresholds)
  // Engage compact state at scrollY > 80, disengage only when scrollY < 30.
  // The ~50px gap absorbs trackpad momentum / rubber-band jitter at the boundary.
  const navBarElement = document.querySelector(".nav-bar");
  const ENGAGE_THRESHOLD = 80;
  const DISENGAGE_THRESHOLD = 30;

  if (navBarElement) {
    let lastToggleTime = 0;
    const DEBOUNCE_MS = 80;

    window.addEventListener("scroll", function () {
      const now = performance.now();
      if (now - lastToggleTime < DEBOUNCE_MS) return;

      const y = Math.max(0, window.scrollY);
      const isScrolled = navBarElement.classList.contains("scrolled");

      if (!isScrolled && y > ENGAGE_THRESHOLD) {
        navBarElement.classList.add("scrolled");
        lastToggleTime = now;
      } else if (isScrolled && y < DISENGAGE_THRESHOLD) {
        navBarElement.classList.remove("scrolled");
        lastToggleTime = now;
      }
    }, { passive: true });

    // Set initial state on load (handles back/forward cache)
    requestAnimationFrame(() => {
      if (Math.max(0, window.scrollY) > ENGAGE_THRESHOLD) {
        navBarElement.classList.add("scrolled");
      }
    });
  }

  // ==========================================
  // 8. TOAST NOTIFICATION SYSTEM
  // ==========================================
  const toastContainer = document.querySelector(".toast-container");
  if (!toastContainer) {
    const container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  window.showToast = function(message, type) {
    const container = document.querySelector(".toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = "toast" + (type === "error" ? " toast-error" : " toast-success");

    const iconSvg = type === "error"
      ? '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>'
      : '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="#2da149" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>';

    toast.innerHTML = iconSvg + '<span class="toast-message">' + message + '</span><button class="toast-close">&times;</button>';
    container.appendChild(toast);

    toast.querySelector(".toast-close").addEventListener("click", () => toast.remove());
    setTimeout(() => { if (toast.parentNode) toast.remove(); }, 4000);
  };

  // ==========================================
  // 9. CONTACT FORM SUBMISSION
  // ==========================================
  const contactForm = document.getElementById("contactForm");

  if (contactForm) {
    contactForm.addEventListener("submit", function(e) {
      e.preventDefault();

      const submitBtn = contactForm.querySelector('button[type="submit"]');
      const originalBtnText = submitBtn.innerHTML;

      const nameField = document.getElementById("name");
      const emailField = document.getElementById("email");
      const messageField = document.getElementById("message");
      const honeypotField = document.getElementById("website");

      if (honeypotField && honeypotField.value.trim() !== "") {
        showToast("Thank you! Your enquiry has been sent successfully.", "success");
        contactForm.reset();
        return;
      }

      if (!nameField.value.trim()) {
        showToast("Please enter your name.", "error");
        nameField.focus();
        return;
      }

      if (!emailField.value.trim() || !validateEmail(emailField.value)) {
        showToast("Please enter a valid email address.", "error");
        emailField.focus();
        return;
      }

      if (!messageField.value.trim()) {
        showToast("Please enter your message.", "error");
        messageField.focus();
        return;
      }

      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner"></span> Sending...';

      const formDataObj = {};
      new FormData(contactForm).forEach((value, key) => {
        formDataObj[key] = value;
      });

      fetch("/api/send-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formDataObj)
      })
      .then(async response => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
        const data = await response.json();
        if (response.ok) {
          showToast("Success! Your message has been sent successfully.", "success");
          contactForm.reset();
        } else {
          showToast(data.error || "Failed to send message. Please try again.", "error");
        }
      })
      .catch(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
        showToast("An error occurred. Please check your network and try again.", "error");
      });
    });
  }

  function validateEmail(email) {
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
  }

  // ======= COOKIE CONSENT PANEL =======
  const cookieConsentPanel = document.getElementById('cookieConsentPanel');
  const cookieBtnAccept = document.getElementById('cookieBtnAccept');
  const cookieBtnReject = document.getElementById('cookieBtnReject');

  if (cookieConsentPanel && cookieBtnAccept && cookieBtnReject) {
    // Show panel if consent hasn't been set yet
    if (!localStorage.getItem('cookie-consent')) {
      setTimeout(() => {
        cookieConsentPanel.classList.add('active');
      }, 1000); // Small delay for better UX entry
    }

    cookieBtnAccept.addEventListener('click', () => {
      localStorage.setItem('cookie-consent', 'granted');
      if (typeof gtag === 'function') {
        gtag('consent', 'update', {
          'ad_storage': 'granted',
          'ad_user_data': 'granted',
          'ad_personalization': 'granted',
          'analytics_storage': 'granted'
        });
      }
      cookieConsentPanel.classList.remove('active');
    });

    cookieBtnReject.addEventListener('click', () => {
      localStorage.setItem('cookie-consent', 'denied');
      if (typeof gtag === 'function') {
        gtag('consent', 'update', {
          'ad_storage': 'denied',
          'ad_user_data': 'denied',
          'ad_personalization': 'denied',
          'analytics_storage': 'denied'
        });
      }
      cookieConsentPanel.classList.remove('active');
    });
  }

});
