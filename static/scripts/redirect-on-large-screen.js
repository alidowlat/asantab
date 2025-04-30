checkSize();
window.onresize = function () {
  checkSize();
};

function checkSize() {
  if (window.innerWidth > 1024) window.location.href = "./index.html"; // Change this to the page you want to Redirect
}
