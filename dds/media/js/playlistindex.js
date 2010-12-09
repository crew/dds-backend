function deleteplaylist(src, removalid) {
  if(!confirm("Are you sure you want to delete this playlist?  Click OK to delete the playlist or Cancel to not delete the playlist."))
      return;
  $.ajax({type:'POST', data:{remove:removalid},
          success:function(data) {
	      $(src).parent().fadeOut();
          },
          error:function(xhr,textStatus,errorThrown) {
            if (xhr.status == 404) {
              alert('The playlist you are trying to delete has vanished!');
            }
            else if (xhr.status == 500) {
              alert('There was an internal server error while deleting!');
            }
            else if (xhr.status == 400) {
              alert('The deletion request was malformed. Is the page stale?');
            }
            else if (xhr.status == 403) {
              alert('Sorry, you do not have the required permissions.');
            }
          }
  });
}
