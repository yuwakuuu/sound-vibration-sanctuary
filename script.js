/* Sound Vibration Sanctuary: the small bits of behaviour the page needs. Everything still reads and works without it. */
(function () {
  'use strict';

  // Mobile menu
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.nav-toggle');
  if (header && toggle) {
    var setOpen = function (open) {
      header.classList.toggle('nav-open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.setAttribute('aria-label', open ? 'Close the menu' : 'Open the menu');
    };
    toggle.addEventListener('click', function () { setOpen(!header.classList.contains('nav-open')); });
    header.addEventListener('click', function (e) { if (e.target.closest('.menu a')) setOpen(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setOpen(false); });
  }

  // "Book this" buttons pick the session in the form
  var select = document.getElementById('f-session');
  document.addEventListener('click', function (e) {
    var a = e.target.closest('[data-book]');
    if (!a || !select) return;
    var want = a.getAttribute('data-book');
    for (var i = 0; i < select.options.length; i++) {
      if (select.options[i].text === want) { select.selectedIndex = i; break; }
    }
  });

  // Forms: they open an email to the sanctuary once its address is set in data-email on the <form>.
  // Until then they say so plainly and point to Facebook, so no message is ever silently lost.
  function status(form, text) { var s = form.querySelector('.form-status'); if (s) s.textContent = text; }
  function wire(form, subject, body) {
    if (!form) return;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var email = form.querySelector('input[type=email]');
      if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) {
        status(form, 'Please enter your email address.');
        email.focus();
        return;
      }
      var name = form.querySelector('[name=name]');
      if (name && !name.value.trim()) { status(form, 'Please tell us your name.'); name.focus(); return; }
      var to = (form.getAttribute('data-email') || '').trim();
      if (!to) {
        status(form, 'Thank you! Online messages are not connected yet, so please message us on Facebook and we will get back to you.');
        return;
      }
      window.location.href = 'mailto:' + to + '?subject=' + encodeURIComponent(subject(form)) + '&body=' + encodeURIComponent(body(form));
      status(form, 'Thank you! Your email app is opening with your message ready to send.');
    });
  }
  var val = function (form, n) { var f = form.querySelector('[name=' + n + ']'); return f ? f.value.trim() : ''; };
  wire(document.getElementById('book-form'),
    function (f) { return 'Booking request: ' + val(f, 'session'); },
    function (f) {
      return 'Name: ' + val(f, 'name') + '\nEmail: ' + val(f, 'email') + '\nPhone: ' + val(f, 'phone') +
        '\nInterested in: ' + val(f, 'session') + '\n\n' + val(f, 'message');
    });
  wire(document.getElementById('news-form'),
    function () { return 'Please add me to the mailing list'; },
    function (f) { return 'Please add ' + val(f, 'email') + ' to the Sound Vibration Sanctuary mailing list.'; });

  // "Hear a singing bowl": a soft bowl tone made in the browser (no sound files), only when asked
  var bowl = document.getElementById('bowl');
  var ctx = null;
  if (bowl) {
    bowl.addEventListener('click', function () {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return;
      ctx = ctx || new AC();
      if (ctx.state === 'suspended') ctx.resume();
      var now = ctx.currentTime, base = 262;
      var out = ctx.createGain();
      out.gain.setValueAtTime(0.0001, now);
      out.gain.exponentialRampToValueAtTime(0.32, now + 0.04);
      out.gain.exponentialRampToValueAtTime(0.0001, now + 9);
      out.connect(ctx.destination);
      [[1, 1], [1.004, 0.6], [2.71, 0.35], [5.15, 0.12]].forEach(function (p) {
        var o = ctx.createOscillator(), g = ctx.createGain();
        o.type = 'sine';
        o.frequency.value = base * p[0];
        g.gain.value = p[1] * 0.4;
        o.connect(g); g.connect(out);
        o.start(now); o.stop(now + 9.2);
      });
      bowl.classList.remove('ringing');
      void bowl.offsetWidth;
      bowl.classList.add('ringing');
    });
  }
})();
