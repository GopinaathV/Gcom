// Get the modal
window.onload = function(){

for (var i = 1; i < 5; i++) {


var modal = document.getElementById("myModal_"+i);
var img = document.getElementById("myImg_"+i);
var modalImg = document.getElementById("img_"+i);
var captionText = document.getElementById("caption_"+i);
if (modal && img && modalImg){
    console.log(modal,img,modalImg,captionText)
    img.onclick = function(){
      modal.style.display = "block";
      modalImg.src = this.src;
      captionText.innerHTML = this.alt;
    }



    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[i];
    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
      console.log("Clicked")
      modal.style.display = "none";
    }
}
else{
   pass;
}
}


};
