/* After-hours callback boxes (v1). Phones: Mon-Fri 9 AM-5 PM America/Chicago.
   Without JS the in-hours layout shows unchanged. */
(function(){
  function chicagoNow(){
    try{
      var p=new Intl.DateTimeFormat('en-US',{timeZone:'America/Chicago',weekday:'short',hour:'numeric',hourCycle:'h23'}).formatToParts(new Date());
      var o={};p.forEach(function(x){o[x.type]=x.value;});
      var d=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].indexOf(o.weekday);
      return {day:d,hour:parseInt(o.hour,10)%24};
    }catch(e){return null;}
  }
  var n=chicagoNow(); if(!n||n.day<0) return;
  var weekday=n.day>=1&&n.day<=5;
  if(weekday&&n.hour>=9&&n.hour<17) return;
  var when;
  if(weekday&&n.hour<9) when='this morning, once our phones open';
  else if(n.day===5||n.day===6||n.day===0) when='on Monday';
  else when='tomorrow';
  var TITLE='Our phones are closed right now, but we\u2019d love to hear from you.';
  var LEAD='Leave your name and number, and we\u2019ll call you back '+when+', at your preferred time whenever we can.';
  function phoneLine(call,cls){
    var p=document.createElement('p');p.className=cls;
    p.appendChild(document.createTextNode('Phones open Mon to Fri, 9 AM to 5 PM: '));
    call.className=call.className.replace(/\bqcb-call\b|\bcta-call\b/g,'').trim()+' ah-phonelink';
    call.textContent='(815) 993-1614';p.appendChild(call);return p;
  }
  function apply(){
    document.documentElement.classList.add('after-hours');
    document.querySelectorAll('.qcb').forEach(function(b){
      var t=b.querySelector('.qcb-title'),c=b.querySelector('.qcb-call'),l=b.querySelector('.qcb-lead'),f=b.querySelector('form');
      if(!t||!c||!f) return;
      b.classList.add('after-hours');
      t.textContent=TITLE;
      if(l){l.textContent=LEAD;t.parentNode.insertBefore(l,t.nextSibling);}
      f.parentNode.insertBefore(phoneLine(c,'qcb-ah-phone'),f.nextSibling);
    });
    document.querySelectorAll('.callback-cta').forEach(function(s){
      var h=s.querySelector('h2'),c=s.querySelector('.cta-call'),l=s.querySelector('.cta-lead'),box=s.querySelector('.callback-box');
      if(!h||!c||!box) return;
      s.classList.add('after-hours');
      h.textContent=TITLE;
      if(l){l.textContent=LEAD;h.parentNode.insertBefore(l,h.nextSibling);}
      box.parentNode.insertBefore(phoneLine(c,'cta-ah-phone'),box.nextSibling);
    });
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',apply); else apply();
})();
