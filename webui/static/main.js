$(document).ready(function() {

  // Load the subnavbar dynamically if the div exists on the page already
  if( $("#subnavbar").length !== 0 ) {
    console.log("Subnavbar div exists");
    $("#subnavbar").load("subnavbar.html", function() {
      console.log("Subnavbar loaded.");
    });
  }

  // Scroll to top ---------------------------------------------------------------
  window.onscroll = function() {

    if (document.body.scrollTop > 80 || document.documentElement.scrollTop > 80) {
      document.getElementById("back-to-top").style.display = "block";
    } else {
      document.getElementById("back-to-top").style.display = "none";
    }
  };

  $('#back-to-top').on("click", function(event) {

    if (
      location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') &&
      location.hostname == this.hostname
    ) {
      // Figure out element to scroll to
      var target = $(this.hash);
      target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
      // Does a scroll target exist?
      if (target.length) {
        // Only prevent default if animation is actually gonna happen
        event.preventDefault();
        $('html, body').animate({
          scrollTop: target.offset().top
        }, 300, function() {
          // Callback after animation
          // Must change focus!
          var $target = $(target);
          $target.focus();
          if ($target.is(":focus")) { // Checking if the target was focused
            return false;
          } else {
            $target.attr('tabindex', '-1'); // Adding tabindex for elements not focusable
            $target.focus(); // Set focus again
          }
        });
      }
    }
  });

  // Link to elements with data-url attributes ------------------------------------------
  $(document).on("click", "[data-url]", function() {
    let url = $(this).data("url");
    window.location.href = url;
  });

  // FAQ Expander section -- open all accordion panels for possible printing or close ---
  $(".expander").on("click", function() {

    if ($(".expander").text() === "show all") {

      // Change the button text
      $(".expander").text("hide all");
      // show all accordions
      $("#wrapper .collapse").collapse('show');
      $(".btn").prev().find("i").addClass("fa-rotate-45");

    } else {
      // Change the button text
      $(".expander").text("show all");
      // hide all accordions
      $("#wrapper .collapse").collapse('hide');
      $(".btn").prev().find("i").removeClass("fa-rotate-45");
    }
  });


  // plus/minus toggler on opening/closing the accordions
  $(".btn-link").on("click", function() {
    // alert($(this).prev().find("i").text());
    if ($(this).prev().find("i").hasClass("fa-plus") && $(this).prev().find("i").hasClass("fa-rotate-45")) {
      $(this).prev().find("i").removeClass("fa-rotate-45");
    } else {
      $(this).prev().find("i").addClass("fa-rotate-45");
    }

  });

  // Questions & Comments form show / hide functionality --------------------------------
  $("#reason-for-contact").on("change", function() {

    if ($(this).val() === "no") {
      $(".form-optional").fadeOut().$(function(){
        $(".form-optional").addClass("d-none");
      });
    } else {
      $(".form-optional").fadeIn().removeClass("d-none");
    }
  });


  // Form validation ------------------------------------------------------------
  window.addEventListener('load', function() {
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.getElementsByClassName('needs-validation');
    // Loop over them and prevent submission
    var validation = Array.prototype.filter.call(forms, function(form) {
      form.addEventListener('submit', function(event) {
        if (form.checkValidity() === false) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add('was-validated');
      }, false);
    });
  }, false);


  // Smooth scroll for the basic reports -- find .dr-smooth-scroll
   $(".dr-smooth-scroll").click( function (event) {

      // Prevent the default link behavior
      event.preventDefault();

      // Scroll page to the link clicked over .4 seconds
      $("html, body").animate({
         scrollTop: $($(this).attr("href")).offset().top
      }, 400);

   });

   // Switch tabs
   $(".switchTabs").on("click", function() {
  // Get data attribute
  var switcher = $(this).data("switcher");
  // show the appropriate tab
  if (switcher === "sign in") {
    // Select tab by name
    $('#sign-tabs li:nth-child(odd) a').tab('show')
  } else {
    // Select tab by name
    $('#sign-tabs li:nth-child(even) a').tab('show')
  }
});

});
// document.ready
