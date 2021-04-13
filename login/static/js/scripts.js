$("form[name=signup_form").submit(function(e) {

    var $form = $(this);
    var $error = $form.find(".error");
    var data = $form.serialize();
  
    $.ajax({
      url: "/user/signup",
      type: "POST",
      data: data,
      dataType: "json",
      success: function(resp) {
        window.location.href = "/dashboard/";
        //console.log(resp);
      },
      error: function(resp) {
        $error.text(resp.responseJSON.error).removeClass("error--hidden");
        console.log(resp);
      }
    });
  
    e.preventDefault();
  });

$("form[name=login_form").submit(function(e) {

    var $form = $(this);
    var $error = $form.find(".error");
    var data = $form.serialize();
  
    $.ajax({
      url: "/user/login",
      type: "POST",
      data: data,
      dataType: "json",
      success: function(resp) {
        window.location.href = "/dashboard/";
      },
      error: function(resp) {
        $error.text(resp.responseJSON.error).removeClass("error--hidden");
      }
    });
  
    e.preventDefault();
  });

  $("form[name=add_article_form").submit(function(e) {

    var $form = $(this);
    var $error = $form.find(".error");
    var data = $form.serialize();
  
    $.ajax({
      url: "/write_article",
      type: "POST",
      data: data,
      dataType: "json",
      success: function(resp) {
        window.location.href = "/dashboard/";
      },
      error: function(resp) {
        $error.text(resp.responseJSON.error).removeClass("error--hidden");
      }
    });
  
    e.preventDefault();
  });
  
  // $("form[name=delete_article_form").submit(function(e) {

  //   var $form = $(this);
  //   var $error = $form.find(".error");
  //   var data = $form.serialize();
  
  //   $.ajax({
  //     url: "/delete_article/",
  //     type: "DELETE",
  //     data: data,
  //     dataType: "json",
  //     success: function(resp) {
  //       window.location.href = "/dashboard/";
  //     },
  //     error: function(resp) {
  //       $error.text(resp.responseJSON.error).removeClass("error--hidden");
  //     }
  //   });
  
  //   e.preventDefault();
  // });