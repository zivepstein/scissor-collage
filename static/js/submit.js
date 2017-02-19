$("#data").submit(function(e){
  e.preventDefault();
  console.log(e);
  console.log(this);
  // var formData = new FormData(this);
  // e.preventDefault();
  // console.log(formData);
  // $.ajax({
  //     url: '/upload',
  //     type: 'POST',
  //     data: formData,
  //     async: false,
  //     cache: false,
  //     contentType: false,
  //     processData: false
  // });
  // return false;
});
