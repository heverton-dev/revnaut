(function(){
  var els=document.querySelectorAll('.reveal');
  if(!('IntersectionObserver' in window)){els.forEach(function(e){e.classList.add('in')});return;}
  var io=new IntersectionObserver(function(entries){
    entries.forEach(function(en){if(en.isIntersecting){en.target.classList.add('in');io.unobserve(en.target);}});
  },{rootMargin:'0px 0px -8% 0px',threshold:.08});
  els.forEach(function(e){io.observe(e)});
})();
