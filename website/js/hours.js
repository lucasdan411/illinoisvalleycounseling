/* After-hours callback boxes (v2, holidays). Phones: Mon-Fri 9 AM-5 PM America/Chicago.
   Without JS the in-hours layout shows unchanged. */
(function(){
  /* Closed days. Add more here: {fixed:'MM-DD'} for the same date every year,
     or {month:M, weekday:0-6 (Sun=0), nth:N} for e.g. the 4th Thursday. */
  /* All US federal holidays. Fixed-date ones use observed rules:
     Saturday -> Friday before, Sunday -> Monday after. nth:-1 = last. */
  var HOLIDAYS=[
    {name:'New Year\u2019s Day',fixed:'01-01'},
    {name:'MLK Day',month:1,weekday:1,nth:3},
    {name:'Presidents Day',month:2,weekday:1,nth:3},
    {name:'Memorial Day',month:5,weekday:1,nth:-1},
    {name:'Juneteenth',fixed:'06-19'},
    {name:'Independence Day',fixed:'07-04'},
    {name:'Labor Day',month:9,weekday:1,nth:1},
    {name:'Columbus / Indigenous Peoples Day',month:10,weekday:1,nth:2},
    {name:'Veterans Day',fixed:'11-11'},
    {name:'Thanksgiving',month:11,weekday:4,nth:4},
    {name:'Christmas Day',fixed:'12-25'}
  ];
  var DAYS=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  function chicagoNow(){
    try{
      var p=new Intl.DateTimeFormat('en-US',{timeZone:'America/Chicago',year:'numeric',month:'numeric',day:'numeric',hour:'numeric',hourCycle:'h23'}).formatToParts(new Date());
      var o={};p.forEach(function(x){o[x.type]=x.value;});
      return {date:new Date(Date.UTC(+o.year,+o.month-1,+o.day)),hour:parseInt(o.hour,10)%24};
    }catch(e){return null;}
  }
  function observed(y,h){
    var f=h.fixed.split('-'),d=new Date(Date.UTC(y,+f[0]-1,+f[1])),w=d.getUTCDay();
    if(w===6) return new Date(d.getTime()-864e5);
    if(w===0) return new Date(d.getTime()+864e5);
    return d;
  }
  function nthDay(y,h){
    if(h.nth<0){
      var last=new Date(Date.UTC(y,h.month,0)),lw=last.getUTCDay();
      return last.getUTCDate()-((lw-h.weekday+7)%7);
    }
    var first=new Date(Date.UTC(y,h.month-1,1)).getUTCDay();
    return 1+((h.weekday-first+7)%7)+7*(h.nth-1);
  }
  function isHoliday(d){
    var y=d.getUTCFullYear(),m=d.getUTCMonth()+1,dd=d.getUTCDate(),t=d.getTime();
    return HOLIDAYS.some(function(h){
      if(h.fixed){
        /* check this year and next (Dec 31 can be observed New Year's) */
        return observed(y,h).getTime()===t||observed(y+1,h).getTime()===t;
      }
      return h.month===m&&dd===nthDay(y,h);
    });
  }
  if(typeof window!=='undefined') window.__ivcsIsHoliday=isHoliday;
  function isOpenDay(d){var w=d.getUTCDay();return w>=1&&w<=5&&!isHoliday(d);}
  var n=chicagoNow(); if(!n||isNaN(n.date)) return;
  var openToday=isOpenDay(n.date);
  if(openToday&&n.hour>=9&&n.hour<17) return;
  var when;
  if(openToday&&n.hour<9) when='this morning, once our phones open';
  else{
    var d=new Date(n.date.getTime()),i=0;
    do{d=new Date(d.getTime()+864e5);i++;}while(!isOpenDay(d)&&i<14);
    when=i===1?'tomorrow':'on '+DAYS[d.getUTCDay()];
  }
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
