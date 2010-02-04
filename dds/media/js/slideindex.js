function getfilters() {
  var classes = new Array();
  classes.push('.slidebox');
  var loc = $('#locationselect').val();
  var group = $('#groupselect').val();
  var showoffline = $('#showoffline').is(':checked');
  if (group != '') {
    classes.push('.slide-group-'+group);
  }
  classlist = classes.join('');
  return classlist;
}

function filtergrouplocation() {
  filterlist = getfilters();
  $('.slidebox').hide();
  $(filterlist).show();
}

function resetfilterform() {
  document.getElementById('slidefilterform').reset();
  filtergrouplocation();
}

function setupdialogs() {
  $('.slidebox').each(function() {
      var id = $(this).children('.infopopup').attr('id');
      $('#'+id).dialog({modal:true,autoOpen:false,
                        resizable:false,draggable:false});
      $(this).click(function() {
        $('#'+id).dialog('open');});
      });
}

$(document).ready(function() {
  setupdialogs();
  $('#showoffline').change(filtergrouplocation);
  $('#groupselect').change(filtergrouplocation);
  $('#resetfilter').click(resetfilterform);
  $('.slide-details-save').live("click", function(){
	  $.post("", this.id, function(data) {
		  $('.result').html(data);
	      });});
  $('.slide-details-remove').live("click", function(){
	  $.post("",{ remove : this.id } , function(data) {
		  $('.result').html(data);
	      });});
  
});
