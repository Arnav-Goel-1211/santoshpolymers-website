document.addEventListener("DOMContentLoaded", function() {
  var mainGallery = document.getElementById("pdpMainGallery");
  var lightboxModal = document.getElementById("pdpLightboxModal");
  var lightboxImg = document.getElementById("pdpLightboxImg");
  var lightboxClose = document.getElementById("pdpLightboxClose");
  
  if (mainGallery && lightboxModal && lightboxImg) {
    mainGallery.addEventListener("click", function() {
      var activeImgSrc = document.getElementById("mainGalleryImg").getAttribute("src");
      lightboxImg.setAttribute("src", activeImgSrc);
      lightboxModal.classList.add("open");
      lightboxModal.setAttribute("aria-hidden", "false");
      document.body.style.overflow = "hidden";
    });
    
    function closeLightbox() {
      lightboxModal.classList.remove("open");
      lightboxModal.setAttribute("aria-hidden", "true");
      document.body.style.overflow = "";
    }
    
    if (lightboxClose) lightboxClose.addEventListener("click", closeLightbox);
    lightboxModal.addEventListener("click", function(e) {
      if (e.target === lightboxModal || e.target.classList.contains("pdp-lightbox-content")) {
        closeLightbox();
      }
    });
    
    document.addEventListener("keydown", function(e) {
      if (e.key === "Escape" && lightboxModal.classList.contains("open")) {
        closeLightbox();
      }
    });
  }
});
