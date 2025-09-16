// Base Template JavaScript

// Mobile Navigation Toggle
function toggleMobileNav() {
  const navbar = document.getElementById("leftNavbar");
  navbar.classList.toggle("mobile-open");
}

// Navbar Collapse Toggle
function toggleNavbarCollapse() {
  const navbar = document.getElementById("leftNavbar");
  const mainContent = document.querySelector(".main-content");
  
  navbar.classList.toggle("collapsed");
  mainContent.classList.toggle("navbar-collapsed");
  
  // Save collapse state to localStorage
  const isCollapsed = navbar.classList.contains("collapsed");
  localStorage.setItem("navbarCollapsed", isCollapsed);
  
  // Close all dropdowns when collapsing
  if (isCollapsed) {
    const allDropdowns = document.querySelectorAll('.nav-dropdown');
    allDropdowns.forEach(dd => dd.classList.remove('open'));
  }
}

// Show mobile toggle on small screens
function checkScreenSize() {
  const mobileToggle = document.querySelector(".mobile-toggle");
  if (window.innerWidth <= 768) {
    mobileToggle.style.display = "block";
  } else {
    mobileToggle.style.display = "none";
    document.getElementById("leftNavbar").classList.remove("mobile-open");
  }
}

// Dropdown functionality
function toggleDropdown(dropdownId) {
  const dropdown = document.getElementById(dropdownId);
  const allDropdowns = document.querySelectorAll('.nav-dropdown');

  // Close all other dropdowns
  allDropdowns.forEach(dd => {
    if (dd.id !== dropdownId) {
      dd.classList.remove('open');
    }
  });

  // Toggle current dropdown
  dropdown.classList.toggle('open');
}

// Initialize base functionality
document.addEventListener('DOMContentLoaded', function() {
  // Check screen size on load and resize
  window.addEventListener("resize", checkScreenSize);
  window.addEventListener("load", checkScreenSize);
  
  // Restore navbar collapse state from localStorage
  const isCollapsed = localStorage.getItem("navbarCollapsed") === "true";
  if (isCollapsed) {
    const navbar = document.getElementById("leftNavbar");
    const mainContent = document.querySelector(".main-content");
    navbar.classList.add("collapsed");
    mainContent.classList.add("navbar-collapsed");
  }
  
  // Add tooltips to nav links for collapsed state
  addNavTooltips();

  // Close mobile nav when clicking outside
  document.addEventListener("click", function (event) {
    const navbar = document.getElementById("leftNavbar");
    const toggle = document.querySelector(".mobile-toggle");

    if (
      window.innerWidth <= 768 &&
      navbar && toggle &&
      !navbar.contains(event.target) &&
      !toggle.contains(event.target)
    ) {
      navbar.classList.remove("mobile-open");
    }
  });

  // Close dropdowns when clicking outside
  document.addEventListener('click', function (event) {
    const dropdowns = document.querySelectorAll('.nav-dropdown');
    const clickedInsideDropdown = event.target.closest('.nav-dropdown');

    if (!clickedInsideDropdown) {
      dropdowns.forEach(dropdown => {
        dropdown.classList.remove('open');
      });
    }
  });
});

// Add tooltips to navigation links
function addNavTooltips() {
  const navLinks = document.querySelectorAll('.nav-link');
  
  navLinks.forEach(link => {
    const textSpan = link.querySelector('span:not(.nav-icon)');
    if (textSpan) {
      const text = textSpan.textContent.trim();
      link.setAttribute('data-tooltip', text);
    }
  });
  
  // Add tooltips to dropdown toggles
  const dropdownToggles = document.querySelectorAll('.nav-dropdown-toggle');
  dropdownToggles.forEach(toggle => {
    const textSpan = toggle.querySelector('span span:not(.nav-icon)');
    if (textSpan) {
      const text = textSpan.textContent.trim();
      toggle.setAttribute('data-tooltip', text);
    }
  });
}