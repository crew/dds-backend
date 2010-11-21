$(document).ready(function() {
    //check for a previsously set tab
    url = window.location.href;
    loc = url.substring(url.indexOf('#')+1,url.length);
    $('.linkmenu').children('li').each( function () { $(this).removeClass('.active'); });
    if (url.indexOf('#') > 0) {
      $('#'+loc).show();
      $('.nav_'+loc).addClass('active');
    } else {
      $('.nav_status').addClass('active');
      $('#status').show();
    }
});
//cmccoy - Feel free to move me to a different file
//used on /backend/dds/orwell/templtes/orwell/landing-page.html
function setActive(tabElem,name) {
  activeTab = $(tabElem).parent('ul').children('.active')[0];
  $(activeTab).toggleClass('active');
  $(tabElem).toggleClass('active');
  loc = window.location.href;
  window.location = loc.substring(0,loc.lastIndexOf('/'))+'#'+name
  $('#viewer').children('div').hide();
  $('#'+name).show();
  return false;
}
