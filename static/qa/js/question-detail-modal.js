    var modalBounty = document.getElementById("bounty-model-content");
    var btn = document.getElementById("bounty-model-open-button");
    var span = document.getElementsByClassName("close")[0]; 
    btn.onclick = function () {
      modalBounty.style.display = "block";
    }
    span.onclick = function () {
      modalBounty.style.display = "none";
    }
    window.onclick = function (event) {
      if (event.target == modalBounty) {
        modalBounty.style.display = "none";
      }
    }

$(document).keydown(function(event) { 
  if (event.keyCode == 27) { 
    $('#bounty-model-content').hide();
  }
});

$(document).ready(function() {
    var base_color_bounty = "rgb(230,230,230)";
    var activeBountyColor = "rgb(237, 40, 70)";

    var bountyCir = 1;
    var BountyLength = $(".sectionBounty").length - 1;
    $("#previous").addClass("disabled");
    $("#submit").addClass("disabled");

    $("section").not("section:nth-of-type(1)").hide();
    $("section").not("section:nth-of-type(1)").css('transform','translateX(100px)');

    var svgWidth = BountyLength * 200 + 24;
    $("#svg_wrapping").html(
      '<svg version="1.1" id="svg_from_section" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 ' +
        svgWidth +
        ' 24" xml:space="preserve"></svg>'
    );

function createSVG(tag, attrs) {
      var elt = document.createElementNS("http://www.w3.org/2000/svg", tag);
      for (var k in attrs) elt.setAttribute(k, attrs[k]);
      return elt;
    }

    for (i = 0; i < BountyLength; i++) {
      var positionX = 12 + i * 200;
      var rect = createSVG("rect", { x: positionX, y: 9, width: 200, height: 6 });
      document.getElementById("svg_from_section").appendChild(rect);
      // <g><rect x="12" y="9" width="200" height="6"></rect></g>'
      var bountyCircle = createSVG("circle", {
        cx: positionX,
        cy: 12,
        r: 12,
        width: positionX,
        height: 6
      });
      document.getElementById("svg_from_section").appendChild(bountyCircle);
    }

    var bountyCircle = createSVG("circle", {
      cx: positionX + 200,
      cy: 12,
      r: 12,
      width: positionX,
      height: 6
    });
    document.getElementById("svg_from_section").appendChild(bountyCircle);

    $('#svg_from_section rect').css('fill',base_color_bounty);
    $('#svg_from_section circle').css('fill',base_color_bounty);
    $("circle:nth-of-type(1)").css("fill", activeBountyColor);

     
    $(".button").click(function () {
      $("#svg_from_section rect").css("fill", activeBountyColor);
      $("#svg_from_section circle").css("fill", activeBountyColor);
      var id = $(this).attr("id");
      if (id == "nextSection") {
        $("#previous").removeClass("disabled");
        if (bountyCir >= BountyLength) {
          $(this).addClass("disabled");
          $('#submit').removeClass("disabled");
        }
        if (bountyCir <= BountyLength) {
          bountyCir++;
        }
      } else if (id == "previous") {
        $("#nextSection").removeClass("disabled");
        $('#submit').addClass("disabled");
        if (bountyCir <= 2) {
          $(this).addClass("disabled");
        }
        if (bountyCir > 1) {
          bountyCir--;
        }
      }
      var circle_child = bountyCir + 1;
      $("#svg_from_section rect:nth-of-type(n + " + bountyCir + ")").css(
        "fill",
        base_color_bounty
      );
      $("#svg_from_section circle:nth-of-type(n + " + circle_child + ")").css(
        "fill",
        base_color_bounty
      );
      var currentSection = $("section:nth-of-type(" + bountyCir + ")");
      currentSection.fadeIn();
      currentSection.css('transform','translateX(0)');
     currentSection.prevAll('section').css('transform','translateX(-100px)');
      currentSection.nextAll('section').css('transform','translateX(100px)');
      $('section').not(currentSection).hide();
    });

});



    const modal=(()=>{var e={},t={speedOpen:50,speedClose:250,toggleClass:"hidden",selectorTarget:"[data-modal-target]",selectorTrigger:"[data-modal-trigger]",selectorClose:"[data-modal-close]",selectorOverlay:"[data-modal-overlay]",selectorWrapper:"[data-modal-wrapper]",selectorInputFocus:"[data-modal-input-focus]"};Element.prototype.closest||(Element.prototype.matches||(Element.prototype.matches=Element.prototype.msMatchesSelector||Element.prototype.webkitMatchesSelector),Element.prototype.closest=function(e){var t=this;if(!document.documentElement.contains(this))return null;do{if(t.matches(e))return t;t=t.parentElement}while(null!==t);return null});var a=function(e){"true"===e.getAttribute("aria-expanded")?e.setAttribute("aria-expanded",!1):e.setAttribute("aria-expanded",!0)},s=function(e,s){var r=s;if("string"==typeof e&&(r=document.getElementById(e))&&r.setAttribute("data-auto-trigger",""),r){var o=r.querySelector(t.selectorOverlay),l=r.querySelector(t.selectorWrapper),n=r.querySelector(t.selectorInputFocus);r.classList.remove(t.toggleClass),document.documentElement.style.overflow="hidden","string"!=typeof e&&a(e),setTimeout(function(){if(o){var e=o.getAttribute("data-class-in").split(" "),t=o.getAttribute("data-class-out").split(" ");o.classList.remove(...t),o.classList.add(...e)}if(l){var a=l.getAttribute("data-class-in").split(" "),s=l.getAttribute("data-class-out").split(" ");l.classList.remove(...s),l.classList.add(...a)}var i,c,d,u;n&&n.focus(),c=(i=r).querySelectorAll('a[href]:not([disabled]), button:not([disabled]), textarea:not([disabled]), input[type="text"]:not([disabled]), input[type="radio"]:not([disabled]), input[type="checkbox"]:not([disabled]), select:not([disabled])'),d=c[0],u=c[c.length-1],i.addEventListener("keydown",function(e){("Tab"===e.key||9===e.keyCode)&&(e.shiftKey?document.activeElement===d&&(u.focus(),e.preventDefault()):document.activeElement===u&&(d.focus(),e.preventDefault()))})},t.speedOpen)}},r=function(e){var s=e.closest(t.selectorTarget),r=document.querySelector('[aria-controls="'+s.id+'"'),o=s.querySelector(t.selectorOverlay),l=s.querySelector(t.selectorWrapper);if(null===r&&(r=document.querySelector('a[href="#'+s.id+'"')),o){var n=o.getAttribute("data-class-in").split(" "),i=o.getAttribute("data-class-out").split(" ");o.classList.remove(...n),o.classList.add(...i)}if(l){var c=l.getAttribute("data-class-in").split(" "),d=l.getAttribute("data-class-out").split(" ");l.classList.remove(...c),l.classList.add(...d)}document.documentElement.style.overflow="",s.hasAttribute("data-auto-trigger")?s.removeAttribute("data-auto-trigger"):a(r),setTimeout(function(){s.classList.add(t.toggleClass)},t.speedClose)},o=function(e){var a,o,l=e.target,n=null;l.hasAttribute(t.selectorTrigger.replace(/[\[\]']+/g,""))&&l.hasAttribute("aria-controls")?(a=l.closest(t.selectorTrigger),o=document.getElementById(a.getAttribute("aria-controls")),n=!0):l.hash&&l.hash.substr(1).indexOf("modal")>-1&&(a=l,o=document.getElementById(l.hash.substr(1)),n=!0);var i=l.closest(t.selectorClose);n&&o&&s(a,o),i&&r(i),(n||i)&&e.preventDefault()},l=function(e){if("Escape"===e.key||27===e.keyCode){var a,s=document.querySelectorAll(t.selectorTarget);for(a=0;a<s.length;++a)s[a].classList.contains(t.toggleClass)||r(s[a])}};return e.init=function(){document.addEventListener("click",o,!1),document.addEventListener("keydown",l,!1)},e.openModal=s,e.closeModal=r,e})();

