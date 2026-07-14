document.addEventListener("DOMContentLoaded", function() {
  var segmentBtns = document.querySelectorAll(".pill-btn");
  var formBtns = document.querySelectorAll(".form-pill");
  var searchInput = document.getElementById("catalogSearch");
  var clearSearchBtn = document.getElementById("clearSearch");
  var moreFiltersToggle = document.getElementById("moreFiltersToggle");
  var secondaryFiltersPanel = document.getElementById("secondaryFiltersPanel");
  var productCards = document.querySelectorAll("#productsCatalogGrid .product-card");
  var productsGrid = document.getElementById("productsCatalogGrid");
  var noResultsAlert = document.getElementById("noResultsAlert");
  var resetFiltersButton = document.getElementById("resetFiltersButton");
  var resetAllFiltersBtn = document.getElementById("resetAllFiltersBtn");

  var activeSegment = "all";
  var activeForm = "all";
  var searchQuery = "";

  if (moreFiltersToggle && secondaryFiltersPanel) {
    moreFiltersToggle.addEventListener("click", function() {
      var isExpanded = this.getAttribute("aria-expanded") === "true";
      this.setAttribute("aria-expanded", !isExpanded);
      this.classList.toggle("active");
      secondaryFiltersPanel.classList.toggle("open");
    });
  }

  function applyFilters() {
    productsGrid.classList.add("filtering-transition");

    setTimeout(function() {
      var visibleCount = 0;
      
      productCards.forEach(function(card) {
        var segmentsAttr = card.getAttribute("data-segments") || "";
        var productSegments = segmentsAttr.split(",").map(function(s) { return s.trim(); });
        var productForm = card.getAttribute("data-form") || "N/A";
        var productName = card.querySelector(".product-title").textContent.toLowerCase();
        var productDesc = card.querySelector(".product-desc").textContent.toLowerCase();
        var subTypeTag = card.querySelector(".tag-subtype") ? card.querySelector(".tag-subtype").textContent.toLowerCase() : "";

        var matchesSegment = activeSegment === "all" || productSegments.includes(activeSegment);
        var matchesForm = activeForm === "all" || productForm.toLowerCase() === activeForm.toLowerCase();
        
        var q = searchQuery.toLowerCase().trim();
        var matchesSearch = q === "" || 
                              productName.includes(q) || 
                              productDesc.includes(q) ||
                              subTypeTag.includes(q);

        if (matchesSegment && matchesForm && matchesSearch) {
          card.style.display = "flex";
          setTimeout(function() { card.style.opacity = "1"; card.style.transform = "translateY(0)"; }, 20);
          visibleCount++;
        } else {
          card.style.display = "none";
          card.style.opacity = "0";
          card.style.transform = "translateY(10px)";
        }
      });

      if (visibleCount === 0) {
        noResultsAlert.style.display = "block";
        setTimeout(function() { noResultsAlert.style.opacity = "1"; }, 20);
      } else {
        noResultsAlert.style.display = "none";
        noResultsAlert.style.opacity = "0";
      }

      var hasActiveFilters = activeSegment !== "all" || activeForm !== "all" || searchQuery !== "";
      if (resetAllFiltersBtn) {
        resetAllFiltersBtn.style.display = hasActiveFilters ? "inline-flex" : "none";
      }

      productsGrid.classList.remove("filtering-transition");
    }, 200);
  }

  segmentBtns.forEach(function(btn) {
    btn.addEventListener("click", function() {
      segmentBtns.forEach(function(b) { b.classList.remove("active"); });
      this.classList.add("active");
      activeSegment = this.getAttribute("data-segment");
      applyFilters();
    });
  });

  formBtns.forEach(function(btn) {
    btn.addEventListener("click", function() {
      formBtns.forEach(function(b) { b.classList.remove("active"); });
      this.classList.add("active");
      activeForm = this.getAttribute("data-form");
      applyFilters();
    });
  });

  if (searchInput) {
    searchInput.addEventListener("input", function() {
      searchQuery = this.value;
      if (clearSearchBtn) {
        clearSearchBtn.style.display = searchQuery ? "flex" : "none";
      }
      applyFilters();
    });
  }

  if (clearSearchBtn) {
    clearSearchBtn.addEventListener("click", function() {
      searchInput.value = "";
      searchQuery = "";
      this.style.display = "none";
      searchInput.focus();
      applyFilters();
    });
  }

  function resetAll() {
    activeSegment = "all";
    activeForm = "all";
    searchQuery = "";
    
    segmentBtns.forEach(function(b) { b.classList.remove("active"); });
    segmentBtns[0].classList.add("active");
    
    formBtns.forEach(function(b) { b.classList.remove("active"); });
    formBtns[0].classList.add("active");

    if (searchInput) {
      searchInput.value = "";
      if (clearSearchBtn) clearSearchBtn.style.display = "none";
    }

    applyFilters();
  }

  if (resetFiltersButton) resetFiltersButton.addEventListener("click", resetAll);
  if (resetAllFiltersBtn) resetAllFiltersBtn.addEventListener("click", resetAll);

  function handleUrlHash() {
    var hash = window.location.hash;
    if (hash) {
      var targetSegment = hash.substring(1);
      var targetBtn = document.querySelector('.pill-btn[data-segment="' + targetSegment + '"]');
      if (targetBtn) {
        segmentBtns.forEach(function(b) { b.classList.remove("active"); });
        targetBtn.classList.add("active");
        activeSegment = targetSegment;
        
        targetBtn.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
        applyFilters();
      }
    }
  }

  handleUrlHash();
  window.addEventListener("hashchange", handleUrlHash);
});
