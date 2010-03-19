function gotoplaylist(selector) {
  document.location.href = $(this).val();
}

$(function() {
  $('#playlist').change(gotoplaylist);
});
